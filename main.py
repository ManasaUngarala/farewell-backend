from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Farewell App API")

# CORS - allow your frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # After deploying, replace * with your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGODB_URL)
db = client["farewell_db"]

# ─── Models ───────────────────────────────────────────────────────────────────

class VerifyRequest(BaseModel):
    full_name: str
    passcode: str
    friend_id: str | None = None

class SlamEntry(BaseModel):
    message: str
    full_name: str | None = None
    passcode: str | None = None
    friend_id: str | None = None

class FriendCreate(BaseModel):
    friend_id: str       # e.g. "ravi", "priya" — becomes the URL slug
    display_name: str    # shown on their page
    passcode: str        # secret code you share with them
    secret_message: str  # your personal message to them
    photos: list[str]    # list of image URLs (you can use Google Drive / Cloudinary)
    music_url: str       # background music URL (YouTube embed or direct mp3)

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"status": "Farewell API is running 🎓"}


@app.post("/admin/add-friend")
async def add_friend(data: FriendCreate):
    """
    Admin endpoint — you call this (via Postman or the script) to add each friend.
    """
    existing = await db.friends.find_one({"friend_id": data.friend_id})
    if existing:
        raise HTTPException(status_code=400, detail="Friend ID already exists")
    
    doc = data.dict()
    doc["created_at"] = datetime.utcnow()
    await db.friends.insert_one(doc)
    return {"message": f"Friend '{data.friend_id}' added successfully!"}


@app.post("/verify")
async def verify_friend(req: VerifyRequest):
    """
    Called when friend enters their name + passcode.
    Returns their secret message and photos on success.
    """
    friend = None
    if req.friend_id:
        friend = await db.friends.find_one({"friend_id": req.friend_id})
        if not friend:
            raise HTTPException(status_code=404, detail="Friend not found")
        if friend.get("passcode") != req.passcode:
            raise HTTPException(status_code=401, detail="Wrong passcode. Try again!")
    else:
        friend = await db.friends.find_one({"passcode": req.passcode})
        if not friend:
            raise HTTPException(status_code=404, detail="Friend not found")

    expected_name = (friend.get("display_name") or "").strip().casefold()
    expected_verified = (friend.get("verified_name") or "").strip().casefold()
    entered_name = (req.full_name or "").strip().casefold()
    if expected_name and entered_name != expected_name and entered_name != expected_verified:
        raise HTTPException(status_code=401, detail="Wrong name for this passcode")
    
    # Save the verified name (update if already set)
    await db.friends.update_one(
        {"friend_id": friend["friend_id"]},
        {"$set": {"verified_name": req.full_name, "verified_at": datetime.utcnow()}}
    )
    
    return {
        "success": True,
        "friend_id": friend["friend_id"],
        "display_name": friend.get("display_name", req.full_name),
        "secret_message": friend["secret_message"],
        "photos": friend.get("photos", []),
        "music_url": friend.get("music_url", ""),
    }


@app.post("/slam")
async def save_slam(entry: SlamEntry):
    """
    Saves friend's slam book message.
    """
    friend = None
    if entry.friend_id:
        friend = await db.friends.find_one({"friend_id": entry.friend_id})
    elif entry.passcode:
        friend = await db.friends.find_one({"passcode": entry.passcode})

    if not friend:
        raise HTTPException(status_code=404, detail="Friend not found")

    if entry.full_name:
        expected_name = (friend.get("display_name") or "").strip().casefold()
        expected_verified = (friend.get("verified_name") or "").strip().casefold()
        entered_name = (entry.full_name or "").strip().casefold()
        if expected_name and entered_name != expected_name and entered_name != expected_verified:
            raise HTTPException(status_code=401, detail="Wrong name for this passcode")
    
    doc = {
        "friend_id": friend["friend_id"],
        "display_name": friend.get("display_name", "Anonymous"),
        "message": entry.message,
        "submitted_at": datetime.utcnow()
    }
    await db.slam_entries.insert_one(doc)
    return {"success": True, "message": "Your message has been saved with love 💌"}


@app.get("/admin/slam-entries")
async def get_slam_entries():
    """
    View all slam book entries. You open this in your browser.
    """
    entries = []
    async for doc in db.slam_entries.find({}, {"_id": 0}).sort("submitted_at", -1):
        doc["submitted_at"] = str(doc["submitted_at"])
        entries.append(doc)
    return {"total": len(entries), "entries": entries}


@app.get("/admin/friends")
async def list_friends():
    """
    See all friends you've added.
    """
    friends = []
    async for doc in db.friends.find({}, {"_id": 0, "passcode": 0, "secret_message": 0}):
        friends.append(doc)
    return friends
