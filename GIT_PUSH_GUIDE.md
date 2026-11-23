# 📦 Git Push Guide - What to Commit

This guide helps you decide what files to push to your Git repository and what to keep local.

---

## ✅ Files to PUSH (Essential for Repository)

### Core Application Files
```
✅ scraper.py                    # Main scraper orchestrator
✅ config.py                     # Configuration settings
✅ models.py                     # Data models
✅ requirements.txt              # Python dependencies
✅ .gitignore                    # Git ignore rules
✅ README.md                     # Project documentation
✅ AGENT.md                      # AI agent documentation
✅ LICENSE                       # License file
```

### Skill Extraction System
```
✅ skills_manager.py             # Skill database manager
✅ spacy_extractor.py            # spaCy skill extraction
✅ llm_skill_extractor.py        # LLM skill extraction
✅ skill_extraction_service.py   # Skill extraction orchestrator
✅ skill_discovery.py            # New skill discovery
✅ skill_schema.py               # Skill data models
✅ skills.py                     # Skill master data (reference)
```

### Job Scoring System
```
✅ job_scorer.py                 # Job scoring engine
✅ profile_scorer.py             # Profile-based scoring
✅ scoring_orchestrator.py       # Scoring orchestrator
✅ section_splitter.py           # Resume section parser
```

### Resume Generation
```
✅ custom_resume_generator.py    # Resume customization
✅ pdf_generator.py              # PDF generation
✅ resume_parser.py              # Resume parsing
```

### Database & Storage
```
✅ supabase_utils.py             # Supabase utilities
✅ cache_manager.py              # Prompt caching
```

### LLM & AI
```
✅ llm_client.py                 # Universal LLM client
```

### Utilities
```
✅ user_agents.py                # User agent rotation
✅ job_manager.py                # Job management
```

### GitHub Actions
```
✅ .github/workflows/daily-scraper.yml  # Daily scraper workflow
```

### Database Setup Scripts
```
✅ supabase_setup/init.sql                      # Initial setup
✅ supabase_setup/create_skills_table.sql       # Skills table
✅ supabase_setup/add_job_matches_table.sql     # Job matches table
✅ supabase_setup/add_profile_scoring.sql       # Profile scoring
✅ supabase_setup/phase1_user_profiles.sql      # User profiles
✅ supabase_setup/seed_core_skills.sql          # Seed skills
✅ supabase_setup/fix_rls_policies.sql          # RLS policies
✅ supabase_setup/MIGRATION_GUIDE.sql           # Migration guide
```

### Documentation
```
✅ GITHUB_ACTIONS_STEP_BY_STEP.md      # Step-by-step setup
✅ GITHUB_ACTIONS_CRON_SETUP.md        # Cron setup guide
✅ GITHUB_ACTIONS_QUICK_REFERENCE.md   # Quick reference
✅ ARCHITECTURE_Q_AND_A.md             # Architecture decisions
✅ scoring_engine.md                   # Scoring algorithm
✅ SECTION_SPLITTER_EXPLAINED.md       # Resume parsing
✅ SPACY_EXTRACTOR_DATABASE_UPDATE.md  # Skill extraction
✅ RLS_FIX_GUIDE.md                    # RLS fixes
✅ SQL_FIX_SUMMARY.md                  # SQL fixes
✅ SKILLS_MIGRATION_FIX_COMPLETE.md    # Skills migration
✅ SKILLS_FIX_QUICK_REFERENCE.md       # Quick skills fix
✅ JOB_MATCHES_COLUMN_EXPLANATION_SUMMARY.md  # Job matches
```

### Test Files
```
✅ test_skills_migration.py        # Skill migration tests
✅ test_supabase_connection.py     # Database tests
✅ test_job_scorer.py              # Scoring tests
✅ test_llm_skill_extractor.py     # LLM extraction tests
✅ test_cache_phase1.py            # Cache tests
✅ test_multi_user_scoring.py      # Multi-user tests
✅ test_profiles_setup.py          # Profile setup tests
✅ test_rls_fix.py                 # RLS fix tests
✅ test_customizer_stages.py       # Customizer tests
✅ create_test_profiles.py         # Test profile creation
```

---

## ❌ Files to KEEP LOCAL (Do NOT Push)

### Environment & Secrets
```
❌ .env                          # Environment variables (NEVER COMMIT)
❌ *.env                         # Any environment files
❌ .env.local                    # Local environment
❌ .env.*.local                  # Environment variants
```

### Virtual Environments
```
❌ .venv/                        # Virtual environment
❌ .venv-1/                      # Another virtual environment
❌ venv/                         # Virtual environment
❌ ENV/                          # Virtual environment
```

### Python Cache
```
❌ __pycache__/                  # Python cache
❌ *.pyc                         # Compiled Python
❌ *.pyo                         # Optimized Python
❌ *.pyd                         # Python DLL
❌ .pytest_cache/                # Pytest cache
```

### IDE & Editor Files
```
❌ .vscode/                      # VS Code settings
❌ .idea/                        # PyCharm settings
❌ *.swp                         # Vim swap files
❌ *.swo                         # Vim swap files
❌ *~                            # Backup files
```

