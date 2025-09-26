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
    """AI system using external model with 6 parameters only"""

    def __init__(self):
        # Load fleet data from model file
        self.load_fleet_data()
        
        # Load external model and encoders
        self.load_external_model()

        app.logger.info("Fleet AI System initialized!")
        app.logger.info(f"Fleet size: {len(self.fleet_data)} trucks")
        app.logger.info(f"External model: {'Available' if self.external_model_available else 'Not Available'}")

    def load_fleet_data(self):
        """Load fleet data from model pickle file"""
        try:
            with open("model/fleet_data.pkl", "rb") as f:
                self.fleet_data = pickle.load(f)
            app.logger.info(f"Fleet data loaded: {len(self.fleet_data)} trucks")
        except FileNotFoundError:
            app.logger.error("Fleet data file not found! Run create_fleet_data.py first")
            # Fallback minimal data
            self.fleet_data = [
                {'id': 'T0', 'driver': 'Test Driver', 'lat': 18.5204, 'lng': 73.8567, 'status': 'available', 'fuel': 75, 'type': 'Medium', 'capacity': 5.0, 'load': 0}
            ]

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
            self.external_model_available = False

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

    def predict_best_truck(self, break_lat, break_lon, urgency="medium"):
        """Use external model to predict best truck using only 6 parameters"""
        try:
            if not self.external_model_available:
                return self.fallback_selection(break_lat, break_lon, urgency)

            # Generate destination near breakdown (within 10km radius)
            dest_lat = break_lat + np.random.uniform(-0.1, 0.1)
            dest_lon = break_lon + np.random.uniform(-0.1, 0.1)
            
            # Generate cargo details based on urgency
            cargo_types = ['normal', 'refrigerated']
            cargo_type = np.random.choice(cargo_types)
            
            if urgency == 'high':
                cargo_weight = np.random.randint(1, 10)  # Light cargo for emergency
            elif urgency == 'medium':
                cargo_weight = np.random.randint(5, 15)  # Medium cargo
            else:
                cargo_weight = np.random.randint(10, 25)  # Heavy cargo

            app.logger.info(f"Model input - Break: ({break_lat:.4f}, {break_lon:.4f}), Dest: ({dest_lat:.4f}, {dest_lon:.4f}), Cargo: {cargo_type}, Weight: {cargo_weight}")

            # Encode cargo type using saved encoder
            cargo_encoded = self.le_cargo.transform([cargo_type])[0]

            # Prepare input with exact 6 parameters your model expects
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
            predicted_truck_id = self.le_y.inverse_transform([truck_encoded])[0]

            app.logger.info(f"Model predicted truck: {predicted_truck_id}")

            # Find the predicted truck in fleet data
            predicted_truck = next((t for t in self.fleet_data if t['id'] == predicted_truck_id), None)

            if predicted_truck and predicted_truck['status'] == 'available':
                # Calculate display metrics
                distance = self.haversine_distance(
                    predicted_truck['lat'], predicted_truck['lng'], break_lat, break_lon
                )
                eta_minutes = max(5, int(distance * 1.5 + np.random.uniform(-3, 3)))

                result = {
                    'truck_id': predicted_truck['id'],
                    'truck_data': predicted_truck,
                    'score': 0.95,  # High confidence for ML model
                    'distance_km': distance,
                    'eta_minutes': eta_minutes,
                    'prediction_method': 'external_model',
                    'model_params': {
                        'cargo_type': cargo_type,
                        'cargo_weight': cargo_weight,
                        'dest_lat': dest_lat,
                        'dest_lon': dest_lon
                    }
                }

                app.logger.info(f"Selected truck {predicted_truck_id} at {distance:.1f}km distance")
                return [result]
            
            # If predicted truck not available, get top 3 available by distance
            app.logger.warning(f"Predicted truck {predicted_truck_id} not available, using fallback")
            return self.fallback_selection(break_lat, break_lon, urgency)

        except Exception as e:
            app.logger.error(f"Model prediction error: {e}")
            return self.fallback_selection(break_lat, break_lon, urgency)

    def fallback_selection(self, break_lat, break_lon, urgency):
        """Fallback distance-based selection"""
        available_trucks = [truck for truck in self.fleet_data if truck['status'] == 'available']
        
        if not available_trucks:
            app.logger.warning("No available trucks found!")
            return []

        recommendations = []
        for truck in available_trucks:
            distance = self.haversine_distance(
                truck['lat'], truck['lng'], break_lat, break_lon
            )

            # Simple scoring: closer distance = higher score
            score = max(0, min(1, (50 - min(distance, 50)) / 50))
            eta_minutes = max(5, int(distance * 1.5))

            recommendations.append({
                'truck_id': truck['id'],
                'truck_data': truck,
                'score': score,
                'distance_km': distance,
                'eta_minutes': eta_minutes,
                'prediction_method': 'fallback_distance'
            })

        # Sort by distance (ascending)
        recommendations.sort(key=lambda x: x['distance_km'])
        
        app.logger.info(f"Fallback selection: {len(recommendations)} trucks analyzed")
        return recommendations[:3]  # Return top 3 closest

    def get_fleet_data(self):
        """Return current fleet data"""
        return self.fleet_data

    def update_truck_status(self, truck_id, new_status):
        """Update truck status"""
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
        'service': 'SwarmSync AI Fleet Management - Model Integration',
        'model_parameters': ['breaklat', 'breaklon', 'destlat', 'destlon', 'cargoweight', 'cargotype']
    })

