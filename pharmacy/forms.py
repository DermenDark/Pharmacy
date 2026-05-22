from datetime import date, timedelta

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError

from .models import (
    Benefits,
    CategoryMedication,
    Coupons,
    Department,
    Employee,
    phone_validator,
    EmployeeAccount,
    Medication,
    Sale,
    SaleItem,
    Supplier,
    UserProfile,
    Vacancy,
)


class DateTimeLocalInput(forms.DateTimeInput):
    input_type = "datetime-local"


class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label="Логин",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
    birth_date = forms.DateField(
        label="Дата рождения",
        help_text="Выберите дату рождения (18+)",
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
            }
        ),
    )
    phone = forms.CharField(
        label="Телефон",
        help_text="Формат: +375 (29) XXX-XX-XX",
        validators=[phone_validator],
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "+375 (29) 123-45-67",
                "inputmode": "tel",
                "pattern": r"\+375 \(29\) \d{3}-\d{2}-\d{2}",
            }
        ),
    )

    class Meta:
        model = User
        fields = ("username", "phone", "birth_date", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = date.today()
        self.fields["birth_date"].widget.attrs.update({
            "min": (today - timedelta(days=365 * 120)).strftime("%Y-%m-%d"),
            "max": (today - timedelta(days=365 * 18)).strftime("%Y-%m-%d"),
        })

    def clean_birth_date(self):
        birth_date = self.cleaned_data["birth_date"]
        today = date.today()
        age = today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
        )
        if age < 18:
            raise ValidationError("Вам должно быть не менее 18 лет.")
        if age > 120:
            raise ValidationError("Проверьте правильность даты рождения.")
        return birth_date

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.birth_date = self.cleaned_data["birth_date"]
            profile.phone = self.cleaned_data["phone"]
            profile.full_clean()
            profile.save()

            clients_group, _ = Group.objects.get_or_create(name="clients")
            user.groups.add(clients_group)
        return user


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = "__all__"
        labels = {"name": "Название отдела"}
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Введите название отдела"}),
        }


class EmployeeForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.order_by("name"),
        required=False,
        empty_label="Без отдела",
        label="Отдел",
    )

    class Meta:
        model = Employee
        fields = "__all__"
        labels = {
            "name": "Имя сотрудника",
            "department": "Отдел",
            "photo": "Фото",
            "description": "Описание работы",
            "phone": "Телефон",
            "email": "Почта",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Введите имя"}),
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Описание обязанностей"}),
            "phone": forms.TextInput(attrs={"placeholder": "+375 (29) 123-45-67"}),
            "email": forms.EmailInput(attrs={"placeholder": "name@example.com"}),
        }


class EmployeeAccountForm(forms.ModelForm):
    class Meta:
        model = EmployeeAccount
        fields = "__all__"
        labels = {
            "name": "Название учетной записи",
            "date_of_birth": "Дата рождения",
            "employee": "Сотрудник",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Название учетной записи"}),
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "employee": forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = date.today()
        self.fields["date_of_birth"].widget.attrs.update({
            "min": (today - timedelta(days=365 * 120)).strftime("%Y-%m-%d"),
            "max": (today - timedelta(days=365 * 18)).strftime("%Y-%m-%d"),
        })


class CategoryMedicationForm(forms.ModelForm):
    class Meta:
        model = CategoryMedication
        fields = "__all__"
        labels = {"name": "Название категории"}
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Например: Антибиотики"}),
        }


class MedicationForm(forms.ModelForm):
    class Meta:
        model = Medication
        fields = "__all__"
        labels = {
            "name": "Название",
            "category": "Категория",
            "description": "Описание",
            "cost": "Цена",
            "count": "Количество",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Название медикамента"}),
            "category": forms.Select(),
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Описание"}),
            "cost": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "count": forms.NumberInput(attrs={"min": "0"}),
        }

    def clean_cost(self):
        cost = self.cleaned_data["cost"]
        if cost <= 0:
            raise ValidationError("Цена должна быть больше 0.")
        return cost

    def clean_count(self):
        count = self.cleaned_data["count"]
        if count < 0:
            raise ValidationError("Количество не может быть отрицательным.")
        return count


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = "__all__"
        labels = {
            "name": "Название поставщика",
            "medications": "Медикаменты",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Название поставщика"}),
            "medications": forms.SelectMultiple(),
        }


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = "__all__"
        labels = {
            "employee": "Сотрудник",
            "total_cost": "Общая стоимость",
            "made": "Продажа выполнена",
            "sale_date": "Дата продажи",
        }
        widgets = {
            "employee": forms.Select(),
            "total_cost": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "made": forms.CheckboxInput(),
            "sale_date": DateTimeLocalInput(),
        }


class SaleItemForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        fields = "__all__"
        labels = {
            "sale": "Продажа",
            "medication": "Медикамент",
            "count": "Количество",
        }
        widgets = {
            "sale": forms.Select(),
            "medication": forms.Select(),
            "count": forms.NumberInput(attrs={"min": "1"}),
        }

    def clean_count(self):
        count = self.cleaned_data["count"]
        if count <= 0:
            raise ValidationError("Количество должно быть больше 0.")
        return count


class BenefitsForm(forms.ModelForm):
    class Meta:
        model = Benefits
        fields = "__all__"
        labels = {
            "name": "Название льготы",
            "min_age": "Минимальный возраст",
            "is_pensioner": "Пенсионер",
            "is_disability": "Инвалидность",
            "discount_cost": "Сумма скидки",
            "discount_percent": "Процент скидки",
            "is_active": "Активна",
            "valid_from": "Действует с",
            "valid_to": "Действует до",
            "usage_limit": "Лимит использований",
            "used_count": "Использовано",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Название льготы"}),
            "min_age": forms.NumberInput(attrs={"min": "0"}),
            "discount_cost": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "discount_percent": forms.NumberInput(attrs={"min": "0", "max": "100"}),
            "valid_from": DateTimeLocalInput(),
            "valid_to": DateTimeLocalInput(),
            "usage_limit": forms.NumberInput(attrs={"min": "0"}),
            "used_count": forms.NumberInput(attrs={"min": "0"}),
        }


class CouponsForm(forms.ModelForm):
    class Meta:
        model = Coupons
        fields = "__all__"
        labels = {
            "discount_cost": "Сумма скидки",
            "discount_percent": "Процент скидки",
            "is_active": "Активен",
            "valid_from": "Действует с",
            "valid_to": "Действует до",
            "usage_limit": "Лимит использований",
            "used_count": "Использовано",
        }
        widgets = {
            "discount_cost": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "discount_percent": forms.NumberInput(attrs={"min": "0", "max": "100"}),
            "valid_from": DateTimeLocalInput(),
            "valid_to": DateTimeLocalInput(),
            "usage_limit": forms.NumberInput(attrs={"min": "0"}),
            "used_count": forms.NumberInput(attrs={"min": "0"}),
        }


class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = "__all__"
        labels = {
            "title": "Название вакансии",
            "description": "Описание",
            "is_active": "Активна",
        }
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Название вакансии"}),
            "description": forms.Textarea(attrs={"rows": 5, "placeholder": "Описание вакансии"}),
            "is_active": forms.CheckboxInput(),
        }
