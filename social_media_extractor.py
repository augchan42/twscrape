"""Social media content extraction using snscrape."""

import logging
import re
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse
from datetime import datetime
import certifi
import os
import asyncio
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

# Try to import twscrape
try:
    import twscrape
    TWSCRAPE_AVAILABLE = True
except ImportError:
    TWSCRAPE_AVAILABLE = False
    logging.warning("twscrape not available. Install with: pip install twscrape")

logger = logging.getLogger(__name__)

class SocialMediaExtractor:
    """Extracts content from social media platforms like Twitter/X."""
    
    def __init__(self):
        if not TWSCRAPE_AVAILABLE:
            logger.warning("twscrape not available. Social media extraction will not work.")
        else:
            # Initialize twscrape API
            logger.info("Initializing twscrape API...")
            self.api = twscrape.API()
            logger.info("twscrape API initialized successfully")
            
            # Log pool information
            logger.info(f"twscrape pool type: {type(self.api.pool)}")
            logger.info(f"twscrape pool: {self.api.pool}")
    
    async def _check_accounts(self):
        """Check if twscrape accounts are available."""
        if not TWSCRAPE_AVAILABLE:
            logger.warning("twscrape not available for account checking")
            return
        
        try:
            logger.info("=== TWSCRAPE ACCOUNT CHECK ===")
            logger.info("Fetching twscrape accounts...")
            
            # Get all accounts
            accounts = await self.api.pool.get_all()
            logger.info(f"Total accounts found: {len(accounts)}")
            
            if len(accounts) == 0:
                logger.warning("❌ No Twitter accounts configured in twscrape!")
                logger.warning("You need to add accounts for it to work.")
                logger.warning("Run: twscrape add_accounts accounts.txt username:password:email:email_password:cookies")
                return
            
            # Log detailed account information
            logger.info("=== ACCOUNT DETAILS ===")
            for i, account in enumerate(accounts):
                logger.info(f"Account {i+1}:")
                logger.info(f"  - Username: {account.username}")
                logger.info(f"  - Active: {account.active}")
                logger.info(f"  - Last used: {account.last_used}")
                logger.info(f"  - Total requests: {sum(account.stats.values())}")
                logger.info(f"  - Error message: {account.error_msg}")
                logger.info(f"  - Stats: {account.stats}")
                
                # Check if account has valid cookies
                has_ct0 = 'ct0' in account.cookies
                logger.info(f"  - Has ct0 cookie: {has_ct0}")
                if has_ct0:
                    logger.info(f"  - ct0 cookie: {account.cookies['ct0'][:20]}...")
                
            # Check login status
            logger.info("=== LOGIN STATUS ===")
            active_count = sum(1 for acc in accounts if acc.active)
            logger.info(f"Active accounts: {active_count}/{len(accounts)}")
            
            if active_count == 0:
                logger.warning("⚠️  No accounts are active!")
                logger.info("You may need to run: twscrape login_accounts")
                logger.info("Or get fresh cookies and re-add accounts")
            else:
                logger.info("✅ Some accounts are active and ready to use")
                
            # Try to get accounts info using the proper method
            try:
                logger.info("=== ACCOUNTS INFO ===")
                accounts_info = await self.api.pool.accounts_info()
                logger.info(f"Accounts info method result: {accounts_info}")
            except Exception as info_e:
                logger.error(f"Could not get accounts info: {info_e}")
                
        except Exception as e:
            logger.error(f"❌ Could not check twscrape accounts: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception details: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def is_twitter_url(self, url: str) -> bool:
        """Check if URL is a Twitter/X URL."""
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        return netloc in ['twitter.com', 'x.com', 'www.twitter.com', 'www.x.com']
    
    def extract_twitter_id_from_url(self, url: str) -> Optional[str]:
        """Extract Twitter/X post ID from URL."""
        if not self.is_twitter_url(url):
            return None
        
        # Patterns for Twitter/X URLs
        patterns = [
            r'twitter\.com/\w+/status/(\d+)',
            r'x\.com/\w+/status/(\d+)',
            r'twitter\.com/i/status/(\d+)',
            r'x\.com/i/status/(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    async def _diagnose_tweet_accessibility(self, tweet_id: str) -> Dict[str, Any]:
        """Diagnose why a specific tweet might not be accessible."""
        diagnosis: Dict[str, Any] = {
            "tweet_id": tweet_id,
            "accessible": False,
            "reasons": [],
            "suggestions": []
        }
        reasons: List[str] = diagnosis["reasons"]
        suggestions: List[str] = diagnosis["suggestions"]
        
        logger.info(f"🔍 Diagnosing accessibility for tweet {tweet_id}")
        
        # Test 1: Try tweet_details
        try:
            tweet = await self.api.tweet_details(tweet_id)
            if tweet:
                diagnosis["accessible"] = True
                reasons.append("tweet_details method succeeded")
                return diagnosis
            else:
                reasons.append("tweet_details returned None")
        except Exception as e:
            reasons.append(f"tweet_details failed: {e}")
        
        # Test 2: Try search method
        try:
            search_results = []
            async for tweet in self.api.search(f"id:{tweet_id}", limit=1):
                search_results.append(tweet)
                break
            
            if search_results and len(search_results) > 0:
                diagnosis["accessible"] = True
                reasons.append("search method succeeded")
                return diagnosis
            else:
                reasons.append("search returned no results")
        except Exception as e:
            reasons.append(f"search failed: {e}")
        
        # Test 3: Try raw request to get more details
        try:
            raw_response = await self.api.tweet_details_raw(tweet_id)
            if raw_response:
                if raw_response.status_code == 200:
                    data = raw_response.json()
                    if 'data' in data and 'tweet_detail' in data['data']:
                        tweet_detail = data['data']['tweet_detail']
                        if 'instructions' in tweet_detail:
                            instructions = tweet_detail['instructions']
                            if len(instructions) == 0:
                                reasons.append("Tweet detail has no instructions - likely deleted or private")
                                suggestions.append("This tweet may have been deleted or is from a private account")
                            else:
                                reasons.append("Raw request succeeded but tweet not parseable")
                        else:
                            reasons.append("Tweet detail missing instructions")
                    else:
                        reasons.append("Response missing tweet detail data")
                else:
                    reasons.append(f"Raw request failed with status {raw_response.status_code}")
            else:
                reasons.append("Raw request returned None")
        except Exception as e:
            reasons.append(f"Raw request failed: {e}")
        
        # Common suggestions based on patterns
        if "deleted" in str(reasons).lower():
            suggestions.append("Tweet may have been deleted by the author")
        if "private" in str(reasons).lower():
            suggestions.append("Tweet may be from a private account")
        if "rate limit" in str(reasons).lower():
            suggestions.append("Rate limit reached - try again later")
        
        suggestions.append("Try testing with a different tweet ID to verify the system works")
        suggestions.append("Check if the tweet URL is still accessible in a browser")
        
        return diagnosis

    async def _try_tweet_details(self, tweet_id: str) -> Optional[Any]:
        """Try to get tweet details using the primary method."""
        try:
            logger.info(f"Trying tweet_details method for ID: {tweet_id}")
            tweet = await self.api.tweet_details(tweet_id)
            if tweet:
                logger.info("✅ tweet_details method succeeded")
                return tweet
            else:
                logger.warning("❌ tweet_details returned None - tweet may be deleted, private, or inaccessible")
                return None
        except Exception as e:
            logger.error(f"❌ tweet_details method failed: {e}")
            return None
    
    async def _try_search_method(self, tweet_id: str) -> Optional[Any]:
        """Try to get tweet using search method."""
        try:
            logger.info(f"Trying search method for ID: {tweet_id}")
            search_results = []
            async for tweet in self.api.search(f"id:{tweet_id}", limit=1):
                search_results.append(tweet)
                break
            
            if search_results and len(search_results) > 0:
                logger.info("✅ search method succeeded")
                return search_results[0]
            else:
                logger.warning("❌ search method returned no results - tweet may not be searchable")
                return None
        except Exception as e:
            logger.error(f"❌ search method failed: {e}")
            return None
    
    async def _try_raw_request(self, tweet_id: str) -> Optional[Any]:
        """Try to get tweet using raw GraphQL request."""
        try:
            logger.info(f"Trying raw GraphQL request for ID: {tweet_id}")
            
            # Use the built-in tweet_details_raw method instead of manual client management
            raw_response = await self.api.tweet_details_raw(tweet_id)
            if raw_response and raw_response.status_code == 200:
                data = raw_response.json()
                logger.info("✅ Raw GraphQL request succeeded")
                return data
            else:
                status_code = raw_response.status_code if raw_response else "No response"
                logger.warning(f"❌ Raw request failed with status {status_code}")
                return None
                    
        except Exception as e:
            logger.error(f"❌ Raw request method failed: {e}")
            return None
    
    async def extract_tweet_with_replies(self, url: str) -> Dict[str, Any]:
        """Extract a tweet and its replies."""
        logger.info(f"Starting tweet and replies extraction for URL: {url}")
        
        if not TWSCRAPE_AVAILABLE:
            return {
                "success": False,
                "error": "twscrape not available",
                "title": "Twitter/X Post with Replies",
                "extracted_content": "Failed to extract: twscrape not available"
            }
        
        try:
            # Extract tweet ID
            tweet_id = self.extract_twitter_id_from_url(url)
            if not tweet_id:
                return {
                    "success": False,
                    "error": f"Could not extract tweet ID from URL: {url}",
                    "title": "Twitter/X Post with Replies",
                    "extracted_content": "Failed to extract: Invalid Twitter/X URL format"
                }
            
            logger.info(f"Extracting tweet {tweet_id} and its replies...")
            
            # Get the main tweet
            main_tweet = await self.api.tweet_details(tweet_id)
            if not main_tweet:
                return {
                    "success": False,
                    "error": f"Could not find tweet with ID: {tweet_id}",
                    "title": "Twitter/X Post with Replies",
                    "extracted_content": "Failed to extract: Tweet not found"
                }
            
            # Get replies using the dedicated tweet_replies method
            replies = []
            try:
                async for tweet in self.api.tweet_replies(int(tweet_id), limit=20):
                    replies.append(tweet)
            except Exception as e:
                logger.warning(f"Could not fetch replies: {e}")
            
            # Format the content
            main_content = f"""
MAIN TWEET:
Twitter/X Post by @{main_tweet.user.username}
Tweet ID: {tweet_id}
Posted: {main_tweet.date}

Content:
{main_tweet.rawContent}

Engagement:
- Likes: {main_tweet.likeCount}
- Retweets: {main_tweet.retweetCount}
- Replies: {main_tweet.replyCount}
- Quotes: {main_tweet.quoteCount}
""".strip()
            
            if replies:
                replies_content = "\n\nREPLIES:\n" + "="*50 + "\n"
                for i, reply in enumerate(replies, 1):
                    replies_content += f"""
Reply {i}:
Author: @{reply.user.username}
Tweet ID: {reply.id}
Posted: {reply.date}

Content:
{reply.rawContent}

Engagement:
- Likes: {reply.likeCount}
- Retweets: {reply.retweetCount}
- Replies: {reply.replyCount}
""".strip() + "\n\n"
                
                full_content = main_content + replies_content
            else:
                full_content = main_content + "\n\nNo replies found."
            
            return {
                "success": True,
                "title": f"Twitter/X Post by @{main_tweet.user.username} with {len(replies)} replies",
                "extracted_content": full_content,
                "word_count": len(main_tweet.rawContent.split()),
                "metadata": {
                    "tweet_id": tweet_id,
                    "author": main_tweet.user.username,
                    "replies_count": len(replies),
                    "main_tweet": {
                        "likes": main_tweet.likeCount,
                        "retweets": main_tweet.retweetCount,
                        "replies": main_tweet.replyCount,
                        "quotes": main_tweet.quoteCount,
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to extract tweet with replies: {e}")
            return {
                "success": False,
                "error": str(e),
                "title": "Twitter/X Post with Replies",
                "extracted_content": f"Failed to extract: {str(e)}"
            }

    async def extract_twitter_content(self, url: str, bypass_rate_limit: bool = False) -> Dict[str, Any]:
        """Extract content from Twitter/X URL using twscrape."""
        logger.info(f"Starting Twitter content extraction for URL: {url}")
        
        if not TWSCRAPE_AVAILABLE:
            logger.error("twscrape not available")
            return {
                "success": False,
                "error": "twscrape not available. Install with: pip install twscrape",
                "title": "Twitter/X Post",
                "extracted_content": f"Failed to extract: twscrape not available"
            }
        
        # Check accounts availability (skip if bypassing rate limit for testing)
        if not bypass_rate_limit:
            logger.info("Checking twscrape accounts...")
            await self._check_accounts()
        
        try:
            # Extract tweet ID
            tweet_id = self.extract_twitter_id_from_url(url)
            if not tweet_id:
                logger.error(f"Could not extract tweet ID from URL: {url}")
                return {
                    "success": False,
                    "error": f"Could not extract tweet ID from URL: {url}",
                    "title": "Twitter/X Post",
                    "extracted_content": f"Failed to extract: Invalid Twitter/X URL format"
                }
            
            logger.info(f"Extracted tweet ID: {tweet_id}")
            logger.info(f"=== FETCHING TWEET DATA ===")
            
            # Try multiple methods to get tweet data
            tweet_data = None
            method_used = None
            
            # Method 1: tweet_details
            tweet_data = await self._try_tweet_details(tweet_id)
            if tweet_data:
                method_used = "tweet_details"
            
            # Method 2: search method
            if not tweet_data:
                tweet_data = await self._try_search_method(tweet_id)
                if tweet_data:
                    method_used = "search"
            
            # Method 3: raw GraphQL request
            if not tweet_data:
                tweet_data = await self._try_raw_request(tweet_id)
                if tweet_data:
                    method_used = "raw_graphql"
            
            if not tweet_data:
                logger.error(f"❌ All methods failed to fetch tweet with ID: {tweet_id}")
                
                # Run diagnosis to get more specific information
                diagnosis = await self._diagnose_tweet_accessibility(tweet_id)
                
                return {
                    "success": False,
                    "error": f"Could not find tweet with ID: {tweet_id}",
                    "title": "Twitter/X Post",
                    "extracted_content": f"Failed to extract: Tweet not found or inaccessible",
                    "diagnosis": diagnosis,
                    "suggestions": diagnosis.get("suggestions", [
                        "Check if the tweet is private or deleted",
                        "Verify your Twitter account has valid cookies", 
                        "Try getting fresh cookies from your Twitter account",
                        "The tweet might require authentication"
                    ])
                }
            
            logger.info(f"✅ Tweet found using method: {method_used}")
            
            # Extract content based on the method used
            if method_used == "raw_graphql":
                # Handle raw GraphQL response
                content = self._extract_from_raw_response(tweet_data, tweet_id)
            else:
                # Handle parsed tweet object
                content = self._extract_from_tweet_object(tweet_data, tweet_id)
            
            if not content:
                logger.error("❌ Could not extract content from tweet data")
                return {
                    "success": False,
                    "error": "Could not extract content from tweet data",
                    "title": "Twitter/X Post",
                    "extracted_content": f"Failed to extract: Content extraction failed"
                }
            
            return content
            
        except Exception as e:
            logger.error(f"Failed to extract Twitter/X content from {url}: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception details: {e}")
            return {
                "success": False,
                "error": str(e),
                "title": "Twitter/X Post",
                "extracted_content": f"Failed to extract: {str(e)}"
            }
    
    def _extract_from_tweet_object(self, tweet_data: Any, tweet_id: str) -> Optional[Dict[str, Any]]:
        """Extract content from a parsed tweet object."""
        try:
            logger.info(f"🔍 Extracting from tweet object: {type(tweet_data)}")
            logger.info(f"   Tweet object attributes: {dir(tweet_data)}")
            
            # Extract content
            content = tweet_data.rawContent if hasattr(tweet_data, 'rawContent') else str(tweet_data)
            logger.info(f"   Content: {content[:100]}...")
            
            # Get user information safely
            author = "Unknown"
            if hasattr(tweet_data, 'user'):
                user = tweet_data.user
                logger.info(f"   User object type: {type(user)}")
                logger.info(f"   User object attributes: {dir(user)}")
                
                if hasattr(user, 'username'):
                    author = user.username
                elif hasattr(user, 'screen_name'):
                    author = user.screen_name
                elif hasattr(user, 'get'):
                    author = user.get('username', 'Unknown')
                else:
                    author = str(user)
            
            logger.info(f"   Author: {author}")
            
            # Get additional metadata
            metadata = {
                "tweet_id": tweet_id,
                "author": author,
                "date": getattr(tweet_data, 'date', None),
                "likes": getattr(tweet_data, 'likeCount', 0),
                "retweets": getattr(tweet_data, 'retweetCount', 0),
                "replies": getattr(tweet_data, 'replyCount', 0),
                "quotes": getattr(tweet_data, 'quoteCount', 0),
            }
            
            # Create a formatted content string
            formatted_content = f"""
Twitter/X Post by @{metadata['author']}
Tweet ID: {tweet_id}
Posted: {metadata['date']}

Content:
{content}

Engagement:
- Likes: {metadata['likes']}
- Retweets: {metadata['retweets']}
- Replies: {metadata['replies']}
- Quotes: {metadata['quotes']}
""".strip()
            
            return {
                "success": True,
                "title": f"Twitter/X Post by @{metadata['author']}",
                "extracted_content": formatted_content,
                "word_count": len(content.split()),
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error extracting from tweet object: {e}")
            return None
    
    def _extract_from_raw_response(self, raw_data: Dict[str, Any], tweet_id: str) -> Optional[Dict[str, Any]]:
        """Extract content from raw GraphQL response."""
        try:
            logger.info(f"🔍 Extracting from raw response structure...")
            logger.info(f"   Raw data keys: {list(raw_data.keys())}")
            
            # Navigate through the GraphQL response structure
            data = raw_data.get('data', {})
            logger.info(f"   Data keys: {list(data.keys())}")
            
            tweet_detail = data.get('tweet_detail', {})
            logger.info(f"   Tweet detail keys: {list(tweet_detail.keys())}")
            
            instructions = tweet_detail.get('instructions', [])
            logger.info(f"   Found {len(instructions)} instructions")
            
            for i, instruction in enumerate(instructions):
                logger.info(f"   Instruction {i}: {instruction.get('type', 'unknown')}")
                
                if instruction.get('type') == 'TimelineAddEntries':
                    entries = instruction.get('entries', [])
                    logger.info(f"     Found {len(entries)} entries")
                    
                    for j, entry in enumerate(entries):
                        entry_type = entry.get('content', {}).get('entryType', 'unknown')
                        logger.info(f"       Entry {j}: {entry_type}")
                        
                        if entry_type == 'Tweet':
                            tweet_content = entry.get('content', {}).get('itemContent', {}).get('tweet_results', {}).get('result', {})
                            logger.info(f"         Tweet content keys: {list(tweet_content.keys())}")
                            
                            if tweet_content:
                                # Extract tweet text
                                legacy = tweet_content.get('legacy', {})
                                logger.info(f"         Legacy keys: {list(legacy.keys())}")
                                
                                tweet_text = legacy.get('full_text', '')
                                logger.info(f"         Tweet text: {tweet_text[:100]}...")
                                
                                # Extract author information
                                core = tweet_content.get('core', {})
                                user_results = core.get('user_results', {})
                                result = user_results.get('result', {})
                                user_legacy = result.get('legacy', {})
                                author = user_legacy.get('screen_name', 'Unknown')
                                logger.info(f"         Author: {author}")
                                
                                # Extract engagement metrics
                                likes = legacy.get('favorite_count', 0)
                                retweets = legacy.get('retweet_count', 0)
                                replies = legacy.get('reply_count', 0)
                                quotes = legacy.get('quote_count', 0)
                                
                                logger.info(f"         Engagement: {likes} likes, {retweets} retweets, {replies} replies, {quotes} quotes")
                                
                                # Create formatted content
                                formatted_content = f"""
Twitter/X Post by @{author}
Tweet ID: {tweet_id}

Content:
{tweet_text}

Engagement:
- Likes: {likes}
- Retweets: {retweets}
- Replies: {replies}
- Quotes: {quotes}
""".strip()
                                
                                metadata = {
                                    "tweet_id": tweet_id,
                                    "author": author,
                                    "likes": likes,
                                    "retweets": retweets,
                                    "replies": replies,
                                    "quotes": quotes,
                                }
                                
                                return {
                                    "success": True,
                                    "title": f"Twitter/X Post by @{author}",
                                    "extracted_content": formatted_content,
                                    "word_count": len(tweet_text.split()),
                                    "metadata": metadata
                                }
            
            logger.warning("Could not find tweet content in raw response")
            logger.info(f"   Raw response structure: {raw_data}")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting from raw response: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    async def extract_social_media_content(self, url: str) -> Dict[str, Any]:
        """Extract content from any supported social media platform."""
        if self.is_twitter_url(url):
            return await self.extract_twitter_content(url)
        else:
            return {
                "success": False,
                "error": f"Unsupported social media platform: {url}",
                "title": "Social Media Post",
                "extracted_content": f"Failed to extract: Unsupported platform"
            }
    
    async def extract_twitter_content_with_fallback(self, url: str) -> Dict[str, Any]:
        """Extract Twitter/X content with fallback to web scraping."""
        # Try twscrape first
        result = await self.extract_twitter_content(url)
        
        if result["success"]:
            return result
        
        # If twscrape fails, return a structured error that indicates fallback should be used
        return {
            "success": False,
            "error": f"twscrape failed: {result['error']}",
            "title": "Twitter/X Post (twscrape failed)",
            "extracted_content": f"twscrape extraction failed: {result['error']}. Will fall back to web scraping.",
            "fallback_to_web_scraping": True
        }
    
    async def extract_twitter_content_guest(self, url: str) -> Dict[str, Any]:
        """Extract Twitter/X content using guest mode (no account required)."""
        # Guest mode is not supported by twscrape - this method is kept for compatibility
        return {
            "success": False,
            "error": "Guest mode is not supported by twscrape. Twitter accounts are required.",
            "title": "Twitter/X Post",
            "extracted_content": f"Guest mode not supported. Please add Twitter accounts to use twscrape."
        }

# Create a global instance
social_media_extractor = SocialMediaExtractor() 