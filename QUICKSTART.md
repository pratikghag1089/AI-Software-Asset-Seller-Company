# Quick Start - 5 Minutes to First Run

Get the Prog Silo autonomous LinkedIn agent running in 5 minutes.

## Prerequisites
- Python 3.10+
- Ollama installed with gpt-oss model
- LinkedIn account credentials

---

## 1. Install Ollama & Model (2 min)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull gpt-oss model
ollama pull gpt-oss:latest

# Verify
ollama list
```

---

## 2. Setup Project (1 min)

```bash
# Navigate to project
cd /home/user/AI-Software-Asset-Seller-Company

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

---

## 3. Configure (1 min)

```bash
# Copy config
cp .env.example .env

# Edit with your LinkedIn credentials
nano .env
```

**Minimum required settings:**
```bash
LINKEDIN_EMAIL=your-email@example.com
LINKEDIN_PASSWORD=your-password

# Keep these for safety
DRY_RUN_MODE=true
ENABLE_AUTO_POSTING=false
ENABLE_AUTO_COMMENTING=false
```

---

## 4. Initialize (30 sec)

```bash
# Create database
python scripts/init_db.py

# Test Ollama
python scripts/test_ollama.py

# Test LinkedIn login
python scripts/test_linkedin.py
```

---

## 5. Run First Cycle (30 sec)

```bash
# Run one complete cycle in dry-run mode
python main.py manual
```

You should see:
```
🚀 Starting autonomous agent workflow...
🧠 Strategy Agent: Deciding today's actions...
📊 Learning Agent: Analyzing performance...
✍️  Content Agent: Generating post...
[DRY RUN] Would post to LinkedIn:
[Generated content...]
💬 Engagement Agent: Commenting on posts...
[DRY RUN] Would comment on...
✓ Workflow completed successfully
```

---

## Next Steps

### Review Generated Content
```bash
python scripts/generate_test_post.py
```

### Enable Autonomous Mode (when ready)
Edit `.env`:
```bash
DRY_RUN_MODE=false
ENABLE_AUTO_POSTING=true
ENABLE_AUTO_COMMENTING=true
```

### Run Continuously
```bash
python main.py scheduled
```

---

## Troubleshooting

**Ollama not found:**
```bash
ollama serve
```

**LinkedIn login fails:**
- Check credentials in .env
- Temporarily disable 2FA
- Use app-specific password

**Import errors:**
```bash
pip install -r requirements.txt --force-reinstall
```

---

## Configuration Options

### LinkedIn Account Setup

**Option 1: Quick Test (Personal Account)**
- Use your personal LinkedIn
- Test in dry-run mode only

**Option 2: Company Page (Recommended)**
1. Create LinkedIn company page: https://www.linkedin.com/company/setup/new/
2. Name it "Prog Silo Company"
3. Use your personal login credentials

**Option 3: Dedicated Account (Safest)**
- Create new LinkedIn account
- Age it 1-2 weeks before automation

---

## Usage Modes

### Manual (One-time run)
```bash
python main.py manual
```

### Scheduled (Autonomous)
```bash
python main.py scheduled
# Runs daily at 8 AM + engagement every 3 hours
```

---

## Safety Features

✅ Dry-run mode (test without posting)
✅ Content filters (blocks spam, politics, controversial)
✅ Rate limiting (prevents spam detection)
✅ Quality scoring (only posts high-quality content)
✅ Human-like delays (appears natural)

---

## Monitoring

### View Current Stats
```bash
python scripts/view_stats.py
```

### Check Logs
```bash
tail -f logs/progsilo_*.log
```

---

For detailed setup including Digital Ocean deployment, see **SETUP_GUIDE.md**

**Ready to grow your LinkedIn autonomously!** 🚀
