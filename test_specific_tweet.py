#!/usr/bin/env python3
"""Test script to check specific tweet accessibility and test with working tweet."""

import asyncio
import logging
from social_media_extractor import social_media_extractor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_specific_tweet():
    """Test the specific tweet and find a working alternative."""
    
    print("🧪 TESTING SPECIFIC TWEET ACCESSIBILITY")
    print("=" * 50)
    
    # Test the specific tweet first
    target_url = "https://x.com/lilicjohn/status/1939764384160743841?s=52"
    target_id = "1939764384160743841"
    
    print(f"📝 Testing target tweet: {target_url}")
    print("-" * 40)
    
    api = social_media_extractor.api
    
    # Method 1: Try tweet_details
    print("1️⃣ Testing tweet_details...")
    try:
        tweet_detail = await api.tweet_details(target_id)
        if tweet_detail:
            print("✅ tweet_details found the tweet!")
            print(f"   Author: @{tweet_detail.user.username}")
            print(f"   Content: {tweet_detail.rawContent[:100]}...")
            print(f"   Replies: {tweet_detail.replyCount}")
        else:
            print("❌ tweet_details returned None")
    except Exception as e:
        print(f"❌ tweet_details error: {e}")
    
    # Method 2: Try search
    print("\n2️⃣ Testing search...")
    try:
        search_results = []
        async for tweet in api.search(f"id:{target_id}", limit=5):
            search_results.append(tweet)
        
        if search_results:
            print(f"✅ Search found {len(search_results)} results")
            for i, tweet in enumerate(search_results):
                print(f"   Result {i+1}: @{tweet.user.username} - {tweet.rawContent[:50]}...")
        else:
            print("❌ Search found no results")
    except Exception as e:
        print(f"❌ Search error: {e}")
    
    # Method 3: Try to find a working tweet with replies
    print("\n3️⃣ Finding a working tweet with replies...")
    try:
        # Search for tweets that might have replies
        working_tweets = []
        async for tweet in api.search("test replies", limit=10):
            if tweet.replyCount > 0:
                working_tweets.append(tweet)
                if len(working_tweets) >= 3:  # Get a few options
                    break
        
        if working_tweets:
            print(f"✅ Found {len(working_tweets)} tweets with replies:")
            for i, tweet in enumerate(working_tweets):
                print(f"   Option {i+1}:")
                print(f"     ID: {tweet.id}")
                print(f"     Author: @{tweet.user.username}")
                print(f"     Content: {tweet.rawContent[:80]}...")
                print(f"     Replies: {tweet.replyCount}")
                print(f"     URL: https://x.com/{tweet.user.username}/status/{tweet.id}")
                print()
        else:
            print("❌ No tweets with replies found")
    except Exception as e:
        print(f"❌ Error finding working tweets: {e}")

if __name__ == "__main__":
    print("Starting specific tweet test...")
    asyncio.run(test_specific_tweet())
    print("\n�� Test complete!") 