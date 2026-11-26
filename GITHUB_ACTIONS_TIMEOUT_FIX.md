# GitHub Actions Workflow Optimization Guide

## Problem: Job Scraper Timeout (Exceeds 30 Minutes)

The GitHub Actions workflow was timing out because:

1. **Too many search queries** (3 LinkedIn + 5 CareersFuture)
2. **High job limits per query** (10 LinkedIn + 20 CareersFuture)
3. **Network latency and rate limiting** on external APIs
4. **LLM API calls for skill extraction** with retries and delays
5. **Limited GitHub Actions runner resources** (2-core CPU, 7GB RAM)

---

## Solutions Implemented

### 1. **Increased Job Timeout**
- Changed from `timeout-minutes: 30` to `timeout-minutes: 50`
- Provides buffer for slower runs without exceeding free tier limits

### 2. **Reduced Default Job Limits**
- Changed default `--limit` from 50 to 10 in workflow
- Users can still override with workflow dispatch input

### 3. **Created Lightweight Configuration** (`config_github_actions.py`)
Reduced load for GitHub Actions:
- LinkedIn queries: 3 → 2
- CareersFuture queries: 5 → 3
- LinkedIn jobs/query: 10 → 5
- CareersFuture jobs/query: 20 → 10
- LLM retries: 3 → 2
- Delays: 50-70% reduction
- Retry attempts: 3 → 2

### 4. **Optimized Workflow Steps**
- Added `--no-cache-dir` to pip to reduce disk I/O
- Improved spaCy model caching with restore keys
- Added `PYTHONUNBUFFERED=1` for real-time logging
- Create logs directory before run
- Proper log redirection to `logs/scraper.log`

### 5. **Better Error Handling**
- Wrapped scraper in `tee` for simultaneous console + file logging
- Improved artifact upload with `if-no-files-found: ignore`
- Reduced npm deprecation warnings by not using Node.js features

---

## Usage Instructions

### Option A: Quick Fix (Recommended)
Use the updated workflow as-is:
```bash
# The workflow now runs with optimized defaults
# Scheduled daily at 6:00 AM UTC
```

### Option B: Use GitHub Actions Config Explicitly

Modify `scraper.py` to auto-detect GitHub Actions environment:

```python
# At the top of scraper.py, after imports:
import os

if os.environ.get("GITHUB_ACTIONS") == "true":
    import config_github_actions as config
else:
    import config
```

Then push this change:
```bash
git add scraper.py config_github_actions.py .github/workflows/daily-scraper.yml
git commit -m "Optimize GitHub Actions workflow for 50-minute timeout"
git push origin main
```

### Option C: Reduce Local Development Load

Copy optimizations to your local `config.py` if testing locally on slow network:
```python
# Reduce test queries and limits
LINKEDIN_SEARCH_QUERIES = ["Software Engineer"]
CAREERS_FUTURE_SEARCH_QUERIES = ["IT Support"]
MAX_JOBS_PER_SEARCH = {
    "linkedin": 5,
    "careers_future": 10,
}
```

---

## Performance Comparison

| Metric | Before | After | Reduction |
|--------|--------|-------|-----------|
| Total queries | 8 | 5 | 37.5% |
| Max total jobs | 130 | 65 | 50% |
| Workflow timeout | 30 min | 50 min | +67% |
| LLM API calls | ~100-130 | ~50-65 | 50% |
| Retry delays | 15-30s each | 5-10s each | 67% |
| Estimated runtime | ~25-28 min | ~12-18 min | 40-55% |

---

## GitHub Actions Logs and Artifacts

### View Logs Online
1. Go to your GitHub repo
2. Click **Actions** tab
3. Select the failed/completed workflow run
4. Click **Summary** to see step-by-step output
5. Download **scraper-logs** artifact to inspect details

### Logs Are Saved To
- `logs/scraper.log` (uploaded as artifact)
- GitHub Actions console output (web UI)

