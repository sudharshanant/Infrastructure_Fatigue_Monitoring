# Infrastructure Fatigue Monitoring Dashboard

A production-ready Flask application for real-time vibration-based infrastructure fatigue monitoring with professional analytics dashboard.

**Status**: ✅ Production Ready  
**Dataset**: 1000+ records (2023-01-01 to 2025-09-26)  
**Technology**: Flask 3.0.3 | Pandas 2.2.3 | Chart.js | Docker  

---

## 🚀 Quick Start

### Development Mode (Local)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py
```

Visit: http://127.0.0.1:5000

### Production Deployment

Choose your deployment method:

| Method | Use Case | Guide |
|--------|----------|-------|
| **Docker** | Containerized, portable | See [DEPLOYMENT.md](DEPLOYMENT.md#docker-deployment) |
| **Systemd** | Native Linux service | See [DEPLOYMENT.md](DEPLOYMENT.md#production-systemd-service) |
| **Gunicorn** | Manual WSGI server | See [DEPLOYMENT.md](DEPLOYMENT.md#gunicorn-manual-setup) |

**Full deployment guide**: [DEPLOYMENT.md](DEPLOYMENT.md)  
**Pre-deployment checklist**: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

---

## 📊 Project Structure

```
├── app.py                      # Flask backend (analysis logic, data loading, routing)
├── wsgi.py                     # WSGI entry point (Gunicorn)
├── requirements.txt            # Development dependencies
├── requirements-prod.txt       # Production dependencies (minimal)
├── .env.example                # Environment configuration template
├── Dockerfile                  # Production container image
├── docker-compose.yml          # Container orchestration
├── data/
│   └── vibration_data.csv     # 1000-record dataset (2023-2025)
├── templates/
│   └── index.html             # Dashboard UI (8 sections)
├── static/
│   └── styles.css             # Modern responsive styles (CSS Variables)
├── DEPLOYMENT.md              # 400+ line deployment guide
├── DEPLOYMENT_CHECKLIST.md    # Pre-deployment summary
└── README.md                  # This file
```

---

## 📈 Dataset Format

The app expects `data/vibration_data.csv` with these columns:

| Column | Type | Unit |
|--------|------|------|
| `Date` | datetime | YYYY-MM-DD HH:MM:SS |
| `Vibration` | float | m/s² |

**Current Dataset**:
- Records: 1000
- Date range: 2023-01-01 to 2025-09-26 (997 days)
- Vibration range: 0.100 to 0.306 m/s²
- Distribution: 88% SAFE, 11.6% EARLY FATIGUE, 0.4% HIGH RISK

Example:
```csv
Date,Vibration
2023-01-01 00:00:00,0.125
2023-01-02 00:00:00,0.130
```

---

## 🎯 Status Classification

### Point-Level (Individual Reading)

| Status | Range | Meaning |
|--------|-------|---------|
| **SAFE** | < 0.22 m/s² | Normal operation |
| **EARLY FATIGUE** | 0.22 - 0.30 m/s² | Caution zone, monitor closely |
| **HIGH RISK** | ≥ 0.30 m/s² | Critical, immediate action required |

### Monthly-Level (Aggregated Average)

| Status | Avg Range | Meaning |
|--------|-----------|---------|
| **NORMAL** | < 0.22 m/s² | Normal monthly average |
| **EARLY FATIGUE** | 0.22 - 0.30 m/s² | Watch month, review trends |
| **CRITICAL** | ≥ 0.30 m/s² | Critical month, investigate cause |

---

## 🎨 Dashboard Features

### 8 Main Sections

1. **Header** - Project title, statistics, date range
2. **Quick Analysis** - Date picker + vibration input form
3. **Result Card** - Color-coded analysis output
4. **Vibration Trend** - 120-point line chart with threshold lines
5. **Key Metrics** - 6 cards: Total Records, Date Range, Safe/Fatigue/Risk counts, Avg Vibration
6. **Monthly Analysis** - Table with month-level status and averages
7. **Recent Readings** - Last 10 measurements with per-point status
8. **Legend** - Status definitions and color coding

### Technology Stack

- **Backend**: Flask 3.0.3 + Pandas 2.2.3
- **Frontend**: HTML5 + CSS3 (Variables, Gradients, Flexbox) + Chart.js
- **Design**: Modern responsive UI with 3 breakpoints (desktop, tablet, mobile)
- **Visualization**: Interactive Chart.js line charts with dual threshold lines

---

## ⚙️ Configuration

### Environment Variables (`.env`)

```bash
# Application
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secure-key-here

