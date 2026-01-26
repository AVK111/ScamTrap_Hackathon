# 🏗️ ScamTrap AI - System Architecture

## 📐 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Interface                      │
│                     (React Frontend)                        │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway                             │
│                   (FastAPI/Express)                         │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                  Agent Orchestration Layer                  │
│                      (LangGraph)                            │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Persona  │  │Convers-  │  │Strategy  │  │Extraction│  │
│  │  Agent   │  │ation     │  │  Agent   │  │  Agent   │  │
│  │          │  │Agent     │  │          │  │          │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                             │
│  ┌──────────┐  ┌──────────┐                               │
│  │   Risk   │  │Leaderboard│                              │
│  │  Agent   │  │  Agent   │                               │
│  └──────────┘  └──────────┘                               │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   MongoDB    │  │    Redis     │  │  Vector DB   │    │
│  │(Leaderboard) │  │   (Cache)    │  │ (Embeddings) │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## 🤖 Agent System Design

### 1. Persona Agent
**Responsibility**: Generate believable victim profiles

**Input**: Scam message text

**Process**:
1. Classify scam type (Bank/Job/Lottery/Crypto)
2. Select appropriate demographic template
3. Generate fake identity:
   - Name (region-appropriate)
   - Age (scam-type appropriate)
   - Occupation
   - Location
   - Tech literacy level
   - Bank type

**Output**: Persona object

**Example**:
```javascript
{
  name: "Ramesh Kumar",
  age: 58,
  job: "Retired Teacher",
  city: "Pune",
  bank: "State Bank of India",
  techLevel: "Low",
  avatar: "👴"
}
```

---

### 2. Conversation Agent
**Responsibility**: Generate human-like responses

**Input**: 
- Scammer message
- Persona context
- Conversation history

**Process**:
1. Understand scammer's intent
2. Generate response matching persona
3. Add human elements:
   - Typos (for low tech personas)
   - Hesitation ("wait...", "hmm...")
   - Questions
   - Emotional reactions

**Output**: AI response text

**Techniques**:
- Few-shot prompting with persona examples
- Temperature control for varied responses
- Context window of last 5 messages

---

### 3. Strategy Agent
**Responsibility**: Control conversation flow

**Input**: 
- Current conversation state
- Scammer pressure tactics
- Time elapsed

**Strategies**:
1. **Delay Tactics**
   - "Let me find my card..."
   - "My son usually helps..."
   - "Wait, phone ringing..."

2. **Partial Compliance**
   - Give some info, ask for clarification
   - Show willingness but create obstacles

3. **Emotional Manipulation (Reverse)**
   - Excitement (lottery)
   - Fear (bank)
   - Desperation (job)

4. **Exit Conditions**
   - Scammer loses patience
   - Risk threshold exceeded
   - Maximum time reached

**Output**: Conversation directive

---

### 4. Extraction Agent
**Responsibility**: Extract fraud intelligence

**Input**: All scammer messages

**Methods**:

**Regex Patterns**:
```javascript
// UPI IDs
/[\w.-]+@[\w.-]+/g

// Indian Phone Numbers
/(\+91|91)?[\s-]?[6-9]\d{9}/g

// URLs
/(https?:\/\/[^\s]+)/g

// Bank Account Numbers
/\b\d{9,18}\b/g

// IFSC Codes
/^[A-Z]{4}0[A-Z0-9]{6}$/
```

**NLP Analysis**:
- Entity recognition for bank names
- Payment instruction detection
- Threat/urgency keyword tracking

**Output**: Structured intelligence
```javascript
{
  upiIds: ["scammer@paytm", "fraud@gpay"],
  phoneNumbers: ["+919876543210"],
  urls: ["http://phishing-site.com"],
  bankAccounts: ["1234567890"],
  ifscCodes: ["SBIN0001234"],
  paymentInstructions: [...],
  urgencyScore: 8.5
}
```

---

### 5. Risk Agent
**Responsibility**: Safety and termination

**Monitors**:
1. **Real Data Leakage**
   - Never share real OTP
   - Never share real bank details
   - Never click malicious links

2. **Dangerous Escalation**
   - Physical threats
   - Request for video call
   - Meeting requests

3. **System Abuse**
   - Repeated failed attempts
   - Non-scam conversations
   - Resource exhaustion

**Actions**:
- `CONTINUE` - Safe to proceed
- `WARN` - Approaching threshold
- `TERMINATE` - End conversation immediately
- `BLOCK` - Add to permanent blocklist

**Output**: Risk assessment + action

---

### 6. Leaderboard Agent
**Responsibility**: Analytics and ranking

**Metrics Tracked**:
1. **Time Wasted** (primary ranking)
2. **Extraction Attempts** (secondary)
3. **Scam Type Distribution**
4. **Geographic Patterns**
5. **Success Rate** (completed extractions)

**Ranking Algorithm**:
```javascript
score = (timeWasted * 10) + (attempts * 5) + (extractions * 20)
```

