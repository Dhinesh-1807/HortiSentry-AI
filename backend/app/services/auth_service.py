import logging
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.models import User
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.core.constants import UserRole, AuditAction, VerificationStatus, AccountStatus
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)
security_bearer = HTTPBearer(auto_error=False)

class AuthService:
    @staticmethod
    def register_user(
        db: Session,
        name: str,
        email: str,
        password: str,
        role: str = UserRole.FARMER,
        phone: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        email_clean = email.strip().lower()
        existing = db.query(User).filter(User.email == email_clean).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"An account with email '{email_clean}' already exists."
            )

        role_clean = role.strip().upper()
        if role_clean not in [UserRole.FARMER, UserRole.EXPERT, UserRole.ADMIN]:
            role_clean = UserRole.FARMER

        # Determine verification status
        if role_clean == UserRole.EXPERT:
            verification_status = VerificationStatus.PENDING
        else:
            verification_status = VerificationStatus.NOT_REQUIRED

        # Generate anonymous non-identifiable farmer code if role is FARMER
        farmer_code = None
        if role_clean == UserRole.FARMER:
            base_count = db.query(User).filter(User.role == UserRole.FARMER).count() + 1
            code_candidate = f"HS-FARMER-{base_count:04d}"
            while db.query(User).filter(User.farmer_code == code_candidate).first():
                base_count += 1
                code_candidate = f"HS-FARMER-{base_count:04d}"
            farmer_code = code_candidate

        user = User(
            name=name.strip(),
            email=email_clean,
            password_hash=hash_password(password),
            role=role_clean,
            verification_status=verification_status,
            account_status=AccountStatus.ACTIVE,
            farmer_code=farmer_code,
            phone=phone,
            location=location,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        AuditService.record(
            db=db,
            action=AuditAction.USER_REGISTER,
            user_id=user.id,
            user_email=user.email,
            entity_type="User",
            entity_id=user.id,
            details={"role": user.role, "farmer_code": user.farmer_code, "verification_status": user.verification_status}
        )

        # DO NOT return token upon registration; user must log in manually
        return {
            "message": "Registration successful! Please sign in with your new account.",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "verification_status": user.verification_status,
                "account_status": user.account_status,
                "farmer_code": user.farmer_code,
                "location": user.location
            }
        }

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Dict[str, Any]:
        email_clean = email.strip().lower()
        user = db.query(User).filter(User.email == email_clean).first()
        if not user or not user.password_hash or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password credentials."
            )

        if not user.is_active or user.account_status == AccountStatus.SUSPENDED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deactivated or suspended. Please contact the administrator."
            )

        AuditService.record(
            db=db,
            action=AuditAction.USER_LOGIN,
            user_id=user.id,
            user_email=user.email,
            entity_type="User",
            entity_id=user.id
        )

        token = create_access_token({
            "sub": user.id,
            "email": user.email,
            "role": user.role,
            "verification_status": user.verification_status or VerificationStatus.NOT_REQUIRED
        })
        return {
            "token": token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "verification_status": user.verification_status or VerificationStatus.NOT_REQUIRED,
                "account_status": user.account_status or AccountStatus.ACTIVE,
                "farmer_code": user.farmer_code,
                "location": user.location
            }
        }

    @staticmethod
    def get_demo_user(db: Session, role: str) -> Dict[str, Any]:
        role_upper = role.upper()
        email_map = {
            "FARMER": "farmer@hortisentry.demo",
            "EXPERT": "expert@hortisentry.demo",
            "ADMIN": "admin@hortisentry.demo"
        }
        target_email = email_map.get(role_upper, "farmer@hortisentry.demo")
        user = db.query(User).filter(User.email == target_email).first()
        if not user:
            # Fallback to any user with this role
            user = db.query(User).filter(User.role == role_upper).first()

        if not user:
            raise HTTPException(status_code=404, detail=f"Demo account for role {role_upper} not found.")

        token = create_access_token({
            "sub": user.id,
            "email": user.email,
            "role": user.role,
            "verification_status": user.verification_status or VerificationStatus.NOT_REQUIRED
        })
        return {
            "token": token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "verification_status": user.verification_status or VerificationStatus.NOT_REQUIRED,
                "account_status": user.account_status or AccountStatus.ACTIVE,
                "farmer_code": user.farmer_code,
                "location": user.location
            }
        }

def get_current_user_optional(
    cred: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> Optional[User]:
    if not cred or not cred.credentials:
        return None
    payload = decode_access_token(cred.credentials)
    if not payload or "sub" not in payload:
        return None
    return db.query(User).filter(User.id == payload["sub"]).first()

def get_current_user(
    cred: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> User:
    if not cred or not cred.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required."
        )
    payload = decode_access_token(cred.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token."
        )
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User account not found.")
    return user

def get_current_verified_expert(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Ensures the user is authenticated, has EXPERT role, verification_status == VERIFIED,
    and account_status == ACTIVE. Otherwise returns HTTP 403.
    """
    if current_user.role != UserRole.EXPERT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Expert role required."
        )

    if not current_user.is_active or current_user.account_status == AccountStatus.SUSPENDED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your expert account has been suspended. Please contact the administrator."
        )

    if current_user.verification_status == VerificationStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your expert account is awaiting verification by the administrator."
        )
    elif current_user.verification_status == VerificationStatus.REJECTED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your expert registration was not approved. Please contact the administrator."
        )
    elif current_user.verification_status == VerificationStatus.SUSPENDED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your expert account has been suspended. Please contact the administrator."
        )
    elif current_user.verification_status != VerificationStatus.VERIFIED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Verified expert account required."
        )

    return current_user

def require_role(*allowed_roles: str):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires one of roles: {', '.join(allowed_roles)}"
            )
        if not current_user.is_active or current_user.account_status == AccountStatus.SUSPENDED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account has been suspended. Please contact the administrator."
            )
        return current_user
    return role_checker
