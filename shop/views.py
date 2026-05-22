from datetime import timezone
import logging
from decimal import Decimal

from django.db.models import F
from .form import CheckoutForm
from pharmacy.models import Medication, Sale, SaleItem, Coupons
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from pharmacy.models import Medication, UserProfile
from shop.services import approve_order_to_sale

from .models import Cart, CartItem, Order

logger = logging.getLogger("shop")


@login_required(login_url="login_view")
def profile_view(request):
    logger.info("Открыт профиль пользователя %s", request.user)

    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related("medication").all()
    orders = request.user.orders.prefetch_related("items__medication").order_by("-created_at")
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    return render(request, "shop/profile.html", {
        "profile_user": request.user,
        "user_profile": user_profile,
        "cart": cart,
        "cart_items": cart_items,
        "orders": orders,
    })


@login_required(login_url="login_view")
def cart_view(request):
    logger.info("Открыта корзина пользователя %s", request.user)

    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related("medication").all()

    return render(request, "shop/cart.html", {
        "cart": cart,
        "items": items,
        "total_cost": cart.total_cost,
    })


@login_required(login_url="login_view")
def add_to_cart(request, pk):
    medication = get_object_or_404(Medication, pk=pk)
    logger.info("Попытка добавить товар id=%s в корзину пользователем %s", pk, request.user)

    if medication.count <= 0:
        messages.error(request, "Товара нет в наличии.")
        logger.warning("Товар id=%s недоступен для добавления пользователем %s", pk, request.user)
        return redirect("catalog")

    cart, _ = Cart.objects.get_or_create(user=request.user)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        medication=medication,
        defaults={"quantity": 1},
    )

    if not created:
        if item.quantity < medication.count:
            item.quantity += 1
            item.save()
            messages.success(request, f"{medication.name} добавлен в корзину.")
            logger.info("Увеличено количество товара id=%s в корзине пользователем %s", pk, request.user)
        else:
            messages.warning(request, "Нельзя добавить больше, чем есть в наличии.")
            logger.warning("Превышено доступное количество товара id=%s пользователем %s", pk, request.user)
    else:
        messages.success(request, f"{medication.name} добавлен в корзину.")
        logger.info("Товар id=%s добавлен в корзину пользователем %s", pk, request.user)

    return redirect("shop:cart")


@login_required(login_url="login_view")
def cart_item_add(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)

    if item.quantity < item.medication.count:
        item.quantity += 1
        item.save()
        logger.info("Увеличено количество позиции id=%s пользователем %s", item_id, request.user)
    else:
        messages.warning(request, "Нельзя добавить больше, чем есть в наличии.")
        logger.warning("Превышен лимит позиции id=%s пользователем %s", item_id, request.user)

    return redirect("shop:cart")


