"""
Run this script to add your friends one by one.
Usage: python add_friends.py

Make sure your backend is running first:
  cd backend && uvicorn main:app --reload
"""

import requests

# ─── CHANGE THIS to your deployed backend URL after deployment ────────────────
BASE_URL = "http://localhost:8000"
# After deploying to Render, it will be like:
# BASE_URL = "https://farewell-backend.onrender.com"

# ─── ADD YOUR FRIENDS HERE ────────────────────────────────────────────────────
friends = [
    {
        "friend_id": "ravi",          # This becomes the URL: yourapp.vercel.app/friend/ravi
        "display_name": "Ravi Kumar", # Shown on their page
        "passcode": "RAVI2025",       # You send this to them privately
        "secret_message": """Dear Ravi,
        
You've been one of the most genuine people I've met in college. 
Your laugh is contagious and your support during tough times meant the world to me.
I know you're going to do great things. Keep being you — the world needs more people like you.

With love,
[Your Name]""",
        "photos": [
            # Add direct image URLs here — Google Drive, Cloudinary, or any public image link
            # To use Google Drive: right-click image → Share → Anyone with link → Copy link
            # Then change the URL from:
            #   https://drive.google.com/file/d/FILE_ID/view
            # To:
            #   https://drive.google.com/uc?export=view&id=FILE_ID
            "https://drive.google.com/uc?export=view&id=YOUR_PHOTO_ID_1",
            "https://drive.google.com/uc?export=view&id=YOUR_PHOTO_ID_2",
        ],
        "music_url": "https://www.youtube.com/embed/450p7goxZqg?autoplay=1&loop=1",
        # ^ This is a gentle piano music embed. Replace with any YouTube embed URL.
        # Format: https://www.youtube.com/embed/VIDEO_ID?autoplay=1&loop=1
    },
    {
        "friend_id": "priya",
        "display_name": "Priya Sharma",
        "passcode": "PRIYA2025",
        "secret_message": """Dear Priya,

Thank you for being my partner in crime through every deadline and every crisis.
Your kindness is something I'll carry with me always.

With love,
[Your Name]""",
        "photos": [
            "https://drive.google.com/uc?export=view&id=YOUR_PHOTO_ID_3",
        ],
        "music_url": "https://www.youtube.com/embed/450p7goxZqg?autoplay=1&loop=1",
    },
    # Add more friends by copying the block above...
]

# ─── Script ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    for friend in friends:
        response = requests.post(f"{BASE_URL}/admin/add-friend", json=friend)
        if response.status_code == 200:
            link = f"Send this link to {friend['display_name']}: yourapp.vercel.app/friend/{friend['friend_id']}"
            code = f"Their passcode: {friend['passcode']}"
            print(f"✅ Added {friend['display_name']}")
            print(f"   🔗 {link}")
            print(f"   🔑 {code}")
        else:
            print(f"❌ Error adding {friend['display_name']}: {response.json()}")
        print()