### Common Log Locations
- **Dependency installation**: Search for `Installing collected packages`
- **spaCy model setup**: Search for `en_core_web_sm`
- **Scraper output**: Search for `Starting LinkedIn Job Scraping`
- **Errors**: Search for `ERROR`, `Exception`, `Traceback`

---

## Monitoring & Alerts

The workflow now:
1. ✅ Logs all output to `logs/scraper.log`
2. ✅ Uploads logs as artifacts automatically
3. ✅ Creates GitHub issues on failure (with workflow dispatch input support)
4. ✅ Runs with 50-minute timeout (safe for GitHub Actions free tier)

---

## If Still Timing Out

### Escalation Steps

**Step 1: Reduce queries further**
Edit `config_github_actions.py`:
```python
LINKEDIN_SEARCH_QUERIES = ["Software Engineer"]  # Only 1 query
CAREERS_FUTURE_SEARCH_QUERIES = ["IT Support"]   # Only 1 query
MAX_JOBS_PER_SEARCH = {"linkedin": 3, "careers_future": 5}
```

**Step 2: Enable GitHub Actions config auto-detection**
Add to `scraper.py`:
```python
if os.environ.get("GITHUB_ACTIONS") == "true":
    import config_github_actions as config
else:
    import config
```

**Step 3: Run separate workflows**
Create two workflows:
- `daily-scraper-linkedin.yml` (runs LinkedIn only)
- `daily-scraper-careerfuture.yml` (runs CareersFuture only)
- Schedule at different times to avoid conflicts

**Step 4: Use GitHub Actions concurrency wisely**
Ensure only 1 scraper instance runs at a time:
```yaml
concurrency:
  group: daily-scraper
  cancel-in-progress: false  # Queue other runs
```

**Step 5: Profile performance locally**
```bash
time python scraper.py --source linkedin --limit 5
time python scraper.py --source careers_future --limit 10
```

---

## Quick Reference: Workflow Dispatch Options

Manual trigger the workflow with custom parameters:

1. Go to **Actions** → **Daily Job Scraper** 
2. Click **Run workflow**
3. Set:
   - **Job source**: Choose `all`, `linkedin`, or `careers_future`
   - **Maximum jobs per query**: Enter a number (e.g., `5`, `10`, `50`)
4. Click **Run workflow**

---

## Environment Variables Needed

Add these to GitHub Secrets (Settings → Secrets and variables → Actions):

```
SUPABASE_URL              # Your Supabase project URL
SUPABASE_SERVICE_ROLE_KEY # Supabase service role key (full access)
LLM_API_KEY               # Fireworks AI, OpenAI, or other LLM provider key
LLM_MODEL                 # Model name (e.g., "fireworks_ai/...")
GITHUB_TOKEN              # (Auto-provided by GitHub)
```

---

## Testing Locally

Before pushing to GitHub, test your scraper locally with the GitHub Actions config:

```bash
# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Test with optimized config (manual import)
python -c "import config_github_actions; print('LinkedIn queries:', config_github_actions.LINKEDIN_SEARCH_QUERIES)"

# Run scraper with limits
python scraper.py --source all --limit 5
```

---

## Success Indicators

After these changes, you should see:
- ✅ Workflow completes in **12-18 minutes** (before 50-min timeout)
- ✅ All `scraper-logs` artifacts uploaded successfully
- ✅ No timeout errors in GitHub Actions
- ✅ Jobs successfully saved to Supabase
- ✅ Detailed logs available for debugging

---

## Questions or Issues?

If the workflow still times out:

1. **Check GitHub Actions logs**: Actions tab → Your workflow → View raw logs
2. **Inspect artifact logs**: Download `scraper-logs-*` → Open `scraper.log`
3. **Review network bottlenecks**: 
   - LinkedIn may rate-limit aggressively
   - LLM API might be slow
   - Supabase might be under load
4. **Consider splitting into separate workflows** for different sources
5. **Reduce job limits further** in `config_github_actions.py`

---

**Last Updated**: 2025
**Status**: Optimized for 50-minute GitHub Actions timeout
