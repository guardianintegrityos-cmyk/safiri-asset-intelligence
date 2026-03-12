"""
Fraud Detection Engine for Safiri Asset Intelligence
Detects:
- Data scraping attempts (high search volume)
- Identity spoofing (repeated queries of same IDs)
- Device-based attacks (same device multiple claims)
- Behavioral anomalies (unusual search patterns)
- Mass IP attacks (single IP searching thousands of IDs)
"""

from datetime import datetime, timedelta
from typing import Tuple, Dict, Optional
from collections import defaultdict
from sqlalchemy.orm import Session
from app.models import (
    FraudDetectionEvent, AuditLog, User, IdentityVerification
)
from app.config import security_config


class DeviceFingerprinter:
    """
    Creates device fingerprints from user-agent and other signals
    Used to detect botnet attacks and coordinated fraud
    """
    
    @staticmethod
    def generate_fingerprint(user_agent: str, ip_address: str, accept_language: str = "") -> str:
        """
        Generate device fingerprint from multiple signals
        
        Args:
            user_agent: HTTP User-Agent header
            ip_address: Client IP address
            accept_language: Accept-Language header
            
        Returns:
            Device fingerprint hash
        """
        import hashlib
        
        fingerprint_data = f"{user_agent}||{ip_address}||{accept_language}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    @staticmethod
    def get_fingerprint_from_request(request: dict) -> str:
        """
        Extract device fingerprint from HTTP request
        
        Args:
            request: FastAPI request object
            
        Returns:
            Device fingerprint
        """
        user_agent = request.get("user_agent", "unknown")
        client_ip = request.get("client_ip", "unknown")
        
        return DeviceFingerprinter.generate_fingerprint(user_agent, client_ip)


