# SE_sales/api.py
from decimal import Decimal
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Product, Order, OrderItem
from .serializers import ProductSerializer, CheckoutSerializer

class ProductListAPI(APIView):
    def get(self, request):
        qs = Product.objects.all().order_by("name")
        data = ProductSerializer(qs, many=True).data
        return Response(data, status=200)

class CheckoutAPI(APIView):
    def post(self, request):
        ser = CheckoutSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        items = ser.validated_data["items"]
        customer_name  = ser.validated_data.get("customer_name", "")
        customer_email = ser.validated_data.get("customer_email", "")

        if not items:
            return Response({"detail": "Carrito vacío"}, status=400)

        try:
            with transaction.atomic():
                skus = sorted([i["sku"] for i in items])
                products = list(Product.objects.select_for_update().filter(sku__in=skus))
                by_sku = {p.sku: p for p in products}

                errors = []
                for it in items:
                    p = by_sku.get(it["sku"])
                    if not p:
                        errors.append(f"SKU inexistente: {it['sku']}")
                    elif p.stock < it["qty"]:
                        errors.append(f"Stock insuficiente para {it['sku']} (disp={p.stock}, req={it['qty']})")
                if errors:
                    return Response({"detail": "Validación falló", "errors": errors}, status=400)

                order = Order.objects.create(
                    customer_name=customer_name,
                    customer_email=customer_email,
                    total_amount=Decimal("0.00"),
                )

                total = Decimal("0.00")
                batch = []
                for it in items:
                    p = by_sku[it["sku"]]
                    qty = it["qty"]
                    line_total = (p.price or Decimal("0.00")) * qty
                    p.stock = F("stock") - qty
                    p.save(update_fields=["stock"])
                    batch.append(OrderItem(order=order, product=p, qty=qty, price_at=p.price, line_total=line_total))
                    total += line_total

                OrderItem.objects.bulk_create(batch)
                order.total_amount = total
                order.save(update_fields=["total_amount"])

            return Response({
                "order_id": order.id,
                "created_at": timezone.localtime(order.created_at).isoformat(),
                "total_amount": str(order.total_amount),
                "items": [{"sku": it["sku"], "qty": it["qty"]} for it in items],
            }, status=201)
        except Exception as e:
            return Response({"detail": f"Error en checkout: {e}"}, status=500)
