from pymongo import MongoClient
from datetime import datetime, timedelta
from bson import ObjectId 
from config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
tasks_collection = db.tasks


def add_task(user_id, text, deadline: datetime):
    task = {
        "user_id": user_id,
        "text": text,
        "deadline": deadline, 
        "completed": False
    }
    tasks_collection.insert_one(task)

def get_tasks(user_id):
    return list(tasks_collection.find({"user_id": user_id}))

def update_task(task_id, new_text=None, completed=None):

    update_data = {}
    if new_text:
        update_data["text"] = new_text
    if completed is not None:
        update_data["completed"] = completed
    
    result = tasks_collection.update_one(
        {"_id": ObjectId(task_id)}, 
        {"$set": update_data}
    )
    return result.modified_count 

def delete_tasks_by_date(user_id, date_str):

    target_date = datetime.strptime(date_str, "%Y-%m-%d")
    tasks_collection.delete_many({
        "user_id": user_id,
        "deadline": {
            "$gte": target_date,
            "$lt": target_date + timedelta(days=1)
        }
    })