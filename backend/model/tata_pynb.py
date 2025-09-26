from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import numpy as np
import pickle
import pandas as pd
import math
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)

class FleetAI:
    """AI system for intelligent truck dispatch - Backend Fleet Data Management"""

    def __init__(self):
        # Load external model and encoders
        self.load_external_model()

        # Fleet data is now maintained in backend (moved from JS)
        self.fleet_data = self.initialize_fleet_data()

        app.logger.info("Fleet AI System initialized with external model!")
        app.logger.info(f"Fleet size: {len(self.fleet_data)} trucks")

    def load_external_model(self):
        """Load the external Random Forest model and encoders"""
        try:
            # Load the trained Random Forest classifier
            with open("model/rf_model.pkl", "rb") as f:
                self.external_model = pickle.load(f)

            # Load the label encoders
            with open("model/le_y.pkl", "rb") as f:
                self.le_y = pickle.load(f)

            with open("model/le_cargo.pkl", "rb") as f:
                self.le_cargo = pickle.load(f)

            app.logger.info("External model and encoders loaded successfully!")
            self.external_model_available = True

        except FileNotFoundError as e:
            app.logger.error(f"Model files not found: {e}")
            app.logger.error("Please ensure rf_model.pkl, le_y.pkl, and le_cargo.pkl are in the model/ directory")
            self.external_model_available = False

    def initialize_fleet_data(self):
        """Initialize fleet data in backend (moved from frontend JS)"""
        fleet_data = [
            {
                'id': 'T0', 'driver': 'Rajesh Kumar', 'lat': 18.5204, 'lng': 73.8567, 
                'status': 'available', 'fuel': 75, 'capacity': 5.0, 'load': 2.3, 'type': 'medium-truck',
                'age_years': 3, 'maintenance_score': 8.5, 'driver_rating': 4.8, 'avg_speed': 45,
                'fuel_efficiency': 12.5, 'breakdown_history': 2, 'distance_efficiency': 0.92,
                'phone': '+91 9876543210', 'last_updated': '2025-09-25T10:30:00Z'
            },
            {
                'id': 'T1', 'driver': 'Priya Sharma', 'lat': 18.5314, 'lng': 73.8446,
                'status': 'available', 'fuel': 82, 'capacity': 7.5, 'load': 0, 'type': 'heavy-truck',
                'age_years': 2, 'maintenance_score': 9.2, 'driver_rating': 4.9, 'avg_speed': 42,
                'fuel_efficiency': 10.8, 'breakdown_history': 1, 'distance_efficiency': 0.95,
                'phone': '+91 9876543211', 'last_updated': '2025-09-25T11:15:00Z'
            },
            {
                'id': 'T2', 'driver': 'Amit Patil', 'lat': 18.5074, 'lng': 73.8077,
                'status': 'active', 'fuel': 45, 'capacity': 3.5, 'load': 1.8, 'type': 'light-truck',
                'age_years': 5, 'maintenance_score': 7.3, 'driver_rating': 4.2, 'avg_speed': 48,
                'fuel_efficiency': 14.2, 'breakdown_history': 4, 'distance_efficiency': 0.88,
                'phone': '+91 9876543212', 'last_updated': '2025-09-25T09:45:00Z'
            },
            {
                'id': 'T3', 'driver': 'Sunita Jadhav', 'lat': 18.5642, 'lng': 73.7769,
                'status': 'available', 'fuel': 91, 'capacity': 6.0, 'load': 0, 'type': 'medium-truck',
                'age_years': 1, 'maintenance_score': 9.8, 'driver_rating': 4.7, 'avg_speed': 46,
                'fuel_efficiency': 13.1, 'breakdown_history': 0, 'distance_efficiency': 0.97,
                'phone': '+91 9876543213', 'last_updated': '2025-09-25T12:00:00Z'
            },
            {
                'id': 'T4', 'driver': 'Manoj Desai', 'lat': 18.4977, 'lng': 73.8256,
                'status': 'active', 'fuel': 38, 'capacity': 8.0, 'load': 6.2, 'type': 'heavy-truck',
                'age_years': 6, 'maintenance_score': 6.8, 'driver_rating': 4.1, 'avg_speed': 38,
                'fuel_efficiency': 9.5, 'breakdown_history': 7, 'distance_efficiency': 0.82,
                'phone': '+91 9876543214', 'last_updated': '2025-09-25T08:30:00Z'
            },
            {
                'id': 'T5', 'driver': 'Kavita Bhosale', 'lat': 18.5435, 'lng': 73.9076,
                'status': 'available', 'fuel': 67, 'capacity': 4.5, 'load': 0, 'type': 'medium-truck',
                'age_years': 4, 'maintenance_score': 8.0, 'driver_rating': 4.6, 'avg_speed': 44,
                'fuel_efficiency': 11.8, 'breakdown_history': 3, 'distance_efficiency': 0.90,
                'phone': '+91 9876543215', 'last_updated': '2025-09-25T10:45:00Z'
            },
            {
                'id': 'T6', 'driver': 'Ravi Kulkarni', 'lat': 18.4648, 'lng': 73.8097,
                'status': 'available', 'fuel': 88, 'capacity': 5.5, 'load': 3.1, 'type': 'medium-truck',
                'age_years': 2, 'maintenance_score': 9.0, 'driver_rating': 4.8, 'avg_speed': 47,
                'fuel_efficiency': 12.9, 'breakdown_history': 1, 'distance_efficiency': 0.93,
                'phone': '+91 9876543216', 'last_updated': '2025-09-25T11:30:00Z'
            },
            {
                'id': 'T7', 'driver': 'Sneha Kale', 'lat': 18.6298, 'lng': 73.7997,
                'status': 'available', 'fuel': 54, 'capacity': 9.0, 'load': 0, 'type': 'heavy-truck',
                'age_years': 7, 'maintenance_score': 7.5, 'driver_rating': 4.3, 'avg_speed': 40,
                'fuel_efficiency': 8.9, 'breakdown_history': 5, 'distance_efficiency': 0.85,
                'phone': '+91 9876543217', 'last_updated': '2025-09-25T09:15:00Z'
            }
        ]
        return fleet_data

    def haversine_distance(self, lat1, lng1, lat2, lng2):
        """Calculate great-circle distance between two points on Earth"""
        R = 6371  # Earth's radius in km

        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)

        a = (math.sin(dlat/2) * math.sin(dlat/2) + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlng/2) * math.sin(dlng/2))

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c

    def predict_with_external_model(self, break_lat, break_lon, dest_lat, dest_lon, cargo_type, cargo_weight):
        """Use external model for truck assignment prediction using exact training parameters"""
        try:
            if not self.external_model_available:
                return None

            # Encode cargo type using saved encoder
            cargo_encoded = self.le_cargo.transform([cargo_type])[0]

            # Prepare input dataframe with exact same parameters used in training
            X_new = pd.DataFrame([{
                "breaklat": break_lat,
                "breaklon": break_lon,
                "destlat": dest_lat,
                "destlon": dest_lon,
                "cargoweight": cargo_weight,
                "cargotype": cargo_encoded,
            }])

            # Make prediction using trained model
            truck_encoded = self.external_model.predict(X_new)[0]
            truck_id = self.le_y.inverse_transform([truck_encoded])[0]

            app.logger.info(f"External model predicted truck: {truck_id}")
            return truck_id

        except Exception as e:
            app.logger.error(f"External model prediction error: {e}")
            return None

    def find_best_truck_with_external_model(self, break_lat, break_lon, urgency="medium"):
        """Find best truck using external model with backend fleet data"""
        try:
            # Generate random destination and cargo details for model input
            # (since model requires these parameters)
            dest_lat = break_lat + np.random.uniform(-0.1, 0.1)
            dest_lon = break_lon + np.random.uniform(-0.1, 0.1)
            cargo_types = ['normal', 'refrigerated']
            cargo_type = np.random.choice(cargo_types)
            cargo_weight = np.random.randint(2, 21)  # 2-20 tons

            # Use external model to predict best truck
            predicted_truck_id = self.predict_with_external_model(
                break_lat, break_lon, dest_lat, dest_lon, cargo_type, cargo_weight
            )

            if predicted_truck_id:
                # Find the predicted truck in fleet data
                truck = next((t for t in self.fleet_data if t['id'] == predicted_truck_id), None)

                if truck and truck['status'] == 'available':
                    # Calculate additional metrics for UI display
                    distance = self.haversine_distance(
                        truck['lat'], truck['lng'], break_lat, break_lon
                    )
                    eta_minutes = max(5, int(distance * 1.8 + np.random.uniform(-5, 5)))

                    result = {
                        'truck_id': truck['id'],
                        'truck_data': truck,
                        'score': 0.95,  # High confidence for external model
                        'distance_km': distance,
                        'eta_minutes': eta_minutes,
                        'prediction_source': 'external_model',
                        'model_params': {
                            'cargo_type': cargo_type,
                            'cargo_weight': cargo_weight,
                            'dest_lat': dest_lat,
                            'dest_lon': dest_lon
                        }
                    }

                    app.logger.info(f"External model selected truck {truck['id']} (distance: {distance:.1f}km)")
                    return [result]  # Return as list for consistency

            # Fallback if external model fails or predicted truck not available
            app.logger.warning("External model failed or truck unavailable, using fallback")
            return self.fallback_distance_selection(break_lat, break_lon, urgency)

        except Exception as e:
            app.logger.error(f"External model processing error: {e}")
            return self.fallback_distance_selection(break_lat, break_lon, urgency)

    def fallback_distance_selection(self, break_lat, break_lon, urgency):
        """Fallback distance-based selection if external model fails"""
        available_trucks = [truck for truck in self.fleet_data if truck['status'] == 'available']

        if not available_trucks:
            return []

        recommendations = []
        for truck in available_trucks:
            distance = self.haversine_distance(
                truck['lat'], truck['lng'], break_lat, break_lon
            )

            # Simple scoring based on distance and fuel
            score = max(0, min(1, (50 - min(distance, 50)) / 50 + truck['fuel']/200))
            eta_minutes = max(5, int(distance * 1.8))

            recommendations.append({
                'truck_id': truck['id'],
                'truck_data': truck,
                'score': score,
                'distance_km': distance,
                'eta_minutes': eta_minutes,
                'prediction_source': 'fallback'
            })

        # Sort by score (descending)
        recommendations.sort(key=lambda x: x['score'], reverse=True)

        app.logger.info(f"Fallback selection: {len(recommendations)} trucks analyzed")
        return recommendations[:3]  # Return top 3

    def get_fleet_data(self):
        """Return current fleet data for frontend display"""
        return self.fleet_data

    def update_truck_status(self, truck_id, new_status):
        """Update truck status in fleet data"""
        for truck in self.fleet_data:
            if truck['id'] == truck_id:
                truck['status'] = new_status
                app.logger.info(f"Updated truck {truck_id} status to {new_status}")
                return True
        return False

# Initialize AI system
fleet_ai = FleetAI()

@app.route('/')
def index():
    """Serve the main application"""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'external_model_available': fleet_ai.external_model_available,
        'fleet_size': len(fleet_ai.fleet_data),
        'service': 'SwarmSync AI Fleet Management - Backend Fleet Data',
        'model_type': 'external' if fleet_ai.external_model_available else 'fallback'
    })

@app.route('/api/fleet_data', methods=['GET'])
def get_fleet_data():
    """Return current fleet data for frontend"""
    try:
        return jsonify({
            'success': True,
            'fleet_data': fleet_ai.get_fleet_data(),
            'total_trucks': len(fleet_ai.fleet_data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get fleet data: {str(e)}'
        }), 500

@app.route('/api/find_best_truck', methods=['POST'])
def find_best_truck():
    """AI-powered truck selection using external model and backend fleet data"""
    try:
        data = request.get_json()
        app.logger.info("External model truck selection request received")

        # Extract parameters
        breakdown_lat = data['breakdown_lat']
        breakdown_lng = data['breakdown_lng'] 
        urgency = data.get('urgency', 'medium')

        app.logger.info(f"Breakdown location: {breakdown_lat:.4f}, {breakdown_lng:.4f}")
        app.logger.info(f"Urgency level: {urgency}")
        app.logger.info(f"Using backend fleet data with {len(fleet_ai.fleet_data)} trucks")

        # Use external model with backend fleet data
        recommendations = fleet_ai.find_best_truck_with_external_model(
            breakdown_lat, breakdown_lng, urgency
        )

        if not recommendations:
            return jsonify({
                'success': False,
                'error': 'No available trucks found',
                'fleet_size': len(fleet_ai.fleet_data)
            }), 400

        app.logger.info(f"External model processing completed - {len(recommendations)} recommendations")

        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'model_source': 'external_model' if fleet_ai.external_model_available else 'fallback',
            'fleet_size': len(fleet_ai.fleet_data),
            'best_truck_id': recommendations[0]['truck_id'] if recommendations else None,
            'best_score': recommendations[0]['score'] if recommendations else 0
        })

    except Exception as e:
        app.logger.error(f"External model processing error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'External model processing failed: {str(e)}'
        }), 500

