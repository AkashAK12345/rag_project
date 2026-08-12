"""
services/field_normalization_service.py

Service dedicated to normalizing raw column names into canonical field names.
"""

import re
from core.field_aliases import FIELD_ALIASES

class FieldNormalizationService:
    @staticmethod
    def normalize_column_name(raw_name: str) -> str:
        """
        Cleans a raw column name and maps it to a canonical field if an alias matches.
        """
        if not raw_name:
            return ""
            
        # Clean: lowercase, strip, remove punctuation, collapse whitespace
        cleaned = str(raw_name).lower().strip()
        cleaned = re.sub(r'[^\w\s]', '', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Check against aliases
        for canonical_name, aliases in FIELD_ALIASES.items():
            if cleaned in aliases:
                return canonical_name
                
            # Fallback: substring match if exact match fails
            for alias in aliases:
                if alias in cleaned:
                    return canonical_name
                    
        # If no mapping found, return a snake_case version of the cleaned name
        return cleaned.replace(' ', '_')
