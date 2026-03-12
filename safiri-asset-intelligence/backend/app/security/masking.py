"""
Data Masking Utilities for Safiri Asset Intelligence
Prevents identity harvesting by masking sensitive data in API responses
Implements privacy-by-design principles
"""

from app.config import security_config
import re


class DataMasker:
    """
    Masks sensitive personally identifiable information (PII)
    in API responses according to configured masking strategies
    """
    
    @staticmethod
    def mask_full_name(name: str) -> str:
        """
        Mask full name to prevent identity disclosure
        
        Strategies:
        - "partial": Show first letter + asterisks + last letter
          e.g., "James Mwangi" → "J**** M*****"
        - "full": Hide completely (for sensitive contexts)
          e.g., "James Mwangi" → "**** ****"
        
        Args:
            name: Full name to mask
            
        Returns:
            Masked name string
        """
        if not name or not security_config.MASK_SENSITIVE_DATA:
            return name
        
        parts = name.strip().split()
        mode = security_config.MASK_FULL_NAME_MODE
        
        masked_parts = []
        for part in parts:
            if len(part) <= 2:
                masked_parts.append("*" * len(part))
            elif mode == "partial":
                masked_parts.append(f"{part[0]}{'*' * (len(part) - 2)}{part[-1]}")
            else:  # "full"
                masked_parts.append("*" * len(part))
        
        return " ".join(masked_parts)
    
    @staticmethod
    def mask_national_id(id_number: str) -> str:
        """
        Mask national ID number
        
        Strategies:
        - "last_4": Show only last 4 digits
          e.g., "12345678" → "****5678"
        - "last_2": Show only last 2 digits
          e.g., "12345678" → "******78"
        
        Args:
            id_number: National ID to mask
            
        Returns:
            Masked ID string
        """
        if not id_number or not security_config.MASK_SENSITIVE_DATA:
            return id_number
        
        id_str = str(id_number).strip()
        mode = security_config.MASK_ID_NUMBER_MODE
        
        if mode == "last_4" and len(id_str) >= 4:
            return f"{'*' * (len(id_str) - 4)}{id_str[-4:]}"
        elif mode == "last_2" and len(id_str) >= 2:
            return f"{'*' * (len(id_str) - 2)}{id_str[-2:]}"
        else:
            return "*" * len(id_str)
    
    @staticmethod
    def mask_phone(phone: str) -> str:
        """
        Mask phone number
        
        Strategy: Show last 4 digits
        e.g., "+254712345678" → "+2547****5678"
        
        Args:
            phone: Phone number to mask
            
        Returns:
            Masked phone number
        """
        if not phone or not security_config.MASK_SENSITIVE_DATA:
            return phone
        
        phone_str = str(phone).strip()
        mode = security_config.MASK_PHONE_MODE
        
        if mode == "last_4" and len(phone_str) >= 4:
            return f"{phone_str[:len(phone_str) - 4]}****{phone_str[-4:]}"
        elif mode == "last_2" and len(phone_str) >= 2:
            return f"{phone_str[:len(phone_str) - 2]}**{phone_str[-2:]}"
        else:
            return "*" * len(phone_str)
    
    @staticmethod
    def mask_email(email: str) -> str:
        """
        Mask email address
        
        Strategies:
        - "domain_only": Show only domain
          e.g., "james@example.com" → "***@example.com"
        - "partial": Show first letter + domain
          e.g., "james@example.com" → "j***@example.com"
        
        Args:
            email: Email address to mask
            
        Returns:
            Masked email address
        """
        if not email or not security_config.MASK_SENSITIVE_DATA:
            return email
        
        email_str = str(email).strip()
        mode = security_config.MASK_EMAIL_MODE
        
        if "@" not in email_str:
            return email_str
        
        local, domain = email_str.split("@", 1)
        
        if mode == "domain_only":
            return f"***@{domain}"
        elif mode == "partial":
            return f"{local[0]}{'*' * (len(local) - 1)}@{domain}"
        else:
            return f"***@{domain}"
    
    @staticmethod
    def mask_account_number(account: str) -> str:
        """
        Mask bank account number
        Shows only last 4 digits
        
        e.g., "1234567890" → "****7890"
        
        Args:
            account: Account number to mask
            
        Returns:
            Masked account number
        """
        if not account or not security_config.MASK_SENSITIVE_DATA:
            return account
        
        account_str = str(account).strip()
        if len(account_str) >= 4:
            return f"{'*' * (len(account_str) - 4)}{account_str[-4:]}"
        return "*" * len(account_str)
    
    @staticmethod
    def mask_asset_amount(amount: float) -> dict:
        """
        Mask asset amount with range instead of exact value
        Prevents precise asset harvesting for fraudulent claims
        
        Example ranges:
        - 1000 → "1k - 2k"
        - 50000 → "50k - 60k"
        - 1000000 → "900k - 1.1M"
        
        Args:
            amount: Asset amount in currency units
            
        Returns:
            Dictionary with masked range and actual value for authorized access
        """
        if not security_config.MASK_SENSITIVE_DATA or amount is None:
            return {
                "exact_amount": amount,
                "masked_range": None,
                "show_exact": True
            }
        
        # Calculate lower and upper bounds (±10%)
        lower = amount * 0.9
        upper = amount * 1.1
        
        # Format ranges
        def format_currency(val):
            if val >= 1_000_000:
                return f"{val / 1_000_000:.1f}M"
            elif val >= 1_000:
                return f"{val / 1_000:.0f}k"
            else:
                return f"{val:.0f}"
        
        return {
            "exact_amount": amount,
            "masked_range": f"{format_currency(lower)} - {format_currency(upper)}",
            "show_exact": False
        }


