# Generated by Django 4.2.7 on 2024-11-27 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0012_remove_post_pdf_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='gv',
            name='enable',
            field=models.BooleanField(default=True),
        ),
    ]
