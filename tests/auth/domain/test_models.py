import uuid

from src.auth.domain.models import Role, User


def test_user_creation_defaults():
    """Test that User is created with default role and generated ID."""
    user = User(email="alice@example.com", hashed_password="hashed123")
    assert user.email == "alice@example.com"
    assert user.hashed_password == "hashed123"
    assert user.role == Role.USER
    assert user.id is not None
    assert isinstance(user.id, uuid.UUID)


def test_user_creation_with_admin_role():
    """Test that User can be created with admin role."""
    user = User(email="admin@example.com", hashed_password="hashed456", role=Role.ADMIN)
    assert user.role == Role.ADMIN


def test_role_values():
    """Test that Role enum has expected values."""
    assert Role.ADMIN == "admin"
    assert Role.USER == "user"
    assert Role.ADMIN.value == "admin"
    assert Role.USER.value == "user"


def test_user_with_explicit_id():
    """Test that User can be created with an explicit ID."""
    explicit_id = uuid.UUID("12345678-1234-5678-1234-567812345678")
    user = User(email="bob@example.com", hashed_password="hashed789", id=explicit_id)
    assert user.id == explicit_id


def test_user_email_validation():
    """Test that User email is validated correctly."""
    try:
        User(email="invalid-email", hashed_password="hashed000")
    except Exception as e:
        assert "value is not a valid email address" in str(e)
