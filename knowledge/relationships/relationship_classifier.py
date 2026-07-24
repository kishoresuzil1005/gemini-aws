# knowledge/relationships/relationship_classifier.py
"""Maps raw relationship strings into standard taxonomy."""

import logging

logger = logging.getLogger(__name__)

class RelationshipClassifier:
    """Classifies raw edges into Canonical Relationship Types."""
    
    # Static taxonomy map for demonstration
    TAXONOMY = {
        "depends_on": "DEPENDS_ON",
        "attached_to": "ATTACHED_TO",
        "assumes_role": "ASSUMES_ROLE",
        "grants_permission": "GRANTS_PERMISSION",
        "monitors": "MONITORS",
        "incurs_cost": "INCURS_COST",
        "part_of": "PART_OF"
    }

    def classify(self, raw_type: str) -> str:
        """Map a raw string to the official taxonomy."""
        normalized = raw_type.lower().strip()
        classified = self.TAXONOMY.get(normalized)
        
        if not classified:
            logger.warning(f"Unmapped relationship type '{raw_type}'. Defaulting to DEPENDS_ON.")
            return "DEPENDS_ON"
            
        return classified
