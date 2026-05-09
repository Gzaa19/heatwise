# HeatWise — Smart City AI for Urban Heat Mitigation

<p align="center">
  <img src="https://img.shields.io/badge/Next.js-16.1.6-000?style=for-the-badge&logo=next.js" alt="Next.js">
  <img src="https://img.shields.io/badge/React-19.2-61DAFB?style=for-the-badge&logo=react&logoColor=000" alt="React">
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/TensorFlow-2.x-FF6F00?style=for-the-badge&logo=tensorflow" alt="TensorFlow">
  <img src="https://img.shields.io/badge/Gemini_AI-Powered-4285F4?style=for-the-badge&logo=google" alt="Gemini AI">
  <img src="https://img.shields.io/badge/Tailwind_CSS-4.0-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white" alt="Tailwind">
</p>

<p align="center">
  <strong>AI-powered urban heat analysis platform for Indonesian cities.</strong><br>
  Monitor Urban Heat Islands, get real-time environmental data, and receive AI-driven mitigation strategies.
</p>

---

## Features

| Feature | Description |
|---|---|
| **Interactive Heat Map** | Leaflet-based map with click-to-analyze — get weather, air quality, and soil data for any coordinate |
| **Comprehensive Location Analysis** | Weather, air pollution (AQI), soil moisture, and health recommendations based on WHO/EPA standards |
| **AI-Powered Green Analysis** | Google Gemini generates tree planting plans, infrastructure development timelines, and expected benefits |
| **WISE-AI Chatbot** | Conversational AI assistant for urban heat and environmental planning queries (Markdown-rendered) |
| **AQI Prediction** | TensorFlow ML model predicts Air Quality Index from environmental sensor data |
| **Reverse Geocoding** | OpenCage integration for coordinate-to-address resolution |

## Architecture

```
HeatWise/
├── frontend/                   # Next.js 16 + React 19 + TypeScript
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx                # Root → redirects to /heatmap
│   │   │   ├── layout.tsx              # Root layout (Geist font, MainLayout)
│   │   │   ├── heatmap/
│   │   │   │   ├── page.tsx            # Heat Map page
│   │   │   │   └── analysis/page.tsx   # Location analysis (weather, AQI, AI)
│   │   │   └── chat/page.tsx           # WISE-AI Chatbot page
│   │   ├── components/
│   │   │   ├── HeatMap.tsx             # Map wrapper with controls & legend
│   │   │   ├── WISEAIChatbot.tsx       # Chat UI with Markdown rendering
│   │   │   ├── layout/
│   │   │   │   ├── MainLayout.tsx      # App shell (sidebar + topbar + content)
│   │   │   │   ├── Sidebar.tsx         # Navigation sidebar
│   │   │   │   └── Topbar.tsx          # Top bar with search & profile
│   │   │   ├── leaflet/
│   │   │   │   ├── BasicMap.tsx        # Leaflet MapContainer wrapper
│   │   │   │   ├── ClickToAnalyze.tsx  # Click-to-pin + popup with analysis link
│   │   │   │   ├── CurrentLocation.tsx # Geolocation button
│   │   │   │   └── osm-providers.ts   # Tile provider configs
│   │   │   └── ui/                     # Shadcn/ui components (button, card, etc.)
│   │   ├── hooks/
│   │   │   └── useGeoLocation.ts       # Browser geolocation hook
│   │   └── lib/utils.ts                # Tailwind merge utility
│   └── package.json
│
└── ml_service/                 # FastAPI + TensorFlow Python Backend
    ├── app/
    │   ├── main.py                     # FastAPI app, CORS, lifespan, routers
    │   ├── schemas.py                  # Pydantic request/response models
    │   ├── controllers/
    │   │   ├── weather.py              # /api/weather/* endpoints
    │   │   ├── geocoding.py            # /api/geocode/* endpoints
    │   │   ├── analysis.py             # /api/analysis/* endpoints
    │   │   └── chatbot.py              # /api/chat/* endpoints
    │   └── services/
    │       ├── weather.py              # OpenWeatherMap API client
    │       ├── geocoding.py            # OpenCage geocoding client
    │       ├── agromonitoring.py       # Soil data API client
    │       ├── gemini.py               # Google Gemini AI (chat + analysis)
    │       └── predictor.py            # TensorFlow AQI prediction model
    ├── artifacts/
    │   ├── heat_wise_model.keras       # Trained ML model
    │   └── scaler_params.json          # Feature scaler parameters
    ├── train_model.py                  # Model training script
    ├── requirements.txt
    └── .env                            # API keys (not committed)
```

## Quick Start

### Prerequisites

