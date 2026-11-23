"""
Deterministic skill extraction using spaCy's PhraseMatcher.

Loads skills from database (via SkillManager) instead of static SKILL_MASTER.

Usage:
    from skills_manager import SkillManager
    from spacy_skill_extractor import SpacySkillExtractor
    
    skill_manager = SkillManager(supabase)
    extractor = SpacySkillExtractor(skill_manager.get_all_skills())
    skills = extractor.extract(text)
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
import spacy
from spacy.matcher import PhraseMatcher
from spacy.tokens import Span

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class SkillMatch:
    name: str
    category: str
    matched_text: str
    start: int
    end: int


class SpacySkillExtractor:
    """
    Matches skills in text using spaCy's PhraseMatcher.
    
    Now loads skills from database (via SkillManager) instead of hardcoded SKILL_MASTER.
    This allows automatic discovery of new skills as they're added to the database.
    """

    def __init__(self, skill_names: list[str]):
        """
        Initialize extractor with list of skill names.
        
        Args:
            skill_names: List of skill names to match (from SkillManager.get_all_skills())
        """
        self._nlp = spacy.blank("en")
        self._matcher = PhraseMatcher(self._nlp.vocab, attr="LOWER")
        self._skill_names: dict[str, str] = {}  # Normalized name -> canonical name
        self._load(skill_names)

    def _load(self, skill_names: list[str]) -> None:
        """
        Load skills from database-backed list.
        
        Args:
            skill_names: List of skill names to index
        """
        if not isinstance(skill_names, list):
            raise TypeError("skill_names must be a list of strings")

        loaded = 0
        for skill_name in skill_names:
            if not isinstance(skill_name, str) or not skill_name.strip():
                log.warning("Skipping invalid skill name: %r", skill_name)
                continue

            canonical = skill_name.strip()
            
            # Create pattern for matching
            pattern = self._nlp.make_doc(canonical)
            
            # Normalize for deduplication (lowercase)
            normalized = canonical.lower()
            
            # Skip duplicates (case-insensitive)
            if normalized in self._skill_names:
                continue
            
            # Add to matcher using normalized name as key
            self._matcher.add(normalized, [pattern])
            self._skill_names[normalized] = canonical
            loaded += 1

        log.info("✅ SpacySkillExtractor loaded %d skills from database", loaded)

    def extract(self, text: str) -> list[SkillMatch]:
        """
        Extract skills from text.
        
        Returns non-overlapping skill matches, one per skill, ordered by position.
        
        Args:
            text: Text to extract skills from
            
        Returns:
            List of SkillMatch objects with skill names found in text
        """
        if not isinstance(text, str) or not text.strip():
            return []

        doc = self._nlp(text)
        raw = []
        for match_id, start, end in self._matcher(doc):
            key = self._nlp.vocab.strings[match_id]
            name = self._skill_names[key]
            span: Span = doc[start:end]
            raw.append((start, end, name, span))

        # Prefer longer matches so "Spring Boot" wins over "Spring"
        raw.sort(key=lambda m: (m[0], -(m[1] - m[0])))
        
        chosen = []
        last_end = -1
        for start, end, name, span in raw:
            if start < last_end:
                continue  # Overlaps a longer match already chosen
            chosen.append(SkillMatch(
                name=name,
                category="",  # Category not tracked in database-backed version
                matched_text=span.text,
                start=span.start_char,
                end=span.end_char,
            ))
            last_end = end

        # One entry per canonical skill, keeping the first occurrence
        seen: set[str] = set()
        unique: list[SkillMatch] = []
        for m in chosen:
            if m.name.lower() not in seen:
                seen.add(m.name.lower())
                unique.append(m)
        
        return unique