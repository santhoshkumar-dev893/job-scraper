# GitHub Actions Cron Job Setup Guide
## Automated Daily Job Scraper Execution

This guide will help you set up a GitHub Actions workflow to run your job scraper automatically every day.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Understanding GitHub Actions Cron](#understanding-github-actions-cron)
3. [Step-by-Step Setup](#step-by-step-setup)
4. [Workflow Configuration](#workflow-configuration)
5. [Environment Variables & Secrets](#environment-variables--secrets)
6. [Testing the Workflow](#testing-the-workflow)
7. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
8. [Advanced Configurations](#advanced-configurations)
9. [Cost Considerations](#cost-considerations)
10. [Best Practices](#best-practices)

---

## Prerequisites

Before setting up the cron job, ensure you have:

- ✅ A GitHub repository with your job scraper code
- ✅ All required environment variables (API keys, database credentials)
- ✅ A working `requirements.txt` file
- ✅ Your scraper runs successfully locally
- ✅ GitHub account with Actions enabled (free tier includes 2,000 minutes/month)

---

## Understanding GitHub Actions Cron

### What is a Cron Job?
A cron job is a scheduled task that runs automatically at specified intervals. GitHub Actions uses cron syntax to schedule workflows.

### Cron Syntax Format
```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday to Saturday)
│ │ │ │ │
│ │ │ │ │
* * * * *
```

### Common Cron Schedules
| Schedule | Cron Expression | Description |
|----------|----------------|-------------|
| Daily at midnight | `0 0 * * *` | Runs at 12:00 AM UTC every day |
| Daily at 6 AM | `0 6 * * *` | Runs at 6:00 AM UTC every day |
| Every 6 hours | `0 */6 * * *` | Runs at 12 AM, 6 AM, 12 PM, 6 PM UTC |
| Weekdays at 9 AM | `0 9 * * 1-5` | Runs Monday-Friday at 9:00 AM UTC |
| Every Monday at 8 AM | `0 8 * * 1` | Runs every Monday at 8:00 AM UTC |

**Note:** GitHub Actions uses **UTC time zone**. Convert your local time to UTC.

---

## Step-by-Step Setup

### Step 1: Create Workflow Directory

Create the GitHub Actions workflow directory in your repository:

```bash
mkdir -p .github/workflows
```

### Step 2: Create Workflow File

Create a new file `.github/workflows/daily-scraper.yml`:

```yaml
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

jobs:
  scrape-jobs:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'
          cache: 'pip'
      
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
          python scraper.py --source ${{ github.event.inputs.source || 'all' }} --limit ${{ github.event.inputs.limit || '50' }}
      
      - name: Upload logs
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: scraper-logs-${{ github.run_number }}
          path: |
            *.log
            logs/
          retention-days: 30
```

---

## Workflow Configuration

### Basic Daily Schedule

For a simple daily run at midnight UTC:

```yaml
on:
  schedule:
    - cron: '0 0 * * *'
```

### Multiple Daily Runs

To run multiple times per day:

```yaml
on:
  schedule:
    - cron: '0 6 * * *'   # 6 AM UTC
    - cron: '0 18 * * *'  # 6 PM UTC
```

### Weekday-Only Schedule

To run only on weekdays:

```yaml
on:
  schedule:
    - cron: '0 6 * * 1-5'  # Monday-Friday at 6 AM UTC
```

### Manual Trigger with Parameters

Add `workflow_dispatch` to enable manual runs with custom parameters:

```yaml
on:
  workflow_dispatch:
    inputs:
      source:
        description: 'Job source'
        required: true
        default: 'all'
      query:
        description: 'Search query'
        required: false
      limit:
        description: 'Job limit'
        required: false
        default: '50'
```

---

## Environment Variables & Secrets

### Step 1: Add Secrets to GitHub Repository

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each of the following secrets:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `SUPABASE_URL` | Your Supabase project URL | `https://xxxxx.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `LLM_API_KEY` | Your LLM API key (Fireworks/OpenAI) | `fw_xxxxxxxxxxxxx` |
| `FIREWORKS_API_KEY` | Fireworks AI API key (if using) | `fw_xxxxxxxxxxxxx` |
| `LLM_MODEL` | LLM model name | `fireworks_ai/accounts/fireworks/models/glm-5p3-flash` |

### Step 2: Reference Secrets in Workflow

```yaml
env:
  SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
  SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
  LLM_API_KEY: ${{ secrets.LLM_API_KEY }}
```

### Step 3: Optional Environment Variables

For non-sensitive configuration, use environment variables:

```yaml
env:
  LINKEDIN_LOCATION: "India"
  LINKEDIN_JOB_TYPE: "F"
  LINKEDIN_JOB_POSTING_DATE: "r86400"
```

---

## Testing the Workflow

### Test 1: Manual Trigger

1. Go to **Actions** tab in your GitHub repository
2. Select **Daily Job Scraper** workflow
3. Click **Run workflow**
4. Select branch and parameters
5. Click **Run workflow** button

### Test 2: Verify Cron Schedule

Check when your next scheduled run will occur:

```bash
# Install croniter (optional)
pip install croniter

# Check next run time
python3 -c "from croniter import croniter; from datetime import datetime; print(croniter('0 6 * * *', datetime.now()).get_next(datetime))"
```

### Test 3: Dry Run Locally

Test the workflow steps locally before pushing:

```bash
# Simulate the workflow environment
export SUPABASE_URL="your_url"
export SUPABASE_SERVICE_ROLE_KEY="your_key"
export LLM_API_KEY="your_key"

# Run the scraper
python3 scraper.py --source all --limit 10
```

---

## Monitoring & Troubleshooting

### View Workflow Runs

1. Go to **Actions** tab
2. Click on a workflow run to see details
3. View logs for each step

### Common Issues & Solutions

#### Issue 1: Workflow Not Running on Schedule

**Problem:** Cron job doesn't trigger automatically

**Solutions:**
- ✅ Ensure the workflow file is in the **default branch** (usually `main` or `master`)
- ✅ Check that the cron syntax is correct
- ✅ Verify GitHub Actions is enabled for your repository
- ✅ Note: Scheduled workflows may be delayed during high GitHub Actions usage

#### Issue 2: Secrets Not Found

**Problem:** `Error: Secret SUPABASE_URL not found`

**Solutions:**
- ✅ Verify secrets are added in repository settings
- ✅ Check secret names match exactly (case-sensitive)
- ✅ Ensure you're using `${{ secrets.SECRET_NAME }}` syntax

#### Issue 3: Python Dependencies Fail

**Problem:** `pip install` fails

**Solutions:**
```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install --no-cache-dir -r requirements.txt
```

#### Issue 4: spaCy Model Not Found

**Problem:** `OSError: Can't find model 'en_core_web_sm'`

**Solutions:**
```yaml
- name: Download spaCy model
  run: |
    python -m spacy download en_core_web_sm
    # Or use direct download
    pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
```

#### Issue 5: Timeout Errors

**Problem:** Workflow times out (default: 6 hours)

**Solutions:**
```yaml
jobs:
  scrape-jobs:
    runs-on: ubuntu-latest
    timeout-minutes: 30  # Set custom timeout
```

### Enable Debug Logging

Add debug logging to troubleshoot issues:

```yaml
- name: Run job scraper
  env:
    ACTIONS_STEP_DEBUG: true
    ACTIONS_RUNNER_DEBUG: true
  run: |
    python scraper.py --source all --limit 50
```

---

## Advanced Configurations

### 1. Matrix Strategy (Multiple Python Versions)

Test across multiple Python versions:

```yaml
jobs:
  scrape-jobs:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12', '3.13']
    
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
```

### 2. Conditional Execution

Run only if changes detected:

```yaml
jobs:
  check-changes:
    runs-on: ubuntu-latest
    outputs:
      should_run: ${{ steps.check.outputs.should_run }}
    steps:
      - name: Check if should run
        id: check
        run: |
          # Your logic here
          echo "should_run=true" >> $GITHUB_OUTPUT
  
  scrape-jobs:
    needs: check-changes
    if: needs.check-changes.outputs.should_run == 'true'
    runs-on: ubuntu-latest
    steps:
      # ... scraping steps
```

### 3. Notifications on Failure

Send notifications when workflow fails:

```yaml
- name: Send notification on failure
  if: failure()
  uses: actions/github-script@v7
  with:
    script: |
      github.rest.issues.create({
        owner: context.repo.owner,
        repo: context.repo.repo,
        title: 'Job Scraper Failed',
        body: 'The daily job scraper workflow failed. Check the logs.',
        labels: ['bug', 'automation']
      })
```

### 4. Slack Notifications

```yaml
- name: Notify Slack
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'Job scraper completed'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### 5. Cache Dependencies

Speed up workflow by caching dependencies:

```yaml
- name: Cache pip dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

### 6. Artifact Upload

Save scraped data as artifacts:

```yaml
- name: Upload scraped data
  uses: actions/upload-artifact@v4
  with:
    name: scraped-jobs-${{ github.run_number }}
    path: |
      data/
      logs/
    retention-days: 30
```

### 7. Database Backup

Backup database before scraping:

```yaml
- name: Backup database
  run: |
    python scripts/backup_database.py
```

---

## Cost Considerations

### GitHub Actions Free Tier

- **Public repositories:** Unlimited minutes
- **Private repositories:** 2,000 minutes/month free
- **Storage:** 500 MB for artifacts

### Estimated Usage

For a daily scraper run:
- **Average run time:** 5-10 minutes
- **Monthly usage:** 150-300 minutes
- **Cost:** FREE (within free tier)

### Optimization Tips

1. **Use caching** to reduce dependency installation time
2. **Limit job count** to reduce execution time
3. **Use concurrency** to cancel outdated runs:

```yaml
concurrency:
  group: daily-scraper
  cancel-in-progress: true
```

---

## Best Practices

### 1. Error Handling

Always handle errors gracefully:

```yaml
- name: Run scraper
  continue-on-error: true
  run: python scraper.py

- name: Check exit code
  if: failure()
  run: echo "Scraper failed but continuing..."
```

### 2. Logging

Implement comprehensive logging:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
```

### 3. Rate Limiting

Respect API rate limits:

```python
import time

# Add delays between requests
time.sleep(2)  # 2 seconds between requests
```

### 4. Data Validation

Validate scraped data before saving:

```python
def validate_job(job):
    required_fields = ['job_id', 'title', 'company']
    return all(field in job for field in required_fields)
```

### 5. Monitoring

Set up monitoring and alerts:

```yaml
- name: Health check
  run: |
    python scripts/health_check.py
```

### 6. Version Control

Keep workflow file in version control:

```bash
git add .github/workflows/daily-scraper.yml
git commit -m "Add daily scraper workflow"
git push
```

---

## Complete Example Workflow

Here's a production-ready workflow file:

```yaml
name: Daily Job Scraper

on:
  schedule:
    - cron: '0 6 * * *'  # 6 AM UTC daily
  workflow_dispatch:
    inputs:
      source:
        description: 'Job source'
        required: false
        default: 'all'
        type: choice
        options: [all, linkedin, careers_future]
      limit:
        description: 'Max jobs per query'
        required: false
        default: '50'

env:
  PYTHON_VERSION: '3.13'

jobs:
  scrape:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    
    concurrency:
      group: daily-scraper
      cancel-in-progress: false
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup Python
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
        run: python -m spacy download en_core_web_sm
      
      - name: Run scraper
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
          name: logs-${{ github.run_number }}
          path: '*.log'
          retention-days: 30
      
      - name: Notify on failure
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `Scraper Failed - ${new Date().toISOString()}`,
              body: 'Check workflow logs for details',
              labels: ['automation', 'bug']
            })
```

---

## Quick Start Checklist

- [ ] Create `.github/workflows/` directory
- [ ] Create `daily-scraper.yml` workflow file
- [ ] Add all required secrets to GitHub repository
- [ ] Test workflow manually using `workflow_dispatch`
- [ ] Verify cron schedule is correct
- [ ] Monitor first few automated runs
- [ ] Set up notifications for failures
- [ ] Document any custom configurations

---

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Cron Syntax Reference](https://crontab.guru/)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)

---

## Support

If you encounter issues:

1. Check the **Actions** tab for error logs
2. Review this guide's troubleshooting section
3. Enable debug logging for detailed output
4. Test locally first before pushing to GitHub

---

**Last Updated:** November 22, 2026  
**Version:** 1.0  
**Status:** Production Ready ✅
