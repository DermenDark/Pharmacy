from pharmacy.models import Sale, SaleItem


def approve_order_to_sale(order, employee):
    sale = Sale.objects.create(
        order=order,
        employee=employee,
        total_cost=order.total_cost,
        made=True,
    )

    for item in order.items.all():
        SaleItem.objects.create(
            sale=sale,
            medication=item.medication,
            count=item.quantity,
        )

    order.status = "done"
    order.save(update_fields=["status"])

    return sale

