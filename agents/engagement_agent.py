"""
Engagement Agent - Finds and comments on relevant LinkedIn posts
"""
from typing import Dict, List
from datetime import datetime
from loguru import logger
from core.ollama_client import get_ollama_client
from core.linkedin_client import get_linkedin_client
from database.models import Comment, Learning, get_session
import random


class EngagementAgent:
    """Autonomous agent that engages with LinkedIn posts"""

    def __init__(self):
        self.ollama = get_ollama_client()
        self.name = "EngagementAgent"

    def find_and_engage(
        self,
        strategy: Dict,
        num_comments: int = 5,
        dry_run: bool = True
    ) -> List[Dict]:
        """
        Find relevant posts and comment on them

        Args:
            strategy: Current strategy with target hashtags
            num_comments: Number of posts to comment on
            dry_run: If True, don't actually post comments

        Returns:
            List of comment results
        """
        logger.info(f"Finding {num_comments} posts to engage with...")

        # Get target hashtags from strategy
        hashtags = strategy.get('target_hashtags', ['programming', 'softwaredevelopment'])

        # Select random hashtag for variety
        hashtag = random.choice(hashtags)

        results = []

        with get_linkedin_client(headless=True) as linkedin:
            if not linkedin.login():
                logger.error("Failed to login to LinkedIn")
                return results

            # Search for posts
            posts = linkedin.search_posts(hashtag, limit=num_comments * 3)

            if not posts:
                logger.warning(f"No posts found for #{hashtag}")
                return results

            # Filter and select best posts
            selected_posts = self._select_best_posts(
                posts,
                num_comments,
                strategy
            )

            # Comment on each selected post
            for post in selected_posts:
                try:
                    comment_data = self._generate_comment(post)

                    if comment_data['quality_score'] >= strategy.get('min_comment_quality_score', 7):
                        success = linkedin.comment_on_post(
                            post['url'],
                            comment_data['comment'],
                            dry_run=dry_run
                        )

                        if success:
                            self._save_comment(post, comment_data)
                            results.append({
                                'post_url': post['url'],
                                'comment': comment_data['comment'],
                                'success': True
                            })
                        else:
                            results.append({
                                'post_url': post['url'],
                                'success': False,
                                'error': 'Failed to post'
                            })

                    else:
                        logger.info(f"Skipping low quality comment (score: {comment_data['quality_score']:.1f})")

                    # Human-like delay between comments
                    import time
                    time.sleep(random.uniform(30, 90))

                except Exception as e:
                    logger.error(f"Failed to comment on post: {e}")
                    continue

        logger.info(f"Successfully commented on {len([r for r in results if r.get('success')])} posts")
        return results

    def _select_best_posts(
        self,
        posts: List[Dict],
        num_select: int,
        strategy: Dict
    ) -> List[Dict]:
        """
        Select best posts to comment on based on strategy

        Args:
            posts: List of post dicts
            num_select: Number to select
            strategy: Strategy with targeting criteria

        Returns:
            Selected posts
        """
        scored_posts = []

        for post in posts:
            score = self._score_post_relevance(post, strategy)
            scored_posts.append((score, post))

        # Sort by score and take top N
        scored_posts.sort(key=lambda x: x[0], reverse=True)
        selected = [post for score, post in scored_posts[:num_select]]

        logger.info(f"Selected {len(selected)} posts out of {len(posts)}")
        return selected

    def _score_post_relevance(self, post: Dict, strategy: Dict) -> float:
        """Score how relevant a post is for engagement"""
        score = 5.0  # Base score

        content = post.get('content', '').lower()

        # Check for relevant keywords
        relevant_keywords = ['developer', 'programming', 'code', 'software', 'tech', 'career', 'learning']
        keyword_matches = sum(1 for kw in relevant_keywords if kw in content)
        score += keyword_matches * 0.5

        # Prefer posts with questions (more engagement opportunity)
        if '?' in content:
            score += 1.0

        # Avoid overly long posts (harder to comment meaningfully)
        if len(content) > 1000:
            score -= 1.0

        return score

    def _generate_comment(self, post: Dict) -> Dict:
        """
        Generate thoughtful comment for a post

        Args:
            post: Post dict with content and author

        Returns:
            Dict with 'comment' and 'quality_score'
        """
        logger.debug(f"Generating comment for post by {post.get('author', 'unknown')}")

        # Get best commenting strategies from learnings
        strategies = self._get_comment_strategies()

        system_prompt = """You are commenting as Prog Silo Company, a tech coaching brand.

Your commenting style:
- Add genuine value to the conversation
- Be professional but friendly
- Share relevant insights or experiences
- Ask thoughtful follow-up questions
- NO self-promotion or sales
- NO generic praise ("Great post!")
- Keep it 2-4 sentences

Goal: Build relationships and demonstrate expertise authentically."""

        prompt = f"""Write a thoughtful comment on this LinkedIn post.

Post by {post.get('author', 'Unknown')}:
{post.get('content', '')[:500]}

Best practices from past experience:
{strategies}

Write your comment now (2-4 sentences, valuable, engaging):"""

        comment = self.ollama.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7
        ).strip()

        # Remove quotes if wrapped
        if comment.startswith('"') and comment.endswith('"'):
            comment = comment[1:-1]

        # Score quality
        quality_score = self._score_comment_quality(comment, post)

        return {
            'comment': comment,
            'quality_score': quality_score
        }

    def _score_comment_quality(self, comment: str, post: Dict) -> float:
        """Score comment quality"""
        criteria = """
        - Adds genuine value to the conversation
        - Relevant to the original post
        - Professional tone
        - 2-4 sentences (not too short or long)
        - Specific and thoughtful (not generic)
        - Engaging without being salesy
        """

        score = self.ollama.score_text(comment, criteria, scale=10)
        return score

    def _get_comment_strategies(self) -> str:
        """Get successful comment strategies from learnings"""
        session = get_session()
        try:
            learnings = session.query(Learning).filter(
                Learning.active == True,
                Learning.category == 'engagement'
            ).order_by(
                Learning.confidence.desc()
            ).limit(3).all()

            if not learnings:
                return "- Share relevant personal experience\n- Ask thoughtful questions\n- Add practical insights"

            return "\n".join([f"- {l.insight}" for l in learnings])
        finally:
            session.close()

    def _save_comment(self, post: Dict, comment_data: Dict):
        """Save comment to database"""
        session = get_session()
        try:
            comment = Comment(
                post_url=post.get('url', ''),
                post_author=post.get('author', ''),
                comment_text=comment_data['comment'],
                commented_at=datetime.utcnow(),
                quality_score=comment_data['quality_score']
            )
            session.add(comment)
            session.commit()
            logger.debug(f"Saved comment to database (ID: {comment.id})")
        finally:
            session.close()


# Convenience function
def engage_with_posts(strategy: Dict, num_comments: int = 5, dry_run: bool = True) -> List[Dict]:
    """Engage with posts using EngagementAgent"""
    agent = EngagementAgent()
    return agent.find_and_engage(strategy, num_comments, dry_run)
