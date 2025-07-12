#!/usr/bin/env python3
"""Test script for the improved social media extractor."""

import asyncio
import logging
from social_media_extractor import social_media_extractor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_extractor():
    """Test the improved social media extractor."""
    
    print("🧪 TESTING IMPROVED SOCIAL MEDIA EXTRACTOR")
    print("=" * 50)
    
    # Test URLs - mix of working and problematic tweets
    test_urls = [
        "https://x.com/conqern/status/1943859422058704935",  # Working tweet from debug
        "https://x.com/elonmusk/status/1943393540538798263",  # Your original problematic tweet
        "https://x.com/test/status/1234567890",  # Non-existent tweet
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n📝 Test {i}: {url}")
        print("-" * 40)
        
        try:
            result = await social_media_extractor.extract_twitter_content(url)
            
            if result["success"]:
                print("✅ SUCCESS!")
                print(f"   Title: {result['title']}")
                print(f"   Content preview: {result['extracted_content'][:200]}...")
                if 'metadata' in result:
                    metadata = result['metadata']
                    print(f"   Author: @{metadata.get('author', 'Unknown')}")
                    print(f"   Engagement: {metadata.get('likes', 0)} likes, {metadata.get('replies', 0)} replies")
            else:
                print("❌ FAILED")
                print(f"   Error: {result['error']}")
                
                # Show diagnosis if available
                if 'diagnosis' in result:
                    diagnosis = result['diagnosis']
                    print(f"   🔍 DIAGNOSIS:")
                    print(f"      Accessible: {diagnosis['accessible']}")
                    print(f"      Reasons: {', '.join(diagnosis['reasons'])}")
                    print(f"      Suggestions: {', '.join(diagnosis['suggestions'])}")
                
                # Show suggestions
                if 'suggestions' in result:
                    print(f"   💡 SUGGESTIONS:")
                    for suggestion in result['suggestions']:
                        print(f"      • {suggestion}")
                        
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    print("Starting improved extractor test...")
    asyncio.run(test_extractor())
    print("\n�� Test complete!") 