"""
Audit Logging System for Safiri Asset Intelligence
Financial-grade audit trail for compliance and fraud investigation
Records every action systematically for forensic analysis
"""

from datetime import datetime
from typing import Optional, Dict
from sqlalchemy.orm import Session
from app.models import AuditLog, User
from app.config import security_config
import json


class AuditLogger:
    """
    Centralized audit logging service
    Every action is recorded immutably for investigation and compliance
    """
    
    def __init__(self):
        self.enabled = security_config.AUDIT_LOG_ENABLED
    
    def log_action(
        self,
        action: str,
        action_type: str,
        user_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        device_fingerprint: Optional[str] = None,
        status_code: int = 200,
        result: str = "success",
        query_data: Optional[Dict] = None,
        error_message: Optional[str] = None,
        fraud_score: float = 0.0,
        db: Session = None
    ) -> Optional[AuditLog]:
        """
        Log an action with comprehensive context
        
        Args:
            action: General action (search, claim, upload, etc.)
            action_type: Specific action type (identity_query, asset_claim, etc.)
            user_id: User performing action
            resource_type: Type of resource accessed (identity, asset, document)
            resource_id: Specific resource ID
            ip_address: Client IP address
            user_agent: Browser user agent
            device_fingerprint: Device fingerprint
            status_code: HTTP status code
            result: success, failure, blocked
            query_data: Query parameters (safely redact PII)
            error_message: Error if action failed
            fraud_score: Fraud score if suspicious
            db: Database session
            
        Returns:
            Created AuditLog or None
        """
        if not self.enabled or not db:
            return None
        
        # Redact sensitive data from query
        safe_query = self._redact_query(query_data)
        
        # Determine if suspicious
        is_suspicious = fraud_score > security_config.FRAUD_BEHAVIOR_ANOMALY_THRESHOLD
        
        # Create audit log
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            action_type=action_type,
            result=result,
            resource_type=resource_type,
            resource_id=resource_id,
            query_data=safe_query,
            ip_address=ip_address,
            user_agent=user_agent,
            device_fingerprint=device_fingerprint,
            status_code=status_code,
            error_message=error_message,
            flagged_as_suspicious=is_suspicious,
            fraud_score=fraud_score,
            created_at=datetime.utcnow()
        )
        
        db.add(audit_log)
        db.commit()
        
        # Log to stdout for backup
        self._log_to_stdout(audit_log)
        
        return audit_log
    
    def log_identity_query(
        self,
        user_id: Optional[int],
        query: str,
        identity_id: int,
        ip_address: str,
        user_agent: str,
        device_fingerprint: str,
        found: bool = False,
        fraud_score: float = 0.0,
        db: Session = None
    ) -> Optional[AuditLog]:
        """
        Log identity search query
        
        Args:
            user_id: User performing search
            query: Search query string
            identity_id: Identity found (if any)
            ip_address: Client IP
            user_agent: Browser user agent
            device_fingerprint: Device fingerprint
            found: Whether identity was found
            fraud_score: Fraud risk score
            db: Database session
            
        Returns:
            Created AuditLog
        """
        if not security_config.AUDIT_IDENTITY_QUERIES:
            return None
        
        # Redact name from query
        safe_query = {
            "query_length": len(query),
            "query_type": self._detect_query_type(query),
            "found": found
        }
        
        return self.log_action(
            action="search",
            action_type="identity_query",
            user_id=user_id,
            resource_type="identity",
            resource_id=identity_id if found else None,
            ip_address=ip_address,
            user_agent=user_agent,
            device_fingerprint=device_fingerprint,
            query_data=safe_query,
            result="success" if found else "not_found",
            fraud_score=fraud_score,
            db=db
        )
    
    def log_asset_claim(
        self,
        user_id: int,
        identity_id: int,
        asset_id: int,
        ip_address: str,
        user_agent: str,
        device_fingerprint: str,
        status: str = "pending",
        fraud_score: float = 0.0,
        db: Session = None
    ) -> Optional[AuditLog]:
        """
        Log asset claim attempt
        
        Args:
            user_id: User making claim
            identity_id: Identity claiming asset
            asset_id: Asset being claimed
            ip_address: Client IP
            user_agent: Browser user agent
            device_fingerprint: Device fingerprint
            status: pending, approved, rejected
            fraud_score: Fraud risk score
            db: Database session
            
        Returns:
            Created AuditLog
        """
        if not security_config.AUDIT_ASSET_CLAIMS:
            return None
        
        return self.log_action(
            action="claim",
            action_type="asset_claim",
            user_id=user_id,
            resource_type="asset",
            resource_id=asset_id,
            ip_address=ip_address,
            user_agent=user_agent,
            device_fingerprint=device_fingerprint,
            query_data={"identity_id": identity_id, "claim_status": status},
            result="success",
            fraud_score=fraud_score,
            db=db
        )
    
    def log_document_upload(
        self,
        user_id: int,
        document_type: str,
        file_hash: str,
        ip_address: str,
        user_agent: str,
        device_fingerprint: str,
        success: bool = True,
        error: Optional[str] = None,
        db: Session = None
    ) -> Optional[AuditLog]:
        """
        Log document upload
        
        Args:
            user_id: User uploading document
            document_type: Type of document
            file_hash: SHA256 hash of file
            ip_address: Client IP
            user_agent: Browser user agent
            device_fingerprint: Device fingerprint
            success: Whether upload succeeded
            error: Error message if failed
            db: Database session
            
        Returns:
            Created AuditLog
        """
        if not security_config.AUDIT_DOCUMENT_UPLOADS:
            return None
        
        return self.log_action(
            action="upload",
            action_type="document_upload",
            user_id=user_id,
            resource_type="document",
            ip_address=ip_address,
            user_agent=user_agent,
            device_fingerprint=device_fingerprint,
            query_data={
                "document_type": document_type,
                "file_hash": file_hash
            },
            result="success" if success else "failure",
            error_message=error,
            db=db
        )
    
    def log_authentication_attempt(
        self,
        username: str,
        ip_address: str,
        user_agent: str,
        success: bool = True,
        error: Optional[str] = None,
        db: Session = None
    ) -> Optional[AuditLog]:
        """
        Log authentication attempt
        
        Args:
            username: Username attempting to login
            ip_address: Client IP
            user_agent: Browser user agent
            success: Whether authentication succeeded
            error: Error message if failed
            db: Database session
            
        Returns:
            Created AuditLog
        """
        if not security_config.AUDIT_FAILED_AUTHENTICATIONS and not success:
            return None
        
        return self.log_action(
            action="authenticate",
            action_type="user_login",
            ip_address=ip_address,
            user_agent=user_agent,
            query_data={"username": username},
            result="success" if success else "failure",
            error_message=error if not success else None,
            status_code=200 if success else 401,
            db=db
        )
    
    def log_admin_action(
        self,
        admin_user_id: int,
        action_type: str,
        resource_type: str,
        resource_id: int,
        changes: Dict,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        db: Session = None
    ) -> Optional[AuditLog]:
        """
        Log administrative action
        
        Args:
            admin_user_id: Admin user performing action
            action_type: Type of admin action (user_banned, claim_rejected, etc.)
            resource_type: Type of resource affected
            resource_id: ID of affected resource
            changes: Dictionary of changes made
            reason: Reason for action
            ip_address: Admin IP address
            user_agent: Admin browser user agent
            db: Database session
            
        Returns:
            Created AuditLog
        """
        if not security_config.AUDIT_ADMIN_ACTIONS:
            return None
        
        return self.log_action(
            action="admin_action",
            action_type=action_type,
            user_id=admin_user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            query_data={
                "changes": changes,
                "reason": reason
            },
            result="success",
            db=db
        )
    
    def get_audit_trail(
        self,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        user_id: Optional[int] = None,
        days: int = 7,
        db: Session = None
    ) -> list:
        """
        Retrieve audit trail for investigation
        
        Args:
            resource_type: Filter by resource type
            resource_id: Filter by resource ID
            user_id: Filter by user
            days: Number of days to retrieve
            db: Database session
            
        Returns:
            List of audit logs
        """
        if not db:
            return []
        
        from datetime import timedelta
        
        query = db.query(AuditLog)
        
        # Filter by date
        since = datetime.utcnow() - timedelta(days=days)
        query = query.filter(AuditLog.created_at >= since)
        
        # Optional filters
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if resource_id:
            query = query.filter(AuditLog.resource_id == resource_id)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        return query.order_by(AuditLog.created_at.desc()).all()
    
    def analyze_suspicious_activity(
        self,
        ip_address: str,
        days: int = 7,
        db: Session = None
    ) -> Dict:
        """
        Analyze suspicious activity from IP address
        
        Args:
            ip_address: IP to analyze
            days: Number of days to review
            db: Database session
            
        Returns:
            Dictionary with activity analysis
        """
        if not db:
            return {}
        
        from datetime import timedelta
        
        since = datetime.utcnow() - timedelta(days=days)
        
        logs = db.query(AuditLog).filter(
            AuditLog.ip_address == ip_address,
            AuditLog.created_at >= since
        ).all()
        
        # Analyze patterns
        identity_queries = len([l for l in logs if l.action_type == "identity_query"])
        asset_claims = len([l for l in logs if l.action_type == "asset_claim"])
        flagged = len([l for l in logs if l.flagged_as_suspicious])
        
        return {
            "ip_address": ip_address,
            "total_actions": len(logs),
            "identity_queries": identity_queries,
            "asset_claims": asset_claims,
            "flagged_as_suspicious": flagged,
            "average_fraud_score": sum(l.fraud_score for l in logs) / len(logs) if logs else 0,
            "first_action": logs[-1].created_at if logs else None,
            "last_action": logs[0].created_at if logs else None
        }
    
    @staticmethod
    def _redact_query(query_data: Optional[Dict]) -> Optional[Dict]:
        """
        Redact sensitive PII from logged query data
        
        Args:
            query_data: Query parameters to redact
            
        Returns:
            Redacted query data
        """
        if not query_data:
            return None
        
        redacted = {}
        sensitive_keys = ["password", "pin", "otp", "ssn", "national_id"]
        
        for key, value in query_data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                redacted[key] = "***REDACTED***"
            else:
                redacted[key] = value
        
        return redacted
    
    @staticmethod
    def _detect_query_type(query: str) -> str:
        """
        Detect type of query (name, ID, email, phone)
        
        Args:
            query: Query string
            
        Returns:
            Query type
        """
        if "@" in query:
            return "email"
        elif len(query) > 10 and query.isdigit():
            return "id_number"
        elif query.startswith("+") or query.startswith("254"):
            return "phone"
        else:
            return "name"
    
    @staticmethod
    def _log_to_stdout(audit_log: AuditLog):
        """
        Write audit log to stdout for operational visibility
        
        Args:
            audit_log: Audit log entry
        """
        timestamp = audit_log.created_at.isoformat()
        user = audit_log.user_id or "anonymous"
        action = audit_log.action_type or audit_log.action
        
        print(f"[AUDIT] {timestamp} | User: {user} | Action: {action} | IP: {audit_log.ip_address} | Result: {audit_log.result}")


# Global audit logger instance
audit_logger = AuditLogger()
