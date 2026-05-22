from datetime import date

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from pharmacy.models import (
    CategoryMedication,
    Department,
    Employee,
    Medication,
    Sale,
    SaleItem,
    UserProfile,
)


def _birth_date_years_ago(years: int):
    today = date.today()
    year = today.year - years
    day = min(today.day, 28)
    return date(year, today.month, day)


class StatsViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_superuser(
            username="root",
            password="pass12345",
            email="root@example.com",
        )
        cls.user = User.objects.create_user(
            username="regular",
            password="pass12345",
            email="regular@example.com",
        )

        UserProfile.objects.update_or_create(
            user=cls.superuser,
            defaults={"birth_date": _birth_date_years_ago(30), "phone": "+375 (29) 123-45-67"},
        )
        UserProfile.objects.update_or_create(
            user=cls.user,
            defaults={"birth_date": _birth_date_years_ago(25), "phone": "+375 (29) 123-45-67"},
        )

        cls.dept1 = Department.objects.create(name="Отдел 1")
        cls.dept2 = Department.objects.create(name="Отдел 2")

        cls.emp1 = Employee.objects.create(
            name="Сотрудник 1",
            department=cls.dept1,
            phone="+375 (29) 123-45-67",
            email="emp1@example.com",
        )
        cls.emp2 = Employee.objects.create(
            name="Сотрудник 2",
            department=cls.dept2,
            phone="+375 (29) 123-45-67",
            email="emp2@example.com",
        )

        cls.cat_a = CategoryMedication.objects.create(name="Категория A")
        cls.cat_b = CategoryMedication.objects.create(name="Категория B")

        cls.med1 = Medication.objects.create(
            name="Med1",
            category=cls.cat_a,
            description="desc",
            cost=10,
            count=10,
        )
        cls.med2 = Medication.objects.create(
            name="Med2",
            category=cls.cat_a,
            description="desc",
            cost=20,
            count=10,
        )
        cls.med3 = Medication.objects.create(
            name="Med3",
            category=cls.cat_b,
            description="desc",
            cost=30,
            count=10,
        )

        sale1 = Sale.objects.create(employee=cls.emp1, total_cost=100, made=True)
        sale2 = Sale.objects.create(employee=cls.emp1, total_cost=100, made=True)
        sale3 = Sale.objects.create(employee=cls.emp2, total_cost=200, made=True)

        SaleItem.objects.create(sale=sale1, medication=cls.med1, count=2)
        SaleItem.objects.create(sale=sale2, medication=cls.med2, count=5)
        SaleItem.objects.create(sale=sale3, medication=cls.med3, count=1)

    def test_stats_view_denied_for_regular_user(self):
        client = Client()
        self.assertTrue(client.login(username="regular", password="pass12345"))
        response = client.get(reverse("stats_graf:stats"))
        self.assertEqual(response.status_code, 403)

    def test_stats_view_shows_required_metrics(self):
        client = Client()
        self.assertTrue(client.login(username="root", password="pass12345"))
        response = client.get(reverse("stats_graf:stats"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_revenue"], 400)
        self.assertEqual(response.context["sales_mode"], 100)
        self.assertEqual(response.context["sales_median"], 100)
        self.assertEqual(round(float(response.context["sales_mean"]), 2), 133.33)
        expected_ages = [self.superuser.profile.age, self.user.profile.age]
        self.assertEqual(response.context["clients_mean_age"], sum(expected_ages) / len(expected_ages))
        self.assertEqual(response.context["clients_median_age"], sum(expected_ages) / len(expected_ages))
        self.assertEqual(response.context["most_popular_category"]["medication__category__name"], "Категория A")
        self.assertEqual(response.context["most_profitable_category"]["medication__category__name"], "Категория A")
        self.assertIn(str(date.today().year), response.context["calendar_text"])
        self.assertTrue(response.context["current_timezone_name"])

    def test_stats_view_contains_graphs(self):
        client = Client()
        self.assertTrue(client.login(username="root", password="pass12345"))
        response = client.get(reverse("stats_graf:stats"))
        self.assertContains(response, "Динамика продаж по дням")
        self.assertContains(response, "Распределение выручки по отделам")
