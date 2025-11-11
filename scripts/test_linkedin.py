#!/usr/bin/env python3
"""
Test LinkedIn client connection
"""
from core.linkedin_client import get_linkedin_client
from loguru import logger
import os

if __name__ == '__main__':
    logger.info("Testing LinkedIn connection...")

    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')

    if not email or not password:
        logger.error("LinkedIn credentials not configured in .env file")
        logger.info("Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD")
        exit(1)

    logger.info(f"Using account: {email}")

    try:
        with get_linkedin_client(headless=False) as linkedin:
            logger.info("Attempting to login...")
            if linkedin.login():
                logger.info("✓ Successfully logged in!")

                # Get profile stats
                stats = linkedin.get_profile_stats()
                logger.info(f"Profile stats: {stats}")

                logger.info("\n✓ LinkedIn client working!")
            else:
                logger.error("❌ Login failed")
                logger.error("Check your credentials in .env file")

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise
