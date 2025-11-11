# Setup Guide - Prog Silo Company Autonomous LinkedIn Agent

Complete step-by-step guide to get your autonomous LinkedIn agent running.

## Prerequisites

- Python 3.10+
- Ollama installed
- LinkedIn account
- (Optional) PostgreSQL database

---

## Step 1: Install Ollama

### Linux/Mac:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Windows:
Download from https://ollama.com/download

### Pull the gpt-oss model:
```bash
ollama pull gpt-oss:latest
```

### Verify it's running:
```bash
ollama list
# Should show gpt-oss:latest
```

---

## Step 2: LinkedIn Account Setup

You have 3 options:

### Option A: Personal Account (Quick Test)
- Use your existing LinkedIn login
- ⚠️ Use carefully - LinkedIn may detect automation

### Option B: Company Page (Recommended)
1. Go to https://www.linkedin.com/company/setup/new/
2. Create "Prog Silo Company" page
3. Fill in details:
   - **Company name**: Prog Silo Company
   - **LinkedIn URL**: linkedin.com/company/prog-silo
   - **Website**: (your website or github)
   - **Industry**: Technology, Information and Internet
   - **Company size**: 2-10 employees
   - **Company type**: Privately Held
   - **Tagline**: Elevating developers, one insight at a time
   - **Description**: Tech coaching and programming insights for mid-level developers

