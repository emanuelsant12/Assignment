from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables from .env
load_dotenv()

# Connect to MongoDB Atlas
MONGO_URL = os.getenv("MONGO_URL")
client = AsyncIOMotorClient(MONGO_URL)
db = client["game_assets_db"]

app = FastAPI(title="Game Assets API", version="1.0")

# Pydantic model for score submission
class PlayerScore(BaseModel):
    player_name: str
    score: int

# Upload a sprite image
@app.post("/upload_sprite")
async def upload_sprite(file: UploadFile = File(...)):
    content = await file.read()
    sprite_doc = {
        "filename": file.filename,
        "filetype": file.content_type,
        "content": content,
        "uploaded_at": datetime.utcnow()
    }
    result = await db.sprites.insert_one(sprite_doc)
    return {"message": "Sprite uploaded", "id": str(result.inserted_id)}

# Upload an audio file
@app.post("/upload_audio")
async def upload_audio(file: UploadFile = File(...)):
    content = await file.read()
    audio_doc = {
        "filename": file.filename,
        "filetype": file.content_type,
        "content": content,
        "uploaded_at": datetime.utcnow()
    }
    result = await db.audio.insert_one(audio_doc)
    return {"message": "Audio uploaded", "id": str(result.inserted_id)}

# Submit a player score
@app.post("/player_score")
async def add_score(score: PlayerScore):
    score_doc = {
        "player_name": score.player_name,
        "score": score.score,
        "submitted_at": datetime.utcnow()
    }
    result = await db.scores.insert_one(score_doc)
    return {"message": "Score recorded", "id": str(result.inserted_id)}

# Get all scores
@app.get("/scores")
async def get_scores():
    scores = []
    async for score in db.scores.find():
        score["_id"] = str(score["_id"])
        scores.append(score)
    return scores

@app.get("/")
async def root():
    return {"message": "Game Assets API is running!"}