@login_required(login_url="login_view")
def cart_item_notadd(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
        logger.info("Уменьшено количество позиции id=%s пользователем %s", item_id, request.user)
    else:
        item.delete()
        logger.warning("Позиция id=%s удалена из корзины пользователем %s", item_id, request.user)

    return redirect("shop:cart")


@login_required(login_url="login_view")
def cart_item_delete(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    item.delete()
    logger.warning("Позиция id=%s удалена из корзины пользователем %s", item_id, request.user)
    return redirect("shop:cart")


@login_required(login_url="login_view")
def checkout(request):
    cart_items = request.session.get("cart", {})
    form = CheckoutForm(request.POST or None)

    if not cart_items:
        return render(request, "shop/checkout.html", {
            "form": form,
            "cart_items": {},
            "error": "Корзина пуста.",
        })

    if request.method == "POST" and form.is_valid():
        selected_coupons = form.cleaned_data["coupons"]

        medication_ids = list(cart_items.keys())
        medications = Medication.objects.filter(id__in=medication_ids)

        items = []
        subtotal = Decimal("0.00")

        for medic in medications:
            qty = int(cart_items[str(medic.id)])
            line_total = medic.cost * qty
            subtotal += line_total
            items.append((medic, qty, line_total))

        now = timezone.now()
        discount_total = Decimal("0.00")
        valid_coupons = []

        for coupon in selected_coupons:
            if not coupon.is_active:
                continue
            if coupon.valid_from and coupon.valid_from > now:
                continue
            if coupon.valid_to and coupon.valid_to < now:
                continue
            if coupon.usage_limit is not None and coupon.used_count >= coupon.usage_limit:
                continue
            valid_coupons.append(coupon)

        for coupon in valid_coupons:
            if coupon.discount_cost:
                discount_total += coupon.discount_cost

            if coupon.discount_percent:
                discount_total += (subtotal * Decimal(coupon.discount_percent) / Decimal("100"))

        if discount_total > subtotal:
            discount_total = subtotal

        final_total = subtotal - discount_total

        with transaction.atomic():
            # ВАЖНО: тут подставь свою связь с сотрудником/кассиром
            sale = Sale.objects.create(
                employee=request.user.employeeaccount.employee,
                total_cost=final_total,
                discount_total=discount_total,
            )

            for medic, qty, line_total in items:
                SaleItem.objects.create(
                    sale=sale,
                    medication=medic,
                    quantity=qty,
                    price=medic.cost,
                )

            sale.coupons.set(valid_coupons)

            Coupons.objects.filter(pk__in=[c.pk for c in valid_coupons]).update(
                used_count=F("used_count") + 1
            )

        request.session["cart"] = {}
        logger.info("Покупка оформлена пользователем %s", request.user)
        return redirect("sale_detail", pk=sale.pk)

    return render(request, "shop/checkout.html", {
        "form": form,
        "cart_items": cart_items,
    })

@login_required(login_url="login_view")
@permission_required("shop.view_order", raise_exception=True)
def orders_to_process(request):
    orders = (
        Order.objects
        .filter(status=Order.Status.NEW)
        .select_related("user")
        .prefetch_related("items__medication")
        .order_by("-created_at")
    )

    return render(request, "shop/orders_to_process.html", {
        "orders": orders
    })


@login_required(login_url="login_view")
@permission_required("shop.change_order", raise_exception=True)
@require_POST
@transaction.atomic
def approve_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, status=Order.Status.NEW)

    employee = getattr(request.user, "employee", None)
    if employee is None:
        messages.error(request, "У текущего пользователя нет профиля сотрудника.")

    approve_order_to_sale(order, employee)
    messages.success(request, f"Заказ #{order.id} одобрен и передан в продажу.")
    return redirect("shop:orders_to_process")


@login_required(login_url="login_view")
def order_history(request):
    """
    История заказов:
    - обычному пользователю показываются только его заказы;
    - пользователю с правом shop.view_order показываются все заказы.
    """
    if request.user.has_perm("shop.view_order"):
        orders = Order.objects.select_related("user").prefetch_related("items__medication").order_by("-created_at")
    else:
        orders = request.user.orders.select_related("user").prefetch_related("items__medication").order_by("-created_at")

    return render(request, "shop/order_history.html", {
        "orders": orders,
    })


@login_required(login_url="login_view")
def order_detail(request, order_id):
    """
    Карточка заказа:
    - сотрудник с shop.view_order видит любой заказ;
    - обычный пользователь — только свой заказ.
    """
    if request.user.has_perm("shop.view_order"):
        order = get_object_or_404(
            Order.objects.select_related("user").prefetch_related("items__medication"),
            pk=order_id,
        )
    else:
        order = get_object_or_404(
            Order.objects.select_related("user").prefetch_related("items__medication"),
            pk=order_id,
            user=request.user,
        )

    return render(request, "shop/order_detail.html", {
        "order": order,
        "is_employee": request.user.has_perm("shop.change_order"),
    })


@login_required(login_url="login_view")
@require_POST
@transaction.atomic
def cancel_order(request, order_id):
    """
    Отмена только собственного нового заказа.
    Возвращает товары обратно на склад.
    """
    order = get_object_or_404(
        Order.objects.prefetch_related("items__medication"),
        pk=order_id,
        user=request.user,
        status=Order.Status.NEW,
    )

    for item in order.items.all():
        medication = item.medication
        medication.count += item.quantity
        medication.save(update_fields=["count"])

    order.status = Order.Status.REJECTED
    order.save(update_fields=["status"])

    messages.success(request, f"Заказ #{order.id} отменён.")
    return redirect("shop:order_detail", order_id=order.id)