class FraudDetectionEngine:
    """
    Real-time fraud detection with pattern analysis
    Tracks IP addresses, devices, and user behavior
    """
    
    def __init__(self):
        # In-memory tracking (use Redis for production)
        self.ip_searches = defaultdict(list)  # IP -> [search times]
        self.device_claims = defaultdict(list)  # device_fingerprint -> [claim times]
        self.identity_queries = defaultdict(int)  # identity_id -> query count
        self.repeated_ids_from_ip = defaultdict(set)  # IP -> set of queried IDs
    
    def check_search_rate_limit(self, ip_address: str, db: Session) -> Tuple[bool, str, float]:
        """
        Check if IP has exceeded search rate limit
        
        Args:
            ip_address: Client IP address
            db: Database session
            
        Returns:
            Tuple of (is_clean, message, fraud_score)
        """
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)
        
        # Count searches in last hour
        recent_searches = [
            time for time in self.ip_searches[ip_address]
            if time > one_hour_ago
        ]
        
        self.ip_searches[ip_address] = recent_searches
        self.ip_searches[ip_address].append(now)
        
        search_count = len(recent_searches) + 1  # +1 for current search
        
        if search_count > security_config.FRAUD_SEARCH_LIMIT_PER_HOUR:
            fraud_score = min(1.0, search_count / (security_config.FRAUD_SEARCH_LIMIT_PER_HOUR * 2))
            return False, f"Rate limit exceeded: {search_count} searches in 1 hour", fraud_score
        
        return True, "Search rate OK", 0.0
    
    def check_repeated_identity_queries(
        self,
        ip_address: str,
        identity_id: int,
        db: Session
    ) -> Tuple[bool, str, float]:
        """
        Detect repeated queries of same identity (indicator of spoofing attempt)
        
        Args:
            ip_address: Client IP address
            identity_id: Identity being queried
            db: Database session
            
        Returns:
            Tuple of (is_clean, message, fraud_score)
        """
        # Track unique IDs queried from this IP
        self.repeated_ids_from_ip[ip_address].add(identity_id)
        
        # Count how many times this exact identity was queried from this IP
        identity_key = f"{ip_address}:{identity_id}"
        self.identity_queries[identity_key] += 1
        
        query_count = self.identity_queries[identity_key]
        
        # Repeated queries of same ID indicate potential spoofing
        if query_count > 3:
            fraud_score = 0.85
            return False, f"Repeated queries of same identity: {query_count} times", fraud_score
        
        return True, "Identity query OK", 0.0
    
    def check_mass_id_enumeration(self, ip_address: str, db: Session) -> Tuple[bool, str, float]:
        """
        Detect mass enumeration attacks (querying many different IDs from same IP)
        Indicator of data scraping
        
        Args:
            ip_address: Client IP address
            db: Database session
            
        Returns:
            Tuple of (is_clean, message, fraud_score)
        """
        unique_ids_queried = len(self.repeated_ids_from_ip[ip_address])
        
        # Threshold for suspicious behavior
        if unique_ids_queried > 50:  # arbitrary threshold
            fraud_score = min(1.0, unique_ids_queried / 100)
            return False, f"Mass ID enumeration: {unique_ids_queried} different IDs queried", fraud_score
        
        return True, "ID enumeration OK", 0.0
    
    def check_device_fingerprint(self, device_fingerprint: str, db: Session) -> Tuple[bool, str, float]:
        """
        Detect suspicious device patterns
        
        Args:
            device_fingerprint: Device fingerprint hash
            db: Database session
            
        Returns:
            Tuple of (is_clean, message, fraud_score)
        """
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)
        
        # Count claims from this device
        recent_claims = [
            time for time in self.device_claims[device_fingerprint]
            if time > one_hour_ago
        ]
        
        claim_count = len(recent_claims)
        
        if claim_count > 5:  # More than 5 claims from same device in 1 hour
            fraud_score = min(1.0, claim_count / 10)
            return False, f"Suspicious device activity: {claim_count} claims in 1 hour", fraud_score
        
        return True, "Device activity OK", 0.0
    
    def analyze_behavior(
        self,
        ip_address: str,
        device_fingerprint: str,
        identity_id: int,
        db: Session
    ) -> Dict[str, any]:
        """
        Comprehensive behavioral analysis for fraud scoring
        
        Args:
            ip_address: Client IP address
            device_fingerprint: Device fingerprint
            identity_id: Identity being accessed
            db: Database session
            
        Returns:
            Dictionary with fraud analysis results
        """
        results = {
            "fraud_score": 0.0,
            "is_suspicious": False,
            "flags": [],
            "checks": {}
        }
        
        # Run multiple checks
        checks = [
            ("Search Rate Limit", self.check_search_rate_limit(ip_address, db)),
            ("Repeated Identity Queries", self.check_repeated_identity_queries(ip_address, identity_id, db)),
            ("Mass ID Enumeration", self.check_mass_id_enumeration(ip_address, db)),
            ("Device Fingerprint", self.check_device_fingerprint(device_fingerprint, db))
        ]
        
        fraud_scores = []
        for check_name, (is_clean, message, score) in checks:
            results["checks"][check_name] = {
                "is_clean": is_clean,
                "message": message,
                "score": score
            }
            
            if not is_clean:
                results["flags"].append(f"{check_name}: {message}")
                fraud_scores.append(score)
        
        # Aggregate fraud scores
        if fraud_scores:
            results["fraud_score"] = sum(fraud_scores) / len(fraud_scores)
            results["is_suspicious"] = results["fraud_score"] > security_config.FRAUD_BEHAVIOR_ANOMALY_THRESHOLD
        
        return results
    
    def should_block_user(
        self,
        ip_address: str,
        device_fingerprint: str,
        db: Session
    ) -> Tuple[bool, Optional[datetime]]:
        """
        Determine if user should be temporarily blocked
        
        Args:
            ip_address: Client IP address
            device_fingerprint: Device fingerprint
            db: Database session
            
        Returns:
            Tuple of (should_block, unblock_time)
        """
        # Check if IP has recent fraud events
        recent_events = db.query(FraudDetectionEvent).filter(
            FraudDetectionEvent.ip_address == ip_address,
            FraudDetectionEvent.action_taken == "blocked",
            FraudDetectionEvent.blocked_until > datetime.utcnow()
        ).first()
        
        if recent_events:
            return True, recent_events.blocked_until
        
        return False, None
    
    def log_fraud_event(
        self,
        event_type: str,
        ip_address: str,
        device_fingerprint: str,
        severity: str,
        fraud_analysis: Dict,
        db: Session
    ) -> FraudDetectionEvent:
        """
        Log fraud detection event for investigation
        
        Args:
            event_type: Type of fraud event
            ip_address: Client IP address
            device_fingerprint: Device fingerprint
            severity: low, medium, high, critical
            fraud_analysis: Result from analyze_behavior()
            db: Database session
            
        Returns:
            Created FraudDetectionEvent
        """
        event = FraudDetectionEvent(
            event_type=event_type,
            severity=severity,
            ip_address=ip_address,
            device_fingerprint=device_fingerprint,
            fraud_score=fraud_analysis.get("fraud_score", 0.0),
            action_taken="warned" if severity in ["low", "medium"] else "blocked"
        )
        
        # Set block duration based on severity
        if event.action_taken == "blocked":
            duration_minutes = {
                "high": 60,
                "critical": 1440  # 24 hours
            }.get(severity, 60)
            
            event.blocked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        
        db.add(event)
        db.commit()
        
        return event
    
    def verify_before_claim(
        self,
        user_id: int,
        identity_id: int,
        ip_address: str,
        device_fingerprint: str,
        db: Session
    ) -> Tuple[bool, str, Optional[Dict]]:
        """
        Pre-claim fraud check
        Must pass before allowing asset claim
        
        Args:
            user_id: User making claim
            identity_id: Identity being claimed
            ip_address: Client IP address
            device_fingerprint: Device fingerprint
            db: Database session
            
        Returns:
            Tuple of (is_verified, message, analysis_details)
        """
        # Check if user is blocked
        should_block, unblock_time = self.should_block_user(ip_address, device_fingerprint, db)
        if should_block:
            return False, f"Account temporarily blocked until {unblock_time}", None
        
        # Run behavioral analysis
        analysis = self.analyze_behavior(ip_address, device_fingerprint, identity_id, db)
        
        if analysis["is_suspicious"]:
            severity = "critical" if analysis["fraud_score"] > 0.9 else "high"
            
            # Log event
            self.log_fraud_event(
                event_type="suspicious_claim",
                ip_address=ip_address,
                device_fingerprint=device_fingerprint,
                severity=severity,
                fraud_analysis=analysis,
                db=db
            )
            
            return False, "Claim requires additional verification", analysis
        
        return True, "Claim verified", analysis


# Global fraud detection service
fraud_detection_engine = FraudDetectionEngine()
