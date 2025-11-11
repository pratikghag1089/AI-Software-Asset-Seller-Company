"""
LinkedIn client for posting and engagement
Supports both web scraping and manual interaction
"""
import os
import time
import random
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv
from loguru import logger
from playwright.sync_api import sync_playwright, Page, Browser, TimeoutError as PlaywrightTimeout

load_dotenv()


class LinkedInClient:
    """Client for LinkedIn automation using Playwright"""

    def __init__(self, headless: bool = True):
        self.email = os.getenv('LINKEDIN_EMAIL')
        self.password = os.getenv('LINKEDIN_PASSWORD')
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.logged_in = False

        if not self.email or not self.password:
            logger.warning("LinkedIn credentials not found in environment")

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

    def start(self):
        """Start browser and initialize"""
        logger.info("Starting LinkedIn client...")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.page = self.browser.new_page()

        # Set realistic user agent
        self.page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

        logger.info("LinkedIn client started")

    def close(self):
        """Close browser and cleanup"""
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("LinkedIn client closed")

    def login(self) -> bool:
        """
        Login to LinkedIn

        Returns:
            True if successful, False otherwise
        """
        if not self.email or not self.password:
            logger.error("LinkedIn credentials not configured")
            return False

        try:
            logger.info("Logging into LinkedIn...")
            self.page.goto('https://www.linkedin.com/login')
            time.sleep(random.uniform(2, 4))

            # Fill in credentials
            self.page.fill('input#username', self.email)
            time.sleep(random.uniform(0.5, 1.5))
            self.page.fill('input#password', self.password)
            time.sleep(random.uniform(0.5, 1.5))

            # Click sign in
            self.page.click('button[type="submit"]')
            time.sleep(random.uniform(4, 6))

            # Check if login successful
            if 'feed' in self.page.url or 'mynetwork' in self.page.url:
                self.logged_in = True
                logger.info("✓ Successfully logged into LinkedIn")
                return True
            else:
                logger.error("Login failed - unexpected redirect")
                return False

        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False

    def post_content(self, content: str, dry_run: bool = True) -> bool:
        """
        Post content to LinkedIn

        Args:
            content: Text content to post
            dry_run: If True, don't actually post

        Returns:
            True if successful
        """
        if dry_run:
            logger.info(f"[DRY RUN] Would post to LinkedIn:\n{content[:100]}...")
            return True

        if not self.logged_in:
            logger.error("Not logged in to LinkedIn")
            return False

        try:
            logger.info("Posting to LinkedIn...")

            # Go to feed
            self.page.goto('https://www.linkedin.com/feed/')
            time.sleep(random.uniform(2, 4))

            # Click "Start a post" button
            self.page.click('button.artdeco-button--muted.artdeco-button--4.artdeco-button--tertiary')
            time.sleep(random.uniform(1, 2))

            # Fill in post content
            editor = self.page.locator('div.ql-editor')
            editor.click()
            time.sleep(0.5)
            editor.fill(content)
            time.sleep(random.uniform(1, 2))

            # Click Post button
            self.page.click('button.share-actions__primary-action')
            time.sleep(random.uniform(3, 5))

            logger.info("✓ Successfully posted to LinkedIn")
            return True

        except Exception as e:
            logger.error(f"Failed to post: {e}")
            return False

    def search_posts(self, hashtag: str, limit: int = 10) -> List[Dict]:
        """
        Search for posts by hashtag

        Args:
            hashtag: Hashtag to search (without #)
            limit: Maximum posts to return

        Returns:
            List of post dictionaries
        """
        if not self.logged_in:
            logger.error("Not logged in to LinkedIn")
            return []

        try:
            logger.info(f"Searching for #{hashtag} posts...")

            # Navigate to search
            search_url = f'https://www.linkedin.com/search/results/content/?keywords=%23{hashtag}&sortBy="date_posted"'
            self.page.goto(search_url)
            time.sleep(random.uniform(3, 5))

            # Scroll to load more posts
            for _ in range(3):
                self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                time.sleep(random.uniform(1, 2))

            # Extract posts
            posts = []
            post_elements = self.page.locator('div.feed-shared-update-v2').all()[:limit]

            for element in post_elements:
                try:
                    post_data = {
                        'url': element.locator('a[href*="/feed/update/"]').get_attribute('href'),
                        'author': element.locator('span.feed-shared-actor__name').inner_text(),
                        'content': element.locator('div.feed-shared-text').inner_text()[:500],
                        'timestamp': datetime.now().isoformat()
                    }
                    posts.append(post_data)
                except Exception as e:
                    logger.debug(f"Failed to extract post data: {e}")
                    continue

            logger.info(f"Found {len(posts)} posts")
            return posts

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def comment_on_post(self, post_url: str, comment: str, dry_run: bool = True) -> bool:
        """
        Comment on a LinkedIn post

        Args:
            post_url: URL of the post
            comment: Comment text
            dry_run: If True, don't actually comment

        Returns:
            True if successful
        """
        if dry_run:
            logger.info(f"[DRY RUN] Would comment on {post_url}:\n{comment[:100]}...")
            return True

        if not self.logged_in:
            logger.error("Not logged in to LinkedIn")
            return False

        try:
            logger.info(f"Commenting on post: {post_url[:50]}...")

            self.page.goto(post_url)
            time.sleep(random.uniform(2, 4))

            # Click comment button to expand
            try:
                self.page.click('button.comment-button')
                time.sleep(random.uniform(1, 2))
            except:
                pass

            # Find comment box and click
            comment_box = self.page.locator('div.ql-editor[data-placeholder="Add a comment…"]')
            comment_box.click()
            time.sleep(0.5)

            # Type comment
            comment_box.fill(comment)
            time.sleep(random.uniform(1, 2))

            # Submit comment
            self.page.click('button.comments-comment-box__submit-button')
            time.sleep(random.uniform(2, 3))

            logger.info("✓ Successfully commented")
            return True

        except Exception as e:
            logger.error(f"Failed to comment: {e}")
            return False

    def get_profile_stats(self) -> Dict:
        """
        Get current profile statistics

        Returns:
            Dict with followers, views, etc.
        """
        if not self.logged_in:
            logger.error("Not logged in to LinkedIn")
            return {}

        try:
            logger.info("Fetching profile stats...")

            self.page.goto('https://www.linkedin.com/in/me/')
            time.sleep(random.uniform(2, 4))

            stats = {
                'followers': 0,
                'connections': 0,
                'profile_views': 0,
                'timestamp': datetime.now().isoformat()
            }

            # Try to extract followers (this varies based on LinkedIn UI)
            try:
                followers_text = self.page.locator('text=/followers/i').first.inner_text()
                stats['followers'] = int(''.join(filter(str.isdigit, followers_text)))
            except:
                logger.debug("Could not extract followers")

            logger.info(f"Profile stats: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Failed to get profile stats: {e}")
            return {}


# Helper function for easy access
def get_linkedin_client(headless: bool = True) -> LinkedInClient:
    """Create and return LinkedIn client"""
    return LinkedInClient(headless=headless)