- **Node.js** 18+
- **Python** 3.9+
- **API Keys** (see [Environment Variables](#environment-variables))

### 1. Clone & Setup Backend

```bash
git clone https://github.com/Gzaa19/heatwise.git
cd HeatWise/ml_service

# Create virtual environment
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys (see below)

# (Optional) Train the AQI prediction model
python train_model.py

# Start backend
uvicorn app.main:app --reload --port 8000
```

### 2. Setup Frontend

```bash
cd HeatWise/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 3. Open the App

- **Frontend**: http://localhost:3000 (auto-redirects to `/heatmap`)
- **Backend API Docs**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

## Environment Variables

Create `ml_service/.env` with the following keys:

```env
OPENWEATHER_API_KEY=your_openweather_api_key
GOOGLE_API_KEY=your_google_gemini_api_key
AGROMONITORING_API_KEY=your_agromonitoring_api_key
OPENCAGE_API_KEY=your_opencage_api_key
```

| Key | Source | Used For |
|-----|--------|----------|
| `OPENWEATHER_API_KEY` | [openweathermap.org](https://openweathermap.org/api) | Weather data & air pollution |
| `GOOGLE_API_KEY` | [ai.google.dev](https://ai.google.dev/) | Gemini AI (chatbot + analysis) |
| `AGROMONITORING_API_KEY` | [agromonitoring.com](https://agromonitoring.com/) | Soil moisture & temperature |
| `OPENCAGE_API_KEY` | [opencagedata.com](https://opencagedata.com/) | Reverse geocoding |

## API Endpoints

### Weather & Environment
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/weather/current` | `GET` | Current weather by coordinates |
| `/api/weather/air-pollution` | `GET` | Air pollution data (AQI, CO, NO₂, PM2.5, etc.) |
| `/api/weather/complete` | `GET` | Combined weather + pollution data |
| `/api/weather/city/{city_name}` | `GET` | Weather by city name |

### Geocoding
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/geocode/reverse` | `GET` | Coordinates → place name & address |

### Location Analysis
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/analysis/location` | `GET` | Full location analysis (weather + AQI + soil + health) |
| `/api/analysis/generate` | `POST` | AI-generated mitigation plan (tree planting, infrastructure) |

### AI Chatbot
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat/message` | `POST` | Send message to WISE-AI assistant |

### Prediction
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/predict` | `POST` | Predict AQI from environmental sensor data |
| `/predict/weather` | `POST` | Predict AQI from weather + air pollution data |

## Tech Stack

### Frontend
| Technology | Version | Purpose |
|-----------|---------|---------|
| Next.js | 16.1.6 | React framework (App Router) |
| React | 19.2 | UI library |
| TypeScript | 5.x | Type safety |
| Tailwind CSS | 4.0 | Styling |
| Shadcn/ui (Radix) | Latest | UI component library |
| Leaflet + React Leaflet | 1.9 / 5.0 | Interactive maps |
| react-markdown | 10.1 | Markdown rendering (chatbot) |
| Zustand | 5.0 | State management |
| Lucide React | 0.563 | Icon library |
| Geist | — | Typography (Sans + Mono) |

### Backend
| Technology | Version | Purpose |
|-----------|---------|---------|
| FastAPI | Latest | Python web framework |
| TensorFlow / Keras | 2.x | AQI prediction model |
| Google GenAI | Latest | Gemini AI integration |
| scikit-learn | Latest | Feature scaling |
| httpx | Latest | Async HTTP client |
| Pydantic | Latest | Data validation |
| uvicorn | Latest | ASGI server |

## Analysis & Standards

The location analysis page provides data assessed against international standards:

- **WHO Air Quality Guidelines** — Air pollution health implications
- **EPA Heat Index** — Heat stress risk levels  
- **Singapore Green City** — Target green canopy coverage (25–30%)
- **European Environment Agency** — Urban green space recommendations

### AI Analysis Output Includes:
- Current vs. target green canopy coverage
- UHI intensity assessment
- Tree planting plan with native Indonesian species (Trembesi, Mahoni, Angsana, etc.)
- Short/medium/long-term infrastructure development plans
- Estimated temperature reduction, AQI improvement, and carbon sequestration

## Native Tree Species Database

| Species | Cooling Effect | Growth Rate |
|---------|---------------|-------------|
| Trembesi (Samanea saman) | Very High | Fast |
| Beringin (Ficus benjamina) | Very High | Medium |
| Angsana (Pterocarpus indicus) | High | Fast |
| Mahoni (Swietenia macrophylla) | High | Medium |
| Flamboyan (Delonix regia) | High | Fast |
| Ketapang (Terminalia catappa) | High | Fast |
| Tanjung (Mimusops elengi) | Medium | Slow |

## License

MIT License — see [LICENSE](LICENSE) for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

<p align="center">
  Made for a cooler, greener Indonesia.
</p>