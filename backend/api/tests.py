from unittest import mock

from django.contrib.auth.models import User
from django.core import signing
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import Order, Recipe


def chef_token():
    resp = APIClient().post("/api/chef/login/", {"username": "chef", "password": "kitchen123"})
    assert resp.status_code == 200, resp.content
    return resp.data["token"]


class OrderAccessTests(TestCase):
    """订单里有顾客姓名：匿名不可读写；普通用户只看自己的；改状态和删除只给主厨。"""

    def setUp(self):
        self.recipe = Recipe.objects.create(title="番茄炒蛋", cooking_time=10)
        self.alice = User.objects.create_user(username="alice@example.com", password="pw-alice-1")
        self.bob = User.objects.create_user(username="bob@example.com", password="pw-bob-1")
        self.legacy = Order.objects.create(customer_name="老顾客")

    def client_for(self, user):
        client = APIClient()
        client.force_authenticate(user)
        return client

    def place_order(self, user, name="Alice"):
        payload = {"customer_name": name, "items": [{"recipe": self.recipe.id, "quantity": 1, "note": ""}]}
        return self.client_for(user).post("/api/orders/", payload, format="json")

    def test_anonymous_cannot_list_retrieve_create_or_delete(self):
        anon = APIClient()
        self.assertEqual(anon.get("/api/orders/").status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(anon.get(f"/api/orders/{self.legacy.id}/").status_code, status.HTTP_401_UNAUTHORIZED)
        payload = {"customer_name": "x", "items": [{"recipe": self.recipe.id, "quantity": 1}]}
        self.assertEqual(anon.post("/api/orders/", payload, format="json").status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(anon.delete(f"/api/orders/{self.legacy.id}/").status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Order.objects.filter(id=self.legacy.id).exists())

    def test_created_order_belongs_to_requester(self):
        resp = self.place_order(self.alice)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.get(id=resp.data["id"]).user, self.alice)

    def test_owner_field_cannot_be_forged(self):
        payload = {"customer_name": "A", "user": self.bob.id,
                   "items": [{"recipe": self.recipe.id, "quantity": 1}]}
        resp = self.client_for(self.alice).post("/api/orders/", payload, format="json")
        self.assertEqual(Order.objects.get(id=resp.data["id"]).user, self.alice)

    def test_user_sees_only_own_orders(self):
        mine = self.place_order(self.alice).data["id"]
        theirs = self.place_order(self.bob, name="Bob").data["id"]
        alice = self.client_for(self.alice)
        ids = [o["id"] for o in alice.get("/api/orders/").data]
        self.assertEqual(ids, [mine])
        self.assertEqual(alice.get(f"/api/orders/{mine}/").status_code, status.HTTP_200_OK)
        self.assertEqual(alice.get(f"/api/orders/{theirs}/").status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(alice.get(f"/api/orders/{self.legacy.id}/").status_code, status.HTTP_404_NOT_FOUND)

    def test_customer_cannot_change_status_or_delete(self):
        mine = self.place_order(self.alice).data["id"]
        alice = self.client_for(self.alice)
        self.assertEqual(alice.patch(f"/api/orders/{mine}/", {"status": "completed"}, format="json").status_code,
                         status.HTTP_403_FORBIDDEN)
        self.assertEqual(alice.delete(f"/api/orders/{mine}/").status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Order.objects.get(id=mine).status, "pending")

    def test_chef_sees_all_and_updates_status(self):
        self.place_order(self.alice)
        chef = self.client_for(self.bob)
        chef.credentials(HTTP_X_CHEF_TOKEN=chef_token())
        self.assertEqual(len(chef.get("/api/orders/").data), 2)
        resp = chef.patch(f"/api/orders/{self.legacy.id}/", {"status": "cooking"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(Order.objects.get(id=self.legacy.id).status, "cooking")

    def test_forged_and_expired_chef_tokens_are_rejected(self):
        client = self.client_for(self.bob)
        client.credentials(HTTP_X_CHEF_TOKEN="0" * 32)
        self.assertEqual(len(client.get("/api/orders/").data), 0)
        self.assertEqual(client.patch(f"/api/orders/{self.legacy.id}/", {"status": "cooking"}, format="json").status_code,
                         status.HTTP_403_FORBIDDEN)

        token = chef_token()
        with mock.patch("api.permissions.CHEF_TOKEN_MAX_AGE", 0), mock.patch("time.time", return_value=10**10):
            client.credentials(HTTP_X_CHEF_TOKEN=token)
            self.assertEqual(client.patch(f"/api/orders/{self.legacy.id}/", {"status": "cooking"}, format="json").status_code,
                             status.HTTP_403_FORBIDDEN)


class ChefAuthTests(TestCase):
    def test_verify_rejects_unsigned_token(self):
        resp = APIClient().get("/api/chef/login/", HTTP_AUTHORIZATION="Bearer " + "a" * 32)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_verify_accepts_issued_token(self):
        resp = APIClient().get("/api/chef/login/", HTTP_AUTHORIZATION="Bearer " + chef_token())
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_verify_accepts_chef_header(self):
        client = APIClient()
        self.assertEqual(client.get("/api/chef/login/", HTTP_X_CHEF_TOKEN=chef_token()).status_code,
                         status.HTTP_200_OK)
        self.assertEqual(client.get("/api/chef/login/", HTTP_X_CHEF_TOKEN="b" * 32).status_code,
                         status.HTTP_401_UNAUTHORIZED)

    def test_wrong_password_gets_no_token(self):
        resp = APIClient().post("/api/chef/login/", {"username": "chef", "password": "nope"})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("token", resp.data)

    def test_token_is_signed_for_chef_username(self):
        value = signing.TimestampSigner(salt="kitchen.chef").unsign(chef_token())
        self.assertEqual(value, "chef")
