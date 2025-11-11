# Project Structure

```
AI-Software-Asset-Seller-Company/
│
├── main.py                     # Main entry point - runs the autonomous system
│
├── agents/                     # Autonomous AI agents
│   ├── __init__.py
│   ├── strategy_agent.py      # Decides overall strategy and daily actions
│   ├── content_agent.py       # Generates LinkedIn posts
│   ├── engagement_agent.py    # Finds and comments on posts
│   └── learning_agent.py      # Analyzes data and improves strategy
│
├── core/                       # Core functionality
│   ├── __init__.py
│   ├── orchestrator.py        # LangGraph workflow coordinator
│   ├── ollama_client.py       # Interface to Ollama (gpt-oss)
│   ├── linkedin_client.py     # LinkedIn automation (Playwright)
│   └── safety_filters.py      # Content filters and rate limiting
│
├── database/                   # Database models and queries
│   ├── __init__.py
│   └── models.py              # SQLAlchemy models (Posts, Comments, Metrics, etc.)
│
├── scripts/                    # Utility scripts
│   ├── __init__.py
│   ├── init_db.py             # Initialize database
│   ├── test_ollama.py         # Test Ollama connection
│   ├── test_linkedin.py       # Test LinkedIn login
│   ├── generate_test_post.py  # Generate sample post
│   └── view_stats.py          # View performance statistics
│
├── logs/                       # Application logs (auto-created)
│   └── progsilo_YYYY-MM-DD.log
│
├── reports/                    # Performance reports (auto-created)
│   └── week_NN.txt
│
├── requirements.txt            # Python dependencies
├── .env.example               # Example environment configuration
├── .env                       # Your actual config (not in git)
├── .gitignore                 # Git ignore rules
│
├── README.md                  # Project overview and documentation
├── QUICKSTART.md              # 5-minute quick start guide
├── SETUP_GUIDE.md             # Comprehensive setup instructions
└── PROJECT_STRUCTURE.md       # This file
```

## File Descriptions

### Main Files

**main.py**
- Entry point for the application
- Supports two modes: `manual` (one-time run) and `scheduled` (autonomous)
- Initializes system, schedules agent cycles
- Handles graceful shutdown

### Agents

**strategy_agent.py**
- Loads and manages current strategy from database
- Decides daily action plan (what to post, how many comments, etc.)
- Updates strategy based on learning recommendations
- Calculates strategy performance scores

**content_agent.py**
- Generates LinkedIn posts using Ollama
- Incorporates past learnings into content creation
- Scores post quality (1-10)
- Saves posts to database with metadata

**engagement_agent.py**
- Searches LinkedIn for relevant posts
- Filters posts by relevance and engagement potential
- Generates thoughtful, valuable comments
- Tracks comment performance

**learning_agent.py**
- Analyzes post performance (views, engagement rate)
- Analyzes comment effectiveness (reply rate)
- Tracks growth metrics (followers, profile views)
- Generates insights and strategy recommendations

### Core

**orchestrator.py**
- Uses LangGraph to coordinate agent workflow
- Defines execution flow: Strategy → Learn → Create → Publish → Engage
- Handles errors and logging
- Manages dry-run vs live mode

**ollama_client.py**
- Interface to local Ollama instance
- Supports text generation, structured output (JSON), and scoring
- Uses gpt-oss:latest model
- Handles retries and error recovery

**linkedin_client.py**
- Automates LinkedIn interactions using Playwright
- Handles login, posting, commenting, searching
- Extracts profile statistics
- Implements human-like delays and behavior

**safety_filters.py**
- Content safety filters (blocks spam, politics, controversial topics)
- Rate limiting (prevents spam detection by LinkedIn)
- Professional tone validation
- Human-like delay simulation

### Database

**models.py**
- SQLAlchemy ORM models
- Tables: Posts, Comments, Metrics, Learnings, Strategies, AgentRuns
- Database initialization and session management
- Supports both SQLite (dev) and PostgreSQL (prod)

### Scripts

**init_db.py**
- Creates database tables
- Safe to run multiple times (idempotent)

**test_ollama.py**
- Verifies Ollama connection
- Tests text generation and scoring
- Validates gpt-oss model is available

**test_linkedin.py**
- Tests LinkedIn login
- Fetches profile stats
- Runs in non-headless mode for debugging

**generate_test_post.py**
- Generates a sample LinkedIn post
- Useful for testing content quality
- Doesn't post to LinkedIn

**view_stats.py**
- Displays current performance statistics
- Shows posts, comments, growth, learnings
- Useful for monitoring progress

## Data Flow

