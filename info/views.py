import logging

import calendar
from django.utils import timezone
from datetime import date
import requests
from django.shortcuts import get_object_or_404, render

from .help_funk.filter import filter_news, filter_reviews, filter_terms
from .models import AboutCompany, News, Review, Term

logger = logging.getLogger("info")

def index(request):
    logger.info("Открыта главная страница пользователем %s", request.user)

    company = AboutCompany.objects.first()
    latest_news = News.objects.filter(is_published=True).order_by("-created_at").first()

    weather = None
    history_fact2 = None
    api_error = None
    city = request.GET.get("city", "London")

    if request.user.is_authenticated:
        appid = "63026ab922acdc159af4d7d5c6adca54"
        url = "https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=" + appid

        try:
            response = requests.get(url.format(city), timeout=5)
            res = response.json()

            if int(res.get("cod", 0)) == 200:
                weather = {
                    "city": city,
                    "temp": res["main"]["temp"],
                    "icon": res["weather"][0]["icon"],
                }
            else:
                api_error = "Город не найден"
                logger.error("API о погоде ответила с ошибкой: %s", res.get("cod"))
        except requests.RequestException as exc:
            api_error = "Ошибка подключения к API погоды"
            logger.error("Ошибка API погоды: %s", exc)

        api_url2 = "https://api.api-ninjas.com/v1/dayinhistory"
        try:
            response2 = requests.get(
                api_url2,
                headers={"X-Api-Key": "XYs4lfY3vc3uV7BsbrntM2PvZMiIeKLGzEd2a0X9"},
                timeout=5,
            )

            if response2.status_code == 200:
                data = response2.json()
                if data:
                    history_fact2 = data[0].get("event") if isinstance(data, list) else data.get("event")
            elif response2.status_code == 404:
                api_error = "API временно недоступен"
            else:
                api_error = f"Ошибка API: {response2.status_code}"
        except requests.RequestException as exc:
            api_error = "Ошибка подключения к API"
            logger.error("Ошибка API-Ninjas: %s", exc)

    today = date.today()
    month_matrix = calendar.monthcalendar(today.year, today.month)
    month_name = calendar.month_name[today.month]
    weekday_names = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    server_now = timezone.localtime(timezone.now())
    server_tz_name = timezone.get_current_timezone_name()
    return render(request, "info/index.html", {
        "company": company,
        "latest_news": latest_news,
        "weather": weather,
        "api_error": api_error,
        "history_day2": history_fact2,
        "today": today,
        "month_matrix": month_matrix,
        "month_name": month_name,
        "weekday_names": weekday_names,
        "server_now": server_now,
        "server_tz_name": server_tz_name,
    })


def news(request):
    logger.info("Открыт список новостей пользователем %s", request.user)
    news_list = News.objects.all().order_by("-created_at")
    news_list = filter_news(request, news_list)
    return render(request, "info/news.html", {"news": news_list})


def news_detail(request, pk):
    logger.info("Открыта новость id=%s пользователем %s", pk, request.user)
    news = get_object_or_404(News, pk=pk, is_published=True)
    return render(request, "info/news_detail.html", {"news": news})


def reviews(request):
    logger.info("Открыт список отзывов пользователем %s", request.user)
    reviews_list = Review.objects.all().order_by("-created_at")
    reviews_list = filter_reviews(request, reviews_list)
    return render(request, "info/reviews.html", {"reviews": reviews_list})


def terms(request):
    logger.info("Открыт словарь терминов пользователем %s", request.user)
    terms_list = Term.objects.all().order_by("-created_at")
    terms_list = filter_terms(request, terms_list)
    return render(request, "info/terms.html", {"terms": terms_list})


def politic(request):
    logger.info("Открыта страница политики конфиденциальности пользователем %s", request.user)
    return render(request, "info/politic.html")
