# Generated by Django 5.2.4 on 2025-07-22 14:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0002_remove_movimientos_cuenta_id_and_more'),
        ('ordenes', '0007_alter_equipo_cliente_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipo',
            name='cliente_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cliente.cliente'),
        ),
    ]
