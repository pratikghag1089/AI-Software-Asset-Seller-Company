"""
Ollama client for local LLM inference using gpt-oss:latest
"""
import ollama
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


class OllamaClient:
    """Client for interacting with Ollama GPT-OSS model"""

    def __init__(self):
        self.host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self.model = os.getenv('OLLAMA_MODEL', 'gpt-oss:latest')
        logger.info(f"Initialized Ollama client: {self.host} with model {self.model}")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate text using Ollama

        Args:
            prompt: User prompt
            system_prompt: System instruction
            temperature: Randomness (0.0 = deterministic, 1.0 = creative)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        try:
            messages = []

            if system_prompt:
                messages.append({
                    'role': 'system',
                    'content': system_prompt
                })

            messages.append({
                'role': 'user',
                'content': prompt
            })

            options = {
                'temperature': temperature,
            }

            if max_tokens:
                options['num_predict'] = max_tokens

            response = ollama.chat(
                model=self.model,
                messages=messages,
                options=options
            )

            result = response['message']['content']
            logger.debug(f"Generated {len(result)} characters")
            return result

        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise

    def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> Dict:
        """
        Generate structured output (expects JSON response)

        Args:
            prompt: User prompt (should request JSON)
            system_prompt: System instruction
            temperature: Randomness

        Returns:
            Parsed JSON dict
        """
        import json

        full_system = system_prompt or ""
        full_system += "\n\nIMPORTANT: Respond with valid JSON only. No markdown, no explanations."

        response = self.generate(
            prompt=prompt,
            system_prompt=full_system,
            temperature=temperature
        )

        # Try to extract JSON if wrapped in markdown
        if '```json' in response:
            response = response.split('```json')[1].split('```')[0].strip()
        elif '```' in response:
            response = response.split('```')[1].split('```')[0].strip()

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {response[:200]}")
            raise ValueError(f"Invalid JSON response: {e}")

    def score_text(
        self,
        text: str,
        criteria: str,
        scale: int = 10
    ) -> float:
        """
        Score text based on criteria

        Args:
            text: Text to score
            criteria: Scoring criteria
            scale: Scale (default 1-10)

        Returns:
            Score as float
        """
        prompt = f"""Score the following text on a scale of 1-{scale} based on: {criteria}

Text:
{text}

Respond with ONLY a number (e.g., 7.5). No explanation."""

        response = self.generate(prompt, temperature=0.3)

        try:
            # Extract first number found
            import re
            numbers = re.findall(r'\d+\.?\d*', response)
            if numbers:
                score = float(numbers[0])
                return min(max(score, 1.0), float(scale))  # Clamp to scale
            else:
                logger.warning(f"No number found in score response: {response}")
                return 5.0  # Default middle score
        except Exception as e:
            logger.error(f"Failed to parse score: {e}")
            return 5.0

    def test_connection(self) -> bool:
        """Test if Ollama is accessible"""
        try:
            response = self.generate("Reply with 'OK'", temperature=0.0)
            logger.info(f"Ollama connection test successful: {response[:50]}")
            return True
        except Exception as e:
            logger.error(f"Ollama connection test failed: {e}")
            return False


# Singleton instance
_ollama_client = None


def get_ollama_client() -> OllamaClient:
    """Get or create Ollama client singleton"""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client
