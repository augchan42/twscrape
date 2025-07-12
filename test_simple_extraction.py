#!/usr/bin/env python3
"""Simple test for tweet extraction with detailed debugging."""

import asyncio
import logging
from social_media_extractor import social_media_extractor

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_simple_extraction():
    """Test basic tweet extraction with a known working tweet."""
    
    print("🧪 SIMPLE TWEET EXTRACTION TEST")
    print("=" * 50)
    
    # Test with a recent tweet that should be accessible
    test_url = "https://x.com/elonmusk/status/1943859422058704935"
    
    print(f"📝 Testing URL: {test_url}")
    print("-" * 40)
    
    try:
        # First, let's check if we can get any tweet via search
        print("🔍 Testing search functionality...")
        api = social_media_extractor.api
        
        search_results = []
        async for tweet in api.search("test", limit=1):
            search_results.append(tweet)
            break
        
        if search_results:
            working_tweet = search_results[0]
            print(f"✅ Found working tweet via search:")
            print(f"   ID: {working_tweet.id}")
            print(f"   Author: {working_tweet.user.username if hasattr(working_tweet.user, 'username') else 'Unknown'}")
            print(f"   Content: {working_tweet.rawContent[:100]}...")
            
            # Now test extraction with this working tweet
            print(f"\n🔍 Testing extraction with working tweet...")
            result = await social_media_extractor.extract_twitter_content(f"https://x.com/test/status/{working_tweet.id}")
            
            if result["success"]:
                print("✅ EXTRACTION SUCCESS!")
                print(f"   Title: {result['title']}")
                print(f"   Content: {result['extracted_content'][:200]}...")
            else:
                print("❌ EXTRACTION FAILED")
                print(f"   Error: {result['error']}")
                if 'diagnosis' in result:
                    diagnosis = result['diagnosis']
                    print(f"   Diagnosis: {diagnosis}")
        else:
            print("❌ No search results found")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    print("Starting simple extraction test...")
    asyncio.run(test_simple_extraction())
    print("\n�� Test complete!") 