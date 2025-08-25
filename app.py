import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
os.environ['DATABASE_URL']="postgresql://neondb_owner:npg_3kwA6KTBGVci@ep-jolly-surf-af4x4sxk.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///mental_health_tracker.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Configure Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True

# Initialize extensions
db.init_app(app)
Session(app)

with app.app_context():
    # Import models to ensure tables are created
    import models
    db.create_all()

# Import routes
import routes
