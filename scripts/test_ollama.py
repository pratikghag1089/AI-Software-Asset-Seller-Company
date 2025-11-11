#!/usr/bin/env python3
"""
Test Ollama connection and gpt-oss model
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.ollama_client import get_ollama_client
from loguru import logger

if __name__ == '__main__':
    logger.info("Testing Ollama connection...")

    try:
        ollama = get_ollama_client()

        # Test basic generation
        logger.info("Test 1: Basic generation")
        response = ollama.generate("Say 'Hello from Prog Silo!'", temperature=0.5)
        logger.info(f"Response: {response}")

        # Test scoring
        logger.info("\nTest 2: Scoring")
        text = "Python is a great programming language for beginners."
        score = ollama.score_text(text, "grammatical correctness and clarity", scale=10)
        logger.info(f"Score: {score}/10")

        # Test structured output
        logger.info("\nTest 3: Structured output (JSON)")
        structured = ollama.generate_structured(
            prompt="List 3 programming languages as JSON array with 'name' and 'difficulty' fields",
            temperature=0.3
        )
        logger.info(f"Structured: {structured}")

        logger.info("\n✓ All tests passed!")

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise
