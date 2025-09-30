import pickle
import pandas as pd
import os

def create_fleet_data_model():
    """Create simple fleet data matching training model truck IDs"""
    
    # Create model directory if it doesn't exist
    os.makedirs('model', exist_ok=True)
    
    # Simple fleet data with truck IDs that match your training model
    # Only essential data needed for UI display
    fleet_data = [
        {
            'id': 'T0', 'driver': 'Rajesh Kumar', 'lat': 18.5204, 'lng': 73.8567, 
            'status': 'available', 'fuel': 75, 'type': 'Medium Truck', 'capacity': 5.0, 'load': 2.3,
            'phone': '+91 9876543210'
        },
        {
            'id': 'T1', 'driver': 'Priya Sharma', 'lat': 18.5314, 'lng': 73.8446,
            'status': 'available', 'fuel': 82, 'type': 'Heavy Truck', 'capacity': 7.5, 'load': 0,
            'phone': '+91 9876543211'
        },
        {
            'id': 'T2', 'driver': 'Amit Patil', 'lat': 18.5074, 'lng': 73.8077,
            'status': 'active', 'fuel': 45, 'type': 'Light Truck', 'capacity': 3.5, 'load': 1.8,
            'phone': '+91 9876543212'
        },
        {
            'id': 'T3', 'driver': 'Sunita Jadhav', 'lat': 18.5642, 'lng': 73.7769,
            'status': 'available', 'fuel': 91, 'type': 'Medium Truck', 'capacity': 6.0, 'load': 0,
            'phone': '+91 9876543213'
        },
        {
            'id': 'T4', 'driver': 'Manoj Desai', 'lat': 18.4977, 'lng': 73.8256,
            'status': 'active', 'fuel': 38, 'type': 'Heavy Truck', 'capacity': 8.0, 'load': 6.2,
            'phone': '+91 9876543214'
        },
        {
            'id': 'T5', 'driver': 'Kavita Bhosale', 'lat': 18.5435, 'lng': 73.9076,
            'status': 'available', 'fuel': 67, 'type': 'Medium Truck', 'capacity': 4.5, 'load': 0,
            'phone': '+91 9876543215'
        },
        {
            'id': 'T6', 'driver': 'Ravi Kulkarni', 'lat': 18.4648, 'lng': 73.8097,
            'status': 'available', 'fuel': 88, 'type': 'Medium Truck', 'capacity': 5.5, 'load': 3.1,
            'phone': '+91 9876543216'
        },
        {
            'id': 'T7', 'driver': 'Sneha Kale', 'lat': 18.6298, 'lng': 73.7997,
            'status': 'available', 'fuel': 54, 'type': 'Heavy Truck', 'capacity': 9.0, 'load': 0,
            'phone': '+91 9876543217'
        },
        {
            'id': 'T8', 'driver': 'Vikram Jagtap', 'lat': 18.4586, 'lng': 73.8370,
            'status': 'available', 'fuel': 73, 'type': 'Light Truck', 'capacity': 3.0, 'load': 1.5,
            'phone': '+91 9876543218'
        },
        {
            'id': 'T9', 'driver': 'Anita More', 'lat': 18.5751, 'lng': 73.8321,
            'status': 'available', 'fuel': 65, 'type': 'Medium Truck', 'capacity': 5.5, 'load': 2.1,
            'phone': '+91 9876543219'
        }
    ]
    
    # Save fleet data as pickle file
    with open('model/fleet_data.pkl', 'wb') as f:
        pickle.dump(fleet_data, f)
    
    print("✅ Fleet data saved to model/fleet_data.pkl")
    print(f"✅ Created {len(fleet_data)} trucks with IDs: {[truck['id'] for truck in fleet_data]}")
    
    # Also create a simple lookup for quick reference
    truck_locations = {}
    for truck in fleet_data:
        truck_locations[truck['id']] = {
            'lat': truck['lat'], 
            'lng': truck['lng'],
            'status': truck['status']
        }
   
    with open('model/truck_locations.pkl', 'wb') as f:
        pickle.dump(truck_locations, f)
    
    print("✅ Truck locations saved to model/truck_locations.pkl")
    
    return fleet_data

if __name__ == "__main__":
    create_fleet_data_model()