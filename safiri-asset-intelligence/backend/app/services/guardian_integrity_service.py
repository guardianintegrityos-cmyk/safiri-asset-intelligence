"""
Guardian Integrity Oversight Layer for Safiri Asset Intelligence
Implements claim classification, institutional verification, and appeal process
Part of Guardian Academy's mission to create transparent asset intelligence
"""

from datetime import datetime
from typing import Optional, Dict
from sqlalchemy.orm import Session
from app.models import GuardianIntegrity, IdentityVerification, IdentityCore, Asset
from app.config import security_config


class IntegrityScorer:
    """
    Calculates integrity scores for claims
    Combines identity confidence, document authenticity, and behavior risk
    """
    
    @staticmethod
    def calculate_identity_confidence(verification: IdentityVerification) -> float:
        """
        Calculate identity confidence score (0.0-1.0)
        Higher = more confident in identity
        
        Based on:
        - Email verification
        - Phone verification
        - Face match confidence
        - Document authenticity
        
        Args:
            verification: IdentityVerification object
            
        Returns:
            Confidence score 0.0-1.0
        """
        components = []
        
        # Email verification (0.25 weight)
        if verification.email_verified:
            components.append((0.25, 1.0))
        else:
            components.append((0.25, 0.0))
        
        # Phone verification (0.25 weight)
        if verification.phone_verified:
            components.append((0.25, 1.0))
        else:
            components.append((0.25, 0.0))
        
        # Face match confidence (0.25 weight)
        if verification.face_match_confidence:
            components.append((0.25, verification.face_match_confidence))
        else:
            components.append((0.25, 0.0))
        
        # Document verification (0.25 weight)
        if verification.document_verified:
            components.append((0.25, 1.0))
        else:
            components.append((0.25, 0.0))
        
        # Weighted average
        total = sum(weight * score for weight, score in components)
        return min(1.0, max(0.0, total))
    
    @staticmethod
    def calculate_document_authenticity(verification: IdentityVerification) -> float:
        """
        Calculate document authenticity score (0.0-1.0)
        Higher = more confident document is genuine
        
        Checks:
        - Document hash not in fraud database
        - Metadata validation
        - Forgery detection (AI-based)
        - Watermark verification
        
        Args:
            verification: IdentityVerification object
            
        Returns:
            Authenticity score 0.0-1.0
        """
        if not verification.document_uploaded:
            return 0.0
        
        if not verification.document_verified:
            return 0.5  # Default if not yet verified
        
        # In production, would check:
        # - Document against known fraud database
        # - AI forgery detection
        # - Watermark and security features
        
        return 0.95  # High confidence if verified
    
    @staticmethod
    def calculate_behavior_risk(fraud_score: float) -> float:
        """
        Calculate behavior risk score (0.0-1.0)
        Higher = more risky behavior
        Inverted for integrity score (lower risk = higher integrity)
        
        Args:
            fraud_score: Fraud detection engine score (0.0-1.0)
            
        Returns:
            Behavior score 0.0-1.0
        """
        # Invert fraud score to produce integrity score
        return 1.0 - fraud_score
    
    @staticmethod
    def calculate_overall_integrity_score(
        identity_confidence: float,
        document_authenticity: float,
        behavior_risk: float
    ) -> float:
        """
        Calculate overall integrity score (0.0-1.0)
        Weighted combination of components
        
        Weights:
        - Identity confidence: 40%
        - Document authenticity: 35%
        - Behavior risk: 25%
        
        Args:
            identity_confidence: Identity verification score
            document_authenticity: Document authenticity score
            behavior_risk: Behavior risk score
            
        Returns:
            Overall integrity score 0.0-1.0
        """
        weights = [0.40, 0.35, 0.25]
        scores = [identity_confidence, document_authenticity, behavior_risk]
        
        weighted_sum = sum(w * s for w, s in zip(weights, scores))
        return min(1.0, max(0.0, weighted_sum))


