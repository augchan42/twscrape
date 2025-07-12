"""Twitter thread extraction using twscrape."""

import asyncio
from typing import List, Dict, Any, Optional
from twscrape import API
import logging

logger = logging.getLogger(__name__)

class TwitterThreadExtractor:
    """Extract complete Twitter threads including replies."""
    
    def __init__(self):
        self.api = API()
    
    async def get_complete_thread(self, tweet_id: str, max_depth: int = 3) -> Dict[str, Any]:
        """Get a complete thread starting from a tweet ID."""
        
        thread = {
            "original_tweet": None,
            "replies": [],
            "total_tweets": 0,
            "max_depth": max_depth,
            "error": None
        }
        
        try:
            # Check account status first
            await self._check_accounts()
            
            # Get the original tweet
            logger.info(f"Attempting to fetch tweet: {tweet_id}")
            original_tweet = await self.api.tweet_details(tweet_id)
            
            if not original_tweet:
                error_msg = f"Could not find original tweet: {tweet_id}"
                logger.error(error_msg)
                thread["error"] = error_msg
                return thread
            
            logger.info(f"✅ Successfully found tweet: {tweet_id}")
            thread["original_tweet"] = self._format_tweet(original_tweet)
            
            # Get replies recursively
            replies = await self._get_replies_recursive(tweet_id, depth=0, max_depth=max_depth)
            thread["replies"] = replies
            thread["total_tweets"] = 1 + len(replies)
            
            return thread
            
        except Exception as e:
            error_msg = f"Error extracting thread: {e}"
            logger.error(error_msg)
            thread["error"] = error_msg
            return thread
    
    async def _check_accounts(self):
        """Check account status and provide debugging info."""
        try:
            accounts = await self.api.pool.get_all()
            logger.info(f"Total accounts: {len(accounts)}")
            
            active_accounts = [acc for acc in accounts if acc.active]
            logger.info(f"Active accounts: {len(active_accounts)}")
            
            if not active_accounts:
                logger.warning("⚠️  No active accounts available!")
                logger.info("You may need to:")
                logger.info("1. Get fresh cookies from your Twitter account")
                logger.info("2. Update accounts.txt with new cookies")
                logger.info("3. Re-add accounts: twscrape add_accounts accounts.txt username:password:email:email_password:cookies")
            else:
                logger.info(f"✅ {len(active_accounts)} active accounts available")
                for acc in active_accounts:
                    logger.info(f"  - {acc.username} (last used: {acc.last_used})")
                    
        except Exception as e:
            logger.error(f"Error checking accounts: {e}")
    
    async def _get_replies_recursive(self, tweet_id: str, depth: int, max_depth: int) -> List[Dict[str, Any]]:
        """Recursively get replies to build a thread."""
        
        if depth >= max_depth:
            return []
        
        try:
            logger.info(f"Getting replies for tweet {tweet_id} (depth {depth})")
            replies = await self.api.tweet_replies(tweet_id, limit=20)
            logger.info(f"Found {len(replies)} replies at depth {depth}")
            
            formatted_replies = []
            
            for reply in replies:
                formatted_reply = self._format_tweet(reply)
                
                # Recursively get replies to this reply
                sub_replies = await self._get_replies_recursive(
                    reply.id, depth + 1, max_depth
                )
                formatted_reply["replies"] = sub_replies
                
                formatted_replies.append(formatted_reply)
            
            return formatted_replies
            
        except Exception as e:
            logger.error(f"Error getting replies for {tweet_id}: {e}")
            return []
    
    def _format_tweet(self, tweet) -> Dict[str, Any]:
        """Format a tweet object into a dictionary."""
        return {
            "id": tweet.id,
            "content": tweet.rawContent,
            "author": tweet.user.username if tweet.user else "Unknown",
            "author_id": tweet.user.id if tweet.user else None,
            "date": tweet.date.isoformat() if tweet.date else None,
            "likes": tweet.likeCount,
            "retweets": tweet.retweetCount,
            "replies": tweet.replyCount,
            "quotes": tweet.quoteCount,
            "is_reply": hasattr(tweet, 'inReplyToTweetId') and tweet.inReplyToTweetId,
            "replies": []  # Will be populated by recursive calls
        }
    
    async def get_user_threads(self, username: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get threads from a user's recent tweets."""
        
        try:
            # Get user
            user = await self.api.user_by_login(username)
            if not user:
                logger.error(f"Could not find user: {username}")
                return []
            
            # Get user's tweets
            tweets = await self.api.user_tweets_and_replies(user.id, limit=limit)
            
            threads = []
            for tweet in tweets:
                # Only process tweets that are likely to be thread starters
                if tweet.replyCount > 0 or not tweet.inReplyToTweetId:
                    thread = await self.get_complete_thread(tweet.id, max_depth=2)
                    threads.append(thread)
            
            return threads
            
        except Exception as e:
            logger.error(f"Error getting user threads: {e}")
            return []
    
    async def search_threads(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for tweets and extract threads from results."""
        
        try:
            search_results = await self.api.search(query, limit=limit)
            
            threads = []
            for tweet in search_results:
                # Only process tweets with replies (potential thread starters)
                if tweet.replyCount > 0:
                    thread = await self.get_complete_thread(tweet.id, max_depth=2)
                    threads.append(thread)
            
            return threads
            
        except Exception as e:
            logger.error(f"Error searching threads: {e}")
            return []
    
    def format_thread_as_text(self, thread: Dict[str, Any]) -> str:
        """Format a thread as readable text."""
        
        if thread.get("error"):
            return f"Error: {thread['error']}"
        
        if not thread["original_tweet"]:
            return "Thread not found"
        
        text = []
        original = thread["original_tweet"]
        
        # Original tweet
        text.append(f"🧵 Thread by @{original['author']}")
        text.append(f"📅 {original['date']}")
        text.append(f"❤️ {original['likes']} | 🔄 {original['retweets']} | 💬 {original['replies']}")
        text.append("")
        text.append(original['content'])
        text.append("")
        
        # Add replies
        def add_replies(replies, indent=0):
            for i, reply in enumerate(replies, 1):
                prefix = "  " * indent
                text.append(f"{prefix}{i}. @{reply['author']}: {reply['content']}")
                text.append(f"{prefix}   ❤️ {reply['likes']} | 🔄 {reply['retweets']} | 💬 {reply['replies']}")
                text.append("")
                
                if reply['replies']:
                    add_replies(reply['replies'], indent + 1)
        
        add_replies(thread["replies"])
        
        return "\n".join(text)

# Example usage
async def main():
    extractor = TwitterThreadExtractor()
    
    # Example 1: Get a specific thread
    tweet_id = "1943393540538798263"
    thread = await extractor.get_complete_thread(tweet_id, max_depth=2)
    
    print("=== THREAD EXTRACTION ===")
    print(f"Total tweets in thread: {thread['total_tweets']}")
    
    if thread.get("error"):
        print(f"❌ Error: {thread['error']}")
        print("\nTroubleshooting tips:")
        print("1. Check if your Twitter account has valid cookies")
        print("2. Try getting fresh cookies from your Twitter account")
        print("3. Update accounts.txt and re-add accounts")
        print("4. The tweet might be private or deleted")
    elif thread['original_tweet']:
        print(f"✅ Original tweet: {thread['original_tweet']['content'][:100]}...")
        print(f"Number of replies: {len(thread['replies'])}")
        
        # Format as text
        thread_text = extractor.format_thread_as_text(thread)
        print("\n=== FORMATTED THREAD ===")
        print(thread_text[:500] + "..." if len(thread_text) > 500 else thread_text)
    else:
        print("❌ No tweet found and no error reported")
    
    # Example 2: Search for threads (only if first example worked)
    if not thread.get("error") and thread['original_tweet']:
        print("\n=== SEARCHING FOR THREADS ===")
        search_threads = await extractor.search_threads("elon musk", limit=5)
        print(f"Found {len(search_threads)} potential threads")
    else:
        print("\nSkipping search example due to authentication issues")

if __name__ == "__main__":
    asyncio.run(main()) 