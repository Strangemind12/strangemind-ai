import datetime
import os
from pymongo import MongoClient
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://user:pass@cluster.mongodb.net/strangemindDB")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.example.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "smtp_user")
SMTP_PASS = os.getenv("SMTP_PASS", "smtp_password")

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client.strangemindDB
complaints_collection = db.complaints

def log_complaint(user_id: str, user_name: str, message: str) -> str:
    """Logs complaint to MongoDB and returns inserted ID."""
    complaint = {
        "user_id": user_id,
        "user_name": user_name,
        "message": message,
        "timestamp": datetime.datetime.utcnow()
    }
    result = complaints_collection.insert_one(complaint)
    return str(result.inserted_id)

def send_admin_email(complaint_id: str, user_id: str, user_name: str, message: str):
    """Send complaint notification email to admin."""
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = ADMIN_EMAIL
        msg['Subject'] = f"New Complaint Received - ID {complaint_id}"

        body = f"""
        New complaint logged:

        Complaint ID: {complaint_id}
        User ID: {user_id}
        User Name: {user_name}
        Message: {message}
        Timestamp: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
        """

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print(f"Admin notified for complaint ID: {complaint_id}")
    except Exception as e:
        print(f"Failed to send admin email: {e}")

def handle_complaint(user_id: str, user_name: str, message: str) -> str:
    """Validates, logs complaint, sends admin notification, and returns user reply."""
    if not message or len(message.strip()) < 10:
        return "⚠️ Please provide a detailed complaint (at least 10 characters)."

    complaint_id = log_complaint(user_id, user_name, message)
    send_admin_email(complaint_id, user_id, user_name, message)

    return (f"✅ Thanks for your feedback, {user_name}! "
            f"Your complaint ID is `{complaint_id}`. We'll review it ASAP.")

# Example local test (comment out in production)
if __name__ == "__main__":
    sample_user_id = "+2348012345678"
    sample_user_name = "Strangemind"
    sample_message = "Hey, the movie search feature sometimes returns broken links."

    response = handle_complaint(sample_user_id, sample_user_name, sample_message)
    print(response)# User complaint handling
