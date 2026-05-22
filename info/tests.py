from datetime import date
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from pharmacy.models import UserProfile

from .models import AboutCompany, News, Review, Term


def _birth_date_years_ago(years: int):
    today = date.today()
    year = today.year - years
    day = min(today.day, 28)
    return date(year, today.month, day)


class InfoViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        AboutCompany.objects.create(
            title="О компании",
            text="Текст о компании",
        )
        cls.latest_news = News.objects.create(
            title="Последняя новость",
            short_content="Кратко о последней новости",
            content="Полный текст последней новости",
            is_published=True,
        )
        News.objects.create(
            title="Старая новость",
            short_content="Старое",
            content="Старый текст",
            is_published=True,
        )
        Review.objects.create(name="Анна", rating=5, text="Отлично")
        Term.objects.create(question="Что это?", answer="Ответ")
        cls.user = User.objects.create_user(username="info_user", password="pass12345")
        UserProfile.objects.update_or_create(
            user=cls.user,
            defaults={
                "birth_date": _birth_date_years_ago(22),
                "phone": "+375 (29) 123-45-67",
            },
        )

    def test_home_page_anonymous_does_not_call_external_apis(self):
        client = Client()
        with patch("info.views.requests.get") as mocked_get:
            response = client.get(reverse("about_company"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(mocked_get.call_count, 0)
        self.assertContains(response, "Последняя статья")
        self.assertContains(response, self.latest_news.title)

    def test_home_page_authenticated_calls_external_apis(self):
        client = Client()
        self.assertTrue(client.login(username="info_user", password="pass12345"))

        weather_response = Mock()
        weather_response.json.return_value = {
            "cod": 200,
            "main": {"temp": 18},
            "weather": [{"icon": "10d"}],
        }
        weather_response.status_code = 200

        history_response = Mock()
        history_response.status_code = 200
        history_response.json.return_value = [{"event": "Some event"}]

        with patch("info.views.requests.get", side_effect=[weather_response, history_response]) as mocked_get:
            response = client.get(reverse("about_company"), {"city": "Minsk"})

        self.assertEqual(mocked_get.call_count, 2)
        self.assertEqual(response.context["weather"]["city"], "Minsk")
        self.assertEqual(response.context["weather"]["temp"], 18)
        self.assertEqual(response.context["history_day2"], "Some event")
        self.assertContains(response, "Погода в городе: Minsk")

    def test_news_detail_returns_404_for_unpublished(self):
        unpublished = News.objects.create(
            title="Черновик",
            short_content="Не опубликовано",
            content="Текст",
            is_published=False,
        )
        client = Client()
        response = client.get(reverse("news_detail", kwargs={"pk": unpublished.pk}))
        self.assertEqual(response.status_code, 404)

    def test_news_detail_returns_200_for_published(self):
        client = Client()
        response = client.get(reverse("news_detail", kwargs={"pk": self.latest_news.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.latest_news.content)
