# ScamTrap - AI Honeypot for Scam Detection

## 🚀 Live API

**Base URL:** `https://scamtrap-hackathon.onrender.com`

## 📡 Endpoints

### Health Check
```
GET /health
```

### Scam Detection & Engagement
```
POST /handover
```

**Request Body:**
```json
{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "Your account is blocked!",
    "timestamp": "2024-01-21T10:15:30Z"
  },
  "conversationHistory": []
}
```

**Response:**
```json
{
  "status": "success",
  "scamDetected": true,
  "reply": "oh no really",
  "riskScore": 85,
  "extractedIntelligence": { ... }
}
```

## 🏗️ Architecture

- **6 Specialized AI Agents**
- **Multi-turn conversation handling**
- **10+ intelligence extraction types**
- **Risk scoring (0-100)**
- **GUVI integration ready**

## 🛠️ Tech Stack

- FastAPI
- Google Gemini AI
- Python 3.11
- Render.com (hosting)

## 📊 Features

✅ Human-like conversation with anti-AI patterns
✅ Scam type classification (9+ types)
✅ Real-time intelligence extraction
✅ Risk assessment
✅ Session memory management

## 🔧 Local Development
```bash
pip install -r scamtrap-backend/requirements.txt
cd scamtrap-backend
uvicorn app.main:app --reload
```

## 📝 License

MIT License