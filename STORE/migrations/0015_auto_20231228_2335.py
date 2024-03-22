from django.db import migrations
import uuid


def gen_uuid1(apps, schema_editor):
    Cart = apps.get_model("STORE", "Cart")
    for row in Cart.objects.all():
        row.uuid_id = uuid.uuid4()
        row.save(update_fields=["uuid_id"])

def gen_uuid2(apps, schema_editor):
            CartItem = apps.get_model("STORE", "CartItem")
            for row in CartItem.objects.all():
                row.uuid_id = uuid.uuid4()
                row.save(update_fields=["uuid_id"])


class Migration(migrations.Migration):

    dependencies = [
        ('STORE', '0014_cart_uuid_id_cartitem_uuid_id'),
    ]

    operations = [
        migrations.RunPython(gen_uuid1, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(gen_uuid2, reverse_code=migrations.RunPython.noop),
    ]
