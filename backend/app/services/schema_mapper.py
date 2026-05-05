"""
Schema Mapper with Embeddings for Automatic Field Mapping

Features:
- Automatic field mapping using embeddings
- Unified ontology support
- Schema versioning
- Field similarity detection
- Type inference
- Mapping history tracking
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    SentenceTransformer = None

logger = logging.getLogger(__name__)


@dataclass
class FieldMapping:
    """Represents a field mapping"""

    source_field: str
    target_field: str
    similarity_score: float
    field_type: str
    transformation: Optional[str] = None
    confidence: float = 0.0


@dataclass
class SchemaVersion:
    """Represents a schema version"""

    version: str
    created_at: datetime
    fields: Dict[str, str]
    description: str


class UnifiedOntology:
    """Unified ontology for data field standardization"""

    # Core African data fields (inspired by Palantir)
    CORE_FIELDS = {
        # Demographics
        "population": ["population", "inhabitants", "residents", "total_pop", "pop_total"],
        "age": ["age", "age_group", "age_range", "age_bracket"],
        "gender": ["gender", "sex", "male", "female"],
        "region": ["region", "province", "state", "district", "area"],
        "country": ["country", "nation", "country_code"],

        # Economics
        "gdp": ["gdp", "gross_domestic_product", "gdp_value"],
        "inflation": ["inflation", "inflation_rate", "cpi"],
        "unemployment": ["unemployment", "unemployment_rate", "jobless_rate"],
        "income": ["income", "salary", "wage", "earnings"],
        "poverty": ["poverty", "poverty_rate", "poor_percentage"],

        # Health
        "mortality": ["mortality", "death_rate", "mortality_rate"],
        "life_expectancy": ["life_expectancy", "life_exp", "avg_lifespan"],
        "disease": ["disease", "illness", "condition", "pathology"],
        "cases": ["cases", "confirmed_cases", "total_cases"],
        "deaths": ["deaths", "fatalities", "deceased"],

        # Education
        "literacy": ["literacy", "literacy_rate", "literate_percentage"],
        "enrollment": ["enrollment", "students", "pupils", "attendees"],
        "schools": ["schools", "educational_institutions", "school_count"],

        # Agriculture
        "crop": ["crop", "crop_type", "commodity"],
        "yield": ["yield", "production", "output"],
        "price": ["price", "cost", "value", "rate"],
        "area": ["area", "land_area", "hectares", "acres"],

        # Environment
        "temperature": ["temperature", "temp", "celsius", "fahrenheit"],
        "rainfall": ["rainfall", "precipitation", "rain"],
        "humidity": ["humidity", "moisture", "relative_humidity"],
        "air_quality": ["air_quality", "aqi", "pollution"],

        # Infrastructure
        "roads": ["roads", "road_network", "highway"],
        "electricity": ["electricity", "power", "energy"],
        "water": ["water", "water_supply", "potable_water"],
        "internet": ["internet", "connectivity", "broadband"],

        # Metadata
        "date": ["date", "timestamp", "time", "datetime", "created_at", "updated_at"],
        "source": ["source", "origin", "provider", "data_source"],
        "quality": ["quality", "quality_score", "reliability"],
    }

    def __init__(self):
        """Initialize unified ontology"""
        self.versions: Dict[str, SchemaVersion] = {}
        self._init_default_version()

    def _init_default_version(self):
        """Initialize default schema version"""
        self.versions["1.0"] = SchemaVersion(
            version="1.0",
            created_at=datetime.utcnow(),
            fields=self.CORE_FIELDS,
            description="Default unified ontology for African data",
        )

    def get_canonical_field(self, field_name: str) -> Optional[str]:
        """
        Get canonical field name from unified ontology

        Args:
            field_name: Field name to normalize

        Returns:
            Canonical field name or None
        """
        field_lower = field_name.lower().strip()

        for canonical, aliases in self.CORE_FIELDS.items():
            if field_lower == canonical or field_lower in aliases:
                return canonical

        return None

    def add_version(self, version: str, fields: Dict[str, str], description: str = ""):
        """
        Add new schema version

        Args:
            version: Version identifier
            fields: Field mappings
            description: Version description
        """
        self.versions[version] = SchemaVersion(
            version=version,
            created_at=datetime.utcnow(),
            fields=fields,
            description=description,
        )

    def get_version(self, version: str = "1.0") -> Optional[SchemaVersion]:
        """Get schema version"""
        return self.versions.get(version)


class SchemaMapper:
    """Automatic schema mapping using embeddings"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize schema mapper

        Args:
            model_name: Sentence transformer model name
        """
        try:
            self.model = SentenceTransformer(model_name)
        except Exception as e:
            logger.warning(f"Failed to load model {model_name}: {str(e)}")
            self.model = None

        self.ontology = UnifiedOntology()
        self.mapping_history: List[Dict[str, Any]] = []

    async def map_schema(
        self,
        source_fields: List[str],
        target_fields: Optional[List[str]] = None,
        min_similarity: float = 0.5,
    ) -> List[FieldMapping]:
        """
        Map source fields to target fields using embeddings

        Args:
            source_fields: Source field names
            target_fields: Target field names (if None, use unified ontology)
            min_similarity: Minimum similarity threshold

        Returns:
            List of field mappings
        """
        if target_fields is None:
            target_fields = list(self.ontology.CORE_FIELDS.keys())

        mappings = []

        for source_field in source_fields:
            # First try exact match in ontology
            canonical = self.ontology.get_canonical_field(source_field)
            if canonical:
                mappings.append(
                    FieldMapping(
                        source_field=source_field,
                        target_field=canonical,
                        similarity_score=1.0,
                        field_type=self._infer_type(source_field),
                        confidence=0.95,
                    )
                )
                continue

            # Use embeddings for similarity matching
            if self.model:
                best_match = await self._find_best_match(
                    source_field, target_fields, min_similarity
                )
                if best_match:
                    mappings.append(best_match)
            else:
                # Fallback to simple string matching
                best_match = self._simple_match(source_field, target_fields)
                if best_match:
                    mappings.append(best_match)

        # Record mapping history
        self._record_mapping(source_fields, mappings)

        return mappings

    async def _find_best_match(
        self,
        source_field: str,
        target_fields: List[str],
        min_similarity: float,
    ) -> Optional[FieldMapping]:
        """
        Find best matching target field using embeddings

        Args:
            source_field: Source field name
            target_fields: List of target field names
            min_similarity: Minimum similarity threshold

        Returns:
            Best matching field mapping or None
        """
        try:
            # Encode source and target fields
            source_embedding = self.model.encode(source_field, convert_to_tensor=True)
            target_embeddings = self.model.encode(target_fields, convert_to_tensor=True)

            # Calculate similarities
            from sentence_transformers.util import pytorch_cos_sim

            similarities = pytorch_cos_sim(source_embedding, target_embeddings)[0]

            # Find best match
            best_idx = similarities.argmax().item()
            best_score = similarities[best_idx].item()

            if best_score >= min_similarity:
                return FieldMapping(
                    source_field=source_field,
                    target_field=target_fields[best_idx],
                    similarity_score=best_score,
                    field_type=self._infer_type(source_field),
                    confidence=best_score,
                )

        except Exception as e:
            logger.warning(f"Error in embedding-based matching: {str(e)}")

        return None

    def _simple_match(
        self,
        source_field: str,
        target_fields: List[str],
    ) -> Optional[FieldMapping]:
        """
        Simple string-based field matching

        Args:
            source_field: Source field name
            target_fields: List of target field names

        Returns:
            Best matching field mapping or None
        """
        source_lower = source_field.lower()
        best_match = None
        best_score = 0.0

        for target_field in target_fields:
            target_lower = target_field.lower()

            # Exact match
            if source_lower == target_lower:
                return FieldMapping(
                    source_field=source_field,
                    target_field=target_field,
                    similarity_score=1.0,
                    field_type=self._infer_type(source_field),
                    confidence=1.0,
                )

            # Substring match
            if source_lower in target_lower or target_lower in source_lower:
                score = len(set(source_lower) & set(target_lower)) / max(
                    len(source_lower), len(target_lower)
                )
                if score > best_score:
                    best_score = score
                    best_match = FieldMapping(
                        source_field=source_field,
                        target_field=target_field,
                        similarity_score=score,
                        field_type=self._infer_type(source_field),
                        confidence=score,
                    )

        return best_match

    def _infer_type(self, field_name: str) -> str:
        """
        Infer field type from field name

        Args:
            field_name: Field name

        Returns:
            Inferred field type
        """
        field_lower = field_name.lower()

        # Type inference heuristics
        if any(x in field_lower for x in ["date", "time", "timestamp", "created", "updated"]):
            return "datetime"
        elif any(x in field_lower for x in ["count", "total", "number", "quantity", "id"]):
            return "integer"
        elif any(x in field_lower for x in ["price", "cost", "value", "rate", "percentage"]):
            return "float"
        elif any(x in field_lower for x in ["name", "title", "description", "text"]):
            return "string"
        elif any(x in field_lower for x in ["active", "enabled", "flag", "is_"]):
            return "boolean"
        else:
            return "string"

    def _record_mapping(self, source_fields: List[str], mappings: List[FieldMapping]):
        """Record mapping in history"""
        self.mapping_history.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "source_fields": source_fields,
                "mappings": [
                    {
                        "source": m.source_field,
                        "target": m.target_field,
                        "similarity": m.similarity_score,
                        "confidence": m.confidence,
                    }
                    for m in mappings
                ],
            }
        )

    def get_mapping_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent mapping history"""
        return self.mapping_history[-limit:]

    def export_mappings(self, mappings: List[FieldMapping]) -> Dict[str, str]:
        """
        Export mappings as dictionary

        Args:
            mappings: List of field mappings

        Returns:
            Dictionary of source -> target mappings
        """
        return {m.source_field: m.target_field for m in mappings}

    def import_mappings(self, mapping_dict: Dict[str, str]) -> List[FieldMapping]:
        """
        Import mappings from dictionary

        Args:
            mapping_dict: Dictionary of source -> target mappings

        Returns:
            List of field mappings
        """
        mappings = []
        for source, target in mapping_dict.items():
            mappings.append(
                FieldMapping(
                    source_field=source,
                    target_field=target,
                    similarity_score=1.0,
                    field_type=self._infer_type(source),
                    confidence=1.0,
                )
            )
        return mappings


