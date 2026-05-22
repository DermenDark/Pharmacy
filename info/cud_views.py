import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required

from .models import AboutCompany, News, Review, Term
from .forms import AboutCompanyForm, NewsForm, ReviewForm, TermForm

logger = logging.getLogger("info")


def _save_form_view(request, form_class, template_name, success_url, instance=None, extra_context=None):
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

    context = {
        "form": form,
        "object": instance,
    }
    if extra_context:
        context.update(extra_context)

    return render(request, template_name, context)


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
@permission_required("info.add_aboutcompany", raise_exception=True)
def about_company_create(request):
    existing = AboutCompany.objects.first()
    if existing:
        logger.warning("Попытка создать вторую запись AboutCompany пользователем %s", request.user)
        return redirect("about_company_edit", pk=existing.pk)

    logger.info("Открыта форма создания AboutCompany пользователем %s", request.user)
    return _save_form_view(
        request,
        AboutCompanyForm,
        "form.html",
        "about_company",
        extra_context={"title": "О компании"},
    )


@login_required
@permission_required("info.change_aboutcompany", raise_exception=True)
def about_company_edit(request, pk):
    obj = get_object_or_404(AboutCompany, pk=pk)
    logger.info("Открыта форма редактирования AboutCompany id=%s пользователем %s", pk, request.user)

    return _save_form_view(
        request,
        AboutCompanyForm,
        "form.html",
        "about_company",
        instance=obj,
        extra_context={"title": "О компании"},
    )


@login_required
@permission_required("info.delete_aboutcompany", raise_exception=True)
def about_company_delete(request, pk):
    obj = get_object_or_404(AboutCompany, pk=pk)
    return _delete_view(request, obj, "delete.html", "about_company")


@login_required
@permission_required("info.add_news", raise_exception=True)
def news_create(request):
    logger.info("Открыта форма создания новости пользователем %s", request.user)
    return _save_form_view(
        request,
        NewsForm,
        "form.html",
        "news",
        extra_context={"title": "Новости"},
    )


@login_required
@permission_required("info.change_news", raise_exception=True)
def news_edit(request, pk):
    obj = get_object_or_404(News, pk=pk)
    logger.info("Открыта форма редактирования новости id=%s пользователем %s", pk, request.user)

    return _save_form_view(
        request,
        NewsForm,
        "form.html",
        "news",
        instance=obj,
        extra_context={"title": "Новости"},
    )


@login_required
@permission_required("info.delete_news", raise_exception=True)
def news_delete(request, pk):
    obj = get_object_or_404(News, pk=pk)
    return _delete_view(request, obj, "delete.html", "news")


@login_required
@permission_required("info.add_review", raise_exception=True)
def review_create(request):
    logger.info("Открыта форма создания отзыва пользователем %s", request.user)

    form = ReviewForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            review = form.save(commit=False)
            review.name = request.user.profile
            review.published = True

            review.save()

            return redirect("reviews")

    return render(
        request,
        "form.html",
        {
            "form": form,
            "title": "Добавить отзыв",
        },
    )


@login_required
@permission_required("info.change_review", raise_exception=True)
def review_edit(request, pk):
    obj = get_object_or_404(Review, pk=pk)
    logger.info("Открыта форма редактирования отзыва id=%s пользователем %s", pk, request.user)

    return _save_form_view(
        request,
        ReviewForm,
        "form.html",
        "reviews",
        instance=obj,
        extra_context={"title": "Отзывы"},
    )


@login_required
@permission_required("info.delete_review", raise_exception=True)
def review_delete(request, pk):
    obj = get_object_or_404(Review, pk=pk)
    return _delete_view(request, obj, "delete.html", "reviews")


@login_required
@permission_required("info.add_term", raise_exception=True)
def term_create(request):
    logger.info("Открыта форма создания термина пользователем %s", request.user)
    return _save_form_view(
        request,
        TermForm,
        "form.html",
        "terms",
        extra_context={"title": "Словарь"},
    )


@login_required
@permission_required("info.change_term", raise_exception=True)
def term_edit(request, pk):
    obj = get_object_or_404(Term, pk=pk)
    logger.info("Открыта форма редактирования термина id=%s пользователем %s", pk, request.user)

    return _save_form_view(
        request,
        TermForm,
        "form.html",
        "terms",
        instance=obj,
        extra_context={"title": "Словарь"},
    )


@login_required
@permission_required("info.delete_term", raise_exception=True)
def term_delete(request, pk):
    obj = get_object_or_404(Term, pk=pk)
    return _delete_view(request, obj, "delete.html", "terms")


@login_required
@permission_required("info.view_news", raise_exception=True)
def admin_news(request):
    logger.info("Открыта админ-страница новостей пользователем %s", request.user)
    news_list = News.objects.all().order_by("-created_at")
    return render(request, "info/news.html", {
        "news": news_list
    })


@login_required
@permission_required("info.view_review", raise_exception=True)
def admin_reviews(request):
    logger.info("Открыта админ-страница отзывов пользователем %s", request.user)
    reviews_list = Review.objects.all().order_by("-created_at")
    return render(request, "info/reviews.html", {
        "reviews": reviews_list
    })


@login_required
@permission_required("info.view_term", raise_exception=True)
def admin_terms(request):
    logger.info("Открыта админ-страница словаря пользователем %s", request.user)
    terms_list = Term.objects.all().order_by("-created_at")
    return render(request, "info/terms.html", {
        "terms": terms_list
    })