"""
Strategy Agent - Makes high-level decisions about what to do
"""
from typing import Dict, List
from datetime import datetime
from loguru import logger
from database.models import Strategy, Learning, Metric, get_session


class StrategyAgent:
    """Autonomous agent that decides overall strategy"""

    def __init__(self):
        self.name = "StrategyAgent"

    def get_current_strategy(self) -> Dict:
        """
        Get or create current active strategy

        Returns:
            Strategy dict with all configuration
        """
        session = get_session()
        try:
            # Get active strategy from database
            strategy_row = session.query(Strategy).filter(
                Strategy.active == True
            ).order_by(Strategy.created_at.desc()).first()

            if strategy_row:
                strategy = self._strategy_to_dict(strategy_row)
            else:
                # Create default strategy
                strategy = self._create_default_strategy(session)

            logger.info(f"Current strategy: {strategy['posting_time']} posting, {strategy['comments_per_day']} comments/day")
            return strategy

        finally:
            session.close()

    def update_strategy(self, recommendations: Dict) -> Dict:
        """
        Update strategy based on learning recommendations

        Args:
            recommendations: Dict from LearningAgent

        Returns:
            Updated strategy dict
        """
        logger.info("Updating strategy based on learnings...")

        session = get_session()
        try:
            # Get current strategy
            current = session.query(Strategy).filter(
                Strategy.active == True
            ).first()

            if not current:
                return self._create_default_strategy(session)

            # Apply recommendations
            # (In a real system, this would intelligently parse recommendations)
            # For now, we'll make small adjustments

            # Adjust comments per day based on engagement success
            if 'engagement_strategy' in recommendations:
                if 'increase' in recommendations['engagement_strategy'].lower():
                    current.comments_per_day = min(current.comments_per_day + 5, 40)
                elif 'decrease' in recommendations['engagement_strategy'].lower():
                    current.comments_per_day = max(current.comments_per_day - 5, 15)

            # Update strategy score based on recent performance
            current.strategy_score = self._calculate_strategy_score(session)

            session.commit()

            logger.info(f"Updated strategy (score: {current.strategy_score:.2f})")
            return self._strategy_to_dict(current)

        finally:
            session.close()

    def decide_daily_actions(self) -> Dict:
        """
        Decide what actions to take today

        Returns:
            Dict with today's action plan
        """
        strategy = self.get_current_strategy()

        # Get recent learnings for context
        session = get_session()
        try:
            high_confidence_learnings = session.query(Learning).filter(
                Learning.active == True,
                Learning.confidence >= 0.7
            ).all()

            action_plan = {
                'post_content': True,  # Always post once per day
                'num_comments': strategy['comments_per_day'],
                'target_hashtags': strategy['target_hashtags'],
                'posting_time': strategy['posting_time'],
                'content_themes': strategy['content_themes'],
                'min_comment_quality_score': strategy.get('min_comment_quality_score', 7),
                'learnings_to_apply': [
                    {'insight': l.insight, 'confidence': l.confidence}
                    for l in high_confidence_learnings[:5]
                ]
            }

            logger.info(f"Today's plan: Post at {action_plan['posting_time']}, make {action_plan['num_comments']} comments")
            return action_plan

        finally:
            session.close()

    def _create_default_strategy(self, session) -> Dict:
        """Create default initial strategy"""
        import json

        default_themes = ['programming', 'career growth', 'software development', 'tech tips']
        default_hashtags = ['programming', 'softwaredevelopment', 'coding', 'python', 'developers']

        strategy_row = Strategy(
            content_themes=json.dumps(default_themes),
            preferred_post_types=json.dumps(['tips', 'insights', 'lessons']),
            posting_time='08:00',
            target_hashtags=json.dumps(default_hashtags),
            target_follower_range_min=1000,
            target_follower_range_max=50000,
            comments_per_day=25,
            daily_follower_target=15,
            engagement_rate_target=0.08,
            active=True,
            strategy_score=5.0
        )

        session.add(strategy_row)
        session.commit()

        logger.info("Created default strategy")
        return self._strategy_to_dict(strategy_row)

    def _strategy_to_dict(self, strategy_row: Strategy) -> Dict:
        """Convert Strategy ORM object to dict"""
        import json

        return {
            'id': strategy_row.id,
            'content_themes': json.loads(strategy_row.content_themes),
            'preferred_post_types': json.loads(strategy_row.preferred_post_types),
            'posting_time': strategy_row.posting_time,
            'target_hashtags': json.loads(strategy_row.target_hashtags),
            'target_follower_range_min': strategy_row.target_follower_range_min,
            'target_follower_range_max': strategy_row.target_follower_range_max,
            'comments_per_day': strategy_row.comments_per_day,
            'daily_follower_target': strategy_row.daily_follower_target,
            'engagement_rate_target': strategy_row.engagement_rate_target,
            'strategy_score': strategy_row.strategy_score,
            'min_comment_quality_score': 7.0
        }

    def _calculate_strategy_score(self, session) -> float:
        """Calculate how well current strategy is performing"""
        from datetime import timedelta

        # Get last 7 days of metrics
        week_ago = datetime.utcnow() - timedelta(days=7)
        metrics = session.query(Metric).filter(
            Metric.date >= week_ago
        ).all()

        if not metrics:
            return 5.0  # Neutral score

        # Calculate score based on multiple factors
        score = 5.0

        # Factor 1: Follower growth
        if len(metrics) >= 2:
            follower_change = metrics[-1].followers - metrics[0].followers
            daily_growth = follower_change / len(metrics)
            if daily_growth >= 15:  # Meeting target
                score += 2.0
            elif daily_growth >= 10:
                score += 1.0
            elif daily_growth < 5:
                score -= 1.0

        # Factor 2: Engagement rate
        avg_engagement = sum(m.avg_engagement_rate for m in metrics) / len(metrics)
        if avg_engagement >= 0.08:  # Meeting target
            score += 2.0
        elif avg_engagement >= 0.05:
            score += 1.0
        elif avg_engagement < 0.03:
            score -= 1.0

        # Factor 3: Consistency
        posts_per_day = sum(m.posts_published for m in metrics) / len(metrics)
        if posts_per_day >= 0.9:  # Nearly daily
            score += 1.0

        # Clamp score to 1-10
        return min(max(score, 1.0), 10.0)


# Convenience function
def get_strategy() -> Dict:
    """Get current strategy"""
    agent = StrategyAgent()
    return agent.get_current_strategy()


def decide_actions() -> Dict:
    """Decide today's actions"""
    agent = StrategyAgent()
    return agent.decide_daily_actions()
