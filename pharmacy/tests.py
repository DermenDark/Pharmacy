from datetime import date

import pytest
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse

from .forms import RegisterForm
from .models import CategoryMedication, Department, Employee, EmployeeAccount, Medication, UserProfile, phone_validator


def _birth_date_years_ago(years: int) -> date:
    today = date.today()
    year = today.year - years
    day = min(today.day, 28)
    return date(year, today.month, day)


class RegisterFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Group.objects.get_or_create(name="clients")
        Group.objects.get_or_create(name="employees")

    def test_register_form_creates_user_profile_and_assigns_clients_group(self):
        form = RegisterForm(
            data={
                "username": "client1",
                "phone": "+375 (29) 123-45-67",
                "birth_date": _birth_date_years_ago(20),
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

        user = form.save()
        profile = user.profile

        self.assertEqual(User.objects.filter(username="client1").count(), 1)
        self.assertEqual(profile.phone, "+375 (29) 123-45-67")
        self.assertEqual(profile.birth_date, _birth_date_years_ago(20))
        self.assertTrue(user.groups.filter(name="clients").exists())

    def test_register_form_rejects_underage_birth_date(self):
        form = RegisterForm(
            data={
                "username": "client2",
                "phone": "+375 (29) 123-45-67",
                "birth_date": _birth_date_years_ago(17),
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("birth_date", form.errors)

    def test_register_form_rejects_bad_phone(self):
        form = RegisterForm(
            data={
                "username": "client3",
                "phone": "12345",
                "birth_date": _birth_date_years_ago(20),
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)

    def test_employee_phone_validator_and_age_rules(self):
        department = Department.objects.create(name="Sales")
        employee = Employee(
            name="Alex",
            department=department,
            phone="bad-phone",
            email="alex@example.com",
        )
        with self.assertRaises(ValidationError):
            employee.full_clean()

        employee.phone = "+375 (29) 123-45-67"
        employee.full_clean()
        employee.save()

        account = EmployeeAccount(
            name="Alex account",
            employee=employee,
            date_of_birth=_birth_date_years_ago(17),
        )
        with self.assertRaises(ValidationError):
            account.full_clean()

        account.date_of_birth = _birth_date_years_ago(20)
        account.full_clean()
        account.save()
        self.assertEqual(account.age, 20)


@pytest.mark.parametrize(
    "phone,should_pass",
    [
        ("+375 (29) 123-45-67", True),
        ("+375 (29) 1234567", False),
        ("123", False),
    ],
)
def test_phone_validator_parametrized(phone, should_pass):
    if should_pass:
        phone_validator(phone)
    else:
        with pytest.raises(ValidationError):
            phone_validator(phone)


class UserManagementViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Group.objects.get_or_create(name="clients")
        Group.objects.get_or_create(name="employees")
        cls.superuser = User.objects.create_superuser(
            username="admin",
            password="pass12345",
            email="admin@example.com",
        )
        cls.user = User.objects.create_user(
            username="john",
            password="pass12345",
            email="john@example.com",
        )
        UserProfile.objects.update_or_create(
            user=cls.user,
            defaults={
                "birth_date": _birth_date_years_ago(25),
                "phone": "+375 (29) 123-45-67",
            },
        )

    def test_superuser_can_assign_groups(self):
        client = Client()
        self.assertTrue(client.login(username="admin", password="pass12345"))

        response = client.post(
            reverse("user_management"),
            data={
                "user_id": self.user.id,
                "groups": ["clients", "employees"],
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.groups.filter(name="clients").exists())
        self.assertTrue(self.user.groups.filter(name="employees").exists())

    def test_regular_user_gets_403(self):
        client = Client()
        self.assertTrue(client.login(username="john", password="pass12345"))
        response = client.get(reverse("user_management"))
        self.assertEqual(response.status_code, 403)


class CatalogViewTests(TestCase):
    def test_catalog_page_opens(self):
        category = CategoryMedication.objects.create(name="Категория")
        Medication.objects.create(
            name="Catalog med",
            category=category,
            description="desc",
            cost=12,
            count=4,
        )

        client = Client()
        response = client.get(reverse("catalog"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Catalog med")
