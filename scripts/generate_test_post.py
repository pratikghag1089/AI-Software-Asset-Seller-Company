#!/usr/bin/env python3
"""
Generate a test LinkedIn post
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.content_agent import ContentAgent
from agents.strategy_agent import StrategyAgent
from loguru import logger

if __name__ == '__main__':
    logger.info("Generating test post...\n")

    try:
        # Get strategy
        strategy_agent = StrategyAgent()
        strategy = strategy_agent.get_current_strategy()

        # Generate post
        content_agent = ContentAgent()
        post = content_agent.generate_post(strategy)

        # Display results
        print("=" * 80)
        print("GENERATED POST")
        print("=" * 80)
        print(f"Topic: {post['topic']}")
        print(f"Quality Score: {post['quality_score']:.1f}/10")
        print("\nContent:")
        print("-" * 80)
        print(post['content'])
        print("-" * 80)

        logger.info("\n✓ Post generated successfully!")

    except Exception as e:
        logger.error(f"❌ Failed to generate post: {e}")
        raise
