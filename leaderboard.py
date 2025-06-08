import datetime from pymongo import MongoClient from config import MONGO_URI

client = MongoClient(MONGO_URI) db = client.strangemindDB game_collection = db.game_data

def get_leaderboard(top_n=10, sort_by="vault"): """ Fetch top N users sorted by vault amount or XP. """ if sort_by not in ["vault", "xp"]: sort_by = "vault"

leaders = game_collection.find().sort(sort_by, -1).limit(top_n)
result = []
for i, user in enumerate(leaders, 1):
    display_name = user.get("name", user.get("phone", "Unknown"))
    result.append(f"{i}. {display_name} - {user.get(sort_by, 0)}")
return "\n".join(result)

def handle_leaderboard_command(sort_by="vault"): """ Builds the leaderboard message to send on WhatsApp. """ header = "🏆 Strangemind AI Leaderboard 🧠\n" header += f"Sorted by {sort_by.upper()}\n\n" board = get_leaderboard(sort_by=sort_by) footer = "\nKeep playing to rise in the ranks! ✨" return header + board + footer

Example usage

if name == "main": print(handle_leaderboard_command("xp"))
