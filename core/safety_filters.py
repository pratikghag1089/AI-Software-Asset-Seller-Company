"""
Safety filters and rate limiting to prevent spam and policy violations
"""
import time
import re
from typing import Dict, Optional
from datetime import datetime, timedelta
from loguru import logger
from functools import wraps


class SafetyFilter:
    """Content safety filters"""

    # Blocked keywords - political, controversial, spam
    BLOCKED_KEYWORDS = [
        # Political
        'trump', 'biden', 'election', 'vote', 'political party',
        'liberal', 'conservative', 'democrat', 'republican',

        # Religious
        'jesus', 'allah', 'buddha', 'religion', 'bible', 'quran',

        # Controversial
        'abortion', 'gun control', 'immigration policy',

        # Spam
        'buy now', 'click here', 'limited time offer', 'act now',
        'guaranteed', 'make money fast', 'work from home',

        # Inappropriate
        'nsfw', 'xxx', 'explicit'
    ]

    # Spam patterns
    SPAM_PATTERNS = [
        r'https?://bit\.ly',  # Shortened URLs
        r'https?://tinyurl',
        r'\$\$\$',  # Money symbols
        r'!!!{3,}',  # Excessive exclamation
        r'CAPS{5,}',  # Excessive caps (pattern)
        r'🔥{3,}',  # Excessive emojis
    ]

    @staticmethod
    def is_safe(text: str) -> tuple[bool, Optional[str]]:
        """
        Check if content is safe to post

        Returns:
            (is_safe, reason_if_not_safe)
        """
        text_lower = text.lower()

        # Check blocked keywords
        for keyword in SafetyFilter.BLOCKED_KEYWORDS:
            if keyword in text_lower:
                return False, f"Contains blocked keyword: {keyword}"

        # Check spam patterns
        for pattern in SafetyFilter.SPAM_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return False, f"Matches spam pattern: {pattern}"

        # Check excessive caps
        if len(text) > 50:
            caps_ratio = sum(1 for c in text if c.isupper()) / len(text)
            if caps_ratio > 0.5:
                return False, "Excessive capitalization"

        # Check excessive punctuation
        punct_count = sum(1 for c in text if c in '!?')
        if punct_count > 5:
            return False, "Excessive punctuation"

        # Check minimum length for posts
        if len(text) < 50:
            return False, "Content too short (min 50 characters)"

        # Check maximum length for posts
        if len(text) > 3000:
            return False, "Content too long (max 3000 characters)"

        return True, None

    @staticmethod
    def is_professional(text: str) -> bool:
        """Check if text maintains professional tone"""
        text_lower = text.lower()

        unprofessional_words = [
            'stupid', 'dumb', 'idiot', 'hate', 'sucks',
            'crap', 'terrible', 'awful', 'worst ever'
        ]

        for word in unprofessional_words:
            if word in text_lower:
                return False

        return True


class RateLimiter:
    """Rate limiting to avoid spam detection"""

    def __init__(self):
        self.action_history: Dict[str, list] = {
            'post': [],
            'comment': [],
            'connection': []
        }

    def can_perform(self, action: str) -> tuple[bool, Optional[str]]:
        """
        Check if action can be performed within rate limits

        Args:
            action: 'post', 'comment', or 'connection'

        Returns:
            (can_perform, reason_if_not)
        """
        now = datetime.now()
        history = self.action_history.get(action, [])

        # Clean old entries (older than 24 hours)
        history = [ts for ts in history if now - ts < timedelta(hours=24)]
        self.action_history[action] = history

        # Define limits per 24 hours
        limits = {
            'post': 3,  # Max 3 posts per day
            'comment': 40,  # Max 40 comments per day
            'connection': 50  # Max 50 connection requests per day
        }

        if len(history) >= limits.get(action, 10):
            return False, f"Rate limit reached: {len(history)}/{limits[action]} per day"

        # Check minimum time between actions
        if history:
            last_action = history[-1]
            min_delays = {
                'post': timedelta(hours=6),  # Min 6 hours between posts
                'comment': timedelta(minutes=2),  # Min 2 min between comments
                'connection': timedelta(minutes=1)
            }

            min_delay = min_delays.get(action, timedelta(minutes=5))
            if now - last_action < min_delay:
                wait_time = (min_delay - (now - last_action)).seconds
                return False, f"Too soon. Wait {wait_time} seconds"

        return True, None

    def record_action(self, action: str):
        """Record that an action was performed"""
        if action not in self.action_history:
            self.action_history[action] = []

        self.action_history[action].append(datetime.now())
        logger.debug(f"Recorded {action} at {datetime.now()}")

    def human_delay(self, min_seconds: int = 2, max_seconds: int = 5):
        """Add human-like random delay"""
        import random
        delay = random.uniform(min_seconds, max_seconds)
        logger.debug(f"Human-like delay: {delay:.1f}s")
        time.sleep(delay)


# Global rate limiter instance
_rate_limiter = RateLimiter()


def rate_limited(action: str):
    """Decorator for rate-limited functions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            can_perform, reason = _rate_limiter.can_perform(action)

            if not can_perform:
                logger.warning(f"Rate limit: {reason}")
                return None

            result = func(*args, **kwargs)

            _rate_limiter.record_action(action)
            _rate_limiter.human_delay()

            return result
        return wrapper
    return decorator


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance"""
    return _rate_limiter


# Content validation wrapper
def validate_content(content: str, content_type: str = "post") -> bool:
    """
    Validate content before posting/commenting

    Args:
        content: Text content
        content_type: 'post' or 'comment'

    Returns:
        True if valid, False otherwise
    """
    # Safety check
    is_safe, reason = SafetyFilter.is_safe(content)
    if not is_safe:
        logger.warning(f"Content blocked: {reason}")
        return False

    # Professional check
    if not SafetyFilter.is_professional(content):
        logger.warning("Content not professional enough")
        return False

    # Length checks for comments
    if content_type == "comment":
        if len(content) < 20:
            logger.warning("Comment too short (min 20 chars)")
            return False
        if len(content) > 500:
            logger.warning("Comment too long (max 500 chars)")
            return False

    logger.debug(f"Content validated successfully ({len(content)} chars)")
    return True
