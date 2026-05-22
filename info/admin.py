from django.contrib import admin

from .models import AboutCompany, News, Review, Term


@admin.register(AboutCompany)
class AboutCompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    search_fields = ("title",)


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "is_published", "created_at")
    search_fields = ("title", "short_content")
    list_filter = ("is_published", "created_at")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "rating", "is_published", "created_at")
    search_fields = ("name", "text")
    list_filter = ("rating", "is_published", "created_at")


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "created_at")
    search_fields = ("question", "answer")
    list_filter = ("created_at",)
