"""
Content Agent - Generates high-quality LinkedIn posts
"""
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger
from core.ollama_client import get_ollama_client
from database.models import Post, Learning, get_session


class ContentAgent:
    """Autonomous agent that creates LinkedIn posts"""

    def __init__(self):
        self.ollama = get_ollama_client()
        self.name = "ContentAgent"

    def generate_post(self, strategy: Dict) -> Dict:
        """
        Generate a LinkedIn post based on current strategy

        Args:
            strategy: Current strategy dict with themes, goals, etc.

        Returns:
            Dict with 'content', 'topic', 'quality_score'
        """
        logger.info("Generating LinkedIn post...")

        # Get recent learnings from database
        learnings = self._get_active_learnings()

        # Build context-aware system prompt
        system_prompt = self._build_system_prompt(strategy, learnings)

        # Generate post
        prompt = f"""Generate a LinkedIn post for Prog Silo Company.

Target Audience: Mid-level developers (2-5 years experience)
Content Themes: {', '.join(strategy.get('content_themes', ['programming', 'career growth']))}

Requirements:
- Professional but friendly tone
- Provide real value (insights, tips, lessons)
- 150-250 words
- Include a hook in first line
- End with an engaging question or call-to-action
- NO hashtags (we'll add them separately if needed)
- NO emojis unless specifically relevant

Based on past learnings:
{self._format_learnings(learnings)}

Write the post now:"""

        content = self.ollama.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.8
        ).strip()

        # Extract topic
        topic = self._extract_topic(content)

        # Score quality
        quality_score = self._score_post_quality(content)

        logger.info(f"Generated post on '{topic}' with quality score: {quality_score:.1f}/10")

        return {
            'content': content,
            'topic': topic,
            'quality_score': quality_score
        }

    def _build_system_prompt(self, strategy: Dict, learnings: List) -> str:
        """Build system prompt based on strategy and learnings"""
        return f"""You are a content creator for Prog Silo Company, a tech coaching brand for developers.

Your voice:
- Professional but approachable
- Educational and valuable
- Based on real experience
- No fluff or generic advice

Your audience:
- Mid-level developers (2-5 years experience)
- Actively learning and growing
- Value practical, actionable insights

Your goal:
- Build trust and authority
- Provide genuine value in every post
- Encourage engagement

Always write posts that YOU would want to read as a developer."""

    def _get_active_learnings(self) -> List[Learning]:
        """Get active learnings from database"""
        session = get_session()
        try:
            learnings = session.query(Learning).filter(
                Learning.active == True,
                Learning.category == 'content'
            ).order_by(
                Learning.confidence.desc()
            ).limit(5).all()
            return learnings
        finally:
            session.close()

    def _format_learnings(self, learnings: List[Learning]) -> str:
        """Format learnings for prompt"""
        if not learnings:
            return "No specific learnings yet - this is an early post."

        formatted = []
        for l in learnings:
            formatted.append(f"- {l.insight} (confidence: {l.confidence:.0%})")

        return "\n".join(formatted)

    def _extract_topic(self, content: str) -> str:
        """Extract main topic from post content"""
        prompt = f"""What is the main topic of this LinkedIn post? Reply with 2-4 words only.

Post:
{content}

Topic:"""

        topic = self.ollama.generate(prompt, temperature=0.3).strip()
        # Clean up
        topic = topic.replace('"', '').replace("'", "")[:100]
        return topic

    def _score_post_quality(self, content: str) -> float:
        """Score post quality"""
        criteria = """
        - Professional tone and language
        - Provides genuine value and insights
        - Appropriate length (150-250 words)
        - Engaging hook in first line
        - Clear structure and readability
        - Relevant to target audience (developers)
        - Ends with engaging question or CTA
        """

        score = self.ollama.score_text(content, criteria, scale=10)
        return score

    def save_post(self, post_data: Dict, posted: bool = False) -> Post:
        """Save post to database"""
        session = get_session()
        try:
            post = Post(
                content=post_data['content'],
                topic=post_data.get('topic'),
                quality_score=post_data.get('quality_score'),
                posted_at=datetime.utcnow() if posted else None,
                posted_by_agent=True,
                agent_version='v1.0'
            )
            session.add(post)
            session.commit()
            logger.info(f"Saved post to database (ID: {post.id})")
            return post
        finally:
            session.close()

    def get_best_performing_topics(self, limit: int = 5) -> List[str]:
        """Get topics that performed best historically"""
        session = get_session()
        try:
            posts = session.query(Post).filter(
                Post.views > 0
            ).order_by(
                Post.engagement_rate.desc()
            ).limit(limit).all()

            return [p.topic for p in posts if p.topic]
        finally:
            session.close()


# Convenience function
def generate_post(strategy: Dict) -> Dict:
    """Generate a post using ContentAgent"""
    agent = ContentAgent()
    return agent.generate_post(strategy)
