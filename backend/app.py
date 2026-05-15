import os
from dotenv import load_dotenv
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
# Import the db instance from your extensions file
from extensions import db 

load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_key')

# Initialize extensions with the app
db.init_app(app) # <--- KEY FIX
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# Import models
from models.olt_models import OLTDevice, ONU, PONPort, EthernetPort, DeviceMetric

# Import routes
from routes.olt_routes import olt_bp, init_db_service

# Import Socket.IO events
from services.socketio_events import setup_socketio_events

# Initialize database service
init_db_service(db)

# Register blueprints
app.register_blueprint(olt_bp, url_prefix='/api/olt')

# Setup Socket.IO events
setup_socketio_events(socketio)

# Create tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    print("=" * 50)
    print("OLT Management System - Flask Backend")
    print("Database: Connected Successfully")
    print(f"Flask Server: http://10.100.93.129:5000")
    print(f"Socket.IO: ws://10.100.93.129:5000")
    
    # Run with socketio
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)