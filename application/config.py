import json
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config():
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class LocalDevelopmentConfig(Config):
    SQLITE_DB_DIR = os.path.join(basedir, '../db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(SQLITE_DB_DIR, 'database.sqlite3')
    DEBUG = True

class APIKeys:
    with open('keys.json') as file:
        data = json.load(file)
    
    GEMINI_KEY = data['GEMINI_KEY']

    llm_config = {
        'model': GEMINI_KEY['MODEL'],
        'api_key': GEMINI_KEY['API_KEY'],
        'api_type': GEMINI_KEY['API_TYPE']
    }

class AgentGuide:
    with open('agent_guide.txt', 'r') as file:
        agent_guide = file.read()

