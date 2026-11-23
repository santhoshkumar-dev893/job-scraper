# GitHub Actions Setup - Step-by-Step Guide
## Linear Setup Instructions for Daily Job Scraper

This guide provides **exact step-by-step instructions** to set up your GitHub Actions cron job. Follow each step in order.

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] GitHub account
- [ ] Repository with your job scraper code
- [ ] Supabase account and credentials
- [ ] LLM API key (Fireworks/OpenAI/etc.)
- [ ] Code pushed to GitHub repository

---

## 🎯 Step 1: Prepare Your Repository

### 1.1 Verify Repository Structure

Your repository should have this structure:
```
job-scraper/
├── .github/
│   └── workflows/
│       └── daily-scraper.yml
├── scraper.py
├── config.py
├── requirements.txt
├── .env (DO NOT COMMIT)
└── ... other files
```

### 1.2 Create .gitignore (if not exists)

Create or update `.gitignore` to exclude sensitive files:

```bash
# Create .gitignore
cat > .gitignore << 'EOF'
# Environment variables
.env
*.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv*/
venv/
ENV/
env/

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Data
data/
*.db
*.sqlite

# Cache
.cache/
*.cache
EOF
```

### 1.3 Verify requirements.txt

Ensure your `requirements.txt` is up to date:

```bash
# Check current requirements
cat requirements.txt

# Should contain:
# requests
# beautifulsoup4
# python-dotenv
# supabase
# httpx
# pdfplumber
# pypdfium2
# reportlab
# litellm
# pydantic
# spacy
# markdownify
# pytest
```

---

## 🔐 Step 2: Set Up GitHub Secrets

### 2.1 Navigate to Secrets Settings

1. Go to your GitHub repository
2. Click **Settings** (top menu)
3. Click **Secrets and variables** (left sidebar)
4. Click **Actions**

### 2.2 Add Required Secrets

Click **New repository secret** for each of the following:

#### Secret 1: SUPABASE_URL
```
Name: SUPABASE_URL
Value: https://your-project.supabase.co
```

#### Secret 2: SUPABASE_SERVICE_ROLE_KEY
```
Name: SUPABASE_SERVICE_ROLE_KEY
Value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Secret 3: LLM_API_KEY
```
Name: LLM_API_KEY
Value: fw_xxxxxxxxxxxxx (or your LLM provider key)
```

#### Secret 4: FIREWORKS_API_KEY (if using Fireworks)
```
Name: FIREWORKS_API_KEY
Value: fw_xxxxxxxxxxxxx
```

#### Secret 5: LLM_MODEL
```
Name: LLM_MODEL
Value: fireworks_ai/accounts/fireworks/models/glm-5p3-flash
```

### 2.3 Verify Secrets

After adding all secrets, you should see:
- ✅ SUPABASE_URL
- ✅ SUPABASE_SERVICE_ROLE_KEY
- ✅ LLM_API_KEY
- ✅ FIREWORKS_API_KEY
- ✅ LLM_MODEL

---

## 📝 Step 3: Create Workflow File

### 3.1 Create Workflow Directory

```bash
# Navigate to your repository
cd /path/to/job-scraper

# Create workflow directory
mkdir -p .github/workflows
```

### 3.2 Create Workflow File

Create `.github/workflows/daily-scraper.yml`:

```bash
cat > .github/workflows/daily-scraper.yml << 'EOF'
name: Daily Job Scraper

on:
  schedule:
    # Runs every day at 6:00 AM UTC (11:30 AM IST)
    - cron: '0 6 * * *'
  
  # Allow manual triggering
  workflow_dispatch:
    inputs:
      source:
        description: 'Job source to scrape'
        required: false
        default: 'all'
        type: choice
        options:
          - all
          - linkedin
          - careers_future
      limit:
        description: 'Maximum jobs per query'
        required: false
        default: '50'
        type: string

env:
  PYTHON_VERSION: '3.13'

