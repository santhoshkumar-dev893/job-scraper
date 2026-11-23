# Summary: Heuristic Skills Extraction - Your Questions Answered

## Question 1: Where does section_splitter happen?

### Answer: Line 121 in job_scorer.py

```python
def _extract_heuristic_skills(self, job_description: str) -> List[SkillMatch]:
    try:
        # LINE 121: This is where section_splitter is called
        sections, split_method = self.section_splitter.split_sections(job_description)
```

**What it does:**
- Takes the full job description text
- Attempts to identify sections (Requirements, Nice-to-Have, Responsibilities, etc.)
- Returns a dictionary of sections and how it split them

**What it returns:**
```python
sections = {
    "requirements": "Python, React, Node.js",
    "nice_to_have": "Docker, Kubernetes",
    "responsibilities": "Build APIs",
    ...
}

split_method = "headings"  # or "fallback"
```

---

## Question 2: What if LinkedIn JD has NO Requirements and Nice_to_Have sections?

### Answer: GRACEFUL FALLBACK - No error, but quality degrades

**The Code (Lines 155-169):**
```python
else:
    # No sections found, extract from full text with unspecified
    data_quality = DataQuality.LOW  # ← Mark as low quality
    for spacy_skill in self.spacy_extractor.extract(job_description):
        extracted_skills.append(SkillMatch(
            name=spacy_skill.name,
            requirement="unspecified",  # ← ALL skills marked this way
            source="heuristic"
        ))
```

**What Happens:**
1. ✅ Spacy still extracts all skills from the full text
2. ✅ No exception thrown, system continues
3. ⚠️ All extracted skills are marked as "unspecified" (not mandatory/preferred)
4. ⚠️ data_quality is set to "LOW"
5. ℹ️ Scoring weight decreases (unspecified=1 vs mandatory=2)

---

## Example Walkthrough: LinkedIn Unstructured JD

### Input: A typical LinkedIn job post
```
"Senior Python Developer

Looking for a developer with Python experience and React knowledge.
We use Docker and Kubernetes. AWS experience is nice to have.

You'll build scalable systems and mentor team members.
We offer health insurance, 401k, and remote work."
```

### What Happens:

**Step 1: section_splitter tries to parse**
```python
sections, split_method = section_splitter.split_sections(text)

# Result: 
# - Couldn't find clear "Requirements:" or "Nice to Have:" headers
# - sections = {} (empty)
# - split_method = "fallback"
```

**Step 2: Check if sections exist**
```python
if sections:
    # This doesn't execute (sections is empty)
else:
    # This executes
    data_quality = DataQuality.LOW
    # Extract from full text...
```

**Step 3: Extract skills from full text**
```python
# Spacy finds all skill mentions in the text
for spacy_skill in spacy_extractor.extract(job_description):
    extracted_skills.append(SkillMatch(
        name=spacy_skill.name,
        requirement="unspecified",  # ← All are unspecified!
        source="heuristic"
    ))

# Results:
# - Python → "unspecified" (Spacy doesn't know it's mandatory)
# - React → "unspecified"
# - Docker → "unspecified"
# - Kubernetes → "unspecified"
# - AWS → "unspecified"
```

**Step 4: Return results**
```python
return [
    SkillMatch("Python", "unspecified", "heuristic"),
    SkillMatch("React", "unspecified", "heuristic"),
    SkillMatch("Docker", "unspecified", "heuristic"),
    SkillMatch("Kubernetes", "unspecified", "heuristic"),
    SkillMatch("AWS", "unspecified", "heuristic"),
]

# Plus: data_quality = "LOW"
```

---

## Impact on Scoring

### Profile: Has Python, React, Docker

**If JD was well-structured:**
```
Requirements: Python, React, Kubernetes
Preferred: Docker, AWS

After matching:
- matched: Python, React, Docker (3 skills)
- mandatory_missing: Kubernetes (1)
- ats_score = 2*3 (mandatory matched) + 1*1 (preferred matched) = ~85
- gate_passed = TRUE (only 1 mandatory missing out of 3)
```

**If JD was unstructured (LinkedIn):**
```
All skills unspecified: Python, React, Docker, Kubernetes, AWS

After matching:
- matched: Python, React, Docker (3 skills)
- mandatory_missing: [] (EMPTY! Nothing is mandatory)
- ats_score = 1*3 (unspecified matched) = ~60
- gate_passed = TRUE (automatically, no mandatory skills to fail)
```

**Key Difference:**
- Structured: Score 85, confident matching
- Unstructured: Score 60, less confident, but still passes gate

---

## Why This Design?

### Problem it Solves:
1. Job descriptions vary wildly in structure
2. Some have clear "Requirements" headers, some don't
3. Can't always parse perfectly

### Solution:
1. Try to parse sections (best effort)
2. If successful, categorize skills by section
3. If fails, extract from full text as "unspecified"
4. Flag data quality so you know confidence level
5. Let LLM fallback fix low-quality extractions

### Benefits:
✅ Never crashes on bad data
✅ Gracefully degrades quality
✅ Provides quality flag for downstream use
✅ Enables LLM to enhance results

---

## What to Know About section_splitter

### The Real Implementation (in production):
Would use heuristics to find:
- Common headers: "Requirements", "What we're looking for", "Must have"
- Preferred headers: "Nice to have", "Preferred", "Bonus"
- Other headers: "Responsibilities", "About company", "Benefits"

### The Test Implementation:
```python
class MockSectionSplitter:
    def split_sections(self, text):
        return {
            "requirements": "Python JavaScript React",
            "nice_to_have": "Docker Kubernetes",
            "responsibilities": "Build scalable apps",
            "about_company": "Tech startup",
        }, "headings"
```

---

## Summary Table

| Scenario | Section Found? | data_quality | Skills Categorized | Impact |
|----------|---|---|---|---|
| Well-structured JD | ✅ YES | HIGH | By section (mandatory/preferred/unspec) | Accurate scoring |
| Unstructured JD | ❌ NO | LOW | ALL unspecified | Lower scores, easier gate |
| LinkedIn post | ❌ NO | LOW | ALL unspecified | Still works, just less accurate |

---

## Key Takeaways

### 1. section_splitter happens at LINE 121
```python
sections, split_method = self.section_splitter.split_sections(job_description)
```

### 2. If no sections, it falls back (lines 155-169)
- Doesn't crash
- Extracts all skills as "unspecified"
- Sets data_quality to "LOW"

### 3. This is by design
- Handles both structured and unstructured JDs
- Graceful degradation of quality
- LLM can fix low-quality results later

### 4. You can check quality
- Look at `result.data_quality`
- If "LOW", consider running LLM fallback
- Combine results for best accuracy

---

## Files Created for Reference

1. **HEURISTIC_EXTRACTION_EXPLAINED.md** - Deep dive explanation
2. **HEURISTIC_EXTRACTION_QUICK_REFERENCE.md** - TL;DR version
3. **HEURISTIC_EXTRACTION_CODE_FLOW.md** - Complete code walkthrough with examples

All explain the same thing from different angles!
