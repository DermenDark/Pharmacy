import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required

from .models import (
    Department,
    Employee,
    EmployeeAccount,
    CategoryMedication,
    Medication,
    Supplier,
    Sale,
    SaleItem,
    Benefits,
    Coupons,
    Vacancy,
)
from .forms import (
    DepartmentForm,
    EmployeeForm,
    EmployeeAccountForm,
    CategoryMedicationForm,
    MedicationForm,
    SupplierForm,
    SaleForm,
    SaleItemForm,
    BenefitsForm,
    CouponsForm,
    VacancyForm,
)

logger = logging.getLogger("pharmacy")


def _save_form_view(request, form_class, template_name, success_url, instance=None):
    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            saved_obj = form.save()
            if instance is None:
                logger.info("Создан объект %s пользователем %s", saved_obj.__class__.__name__, request.user)
            else:
                logger.info("Изменен объект %s id=%s пользователем %s", saved_obj.__class__.__name__, saved_obj.pk, request.user)
            return redirect(success_url)
        logger.warning(
            "Ошибка формы %s пользователем %s: %s",
            form_class.__name__,
            request.user,
            form.errors
        )
    else:
        form = form_class(instance=instance)

    return render(request, template_name, {
        "form": form,
        "object": instance,
    })


def _delete_view(request, obj, template_name, success_url):
    if request.method == "POST":
        model_name = obj.__class__.__name__
        obj_id = obj.pk
        obj.delete()
        logger.warning("Удален объект %s id=%s пользователем %s", model_name, obj_id, request.user)
        return redirect(success_url)

    logger.info("Открыта форма удаления объекта %s id=%s пользователем %s", obj.__class__.__name__, obj.pk, request.user)
    return render(request, template_name, {"object": obj})


@login_required
@permission_required("pharmacy.add_department", raise_exception=True)
def department_create(request):
    logger.info("Открыта форма создания отдела пользователем %s", request.user)
    return _save_form_view(request, DepartmentForm, "form.html", "department_list")


@login_required
@permission_required("pharmacy.change_department", raise_exception=True)
def department_update(request, pk):
    obj = get_object_or_404(Department, pk=pk)
    logger.info("Открыта форма редактирования отдела id=%s пользователем %s", pk, request.user)
    return _save_form_view(request, DepartmentForm, "form.html", "department_list", instance=obj)


@login_required
@permission_required("pharmacy.delete_department", raise_exception=True)
def department_delete(request, pk):
    obj = get_object_or_404(Department, pk=pk)
    return _delete_view(request, obj, "delete.html", "department_list")


@login_required
@permission_required("pharmacy.add_employee", raise_exception=True)
def employee_create(request):
    logger.info("Открыта форма создания сотрудника пользователем %s", request.user)
    return _save_form_view(request, EmployeeForm, "form.html", "employee_list")


@login_required
@permission_required("pharmacy.change_employee", raise_exception=True)
def employee_update(request, pk):
    obj = get_object_or_404(Employee, pk=pk)
    logger.info("Открыта форма редактирования сотрудника id=%s пользователем %s", pk, request.user)
    return _save_form_view(request, EmployeeForm, "form.html", "employee_list", instance=obj)


@login_required
@permission_required("pharmacy.delete_employee", raise_exception=True)
def employee_delete(request, pk):
    obj = get_object_or_404(Employee, pk=pk)
    return _delete_view(request, obj, "delete.html", "employee_list")


@login_required
@permission_required("pharmacy.add_employeeaccount", raise_exception=True)
def employeeaccount_create(request):
    logger.info("Открыта форма создания учетной записи сотрудника пользователем %s", request.user)
    return _save_form_view(request, EmployeeAccountForm, "form.html", "employeeaccount_list")


@login_required
@permission_required("pharmacy.change_employeeaccount", raise_exception=True)
def employeeaccount_update(request, pk):
    obj = get_object_or_404(EmployeeAccount, pk=pk)
    logger.info("Открыта форма редактирования учетной записи сотрудника id=%s пользователем %s", pk, request.user)
    return _save_form_view(request, EmployeeAccountForm, "form.html", "employeeaccount_list", instance=obj)


@login_required
@permission_required("pharmacy.delete_employeeaccount", raise_exception=True)
def employeeaccount_delete(request, pk):
    obj = get_object_or_404(EmployeeAccount, pk=pk)
    return _delete_view(request, obj, "delete.html", "employeeaccount_list")


@login_required
@permission_required("pharmacy.add_categorymedication", raise_exception=True)
def categorymedication_create(request):
    logger.info("Открыта форма создания категории пользователем %s", request.user)
    return _save_form_view(request, CategoryMedicationForm, "form.html", "category_list")


@login_required
@permission_required("pharmacy.change_categorymedication", raise_exception=True)
def categorymedication_update(request, pk):
    obj = get_object_or_404(CategoryMedication, pk=pk)
    logger.info("Открыта форма редактирования категории id=%s пользователем %s", pk, request.user)
    return _save_form_view(request, CategoryMedicationForm, "form.html", "category_list", instance=obj)


@login_required
@permission_required("pharmacy.delete_categorymedication", raise_exception=True)
def categorymedication_delete(request, pk):
    obj = get_object_or_404(CategoryMedication, pk=pk)
    return _delete_view(request, obj, "delete.html", "category_list")