jobs:
  scrape-jobs:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    
    concurrency:
      group: daily-scraper
      cancel-in-progress: false
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
      
      - name: Cache spaCy model
        uses: actions/cache@v3
        with:
          path: ~/.cache/spacy
          key: spacy-model-v1
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Download spaCy model
        run: |
          python -m spacy download en_core_web_sm
      
      - name: Run job scraper
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
          LLM_API_KEY: ${{ secrets.LLM_API_KEY }}
          FIREWORKS_API_KEY: ${{ secrets.FIREWORKS_API_KEY }}
          LLM_MODEL: ${{ secrets.LLM_MODEL }}
        run: |
          python scraper.py \
            --source ${{ github.event.inputs.source || 'all' }} \
            --limit ${{ github.event.inputs.limit || '50' }}
      
      - name: Upload logs
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: scraper-logs-${{ github.run_number }}
          path: |
            *.log
            logs/
          retention-days: 30
      
      - name: Notify on failure
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `Job Scraper Failed - ${new Date().toISOString()}`,
              body: 'The daily job scraper workflow failed. Check the logs for details.',
              labels: ['automation', 'bug']
            })
EOF
```

### 3.3 Verify Workflow File

```bash
# Check if file was created
cat .github/workflows/daily-scraper.yml

# Validate YAML syntax (optional)
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/daily-scraper.yml'))"
```

---

## 🧪 Step 4: Test Locally (Optional but Recommended)

### 4.1 Set Environment Variables

```bash
# Create a test script
cat > test_local.sh << 'EOF'
#!/bin/bash

# Set environment variables
export SUPABASE_URL="your_supabase_url"
export SUPABASE_SERVICE_ROLE_KEY="your_service_role_key"
export LLM_API_KEY="your_llm_api_key"
export FIREWORKS_API_KEY="your_fireworks_key"
export LLM_MODEL="fireworks_ai/accounts/fireworks/models/glm-5p3-flash"

# Run scraper
python3 scraper.py --source all --limit 5
EOF

chmod +x test_local.sh
```

### 4.2 Run Test

```bash
# Run the test
./test_local.sh

# Check if it completes successfully
echo "Exit code: $?"
```

---

## 📤 Step 5: Commit and Push to GitHub

### 5.1 Stage Changes

```bash
# Add all files
git add .github/workflows/daily-scraper.yml
git add .gitignore
git add requirements.txt

# Check what will be committed
git status
```

### 5.2 Commit Changes

```bash
# Commit with descriptive message
git commit -m "Add GitHub Actions workflow for daily job scraping

- Add daily-scraper.yml workflow
- Update requirements.txt with all dependencies
- Add .gitignore for sensitive files
- Configure cron schedule for 6 AM UTC daily"
```

### 5.3 Push to GitHub

```bash
# Push to main branch
git push origin main

# Or if using master branch
git push origin master
```

---

## ✅ Step 6: Verify Workflow in GitHub

### 6.1 Check Workflow File

1. Go to your repository on GitHub
2. Navigate to `.github/workflows/daily-scraper.yml`
3. Verify the file is present and correct

### 6.2 Check Actions Tab

1. Click **Actions** tab
2. You should see **Daily Job Scraper** workflow listed
3. If not, wait a few seconds and refresh

---

## 🧪 Step 7: Test Manual Trigger

### 7.1 Trigger Workflow Manually

1. Go to **Actions** tab
2. Click **Daily Job Scraper** workflow
3. Click **Run workflow** button (right side)
4. Select branch (usually `main`)
5. Choose parameters:
   - **Source**: `all`
   - **Limit**: `5` (for testing)
6. Click **Run workflow** button

### 7.2 Monitor Execution

1. Click on the running workflow (yellow dot)
2. Click on **scrape-jobs** job
3. Watch the logs in real-time
4. Wait for completion (usually 2-5 minutes)

### 7.3 Verify Success

Check for:
- ✅ All steps completed successfully (green checkmarks)
- ✅ No error messages in logs
- ✅ "Run job scraper" step shows scraped jobs count

---

## 📊 Step 8: Verify Scheduled Run

### 8.1 Check Next Scheduled Run

The workflow will run automatically at the scheduled time (6:00 AM UTC daily).

To verify the schedule:
1. Go to **Actions** tab
2. Click **Daily Job Scraper** workflow
3. Look for "Scheduled" badge next to future runs

### 8.2 Wait for First Scheduled Run

- The first scheduled run will occur at the next 6:00 AM UTC
- You can check the exact time using: https://crontab.guru/#0_6_*_*_*

---

## 🔍 Step 9: Monitor and Troubleshoot

### 9.1 View Workflow Runs

```bash
# Using GitHub CLI (optional)
gh run list --workflow=daily-scraper.yml

# View specific run
gh run view <run-id>

