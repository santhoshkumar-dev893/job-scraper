# GitHub Actions Cron - Quick Reference

## 🚀 Quick Setup (5 Minutes)

### 1. Add Secrets to GitHub
Go to: **Repository → Settings → Secrets and variables → Actions → New repository secret**

Add these secrets:
```
SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY
LLM_API_KEY
FIREWORKS_API_KEY
LLM_MODEL
```

### 2. Workflow File Location
```
.github/workflows/daily-scraper.yml
```

### 3. Cron Schedule Examples

| Schedule | Cron Expression | When It Runs |
|----------|----------------|--------------|
| Daily at midnight | `0 0 * * *` | 12:00 AM UTC |
| Daily at 6 AM | `0 6 * * *` | 6:00 AM UTC (11:30 AM IST) |
| Every 12 hours | `0 */12 * * *` | 12 AM and 12 PM UTC |
| Weekdays at 9 AM | `0 9 * * 1-5` | Mon-Fri at 9:00 AM UTC |
| Every Monday | `0 8 * * 1` | Monday at 8:00 AM UTC |

### 4. Manual Trigger
1. Go to **Actions** tab
2. Select **Daily Job Scraper**
3. Click **Run workflow**
4. Choose parameters
5. Click **Run workflow**

### 5. View Logs
1. Go to **Actions** tab
2. Click on a workflow run
3. Click on a job to see logs

---

## 📝 Common Commands

### Test Locally
```bash
# Set environment variables
export SUPABASE_URL="your_url"
export SUPABASE_SERVICE_ROLE_KEY="your_key"
export LLM_API_KEY="your_key"

# Run scraper
python3 scraper.py --source all --limit 10
```

### Check Next Run Time
```bash
# Install croniter
pip install croniter

# Check next run
python3 -c "from croniter import croniter; from datetime import datetime; print(croniter('0 6 * * *', datetime.now()).get_next(datetime))"
```

### Validate Workflow Syntax
```bash
# Install actionlint
brew install actionlint

# Validate workflow
actionlint .github/workflows/daily-scraper.yml
```

---

## 🔧 Troubleshooting

### Workflow Not Running?
- ✅ Check workflow file is in default branch (main/master)
- ✅ Verify cron syntax is correct
- ✅ Ensure GitHub Actions is enabled
- ✅ Wait up to 5 minutes for scheduled runs

### Secrets Not Working?
- ✅ Check secret names match exactly (case-sensitive)
- ✅ Verify secrets are added in repository settings
- ✅ Use `${{ secrets.SECRET_NAME }}` syntax

### Dependencies Failing?
```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install --no-cache-dir -r requirements.txt
```

### spaCy Model Not Found?
```yaml
- name: Download spaCy model
  run: python -m spacy download en_core_web_sm
```

---

## 💡 Pro Tips

1. **Use caching** to speed up workflows
2. **Set timeout** to prevent hanging jobs
3. **Enable notifications** for failures
4. **Test manually** before relying on schedule
5. **Monitor costs** (2,000 free minutes/month)

---

## 📊 Monitoring

### View Workflow Status
```bash
# Using GitHub CLI
gh run list --workflow=daily-scraper.yml
gh run view <run-id>
```

### Download Artifacts
```bash
gh run download <run-id>
```

---

## 🔗 Useful Links

- [Cron Syntax Generator](https://crontab.guru/)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)

---

**Need Help?** Check the full guide: `GITHUB_ACTIONS_CRON_SETUP.md`
