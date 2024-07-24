from flask import Flask
import pymongo
from flask_cors import CORS
from flask_apscheduler import APScheduler
from passlib.hash import pbkdf2_sha256

app = Flask(__name__)
CORS(app)


app.secret_key = b'\xcc^\x91\xea\x17-\xd0W\x03\xa7\xf8J0\xac8\xc5'

# Database
dbUrl = 'mongodb+srv://vyomthaker:vyom2154@cluster0.fllequq.mongodb.net/<dbname>?retryWrites=true&w=majority'
client = pymongo.MongoClient(dbUrl)
db = client.user_login_system

if not db.users.find_one({ "email": "admin@admin.com" }):
    db.users.insert_one({
        "name": "Admin", 
        "email": "admin@admin.com", 
        "password": pbkdf2_sha256.hash('admin'), 
        "role": "admin"
        })
# if not db.riders.find_one({ "email": "admin@admin.com" }):
#     db.rider.insert_one({
#         "name": "Admin", 
#         "email": "admin@admin.com", 
#         "password": pbkdf2_sha256.hash('admin'), 
#         "role": "admin"
#         })

# Scheduler
class Config:
    SCHEDULER_API_ENABLED = True
    
scheduler = APScheduler()
from schedulers.jobs import *

# Routes
from routes import *

if __name__ == "__main__":
    app.config.from_object(Config())
    scheduler.init_app(app)
    scheduler.start()
    app.run(debug=True)