# Server
HOST=0.0.0.0
PORT=5000
WORKERS=4

# Data
DATA_PATH=data/vibration_data.csv

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

Copy `.env.example` to `.env` and update values:
```bash
cp .env.example .env
nano .env
```

---

## 🐳 Docker Deployment

### Quick Start

```bash
# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

**Access**: http://localhost:5000

### Features

- ✅ Non-root user (security best practice)
- ✅ Health checks (automatic restart on failure)
- ✅ Volume mounts (persistent data/logs)
- ✅ Custom network isolation
- ✅ Automatic restart policy

---

## 📋 Production Checklist

Before deploying to production:

- [ ] Update `.env` with production values
- [ ] Set strong `SECRET_KEY` (generate with `python -c "import os; print(os.urandom(24).hex())"`)
- [ ] Configure domain and SSL/TLS certificate
- [ ] Set up log rotation
- [ ] Configure Nginx reverse proxy
- [ ] Create backups of `data/vibration_data.csv`
- [ ] Test health endpoints
- [ ] Review security checklist (see DEPLOYMENT.md)
- [ ] Set up monitoring/alerting

See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for complete pre-deployment guide.

---

## 🔒 Security

### Implemented

- ✅ CSRF protection via Flask-WTF
- ✅ Environment-based secrets management
- ✅ Non-root Docker user
- ✅ Health checks for availability
- ✅ Input validation on form submissions

### Recommended for Production

1. **Enable HTTPS/SSL**: Use Let's Encrypt with certbot
2. **Nginx Reverse Proxy**: See DEPLOYMENT.md section
3. **Rate Limiting**: Add Flask-Limiter for API protection
4. **Database Migration**: Move from CSV to PostgreSQL
5. **User Authentication**: Implement role-based access control

See [DEPLOYMENT.md](DEPLOYMENT.md#security-checklist) for full security guide.

---

## 📊 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Serve dashboard with full analytics |
| `/` | POST | Analyze single vibration reading |

**Request (POST)**:
```json
{
  "analysis_date": "2025-12-15",
  "vibration_value": 0.25
}
```

**Response**: Color-coded status card with visualization

---

## 🛠️ Development

### Add New Features

1. **Backend Analysis**: Add functions to `app.py`
2. **Frontend Components**: Update `templates/index.html`
3. **Styling**: Modify `static/styles.css` (uses CSS Variables)
4. **Data**: Replace `data/vibration_data.csv`

### Testing

```bash
# Run with debug mode
export FLASK_ENV=development
export FLASK_DEBUG=True
python app.py
```

---

## 📈 Scaling & Future Enhancements

### Short-term (Month 1)
- [ ] Database migration (PostgreSQL)
- [ ] Real-time sensor data integration
- [ ] User authentication system

### Medium-term (Quarter 1)
- [ ] Predictive maintenance ML models
- [ ] Multi-site support
- [ ] Notification/alerting system

### Long-term
- [ ] Mobile app
- [ ] Kubernetes deployment
- [ ] Advanced analytics dashboard (Grafana integration)

See DEPLOYMENT.md "Scaling Strategies" section for detailed approach.

---

## 📞 Troubleshooting

### App won't start
```bash
# Check Python version (need 3.11+)
python --version

# Check dependencies
pip list

# Check port availability
lsof -i :5000
```

### Data not loading
```bash
# Validate CSV format
head -5 data/vibration_data.csv

# Check file permissions
ls -l data/vibration_data.csv
```

### Docker issues
```bash
# See full logs
docker-compose logs app

# Rebuild image
docker-compose build --no-cache
```

See [DEPLOYMENT.md](DEPLOYMENT.md#troubleshooting) for comprehensive troubleshooting guide.

---

## 📝 License

This project is configured for Infrastructure Fatigue Monitoring. See LICENSE file for details.

---

## 📚 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Complete production deployment guide (400+ lines)
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)**: Pre-deployment checklist & success criteria
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)**: Technical project overview

---

**Last Updated**: 2025  
**Status**: ✅ Production Ready | 🚀 Ready for Deployment
