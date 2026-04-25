from rest_framework import status
from rest_framework.test import APITestCase

from offers.models import Detail, Package
from tests.utils import VALID_DETAILS, create_test_package, create_test_user


class OfferListViewGetTests(APITestCase):
    """Tests for GET /api/offers/"""

    def setUp(self):
        self.base_url = "/api/offers/"
        self.business_user = create_test_user("business", "seller_1")
        self.package = create_test_package(self.business_user, title="Test Offer")
        self.client.force_authenticate(user=self.business_user)

    def test_list_returns_200(self):
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_unauthenticated_returns_200(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_response_is_paginated(self):
        response = self.client.get(self.base_url)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)

    def test_list_returns_existing_offers(self):
        response = self.client.get(self.base_url)
        self.assertEqual(response.data["count"], 1)

    def test_list_offer_contains_expected_fields(self):
        response = self.client.get(self.base_url)
        offer = response.data["results"][0]
        expected_fields = {
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
            "user_details",
        }
        self.assertEqual(set(offer.keys()), expected_fields)

    def test_filter_by_creator_id_returns_matching_offers(self):
        other_user = create_test_user("business", "seller_2")
        create_test_package(other_user, title="Other Offer")
        response = self.client.get(self.base_url, {"creator_id": self.business_user.pk})
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["user"], self.business_user.pk)

    def test_filter_by_max_delivery_time_returns_matching_offers(self):
        response = self.client.get(self.base_url, {"max_delivery_time": 3})
        self.assertEqual(response.data["count"], 1)

    def test_filter_by_max_delivery_time_excludes_slower_offers(self):
        response = self.client.get(self.base_url, {"max_delivery_time": 1})
        self.assertEqual(response.data["count"], 0)

    def test_search_by_title_returns_matching_offers(self):
        response = self.client.get(self.base_url, {"search": "Test Offer"})
        self.assertEqual(response.data["count"], 1)

    def test_search_excludes_non_matching_offers(self):
        response = self.client.get(self.base_url, {"search": "XYZ_no_match"})
        self.assertEqual(response.data["count"], 0)


