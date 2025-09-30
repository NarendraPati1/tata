# 🚛 SwarmSync AI Fleet Management

An AI-powered fleet management system for logistics that uses machine learning to optimize truck dispatch and emergency response.

## 📋 Overview

SwarmSync is a full-stack fleet management application that leverages Random Forest machine learning to intelligently dispatch trucks in emergency breakdown situations. The system provides real-time tracking, route optimization, and AI-powered truck recommendations.

## 🛠️ Technologies & Libraries

### Frontend
- **Vite** - Fast build tool and dev server
- **React** (18.x) - UI library
- **TypeScript** - Type-safe JavaScript
- **shadcn/ui** - High-quality React components
- **Tailwind CSS** - Utility-first CSS framework
- **Leaflet.js** (1.9.4) - Interactive maps
- **React Leaflet** - React components for Leaflet
- **Lucide React** - Icon library

### Backend (Python)
- **Flask** (2.x) - Web framework
- **Flask-CORS** - Cross-Origin Resource Sharing support
- **NumPy** - Numerical computing
- **Pandas** - Data manipulation and analysis
- **Scikit-learn** - Machine learning (Random Forest model)
- **Pickle** - Model and data serialization

### External APIs
- **OpenRouteService API** - Real-world routing and directions
- **OpenStreetMap** - Map tiles

## 📦 Installation

### Prerequisites
- **Node.js** 18+ and npm/pnpm/yarn/bun
- **Python** 3.7+
- OpenRouteService API key (free at https://openrouteservice.org/)

### Backend Setup

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Install Python dependencies**
```bash
pip install flask flask-cors numpy pandas scikit-learn
```

3. **Generate fleet data and train model**
```bash
python create_fleet_data.py
```

4. **Start Flask backend**
```bash
python backend.py
```
Backend runs on `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install Node dependencies**
```bash
npm install
# or
pnpm install
# or
yarn install
# or
bun install
```

3. **Set up environment variables**

Create `.env` file in frontend directory:
```env
VITE_API_BASE_URL=http://localhost:5000
VITE_ORS_API_KEY=your_openrouteservice_key
```

4. **Start development server**
```bash
npm run dev
```
Frontend runs on `http://localhost:5173`

## 🚀 Running the Application

### Development Mode

**Terminal 1 - Backend:**
```bash
cd backend
python backend.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Then open `http://localhost:5173` in your browser.

## 🗂️ Project Structure

```
CODEBASE/
├── backend/
│   ├── model/
│   │   ├── fleet_data.pkl      # Fleet truck data
│   │   ├── rf_model.pkl        # Trained Random Forest model
│   │   ├── le_y.pkl            # Label encoder for truck IDs
│   │   └── le_cargo.pkl        # Label encoder for cargo types
│   ├── static/                 # Static assets
│   ├── templates/              # HTML templates
│   ├── backend.py              # Flask server
│   └── requirements.txt        # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   │   └── ui/            # shadcn/ui components
│   │   ├── lib/               # Utility functions
│   │   ├── hooks/             # Custom React hooks
│   │   ├── types/             # TypeScript types
│   │   ├── App.tsx            # Main app
│   │   └── main.tsx           # Entry point
│   ├── public/                # Static assets
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── tsconfig.json
│
└── README.md
```

## 🎯 Features

- Real-time Fleet Tracking on interactive map
- AI-Powered Dispatch using ML model
- Emergency Response with breakdown reporting
- Route Optimization using OpenRouteService
- Animated truck movement along routes
- Live Fleet Statistics dashboard
- Dark mode support

## 📝 Usage Guide

1. **View Fleet** - All trucks displayed on map with status
2. **Report Breakdown** - Click map location to set breakdown point
3. **Fill Details** - Enter issue type and urgency level
4. **Get Recommendations** - AI analyzes and ranks available trucks
5. **Dispatch Truck** - Select and dispatch optimal truck
6. **Track Route** - Watch real-time animated route

## 🔧 API Endpoints

### `GET /api/health`
System health check

### `GET /api/fleet_data`
Retrieve all fleet truck data

### `POST /api/find_best_truck`
Get ML-powered truck recommendations
```json
{
  "breakdown_lat": 18.5204,
  "breakdown_lng": 73.8567,
  "urgency": "high"
}
```

### `POST /api/update_truck_status`
Update truck status
```json
{
  "truck_id": "T0",
  "status": "dispatched"
}
```

### `GET /api/fleet_status`
Get fleet statistics summary

## 📊 ML Model

The Random Forest classifier uses 6 parameters:
- `breaklat` - Breakdown latitude
- `breaklon` - Breakdown longitude
- `destlat` - Destination latitude
- `destlon` - Destination longitude
- `cargoweight` - Cargo weight
- `cargotype` - Cargo type (encoded)

---

**Built with modern web technologies for intelligent fleet management**