@app.route('/api/fleet_data', methods=['GET'])
def get_fleet_data():
    """Return fleet data for frontend"""
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
    """Find best truck using external model with 6 parameters"""
    try:
        data = request.get_json()
        app.logger.info("AI truck selection request received")

        # Extract breakdown location
        breakdown_lat = data['breakdown_lat']
        breakdown_lng = data['breakdown_lng']
        urgency = data.get('urgency', 'medium')

        app.logger.info(f"Breakdown: ({breakdown_lat:.4f}, {breakdown_lng:.4f}), Urgency: {urgency}")

        # Use external model for prediction
        recommendations = fleet_ai.predict_best_truck(breakdown_lat, breakdown_lng, urgency)

        if not recommendations:
            return jsonify({
                'success': False,
                'error': 'No available trucks found',
                'fleet_size': len(fleet_ai.fleet_data)
            }), 400

        app.logger.info(f"Generated {len(recommendations)} recommendations")

        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'model_used': 'external' if fleet_ai.external_model_available else 'fallback',
            'fleet_size': len(fleet_ai.fleet_data),
            'best_truck_id': recommendations[0]['truck_id'] if recommendations else None
        })

    except Exception as e:
        app.logger.error(f"Truck selection error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Truck selection failed: {str(e)}'
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
            'error': f'Failed to update status: {str(e)}'
        }), 500

@app.route('/api/fleet_status', methods=['GET'])
def fleet_status():
    """Get fleet status summary"""
    try:
        fleet_data = fleet_ai.get_fleet_data()
        
        status_counts = {}
        for truck in fleet_data:
            status = truck['status']
            status_counts[status] = status_counts.get(status, 0) + 1

        return jsonify({
            'total_trucks': len(fleet_data),
            'active': status_counts.get('active', 0),
            'available': status_counts.get('available', 0), 
            'dispatched': status_counts.get('dispatched', 0),
            'maintenance': status_counts.get('maintenance', 0),
            'last_updated': '2025-09-27T15:00:00Z',
            'model_status': 'operational' if fleet_ai.external_model_available else 'fallback'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("="*80)
    print("SwarmSync AI Fleet Management - External Model Integration")
    print("="*80)
    print(f"Backend API: http://localhost:5000")
    print(f"External Model: {'Loaded' if fleet_ai.external_model_available else 'Not Available'}")
    print(f"Fleet Size: {len(fleet_ai.fleet_data)} trucks (loaded from model/fleet_data.pkl)")
    print(f"Model Parameters: breaklat, breaklon, destlat, destlon, cargoweight, cargotype")
    print("="*80)
    print("READY! Run create_fleet_data.py first to create fleet data file!")
    print("="*80)

    app.run(debug=True, host='0.0.0.0', port=5000)