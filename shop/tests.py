from datetime import date

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from pharmacy.models import CategoryMedication, Medication, UserProfile

from .models import Cart, CartItem, Order


def _birth_date_years_ago(years: int):
    today = date.today()
    year = today.year - years
    day = min(today.day, 28)
    return date(year, today.month, day)


class ShopViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="shop_user", password="pass12345")
        UserProfile.objects.update_or_create(
            user=cls.user,
            defaults={
                "birth_date": _birth_date_years_ago(23),
                "phone": "+375 (29) 123-45-67",
            },
        )
        cls.category = CategoryMedication.objects.create(name="Антибиотики")
        cls.medication = Medication.objects.create(
            name="Amoxicillin",
            category=cls.category,
            description="Test",
            cost=10.00,
            count=5,
        )

    def test_cart_view_requires_login(self):
        client = Client()
        response = client.get(reverse("shop:cart"))
        self.assertEqual(response.status_code, 302)

    def test_add_to_cart_and_checkout(self):
        client = Client()
        self.assertTrue(client.login(username="shop_user", password="pass12345"))

        response = client.get(reverse("shop:add_to_cart", kwargs={"pk": self.medication.pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CartItem.objects.count(), 1)

        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.total_cost, 10)

        response = client.get(reverse("shop:checkout"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(CartItem.objects.count(), 0)

    def test_profile_page_shows_user_profile_data(self):
        profile = self.user.profile
        profile.birth_date = _birth_date_years_ago(23)
        profile.phone = "+375 (29) 123-45-67"
        profile.save()

        client = Client()
        self.assertTrue(client.login(username="shop_user", password="pass12345"))
        response = client.get(reverse("shop:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "+375 (29) 123-45-67")
        self.assertContains(response, "Возраст")
