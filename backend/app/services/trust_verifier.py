"""Trust verification and authenticity scoring for 2026 data integrity."""

import hashlib
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from backend.app.models.data_source import DataSource
from backend.app.models.data_audit import DataAudit, SourceReputation


class TrustVerifier:
    """Verifies data authenticity and calculates trust scores."""

    def __init__(self, db: Session):
        self.db = db

    async def calculate_trust_score(
        self,
        data: List[Dict],
        source: DataSource,
        cross_verify_sources: Optional[List[DataSource]] = None,
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive trust score for collected data.

        Returns:
        {
            "overall": 0-100,
            "authenticity": 0-100,
            "consistency": 0-100,
            "freshness": 0-100,
            "source_reputation": 0-100,
            "ai_generated_count": int,
            "anomalies": [],
            "flags": []
        }
        """
        if not data:
            return self._empty_trust_score()

        score = {
            "overall": 0.0,
            "authenticity": 0.0,
            "consistency": 0.0,
            "freshness": 0.0,
            "source_reputation": 0.0,
            "ai_generated_count": 0,
            "anomalies": [],
            "flags": [],
            "timestamp": datetime.utcnow().isoformat(),
        }

        # 1. Source Reputation (Dynamic)
        score["source_reputation"] = await self._get_source_reputation(source)

        # 2. Authenticity (Anti-fake, Anti-AI)
        authenticity_result = await self._check_authenticity(data)
        score["authenticity"] = authenticity_result["score"]
        score["ai_generated_count"] = authenticity_result["ai_count"]
        if authenticity_result["flags"]:
            score["flags"].extend(authenticity_result["flags"])

        # 3. Consistency (Data coherence)
        consistency_result = await self._check_consistency(data)
        score["consistency"] = consistency_result["score"]
        if consistency_result["anomalies"]:
            score["anomalies"].extend(consistency_result["anomalies"])

        # 4. Freshness (Data recency)
        score["freshness"] = await self._check_freshness(data)

        # 5. Cross-verification (Multiple sources)
        if cross_verify_sources:
            cross_score = await self._cross_verify(data, cross_verify_sources)
            score["cross_verification"] = cross_score

        # Calculate overall score (weighted average)
        weights = {
            "source_reputation": 0.25,
            "authenticity": 0.35,
            "consistency": 0.20,
            "freshness": 0.15,
            "cross_verification": 0.05,
        }

        total_weight = 0
        weighted_sum = 0

        for key, weight in weights.items():
            if key in score and isinstance(score[key], (int, float)):
                weighted_sum += score[key] * weight
                total_weight += weight

        score["overall"] = weighted_sum / total_weight if total_weight > 0 else 0.0

        # Add data hashes for audit trail
        score["data_hash"] = self._generate_data_hash(data)
        score["record_count"] = len(data)

        return score

    async def _get_source_reputation(self, source: DataSource) -> float:
        """Get dynamic source reputation score."""
        reputation = (
            self.db.query(SourceReputation)
            .filter(SourceReputation.data_source_id == source.id)
            .first()
        )

        if not reputation:
            # New source: neutral score
            return 50.0

        return reputation.overall_score

    async def _check_authenticity(self, data: List[Dict]) -> Dict[str, Any]:
        """
        Check for AI-generated content and fake data.
        Returns: {score, ai_count, flags}
        """
        ai_count = 0
        suspicious_records = []
        flags = []

        for idx, record in enumerate(data):
            # Extract text fields
            text_fields = [
                v
                for v in record.values()
                if isinstance(v, str) and len(v) > 50
            ]

            for text in text_fields:
                ai_prob = await self._detect_ai_generated(text)
                if ai_prob > 0.7:
                    ai_count += 1
                    suspicious_records.append(
                        {
                            "record_idx": idx,
                            "ai_probability": ai_prob,
                            "text_sample": text[:100],
                        }
                    )

        # Calculate authenticity score
        if not data:
            authenticity_score = 100.0
        else:
            authenticity_score = max(0, 100 - (ai_count / len(data) * 100))

        if ai_count > len(data) * 0.3:  # More than 30% AI-generated
            flags.append("HIGH_AI_CONTENT_DETECTED")

        return {
            "score": authenticity_score,
            "ai_count": ai_count,
            "flags": flags,
            "suspicious_records": suspicious_records,
        }

    async def _detect_ai_generated(self, text: str) -> float:
        """
        Detect if text is AI-generated.
        Uses lightweight heuristics + optional ML model.

        Returns: probability 0-1
        """
        # Heuristic checks (fast, no ML)
        score = 0.0

        # Check 1: Repetitive patterns
        words = text.lower().split()
        if len(words) > 0:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.5:  # Too repetitive
                score += 0.2

        # Check 2: Unnatural sentence structure
        if self._has_unnatural_structure(text):
            score += 0.15

        # Check 3: Keyword patterns common in AI text
        ai_keywords = [
            "in conclusion",
            "furthermore",
            "it is important to note",
            "as mentioned",
            "in summary",
        ]
        keyword_count = sum(1 for kw in ai_keywords if kw in text.lower())
        if keyword_count > 2:
            score += 0.15

        # Check 4: Lack of specific details
        if self._lacks_specificity(text):
            score += 0.2

        # Check 5: Perfect grammar (sometimes suspicious)
        if self._has_perfect_grammar(text):
            score += 0.1

        # Optional: Use ML model if available
        # score += await self._ml_ai_detection(text) * 0.2

        return min(1.0, score)

    def _has_unnatural_structure(self, text: str) -> bool:
        """Check for unnatural sentence structure."""
        sentences = text.split(".")
        if len(sentences) < 2:
            return False

        # Check average sentence length
        avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
        # AI text often has very uniform sentence length
        if 15 < avg_length < 25:
            return True

        return False

    def _lacks_specificity(self, text: str) -> bool:
        """Check if text lacks specific details."""
        # Count specific markers
        specific_markers = ["specifically", "for example", "such as", "like", "%", "$"]
        marker_count = sum(1 for marker in specific_markers if marker in text.lower())

        return marker_count < 1

    def _has_perfect_grammar(self, text: str) -> bool:
        """Check for suspiciously perfect grammar."""
        # Simple heuristic: no contractions, no informal language
        informal_markers = ["don't", "can't", "won't", "it's", "that's", "gonna"]
        has_informal = any(marker in text.lower() for marker in informal_markers)

        return not has_informal and len(text) > 100

    async def _check_consistency(self, data: List[Dict]) -> Dict[str, Any]:
        """
        Check data consistency and detect anomalies.
        Returns: {score, anomalies}
        """
        anomalies = []
        consistency_issues = 0

        if len(data) < 2:
            return {"score": 100.0, "anomalies": []}

        # Check 1: Temporal consistency
        temporal_issues = self._check_temporal_consistency(data)
        if temporal_issues:
            anomalies.extend(temporal_issues)
            consistency_issues += len(temporal_issues)

        # Check 2: Value range consistency
        range_issues = self._check_value_ranges(data)
        if range_issues:
            anomalies.extend(range_issues)
            consistency_issues += len(range_issues)

        # Check 3: Duplicate detection
        duplicate_count = self._detect_duplicates(data)
        if duplicate_count > len(data) * 0.1:  # More than 10% duplicates
            anomalies.append(
                {
                    "type": "HIGH_DUPLICATE_RATE",
                    "count": duplicate_count,
                    "percentage": (duplicate_count / len(data)) * 100,
                }
            )
            consistency_issues += 1

        # Calculate consistency score
        consistency_score = max(0, 100 - (consistency_issues / len(data) * 100))

        return {"score": consistency_score, "anomalies": anomalies}

    def _check_temporal_consistency(self, data: List[Dict]) -> List[Dict]:
        """Check if timestamps are consistent."""
        issues = []

        # Find timestamp fields
        timestamp_fields = []
        for key in data[0].keys():
            if any(
                ts_marker in key.lower()
                for ts_marker in ["date", "time", "timestamp", "created", "updated"]
            ):
                timestamp_fields.append(key)

        if not timestamp_fields:
            return issues

        # Check for temporal anomalies
        for field in timestamp_fields:
            values = [r.get(field) for r in data if field in r]
            if not values:
                continue

            # Check for future dates
            future_count = sum(
                1
                for v in values
                if isinstance(v, str) and "2099" in v or "2100" in v
            )
            if future_count > 0:
                issues.append(
                    {
                        "type": "FUTURE_DATES",
                        "field": field,
                        "count": future_count,
                    }
                )

        return issues

    def _check_value_ranges(self, data: List[Dict]) -> List[Dict]:
        """Check for extreme values."""
        issues = []

        for key in data[0].keys():
            values = [r.get(key) for r in data if key in r]
            numeric_values = [v for v in values if isinstance(v, (int, float))]

            if len(numeric_values) < 2:
                continue

            # Calculate statistics
            avg = sum(numeric_values) / len(numeric_values)
            std_dev = (
                sum((x - avg) ** 2 for x in numeric_values) / len(numeric_values)
            ) ** 0.5

            # Find extreme values (> 3 std devs)
            extreme_count = sum(
                1 for v in numeric_values if abs(v - avg) > 3 * std_dev
            )

            if extreme_count > len(numeric_values) * 0.05:  # More than 5%
                issues.append(
                    {
                        "type": "EXTREME_VALUES",
                        "field": key,
                        "count": extreme_count,
                        "avg": avg,
                        "std_dev": std_dev,
                    }
                )

        return issues

    def _detect_duplicates(self, data: List[Dict]) -> int:
        """Count duplicate records."""
        seen = set()
        duplicates = 0

        for record in data:
            record_hash = hashlib.md5(str(record).encode()).hexdigest()
            if record_hash in seen:
                duplicates += 1
            seen.add(record_hash)

        return duplicates

    async def _check_freshness(self, data: List[Dict]) -> float:
        """Check data freshness (recency)."""
        # Find timestamp fields
        timestamp_fields = []
        for key in data[0].keys():
            if any(
                ts_marker in key.lower()
                for ts_marker in ["date", "time", "timestamp", "created", "updated"]
            ):
                timestamp_fields.append(key)

        if not timestamp_fields:
            return 50.0  # Unknown freshness

        # Check how recent the data is
        # This is a simplified check - in production, parse actual dates
        recent_count = 0
        for record in data:
            for field in timestamp_fields:
                if field in record:
                    value = str(record[field])
                    # Check if contains current year
                    if "2026" in value or "2025" in value:
                        recent_count += 1

        freshness_score = (recent_count / len(data)) * 100 if data else 50.0
        return min(100.0, freshness_score)

    async def _cross_verify(
        self, data: List[Dict], sources: List[DataSource]
    ) -> Dict[str, Any]:
        """Cross-verify data with other sources."""
        # Simplified: check if key fields exist in other sources
        verified_count = 0

        for source in sources:
            # In production: fetch data from source and compare
            verified_count += 1

        return {
            "verified_sources": verified_count,
            "score": (verified_count / len(sources)) * 100 if sources else 0,
        }

    def _generate_data_hash(self, data: List[Dict]) -> str:
        """Generate SHA-256 hash of data for audit trail."""
        data_str = str(sorted(str(d) for d in data))
        return hashlib.sha256(data_str.encode()).hexdigest()

    def _empty_trust_score(self) -> Dict[str, Any]:
        """Return empty trust score."""
        return {
            "overall": 0.0,
            "authenticity": 0.0,
            "consistency": 0.0,
            "freshness": 0.0,
            "source_reputation": 0.0,
            "ai_generated_count": 0,
            "anomalies": [],
            "flags": ["NO_DATA"],
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def save_audit_trail(
        self,
        source_id: int,
        collection_log_id: int,
        trust_score: Dict[str, Any],
        data: List[Dict],
    ) -> DataAudit:
        """Save audit trail to database."""
        audit = DataAudit(
            data_source_id=source_id,
            collection_log_id=collection_log_id,
            data_hash=trust_score.get("data_hash"),
            record_count=trust_score.get("record_count", 0),
            trust_score=trust_score.get("overall", 0.0),
            authenticity_score=trust_score.get("authenticity", 0.0),
            consistency_score=trust_score.get("consistency", 0.0),
            freshness_score=trust_score.get("freshness", 0.0),
            source_reputation_score=trust_score.get("source_reputation", 0.0),
            ai_generated_count=trust_score.get("ai_generated_count", 0),
            ai_generated_percentage=(
                (trust_score.get("ai_generated_count", 0) / len(data) * 100)
                if data
                else 0
            ),
            cross_verified=bool(trust_score.get("cross_verification")),
            verification_status="verified"
            if trust_score.get("overall", 0) > 75
            else "partial",
            collected_at=datetime.utcnow(),
        )

        self.db.add(audit)
        self.db.commit()
        self.db.refresh(audit)

        return audit
