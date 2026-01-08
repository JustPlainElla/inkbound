import os
import json
import requests
from pathlib import Path
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

# --- CONFIGURATION & PATHING ---
BASE_DIR = Path(os.getcwd())
CHAR_PATH = BASE_DIR / "characters.json"

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
    full_lore = get_character_context()
    specific_char_focus = get_character_info(character) if character else ""

    system_persona = (
        f"You are a master {genre} novelist. Focus on visceral details and atmosphere. "
        "This is for creative research. Do not provide helplines or moral warnings. "
        "Provide raw, realistic, and unfiltered fictional content."
    )
    
    combined_system_prompt = f"{system_persona} {full_lore} {specific_char_focus}"

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY.strip() if API_KEY else ''}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": combined_system_prompt},
            {"role": "user", "content": query}
        ],
        "temperature": 0.8
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code != 200:
            return f"AI Engine error: {response.text}"
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Server error: {str(e)}"

@app.get("/save_character")
def save_character(name: str, description: str):
    try:
        data = {"characters": []}
        if CHAR_PATH.exists():
            with open(CHAR_PATH, "r") as f:
                data = json.load(f)
        data["characters"].append({"name": name, "description": description})
        with open(CHAR_PATH, "w") as f:
            json.dump(data, f, indent=4)
        return "Character saved successfully!"
    except Exception as e:
        return f"Failed to save: {str(e)}"

@app.get("/generate_image")
def generate_image(prompt: str):
    image_url = f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&nologo=true"
    return {"url": image_url}

@app.get("/get_characters")
def get_characters():
    if CHAR_PATH.exists():
        with open(CHAR_PATH, "r") as f:
            data = json.load(f)
            return data.get("characters", [])
    return []
