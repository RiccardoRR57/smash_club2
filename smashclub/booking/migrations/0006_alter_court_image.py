# Generated by Django 5.2.3 on 2025-06-16 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0005_remove_booking_unique_booking_slot_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='court',
            name='image',
            field=models.ImageField(upload_to='courts/'),
        ),
    ]
