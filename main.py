#!/usr/bin/env python3
"""
Prog Silo Company - Autonomous LinkedIn Agent
Main entry point for running the system
"""
import os
import sys
from datetime import datetime, time as dt_time
from dotenv import load_dotenv
from loguru import logger
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from core.orchestrator import run_autonomous_cycle
from database.models import init_db

# Load environment
load_dotenv()

# Configure logging
logger.remove()  # Remove default handler
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/progsilo_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="DEBUG"
)


def initialize():
    """Initialize the system"""
    logger.info("=" * 80)
    logger.info("PROG SILO COMPANY - AUTONOMOUS LINKEDIN AGENT")
    logger.info("=" * 80)

    # Initialize database
    logger.info("Initializing database...")
    try:
        init_db()
        logger.info("✓ Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sys.exit(1)

    # Check Ollama
    logger.info("Checking Ollama connection...")
    try:
        from core.ollama_client import get_ollama_client
        ollama = get_ollama_client()
        if ollama.test_connection():
            logger.info("✓ Ollama connected")
        else:
            logger.warning("⚠ Ollama connection test failed")
    except Exception as e:
        logger.error(f"Failed to connect to Ollama: {e}")
        logger.error("Make sure Ollama is running: ollama serve")
        sys.exit(1)

    # Check configuration
    logger.info("Checking configuration...")
    dry_run = os.getenv('DRY_RUN_MODE', 'true').lower() == 'true'
    auto_post = os.getenv('ENABLE_AUTO_POSTING', 'false').lower() == 'true'
    auto_comment = os.getenv('ENABLE_AUTO_COMMENTING', 'false').lower() == 'true'

    logger.info(f"  Dry Run Mode: {dry_run}")
    logger.info(f"  Auto Posting: {auto_post}")
    logger.info(f"  Auto Commenting: {auto_comment}")

    if dry_run:
        logger.warning("⚠ Running in DRY RUN mode - no actual posts/comments will be made")
    else:
        logger.info("✓ Running in LIVE mode")

    logger.info("=" * 80)


def run_daily_cycle():
    """Run the daily agent cycle"""
    logger.info(f"🌅 Starting daily cycle at {datetime.now()}")

    try:
        # Determine if dry run
        dry_run = os.getenv('DRY_RUN_MODE', 'true').lower() == 'true'

        # Run the orchestrator
        result = run_autonomous_cycle(dry_run=dry_run)

        # Log summary
        logger.info("✓ Daily cycle completed successfully")
        logger.info(f"  - Post generated: {result.get('post_generated', False)}")
        logger.info(f"  - Post published: {result.get('post_published', False)}")
        logger.info(f"  - Comments made: {result.get('comments_made', 0)}")
        logger.info(f"  - Insights: {len(result.get('insights', []))}")

    except Exception as e:
        logger.error(f"❌ Daily cycle failed: {e}")
        import traceback
        logger.error(traceback.format_exc())


def run_manual():
    """Run once manually (for testing)"""
    initialize()
    logger.info("Running manual cycle (one-time)...")
    run_daily_cycle()
    logger.info("Manual cycle complete")


def run_scheduled():
    """Run on schedule (autonomous)"""
    initialize()

    # Get posting time from environment
    posting_time = os.getenv('POSTING_TIME', '08:00')
    hour, minute = map(int, posting_time.split(':'))

    logger.info(f"⏰ Scheduling daily cycles at {posting_time}")

    # Create scheduler
    scheduler = BlockingScheduler()

    # Schedule daily cycle
    scheduler.add_job(
        run_daily_cycle,
        CronTrigger(hour=hour, minute=minute),
        id='daily_cycle',
        name='Daily LinkedIn Agent Cycle',
        replace_existing=True
    )

    # Also run engagement every 3 hours throughout the day
    # This spreads out comments more naturally
    def run_engagement_only():
        """Run just engagement (comments) without posting"""
        logger.info("💬 Running engagement cycle...")
        try:
            from agents.engagement_agent import EngagementAgent
            from agents.strategy_agent import StrategyAgent

            strategy_agent = StrategyAgent()
            strategy = strategy_agent.get_current_strategy()

            engagement_agent = EngagementAgent()
            dry_run = os.getenv('DRY_RUN_MODE', 'true').lower() == 'true'

            # Comment on 8-10 posts (spread throughout day)
            results = engagement_agent.find_and_engage(
                strategy=strategy,
                num_comments=8,
                dry_run=dry_run
            )

            success_count = len([r for r in results if r.get('success', False)])
            logger.info(f"✓ Engagement cycle: {success_count} comments made")

        except Exception as e:
            logger.error(f"Engagement cycle failed: {e}")

    # Schedule engagement throughout the day (10 AM, 1 PM, 4 PM, 7 PM)
    for hour in [10, 13, 16, 19]:
        scheduler.add_job(
            run_engagement_only,
            CronTrigger(hour=hour, minute=0),
            id=f'engagement_{hour}',
            name=f'Engagement Cycle {hour}:00',
            replace_existing=True
        )

    logger.info("✓ Scheduler configured")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 80)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down scheduler...")
        scheduler.shutdown()
        logger.info("Goodbye!")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Prog Silo Company - Autonomous LinkedIn Agent'
    )
    parser.add_argument(
        'mode',
        choices=['manual', 'scheduled'],
        nargs='?',
        default='scheduled',
        help='Run mode: manual (once) or scheduled (autonomous)'
    )

    args = parser.parse_args()

    if args.mode == 'manual':
        run_manual()
    else:
        run_scheduled()


if __name__ == '__main__':
    main()
