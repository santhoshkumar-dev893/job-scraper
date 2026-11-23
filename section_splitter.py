import re
from typing import Dict, List, Tuple
from enum import Enum


class SplitMethod(Enum):
    """Enum for different section splitting methods"""
    REGEX_SECTIONS = "regex_sections"          # Found standard sections (Requirements, Nice-to-Have, etc)
    SIMPLE_SPLIT = "simple_split"              # Fallback: split by common keywords
    FULL_TEXT = "full_text"                    # Last resort: treat entire JD as one section


class SectionSplitter:
    """
    Splits job descriptions into meaningful sections:
    - Requirements
    - Nice-to-Have
    - Responsibilities
    - About Company
    - Benefits
    
    Handles LinkedIn JDs with missing sections gracefully.
    """
    
    # Section patterns (ordered by priority)
    SECTION_PATTERNS = {
        'requirements': [
            r'(?:^|\n)\s*(?:requirements?|must[\s-]*have|required[\s-]*skills?|qualifications?|technical[\s-]*requirements?)\s*:?',
            r'(?:^|\n)\s*(?:\*\*requirements?\*\*|###?\s*requirements?)',
        ],
        'nice_to_have': [
            r'(?:^|\n)\s*(?:nice[\s-]*to[\s-]*have|preferred[\s-]*skills?|bonus[\s-]*skills?|additional[\s-]*skills?)',
            r'(?:^|\n)\s*(?:\*\*nice[\s-]*to[\s-]*have\*\*|###?\s*nice[\s-]*to[\s-]*have)',
        ],
        'responsibilities': [
            r'(?:^|\n)\s*(?:responsibilities?|what[\s-]*you[\s-]*will[\s-]*do|your[\s-]*role|key[\s-]*responsibilities?)',
            r'(?:^|\n)\s*(?:\*\*responsibilities?\*\*|###?\s*responsibilities?)',
        ],
        'about_company': [
            r'(?:^|\n)\s*(?:about[\s-]*(?:us|the[\s-]*company)|company[\s-]*overview)',
            r'(?:^|\n)\s*(?:\*\*about[\s-]*us\*\*|###?\s*about[\s-]*us)',
        ],
        'benefits': [
            r'(?:^|\n)\s*(?:benefits?|perks|compensation|salary|what[\s-]*we[\s-]*offer)',
            r'(?:^|\n)\s*(?:\*\*benefits?\*\*|###?\s*benefits?)',
        ],
    }
    
    def __init__(self):
        """Initialize section splitter with compiled regex patterns"""
        self.compiled_patterns = {}
        for section_name, patterns in self.SECTION_PATTERNS.items():
            self.compiled_patterns[section_name] = [
                re.compile(pattern, re.IGNORECASE | re.MULTILINE)
                for pattern in patterns
            ]
    
    def split_sections(self, job_description: str) -> Tuple[Dict[str, str], SplitMethod]:
        """
        Split job description into sections.
        
        Args:
            job_description: Full job description text
            
        Returns:
            Tuple of:
            - Dictionary with sections: {section_name: section_text}
            - SplitMethod enum indicating which strategy was used
            
        Handles cases where LinkedIn JDs have missing sections gracefully.
        """
        if not job_description or not job_description.strip():
            return {}, SplitMethod.FULL_TEXT
        
        # Try to find structured sections
        sections = self._find_sections(job_description)
        
        if sections and len(sections) > 1:
            # Found multiple sections - use regex approach
            return sections, SplitMethod.REGEX_SECTIONS
        
        # Fallback: Simple split by common keywords
        sections = self._simple_split(job_description)
        
        if sections and len(sections) > 1:
            return sections, SplitMethod.SIMPLE_SPLIT
        
        # Last resort: treat entire JD as "requirements"
        return {'requirements': job_description}, SplitMethod.FULL_TEXT
    
    def _find_sections(self, text: str) -> Dict[str, str]:
        """
        Find sections using regex patterns.
        
        Returns dict with found sections and their content.
        If a section header is not found, that section is empty in the dict.
        """
        sections = {}
        section_positions = {}
        
        # Find all section headers and their positions
        for section_name, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                match = pattern.search(text)
                if match:
                    section_positions[section_name] = match.end()
                    break  # Found this section, move to next
        
        # If no sections found, return empty
        if not section_positions:
            return {}
        
        # Extract content for each section
        sorted_sections = sorted(section_positions.items(), key=lambda x: x[1])
        
        for i, (section_name, start_pos) in enumerate(sorted_sections):
            # Find where this section ends (start of next section or end of text)
            if i < len(sorted_sections) - 1:
                end_pos = sorted_sections[i + 1][1]
                # Go back to find the actual start of next section header
                next_section_text = text[start_pos:end_pos]
                # Find the last newline before end_pos to get clean boundary
                last_newline = next_section_text.rfind('\n')
                if last_newline != -1:
                    end_pos = start_pos + last_newline
            else:
                end_pos = len(text)
            
            section_content = text[start_pos:end_pos].strip()
            sections[section_name] = section_content
        
        return sections
    
    def _simple_split(self, text: str) -> Dict[str, str]:
        """
        Simple fallback split using common section keywords.
        
        Useful for LinkedIn JDs that don't have clear structured sections.
        """
        sections = {}
        
        # Common keywords that indicate sections
        keywords = {
            'requirements': ['requirements', 'must have', 'required', 'qualifications'],
            'nice_to_have': ['nice to have', 'preferred', 'bonus', 'additional skills'],
            'responsibilities': ['responsibilities', 'your role', 'what you will do', 'key responsibilities'],
            'about_company': ['about us', 'about the company', 'our company'],
            'benefits': ['benefits', 'perks', 'compensation', 'salary', 'what we offer'],
        }
        
        # For each keyword set, try to find and extract that section
        text_lower = text.lower()
        found_any = False
        
        for section_name, keyword_list in keywords.items():
            for keyword in keyword_list:
                if keyword.lower() in text_lower:
                    # Found a keyword, try to extract that section
                    idx = text_lower.find(keyword.lower())
                    # Get from keyword to next major section or end
                    start = idx
                    end = len(text)
                    
                    # Look for next section keyword
                    for other_section, other_keywords in keywords.items():
                        if other_section != section_name:
                            for other_keyword in other_keywords:
                                other_idx = text_lower.find(other_keyword.lower(), start + len(keyword))
                                if other_idx != -1 and other_idx < end:
                                    end = other_idx
                    
                    section_content = text[start:end].strip()
                    if section_content:
                        sections[section_name] = section_content
                        found_any = True
                    break
        
        return sections if found_any else {}
    
    def get_all_sections(self, job_description: str) -> Dict[str, str]:
        """
        Get all sections, ensuring empty sections have empty strings.
        
        Returns dict with all known section names, even if not found.
        """
        sections, _ = self.split_sections(job_description)
        
        # Ensure all expected sections exist
        all_sections = {
            'requirements': sections.get('requirements', ''),
            'nice_to_have': sections.get('nice_to_have', ''),
            'responsibilities': sections.get('responsibilities', ''),
            'about_company': sections.get('about_company', ''),
            'benefits': sections.get('benefits', ''),
        }
        
        return all_sections
