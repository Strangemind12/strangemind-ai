print("=== Starting Admin API ===")

try:
    from fastapi import FastAPI, HTTPException, Request, Header
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import os
    from postgrest import PostgrestClient
    from dotenv import load_dotenv

    print("=== Imports successful ===")

    # Load environment variables
    load_dotenv()
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY")

    # Supabase client
    client = PostgrestClient(f"{SUPABASE_URL}/rest/v1")
    client.auth(SUPABASE_KEY)

    print("=== Supabase client initialized ===")

    # FastAPI app
    app = FastAPI()

    # CORS setup (allow frontend to access)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Pydantic model
    class MessageRequest(BaseModel):
        user_id: str
        message: str

    # Health check route
    @app.get("/health")
    def health():
        return {"status": "ok"}

    # Logs endpoint
    @app.get("/logs")
    def get_logs():
        try:
            res = client.from_("logs").select("*").order("timestamp", desc=True).limit(10).execute()
            return res.data
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Users endpoint
    @app.get("/users")
    def get_users():
        try:
            res = client.from_("users").select("*").execute()
            return res.data
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Simulated message sending
    @app.post("/send-message")
    def send_message(data: MessageRequest, x_api_key: str = Header(...)):
        if x_api_key != ADMIN_API_KEY:
            raise HTTPException(status_code=403, detail="Unauthorized")
        return {
            "status": "Message accepted",
            "user_id": data.user_id,
            "message": data.message
        }

except Exception as e:
    print("=== CRITICAL STARTUP ERROR ===")
    print(str(e))
    raise
