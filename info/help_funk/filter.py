def filter_news(request, qs):
    q = request.GET.get('q')
    if q:
        qs = qs.filter(title__icontains=q)

    is_published = request.GET.get('is_published')
    if is_published == "1":
        qs = qs.filter(is_published=True)
    elif is_published == "0":
        qs = qs.filter(is_published=False)

    date_from = request.GET.get('date_from')
    if date_from:
        qs = qs.filter(created_at__date__gte=date_from)

    date_to = request.GET.get('date_to')
    if date_to:
        qs = qs.filter(created_at__date__lte=date_to)

    return qs


def filter_reviews(request, qs):
    q = request.GET.get('q')
    if q:
        qs = qs.filter(name__icontains=q)

    rating = request.GET.get('rating')
    if rating:
        qs = qs.filter(rating=rating)

    is_published = request.GET.get('is_published')
    if is_published == "1":
        qs = qs.filter(is_published=True)
    elif is_published == "0":
        qs = qs.filter(is_published=False)

    return qs


def filter_terms(request, qs):
    q = request.GET.get('q')
    if q:
        qs = qs.filter(question__icontains=q)

    return qs