from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from postgrest import PostgrestClient
from dotenv import load_dotenv
import os

# === Startup Logs ===
print("=== Starting Admin API ===")

# === Load Environment Variables ===
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("=== CRITICAL STARTUP ERROR ===")
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY")

# === Init Supabase Client ===
client = PostgrestClient(f"{SUPABASE_URL}/rest/v1", headers={
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
})

print("=== Supabase client initialized ===")

# === Init FastAPI App ===
app = FastAPI()

# === CORS Config ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can limit to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Models ===
class MessageRequest(BaseModel):
    user_id: str
    message: str

# === Routes ===
@app.get("/")
def root():
    return {"status": "Admin API is alive"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/logs")
def get_logs():
    try:
        res = client.from_("logs").select("*").order("timestamp", desc=True).limit(10).execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users")
def get_users():
    try:
        res = client.from_("users").select("*").execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send-message")
def send_message(data: MessageRequest, x_api_key: str = Header(...)):
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return {
        "status": "Message accepted",
        "user_id": data.user_id,
        "message": data.message
    }
