import logging

from django.contrib import messages
from django.contrib.auth import get_user_model, login as auth_login
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .forms import RegisterForm
from .help_funk.filter import (
    filter_benefits,
    filter_categories,
    filter_coupons,
    filter_departments,
    filter_employee_accounts,
    filter_employees,
    filter_medications,
    filter_saleitems,
    filter_sales,
    filter_suppliers,
    filter_vacancies,
)
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
    Vacancy,
)

logger = logging.getLogger("pharmacy")
User = get_user_model()


def is_superuser(user):
    return user.is_authenticated and user.is_superuser


def catalog(request):
    logger.info("Открыт каталог пользователем %s", request.user)
    all_categories = CategoryMedication.objects.all()
    medics = Medication.objects.select_related("category").all()
    medics = filter_medications(request, medics)

    return render(request, "pharmacy/catalog.html", {
        "all_info": medics,
        "all_categors": all_categories,
    })


@login_required
@permission_required("pharmacy.add_medication", raise_exception=True)
def create_medication(request):
    categories = CategoryMedication.objects.all()

    if request.method == "POST":
        Medication.objects.create(
            name=request.POST.get("name"),
            category_id=request.POST.get("category"),
            description=request.POST.get("description"),
            cost=request.POST.get("cost"),
            count=request.POST.get("count"),
            photo=request.FILES.get("photo"),
        )
        logger.info("Создан медикамент пользователем %s", request.user)
        return redirect("catalog")

    logger.info("Открыта форма создания медикамента пользователем %s", request.user)
    return render(request, "medications/create.html", {"categories": categories})


@login_required
@permission_required("pharmacy.change_medication", raise_exception=True)
def edit_medication(request, pk):
    medic = get_object_or_404(Medication, pk=pk)
    categories = CategoryMedication.objects.all()

    if request.method == "POST":
        medic.name = request.POST.get("name")
        medic.category_id = request.POST.get("category")
        medic.description = request.POST.get("description")
        medic.cost = request.POST.get("cost")
        medic.count = request.POST.get("count")

        if request.FILES.get("photo"):
            medic.photo = request.FILES.get("photo")

        medic.save()
        logger.info("Изменен медикамент id=%s пользователем %s", pk, request.user)
        return redirect("catalog")

    logger.info("Открыта форма редактирования медикамента id=%s пользователем %s", pk, request.user)
    return render(request, "medications/edit.html", {"medic": medic, "categories": categories})


@login_required
@permission_required("pharmacy.delete_medication", raise_exception=True)
def delete_medication(request, pk):
    medic = get_object_or_404(Medication, pk=pk)
    if request.method == "POST":
        medic.delete()
        logger.warning("Удален медикамент id=%s пользователем %s", pk, request.user)
        return redirect("catalog")

    logger.info("Открыта форма удаления медикамента id=%s пользователем %s", pk, request.user)
    return render(request, "medications/delete.html", {"medic": medic})


def promo(request):
    logger.info("Открыта страница промокодов пользователем %s", request.user)
    return render(request, "pharmacy/promo.html", {
        "benefits": Benefits.objects.filter(is_active=True),
        "coupons": Coupons.objects.filter(is_active=True),
    })


def vacancies(request):
    logger.info("Открыта страница вакансий пользователем %s", request.user)
    vacancies_qs = Vacancy.objects.filter(is_active=True).order_by("-created_at")
    vacancies_qs = filter_vacancies(request, vacancies_qs)
    return render(request, "pharmacy/vacancies.html", {"vacancies": vacancies_qs})


def contacts(request):
    logger.info("Открыта страница контактов пользователем %s", request.user)
    return render(request, "pharmacy/contacts.html", {
        "employee": Employee.objects.select_related("department").all()
    })


def login_view(request):
    login_form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST":
        next_url = request.POST.get("next") or "about_company"

        if login_form.is_valid():
            user = login_form.get_user()
            auth_login(request, user)
            logger.info("Успешный вход пользователя %s", user)
            return redirect(next_url)

        logger.warning("Ошибка формы входа у пользователя %s", request.user)

    logger.info("Открыта страница входа пользователем %s", request.user)
    return render(request, "pharmacy/login.html", {
        "login_form": login_form,
    })


def register_view(request):
    register_form = RegisterForm(request.POST or None)
    
    if request.method == "POST":
        next_url = request.POST.get("next") or "about_company"
        action = request.POST.get("action")
        if action == "register":
                if register_form.is_valid():
                    user = register_form.save()
                    group, _ = Group.objects.get_or_create(name='clients')
                    user.groups.add(group)
                    
                    logger.info("Успешная регистрация пользователя %s", user)
                    return redirect(next_url)
                logger.warning("Ошибка формы регистрации у пользователя %s: %s", request.user, register_form.errors)

    logger.info("Открыта страница регистрации пользователем %s", request.user)
    return render(request, "pharmacy/register.html", {
        "register_form": register_form,
    })


@login_required
def profil_view(request):
    logger.info("Открыт профиль/кабинет пользователем %s", request.user)
    login_form = AuthenticationForm(request, data=request.POST or None)
    register_form = RegisterForm(request.POST or None)

    return render(request, "pharmacy/login.html", {
        "login_form": login_form,
        "register_form": register_form,
    })


