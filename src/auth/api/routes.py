from fastapi import APIRouter, Depends

from src.auth.api.dependencies import get_current_user, get_login_user, get_register_user, require_role
from src.auth.api.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from src.auth.domain.models import Role, User
from src.auth.use_cases.login_user import LoginUser
from src.auth.use_cases.register_user import RegisterUser

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/sign-up", response_model=UserResponse, status_code=201)
async def register(body: RegisterRequest, use_case: RegisterUser = Depends(get_register_user)):
    """Register a new user."""
    user = await use_case.execute(email=body.email, password=body.password, role=Role.USER)
    return UserResponse(id=user.id, email=user.email, role=user.role.value)


@router.post("/sign-up-admin", response_model=UserResponse, status_code=201)
async def register_admin(
    body: RegisterRequest,
    use_case: RegisterUser = Depends(get_register_user),
    current_user: User = Depends(require_role("admin")),
):
    """Register a new admin user, restricted to existing admin users."""
    user = await use_case.execute(email=body.email, password=body.password, role=Role.ADMIN)
    return UserResponse(id=user.id, email=user.email, role=user.role.value)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, use_case: LoginUser = Depends(get_login_user)):
    """Authenticate and receive a JWT access token."""
    token = await use_case.execute(email=body.email, password=body.password)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get the currently authenticated user."""
    return UserResponse(id=current_user.id, email=current_user.email, role=current_user.role.value)
