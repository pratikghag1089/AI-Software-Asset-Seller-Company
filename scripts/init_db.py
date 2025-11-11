#!/usr/bin/env python3
"""
Initialize the database
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

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
