from django.db import migrations
from django.utils.text import slugify

def generate_unique_slugs(apps, schema_editor):
    Product = apps.get_model("SE_sales", "Product")

    for product in Product.objects.all():
        if not product.slug:
            base = slugify(product.name or product.sku or "producto")
            cand = base
            i = 1

            # evitar colisiones
            while Product.objects.filter(slug=cand).exclude(pk=product.pk).exists():
                cand = f"{base}-{i}"
                i += 1

            product.slug = cand
            product.save(update_fields=["slug"])

class Migration(migrations.Migration):

    dependencies = [
        ("SE_sales", "0009_product_image_product_image_url_product_slug"),
    ]

    operations = [
        migrations.RunPython(generate_unique_slugs),
    ]
