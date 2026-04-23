from django.contrib.auth import get_user_model

User = get_user_model()


def create_test_user(user_type, username):
    """
    Helper to create a standard user

    Args:

    type (User.type): the user type of the instance to be created.

    """
    return User.objects.create_user(
        username=f"test_{username}_{user_type}",
        email=f"test_{username}_{user_type}@test.com",
        password="testPass123",
        type=user_type,
    )