@login_required
@permission_required("pharmacy.add_supplier", raise_exception=True)
def supplier_create(request):
    logger.info("Открыта форма создания поставщика пользователем %s", request.user)
    return _save_form_view(request, SupplierForm, "form.html", "supplier_list")


@login_required
@permission_required("pharmacy.change_supplier", raise_exception=True)
def supplier_update(request, pk):
    obj = get_object_or_404(Supplier, pk=pk)
    logger.info("Открыта форма редактирования поставщика id=%s пользователем %s", pk, request.user)
    return _save_form_view(request, SupplierForm, "form.html", "supplier_list", instance=obj)


@login_required
@permission_required("pharmacy.delete_supplier", raise_exception=True)
def supplier_delete(request, pk):
    obj = get_object_or_404(Supplier, pk=pk)
    return _delete_view(request, obj, "delete.html", "supplier_list")


@login_required
@permission_required("pharmacy.add_sale", raise_exception=True)
def sale_create(request):
    logger.info("Открыта форма создания продажи пользователем %s", request.user)
    return _save_form_view(request, SaleForm, "form.html", "sale_list")


@login_required
@permission_required("pharmacy.change_sale", raise_exception=True)
def sale_update(request, pk):
    obj = get_object_or_404(Sale, pk=pk)
    logger.info("Открыта форма редактирования продажи id=%s пользователем %s", pk, request.user)
    return _save_form_view(request, SaleForm, "form.html", "sale_list", instance=obj)


@login_required
@permission_required("pharmacy.delete_sale", raise_exception=True)
def sale_delete(request, pk):
    obj = get_object_or_404(Sale, pk=pk)
    return _delete_view(request, obj, "delete.html", "sale_list")


@login_required
@permission_required("pharmacy.add_saleitem", raise_exception=True)
def saleitem_create(request):
    logger.info("Открыта форма создания позиции продажи пользователем %s", request.user)
    return _save_form_view(request, SaleItemForm, "form.html", "sale_list")


@login_required
@permission_required("pharmacy.change_saleitem", raise_exception=True)
def saleitem_update(request, pk):
    obj = get_object_or_404(SaleItem, pk=pk)
    logger.info("Открыта форма редактирования позиции продажи id=%s пользователем %s", pk, request.user)
    return _save_form_view(request, SaleItemForm, "form.html", "sale_list", instance=obj)


@login_required
@permission_required("pharmacy.delete_saleitem", raise_exception=True)
def saleitem_delete(request, pk):
    obj = get_object_or_404(SaleItem, pk=pk)
    return _delete_view(request, obj, "delete.html", "sale_list")


@login_required
@permission_required("pharmacy.add_benefits", raise_exception=True)
def benefits_create(request):
    logger.info("Открыта форма создания льготы пользователем %s", request.user)
    return _save_form_view(request, BenefitsForm, "form.html", "benefits_list")


@login_required
@permission_required("pharmacy.change_benefits", raise_exception=True)
def benefits_update(request, pk):
    obj = get_object_or_404(Benefits, pk=pk)
    logger.info("Открыта форма редактирования льготы id=%s пользователем %s", pk, request.user)
    return _save_form_view(request, BenefitsForm, "form.html", "benefits_list", instance=obj)


@login_required
@permission_required("pharmacy.delete_benefits", raise_exception=True)
def benefits_delete(request, pk):
    obj = get_object_or_404(Benefits, pk=pk)
    return _delete_view(request, obj, "delete.html", "benefits_list")


@login_required
@permission_required("pharmacy.add_coupons", raise_exception=True)
def coupons_create(request):
    logger.info("Открыта форма создания купона пользователем %s", request.user)
    return _save_form_view(request, CouponsForm, "form.html", "coupons_list")


@login_required
@permission_required("pharmacy.change_coupons", raise_exception=True)
def coupons_update(request, pk):
    obj = get_object_or_404(Coupons, pk=pk)
    logger.info("Открыта форма редактирования купона id=%s пользователем %s", pk, request.user)
    return _save_form_view(request, CouponsForm, "form.html", "coupons_list", instance=obj)


@login_required
@permission_required("pharmacy.delete_coupons", raise_exception=True)
def coupons_delete(request, pk):
    obj = get_object_or_404(Coupons, pk=pk)
    return _delete_view(request, obj, "delete.html", "coupons_list")


@login_required
@permission_required("pharmacy.add_vacancy", raise_exception=True)
def vacancy_create(request):
    logger.info("Открыта форма создания вакансии пользователем %s", request.user)
    return _save_form_view(request, VacancyForm, "form.html", "vacancy_list")


@login_required
@permission_required("pharmacy.change_vacancy", raise_exception=True)
def vacancy_update(request, pk):
    obj = get_object_or_404(Vacancy, pk=pk)
    logger.info("Открыта форма редактирования вакансии id=%s пользователем %s", pk, request.user)
    return _save_form_view(request, VacancyForm, "form.html", "vacancy_list", instance=obj)


@login_required
@permission_required("pharmacy.delete_vacancy", raise_exception=True)
def vacancy_delete(request, pk):
    obj = get_object_or_404(Vacancy, pk=pk)
    return _delete_view(request, obj, "delete.html", "vacancy_list")