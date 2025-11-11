#!/usr/bin/env python3
"""
Prog Silo Company - All-in-One Setup and Run Script

This script handles everything:
- Database initialization
- Testing Ollama connection
- Testing LinkedIn (optional)
- Generating test posts
- Running the autonomous system

Usage:
    python run.py setup          # First time setup
    python run.py test           # Test all components
    python run.py generate       # Generate a test post
    python run.py once           # Run one cycle (dry-run)
    python run.py start          # Start autonomous mode
    python run.py stats          # View statistics
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from loguru import logger
import argparse


def setup():
    """First time setup - initialize database"""
    logger.info("=" * 80)
    logger.info("SETUP: Initializing Prog Silo Company")
    logger.info("=" * 80)

    # Check for .env file
    env_file = project_root / '.env'
    env_example = project_root / '.env.example'

    if not env_file.exists():
        logger.warning(".env file not found")
        if env_example.exists():
            logger.info("Creating .env from .env.example...")
            import shutil
            shutil.copy(env_example, env_file)
            logger.info("✓ Created .env file")
            logger.warning("⚠ Please edit .env and add your LinkedIn credentials!")
        else:
            logger.error("❌ .env.example not found")
            return False
    else:
        logger.info("✓ .env file exists")

    # Initialize database
    logger.info("\nInitializing database...")
    try:
        from database.models import init_db
        engine = init_db()
        logger.info(f"✓ Database initialized: {engine.url}")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False

    logger.info("\n" + "=" * 80)
    logger.info("✓ Setup complete!")
    logger.info("=" * 80)
    logger.info("\nNext steps:")
    logger.info("  1. Edit .env and add your LinkedIn credentials")
    logger.info("  2. Make sure Ollama is running: ollama serve")
    logger.info("  3. Run tests: python run.py test")
    logger.info("=" * 80)

    return True


def test():
    """Test all components"""
    logger.info("=" * 80)
    logger.info("TESTING: All Components")
    logger.info("=" * 80)

    all_passed = True

    # Test 1: Ollama
    logger.info("\n[1/3] Testing Ollama connection...")
    try:
        from core.ollama_client import get_ollama_client
        ollama = get_ollama_client()
        response = ollama.generate("Say 'OK'", temperature=0.0)
        logger.info(f"✓ Ollama working: {response[:50]}")
    except Exception as e:
        logger.error(f"❌ Ollama test failed: {e}")
        logger.error("   Make sure Ollama is running: ollama serve")
        all_passed = False

    # Test 2: Database
    logger.info("\n[2/3] Testing database...")
    try:
        from database.models import get_session
        session = get_session()
        session.close()
        logger.info("✓ Database connection working")
    except Exception as e:
        logger.error(f"❌ Database test failed: {e}")
        all_passed = False

    # Test 3: LinkedIn (optional)
    logger.info("\n[3/3] Testing LinkedIn...")
    from dotenv import load_dotenv
    load_dotenv()

    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')

    if not email or not password or 'example.com' in email:
        logger.warning("⚠ LinkedIn credentials not configured (optional)")
        logger.info("   Add to .env: LINKEDIN_EMAIL and LINKEDIN_PASSWORD")
    else:
        try:
            from core.linkedin_client import get_linkedin_client
            logger.info(f"   Using account: {email}")
            logger.info("   This may take 10-15 seconds...")
            with get_linkedin_client(headless=True) as linkedin:
                if linkedin.login():
                    logger.info("✓ LinkedIn login successful")
                else:
                    logger.error("❌ LinkedIn login failed")
                    all_passed = False
        except Exception as e:
            logger.error(f"❌ LinkedIn test failed: {e}")
            all_passed = False

    logger.info("\n" + "=" * 80)
    if all_passed:
        logger.info("✓ All tests passed!")
    else:
        logger.warning("⚠ Some tests failed - check errors above")
    logger.info("=" * 80)

    return all_passed


def generate():
    """Generate a test post"""
    logger.info("=" * 80)
    logger.info("GENERATE: Test LinkedIn Post")
    logger.info("=" * 80)

    try:
        from agents.content_agent import ContentAgent
        from agents.strategy_agent import StrategyAgent

        logger.info("\nGenerating post with AI...")

        strategy_agent = StrategyAgent()
        strategy = strategy_agent.get_current_strategy()

        content_agent = ContentAgent()
        post = content_agent.generate_post(strategy)

        print("\n" + "=" * 80)
        print("GENERATED POST")
        print("=" * 80)
        print(f"Topic: {post['topic']}")
        print(f"Quality Score: {post['quality_score']:.1f}/10")
        print("\nContent:")
        print("-" * 80)
        print(post['content'])
        print("-" * 80)

        logger.info("\n✓ Post generated successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to generate post: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def run_once():
    """Run one complete cycle in dry-run mode"""
    logger.info("=" * 80)
    logger.info("RUN ONCE: Single Autonomous Cycle (Dry Run)")
    logger.info("=" * 80)

    try:
        from core.orchestrator import run_autonomous_cycle

        logger.info("\nRunning complete autonomous cycle...")
        logger.info("(This is DRY RUN - nothing will be posted)\n")

        result = run_autonomous_cycle(dry_run=True)

        logger.info("\n" + "=" * 80)
        logger.info("CYCLE SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Post generated: {result.get('post_generated', False)}")
        if result.get('post_generated'):
            logger.info(f"  Topic: {result['post_data'].get('topic', 'N/A')}")
            logger.info(f"  Quality: {result['post_data'].get('quality_score', 0):.1f}/10")
        logger.info(f"Comments made: {result.get('comments_made', 0)} (dry run)")
        logger.info(f"Insights found: {len(result.get('insights', []))}")
        logger.info("=" * 80)

        return True

    except Exception as e:
        logger.error(f"❌ Cycle failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def start_autonomous():
    """Start autonomous mode"""
    logger.info("=" * 80)
    logger.info("START: Autonomous Mode")
    logger.info("=" * 80)

    from dotenv import load_dotenv
    load_dotenv()

    dry_run = os.getenv('DRY_RUN_MODE', 'true').lower() == 'true'
    auto_post = os.getenv('ENABLE_AUTO_POSTING', 'false').lower() == 'true'
    auto_comment = os.getenv('ENABLE_AUTO_COMMENTING', 'false').lower() == 'true'

    logger.info("\nCurrent Configuration:")
    logger.info(f"  Dry Run Mode: {dry_run}")
    logger.info(f"  Auto Posting: {auto_post}")
    logger.info(f"  Auto Commenting: {auto_comment}")

    if dry_run:
        logger.warning("\n⚠ Running in DRY RUN mode")
        logger.info("   To enable live mode, edit .env:")
        logger.info("   DRY_RUN_MODE=false")

    if not auto_post and not auto_comment:
        logger.warning("\n⚠ Both auto-posting and auto-commenting are disabled")
        logger.info("   To enable, edit .env:")
        logger.info("   ENABLE_AUTO_POSTING=true")
        logger.info("   ENABLE_AUTO_COMMENTING=true")

    logger.info("\n" + "=" * 80)
    logger.info("Starting scheduled autonomous mode...")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 80 + "\n")

    try:
        from main import run_scheduled
        run_scheduled()
    except KeyboardInterrupt:
        logger.info("\n\nStopping autonomous mode...")
        logger.info("Goodbye!")
    except Exception as e:
        logger.error(f"❌ Failed to start: {e}")
        import traceback
        logger.error(traceback.format_exc())


def stats():
    """View statistics"""
    from database.models import Post, Comment, Metric, Learning, get_session
    from datetime import datetime, timedelta

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


def main():
    parser = argparse.ArgumentParser(
        description='Prog Silo Company - Autonomous LinkedIn Agent',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py setup       # First time setup
  python run.py test        # Test all components
  python run.py generate    # Generate a test post
  python run.py once        # Run one cycle (dry-run)
  python run.py start       # Start autonomous mode
  python run.py stats       # View statistics

For more help, see README.md or QUICKSTART.md
        """
    )

    parser.add_argument(
        'command',
        choices=['setup', 'test', 'generate', 'once', 'start', 'stats'],
        help='Command to run'
    )

    args = parser.parse_args()

    # Configure logging
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )

    # Execute command
    if args.command == 'setup':
        setup()
    elif args.command == 'test':
        test()
    elif args.command == 'generate':
        generate()
    elif args.command == 'once':
        run_once()
    elif args.command == 'start':
        start_autonomous()
    elif args.command == 'stats':
        stats()


if __name__ == '__main__':
    main()
