#!/usr/bin/env python3
"""Debug script to print and save the full raw API response for a specific tweet."""

import asyncio
import json
from twscrape import API

async def print_and_save_raw_response(tweet_id):
    api = API()
    print(f"🔍 Fetching raw API response for tweet ID: {tweet_id}")
    raw_response = await api.tweet_details_raw(tweet_id)
    if raw_response:
        print(f"Status code: {raw_response.status_code}")
        try:
            data = raw_response.json()
            # Print the full JSON
            print(json.dumps(data, indent=2))
            # Save to file
            with open(f"tweet_{tweet_id}_raw.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Full raw JSON saved to tweet_{tweet_id}_raw.json")
        except Exception as e:
            print(f"❌ Error parsing JSON: {e}")
            print(f"Raw text: {raw_response.text[:1000]}")
    else:
        print("❌ No response received.")

if __name__ == "__main__":
    tweet_id = "1939764384160743841"
    asyncio.run(print_and_save_raw_response(tweet_id)) 