### OS Files
```
❌ .DS_Store                     # macOS metadata
❌ Thumbs.db                     # Windows thumbnails
❌ desktop.ini                   # Windows settings
```

### Logs & Temporary Files
```
❌ *.log                         # Log files
❌ logs/                         # Log directory
❌ tmp/                          # Temporary files
❌ temp/                         # Temporary files
❌ *.tmp                         # Temporary files
❌ *.bak                         # Backup files
```

### Data Files
```
❌ data/                         # Data directory
❌ *.db                          # Database files
❌ *.sqlite                      # SQLite databases
❌ resume.json                   # Resume data
❌ resume.pdf                    # Resume PDF
❌ test_resume.pdf               # Test resume
```

### Cache Directories
```
❌ .cache/                       # Cache directory
❌ npm_cache/                    # NPM cache
❌ *.cache                       # Cache files
```

### Node.js (if not using)
```
❌ node_modules/                 # Node modules
❌ package-lock.json             # NPM lock file (if not using Node)
❌ package.json                  # NPM config (if not using Node)
```

### Binary Documents
```
❌ bindoc/                       # Binary documents
```

### Local Configuration
```
❌ config_phase1.py              # Phase 1 config (if experimental)
❌ job_hunt_harness.txt          # Personal notes
❌ preferred_skills.txt          # Personal preferences
```

---

## 🔧 Git Commands

### Check What Will Be Committed
```bash
git status
```

### Stage All Appropriate Files
```bash
# Add all files (gitignore will exclude unwanted files)
git add .

# Or add specific files
git add scraper.py config.py models.py requirements.txt
git add .github/workflows/daily-scraper.yml
git add README.md AGENT.md
git add supabase_setup/
git add test_*.py
```

### Commit Changes
```bash
git commit -m "Add job scraper with AI-powered skill extraction and matching

Features:
- Multi-source job scraping (LinkedIn, CareersFuture)
- AI-powered skill extraction (spaCy + LLM)
- Intelligent job matching and scoring
- Automated resume customization
- GitHub Actions daily automation
- Comprehensive test suite
- Complete documentation"
```

### Push to GitHub
```bash
# Push to main branch
git push origin main

# Or if using master branch
git push origin master
```

---

## 📋 Pre-Push Checklist

Before pushing, verify:

- [ ] `.env` is in `.gitignore` and NOT committed
- [ ] Virtual environments (`.venv/`, `.venv-1/`) are NOT committed
- [ ] `__pycache__/` is NOT committed
- [ ] Log files (`*.log`) are NOT committed
- [ ] Personal data files are NOT committed
- [ ] All sensitive information is removed
- [ ] README.md is up to date
- [ ] AGENT.md is created
- [ ] requirements.txt is complete
- [ ] GitHub Actions workflow is configured
- [ ] All tests pass locally

---

## 🔍 Verify Before Pushing

### Check for Sensitive Data
```bash
# Search for potential secrets
grep -r "api_key" --exclude-dir=.git .
grep -r "password" --exclude-dir=.git .
grep -r "secret" --exclude-dir=.git .

# Check if .env is tracked
git ls-files | grep .env
```

### Verify .gitignore
```bash
# Check what git is ignoring
git status --ignored

# Test if a file is ignored
git check-ignore -v .env
```

### Review Changes
```bash
# See what will be committed
git diff --cached

# See what files will be committed
git diff --cached --name-only
```

---

## 🚀 Quick Push Commands

### First Time Setup
```bash
# Initialize git (if not already)
git init

# Add remote repository
git remote add origin https://github.com/yourusername/job-scraper.git

# Add all files
git add .

# Commit
git commit -m "Initial commit: Job scraper with AI-powered matching"

# Push
git push -u origin main
```

### Subsequent Pushes
```bash
# Add changes
git add .

# Commit
git commit -m "Update: [describe changes]"

# Push
git push
```

---

## 📊 Repository Size

### Check Repository Size
```bash
# Check size before pushing
du -sh .git

# Check largest files
git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | awk '/^blob/ {print substr($0,6)}' | sort --numeric-sort --key=2 | tail -10
```

### Reduce Repository Size
```bash
# Remove large files from history (if needed)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch PATH-TO-LARGE-FILE" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (use with caution)
git push origin --force --all
```

---

## 🆘 Troubleshooting

### Issue: Accidentally Committed .env
```bash
# Remove from git but keep locally
git rm --cached .env

# Add to .gitignore
echo ".env" >> .gitignore

# Commit
git commit -m "Remove .env from git"

# Push
git push
```

### Issue: Accidentally Committed Large Files
```bash
# Remove from git
git rm --cached large-file.zip

# Add to .gitignore
echo "large-file.zip" >> .gitignore

# Commit
git commit -m "Remove large file"

# Push
git push
```

### Issue: Need to Remove File from History
```bash
# Use BFG Repo-Cleaner (recommended)
brew install bfg
bfg --delete-files large-file.zip
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force
```

---

## 📞 Need Help?

- **Git Documentation**: https://git-scm.com/doc
- **GitHub Guides**: https://guides.github.com/
- **Git Ignore Generator**: https://www.toptal.com/developers/gitignore

---

**Last Updated**: November 23, 2026  
**Status**: Ready to Push ✅
