#!/usr/bin/env python3
"""Test script for extracting tweets with replies."""

import asyncio
import logging
from social_media_extractor import social_media_extractor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_replies_extraction():
    """Test extracting a tweet with its replies."""
    
    print("🧪 TESTING TWEET WITH REPLIES EXTRACTION")
    print("=" * 50)
    
    # Test with a working tweet that has replies
    test_url = "https://x.com/QuantumTumbler/status/1943847930945056978"
    
    print(f"📝 Testing URL: {test_url}")
    print("-" * 40)
    
    try:
        # Test the new method
        result = await social_media_extractor.extract_tweet_with_replies(test_url)
        
        if result["success"]:
            print("✅ SUCCESS!")
            print(f"   Title: {result['title']}")
            print(f"   Replies found: {result['metadata']['replies_count']}")
            print(f"   Content preview:")
            print("-" * 30)
            print(result['extracted_content'][:500] + "...")
        else:
            print("❌ FAILED")
            print(f"   Error: {result['error']}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    print("Starting replies extraction test...")
    asyncio.run(test_replies_extraction())
    print("\n�� Test complete!") 