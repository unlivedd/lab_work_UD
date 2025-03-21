import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "task_manager"