from django.contrib import admin

from .models import (
    Benefits,
    CategoryMedication,
    Coupons,
    Department,
    Employee,
    EmployeeAccount,
    Medication,
    Sale,
    SaleItem,
    Supplier,
    UserProfile,
    Vacancy,
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "birth_date", "phone", "created_at")
    search_fields = ("user__username", "phone")
    list_filter = ("created_at",)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "department", "phone", "email")
    search_fields = ("name", "phone", "email")
    list_filter = ("department",)


@admin.register(EmployeeAccount)
class EmployeeAccountAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "employee", "date_of_birth")
    search_fields = ("name", "employee__name")
    list_filter = ("date_of_birth",)


@admin.register(CategoryMedication)
class CategoryMedicationAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "cost", "count")
    search_fields = ("name", "category__name")
    list_filter = ("category",)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    filter_horizontal = ("medications",)


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "employee", "total_cost", "made", "sale_date")
    search_fields = ("employee__name",)
    list_filter = ("made", "sale_date")
    inlines = [SaleItemInline]


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ("id", "sale", "medication", "count")
    search_fields = ("medication__name", "sale__employee__name")
    list_filter = ("sale",)


@admin.register(Benefits)
class BenefitsAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "discount_percent", "is_active", "valid_from", "valid_to")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(Coupons)
class CouponsAdmin(admin.ModelAdmin):
    list_display = ("id", "discount_percent", "discount_cost", "is_active", "valid_from", "valid_to")
    list_filter = ("is_active",)


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "is_active", "created_at")
    search_fields = ("title",)
    list_filter = ("is_active", "created_at")
