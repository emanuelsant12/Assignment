from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

# MongoDB Atlas connection string 
# username: gameuser
# password: gamepass123
MONGO_URL = "mongodb+srv://gameuser:gamepass123@cluster0.5obdmcp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Connect to MongoDB Atlas
client = AsyncIOMotorClient(MONGO_URL)
db = client["game_assets_db"]  # This is your database name

@app.get("/")
async def root():
    return {"message": "Game Assets API is running!"}


from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
import motor.motor_asyncio

app = FastAPI()

# Connect to Mongo Atlas
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://gameuser:gamepass123@cluster0.5obdmcp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client.multimedia_db

class PlayerScore(BaseModel):
        player_name: str
        score: int
        
@app.post("/upload_sprite")
async def upload_sprite(file: UploadFile = File(...)):
    # In a real application, the file should be saved to a storage service
    content = await file.read()
    sprite_doc = {"filename": file.filename, "content": content}
    result = await db.sprites.insert_one(sprite_doc)
    return {"message": "Sprite uploaded", "id": str(result.inserted_id)}

@app.post("/upload_audio")
async def upload_audio(file: UploadFile = File(...)):
    content = await file.read()
    audio_doc = {"filename": file.filename, "content": content}
    result = await db.audio.insert_one(audio_doc)
    return {"message": "Audio file uploaded", "id": str(result.inserted_id)}

@app.post("/player_score")
async def add_score(score: PlayerScore):
    score_doc = score.dict()
    result = await db.scores.insert_one(score_doc)
    return {"message": "Score recorded", "id": str(result.inserted_id)}