#!/usr/bin/env python3
"""
Initialize the database
"""
from database.models import init_db
from loguru import logger

if __name__ == '__main__':
    logger.info("Initializing database...")
    try:
        engine = init_db()
        logger.info(f"✓ Database initialized successfully")
        logger.info(f"  Engine: {engine.url}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
