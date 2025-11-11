#!/usr/bin/env python3
"""
View current statistics and performance
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.models import Post, Comment, Metric, Learning, get_session
from datetime import datetime, timedelta
from loguru import logger

if __name__ == '__main__':
    session = get_session()

    try:
        print("=" * 80)
        print("PROG SILO COMPANY - STATISTICS")
        print("=" * 80)

        # Posts
        total_posts = session.query(Post).count()
        recent_posts = session.query(Post).filter(
            Post.posted_at >= datetime.utcnow() - timedelta(days=7)
        ).all()

        print(f"\n📝 POSTS")
        print(f"  Total: {total_posts}")
        print(f"  Last 7 days: {len(recent_posts)}")

        if recent_posts:
            avg_engagement = sum(p.engagement_rate for p in recent_posts if p.engagement_rate) / len(recent_posts)
            print(f"  Avg engagement rate: {avg_engagement:.2%}")

        # Comments
        total_comments = session.query(Comment).count()
        recent_comments = session.query(Comment).filter(
            Comment.commented_at >= datetime.utcnow() - timedelta(days=7)
        ).all()

        print(f"\n💬 COMMENTS")
        print(f"  Total: {total_comments}")
        print(f"  Last 7 days: {len(recent_comments)}")

        if recent_comments:
            reply_rate = sum(1 for c in recent_comments if c.replies > 0) / len(recent_comments)
            print(f"  Reply rate: {reply_rate:.1%}")

        # Metrics
        latest_metric = session.query(Metric).order_by(Metric.date.desc()).first()
        week_ago_metric = session.query(Metric).filter(
            Metric.date <= datetime.utcnow() - timedelta(days=7)
        ).order_by(Metric.date.desc()).first()

        print(f"\n📈 GROWTH")
        if latest_metric:
            print(f"  Current followers: {latest_metric.followers}")
            if week_ago_metric:
                growth = latest_metric.followers - week_ago_metric.followers
                print(f"  7-day growth: +{growth} followers")
        else:
            print("  No metrics recorded yet")

        # Learnings
        active_learnings = session.query(Learning).filter(
            Learning.active == True
        ).order_by(Learning.confidence.desc()).all()

        print(f"\n🧠 LEARNINGS")
        print(f"  Active insights: {len(active_learnings)}")

        if active_learnings:
            print("\n  Top insights:")
            for learning in active_learnings[:5]:
                print(f"    • {learning.insight}")
                print(f"      (confidence: {learning.confidence:.0%}, applied: {learning.applied_count}x)")

        print("\n" + "=" * 80)

    finally:
        session.close()
