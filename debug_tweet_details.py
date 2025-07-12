#!/usr/bin/env python3
"""Debug script to examine tweet_details parsing issues."""

import asyncio
import json
import logging
from twscrape import API
from twscrape.models import parse_tweet, parse_tweets

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_tweet_details():
    """Debug the tweet_details method."""
    
    print("🔍 DEBUGGING TWEET DETAILS")
    print("=" * 50)
    
    api = API()
    
    # Test tweet IDs
    test_tweets = [
        "1943393540538798263",  # Your original tweet
        "20",  # Very old tweet
        "1234567890",  # Non-existent tweet
    ]
    
    for tweet_id in test_tweets:
        print(f"\n📝 Testing tweet ID: {tweet_id}")
        print("-" * 30)
        
        try:
            # Get raw response first
            print("1. Getting raw response...")
            raw_response = await api.tweet_details_raw(tweet_id)
            
            if raw_response:
                print(f"✅ Raw response received (status: {raw_response.status_code})")
                
                # Log response headers
                print(f"   Headers: {dict(raw_response.headers)}")
                
                # Try to parse the response
                print("2. Attempting to parse response...")
                
                try:
                    response_json = raw_response.json()
                    print(f"✅ JSON parsed successfully")
                    print(f"   Response keys: {list(response_json.keys())}")
                    
                    # Check if there's data
                    if 'data' in response_json:
                        data = response_json['data']
                        print(f"   Data keys: {list(data.keys())}")
                        
                        # Look for tweet detail structure
                        if 'tweet_detail' in data:
                            tweet_detail = data['tweet_detail']
                            print(f"   Tweet detail keys: {list(tweet_detail.keys())}")
                            
                            if 'instructions' in tweet_detail:
                                instructions = tweet_detail['instructions']
                                print(f"   Found {len(instructions)} instructions")
                                
                                for i, instruction in enumerate(instructions):
                                    print(f"     Instruction {i}: {instruction.get('type', 'unknown')}")
                                    
                                    if instruction.get('type') == 'TimelineAddEntries':
                                        entries = instruction.get('entries', [])
                                        print(f"       Found {len(entries)} entries")
                                        
                                        for j, entry in enumerate(entries):
                                            entry_type = entry.get('content', {}).get('entryType', 'unknown')
                                            print(f"         Entry {j}: {entry_type}")
                                            
                                            if entry_type == 'Tweet':
                                                tweet_content = entry.get('content', {}).get('itemContent', {})
                                                print(f"           Tweet content keys: {list(tweet_content.keys())}")
                                                
                                                if 'tweet_results' in tweet_content:
                                                    tweet_results = tweet_content['tweet_results']
                                                    print(f"             Tweet results keys: {list(tweet_results.keys())}")
                                                    
                                                    if 'result' in tweet_results:
                                                        result = tweet_results['result']
                                                        print(f"               Result type: {result.get('__typename', 'unknown')}")
                                                        print(f"               Result keys: {list(result.keys())}")
                    
                    # Try the actual parsing
                    print("3. Testing parse_tweet function...")
                    parsed_tweet = parse_tweet(raw_response, int(tweet_id))
                    
                    if parsed_tweet:
                        print(f"✅ SUCCESS! Tweet parsed:")
                        print(f"   ID: {parsed_tweet.id}")
                        print(f"   Author: @{parsed_tweet.user.username}")
                        print(f"   Content: {parsed_tweet.rawContent[:100]}...")
                        print(f"   Likes: {parsed_tweet.likeCount}")
                        print(f"   Replies: {parsed_tweet.replyCount}")
                    else:
                        print("❌ parse_tweet returned None")
                        
                        # Try parse_tweets to see if any tweets are found
                        print("4. Testing parse_tweets function...")
                        all_tweets = list(parse_tweets(raw_response))
                        print(f"   Found {len(all_tweets)} tweets in response")
                        
                        for i, tweet in enumerate(all_tweets):
                            print(f"     Tweet {i}: ID={tweet.id}, Author=@{tweet.user.username}")
                        
                        # Check if the target tweet ID is in the results
                        target_id = int(tweet_id)
                        matching_tweets = [t for t in all_tweets if t.id == target_id]
                        
                        if matching_tweets:
                            print(f"✅ Found target tweet in parse_tweets results!")
                        else:
                            print(f"❌ Target tweet {target_id} not found in parse_tweets results")
                            print(f"   Available tweet IDs: {[t.id for t in all_tweets]}")
                
                except Exception as parse_error:
                    print(f"❌ Error parsing JSON: {parse_error}")
                    print(f"   Response text: {raw_response.text[:500]}...")
                    
            else:
                print("❌ Raw response is None")
                
        except Exception as e:
            print(f"❌ Error getting raw response: {e}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")

async def test_working_tweet():
    """Test with a known working tweet."""
    
    print("\n🧪 TESTING WITH KNOWN WORKING TWEET")
    print("=" * 50)
    
    api = API()
    
    # Try to get a recent tweet from a popular account
    try:
        print("Searching for recent tweets...")
        search_results = []
        
        async for tweet in api.search("test", limit=1):
            search_results.append(tweet)
            break
        
        if search_results:
            working_tweet = search_results[0]
            print(f"✅ Found working tweet: {working_tweet.id}")
            print(f"   Author: @{working_tweet.user.username}")
            print(f"   Content: {working_tweet.rawContent[:100]}...")
            
            # Now try to get this tweet by ID
            print(f"\nTesting tweet_details with ID: {working_tweet.id}")
            tweet_details_result = await api.tweet_details(working_tweet.id)
            
            if tweet_details_result:
                print(f"✅ tweet_details worked for this tweet!")
                print(f"   Content: {tweet_details_result.rawContent[:100]}...")
            else:
                print(f"❌ tweet_details failed for this tweet")
                
        else:
            print("❌ No search results found")
            
    except Exception as e:
        print(f"❌ Error in search test: {e}")

if __name__ == "__main__":
    print("Starting tweet details debug...")
    
    # Run the debug
    asyncio.run(debug_tweet_details())
    
    # Test with working tweet
    asyncio.run(test_working_tweet())
    
    print("\n🏁 Debug complete!") 