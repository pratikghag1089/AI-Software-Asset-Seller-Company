# Prog Silo Company - Autonomous LinkedIn Agent

An intelligent, fully autonomous LinkedIn growth system that posts content and engages with your target audience 24/7.

## 🎯 What It Does

- **Auto-Posts**: Creates and publishes 1 high-quality LinkedIn post per day
- **Auto-Engages**: Comments on 25-30 relevant posts daily with thoughtful insights
- **Auto-Learns**: Analyzes performance and optimizes strategy automatically
- **Grows Autonomously**: Builds your LinkedIn presence while you sleep

## 🏢 Company Profile

**Name**: Prog Silo Company
**Focus**: Tech coaching & programming insights for developers
**Target Audience**: Mid-level developers (2-5 years experience)

## 🤖 How It Works

The system uses 4 autonomous agents:

1. **Strategy Agent**: Analyzes data and decides overall direction
2. **Content Agent**: Creates engaging LinkedIn posts
3. **Engagement Agent**: Finds and comments on relevant posts
4. **Learning Agent**: Tracks metrics and optimizes performance

All powered by Ollama (gpt-oss:latest) running locally.

## 🚀 Quick Start

### 1. Install Ollama

```bash
# Install Ollama from https://ollama.com
curl -fsSL https://ollama.com/install.sh | sh

# Pull the gpt-oss model
ollama pull gpt-oss:latest

# Verify it's running
ollama list
```

### 2. Set Up Database

**Option A: SQLite (Easy, for testing)**
```bash
# No setup needed, just update .env
DATABASE_URL=sqlite:///progsilo.db
```

**Option B: PostgreSQL (Production)**
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE DATABASE progsilo;
CREATE USER progsilo WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE progsilo TO progsilo;
\q
```

### 3. Configure LinkedIn Account

**IMPORTANT**: LinkedIn Account Setup

You have 3 options to connect your LinkedIn account:

#### **Option 1: Use Existing Personal Account** (Quick Start)
- Use your personal LinkedIn login
- System will post/comment as you
- ⚠️ Risk: LinkedIn may flag automated activity

#### **Option 2: Create Company LinkedIn Page** (Recommended)
1. Go to https://www.linkedin.com/company/setup/new/
2. Create "Prog Silo Company" page
3. Use your personal account to manage it
4. System posts as the company
5. ✅ Safer, more professional

#### **Option 3: Create Dedicated Account** (Safest)
1. Create new LinkedIn account for "Prog Silo Company"
2. Build profile manually first (add photo, bio, etc.)
3. Let it age for 1-2 weeks
4. Then enable automation
5. ✅ Safest from account restrictions

**For this setup, I recommend Option 2 (Company Page)**

### 4. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for LinkedIn scraping)
playwright install chromium
```

### 5. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit with your details
nano .env
```

**Required settings in .env:**
```bash
LINKEDIN_EMAIL=your-email@example.com
LINKEDIN_PASSWORD=your-password

# Start in safe mode
DRY_RUN_MODE=true
ENABLE_AUTO_POSTING=false
ENABLE_AUTO_COMMENTING=false
```

### 6. Initialize Database

```bash
python scripts/init_db.py
```

### 7. Test the System

```bash
# Test Ollama connection
python scripts/test_ollama.py

# Test LinkedIn login
python scripts/test_linkedin.py

# Generate a test post
python scripts/generate_test_post.py
```

### 8. Run Autonomous System

```bash
# Start the autonomous agent
python main.py

# Or run in background
nohup python main.py > progsilo.log 2>&1 &
```

## 🛡️ Safety Features

- **Dry Run Mode**: Test everything without actually posting
- **Rate Limiting**: Respects LinkedIn's limits to avoid spam detection
- **Content Filters**: Blocks political, controversial, or spammy content
- **Quality Checks**: Only posts/comments scoring 7+/10
- **Human-like Timing**: Randomized delays to appear natural

## 📊 Monitoring

The system generates weekly reports emailed to you:

```bash
# View current stats
python scripts/view_stats.py

# Check agent logs
tail -f logs/agents.log

# Weekly report
cat reports/week_$(date +%V).txt
```

## ⚙️ Configuration

### Gradual Autonomy (Recommended)

**Week 1**: Manual approval
```bash
DRY_RUN_MODE=true
ENABLE_AUTO_POSTING=false
```

**Week 2**: Auto-comment only
```bash
DRY_RUN_MODE=false
ENABLE_AUTO_COMMENTING=true
```

**Week 3+**: Fully autonomous
```bash
ENABLE_AUTO_POSTING=true
ENABLE_AUTO_COMMENTING=true
```

## 🎯 Growth Goals

- **Month 1**: 500 followers
- **Month 3**: 2,000 followers
- **Month 6**: 5,000+ followers

## 📁 Project Structure

```
.
├── agents/               # Agent implementations
│   ├── strategy_agent.py
│   ├── content_agent.py
│   ├── engagement_agent.py
│   └── learning_agent.py
├── core/                 # Core functionality
│   ├── orchestrator.py   # LangGraph workflow
│   ├── linkedin_client.py
│   └── ollama_client.py
├── database/             # Database models
│   ├── models.py
│   └── queries.py
├── scripts/              # Utility scripts
├── logs/                 # Agent logs
├── reports/              # Performance reports
├── main.py               # Main entry point
└── requirements.txt
```

## 🤔 FAQ

**Q: Will LinkedIn ban my account?**
A: Follow the gradual autonomy approach, use rate limiting, and the system mimics human behavior. Start with a company page for safety.

**Q: How much does it cost to run?**
A: $0 for compute (runs locally), ~$6/month for Digital Ocean hosting (optional)

**Q: Can I customize the content?**
A: Yes! Edit `agents/content_agent.py` to adjust tone, topics, and style.

**Q: What if I want to post manually sometimes?**
A: The system tracks all posts, including manual ones, and learns from them.

## 📝 License

MIT License - Use for any purpose

## 🆘 Support

Issues? Open a GitHub issue or check logs in `logs/agents.log`

---

**Built with**: Python, LangGraph, Ollama, PostgreSQL, Playwright
