from datetime import date

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone


phone_validator = RegexValidator(
    regex=r'^\+375 \(29\) \d{3}-\d{2}-\d{2}$',
    message='Телефон должен быть в формате +375 (29) XXX-XX-XX',
)
class UserProfile(models.Model):
    name = models.CharField(max_length=255, default="User", verbose_name="Имя")
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Пользователь",
    )
    timezone = models.CharField(max_length=64, default="UTC")
    birth_date = models.DateField(
        verbose_name="Дата рождения",
        null=True,
        blank=True,
        help_text="Введите дату рождения в формате календаря",
    )
    phone = models.CharField(
        max_length=19,
        validators=[phone_validator],
        verbose_name="Телефон",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}"

    @property
    def age(self):
        if not self.birth_date:
            return None
        today = timezone.localdate()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

    def clean(self):
        super().clean()
        if self.birth_date:
            age = self.age
            if age is not None and age < 18:
                raise ValidationError({"birth_date": "Вам должно быть не менее 18 лет."})
            if age is not None and age > 120:
                raise ValidationError({"birth_date": "Проверьте правильность даты рождения."})


class Department(models.Model):
    """Отделы аптеки"""
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Employee(models.Model):
    """Сотрудники"""
    name = models.CharField(max_length=30)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees",
        verbose_name="Отдел",
    )
    photo = models.ImageField(
        upload_to="contacts/",
        default="def_ju59XtB.webp",
        blank=True,
        null=True,
        verbose_name="Фото",
    )
    description = models.TextField(blank=True, null=True, verbose_name="Описание работы")
    phone = models.CharField(max_length=19, validators=[phone_validator], verbose_name="Телефон")
    email = models.EmailField(verbose_name="Почта")

    def __str__(self):
        return self.name


class EmployeeAccount(models.Model):
    """Учетная запись сотрудника"""
    name = models.CharField(max_length=30)
    date_of_birth = models.DateField(
        verbose_name="Дата рождения",
        null=True,
        blank=True,
    )
    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name="account",
    )

    def __str__(self):
        return self.name

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = timezone.localdate()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def clean(self):
        super().clean()
        if self.date_of_birth:
            age = self.age
            if age is not None and age < 18:
                raise ValidationError({"date_of_birth": "Возраст должен быть не меньше 18 лет."})
            if age is not None and age > 120:
                raise ValidationError({"date_of_birth": "Проверьте правильность даты рождения."})


class CategoryMedication(models.Model):
    """Категории медикаментов"""
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Medication(models.Model):
    """Медикаменты"""
    name = models.CharField(max_length=30)
    category = models.ForeignKey(CategoryMedication, on_delete=models.CASCADE, related_name="medications")
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    count = models.PositiveIntegerField()
    photo = models.ImageField(
        upload_to="medications/photos/",
        blank=True,
        null=True,
        verbose_name="Фотография",
    )

    def __str__(self):
        return self.name


class Supplier(models.Model):
    """Поставщики"""
    name = models.CharField(max_length=30)
    medications = models.ManyToManyField(Medication, related_name="suppliers")

    def __str__(self):
        return self.name


class Benefits(models.Model):
    """Льготы"""
    name = models.CharField(max_length=100)
    min_age = models.PositiveIntegerField(null=True, blank=True)
    is_pensioner = models.BooleanField(default=False)
    is_disability = models.BooleanField(default=False)
    discount_cost = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Льгота от {self.min_age} лет"


class Coupons(models.Model):
    """Купоны"""
    code = models.CharField(max_length=32)
    discount_cost = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.code} — {self.discount_percent}% / {self.discount_cost}"

class Sale(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    sale_date = models.DateTimeField(auto_now_add=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupons = models.ManyToManyField(Coupons, blank=True, related_name="sales")
    discount_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    made = models.BooleanField(default=False)

    def __str__(self):
        return f"Sale #{self.id}"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    medication = models.ForeignKey(
        Medication,
        on_delete=models.CASCADE,
        related_name="sale_items",
    )
    count = models.PositiveIntegerField()

    class Meta:
        unique_together = ("sale", "medication")

    def __str__(self):
        return f"{self.medication.name} x {self.count}"
    
class Vacancy(models.Model):
    """Вакансии"""
    title = models.CharField(max_length=200, verbose_name="Название вакансии")
    description = models.TextField(verbose_name="Описание")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    def __str__(self):
        return self.title