4. Add logo and cover image
5. Use your personal credentials in .env (you'll manage the page)

### Option C: Dedicated Account (Safest)
1. Create new LinkedIn account
2. Set up profile completely (photo, bio, work history)
3. Let it age 1-2 weeks before automation
4. Add connections manually first (50-100)

---

## Step 3: Clone & Setup Project

```bash
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

## Step 4: Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit configuration
nano .env  # or use your preferred editor
```

### Required settings:

```bash
# LinkedIn credentials
LINKEDIN_EMAIL=your-email@example.com
LINKEDIN_PASSWORD=your-secure-password

# Ollama (default is fine)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gpt-oss:latest

# Database - Start with SQLite
DATABASE_URL=sqlite:///progsilo.db

# Safety first - start in dry run mode
DRY_RUN_MODE=true
ENABLE_AUTO_POSTING=false
ENABLE_AUTO_COMMENTING=false
```

---

## Step 5: Initialize Database

```bash
python scripts/init_db.py
```

You should see:
```
✓ Database initialized successfully
```

---

## Step 6: Test Everything

### Test 1: Ollama
```bash
python scripts/test_ollama.py
```

Expected output:
```
✓ All tests passed!
```

### Test 2: LinkedIn Login
```bash
python scripts/test_linkedin.py
```

Expected output:
```
✓ Successfully logged in!
✓ LinkedIn client working!
```

⚠️ **If login fails:**
- Check your credentials in .env
- LinkedIn may require 2FA - disable temporarily or use app password
- Try running with headless=False to see what's happening

### Test 3: Generate Post
```bash
python scripts/generate_test_post.py
```

Expected output:
```
GENERATED POST
Topic: [some topic]
Quality Score: 7.5/10

Content:
[Generated LinkedIn post]
```

---

## Step 7: Run First Cycle (Dry Run)

```bash
python main.py manual
```

This runs one complete cycle in dry run mode (no actual posts/comments).

Expected output:
```
🌅 Starting daily cycle...
🧠 Strategy Agent: Deciding today's actions...
📊 Learning Agent: Analyzing performance...
✍️  Content Agent: Generating post...
[DRY RUN] Would post to LinkedIn:
...
💬 Engagement Agent: Commenting on posts...
[DRY RUN] Would comment on ...
✓ Daily cycle completed successfully
```

---

## Step 8: Gradual Autonomy (Safe Rollout)

### Week 1: Manual review
Keep everything in dry run mode. Run daily and review what it would do:

```bash
# Run once daily manually
python main.py manual
```

Review the logs to see what content it generates.

### Week 2: Enable commenting only
Once you're comfortable:

```bash
# Edit .env
DRY_RUN_MODE=false
ENABLE_AUTO_COMMENTING=true
ENABLE_AUTO_POSTING=false
```

```bash
# Run scheduled
python main.py scheduled
```

This will auto-comment but you manually review/post content.

### Week 3+: Full autonomy
When confident:

```bash
# Edit .env
ENABLE_AUTO_POSTING=true
ENABLE_AUTO_COMMENTING=true
```

Now it's fully autonomous!

---

## Step 9: Deploy to Server (Optional)

### Using Digital Ocean:

1. **Create Droplet**
   - Ubuntu 22.04 LTS
   - Basic plan ($6/month)
   - Choose region close to you

2. **SSH into server**
   ```bash
   ssh root@your-droplet-ip
   ```

3. **Install dependencies**
   ```bash
   # Update system
   apt update && apt upgrade -y

   # Install Python
   apt install python3 python3-pip python3-venv -y

   # Install Ollama
   curl -fsSL https://ollama.com/install.sh | sh

   # Pull model
   ollama pull gpt-oss:latest
   ```

4. **Clone and setup project**
   ```bash
   cd /root
   git clone <your-repo-url>
   cd AI-Software-Asset-Seller-Company

   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   playwright install chromium --with-deps
   ```

5. **Configure .env**
   ```bash
   cp .env.example .env
   nano .env
   # Add your credentials
   ```

6. **Run as service**
   ```bash
   # Create systemd service
   nano /etc/systemd/system/progsilo.service
   ```

   ```ini
   [Unit]
   Description=Prog Silo Autonomous LinkedIn Agent
   After=network.target

   [Service]
   Type=simple
   User=root
   WorkingDirectory=/root/AI-Software-Asset-Seller-Company
   Environment="PATH=/root/AI-Software-Asset-Seller-Company/venv/bin"
   ExecStart=/root/AI-Software-Asset-Seller-Company/venv/bin/python main.py scheduled
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   ```bash
   # Enable and start
   systemctl daemon-reload
   systemctl enable progsilo
   systemctl start progsilo

   # Check status
   systemctl status progsilo

   # View logs
   journalctl -u progsilo -f
   ```

---

## Monitoring & Maintenance

### View stats:
```bash
python scripts/view_stats.py
```

### Check logs:
```bash
tail -f logs/progsilo_*.log
```

### Weekly reports:
Check logs for weekly summary every 7 days.

---

## Troubleshooting

### Ollama not connecting
```bash
# Check if Ollama is running
ollama list

# Start Ollama service
ollama serve
```

### LinkedIn login fails
- Check credentials
- Disable 2FA temporarily
- Use app-specific password if available
- Run with `headless=False` to debug visually

### Database errors
```bash
# Reinitialize database
rm progsilo.db
python scripts/init_db.py
```

### Low quality posts
- Adjust temperature in `core/ollama_client.py`
- Add more specific themes in strategy
- Review learnings and adjust manually

---

## Safety & Best Practices

1. **Start slow**: Always begin with dry run mode
2. **Monitor daily**: Check logs for first 2 weeks
3. **Rate limits**: System includes delays - don't remove them
4. **Quality over quantity**: Better to post less with high quality
5. **Be authentic**: Review and adjust generated content tone
6. **LinkedIn TOS**: This tool is for legitimate growth, not spam

---

## Next Steps

Once running smoothly:

1. **Optimize content**: Use learnings to refine topics
2. **Grow audience**: Engage more in target communities
3. **Track ROI**: Monitor follower growth and engagement
4. **Monetize**: After 5k+ followers, consider:
   - Digital products
   - Consulting services
   - Course creation
   - Sponsorships

---

## Support

- **Logs**: Check `logs/` directory
- **Stats**: Run `python scripts/view_stats.py`
- **Issues**: Review error messages in logs

Good luck with your autonomous LinkedIn growth! 🚀
