# Generated by Django 4.2.7 on 2024-11-27 08:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0011_uploadedfile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='pdf_file',
        ),
    ]
