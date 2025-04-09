# Import FastAPI, MongoDB client, and tools for handling file uploads
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from datetime import datetime
import re

# Load variables from .env file (e.g., MongoDB URI)
load_dotenv()

# Correct: Load the MongoDB URL from the environment variable
MONGO_URL = os.getenv("MONGO_URL")

# Connect to MongoDB using the URI from the environment
client = AsyncIOMotorClient(MONGO_URL)
db = client["game_assets_db"]  # Use the 'game_assets_db' database

# Create the FastAPI app
app = FastAPI(title="Game Assets API", version="1.0")

# Define the data structure for a player score using Pydantic
class PlayerScore(BaseModel):
    player_name: str
    score: int

# task 4c
# Function to sanitize player name input (removes special characters)
def sanitize_text(text):
    return re.sub(r'[^\w\s\-]', '', text)

# Endpoint: Upload a sprite image (binary file)
@app.post("/upload_sprite")
async def upload_sprite(file: UploadFile = File(...)):
    content = await file.read()  # Read file content
    sprite_doc = {
        "filename": file.filename,
        "filetype": file.content_type,
        "content": content,
        "uploaded_at": datetime.utcnow()
    }
    result = await db.sprites.insert_one(sprite_doc)  # Store in sprites collection
    return {"message": "Sprite uploaded", "id": str(result.inserted_id)}

# Endpoint: Upload an audio file
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

# Endpoint: Submit a player score (JSON body) with input sanitization
@app.post("/player_score")
async def add_score(score: PlayerScore):
    # Sanitize the player name to prevent special character injection
    safe_name = sanitize_text(score.player_name)

    # Prepare document safely with validated and sanitized input
    score_doc = {
        "player_name": safe_name,
        "score": score.score,
        "submitted_at": datetime.utcnow()
    }
    result = await db.scores.insert_one(score_doc)
    return {"message": "Score recorded", "id": str(result.inserted_id)}

# Optional: Get all scores (for testing/reviewing data)
@app.get("/scores")
async def get_scores():
    scores = []
    async for score in db.scores.find():
        score["_id"] = str(score["_id"])  # Convert Mongo ObjectId to string
        scores.append(score)
    return scores

# Root endpoint for testing
@app.get("/")
async def root():
    return {"message": "Game Assets API is running!"}
