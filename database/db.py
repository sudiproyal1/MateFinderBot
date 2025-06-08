from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["matefinder"]
users = db["users"]

def save_user(user_data):
    users.update_one({"id": user_data["id"]}, {"$set": user_data}, upsert=True)

def get_user(user_id):
    return users.find_one({"id": user_id})

def get_all_users():
    return list(users.find())

def delete_user(user_id):
    users.delete_one({"id": user_id})

def find_users_by_gender(gender):
    return list(users.find({"gender": gender}))

def add_to_list(user_id, field, value):
    users.update_one({"id": user_id}, {"$addToSet": {field: value}})

def get_users_liked_by(user_id):
    return users.find({"likes": user_id})

def get_liked_list(user_id):
    user = get_user(user_id)
    return user.get("likes", []) if user else []

def get_skipped_list(user_id):
    user = get_user(user_id)
    return user.get("skips", []) if user else []
  