**Output**: Ranked list of scam operations

---

## 🔄 Conversation Flow

```
1. User pastes scam message
        ↓
2. Persona Agent creates identity
        ↓
3. Conversation starts
        ↓
4. For each scammer message:
   ├─ Extraction Agent pulls intelligence
   ├─ Risk Agent checks safety
   ├─ Strategy Agent plans response
   └─ Conversation Agent generates reply
        ↓
5. Leaderboard Agent updates stats
        ↓
6. Loop until termination condition
```

## 💾 Data Models

### Conversation Schema
```javascript
{
  _id: ObjectId,
  userId: String,
  scamType: String,
  persona: PersonaObject,
  messages: [
    {
      sender: "scammer" | "ai",
      text: String,
      timestamp: Date,
      extracted: [String]
    }
  ],
  intelligence: {
    upiIds: [String],
    phoneNumbers: [String],
    urls: [String]
  },
  metrics: {
    timeWasted: Number,
    attempts: Number,
    startTime: Date,
    endTime: Date
  },
  status: "active" | "completed" | "terminated"
}
```

### Leaderboard Entry Schema
```javascript
{
  _id: ObjectId,
  rank: Number,
  identifier: String, // phone/UPI hash
  scamType: String,
  totalTimeWasted: Number,
  totalAttempts: Number,
  conversationCount: Number,
  lastSeen: Date,
  firstSeen: Date,
  dangerScore: Number
}
```

---

## 🔐 Security & Ethics

### Privacy Protection
1. **No Real User Data**: All personas generated
2. **Hashed Identifiers**: Scammer data anonymized
3. **Secure Storage**: Encrypted at rest
4. **Access Control**: Role-based permissions

### Ethical Guidelines
1. **Defensive Only**: Only respond to forwarded scams
2. **No Entrapment**: Don't initiate contact
3. **No Doxxing**: Don't publish personal info
4. **Law Enforcement Ready**: Data format compatible

### Safety Mechanisms
1. **OTP Blocking**: Never share real OTP
2. **Payment Blocking**: Never make real payments
3. **Auto-Termination**: Exit dangerous situations
4. **Rate Limiting**: Prevent system abuse

---

## 🚀 Tech Stack

### Frontend
- **React 19**: Latest hooks + concurrent features
- **Vite**: Fast build tool
- **Tailwind CSS 4**: Utility-first styling
- **WebSocket**: Real-time updates

### Backend (Planned)
- **FastAPI/Node.js**: API gateway
- **LangGraph**: Agent orchestration
- **OpenAI/Anthropic**: LLM provider
- **Redis**: Session management + caching

### Database
- **MongoDB**: Conversations + leaderboard
- **Redis**: Real-time state
- **Pinecone/Weaviate**: Vector storage for similarity search

### Infrastructure
- **Docker**: Containerization
- **Kubernetes**: Orchestration (for scale)
- **AWS/GCP**: Cloud hosting
- **CloudFlare**: CDN + DDoS protection

---

## 📊 Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Response Time | < 2s | 1.5s (simulated) |
| Concurrent Conversations | 100+ | TBD |
| Uptime | 99.9% | TBD |
| Extraction Accuracy | 95%+ | 90% (regex) |
| False Positive Rate | < 5% | TBD |

---

## 🔮 Future Enhancements

### Phase 2 (Post-Hackathon)
- [ ] Real backend integration
- [ ] WebSocket for live updates
- [ ] Database persistence
- [ ] User authentication

### Phase 3 (Production)
- [ ] Voice call support (SIP integration)
- [ ] Multi-language support
- [ ] Mobile app (React Native)
- [ ] Admin dashboard

### Phase 4 (Scale)
- [ ] Distributed agent system
- [ ] ML-based persona optimization
- [ ] Predictive scam detection
- [ ] API for third-party integration

---

## 🤝 Integration Points

### For Telecom Companies
- API endpoint to forward suspected scam calls
- Real-time intelligence feed
- Bulk scammer database

### For Banks
- Phishing detection service
- Customer protection plugin
- Fraud alert integration

### For Law Enforcement
- Evidence export (court-ready format)
- Pattern analysis reports
- Network mapping tools

---

## 📈 Scaling Strategy

### Horizontal Scaling
- Stateless API servers (auto-scale)
- Agent workers in queue system
- Database sharding by conversation ID

### Optimization
- Cache frequent persona types
- Batch intelligence extraction
- Async processing for non-critical tasks

### Cost Management
- LLM request batching
- Smart caching (Redis)
- Tiered LLM selection (cheap for simple, expensive for complex)

---

**This architecture is designed to be:**
- ✅ **Scalable**: Handle millions of conversations
- ✅ **Maintainable**: Clear separation of concerns
- ✅ **Extensible**: Easy to add new agent types
- ✅ **Secure**: Multiple safety layers
- ✅ **Ethical**: Privacy-first design

---

Built with ❤️ for ScamTrap AI
