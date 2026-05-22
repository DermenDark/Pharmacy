import base64
import calendar
import logging
from io import BytesIO
from statistics import mean, median, multimode
from zoneinfo import ZoneInfo

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.utils import timezone

from pharmacy.models import Employee, Medication, Sale, SaleItem, UserProfile

logger = logging.getLogger("stats_graf")


def _safe_mode(values):
    if not values:
        return None
    modes = multimode(values)
    return modes[0] if modes else None


@login_required
@permission_required("pharmacy.view_sale", raise_exception=True)
def stats_view(request):
    logger.info("Открыта страница статистики пользователем %s", request.user)

    medications = Medication.objects.select_related("category").order_by("name")
    employees = Employee.objects.select_related("department").order_by("name")

    selected_medication_id = request.GET.get("medication") or ""
    selected_employee_id = request.GET.get("employee") or ""

    # Часовой пояс клиента из браузера, если пришёл; иначе серверный
    client_tz_name = request.GET.get("tz") or timezone.get_current_timezone_name()
    try:
        client_tz = ZoneInfo(client_tz_name)
    except Exception:
        client_tz = timezone.get_current_timezone()
        client_tz_name = timezone.get_current_timezone_name()

    made_sales = Sale.objects.filter(made=True).select_related("employee", "employee__department")
    sale_items = SaleItem.objects.filter(sale__made=True).select_related(
        "sale", "sale__employee", "medication", "medication__category"
    )

    total_revenue = made_sales.aggregate(total=Sum("total_cost"))["total"] or 0

    sales_totals = list(made_sales.values_list("total_cost", flat=True))
    sales_mean = mean(sales_totals) if sales_totals else None
    sales_median = median(sales_totals) if sales_totals else None
    sales_mode = _safe_mode(sales_totals)

    client_ages = [
        profile.age
        for profile in UserProfile.objects.select_related("user").all()
        if profile.age is not None
    ]
    clients_mean_age = mean(client_ages) if client_ages else None
    clients_median_age = median(client_ages) if client_ages else None

    by_department = (
        made_sales.values("employee__department__name")
        .annotate(total=Sum("total_cost"))
        .order_by("-total")
    )

    popular_categories = (
        sale_items.values("medication__category__name")
        .annotate(total_count=Sum("count"))
        .order_by("-total_count")
    )
    most_popular_category = popular_categories.first()

    sale_items_with_profit = sale_items.annotate(
        item_total=ExpressionWrapper(
            F("count") * F("medication__cost"),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
    )

    profitable_categories = (
        sale_items_with_profit.values("medication__category__name")
        .annotate(total_profit=Sum("item_total"))
        .order_by("-total_profit")
    )
    most_profitable_category = profitable_categories.first()

    # Продажи медикамента: если выбрано "Все", показываем все позиции
    selected_medication = None
    if selected_medication_id:
        selected_medication = medications.filter(pk=selected_medication_id).first()
        medication_sales = sale_items_with_profit.filter(medication_id=selected_medication_id)
    else:
        medication_sales = sale_items_with_profit.all()

    medication_sales = medication_sales.order_by("-sale__sale_date")

    # Продажи сотрудника: если выбрано "Все", показываем все продажи
    selected_employee = None
    if selected_employee_id:
        selected_employee = employees.filter(pk=selected_employee_id).first()
        employee_sales = made_sales.filter(employee_id=selected_employee_id)
    else:
        employee_sales = made_sales.all()

    employee_sales = employee_sales.order_by("-sale_date")

    sales_by_date = (
        made_sales.annotate(date=TruncDate("sale_date"))
        .values("date")
        .annotate(total=Sum("total_cost"))
        .order_by("date")
    )

    fig, ax = plt.subplots()
    if sales_by_date:
        dates = [entry["date"].strftime("%d.%m") for entry in sales_by_date]
        totals = [entry["total"] for entry in sales_by_date]
        ax.bar(dates, totals)
        ax.set_xlabel("Дата")
        ax.set_ylabel("Выручка")
        ax.set_title("Продажи по датам")
        plt.xticks(rotation=45)
        plt.tight_layout()
    else:
        ax.text(0.5, 0.5, "Нет данных", ha="center", va="center")
        ax.set_title("Продажи по датам")

    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    graphic = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()
    plt.close(fig)

    fig2, ax2 = plt.subplots()
    if by_department:
        dept_names = [d["employee__department__name"] or "Без отдела" for d in by_department]
        dept_totals = [d["total"] for d in by_department]
        ax2.pie(dept_totals, labels=dept_names, autopct="%1.1f%%", startangle=90)
        ax2.set_title("Выручка по отделам")
    else:
        ax2.text(0.5, 0.5, "Нет данных", ha="center", va="center")
        ax2.set_title("Выручка по отделам")

    buf2 = BytesIO()
    fig2.savefig(buf2, format="png")
    buf2.seek(0)
    graphic2 = base64.b64encode(buf2.read()).decode("utf-8")
    buf2.close()
    plt.close(fig2)

    now = timezone.now()
    local_now = now.astimezone(client_tz)
    calendar_text = calendar.TextCalendar(firstweekday=0).formatmonth(local_now.year, local_now.month)

    context = {
        "total_revenue": total_revenue,
        "sales_mean": sales_mean,
        "sales_median": sales_median,
        "sales_mode": sales_mode,
        "clients_mean_age": clients_mean_age,
        "clients_median_age": clients_median_age,
        "by_department": by_department,
        "popular_categories": popular_categories,
        "profitable_categories": profitable_categories,
        "most_popular_category": most_popular_category,
        "most_profitable_category": most_profitable_category,
        "medications": medications,
        "employees": employees,
        "selected_medication_id": selected_medication_id,
        "selected_employee_id": selected_employee_id,
        "selected_medication": selected_medication,
        "selected_employee": selected_employee,
        "medication_sales": medication_sales,
        "employee_sales": employee_sales,
        "graphic": graphic,
        "graphic2": graphic2,
        "current_timezone_name": client_tz_name,
        "current_datetime_local": local_now.strftime("%d/%m/%Y %H:%M"),
        "current_datetime_utc": now.strftime("%d/%m/%Y %H:%M"),
        "calendar_text": calendar_text,
    }
    return render(request, "stats_graf/stats.html", context)