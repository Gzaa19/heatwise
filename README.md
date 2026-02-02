# 🌡️ HeatWise

<p align="center">
  <img src="https://img.shields.io/badge/Next.js-16.1-black?style=for-the-badge&logo=next.js" alt="Next.js">
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/TensorFlow-2.x-FF6F00?style=for-the-badge&logo=tensorflow" alt="TensorFlow">
  <img src="https://img.shields.io/badge/Google_Gemini-AI-4285F4?style=for-the-badge&logo=google" alt="Gemini AI">
</p>

**HeatWise** adalah platform analisis Urban Heat Island (UHI) dan kualitas udara berbasis AI yang membantu perencana kota dan masyarakat memahami serta mengatasi masalah panas urban dan polusi udara.

## ✨ Fitur Utama

- 🗺️ **Interactive Heat Map** - Peta interaktif untuk melihat data suhu dan kualitas udara secara real-time
- 📊 **Comprehensive Analysis** - Analisis lengkap berdasarkan standar WHO, EPA, dan Singapore Green City
- 🤖 **AI-Powered Recommendations** - Rekomendasi mitigasi panas urban menggunakan Google Gemini AI
- 🌳 **Tree Planting Guide** - Panduan penanaman pohon dengan spesies lokal Indonesia
- 💬 **WISE AI Chatbot** - Asisten AI untuk konsultasi lingkungan dan perencanaan kota
- 📈 **AQI Prediction** - Prediksi Air Quality Index menggunakan model Machine Learning

## 🏗️ Arsitektur

```
HeatWise/
├── frontend/          # Next.js 16 + React 19 + TypeScript
│   ├── src/
│   │   ├── app/       # App Router pages
│   │   ├── components/# React components
│   │   └── lib/       # Utilities
│   └── public/        # Static assets
│
└── ml_service/        # FastAPI + TensorFlow Python Backend
    ├── app/
    │   ├── controllers/   # API endpoints
    │   ├── services/      # Business logic & external APIs
    │   └── schemas.py     # Pydantic models
    ├── artifacts/         # ML model artifacts
    └── train_model.py     # Model training script
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ dan npm/yarn/pnpm
- **Python** 3.10+
- **API Keys**:
  - [OpenWeatherMap API Key](https://openweathermap.org/api)
  - [Google Gemini API Key](https://makersuite.google.com/app/apikey)
  - [Agromonitoring API Key](https://agromonitoring.com/api)

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/HeatWise.git
cd HeatWise
```

### 2. Setup ML Service (Backend)

```bash
cd ml_service

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your API keys
```

**.env file:**
```env
OPENWEATHER_API_KEY=your_openweather_api_key
GOOGLE_API_KEY=your_google_gemini_api_key
AGROMONITORING_API_KEY=your_agromonitoring_api_key
```

```bash
# Train the ML model (optional - for AQI prediction)
python train_model.py

# Run the backend server
uvicorn app.main:app --reload --port 8000
```

Backend akan berjalan di `http://localhost:8000`

### 3. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install
# atau
pnpm install

# Run development server
npm run dev
# atau
pnpm dev
```

Frontend akan berjalan di `http://localhost:3000`

## 📚 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/weather/current` | GET | Get current weather data |
| `/api/weather/air-pollution` | GET | Get air pollution data |
| `/api/weather/complete` | GET | Get complete weather + pollution data |
| `/api/analysis/comprehensive` | GET | Get comprehensive location analysis |
| `/api/analysis/generate` | POST | Generate AI-powered analysis |
| `/api/geocoding/reverse` | GET | Reverse geocoding (coords to address) |
| `/api/chatbot/chat` | POST | Chat with WISE AI assistant |

📖 Full API documentation available at `http://localhost:8000/docs`

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 16 (App Router)
- **UI Library**: React 19
- **Styling**: Tailwind CSS 4
- **Components**: Shadcn/ui (Radix UI)
- **Maps**: Leaflet + React Leaflet
- **Charts**: Recharts
- **State**: Zustand
- **Language**: TypeScript

### Backend
- **Framework**: FastAPI
- **ML**: TensorFlow, Scikit-learn
- **AI**: Google Gemini API
- **Weather Data**: OpenWeatherMap API
- **Soil Data**: Agromonitoring API
- **Language**: Python 3.10+

## 🌍 Data Sources

- **Weather & Air Quality**: [OpenWeatherMap API](https://openweathermap.org/api)
- **Soil & Agriculture**: [Agromonitoring API](https://agromonitoring.com/)
- **AI Analysis**: [Google Gemini](https://ai.google.dev/)

## 📊 Standards & Guidelines

HeatWise menggunakan standar internasional untuk analisis:

- **WHO Air Quality Guidelines** - Panduan kualitas udara
- **EPA Heat Index** - Indeks panas dan risiko kesehatan
- **Singapore Green City Standards** - Target tutupan hijau 25-30%
- **European Environment Agency** - Target ruang terbuka hijau

## 🌳 Supported Tree Species

Database pohon lokal Indonesia untuk rekomendasi penanaman:

| Nama | Efek Pendinginan | Ukuran Kanopi |
|------|------------------|---------------|
| Trembesi (Samanea saman) | Sangat Tinggi | Sangat Besar |
| Beringin (Ficus benjamina) | Sangat Tinggi | Sangat Besar |
| Angsana (Pterocarpus indicus) | Sangat Tinggi | Besar |
| Mahoni (Swietenia macrophylla) | Tinggi | Besar |
| Flamboyan (Delonix regia) | Tinggi | Besar |
| Ketapang (Terminalia catappa) | Tinggi | Besar |

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting a PR.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

<p align="center">
  Made with ❤️ for a cooler, greener Indonesia 🇮🇩
</p>
