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


class ChefOnlyWriteTests(TestCase):
    """菜谱、库存、博客：访客只能读公开内容；写操作和 mode=chef 的读都要主厨令牌。"""

    def setUp(self):
        from .models import BlogPost, Ingredient, RecipeStep, Tag, Category
        self.recipe = Recipe.objects.create(title="公开菜", cooking_time=10, chef_notes="秘方")
        self.hidden = Recipe.objects.create(title="私房菜", cooking_time=10, is_public=False)
        self.ingredient = Ingredient.objects.create(name="鸡蛋")
        self.step = RecipeStep.objects.create(recipe=self.recipe, step_number=1, description="打蛋")
        self.tag = Tag.objects.create(name="python")
        self.category = Category.objects.create(name="笔记", slug="notes")
        self.post = BlogPost.objects.create(title="已发布", slug="pub", content="x", is_published=True)
        self.draft = BlogPost.objects.create(title="草稿", slug="draft", content="x", is_published=False)
        self.anon = APIClient()
        self.user = APIClient()
        self.user.force_authenticate(User.objects.create_user(username="u@example.com", password="pw-u-1"))
        self.chef = APIClient()
        self.chef.credentials(HTTP_X_CHEF_TOKEN=chef_token())

    def test_public_reads_still_work_for_guests(self):
        self.assertEqual(self.anon.get("/api/recipes/").status_code, status.HTTP_200_OK)
        self.assertEqual(self.anon.get(f"/api/recipes/{self.recipe.id}/").status_code, status.HTTP_200_OK)
        for url in ("/api/blog/posts/", "/api/blog/tags/", "/api/blog/categories/",
                    "/api/blog/posts/stats/", "/api/blog/posts/graph/", "/api/blog/posts/by-slug/pub/",
                    f"/api/blog/posts/{self.post.id}/"):
            self.assertEqual(self.anon.get(url).status_code, status.HTTP_200_OK, url)

    def test_guest_reads_hide_private_content(self):
        ids = [r["id"] for r in self.anon.get("/api/recipes/").data]
        self.assertNotIn(self.hidden.id, ids)
        self.assertNotIn("chef_notes", self.anon.get(f"/api/recipes/{self.recipe.id}/").data)
        slugs = [p["slug"] for p in self.anon.get("/api/blog/posts/").data]
        self.assertNotIn("draft", slugs)
        self.assertEqual(self.anon.get("/api/blog/posts/by-slug/draft/").status_code, status.HTTP_404_NOT_FOUND)

    def test_chef_mode_reads_need_chef_token(self):
        for client in (self.anon, self.user):
            for url in ("/api/recipes/?mode=chef", f"/api/recipes/{self.recipe.id}/?mode=chef",
                        "/api/blog/posts/?mode=chef", f"/api/blog/posts/{self.draft.id}/?mode=chef",
                        "/api/blog/posts/by-slug/draft/?mode=chef"):
                self.assertIn(client.get(url).status_code,
                              (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN), url)
        self.assertEqual(self.chef.get("/api/recipes/?mode=chef").status_code, status.HTTP_200_OK)
        self.assertEqual(self.chef.get(f"/api/blog/posts/{self.draft.id}/?mode=chef").data["title"], "草稿")
        self.assertIn(self.hidden.id, [r["id"] for r in self.chef.get("/api/recipes/?mode=chef").data])

    def test_kitchen_back_office_endpoints_are_chef_only(self):
        for url in ("/api/ingredients/", "/api/recipe-steps/", "/api/recipe-ingredients/",
                    f"/api/recipe-steps/?recipe={self.recipe.id}"):
            for client in (self.anon, self.user):
                self.assertIn(client.get(url).status_code,
                              (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN), url)
            self.assertEqual(self.chef.get(url).status_code, status.HTTP_200_OK, url)

    def test_writes_are_rejected_without_chef_token(self):
        from .models import BlogPost, Ingredient
        writes = [
            ("post", "/api/recipes/", {"title": "x", "cooking_time": 1}),
            ("patch", f"/api/recipes/{self.recipe.id}/", {"title": "改"}),
            ("delete", f"/api/recipes/{self.recipe.id}/", None),
            ("post", "/api/ingredients/", {"name": "盐"}),
            ("patch", f"/api/ingredients/{self.ingredient.id}/", {"name": "改"}),
            ("delete", f"/api/ingredients/{self.ingredient.id}/", None),
            ("post", "/api/recipe-steps/batch-update/", {"recipe_id": self.recipe.id, "steps": []}),
            ("delete", f"/api/recipe-steps/{self.step.id}/", None),
            ("post", "/api/recipe-ingredients/batch-update/", {"recipe_id": self.recipe.id, "ingredients": []}),
            ("post", "/api/blog/posts/", {"title": "x", "content": "x"}),
            ("patch", f"/api/blog/posts/{self.post.id}/", {"title": "改"}),
            ("delete", f"/api/blog/posts/{self.post.id}/", None),
            ("post", "/api/blog/posts/upload-image/", {}),
            ("post", "/api/blog/tags/", {"name": "新标签"}),
            ("delete", f"/api/blog/tags/{self.tag.id}/", None),
            ("post", "/api/blog/categories/", {"name": "新分类", "slug": "new"}),
            ("delete", f"/api/blog/categories/{self.category.id}/", None),
        ]
        bad_chef = APIClient()
        bad_chef.credentials(HTTP_X_CHEF_TOKEN="0" * 32)
        for client in (self.anon, self.user, bad_chef):
            for method, url, data in writes:
                resp = getattr(client, method)(url, data, format="json")
                self.assertIn(resp.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
                              f"{method} {url}")
        self.assertEqual(Recipe.objects.get(id=self.recipe.id).title, "公开菜")
        self.assertTrue(Ingredient.objects.filter(id=self.ingredient.id).exists())
        self.assertEqual(BlogPost.objects.get(id=self.post.id).title, "已发布")
        self.assertEqual(Recipe.objects.count(), 2)

    def test_chef_can_write(self):
        from .models import BlogPost
        self.assertEqual(self.chef.patch(f"/api/recipes/{self.recipe.id}/", {"title": "改"}, format="json").status_code,
                         status.HTTP_200_OK)
        self.assertEqual(self.chef.post("/api/ingredients/", {"name": "盐"}, format="json").status_code,
                         status.HTTP_201_CREATED)
        self.assertEqual(self.chef.patch(f"/api/blog/posts/{self.post.id}/", {"title": "改"}, format="json").status_code,
                         status.HTTP_200_OK)
        self.assertEqual(BlogPost.objects.get(id=self.post.id).title, "改")
        self.assertEqual(self.chef.post("/api/blog/tags/", {"name": "新标签"}, format="json").status_code,
                         status.HTTP_201_CREATED)


class AiEndpointAuthTests(TestCase):
    """AI 接口会消耗模型额度：必须登录。"""

    URLS = ("/api/ai/chat/", "/api/ai/ocr/", "/api/ai/pdf-extract/", "/api/ai/transcribe/")

    def test_anonymous_is_rejected(self):
        for url in self.URLS:
            self.assertEqual(APIClient().post(url, {}, format="json").status_code,
                             status.HTTP_401_UNAUTHORIZED, url)

    def test_logged_in_user_reaches_validation(self):
        client = APIClient()
        client.force_authenticate(User.objects.create_user(username="ai@example.com", password="pw-ai-1"))
        for url in self.URLS:
            self.assertEqual(client.post(url, {}, format="json").status_code,
                             status.HTTP_400_BAD_REQUEST, url)
