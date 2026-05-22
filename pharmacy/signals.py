from django.contrib.auth.models import Group, Permission, User
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver

from .models import UserProfile


@receiver(post_migrate)
def create_groups(sender, **kwargs):
    employees_group, _ = Group.objects.get_or_create(name="employees")
    clients_group, _ = Group.objects.get_or_create(name="clients")

    employee_permissions = Permission.objects.filter(
        codename__in=[
            "view_medication",
            "view_categorymedication",
            "view_department",
            "view_employee",
            "view_employeeaccount",
            "view_supplier",
            "view_sale",
            "view_saleitem",
            "view_benefits",
            "view_coupons",
            "view_vacancy",
            "view_aboutcompany",
            "view_news",
            "view_review",
            "add_review",
            "view_term",
        ],
        content_type__app_label__in=["pharmacy", "info"],
    )
    employees_group.permissions.set(employee_permissions)

    client_permissions = Permission.objects.filter(
        codename__in=[
            "view_medication",
            "view_categorymedication",
            "view_aboutcompany",
            "view_news",
            "view_term",
            "view_vacancy",
            "view_review",
            "view_benefits",
            "view_coupons",
            "add_review",
            "view_cart",
            "add_cart",
            "change_cart",
            "delete_cart",
            "view_cartitem",
            "add_cartitem",
            "change_cartitem",
            "delete_cartitem",
            "view_order",
            "add_order",
            "view_orderitem",
        ],
        content_type__app_label__in=["pharmacy", "info", "shop"],
    )
    clients_group.permissions.set(client_permissions)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
