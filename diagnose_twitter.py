#!/usr/bin/env python3
"""Diagnostic script for Twitter extraction issues."""

import asyncio
import logging
from twscrape import API

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def diagnose_twitter_access():
    """Diagnose Twitter access issues."""
    
    print("🔍 TWITTER EXTRACTION DIAGNOSTIC")
    print("=" * 50)
    
    api = API()
    
    # 1. Check accounts
    print("\n1️⃣ CHECKING ACCOUNTS")
    print("-" * 30)
    
    try:
        accounts = await api.pool.get_all()
        print(f"Total accounts: {len(accounts)}")
        
        active_accounts = [acc for acc in accounts if acc.active]
        print(f"Active accounts: {len(active_accounts)}")
        
        if not active_accounts:
            print("❌ No active accounts!")
            print("   This is the main issue. You need active accounts.")
            return False
        else:
            print("✅ Found active accounts:")
            for acc in active_accounts:
                print(f"   - {acc.username}")
                print(f"     Active: {acc.active}")
                print(f"     Has ct0 cookie: {'ct0' in acc.cookies}")
                if 'ct0' in acc.cookies:
                    print(f"     ct0 cookie: {acc.cookies['ct0'][:20]}...")
                print(f"     Last used: {acc.last_used}")
                print(f"     Error: {acc.error_msg}")
                print()
        
    except Exception as e:
        print(f"❌ Error checking accounts: {e}")
        return False
    
    # 2. Test simple API call
    print("\n2️⃣ TESTING BASIC API CALL")
    print("-" * 30)
    
    try:
        # Try to get a simple user
        user = await api.user_by_login("xdevelopers")
        if user:
            print(f"✅ Successfully fetched user: @{user.username}")
            print(f"   User ID: {user.id}")
            print(f"   Followers: {user.followersCount}")
        else:
            print("❌ Could not fetch user")
            return False
    except Exception as e:
        print(f"❌ Error fetching user: {e}")
        return False
    
    # 3. Test tweet details
    print("\n3️⃣ TESTING TWEET DETAILS")
    print("-" * 30)
    
    # Try a few different tweet IDs
    test_tweets = [
        "1943393540538798263",  # Your original tweet
        "20",  # Very old tweet (likely accessible)
        "1234567890",  # Non-existent tweet
    ]
    
    for tweet_id in test_tweets:
        try:
            print(f"Testing tweet ID: {tweet_id}")
            tweet = await api.tweet_details(tweet_id)
            
            if tweet:
                print(f"✅ Found tweet: {tweet.rawContent[:50]}...")
                print(f"   Author: @{tweet.user.username}")
                print(f"   Likes: {tweet.likeCount}")
                print(f"   Replies: {tweet.replyCount}")
            else:
                print(f"❌ Tweet not found: {tweet_id}")
                
        except Exception as e:
            print(f"❌ Error fetching tweet {tweet_id}: {e}")
    
    # 4. Test search
    print("\n4️⃣ TESTING SEARCH")
    print("-" * 30)
    
    try:
        search_results = await api.search("test", limit=1)
        if search_results:
            print(f"✅ Search successful: Found {len(search_results)} results")
            tweet = search_results[0]
            print(f"   Sample tweet: {tweet.rawContent[:50]}...")
        else:
            print("❌ Search returned no results")
    except Exception as e:
        print(f"❌ Search error: {e}")
    
    # 5. Recommendations
    print("\n5️⃣ RECOMMENDATIONS")
    print("-" * 30)
    
    if len(active_accounts) == 0:
        print("🔧 IMMEDIATE ACTIONS NEEDED:")
        print("1. Get fresh cookies from your Twitter account:")
        print("   - Log into Twitter in your browser")
        print("   - Open Developer Tools (F12)")
        print("   - Go to Application/Storage tab")
        print("   - Find cookies for twitter.com or x.com")
        print("   - Copy: auth_token, ct0, twid")
        print()
        print("2. Update your accounts.txt:")
        print("   digitalrainhq:password123:email@example.com:email_pass123:auth_token=NEW_TOKEN; ct0=NEW_CT0; twid=NEW_TWID")
        print()
        print("3. Re-add accounts:")
        print("   twscrape add_accounts accounts.txt username:password:email:email_password:cookies")
        print()
        print("4. Check account status:")
        print("   twscrape accounts")
    else:
        print("✅ Your accounts appear to be working!")
        print("   If you're still having issues with specific tweets:")
        print("   - The tweet might be private or deleted")
        print("   - Try a different tweet ID")
        print("   - Check if the tweet requires authentication")
    
    return True

async def test_simple_extraction():
    """Test simple tweet extraction."""
    
    print("\n🧪 SIMPLE EXTRACTION TEST")
    print("=" * 50)
    
    api = API()
    
    # Try a very simple tweet (Elon's first tweet)
    simple_tweet_id = "20"
    
    try:
        print(f"Testing simple tweet extraction: {simple_tweet_id}")
        tweet = await api.tweet_details(simple_tweet_id)
        
        if tweet:
            print("✅ SUCCESS!")
            print(f"Tweet: {tweet.rawContent}")
            print(f"Author: @{tweet.user.username}")
            print(f"Date: {tweet.date}")
            print(f"Likes: {tweet.likeCount}")
            return True
        else:
            print("❌ Tweet not found")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Starting Twitter diagnostic...")
    
    # Run diagnostics
    success = asyncio.run(diagnose_twitter_access())
    
    if success:
        # Try simple extraction
        asyncio.run(test_simple_extraction())
    
    print("\n🏁 Diagnostic complete!") 