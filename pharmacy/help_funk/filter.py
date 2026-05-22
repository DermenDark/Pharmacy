from django.utils import timezone


def filter_medications(request, qs):
    category_id = request.GET.get('category')
    if category_id:
        qs = qs.filter(category_id=category_id)

    q = request.GET.get('q')
    if q:
        qs = qs.filter(name__icontains=q)

    in_stock = request.GET.get('in_stock')
    if in_stock == "1":
        qs = qs.filter(count__gt=0)

    min_price = request.GET.get('min_price')
    if min_price:
        qs = qs.filter(cost__gte=min_price)

    max_price = request.GET.get('max_price')
    if max_price:
        qs = qs.filter(cost__lte=max_price)

    return qs


def filter_departments(request, qs):
    q = request.GET.get('q')
    if q:
        qs = qs.filter(name__icontains=q)
    return qs


def filter_employees(request, qs):
    q = request.GET.get('q')
    if q:
        qs = qs.filter(name__icontains=q)

    department_id = request.GET.get('department')
    if department_id:
        qs = qs.filter(department_id=department_id)

    return qs


def filter_employee_accounts(request, qs):
    q = request.GET.get('q')
    if q:
        qs = qs.filter(name__icontains=q)

    employee_id = request.GET.get('employee')
    if employee_id:
        qs = qs.filter(employee_id=employee_id)

    return qs


def filter_suppliers(request, qs):
    q = request.GET.get('q')
    if q:
        qs = qs.filter(name__icontains=q)

    medication_id = request.GET.get('medication')
    if medication_id:
        qs = qs.filter(medications__id=medication_id).distinct()

    return qs


def filter_sales(request, qs):
    q = request.GET.get('q')
    if q:
        qs = qs.filter(employee__name__icontains=q)

    employee_id = request.GET.get('employee')
    if employee_id:
        qs = qs.filter(employee_id=employee_id)

    made = request.GET.get('made')
    if made == "1":
        qs = qs.filter(made=True)
    elif made == "0":
        qs = qs.filter(made=False)

    date_from = request.GET.get('date_from')
    if date_from:
        qs = qs.filter(sale_date__date__gte=date_from)

    date_to = request.GET.get('date_to')
    if date_to:
        qs = qs.filter(sale_date__date__lte=date_to)

    min_total = request.GET.get('min_total')
    if min_total:
        qs = qs.filter(total_cost__gte=min_total)

    max_total = request.GET.get('max_total')
    if max_total:
        qs = qs.filter(total_cost__lte=max_total)

    return qs


def filter_saleitems(request, qs):
    q = request.GET.get('q')
    if q:
        qs = qs.filter(medication__name__icontains=q)

    sale_id = request.GET.get('sale')
    if sale_id:
        qs = qs.filter(sale_id=sale_id)

    medication_id = request.GET.get('medication')
    if medication_id:
        qs = qs.filter(medication_id=medication_id)

    min_count = request.GET.get('min_count')
    if min_count:
        qs = qs.filter(count__gte=min_count)

    max_count = request.GET.get('max_count')
    if max_count:
        qs = qs.filter(count__lte=max_count)

    return qs


def filter_categories(request, qs):
    q = request.GET.get('q')
    if q:
        qs = qs.filter(name__icontains=q)
    return qs


def filter_benefits(request, qs):
    q = request.GET.get('q')
    if q:
        qs = qs.filter(name__icontains=q)

    min_age = request.GET.get('min_age')
    if min_age:
        qs = qs.filter(min_age__gte=min_age)

    is_pensioner = request.GET.get('is_pensioner')
    if is_pensioner == "1":
        qs = qs.filter(is_pensioner=True)

    is_disability = request.GET.get('is_disability')
    if is_disability == "1":
        qs = qs.filter(is_disability=True)

    is_active = request.GET.get('is_active')
    if is_active == "1":
        qs = qs.filter(is_active=True)
    elif is_active == "0":
        qs = qs.filter(is_active=False)

    return qs


def filter_coupons(request, qs):
    is_active = request.GET.get('is_active')
    if is_active == "1":
        qs = qs.filter(is_active=True)
    elif is_active == "0":
        qs = qs.filter(is_active=False)

    min_percent = request.GET.get('min_percent')
    if min_percent:
        qs = qs.filter(discount_percent__gte=min_percent)

    max_percent = request.GET.get('max_percent')
    if max_percent:
        qs = qs.filter(discount_percent__lte=max_percent)

    return qs


def filter_vacancies(request, qs):
    q = request.GET.get('q')
    if q:
        qs = qs.filter(title__icontains=q)

    is_active = request.GET.get('is_active')
    if is_active == "1":
        qs = qs.filter(is_active=True)
    elif is_active == "0":
        qs = qs.filter(is_active=False)

    date_from = request.GET.get('date_from')
    if date_from:
        qs = qs.filter(created_at__date__gte=date_from)

    date_to = request.GET.get('date_to')
    if date_to:
        qs = qs.filter(created_at__date__lte=date_to)

    return qs