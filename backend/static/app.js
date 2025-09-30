/**
 * SwarmSync AI Fleet Management - Model Integration
 * All fleet data and processing handled by backend
 */

class AIFleetManager {
    constructor() {
        // Backend configuration
        this.BACKEND_URL = 'http://localhost:5000';
        this.apiKeyReady = false;

        // Map and routing variables
        this.map = null;
        this.rescueRoute = null;
        this.rescueMarker = null;
        this.rescueAnimationTimer = null;

        // Breakdown and ML variables
        this.breakdownMarker = null;
        this.breakdownLocation = null;
        this.selectedTruck = null;

        // Fleet management - data from backend
        this.truckMarkers = {}; // Initialize as empty object
        this.customTruckIcon = null;
        this.fleetData = []; // Will be populated from backend

        this.init();
    }

    async init() {
        console.log('🚛 Initializing SwarmSync AI Fleet Manager...');

        // Initialize map
        this.initMap();

        // Create custom truck icon
        this.createCustomTruckIcon();

        // Load fleet data from backend
        await this.loadFleetDataFromBackend();

        // Load trucks on map
        this.loadTrucks();

        // Update UI
        this.updateFleetStats();
        this.updateVehicleList();

        // Test backend connectivity
        await this.testBackendConnection();

        // Set up event listeners
        this.setupEventListeners();

        console.log('✅ Fleet Manager initialized successfully with backend integration!');
    }

    async loadFleetDataFromBackend() {
        try {
            console.log('📡 Loading fleet data from backend...');

            const response = await fetch(this.BACKEND_URL + '/api/fleet_data');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();

            if (data.success) {
                this.fleetData = data.fleet_data;
                console.log(`✅ Loaded ${data.total_trucks} trucks from backend`);
            } else {
                throw new Error(data.error || 'Failed to load fleet data');
            }

        } catch (error) {
            console.error('❌ Failed to load fleet data from backend:', error);
            this.showNotification('Failed to load fleet data. Using offline mode.', 'error');
            
            // Fallback minimal data for offline mode
            this.fleetData = [{
                id: 'T0', driver: 'Offline Mode', lat: 18.5204, lng: 73.8567,
                status: 'available', fuel: 75, type: 'Test Truck', capacity: 5.0, load: 0
            }];
        }
    }

    initMap() {
        // Initialize map centered on Pune
        this.map = L.map('map', {
            center: [18.5204, 73.8567],
            zoom: 12,
            zoomControl: true,
            preferCanvas: true
        });

        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 18,
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);

        // Add map click handler for breakdown reporting
        this.map.on('click', (e) => this.onMapClick(e));