# View logs
gh run view <run-id> --log
```

### 9.2 Download Artifacts

```bash
# Download logs from a run
gh run download <run-id>
```

### 9.3 Common Issues and Solutions

#### Issue: Workflow not appearing
**Solution:** 
- Ensure workflow file is in `.github/workflows/` directory
- Check file extension is `.yml` or `.yaml`
- Verify YAML syntax is correct

#### Issue: Secrets not found
**Solution:**
- Go to Settings → Secrets and variables → Actions
- Verify all secrets are added
- Check secret names match exactly (case-sensitive)

#### Issue: Python dependencies fail
**Solution:**
```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install --no-cache-dir -r requirements.txt
```

#### Issue: spaCy model not found
**Solution:**
```yaml
- name: Download spaCy model
  run: |
    python -m spacy download en_core_web_sm
```

---

## 🎨 Step 10: Customize Schedule (Optional)

### 10.1 Change Cron Schedule

Edit `.github/workflows/daily-scraper.yml`:

```yaml
on:
  schedule:
    - cron: '0 6 * * *'  # Change this line
```

### 10.2 Common Schedules

| Schedule | Cron Expression | Description |
|----------|----------------|-------------|
| Daily at midnight | `0 0 * * *` | 12:00 AM UTC |
| Daily at 6 AM | `0 6 * * *` | 6:00 AM UTC (11:30 AM IST) |
| Every 12 hours | `0 */12 * * *` | 12 AM and 12 PM UTC |
| Weekdays at 9 AM | `0 9 * * 1-5` | Mon-Fri at 9:00 AM UTC |
| Every Monday | `0 8 * * 1` | Monday at 8:00 AM UTC |

### 10.3 Use Cron Generator

Visit https://crontab.guru/ to create custom schedules.

---

## 📈 Step 11: Add Notifications (Optional)

### 11.1 Slack Notifications

Add to workflow:

```yaml
- name: Notify Slack
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'Job scraper completed'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### 11.2 Email Notifications

GitHub sends email notifications by default for failed workflows.

To configure:
1. Go to GitHub Settings → Notifications
2. Enable "Actions" notifications
3. Choose email preferences

---

## 🔒 Step 12: Security Best Practices

### 12.1 Never Commit Secrets

```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo "*.env" >> .gitignore
```

### 12.2 Use GitHub Secrets

Always use `${{ secrets.SECRET_NAME }}` for sensitive data.

### 12.3 Limit Workflow Permissions

Add to workflow:

```yaml
permissions:
  contents: read
  issues: write  # Only if using issue creation
```

---

## 📊 Step 13: Monitor Costs

### 13.1 Check Usage

1. Go to GitHub Settings → Billing
2. Check "Actions" usage
3. Free tier: 2,000 minutes/month

### 13.2 Estimate Costs

- **Average run time:** 5-10 minutes
- **Daily runs:** 30 runs/month
- **Total usage:** 150-300 minutes/month
- **Cost:** FREE (within free tier)

---

## ✨ Step 14: Optimize Performance

### 14.1 Enable Caching

Already included in workflow:

```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    cache: 'pip'  # Caches pip dependencies
```

### 14.2 Reduce Timeout

```yaml
jobs:
  scrape-jobs:
    timeout-minutes: 15  # Reduce from 30 to 15
```

### 14.3 Limit Job Count

```yaml
- name: Run job scraper
  run: |
    python scraper.py --limit 25  # Reduce from 50
```

---

## 🎉 Completion Checklist

- [ ] Repository structure verified
- [ ] .gitignore created/updated
- [ ] requirements.txt updated
- [ ] All secrets added to GitHub
- [ ] Workflow file created
- [ ] Workflow file committed and pushed
- [ ] Manual trigger tested successfully
- [ ] Scheduled run verified
- [ ] Monitoring set up
- [ ] Notifications configured (optional)
- [ ] Documentation reviewed

---

## 📚 Additional Resources

- **Full Documentation:** `GITHUB_ACTIONS_CRON_SETUP.md`
- **Quick Reference:** `GITHUB_ACTIONS_QUICK_REFERENCE.md`
- **Cron Syntax:** https://crontab.guru/
- **GitHub Actions Docs:** https://docs.github.com/en/actions

---

## 🆘 Need Help?

If you encounter issues:

1. Check the **Actions** tab for error logs
2. Review the troubleshooting section above
3. Verify all secrets are correctly set
4. Test locally first before pushing
5. Check the full documentation in `GITHUB_ACTIONS_CRON_SETUP.md`

---

**Setup Time:** ~15-20 minutes  
**Difficulty:** Beginner-friendly  
**Status:** Production Ready ✅

**Last Updated:** November 23, 2026