class ClaimClassifier:
    """
    Classifies claims into processing levels
    Level 1: Auto-approve (low value, high integrity)
    Level 2: AI + Human review (medium value)
    Level 3: Institutional verification (high value, uncertain)
    """
    
    @staticmethod
    def classify_claim(
        integrity_score: float,
        asset_value: Optional[float] = None,
        identity_id: Optional[int] = None
    ) -> int:
        """
        Classify claim into processing level
        
        Args:
            integrity_score: Guardian integrity score (0.0-1.0)
            asset_value: Asset value (optional)
            identity_id: Identity claiming asset (optional)
            
        Returns:
            Claim level: 1, 2, or 3
        """
        # Base classification on integrity score
        if integrity_score >= security_config.CLAIM_LEVEL_1_THRESHOLD:
            return 1  # Auto-approve
        elif integrity_score >= security_config.CLAIM_LEVEL_2_THRESHOLD:
            return 2  # AI + Human review
        else:
            return 3  # Institutional verification
    
    @staticmethod
    def get_processing_rules(level: int) -> Dict:
        """
        Get processing rules for claim level
        
        Args:
            level: Claim level (1, 2, or 3)
            
        Returns:
            Dictionary with processing rules and requirements
        """
        rules = {
            1: {
                "name": "Automatic Approval",
                "requires_human_review": False,
                "requires_institution_review": False,
                "typical_processing_time_hours": 1,
                "success_probability": 0.95,
                "description": "Low-risk, high-integrity claims auto-approved within 1 hour"
            },
            2: {
                "name": "AI + Human Review",
                "requires_human_review": True,
                "requires_institution_review": False,
                "typical_processing_time_hours": 24,
                "success_probability": 0.75,
                "description": "Medium-risk claims reviewed by fraud analysts and AI system"
            },
            3: {
                "name": "Institutional Verification",
                "requires_human_review": True,
                "requires_institution_review": True,
                "typical_processing_time_hours": 72,
                "success_probability": 0.60,
                "description": "High-value claims require institutional verification (banks, govt agencies)"
            }
        }
        
        return rules.get(level, rules[3])


