from django.db import migrations, models
from django.utils.text import slugify


def generate_unique_slugs(apps, schema_editor):
    Product = apps.get_model("SE_sales", "Product")

    for product in Product.objects.all():
        # si ya tiene slug por alguna razón, respétalo
        if getattr(product, "slug", None):
            continue

        base = slugify(product.name or product.sku or "producto")
        if not base:
            base = "producto"

        cand = base
        i = 1
        # evitar colisiones de slug
        while Product.objects.filter(slug=cand).exclude(pk=product.pk).exists():
            cand = f"{base}-{i}"
            i += 1

        product.slug = cand
        product.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("SE_sales", "0010_remove_product_slug"),
    ]

    operations = [
        # 1) agregamos el campo slug SIN unique
        migrations.AddField(
            model_name="product",
            name="slug",
            field=models.SlugField(max_length=140, blank=True),
        ),
        # 2) rellenamos valores únicos para todos los productos ya existentes
        migrations.RunPython(generate_unique_slugs, migrations.RunPython.noop),
        # 3) ahora sí, marcamos el campo como unique
        migrations.AlterField(
            model_name="product",
            name="slug",
            field=models.SlugField(max_length=140, unique=True, blank=True),
        ),
    ]