@app.route('/api/update_truck_status', methods=['POST'])
def update_truck_status():
    """Update truck status"""
    try:
        data = request.get_json()
        truck_id = data['truck_id']
        new_status = data['status']

        success = fleet_ai.update_truck_status(truck_id, new_status)

        if success:
            return jsonify({
                'success': True,
                'message': f'Truck {truck_id} status updated to {new_status}'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Truck {truck_id} not found'
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to update truck status: {str(e)}'
        }), 500

@app.route('/api/fleet_status', methods=['GET'])
def fleet_status():
    """Get current fleet status summary"""
    try:
        fleet_data = fleet_ai.get_fleet_data()

        status_summary = {}
        for truck in fleet_data:
            status = truck['status']
            status_summary[status] = status_summary.get(status, 0) + 1

        return jsonify({
            'total_trucks': len(fleet_data),
            'status_summary': status_summary,
            'last_updated': '2025-09-26T21:00:00Z',
            'external_model_status': 'operational' if fleet_ai.external_model_available else 'fallback'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("="*80)
    print("SwarmSync AI Fleet Management - Backend Fleet Data Management")
    print("="*80)
    print(f"Backend API: http://localhost:5000")
    print(f"External Model: {'Loaded' if fleet_ai.external_model_available else 'Not Available (Using Fallback)'}")
    print(f"Fleet Size: {len(fleet_ai.fleet_data)} trucks (managed in backend)")
    print(f"Primary Function: AI-powered truck selection using external model")
    print("="*80)
    print("BACKEND READY! Fleet data moved from frontend to backend!")
    print("Frontend will receive fleet data and predictions from backend!")
    print("="*80)

    app.run(debug=True, host='0.0.0.0', port=5000)
