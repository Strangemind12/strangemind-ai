from fastapi import FastAPI, HTTPException, Request, Header from fastapi.middleware.cors import CORSMiddleware from pydantic import BaseModel import os from postgrest import PostgrestClient from dotenv import load_dotenv

Load environment variables

load_dotenv() SUPABASE_URL = os.getenv("SUPABASE_URL") SUPABASE_KEY = os.getenv("SUPABASE_KEY") ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")

Supabase client

client = PostgrestClient(f"{SUPABASE_URL}/rest/v1") client.auth(SUPABASE_KEY)

FastAPI app

app = FastAPI()

CORS (allow frontend to fetch data)

app.add_middleware( CORSMiddleware, allow_origins=[""], allow_credentials=True, allow_methods=[""], allow_headers=["*"], )

Models

class MessageRequest(BaseModel): user_id: str message: str

Health check

@app.get("/health") def health(): return {"status": "ok"}

Get recent logs

@app.get("/logs") def get_logs(): try: res = client.from_("logs").select("*").order("timestamp", desc=True).limit(10).execute() return res.data except Exception as e: raise HTTPException(status_code=500, detail=str(e))

Get users

@app.get("/users") def get_users(): try: res = client.from_("users").select("*").execute() return res.data except Exception as e: raise HTTPException(status_code=500, detail=str(e))

Simulate sending a message

@app.post("/send-message") def send_message(data: MessageRequest, x_api_key: str = Header(...)): if x_api_key != ADMIN_API_KEY: raise HTTPException(status_code=403, detail="Unauthorized") return {"status": "Message accepted", "user_id": data.user_id, "message": data.message}

