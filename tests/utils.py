from django.contrib.auth import get_user_model

from offers.models import Detail, Package
from orders.models import Order
from reviews.models import Review

User = get_user_model()

BASIC_DETAIL = {
    "title": "Basic",
    "revisions": 1,
    "delivery_time_in_days": 3,
    "price": 99.99,
    "features": ["feature1"],
    "offer_type": "basic",
}

STANDARD_DETAIL = {
    "title": "Standard",
    "revisions": 3,
    "delivery_time_in_days": 5,
    "price": 149.99,
    "features": ["feature1", "feature2"],
    "offer_type": "standard",
}

PREMIUM_DETAIL = {
    "title": "Premium",
    "revisions": 5,
    "delivery_time_in_days": 7,
    "price": 199.99,
    "features": ["feature1", "feature2", "feature3"],
    "offer_type": "premium",
}

VALID_DETAILS = [BASIC_DETAIL, STANDARD_DETAIL, PREMIUM_DETAIL]


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


def create_test_package(user, title="Test Package"):
    """
    Helper to create a test package with one detail.

    Args:
        user (User): The owner of the package.
        title (str): Optional title for the package.
    """
    package = Package.objects.create(
        user=user,
        title=title,
        description="Test description",
    )
    Detail.objects.create(
        package=package,
        title="Basic",
        revisions=1,
        delivery_time_in_days=3,
        price=99.99,
        features=["feature1"],
        offer_type="basic",
    )
    return package


def create_test_order(customer_user, business_user, status="in_progress"):
    """
    Helper to create a test order between a customer and a business user.

    Args:
        customer_user (User): The customer placing the order.
        business_user (User): The business fulfilling the order.
        status (str): Optional order status (default: "in_progress").
    """
    package = create_test_package(business_user)
    detail = package.details.first()
    return Order.objects.create(
        customer_user=customer_user,
        business_user=business_user,
        detail=detail,
        title=detail.title,
        revisions=detail.revisions,
        delivery_time_in_days=detail.delivery_time_in_days,
        price=detail.price,
        features=detail.features,
        offer_type=detail.offer_type,
        status=status,
    )


def create_test_review(reviewer, business_user, rating=5, description="Great work!"):
    """
    Helper to create a test review from a customer for a business user.

    Args:
        reviewer (User): The customer leaving the review.
        business_user (User): The business being reviewed.
        rating (int): Optional star rating (default: 5).
        description (str): Optional review text.
    """
    return Review.objects.create(
        reviewer=reviewer,
        business_user=business_user,
        rating=rating,
        description=description,
    )