        console.log('🗺️ Map initialized');
    }

    createCustomTruckIcon() {
        this.customTruckIcon = L.divIcon({
            html: `<div style="background: linear-gradient(45deg, #2563eb, #1d4ed8); color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3); font-size: 14px;">🚛</div>`,
            className: 'custom-truck-marker',
            iconSize: [30, 30],
            iconAnchor: [15, 15],
            popupAnchor: [0, -15]
        });
    }

    loadTrucks() {
        // Clear existing markers
        Object.values(this.truckMarkers).forEach(marker => {
            if (this.map.hasLayer(marker)) {
                this.map.removeLayer(marker);
            }
        });
        this.truckMarkers = {};

        // Add truck markers to map
        this.fleetData.forEach(truck => {
            const marker = L.marker([truck.lat, truck.lng], { 
                icon: this.customTruckIcon 
            }).addTo(this.map);

            // Create popup content with truck details
            const popupContent = `
                <div style="font-family: Arial, sans-serif;">
                    <h4 style="margin: 0 0 8px 0; color: #2563eb;">${truck.id}</h4>
                    <p style="margin: 4px 0;"><strong>Driver:</strong> ${truck.driver}</p>
                    <p style="margin: 4px 0;"><strong>Status:</strong> 
                        <span style="background: ${truck.status === 'active' ? '#10b981' : '#06b6d4'}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">
                            ${truck.status.toUpperCase()}
                        </span>
                    </p>
                    <p style="margin: 4px 0;"><strong>Fuel:</strong> ${truck.fuel}%</p>
                    <p style="margin: 4px 0;"><strong>Load:</strong> ${truck.load}/${truck.capacity} tons</p>
                    <p style="margin: 4px 0;"><strong>Type:</strong> ${truck.type}</p>
                </div>
            `;

            marker.bindPopup(popupContent);
            marker.truckData = truck;
            this.truckMarkers[truck.id] = marker;
        });

        console.log(`🚛 Loaded ${this.fleetData.length} trucks on map`);
    }

    updateFleetStats() {
        const activeCount = this.fleetData.filter(t => t.status === 'active').length;
        const availableCount = this.fleetData.filter(t => t.status === 'available').length;

        const activeEl = document.getElementById('activeCount');
        const availableEl = document.getElementById('availableCount');

        if (activeEl) activeEl.textContent = activeCount;
        if (availableEl) availableEl.textContent = availableCount;
    }

    updateVehicleList() {
        const vehicleList = document.getElementById('vehicleList');
        if (!vehicleList) return;

        vehicleList.innerHTML = '';

        this.fleetData.forEach(truck => {
            const vehicleItem = document.createElement('div');
            vehicleItem.className = `vehicle-item ${truck.status}`;
            vehicleItem.innerHTML = `
                <div class="vehicle-info">
                    <h4>${truck.id} - ${truck.driver}</h4>
                    <p>Fuel: ${truck.fuel}% | Load: ${truck.load}/${truck.capacity}t | Type: ${truck.type}</p>
                </div>
                <div class="vehicle-status ${truck.status}">${truck.status}</div>
            `;

            vehicleItem.addEventListener('click', () => {
                this.map.setView([truck.lat, truck.lng], 15);
                const marker = this.truckMarkers[truck.id];
                if (marker) marker.openPopup();
            });

            vehicleList.appendChild(vehicleItem);
        });
    }

    async testBackendConnection() {
        try {
            const response = await fetch(this.BACKEND_URL + '/api/health');
            if (response.ok) {
                const data = await response.json();
                console.log('🏥 Backend connection successful:', data);

                const accuracyEl = document.getElementById('modelAccuracy');
                if (accuracyEl) {
                    accuracyEl.textContent = data.external_model_available 
                        ? 'External Model' 
                        : 'Fallback Mode';
                }
            } else {
                console.warn('⚠️ Backend connection failed');
                this.showNotification('Backend not responding - limited functionality', 'warning');
            }
        } catch (error) {
            console.error('❌ Backend connection error:', error);
            this.showNotification('Backend unavailable - offline mode active', 'warning');
        }
    }

    onMapClick(e) {
        const {lat, lng} = e.latlng;

        // Set breakdown location
        this.breakdownLocation = {lat, lng};

        // Remove existing breakdown marker
        if (this.breakdownMarker) {
            this.map.removeLayer(this.breakdownMarker);
        }

        // Add breakdown marker
        this.breakdownMarker = L.marker([lat, lng], {
            icon: L.divIcon({
                html: `<div style="background: #ef4444; color: white; border-radius: 50%; width: 35px; height: 35px; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 3px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.3); font-size: 18px;">⚠️</div>`,
                iconSize: [35, 35],
                iconAnchor: [17, 17]
            })
        }).addTo(this.map);

        this.breakdownMarker.bindPopup('🚨 Breakdown Location').openPopup();

        // Update UI
        this.updateBreakdownPanel(lat, lng);

        // Open breakdown modal
        this.openBreakdownModal();

        console.log(`🚨 Breakdown location set: ${lat.toFixed(4)}, ${lng.toFixed(4)}`);
    }

    updateBreakdownPanel(lat, lng) {
        const panel = document.getElementById('breakdownPanel');
        if (panel) {
            panel.innerHTML = `
                <div style="text-align: center; color: #ef4444; font-weight: bold;">🚨 BREAKDOWN REPORTED</div>
                <div style="font-size: 0.875rem; margin-top: 0.5rem; text-align: center;">
                    ${lat.toFixed(4)}, ${lng.toFixed(4)}
                </div>
                <button class="btn btn-danger" onclick="window.fleetManager.openBreakdownModal()" style="width: 100%; margin-top: 1rem;">
                    Report Details
                </button>
            `;
        }
    }

    openBreakdownModal() {
        const modal = document.getElementById('breakdownModal');
        const locationDisplay = document.getElementById('locationDisplay');

        if (this.breakdownLocation) {
            locationDisplay.textContent = `${this.breakdownLocation.lat.toFixed(4)}, ${this.breakdownLocation.lng.toFixed(4)}`;
            locationDisplay.classList.add('selected');
        }

        modal.classList.add('show');
    }

    closeBreakdownModal() {
        document.getElementById('breakdownModal').classList.remove('show');
    }

    async findBestTruck() {
        if (!this.breakdownLocation) {
            alert('Please select a breakdown location on the map first');
            return;
        }

        const form = document.getElementById('breakdownForm');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const urgencyLevel = document.getElementById('urgencyLevel').value;
        const issueType = document.getElementById('issueType').value;

        console.log('🤖 Finding best truck using backend AI...');

        try {
            // Call backend AI for truck selection
            const response = await fetch(this.BACKEND_URL + '/api/find_best_truck', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    breakdown_lat: this.breakdownLocation.lat,
                    breakdown_lng: this.breakdownLocation.lng,
                    urgency: urgencyLevel,
                    issue_type: issueType
                })
            });

            if (response.ok) {
                const results = await response.json();
                this.displayMLResults(results.recommendations);
                this.closeBreakdownModal();
                this.openMlResultsModal();
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Backend processing failed');
            }

        } catch (error) {
            console.error('❌ AI Error:', error);
            this.showNotification(`AI processing failed: ${error.message}`, 'error');
        }
    }

    displayMLResults(results) {
        const container = document.getElementById('mlResults');
        if (!container) return;

        container.innerHTML = '';

        results.forEach((result, index) => {
            const truck = result.truck_data;
            const isBest = index === 0;

            const resultCard = document.createElement('div');
            resultCard.className = `truck-candidate ${isBest ? 'best' : ''}`;
            resultCard.innerHTML = `
                <div class="truck-header">
                    <div class="truck-info">
                        <h5>${truck.id} - ${truck.driver}</h5>
                        <p>${truck.type} | Fuel: ${truck.fuel}% | Load: ${truck.load}/${truck.capacity}t</p>
                    </div>
                    <div class="ml-score">${(result.score * 100).toFixed(1)}%</div>
                </div>
                <div class="truck-details">
                    <div class="detail-item">
                        <span class="detail-value">${result.distance_km.toFixed(1)} km</span>
                        <span class="detail-label">Distance</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-value">${result.eta_minutes} min</span>
                        <span class="detail-label">ETA</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-value">${truck.fuel}%</span>
                        <span class="detail-label">Fuel</span>
                    </div>
                </div>
                ${result.prediction_method === 'external_model' ? '<div style="text-align: center; margin-top: 8px; font-size: 12px; color: #10b981;">✓ AI Model Prediction</div>' : ''}
            `;

            resultCard.addEventListener('click', () => {
                // Remove previous selection
                container.querySelectorAll('.truck-candidate').forEach(c => c.classList.remove('selected'));

                // Select this truck
                resultCard.classList.add('selected');
                this.selectedTruck = {...truck, ...result};

                // Enable dispatch button
                const dispatchBtn = document.getElementById('dispatchBtn');
                if (dispatchBtn) dispatchBtn.disabled = false;
            });

            container.appendChild(resultCard);
        });

        // Auto-select the best truck
        if (results.length > 0) {
            container.firstChild.click();
        }
    }

    openMlResultsModal() {
        document.getElementById('mlResultsModal').classList.add('show');
    }

    closeMlResultsModal() {
        document.getElementById('mlResultsModal').classList.remove('show');
    }

    async dispatchSelectedTruck() {
        if (!this.selectedTruck) return;

        // Check if API key is available for routing
        if (!this.apiKeyReady && !orsApiKey) {
            alert('Please enter your OpenRouteService API key first for routing!');
            return;
        }

        console.log(`🚛 Dispatching truck ${this.selectedTruck.id}...`);

        try {
            // Calculate and show route using OpenRouteService
            await this.calculateAndShowRouteViaBrowser();

            // Update truck status in backend
            await this.updateTruckStatusInBackend(this.selectedTruck.id, 'dispatched');

            // Refresh fleet data from backend
            await this.loadFleetDataFromBackend();
            this.loadTrucks();
            this.updateFleetStats();
            this.updateVehicleList();

            // Show success
            this.showSuccessModal();
            this.closeMlResultsModal();

        } catch (error) {
            console.error('❌ Dispatch error:', error);
            this.showNotification(`Dispatch failed: ${error.message}`, 'error');
        }
    }

    async updateTruckStatusInBackend(truck_id, status) {
        try {
            const response = await fetch(this.BACKEND_URL + '/api/update_truck_status', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    truck_id: truck_id,
                    status: status
                })
            });

            if (response.ok) {
                console.log(`✅ Updated truck ${truck_id} status to ${status} in backend`);
            } else {
                throw new Error('Backend status update failed');
            }

        } catch (error) {
            console.error('❌ Failed to update truck status in backend:', error);
        }
    }

    // OpenRouteService routing - direct browser call
    async calculateAndShowRouteViaBrowser() {
        if (!this.selectedTruck || !this.breakdownLocation) return;

        const truck = this.selectedTruck;

        console.log('🛣️ Calling OpenRouteService directly from browser...');

        // Payload for OpenRouteService
        const payload = {
            coordinates: [[truck.lng, truck.lat], [this.breakdownLocation.lng, this.breakdownLocation.lat]],
            profile: "driving-car",
            format: "geojson"
        };

        try {
            // Direct call to OpenRouteService
            const response = await fetch('https://api.openrouteservice.org/v2/directions/driving-car/geojson', {
                method: 'POST',
                headers: {
                    'Authorization': orsApiKey,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`OpenRouteService API error: ${response.status}`);
            }

            const data = await response.json();

            if (data.features && data.features[0] && data.features[0].geometry) {
                // Convert coordinates from [lng, lat] to [lat, lng] for Leaflet
                const coordinates = data.features[0].geometry.coordinates.map(c => [c[1], c[0]]);
                const summary = data.features[0].properties.summary;

                console.log(`🛣️ OpenRouteService returned route with ${coordinates.length} points`);

                // Create route data object
                const routeData = {
                    coordinates: coordinates,
                    distance_km: summary.distance / 1000,
                    duration_minutes: summary.duration / 60
                };

                // Draw route on map
                this.drawRouteOnMap(routeData);

                // Start truck animation along actual path
                this.animateTruckToBreakdown(routeData);

                console.log('✅ Real route calculated and displayed');
            } else {
                throw new Error('Invalid response format from OpenRouteService');
            }

        } catch (error) {
            console.error('❌ OpenRouteService routing error:', error);
            this.showNotification(`Routing failed: ${error.message}`, 'error');

            // Fallback to straight line if routing fails
            this.drawStraightLineRoute();
        }
    }

    drawRouteOnMap(routeData) {
        // Remove existing route
        if (this.rescueRoute) {
            this.map.removeLayer(this.rescueRoute);
        }

        // Draw new route
        const coordinates = routeData.coordinates;
        console.log(`🗺️ Drawing route with ${coordinates.length} coordinate points`);

        this.rescueRoute = L.polyline(coordinates, {
            color: '#10b981',
            weight: 4,
            opacity: 0.8,
            dashArray: '5, 10'
        }).addTo(this.map);

        // Fit map to show route
        const group = new L.featureGroup([this.rescueRoute, this.breakdownMarker]);
        this.map.fitBounds(group.getBounds().pad(0.1));
    }

    drawStraightLineRoute() {
        // Fallback: draw straight line
        console.warn('⚠️ Using fallback straight line route');

        const coordinates = [
            [this.selectedTruck.lat, this.selectedTruck.lng],
            [this.breakdownLocation.lat, this.breakdownLocation.lng]
        ];

        this.drawRouteOnMap({coordinates});
    }

    animateTruckToBreakdown(routeData) {
        if (!routeData || !routeData.coordinates) return;

        const coordinates = routeData.coordinates;
        const truckMarker = this.truckMarkers[this.selectedTruck.id];

        if (!truckMarker) return;

        let currentIndex = 0;
        const totalPoints = coordinates.length;
        const animationSpeed = 200; // ms per move

        console.log(`🚛 Starting truck animation along ${totalPoints} route points`);

        this.rescueAnimationTimer = setInterval(() => {
            currentIndex++;

            if (currentIndex >= totalPoints) {
                clearInterval(this.rescueAnimationTimer);
                truckMarker.bindPopup('🚛 Truck Arrived at Breakdown Location!').openPopup();
                console.log('✅ Truck animation completed');
                return;
            }

            // Move truck marker along actual route path
            truckMarker.setLatLng(coordinates[currentIndex]);

            // Update remaining route
            const remainingCoords = coordinates.slice(currentIndex);
            if (this.rescueRoute) {
                this.rescueRoute.setLatLngs(remainingCoords);
            }

        }, animationSpeed);
    }

    showSuccessModal() {
        document.getElementById('successTruckId').textContent = `Truck ${this.selectedTruck.id}`;

        const details = document.getElementById('successDetails');
        details.innerHTML = `
            <div class="detail-item">
                <span class="detail-value">${this.selectedTruck.driver}</span>
                <span class="detail-label">Driver</span>
            </div>
            <div class="detail-item">
                <span class="detail-value">${this.selectedTruck.distance_km.toFixed(1)} km</span>
                <span class="detail-label">Distance</span>
            </div>
            <div class="detail-item">
                <span class="detail-value">${this.selectedTruck.eta_minutes} min</span>
                <span class="detail-label">ETA</span>
            </div>
        `;

        document.getElementById('successModal').classList.add('show');
    }

    closeSuccessModal() {
        document.getElementById('successModal').classList.remove('show');
    }

    // Utility functions
    calculateDistance(lat1, lng1, lat2, lng2) {
        const R = 6371; // Earth's radius in km
        const dLat = this.toRad(lat2 - lat1);
        const dLng = this.toRad(lng2 - lng1);
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                  Math.cos(this.toRad(lat1)) * Math.cos(this.toRad(lat2)) *
                  Math.sin(dLng/2) * Math.sin(dLng/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }

    toRad(value) {
        return value * Math.PI / 180;
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed; top: 20px; right: 20px; padding: 12px 20px;
            border-radius: 6px; color: white; font-weight: 500; z-index: 10000;
            max-width: 300px; animation: slideIn 0.3s ease;
            background: ${type === 'error' ? '#ef4444' : type === 'warning' ? '#f59e0b' : '#06b6d4'}
        `;
        notification.textContent = message;

        document.body.appendChild(notification);

        // Remove after 5 seconds
        setTimeout(() => notification.remove(), 5000);
    }

    setupEventListeners() {
        // Modal close handlers
        window.closeBreakdownModal = () => this.closeBreakdownModal();
        window.closeMlResultsModal = () => this.closeMlResultsModal();
        window.closeSuccessModal = () => this.closeSuccessModal();
        window.closeHelpModal = () => document.getElementById('helpModal').classList.remove('show');

        // Button handlers
        window.findBestTruck = () => this.findBestTruck();
        window.dispatchSelectedTruck = () => this.dispatchSelectedTruck();

        // Utility handlers
        window.centerMap = () => this.map.setView([18.5204, 73.8567], 12);
        window.clearAllRoutes = () => this.clearAllRoutes();
        window.resetSystem = () => this.resetSystem();
        window.showHelp = () => document.getElementById('helpModal').classList.add('show');
        window.toggleSidebar = () => document.getElementById('sidebar').classList.toggle('open');
    }

    clearAllRoutes() {
        if (this.rescueRoute) {
            this.map.removeLayer(this.rescueRoute);
            this.rescueRoute = null;
        }

        if (this.rescueAnimationTimer) {
            clearInterval(this.rescueAnimationTimer);
            this.rescueAnimationTimer = null;
        }

        this.showNotification('All routes cleared', 'info');
    }

    async resetSystem() {
        // Clear routes and markers
        this.clearAllRoutes();

        if (this.breakdownMarker) {
            this.map.removeLayer(this.breakdownMarker);
            this.breakdownMarker = null;
        }

        // Refresh fleet data from backend
        await this.loadFleetDataFromBackend();

        // Reset variables
        this.breakdownLocation = null;
        this.selectedTruck = null;

        // Update UI
        this.loadTrucks();
        this.updateFleetStats();
        this.updateVehicleList();

        // Reset breakdown panel
        const panel = document.getElementById('breakdownPanel');
        if (panel) {
            panel.innerHTML = `
                <div class="instruction-text">
                    Click on the map to report a truck breakdown and get AI-powered rescue recommendations
                </div>
            `;
        }

        this.showNotification('System reset successfully', 'info');
    }
}

// Export for global use
window.AIFleetManager = AIFleetManager