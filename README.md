# 🔍 Clipse - AI-Powered News Analysis Platform

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![React](https://img.shields.io/badge/react-18.3.1-61dafb.svg)
![Google Cloud](https://img.shields.io/badge/Google%20Cloud-deployed-4285F4.svg)

**Clipse** is an intelligent news verification and analysis platform that helps users fact-check news articles, analyze sentiment, detect bias, and track trending topics using Google's Generative AI and a microservices architecture.

## 🌐 Live Demo

**Frontend:** [https://storage.googleapis.com/clipse-app/index.html](https://storage.googleapis.com/clipse-app/index.html)

## ✨ Features

- **🔍 Real-time News Search** - Search and retrieve news articles from multiple sources
- **✅ Fact-Checking** - AI-powered verification of news claims and statements
- **📊 Sentiment Analysis** - Analyze emotional tone and bias in news articles
- **📈 Trend Detection** - Track popular topics and emerging news trends
- **🎯 Bias Detection** - Identify potential biases in news reporting
- **🔬 Forensic Analysis** - Deep analysis of news sources and credibility

## 🏗️ Architecture

### Microservices Design

```
┌─────────────────┐
│   Frontend      │ (React + TypeScript + Vite)
│  (Clipse App)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Manager Agent   │ (FastAPI + Google ADK)
│   (Port 8000)   │
└────────┬────────┘
         │
    ┌────┴────┬────────┬────────┐
    ▼         ▼        ▼        ▼
┌────────┐┌────────┐┌────────┐┌────────┐
│Search  ││Sentiment││Trends  ││ Fact   │
│Agent   ││Agent   ││Agent   ││Check   │
│:8001   ││:8002   ││:8003   ││Agent   │
│        ││        ││        ││:8004   │
└────────┘└────────┘└────────┘└────────┘
```

### Technology Stack

#### Backend
- **Python 3.11+** - Core programming language
- **FastAPI 0.104.1+** - High-performance web framework
- **Google ADK (Agent Development Kit)** - AI agent framework
- **Google Generative AI (Gemini)** - LLM for analysis
- **TextBlob** - Natural language processing
- **PyTrends** - Google Trends integration
- **Uvicorn** - ASGI server

#### Frontend
- **React 18.3.1** - UI framework
- **TypeScript 5.5.4** - Type-safe JavaScript
- **Vite 5.2.0** - Build tool and dev server
- **Tailwind CSS 3.4.17** - Utility-first CSS
- **React Router 6.26.2** - Client-side routing

#### Infrastructure
- **Google Cloud Run** - Serverless container deployment
- **Google Cloud Storage** - Static website hosting
- **Docker** - Containerization
- **Git/GitHub** - Version control

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- Node.js 18+ and npm
- Google Cloud SDK (for deployment)
- Git

### Local Development

#### 1. Clone the Repository

```bash
git clone https://github.com/argha30009/Google-Gen-Ai.git
cd Google-Gen-Ai
```

#### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies for each service
cd manager
pip install -r requirements.txt

cd sub_agents/search_agent
pip install -r requirements.txt

cd ../sentiment_agent
pip install -r requirements.txt

cd ../trends_agent
pip install -r requirements.txt

cd ../factcheck_agent
pip install -r requirements.txt
```

#### 3. Configure Environment Variables

Create a `.env` file in the `manager` directory:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

#### 4. Start Backend Services

```bash
# Terminal 1 - Manager Agent
cd manager
python server.py

# Terminal 2 - Search Agent
cd manager/sub_agents/search_agent
python server.py

# Terminal 3 - Sentiment Agent
cd manager/sub_agents/sentiment_agent
python server.py

# Terminal 4 - Trends Agent
cd manager/sub_agents/trends_agent
python server.py

# Terminal 5 - FactCheck Agent
cd manager/sub_agents/factcheck_agent
python server.py
```

Or use the convenience script:
```bash
bash start_all_services.sh
```

#### 5. Frontend Setup

```bash
cd frontend/frontend-magic-pattern

# Install dependencies
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env

# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`

## 🌐 Deployment

### Deploy to Google Cloud

#### 1. Configure Google Cloud

```bash
gcloud config set project YOUR_PROJECT_ID
gcloud config set run/region asia-south1
```

#### 2. Deploy Microservices

```bash
# Deploy Search Agent
cd manager/sub_agents/search_agent
gcloud run deploy search-agent --source . --region asia-south1 --allow-unauthenticated

# Deploy Sentiment Agent
cd ../sentiment_agent
gcloud run deploy sentiment-agent --source . --region asia-south1 --allow-unauthenticated

# Deploy Trends Agent
cd ../trends_agent
gcloud run deploy trends-agent --source . --region asia-south1 --allow-unauthenticated

# Deploy FactCheck Agent
cd ../factcheck_agent
gcloud run deploy factcheck-agent --source . --region asia-south1 --allow-unauthenticated

# Deploy Manager Agent with environment variables
cd ../../../manager
gcloud run deploy manager-agent --source . --region asia-south1 --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=YOUR_API_KEY,\
SEARCH_AGENT_URL=https://search-agent-xxx.run.app,\
SENTIMENT_AGENT_URL=https://sentiment-agent-xxx.run.app,\
TRENDS_AGENT_URL=https://trends-agent-xxx.run.app,\
FACTCHECK_AGENT_URL=https://factcheck-agent-xxx.run.app
```

#### 3. Deploy Frontend

```bash
cd frontend/frontend-magic-pattern

# Update .env for production
echo "VITE_API_URL=https://manager-agent-xxx.run.app" > .env

# Build
npm run build

# Create GCS bucket
gsutil mb -l asia-south1 gs://your-bucket-name

# Make bucket public
gsutil iam ch allUsers:objectViewer gs://your-bucket-name

# Configure for website hosting
gsutil web set -m index.html gs://your-bucket-name

# Upload files
gsutil -m cp -r dist/* gs://your-bucket-name/
```

Your app will be available at: `https://storage.googleapis.com/your-bucket-name/index.html`

## 📊 API Endpoints

### Manager Agent (Port 8000)

- `POST /run` - Process news query
  ```json
  {
    "query": "latest AI news"
  }
  ```

- `GET /health` - Health check
- `GET /` - Service info

### Sub-agents (Ports 8001-8004)

Each sub-agent provides:
- `POST /process` - Process specific task
- `GET /health` - Health check

## 🔧 Configuration

### CORS Settings

The manager agent is configured to accept requests from:
- `http://localhost:5173` (local dev)
- `https://storage.googleapis.com` (GCS buckets)

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google AI API key | Yes |
| `SEARCH_AGENT_URL` | Search service URL | Production |
| `SENTIMENT_AGENT_URL` | Sentiment service URL | Production |
| `TRENDS_AGENT_URL` | Trends service URL | Production |
| `FACTCHECK_AGENT_URL` | FactCheck service URL | Production |

## 📝 Project Structure

```
.
├── manager/                    # Manager agent (orchestrator)
│   ├── agent.py               # Agent logic
│   ├── server.py              # FastAPI server
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile            # Container configuration
│   └── sub_agents/           # Microservices
│       ├── search_agent/     # News search service
│       ├── sentiment_agent/  # Sentiment analysis service
│       ├── trends_agent/     # Trends detection service
│       └── factcheck_agent/  # Fact-checking service
├── frontend/
│   └── frontend-magic-pattern/
│       ├── src/
│       │   ├── components/   # React components
│       │   ├── pages/        # Page components
│       │   ├── context/      # React context
│       │   └── App.tsx       # Main app component
│       ├── package.json      # Node dependencies
│       └── vite.config.ts    # Vite configuration
├── scripts/                   # Deployment scripts
└── README.md                 # This file
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Argha Dolai**
- GitHub: [@argha30009](https://github.com/argha30009)
- Email: arghadolai0903@gmail.com

## 🙏 Acknowledgments

- Google Cloud Platform for hosting infrastructure
- Google Generative AI (Gemini) for AI capabilities
- The open-source community for amazing tools and libraries

## 📞 Support

For support, email arghadolai0903@gmail.com or open an issue on GitHub.

---

Made with ❤️ by Team 52Saints