class OfferListViewPostTests(APITestCase):
    """Tests for POST /api/offers/"""

    def setUp(self):
        self.base_url = "/api/offers/"
        self.business_user = create_test_user("business", "seller_1")
        self.customer_user = create_test_user("customer", "buyer_1")
        self.valid_payload = {
            "title": "New Offer",
            "description": "An offer description",
            "details": VALID_DETAILS,
        }
        self.client.force_authenticate(user=self.business_user)

    def test_create_as_business_user_returns_201(self):
        response = self.client.post(self.base_url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_as_customer_user_returns_403(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.post(self.base_url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.base_url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_missing_title_returns_400(self):
        payload = {**self.valid_payload, "title": ""}
        response = self.client.post(self.base_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_missing_details_returns_400(self):
        payload = {"title": "New Offer", "description": "desc"}
        response = self.client.post(self.base_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_fewer_than_three_details_returns_400(self):
        payload = {**self.valid_payload, "details": [VALID_DETAILS[0]]}
        response = self.client.post(self.base_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_detail_missing_required_field_returns_400(self):
        incomplete_detail = {k: v for k, v in VALID_DETAILS[0].items() if k != "price"}
        payload = {
            **self.valid_payload,
            "details": [incomplete_detail, VALID_DETAILS[1], VALID_DETAILS[2]],
        }
        response = self.client.post(self.base_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_response_contains_expected_fields(self):
        response = self.client.post(self.base_url, self.valid_payload, format="json")
        expected_fields = {"id", "title", "image", "description", "details"}
        self.assertEqual(set(response.data.keys()), expected_fields)

    def test_create_assigns_offer_to_authenticated_user(self):
        response = self.client.post(self.base_url, self.valid_payload, format="json")
        package = Package.objects.get(pk=response.data["id"])
        self.assertEqual(package.user, self.business_user)


class OfferRetrieveUpdateDeleteViewGetTests(APITestCase):
    """Tests for GET /api/offers/<pk>/"""

    def setUp(self):
        self.base_url = "/api/offers"
        self.business_user = create_test_user("business", "seller_1")
        self.package = create_test_package(self.business_user)
        self.client.force_authenticate(user=self.business_user)

    def test_retrieve_existing_offer_returns_200(self):
        response = self.client.get(f"{self.base_url}/{self.package.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_offer_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(f"{self.base_url}/{self.package.pk}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_nonexistent_offer_returns_404(self):
        response = self.client.get(f"{self.base_url}/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_offer_contains_expected_fields(self):
        response = self.client.get(f"{self.base_url}/{self.package.pk}/")
        expected_fields = {
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
        }
        self.assertEqual(set(response.data.keys()), expected_fields)

    def test_retrieve_offer_by_other_user_returns_200(self):
        other_user = create_test_user("customer", "buyer_1")
        self.client.force_authenticate(user=other_user)
        response = self.client.get(f"{self.base_url}/{self.package.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class OfferRetrieveUpdateDeleteViewPatchTests(APITestCase):
    """Tests for PATCH /api/offers/<pk>/"""

    def setUp(self):
        self.base_url = "/api/offers"
        self.business_user = create_test_user("business", "seller_1")
        self.other_user = create_test_user("business", "seller_2")
        self.package = create_test_package(self.business_user)
        self.client.force_authenticate(user=self.business_user)

    def test_update_own_offer_returns_200(self):
        response = self.client.patch(
            f"{self.base_url}/{self.package.pk}/",
            {"title": "Updated Title"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_other_offer_returns_403(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(
            f"{self.base_url}/{self.package.pk}/",
            {"title": "Stolen Update"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.patch(
            f"{self.base_url}/{self.package.pk}/",
            {"title": "No Auth"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_title_persists(self):
        self.client.patch(
            f"{self.base_url}/{self.package.pk}/",
            {"title": "Persisted Title"},
            format="json",
        )
        self.package.refresh_from_db()
        self.assertEqual(self.package.title, "Persisted Title")

    def test_update_detail_id_remains_unchanged(self):
        # Spec: detail IDs must not change when patching — details are updated
        # in place, not deleted and recreated.
        original_detail_id = self.package.details.first().pk
        updated_basic = {**VALID_DETAILS[0], "price": 199.99}
        self.client.patch(
            f"{self.base_url}/{self.package.pk}/",
            {"details": [updated_basic]},
            format="json",
        )
        self.assertTrue(Detail.objects.filter(pk=original_detail_id).exists())

    def test_update_nonexistent_offer_returns_404(self):
        response = self.client.patch(
            f"{self.base_url}/99999/",
            {"title": "Ghost"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OfferRetrieveUpdateDeleteViewDeleteTests(APITestCase):
    """Tests for DELETE /api/offers/<pk>/"""

    def setUp(self):
        self.base_url = "/api/offers"
        self.business_user = create_test_user("business", "seller_1")
        self.other_user = create_test_user("business", "seller_2")
        self.package = create_test_package(self.business_user)
        self.client.force_authenticate(user=self.business_user)

    def test_delete_own_offer_returns_204(self):
        response = self.client.delete(f"{self.base_url}/{self.package.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_own_offer_removes_from_db(self):
        pk = self.package.pk
        self.client.delete(f"{self.base_url}/{pk}/")
        self.assertFalse(Package.objects.filter(pk=pk).exists())

    def test_delete_other_offer_returns_403(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(f"{self.base_url}/{self.package.pk}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.delete(f"{self.base_url}/{self.package.pk}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_nonexistent_offer_returns_404(self):
        response = self.client.delete(f"{self.base_url}/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OfferDetailRetrieveViewTests(APITestCase):
    """Tests for GET /api/offerdetails/<pk>/"""

    def setUp(self):
        self.base_url = "/api/offerdetails"
        self.business_user = create_test_user("business", "seller_1")
        self.package = create_test_package(self.business_user)
        self.detail = self.package.details.first()
        self.client.force_authenticate(user=self.business_user)

    def test_retrieve_detail_returns_200(self):
        response = self.client.get(f"{self.base_url}/{self.detail.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_detail_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(f"{self.base_url}/{self.detail.pk}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_nonexistent_detail_returns_404(self):
        response = self.client.get(f"{self.base_url}/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_detail_contains_expected_fields(self):
        response = self.client.get(f"{self.base_url}/{self.detail.pk}/")
        expected_fields = {
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        }
        self.assertEqual(set(response.data.keys()), expected_fields)

    def test_retrieve_detail_by_other_user_returns_200(self):
        other_user = create_test_user("customer", "buyer_1")
        self.client.force_authenticate(user=other_user)
        response = self.client.get(f"{self.base_url}/{self.detail.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
