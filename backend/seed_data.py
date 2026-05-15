import os
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)

# Import models
from models.olt_models import OLTDevice, PONPort, EthernetPort, ONU

def seed_database():
    """Seed the database with sample data"""
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if data already exists
        existing_device = OLTDevice.query.filter_by(id='C-DATA-137.59.48.195').first()
        if existing_device:
            print("Database already seeded. Skipping...")
            return
        
        print("Seeding database with sample data...")
        
        # Create sample device
        device = OLTDevice(
            id='C-DATA-137.59.48.195',
            model='C-DATA FD36024H',
            vendor='C-DATA',
            ip_address='137.59.48.195',
            status='online',
            cpu_usage=45.2,
            memory_usage=62.5,
            temperature=38.5,
            total_onu_count=24,
            online_onu_count=22,
            created_at=datetime.utcnow()
        )
        db.session.add(device)
        db.session.flush()
        
        # Create PON ports
        pon_port_numbers = [1, 2, 3, 4]
        for port_num in pon_port_numbers:
            pon_port = PONPort(
                id=f'C-DATA-137.59.48.195-PON-{port_num}',
                device_id='C-DATA-137.59.48.195',
                port_number=port_num,
                port_name=f'PON-{port_num}',
                status='online',
                port_type='PON',
                updated_at=datetime.utcnow()
            )
            db.session.add(pon_port)
        
        # Create Ethernet ports
        eth_port_numbers = [1, 2, 3, 4, 5, 6]
        for port_num in eth_port_numbers:
            eth_port = EthernetPort(
                id=f'C-DATA-137.59.48.195-ETH-{port_num}',
                device_id='C-DATA-137.59.48.195',
                port_number=port_num,
                port_name=f'ETH-{port_num}',
                status='online' if port_num <= 4 else 'offline',
                port_type='ETH',
                updated_at=datetime.utcnow()
            )
            db.session.add(eth_port)
        
        # Create sample ONUs for PON-1
        for onu_idx in range(1, 7):
            onu = ONU(
                id=f'ONU-{onu_idx:03d}',
                device_id='C-DATA-137.59.48.195',
                port_id=1,
                onu_index=onu_idx,
                serial_number=f'CDDA{1000 + onu_idx:04d}',
                mac_address=f'00:11:22:33:44:{onu_idx:02x}',
                status='online',
                optical_power_downstream=-19.5 + onu_idx * 0.5,
                optical_power_upstream=-21.3 + onu_idx * 0.3,
                distance_km=2.5 + onu_idx * 0.1,
                updated_at=datetime.utcnow()
            )
            db.session.add(onu)
        
        # Create sample ONUs for PON-2
        for onu_idx in range(7, 13):
            onu = ONU(
                id=f'ONU-{onu_idx:03d}',
                device_id='C-DATA-137.59.48.195',
                port_id=2,
                onu_index=onu_idx - 6,
                serial_number=f'CDDA{1000 + onu_idx:04d}',
                mac_address=f'00:11:22:33:44:{onu_idx:02x}',
                status='online',
                optical_power_downstream=-20.5 + onu_idx * 0.4,
                optical_power_upstream=-22.3 + onu_idx * 0.2,
                distance_km=1.8 + onu_idx * 0.1,
                updated_at=datetime.utcnow()
            )
            db.session.add(onu)
        
        # Commit all changes
        db.session.commit()
        print("Database seeded successfully!")
        print(f"- Created device: C-DATA-137.59.48.195")
        print(f"- Created 4 PON ports")
        print(f"- Created 6 Ethernet ports")
        print(f"- Created 12 sample ONUs")


if __name__ == '__main__':
    seed_database()
