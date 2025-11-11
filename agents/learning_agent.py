"""
Learning Agent - Analyzes data and improves strategy
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from loguru import logger
from sqlalchemy import func
from core.ollama_client import get_ollama_client
from database.models import Post, Comment, Metric, Learning, Strategy, get_session


class LearningAgent:
    """Autonomous agent that learns from data and optimizes strategy"""

    def __init__(self):
        self.ollama = get_ollama_client()
        self.name = "LearningAgent"

    def analyze_and_learn(self) -> Dict:
        """
        Analyze all recent data and extract learnings

        Returns:
            Dict with insights and updated strategy recommendations
        """
        logger.info("Analyzing performance data...")

        session = get_session()
        try:
            # Gather data
            post_insights = self._analyze_posts(session)
            comment_insights = self._analyze_comments(session)
            growth_insights = self._analyze_growth(session)

            # Generate learnings
            all_insights = post_insights + comment_insights + growth_insights

            # Save learnings to database
            for insight in all_insights:
                self._save_learning(session, insight)

            # Generate strategy recommendations
            recommendations = self._generate_strategy_recommendations(
                post_insights,
                comment_insights,
                growth_insights
            )

            logger.info(f"Generated {len(all_insights)} insights and strategy recommendations")

            return {
                'insights': all_insights,
                'recommendations': recommendations,
                'timestamp': datetime.utcnow().isoformat()
            }

        finally:
            session.close()

    def _analyze_posts(self, session) -> List[Dict]:
        """Analyze post performance"""
        insights = []

        # Get posts from last 7 days
        week_ago = datetime.utcnow() - timedelta(days=7)
        posts = session.query(Post).filter(
            Post.posted_at >= week_ago,
            Post.views > 0
        ).all()

        if len(posts) < 3:
            return insights

        # Find best performing topics
        topic_performance = {}
        for post in posts:
            if post.topic:
                if post.topic not in topic_performance:
                    topic_performance[post.topic] = []
                topic_performance[post.topic].append(post.engagement_rate)

        for topic, rates in topic_performance.items():
            avg_rate = sum(rates) / len(rates)
            if avg_rate > 0.05:  # 5% engagement rate threshold
                insights.append({
                    'category': 'content',
                    'insight': f"Posts about '{topic}' get {avg_rate:.1%} avg engagement",
                    'confidence': min(0.5 + (len(rates) * 0.1), 0.95),
                    'data_points': len(rates)
                })

        # Analyze post length
        lengths = [(len(post.content), post.engagement_rate) for post in posts]
        if lengths:
            avg_length = sum(l for l, _ in lengths) / len(lengths)
            insights.append({
                'category': 'content',
                'insight': f"Optimal post length around {int(avg_length)} characters",
                'confidence': 0.6,
                'data_points': len(lengths)
            })

        return insights

    def _analyze_comments(self, session) -> List[Dict]:
        """Analyze comment performance"""
        insights = []

        # Get comments from last 7 days
        week_ago = datetime.utcnow() - timedelta(days=7)
        comments = session.query(Comment).filter(
            Comment.commented_at >= week_ago
        ).all()

        if len(comments) < 5:
            return insights

        # Calculate reply rate
        total = len(comments)
        with_replies = sum(1 for c in comments if c.replies > 0)
        reply_rate = with_replies / total if total > 0 else 0

        if reply_rate > 0.3:
            insights.append({
                'category': 'engagement',
                'insight': f"Comments getting {reply_rate:.1%} reply rate - effective engagement",
                'confidence': 0.7,
                'data_points': total
            })

        # Find high-quality comment patterns
        high_quality = [c for c in comments if c.quality_score >= 8.0]
        if len(high_quality) >= 3:
            insights.append({
                'category': 'engagement',
                'insight': "High quality comments (8+) generate more replies",
                'confidence': 0.8,
                'data_points': len(high_quality)
            })

        return insights

    def _analyze_growth(self, session) -> List[Dict]:
        """Analyze growth metrics"""
        insights = []

        # Get metrics from last 30 days
        month_ago = datetime.utcnow() - timedelta(days=30)
        metrics = session.query(Metric).filter(
            Metric.date >= month_ago
        ).order_by(Metric.date).all()

        if len(metrics) < 7:
            return insights

        # Calculate growth rate
        first_followers = metrics[0].followers
        last_followers = metrics[-1].followers
        growth = last_followers - first_followers
        days = len(metrics)
        daily_growth = growth / days if days > 0 else 0

        if daily_growth > 10:
            insights.append({
                'category': 'strategy',
                'insight': f"Strong growth: averaging +{daily_growth:.1f} followers/day",
                'confidence': 0.85,
                'data_points': days
            })
        elif daily_growth < 5:
            insights.append({
                'category': 'strategy',
                'insight': f"Growth slowing: only +{daily_growth:.1f} followers/day - need strategy adjustment",
                'confidence': 0.75,
                'data_points': days
            })

        # Analyze engagement rate trends
        avg_engagement = sum(m.avg_engagement_rate for m in metrics) / len(metrics)
        if avg_engagement > 0.08:
            insights.append({
                'category': 'strategy',
                'insight': f"High engagement rate ({avg_engagement:.1%}) - content resonates well",
                'confidence': 0.9,
                'data_points': len(metrics)
            })

        return insights

    def _generate_strategy_recommendations(
        self,
        post_insights: List[Dict],
        comment_insights: List[Dict],
        growth_insights: List[Dict]
    ) -> Dict:
        """Generate actionable strategy recommendations"""

        all_insights_text = "\n".join([
            f"- {i['insight']} (confidence: {i['confidence']:.0%}, data points: {i['data_points']})"
            for i in (post_insights + comment_insights + growth_insights)
        ])

        if not all_insights_text:
            all_insights_text = "Not enough data yet for specific recommendations."

        prompt = f"""Based on these performance insights, provide strategic recommendations for Prog Silo Company's LinkedIn growth:

