#!/usr/bin/env python3
"""Test script to show what different tweet methods return."""

import asyncio
import logging
from social_media_extractor import social_media_extractor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_tweet_methods():
    """Test different tweet methods to see what they return."""
    
    print("🧪 TESTING TWEET METHODS")
    print("=" * 50)
    
    api = social_media_extractor.api
    
    # First, find a recent tweet to test with
    print("🔍 Finding a recent tweet to test with...")
    search_results = []
    async for tweet in api.search("test", limit=1):
        search_results.append(tweet)
        break
    
    if not search_results:
        print("❌ No tweets found via search")
        return
    
    test_tweet = search_results[0]
    print(f"✅ Found test tweet: {test_tweet.id}")
    print(f"   Author: @{test_tweet.user.username}")
    print(f"   Content: {test_tweet.rawContent[:100]}...")
    print(f"   Replies: {test_tweet.replyCount}")
    
    print("\n" + "="*50)
    print("📊 TESTING DIFFERENT METHODS")
    print("="*50)
    
    # Test 1: tweet_details
    print("\n1️⃣ tweet_details method:")
    print("-" * 30)
    try:
        tweet_detail = await api.tweet_details(test_tweet.id)
        if tweet_detail:
            print(f"✅ Success!")
            print(f"   ID: {tweet_detail.id}")
            print(f"   Author: @{tweet_detail.user.username}")
            print(f"   Content: {tweet_detail.rawContent[:100]}...")
            print(f"   Replies count: {tweet_detail.replyCount}")
            print(f"   Likes: {tweet_detail.likeCount}")
            print(f"   Retweets: {tweet_detail.retweetCount}")
            print(f"   Date: {tweet_detail.date}")
            
            # Check if it has replies data
            print(f"   Has replies data: {'No - only gets the single tweet'}")
        else:
            print("❌ Failed")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: search method
    print("\n2️⃣ search method:")
    print("-" * 30)
    try:
        search_results = []
        async for tweet in api.search(f"id:{test_tweet.id}", limit=5):
            search_results.append(tweet)
        
        print(f"✅ Found {len(search_results)} results")
        for i, tweet in enumerate(search_results):
            print(f"   Result {i+1}:")
            print(f"     ID: {tweet.id}")
            print(f"     Author: @{tweet.user.username}")
            print(f"     Content: {tweet.rawContent[:50]}...")
            print(f"     Is reply: {tweet.inReplyToTweetId is not None}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: user_tweets (to see if we can get replies)
    print("\n3️⃣ user_tweets method:")
    print("-" * 30)
    try:
        user_tweets = []
        async for tweet in api.user_tweets(test_tweet.user.username, limit=5):
            user_tweets.append(tweet)
        
        print(f"✅ Found {len(user_tweets)} user tweets")
        for i, tweet in enumerate(user_tweets):
            print(f"   Tweet {i+1}:")
            print(f"     ID: {tweet.id}")
            print(f"     Content: {tweet.rawContent[:50]}...")
            print(f"     Is reply: {tweet.inReplyToTweetId is not None}")
            if tweet.inReplyToTweetId:
                print(f"     Reply to: {tweet.inReplyToTweetId}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Raw GraphQL response
    print("\n4️⃣ Raw GraphQL response:")
    print("-" * 30)
    try:
        raw_response = await api.tweet_details_raw(test_tweet.id)
        if raw_response and raw_response.status_code == 200:
            data = raw_response.json()
            print("✅ Raw response structure:")
            print(f"   Top level keys: {list(data.keys())}")
            
            if 'data' in data:
                tweet_detail = data['data'].get('tweet_detail', {})
                print(f"   Tweet detail keys: {list(tweet_detail.keys())}")
                
                instructions = tweet_detail.get('instructions', [])
                print(f"   Instructions count: {len(instructions)}")
                
                for i, instruction in enumerate(instructions):
                    print(f"     Instruction {i}: {instruction.get('type', 'unknown')}")
                    if instruction.get('type') == 'TimelineAddEntries':
                        entries = instruction.get('entries', [])
                        print(f"       Entries: {len(entries)}")
                        for j, entry in enumerate(entries):
                            entry_type = entry.get('content', {}).get('entryType', 'unknown')
                            print(f"         Entry {j}: {entry_type}")
        else:
            print("❌ Raw response failed")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Starting tweet methods test...")
    asyncio.run(test_tweet_methods())
    print("\n�� Test complete!") 