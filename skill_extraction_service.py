"""
Combines deterministic spaCy matches with optional LLM enrichment.

spaCy is the baseline: its matches are exact and always available.
The LLM adds skills spaCy missed and attaches requirement levels and evidence.
If the LLM fails or is disabled, the service still returns spaCy results.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Protocol

log = logging.getLogger(__name__)

UNCATEGORIZED = "uncategorized"
UNSPECIFIED = "unspecified"

REQUIREMENT_ORDER = {"mandatory": 0, "preferred": 1, "optional": 2, UNSPECIFIED: 3}
LLM_OK_STATUSES = {"ok", "partial"}


class SpacyMatcher(Protocol):
    def extract(self, text: str) -> list[Any]: ...


class LLMMatcher(Protocol):
    def extract(self, description: str, known_skills: list[str]) -> Any: ...


@dataclass(frozen=True)
class MergedSkill:
    name: str
    category: str
    requirement: str
    confidence: float
    sources: tuple[str, ...]
    evidence: str | None = None


@dataclass
class SkillExtractionResult:
    skills: list[MergedSkill] = field(default_factory=list)
    llm_status: str = "disabled"  # ok | partial | failed | skipped | error | disabled
    warnings: list[str] = field(default_factory=list)


def build_canonical_lookup(skill_master: dict[str, dict[str, list[str]]]) -> dict[str, tuple[str, str]]:
    """Map every alias (lowercased) to (canonical_name, category)."""
    lookup: dict[str, tuple[str, str]] = {}
    for category, skills in skill_master.items():
        for canonical, aliases in skills.items():
            lookup.setdefault(canonical.lower(), (canonical, category))
            for alias in aliases or []:
                if isinstance(alias, str) and alias.strip():
                    lookup.setdefault(alias.strip().lower(), (canonical, category))
    return lookup


class SkillExtractionService:
    def __init__(
        self,
        spacy_extractor: SpacyMatcher,
        canonical_lookup: dict[str, tuple[str, str]],
        llm_extractor: LLMMatcher | None = None,
    ):
        self._spacy = spacy_extractor
        self._lookup = canonical_lookup
        self._llm = llm_extractor

    def extract_skills(self, description: str) -> SkillExtractionResult:
        result = SkillExtractionResult()

        if not isinstance(description, str) or not description.strip():
            result.llm_status = "skipped"
            result.warnings.append("empty description")
            return result

        # Step 1: deterministic matches. A failure here is a bug, so let it propagate.
        spacy_matches = self._spacy.extract(description)
        merged: dict[str, MergedSkill] = {}

        for m in spacy_matches:
            merged[m.name.lower()] = MergedSkill(
                name=m.name,
                category=m.category,
                requirement=UNSPECIFIED,
                confidence=1.0,
                sources=("spacy",),
            )

        # Step 2: LLM enrichment. Any failure is logged and skipped.
        if self._llm is None:
            return self._finish(merged, result)

        known = [m.name for m in spacy_matches]
        try:
            llm_result = self._llm.extract(description, known_skills=known)
        except Exception:
            log.exception("LLM extraction raised unexpectedly")
            result.llm_status = "error"
            result.warnings.append("llm exception")
            return self._finish(merged, result)

        result.llm_status = llm_result.status
        result.warnings.extend(llm_result.warnings)

        if llm_result.status not in LLM_OK_STATUSES:
            return self._finish(merged, result)

        # Step 3: merge LLM skills into the spaCy baseline.
        for s in llm_result.skills:
            raw_name = s.name.strip()
            canonical = self._lookup.get(raw_name.lower())
            name, category = canonical if canonical else (raw_name, UNCATEGORIZED)
            key = name.lower()
            level = getattr(s.level, "value", s.level)

            existing = merged.get(key)
            if existing is None:
                merged[key] = MergedSkill(
                    name=name,
                    category=category,
                    requirement=level,
                    confidence=s.confidence,
                    sources=("llm",),
                    evidence=s.evidence,
                )
            else:
                # spaCy found it: LLM contributes requirement level and evidence.
                requirement = existing.requirement
                if requirement == UNSPECIFIED and level != UNSPECIFIED:
                    requirement = level
                merged[key] = MergedSkill(
                    name=existing.name,
                    category=existing.category,
                    requirement=requirement,
                    confidence=max(existing.confidence, s.confidence),
                    sources=existing.sources + ("llm",),
                    evidence=s.evidence,
                )

        return self._finish(merged, result)

    @staticmethod
    def _finish(merged: dict[str, MergedSkill], result: SkillExtractionResult) -> SkillExtractionResult:
        result.skills = sorted(
            merged.values(),
            key=lambda s: (REQUIREMENT_ORDER.get(s.requirement, 3), s.name.lower()),
        )
        return result