@login_required
@permission_required("pharmacy.view_department", raise_exception=True)
def department_list(request):
    logger.info("Открыт список отделов пользователем %s", request.user)
    departments = Department.objects.prefetch_related("employees").order_by("name")
    departments = filter_departments(request, departments)
    return render(request, "pharmacy/departments.html", {"departments": departments})


@login_required
@permission_required("pharmacy.view_employee", raise_exception=True)
def employee_list(request):
    logger.info("Открыт список сотрудников пользователем %s", request.user)
    employees = Employee.objects.select_related("department").order_by("name")
    employees = filter_employees(request, employees)
    return render(request, "pharmacy/employees.html", {
        "employees": employees,
        "all_departments": Department.objects.all(),
    })


@login_required
@permission_required("pharmacy.view_employeeaccount", raise_exception=True)
def employeeaccount_list(request):
    logger.info("Открыт список учетных записей сотрудников пользователем %s", request.user)
    employeeaccounts = EmployeeAccount.objects.select_related("employee").all()
    employeeaccounts = filter_employee_accounts(request, employeeaccounts)
    return render(request, "pharmacy/employee_accounts.html", {
        "employeeaccounts": employeeaccounts,
        "all_employees": Employee.objects.all(),
    })


@login_required
@permission_required("pharmacy.view_supplier", raise_exception=True)
def supplier_list(request):
    logger.info("Открыт список поставщиков пользователем %s", request.user)
    suppliers = Supplier.objects.prefetch_related("medications").order_by("name")
    suppliers = filter_suppliers(request, suppliers)
    return render(request, "pharmacy/suppliers.html", {
        "suppliers": suppliers,
        "all_medications": Medication.objects.all(),
    })


@login_required
@permission_required("pharmacy.view_sale", raise_exception=True)
def sale_list(request):
    logger.info("Открыт список продаж пользователем %s", request.user)
    sales = (
        Sale.objects.select_related("employee")
        .prefetch_related("items__medication")
        .order_by("-sale_date")
    )
    sales = filter_sales(request, sales)
    return render(request, "pharmacy/sales.html", {
        "sales": sales,
        "all_employees": Employee.objects.all(),
    })


@login_required
@permission_required("pharmacy.view_saleitem", raise_exception=True)
def saleitem_list(request):
    logger.info("Открыт список позиций продаж пользователем %s", request.user)
    saleitems = SaleItem.objects.select_related("sale", "medication")
    saleitems = filter_saleitems(request, saleitems)
    return render(request, "pharmacy/saleitems.html", {
        "saleitems": saleitems,
        "all_sales": Sale.objects.all(),
        "all_medications": Medication.objects.all(),
    })


@login_required
@permission_required("pharmacy.view_categorymedication", raise_exception=True)
def category_list(request):
    logger.info("Открыт список категорий медикаментов пользователем %s", request.user)
    categories = CategoryMedication.objects.prefetch_related("medications").order_by("name")
    categories = filter_categories(request, categories)
    return render(request, "pharmacy/categories.html", {"categories": categories})


@login_required
@permission_required("pharmacy.view_benefits", raise_exception=True)
def benefits_list(request):
    logger.info("Открыт список льгот пользователем %s", request.user)
    benefits = filter_benefits(request, Benefits.objects.all())
    return render(request, "pharmacy/benefits.html", {"benefits": benefits})


@login_required
@permission_required("pharmacy.view_coupons", raise_exception=True)
def coupons_list(request):
    logger.info("Открыт список купонов пользователем %s", request.user)
    coupons = filter_coupons(request, Coupons.objects.all())
    return render(request, "pharmacy/coupons.html", {"coupons": coupons})


@login_required
@permission_required("pharmacy.view_vacancy", raise_exception=True)
def vacancy_list(request):
    logger.info("Открыт список вакансий пользователем %s", request.user)
    vacancies = filter_vacancies(request, Vacancy.objects.all().order_by("-created_at"))
    return render(request, "pharmacy/vacancies.html", {"vacancies": vacancies})


@login_required
def user_management(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    groups = Group.objects.filter(name__in=["employees", "clients"]).order_by("name")
    users = User.objects.prefetch_related("groups").order_by("username")

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        selected_groups = request.POST.getlist("groups")
        target_user = get_object_or_404(User, pk=user_id)

        if target_user.is_superuser:
            messages.warning(request, "Для суперпользователя группы не изменяются.")
            logger.warning("Попытка изменить группы суперпользователя %s", target_user.username)
            return redirect("user_management")

        target_groups = Group.objects.filter(name__in=selected_groups)
        target_user.groups.set(target_groups)
        logger.info(
            "Изменены группы пользователя %s: %s",
            target_user.username,
            list(target_groups.values_list("name", flat=True)),
        )
        messages.success(request, f"Группы пользователя {target_user.username} обновлены.")
        return redirect("user_management")

    logger.info("Открыта страница управления пользователями пользователем %s", request.user)
    return render(request, "pharmacy/users.html", {
        "users": users,
        "groups": groups,
    })
