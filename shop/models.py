from django.db import models
from django.conf import settings
from decimal import Decimal

# Create your models here.

class Cart(models.Model):
    """Корзина пользователя"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Пользователь'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    def __str__(self):
        return f"Корзина {self.user.username}"

    @property
    def total_cost(self):
        return sum(
            (item.subtotal for item in self.items.select_related("medication")),
            Decimal("0.00")
        )


class CartItem(models.Model):
    """Позиция в корзине"""
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Корзина'
    )
    medication = models.ForeignKey(
        "pharmacy.Medication",
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name='Лекарство'
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')

    class Meta:
        unique_together = ('cart', 'medication')

    def __str__(self):
        return f"{self.medication.name} x {self.quantity}"

    @property
    def subtotal(self):
        return self.medication.cost * self.quantity


class Order(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новый"
        APPROVED = "approved", "Одобрен"
        REJECTED = "rejected", "Отклонён"
        DONE = "done", "Выполнен"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Пользователь"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата заказа")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name="Статус"
    )
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class OrderItem(models.Model):
    """Позиция заказа"""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заказ'
    )
    medication = models.ForeignKey(
        "pharmacy.Medication",
        on_delete=models.CASCADE,
        verbose_name='Лекарство'
    )
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена на момент покупки')

    def __str__(self):
        return f"{self.medication.name} x {self.quantity}"