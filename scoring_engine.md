Build a Python job-matching pipeline that scores a job description against a candidate profile. It runs a deterministic heuristic first and calls an LLM only when the heuristic result is not good enough. The LLM only proposes skills. It never writes to the vocabulary.

## Context

The project already has these modules. Reuse them and do not change their matching logic:
- `section_splitter.split_sections(markdown)` returns sections (requirements, responsibilities, nice_to_have, benefits, about_company, other) and `method` ("headings" or "none").
- `SpacySkillExtractor.extract(text)` returns matched skills with canonical names and categories, from `skills.txt`.
- `LLMSkillExtractor.extract(description, known_skills)` returns an ExtractionResult with `status`, `skills` (name, level: mandatory|preferred|optional|unspecified, evidence, confidence), and `warnings`. It never raises.
- `skills.txt` is the approved vocabulary. It is read-only for this pipeline.

## Pipeline (fixed order, no agent loop)

Stage 1: Heuristic
1. Split the cleaned description into sections.
2. Extract skills from the requirements section (must-have) and the nice_to_have section (preferred). If the split is "none", extract from the full text and mark all skills as unspecified.
3. Score against the profile (Stage 2).

Stage 2: Score (pure function, no I/O)
- Normalize skill names: trim, lowercase, collapse spaces.
- Weights: mandatory = 2, preferred = 1, unspecified = 1.
- `ats_score` = round(100 × sum of weights of job skills present in the profile ÷ sum of weights of all job skills). Return 0 if the job has no skills.
- `mandatory_missing` = job mandatory skills not in the profile.
- Gate passes only if `ats_score >= ATS_THRESHOLD` AND `mandatory_missing` is empty.
- If there are no job skills at all, the gate fails and the LLM runs.

Stage 3: LLM fallback (only if the gate fails and LLM is enabled)
- Pass the description and the skills already found as known_skills.
- Accept only skills with status "ok" or "partial".
- Map each LLM skill name through the vocabulary alias map. If it matches a vocabulary entry, use the canonical name. If not, keep the LLM name and flag it as `new`.
- Merge into the job's skill set. A skill already found by the heuristic keeps the heuristic's name, and the LLM level replaces "unspecified" only.
- For each `new` skill, call `candidates.record_candidate(phrase, job_id, evidence)`. This writes to `skills_pending.json` only. Never write to `skills.txt`.

Stage 4: Re-score
- Run Stage 2 again on the merged skill set.
- Return the final result, whether the gate passes or not.

## Output

Return a dataclass `MatchResult`:
- `job_id`, `ats_score` (int 0–100), `gate_passed` (bool)
- `mandatory_missing` (list of names)
- `missing_skills` (list of names, all job skills not in profile)
- `matched_skills` (list of names)
- `skills`: list of {name, requirement, source: "heuristic" | "llm" | "both", is_new_candidate: bool}
- `path`: "heuristic_only" | "llm_rescored" | "llm_failed" | "llm_disabled"
- `data_quality`: "high" if section_method is "headings" and the job has at least 3 skills; otherwise "low"
- `warnings`: list of strings

Also expose `to_dict()` so the result can be printed as JSON or stored.

## Configuration (config.py or a constants block)

- `ATS_THRESHOLD = 70` (placeholder, must be calibrated)
- `MANDATORY_WEIGHT = 2`, `OTHER_WEIGHT = 1`
- `LLM_ENABLED` (bool, from env)
- `PENDING_FILE = "skills_pending.json"`

## Rules

- The LLM never writes to `skills.txt` or `skills_rejected.txt`.
- If the LLM call fails, is disabled, or returns "failed" or "skipped", return the heuristic result with the matching path. Never raise to the caller.
- Only LLM skills with grounded evidence are accepted. This is enforced by the extractor. Do not bypass it.
- Do not use an agent framework. The control flow is the fixed sequence above.
- Keep the scoring module free of I/O and LLM imports, so it stays deterministic and testable.
- Use logging, not print, except in the CLI.
- Python 3.11+, type hints, docstrings, standard library plus pytest for tests.

## Tests

- Scoring: full match = 100; no skills = 0; partial match with mandatory weight; mandatory missing fails the gate even when the score is above the threshold; case-insensitive matching; duplicate skills counted once.
- Pipeline with fake extractors:
  - heuristic passes the gate → LLM not called, path "heuristic_only";
  - heuristic fails → LLM called, new skills recorded as candidates, path "llm_rescored";
  - LLM returns "failed" → path "llm_failed", heuristic result returned;
  - LLM disabled → path "llm_disabled", LLM not called;
  - LLM skill matching a vocabulary alias → canonical name used, not a candidate.
- Candidates: recording the same phrase twice increments times_seen; a phrase in skills.txt is not recorded; a rejected phrase is not recorded; the file is unchanged after a simulated crash before os.replace.

## Deliverables

- The files above with working code.
- A README section with the run command, how to read the output, and how to calibrate ATS_THRESHOLD by scoring 20–30 hand-labelled postings and comparing the gate decisions.
- A list of anything not verified, such as live LLM behavior or real profile data.