class GuardianIntegrityService:
    """
    Main Guardian Integrity service
    Manages claim assessment, institutional review, and appeal process
    """
    
    def __init__(self):
        self.scorer = IntegrityScorer()
        self.classifier = ClaimClassifier()
    
    def assess_claim_integrity(
        self,
        identity_id: int,
        verification: IdentityVerification,
        fraud_score: float,
        asset_value: Optional[float] = None,
        db: Session = None
    ) -> GuardianIntegrity:
        """
        Full integrity assessment for a claim
        
        Args:
            identity_id: Identity making claim
            verification: Identity verification object
            fraud_score: Fraud detection score (0.0-1.0)
            asset_value: Asset value (optional)
            db: Database session
            
        Returns:
            GuardianIntegrity object with assessment
        """
        # Calculate component scores
        identity_confidence = self.scorer.calculate_identity_confidence(verification)
        document_authenticity = self.scorer.calculate_document_authenticity(verification)
        behavior_risk = self.scorer.calculate_behavior_risk(fraud_score)
        
        # Calculate overall integrity score
        overall_score = self.scorer.calculate_overall_integrity_score(
            identity_confidence,
            document_authenticity,
            behavior_risk
        )
        
        # Classify claim
        claim_level = self.classifier.classify_claim(overall_score, asset_value, identity_id)
        
        # Create or update integrity record
        if db:
            integrity = db.query(GuardianIntegrity).filter(
                GuardianIntegrity.identity_id == identity_id
            ).first()
            
            if not integrity:
                integrity = GuardianIntegrity(identity_id=identity_id)
        else:
            integrity = GuardianIntegrity(identity_id=identity_id)
        
        # Set scores
        integrity.overall_score = overall_score
        integrity.identity_confidence = identity_confidence
        integrity.document_authenticity = document_authenticity
        integrity.behavior_risk = behavior_risk
        integrity.claim_level = claim_level
        integrity.updated_at = datetime.utcnow()
        
        if db:
            db.add(integrity)
            db.commit()
        
        return integrity
    
    def request_institutional_review(
        self,
        integrity_id: int,
        reason: str,
        db: Session = None
    ) -> GuardianIntegrity:
        """
        Request institutional review for claim
        
        Args:
            integrity_id: GuardianIntegrity record ID
            reason: Reason for requesting review
            db: Database session
            
        Returns:
            Updated GuardianIntegrity object
        """
        if not db:
            return None
        
        integrity = db.query(GuardianIntegrity).filter(
            GuardianIntegrity.integrity_id == integrity_id
        ).first()
        
        if integrity:
            integrity.claim_level = 3  # Escalate to institutional review
            integrity.institution_review_notes = reason
            integrity.updated_at = datetime.utcnow()
            db.commit()
        
        return integrity
    
    def submit_institution_review(
        self,
        integrity_id: int,
        reviewer_id: int,
        approved: bool,
        notes: str,
        db: Session = None
    ) -> GuardianIntegrity:
        """
        Submit institutional review decision
        
        Args:
            integrity_id: GuardianIntegrity record ID
            reviewer_id: Institution reviewer user ID
            approved: Whether claim is approved
            notes: Review notes and findings
            db: Database session
            
        Returns:
            Updated GuardianIntegrity object
        """
        if not db:
            return None
        
        integrity = db.query(GuardianIntegrity).filter(
            GuardianIntegrity.integrity_id == integrity_id
        ).first()
        
        if integrity:
            integrity.institution_reviewed = True
            integrity.institution_reviewer_id = reviewer_id
            integrity.institution_review_notes = notes
            
            # Boost integrity score if approved by institution
            if approved:
                integrity.overall_score = min(1.0, integrity.overall_score + 0.2)
            else:
                # Penalize if rejected
                integrity.overall_score = max(0.0, integrity.overall_score - 0.3)
            
            integrity.updated_at = datetime.utcnow()
            integrity.last_reviewed_at = datetime.utcnow()
            db.commit()
        
        return integrity
    
    def file_appeal(
        self,
        integrity_id: int,
        appeal_notes: str,
        db: Session = None
    ) -> GuardianIntegrity:
        """
        File appeal against claim decision
        
        Args:
            integrity_id: GuardianIntegrity record ID
            appeal_notes: Reason for appeal
            db: Database session
            
        Returns:
            Updated GuardianIntegrity object with appeal filed
        """
        if not db:
            return None
        
        integrity = db.query(GuardianIntegrity).filter(
            GuardianIntegrity.integrity_id == integrity_id
        ).first()
        
        if integrity:
            integrity.appeal_filed = True
            integrity.appeal_status = "pending"
            integrity.appeal_notes = appeal_notes
            integrity.updated_at = datetime.utcnow()
            db.commit()
        
        return integrity
    
    def resolve_appeal(
        self,
        integrity_id: int,
        approved: bool,
        resolution_notes: str,
        db: Session = None
    ) -> GuardianIntegrity:
        """
        Resolve appeal decision
        
        Args:
            integrity_id: GuardianIntegrity record ID
            approved: Whether appeal is approved
            resolution_notes: Appeal resolution notes
            db: Database session
            
        Returns:
            Updated GuardianIntegrity object
        """
        if not db:
            return None
        
        integrity = db.query(GuardianIntegrity).filter(
            GuardianIntegrity.integrity_id == integrity_id
        ).first()
        
        if integrity:
            integrity.appeal_status = "approved" if approved else "rejected"
            integrity.appeal_notes = resolution_notes
            
            # Adjust integrity score based on appeal outcome
            if approved:
                integrity.overall_score = min(1.0, integrity.overall_score + 0.15)
            
            integrity.updated_at = datetime.utcnow()
            db.commit()
        
        return integrity
    
    def generate_integrity_report(
        self,
        integrity: GuardianIntegrity
    ) -> Dict:
        """
        Generate human-readable integrity report
        
        Args:
            integrity: GuardianIntegrity object
            
        Returns:
            Dictionary with detailed report
        """
        claim_rules = self.classifier.get_processing_rules(integrity.claim_level)
        
        return {
            "integrity_id": integrity.integrity_id,
            "identity_id": integrity.identity_id,
            "overall_integrity_score": round(integrity.overall_score, 2),
            "component_scores": {
                "identity_confidence": round(integrity.identity_confidence, 2),
                "document_authenticity": round(integrity.document_authenticity, 2),
                "behavior_risk": round(integrity.behavior_risk, 2)
            },
            "claim_classification": {
                "level": integrity.claim_level,
                "name": claim_rules["name"],
                "description": claim_rules["description"],
                "typical_processing_time": claim_rules["typical_processing_time_hours"],
                "success_probability": claim_rules["success_probability"]
            },
            "institutional_verification": {
                "required": claim_rules["requires_institution_review"],
                "completed": integrity.institution_reviewed,
                "reviewer_id": integrity.institution_reviewer_id
            },
            "appeal_process": {
                "appeal_filed": integrity.appeal_filed,
                "appeal_status": integrity.appeal_status,
                "notes": integrity.appeal_notes
            },
            "timestamp": {
                "created": integrity.created_at.isoformat() if integrity.created_at else None,
                "last_reviewed": integrity.last_reviewed_at.isoformat() if integrity.last_reviewed_at else None
            }
        }


# Global service instance
guardian_integrity_service = GuardianIntegrityService()
