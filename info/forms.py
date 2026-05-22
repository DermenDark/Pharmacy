from django import forms
from .models import AboutCompany, News, Review, Term

class DateTimeLocalInput(forms.DateTimeInput):
    input_type = "datetime-local"


class AboutCompanyForm(forms.ModelForm):
    class Meta:
        model = AboutCompany
        fields = ["title", "text", "video_url", "logo", "history", "requisites"]
        labels = {
            "title": "Заголовок",
            "text": "Текст о компании",
            "video_url": "Ссылка на видео",
            "logo": "Логотип",
            "history": "История по годам",
            "requisites": "Реквизиты",
        }
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "О компании"}),
            "text": forms.Textarea(attrs={"rows": 6}),
            "video_url": forms.URLInput(attrs={"placeholder": "https://..."}),
            "history": forms.Textarea(attrs={"rows": 5}),
            "requisites": forms.Textarea(attrs={"rows": 4}),
        }


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ["title", "short_content", "content", "image", "is_published"]
        labels = {
            "title": "Заголовок",
            "short_content": "Краткое содержание",
            "content": "Полная статья",
            "image": "Изображение",
            "is_published": "Опубликовано",
        }
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Заголовок новости"}),
            "short_content": forms.Textarea(attrs={"rows": 3}),
            "content": forms.Textarea(attrs={"rows": 7}),
            "is_published": forms.CheckboxInput(),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "text"]
        labels = {
            "rating": "Оценка",
            "text": "Текст отзыва",
        }
        widgets = {
            "rating": forms.NumberInput(attrs={"min": 1, "max": 5}),
            "text": forms.Textarea(attrs={"rows": 5})
        }

    def clean_rating(self):
        rating = self.cleaned_data["rating"]
        if rating < 1 or rating > 5:
            raise forms.ValidationError("Оценка должна быть от 1 до 5.")
        return rating


class TermForm(forms.ModelForm):
    class Meta:
        model = Term
        fields = ["question", "answer"]
        labels = {
            "question": "Вопрос",
            "answer": "Ответ",
        }
        widgets = {
            "question": forms.TextInput(attrs={"placeholder": "Термин или вопрос"}),
            "answer": forms.Textarea(attrs={"rows": 6}),
        }