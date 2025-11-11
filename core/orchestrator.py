"""
Orchestrator - Coordinates all agents using LangGraph
"""
from typing import Dict, Any, TypedDict, Annotated
from datetime import datetime
from loguru import logger
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor

from agents.strategy_agent import StrategyAgent
from agents.content_agent import ContentAgent
from agents.engagement_agent import EngagementAgent
from agents.learning_agent import LearningAgent
from core.linkedin_client import get_linkedin_client
from database.models import AgentRun, get_session
import os


# Define the state that flows through the graph
class AgentState(TypedDict):
    """State passed between agents"""
    # Strategy
    strategy: Dict
    action_plan: Dict

    # Content
    post_generated: bool
    post_data: Dict
    post_published: bool

    # Engagement
    comments_made: int
    comment_results: list

    # Learning
    insights: list
    recommendations: Dict

    # Metadata
    dry_run: bool
    errors: list
    timestamp: str


class AgentOrchestrator:
    """Orchestrates autonomous agent workflow using LangGraph"""

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.strategy_agent = StrategyAgent()
        self.content_agent = ContentAgent()
        self.engagement_agent = EngagementAgent()
        self.learning_agent = LearningAgent()

        # Build the workflow graph
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)

        # Add nodes (agent functions)
        workflow.add_node("strategy", self._strategy_node)
        workflow.add_node("learn", self._learning_node)
        workflow.add_node("create_content", self._content_node)
        workflow.add_node("publish_post", self._publish_node)
        workflow.add_node("engage", self._engagement_node)
        workflow.add_node("finalize", self._finalize_node)

        # Define the flow
        workflow.set_entry_point("strategy")

        # Strategy → Learning → Content
        workflow.add_edge("strategy", "learn")
        workflow.add_edge("learn", "create_content")
        workflow.add_edge("create_content", "publish_post")

        # After publishing → Engage → Finalize
        workflow.add_edge("publish_post", "engage")
        workflow.add_edge("engage", "finalize")
        workflow.add_edge("finalize", END)

        return workflow.compile()

    def _strategy_node(self, state: AgentState) -> AgentState:
        """Strategy agent decides what to do"""
        logger.info("🧠 Strategy Agent: Deciding today's actions...")

        try:
            strategy = self.strategy_agent.get_current_strategy()
            action_plan = self.strategy_agent.decide_daily_actions()

            state['strategy'] = strategy
            state['action_plan'] = action_plan

            self._log_agent_run("StrategyAgent", "Decided daily actions", success=True)

        except Exception as e:
            logger.error(f"Strategy agent failed: {e}")
            state['errors'].append(f"StrategyAgent: {str(e)}")
            self._log_agent_run("StrategyAgent", "Decide actions", success=False, error=str(e))

        return state

    def _learning_node(self, state: AgentState) -> AgentState:
        """Learning agent analyzes past performance"""
        logger.info("📊 Learning Agent: Analyzing performance...")

        try:
            analysis = self.learning_agent.analyze_and_learn()

            state['insights'] = analysis.get('insights', [])
            state['recommendations'] = analysis.get('recommendations', {})

            # Update strategy if there are strong recommendations
            if state['recommendations']:
                updated_strategy = self.strategy_agent.update_strategy(
                    state['recommendations']
                )
                state['strategy'] = updated_strategy

            self._log_agent_run("LearningAgent", "Analyzed performance", success=True)

        except Exception as e:
            logger.error(f"Learning agent failed: {e}")
            state['errors'].append(f"LearningAgent: {str(e)}")
            self._log_agent_run("LearningAgent", "Analyze", success=False, error=str(e))

        return state

    def _content_node(self, state: AgentState) -> AgentState:
        """Content agent creates a post"""
        logger.info("✍️  Content Agent: Generating post...")

        try:
            if state['action_plan'].get('post_content', False):
                post_data = self.content_agent.generate_post(state['strategy'])
                state['post_data'] = post_data
                state['post_generated'] = True

                # Save to database
                self.content_agent.save_post(post_data, posted=False)

                logger.info(f"Generated post: '{post_data.get('topic')}' (quality: {post_data.get('quality_score', 0):.1f}/10)")

                self._log_agent_run("ContentAgent", "Generated post", success=True)
            else:
                state['post_generated'] = False
                logger.info("Skipping post generation (not in action plan)")

        except Exception as e:
            logger.error(f"Content agent failed: {e}")
            state['errors'].append(f"ContentAgent: {str(e)}")
            state['post_generated'] = False
            self._log_agent_run("ContentAgent", "Generate post", success=False, error=str(e))

        return state

    def _publish_node(self, state: AgentState) -> AgentState:
        """Publish the post to LinkedIn"""
        logger.info("📤 Publishing post to LinkedIn...")

        if not state.get('post_generated', False):
            logger.info("No post to publish")
            return state

        try:
            post_data = state['post_data']

            # Check if we should actually post
            auto_post_enabled = os.getenv('ENABLE_AUTO_POSTING', 'false').lower() == 'true'
            dry_run = state.get('dry_run', True) or not auto_post_enabled

            if dry_run:
                logger.info(f"[DRY RUN] Would post:\n{post_data['content'][:200]}...")
                state['post_published'] = False
            else:
                # Actually post to LinkedIn
                with get_linkedin_client(headless=True) as linkedin:
                    if linkedin.login():
                        success = linkedin.post_content(post_data['content'], dry_run=False)
                        state['post_published'] = success

                        if success:
                            logger.info("✓ Post published successfully")
                            # Update database
                            self.content_agent.save_post(post_data, posted=True)
                    else:
                        logger.error("Failed to login to LinkedIn")
                        state['post_published'] = False

        except Exception as e:
            logger.error(f"Publishing failed: {e}")
            state['errors'].append(f"PublishNode: {str(e)}")
            state['post_published'] = False

        return state

    def _engagement_node(self, state: AgentState) -> AgentState:
        """Engagement agent comments on posts"""
        logger.info("💬 Engagement Agent: Commenting on posts...")

        try:
            num_comments = state['action_plan'].get('num_comments', 5)

            # Check if auto-commenting is enabled
            auto_comment_enabled = os.getenv('ENABLE_AUTO_COMMENTING', 'false').lower() == 'true'
            dry_run = state.get('dry_run', True) or not auto_comment_enabled

            results = self.engagement_agent.find_and_engage(
                strategy=state['strategy'],
                num_comments=num_comments,
                dry_run=dry_run
            )

            state['comment_results'] = results
            state['comments_made'] = len([r for r in results if r.get('success', False)])

            logger.info(f"Commented on {state['comments_made']} posts")

            self._log_agent_run("EngagementAgent", f"Made {state['comments_made']} comments", success=True)

        except Exception as e:
            logger.error(f"Engagement agent failed: {e}")
            state['errors'].append(f"EngagementAgent: {str(e)}")
            state['comments_made'] = 0
            self._log_agent_run("EngagementAgent", "Engage", success=False, error=str(e))

        return state

    def _finalize_node(self, state: AgentState) -> AgentState:
        """Finalize and log results"""
        logger.info("🏁 Finalizing agent run...")

        # Log summary
        logger.info("=" * 60)
        logger.info("AGENT RUN SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Timestamp: {state['timestamp']}")
        logger.info(f"Post generated: {state.get('post_generated', False)}")
        logger.info(f"Post published: {state.get('post_published', False)}")
        logger.info(f"Comments made: {state.get('comments_made', 0)}")
        logger.info(f"Insights found: {len(state.get('insights', []))}")
        logger.info(f"Errors: {len(state.get('errors', []))}")

        if state.get('errors'):
            logger.warning(f"Errors encountered: {state['errors']}")

        logger.info("=" * 60)

        return state

    def _log_agent_run(self, agent_name: str, task: str, success: bool, error: str = None):
        """Log agent execution to database"""
        session = get_session()
        try:
            run = AgentRun(
                agent_name=agent_name,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                task=task,
                success=success,
                error=error
            )
            session.add(run)
            session.commit()
        except Exception as e:
            logger.error(f"Failed to log agent run: {e}")
        finally:
            session.close()

    def run(self) -> AgentState:
        """Execute the full agent workflow"""
        logger.info("🚀 Starting autonomous agent workflow...")

        # Initialize state
        initial_state: AgentState = {
            'strategy': {},
            'action_plan': {},
            'post_generated': False,
            'post_data': {},
            'post_published': False,
            'comments_made': 0,
            'comment_results': [],
            'insights': [],
            'recommendations': {},
            'dry_run': self.dry_run,
            'errors': [],
            'timestamp': datetime.utcnow().isoformat()
        }

        # Run the workflow
        try:
            final_state = self.workflow.invoke(initial_state)
            logger.info("✓ Workflow completed successfully")
            return final_state

        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            raise


# Convenience function
def run_autonomous_cycle(dry_run: bool = True) -> AgentState:
    """Run one complete autonomous cycle"""
    orchestrator = AgentOrchestrator(dry_run=dry_run)
    return orchestrator.run()