class SchemaVersionManager:
    """Manage schema versions and migrations"""

    def __init__(self):
        """Initialize schema version manager"""
        self.versions: Dict[str, Dict[str, Any]] = {}
        self.current_version = "1.0"

    def create_version(
        self,
        version: str,
        schema: Dict[str, str],
        description: str = "",
    ):
        """Create new schema version"""
        self.versions[version] = {
            "schema": schema,
            "description": description,
            "created_at": datetime.utcnow().isoformat(),
        }

    def migrate_data(
        self,
        data: List[Dict[str, Any]],
        from_version: str,
        to_version: str,
    ) -> List[Dict[str, Any]]:
        """
        Migrate data from one schema version to another

        Args:
            data: Data to migrate
            from_version: Source schema version
            to_version: Target schema version

        Returns:
            Migrated data
        """
        if from_version == to_version:
            return data

        # Get mapping between versions
        from_schema = self.versions.get(from_version, {}).get("schema", {})
        to_schema = self.versions.get(to_version, {}).get("schema", {})

        migrated = []
        for record in data:
            new_record = {}
            for target_field in to_schema.keys():
                # Find corresponding source field
                for source_field, source_type in from_schema.items():
                    if source_field in record:
                        new_record[target_field] = record[source_field]
                        break

            migrated.append(new_record)

        return migrated

    def get_version_info(self, version: str) -> Optional[Dict[str, Any]]:
        """Get version information"""
        return self.versions.get(version)

    def list_versions(self) -> List[str]:
        """List all available versions"""
        return list(self.versions.keys())