INSIGHTS:
{all_insights_text}

Provide recommendations in these areas:
1. Content Strategy: What topics/formats to focus on?
2. Engagement Strategy: How to improve comment effectiveness?
3. Growth Strategy: How to accelerate follower growth?

Be specific and actionable. Format as JSON:
{{
    "content_strategy": "recommendation here",
    "engagement_strategy": "recommendation here",
    "growth_strategy": "recommendation here",
    "priority_actions": ["action 1", "action 2", "action 3"]
}}"""

        try:
            recommendations = self.ollama.generate_structured(
                prompt=prompt,
                temperature=0.5
            )
            return recommendations
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return {
                'content_strategy': 'Continue posting valuable content daily',
                'engagement_strategy': 'Comment on 25-30 relevant posts daily',
                'growth_strategy': 'Focus on consistency and quality',
                'priority_actions': ['Post daily', 'Engage authentically', 'Track metrics']
            }

    def _save_learning(self, session, insight_data: Dict):
        """Save learning to database"""
        # Check if similar learning exists
        existing = session.query(Learning).filter(
            Learning.category == insight_data['category'],
            Learning.insight.like(f"%{insight_data['insight'][:50]}%"),
            Learning.active == True
        ).first()

        if existing:
            # Update confidence and data points
            existing.confidence = max(existing.confidence, insight_data['confidence'])
            existing.data_points += insight_data['data_points']
        else:
            # Create new learning
            learning = Learning(
                category=insight_data['category'],
                insight=insight_data['insight'],
                confidence=insight_data['confidence'],
                data_points=insight_data['data_points'],
                active=True,
                applied_count=0
            )
            session.add(learning)

        session.commit()

    def update_metrics(self, metrics_data: Dict):
        """Update daily metrics in database"""
        session = get_session()
        try:
            # Check if today's metrics exist
            today = datetime.utcnow().date()
            existing = session.query(Metric).filter(
                func.date(Metric.date) == today
            ).first()

            if existing:
                # Update existing
                for key, value in metrics_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
            else:
                # Create new
                metric = Metric(
                    date=datetime.utcnow(),
                    **metrics_data
                )
                session.add(metric)

            session.commit()
            logger.info("Updated metrics in database")

        finally:
            session.close()


# Convenience function
def analyze_and_learn() -> Dict:
    """Run learning analysis"""
    agent = LearningAgent()
    return agent.analyze_and_learn()