class MaskedIdentity:
    """
    DTO (Data Transfer Object) for returning masked identity data
    Ensures sensitive fields are never exposed in API responses
    """
    
    def __init__(self, identity_data: dict):
        """
        Create masked identity response
        
        Args:
            identity_data: Raw identity dictionary from database
        """
        self.data = identity_data
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """
        Convert to API response dictionary with masked fields
        
        Args:
            include_sensitive: If True, include sensitive data (admin use only)
            
        Returns:
            Dictionary safe for API response
        """
        if include_sensitive:
            # Admin view - show all data
            return self.data
        
        # Public/user view - mask sensitive fields
        return {
            "identity_id": self.data.get("identity_id"),
            "name": DataMasker.mask_full_name(self.data.get("full_name")),
            "national_id": DataMasker.mask_national_id(self.data.get("national_id")),
            "phone": DataMasker.mask_phone(self.data.get("phone")),
            "email": DataMasker.mask_email(self.data.get("email")),
            "postal_address": "*" * 10 if self.data.get("postal_address") else None,
            "date_of_birth": "****-**-**",  # Never expose exact DOB in responses
            "verification_status": self.data.get("verification_status"),
            "integrity_score": self.data.get("integrity_score")
        }


class MaskedAsset:
    """
    DTO for returning masked asset information
    Shows asset type and range but not exact amounts (prevents fraud guidance)
    """
    
    def __init__(self, asset_data: dict):
        """
        Create masked asset response
        
        Args:
            asset_data: Raw asset dictionary from database
        """
        self.data = asset_data
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """
        Convert to API response with masked financial data
        
        Args:
            include_sensitive: If True, show exact amounts (admin use only)
            
        Returns:
            Dictionary safe for API response
        """
        amount_masked = DataMasker.mask_asset_amount(self.data.get("amount"))
        
        return {
            "asset_id": self.data.get("asset_id"),
            "asset_type": self.data.get("asset_type"),
            "institution": self.data.get("institution"),
            "account_number": DataMasker.mask_account_number(self.data.get("account_number")),
            "amount": amount_masked["exact_amount"] if include_sensitive else amount_masked["masked_range"],
            "status": self.data.get("status"),
            "match_confidence": self.data.get("match_confidence")
        }


# Global masker instance
data_masker = DataMasker()