```
                    ┌──────────────┐
                    │  main.py     │
                    │  (Scheduler) │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │ Orchestrator │
                    │  (LangGraph) │
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼─────┐     ┌─────▼──────┐    ┌─────▼─────┐
   │ Strategy │     │  Content   │    │Engagement │
   │  Agent   │     │   Agent    │    │   Agent   │
   └────┬─────┘     └─────┬──────┘    └─────┬─────┘
        │                 │                  │
        │           ┌─────▼──────┐           │
        │           │   Ollama   │           │
        │           │ (gpt-oss)  │           │
        │           └─────┬──────┘           │
        │                 │                  │
        └────────┬────────┴────────┬─────────┘
                 │                 │
          ┌──────▼────────┐  ┌────▼────────┐
          │   Database    │  │  LinkedIn   │
          │ (PostgreSQL/  │  │  (Playwright)│
          │   SQLite)     │  │             │
          └───────────────┘  └─────────────┘
                 │
          ┌──────▼────────┐
          │  Learning     │
          │   Agent       │
          │ (Analyzes &   │
          │  Optimizes)   │
          └───────────────┘
```

## Agent Workflow (LangGraph)

```
START
  ↓
[Strategy Agent] - Decides today's actions
  ↓
[Learning Agent] - Analyzes past performance
  ↓
[Content Agent] - Generates post
  ↓
[Publish Node] - Posts to LinkedIn (if enabled)
  ↓
[Engagement Agent] - Comments on posts
  ↓
[Finalize] - Logs summary
  ↓
END
```

## Configuration

### Environment Variables (.env)

**Required:**
- `LINKEDIN_EMAIL` - Your LinkedIn email
- `LINKEDIN_PASSWORD` - Your LinkedIn password
- `OLLAMA_HOST` - Ollama server URL (default: http://localhost:11434)
- `OLLAMA_MODEL` - Model name (default: gpt-oss:latest)
- `DATABASE_URL` - Database connection string

**Safety:**
- `DRY_RUN_MODE` - Run without actually posting (true/false)
- `ENABLE_AUTO_POSTING` - Allow autonomous posting (true/false)
- `ENABLE_AUTO_COMMENTING` - Allow autonomous commenting (true/false)

**Strategy:**
- `POSTING_TIME` - Daily post time (HH:MM format)
- `MAX_POSTS_PER_DAY` - Maximum posts per day
- `MAX_COMMENTS_PER_DAY` - Maximum comments per day
- `TARGET_HASHTAGS` - Comma-separated hashtags to target

**Growth:**
- `DAILY_FOLLOWER_TARGET` - Target follower growth per day
- `ENGAGEMENT_RATE_TARGET` - Target engagement rate (0.0-1.0)

## Dependencies

**Core:**
- `langgraph` - Agent orchestration framework
- `ollama` - Ollama Python client
- `playwright` - Browser automation
- `sqlalchemy` - Database ORM
- `apscheduler` - Task scheduling
- `loguru` - Advanced logging

**See requirements.txt for full list**

## Database Schema

**posts** - LinkedIn posts created
- content, topic, quality_score
- views, likes, comments, shares
- engagement_rate, posted_at

**comments** - Comments made on LinkedIn
- post_url, comment_text, quality_score
- likes, replies, author_replied
- profile_visits_after

**metrics** - Daily performance metrics
- date, followers, follower_change
- profile_views, avg_post_views
- avg_engagement_rate

**learnings** - Insights learned by system
- category, insight, confidence
- data_points, active, applied_count

**strategies** - Strategy configurations
- content_themes, target_hashtags
- posting_time, comments_per_day
- strategy_score

**agent_runs** - Agent execution logs
- agent_name, task, success
- tokens_used, execution_time

## Extending the System

### Add New Agent

1. Create `agents/new_agent.py`
2. Implement agent class with main method
3. Add node to orchestrator workflow
4. Connect in LangGraph graph

### Modify Content Style

Edit `agents/content_agent.py`:
- Adjust system prompt in `_build_system_prompt()`
- Modify quality criteria in `_score_post_quality()`
- Change content themes in strategy

### Add New Data Sources

Create client in `core/`:
- Follow pattern from `linkedin_client.py`
- Implement context manager
- Add rate limiting
- Handle errors gracefully

### Custom Learning Insights

Edit `agents/learning_agent.py`:
- Add new analysis methods
- Define insight categories
- Adjust confidence calculations
- Update strategy recommendations

## Troubleshooting

**Check logs:**
```bash
tail -f logs/progsilo_*.log
```

**Verify database:**
```bash
sqlite3 progsilo.db ".tables"
```

**Test components:**
```bash
python scripts/test_ollama.py
python scripts/test_linkedin.py
python scripts/generate_test_post.py
```

**Reset database:**
```bash
rm progsilo.db
python scripts/init_db.py
```

## Security Notes

- Never commit `.env` file
- Use app-specific passwords when possible
- Start with dry-run mode
- Monitor LinkedIn account for warnings
- Respect rate limits
- Review generated content initially

## Performance Tips

1. **Ollama**: Use GPU if available for faster generation
2. **Database**: Use PostgreSQL for production
3. **Scheduling**: Spread comments throughout day
4. **Learning**: Collect at least 1 week of data before trusting insights
5. **Quality**: Prioritize quality over quantity

## License

MIT License - See LICENSE file

## Support

- Check logs first
- Review SETUP_GUIDE.md
- Run test scripts to isolate issues
- Examine database for data problems
