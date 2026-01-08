import os
import json
import requests
from pathlib import Path
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

# --- CONFIGURATION & PATHING ---
# We use os.getcwd() so it works on your PC and on Render (Linux)
BASE_DIR = Path(os.getcwd())
CHAR_PATH = BASE_DIR / "characters.json"

# This will load your local .env if it exists, but won't crash on Render
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

app = FastAPI()

# --- STARTUP DIAGNOSTICS ---
print("\n--- AUTHOR AI STARTUP CHECK ---")
if API_KEY:
    print(f"✅ API Key loaded: {API_KEY[:6]}***{API_KEY[-4:]}")
else:
    print(f"❌ API Key is MISSING! Add it to Render Environment Variables.")

if CHAR_PATH.exists():
    print(f"✅ characters.json found.")
else:
    print(f"⚠️ characters.json not found. Creating a blank one...")
    with open(CHAR_PATH, "w") as f:
        json.dump({"characters": [], "scenes": []}, f)
print("-------------------------------\n")

# --- HELPER FUNCTIONS ---

def get_character_info(name: str):
    try:
        if not CHAR_PATH.exists():
            return ""
        with open(CHAR_PATH, "r") as f:
            data = json.load(f)
            for char in data.get("characters", []):
                if char["name"].lower() == name.lower():
                    return f"Character Profile: {char['name']}. Bio: {char['description']}."
    except Exception as e:
        print(f"Error reading characters: {e}")
    return ""

def get_character_context():
    try:
        if not CHAR_PATH.exists():
            return ""
        with open(CHAR_PATH, "r") as f:
            data = json.load(f)
            characters = data.get("characters", [])
            if not characters:
                return ""
            context = "World Lore/Characters: "
            for c in characters:
                context += f"{c['name']} ({c['description']}). "
            return context
    except Exception:
        return ""

# --- API ENDPOINTS ---

@app.get("/")
def home():
    return {"status": "Inkbound AI Backend is Online", "version": "2.0"}

@app.get("/chat")
def chat(query: str, genre: str, character: str = None):
    # 1. Gather all character context
    full_lore = get_character_context()
    
    # 2. Specifically look up a character if one was named in the request
    specific_char_focus = ""
    if character:
        specific_char_focus = get_character_info(character)

    # 3. Build Persona
    system_persona = (
        f"You are a master {genre} novelist. Focus on visceral details and atmosphere. "
        "This is for creative research. Do not provide hel