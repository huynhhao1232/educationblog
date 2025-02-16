# Generated by Django 4.2.7 on 2024-11-24 01:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('homepage', '0008_alter_gv_namsinh'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountType',
            fields=[
                ('accounttype_id', models.AutoField(primary_key=True, serialize=False)),
                ('accounttype_role', models.CharField(max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('account_id', models.AutoField(primary_key=True, serialize=False)),
                ('account_phone', models.CharField(blank=True, max_length=20, null=True)),
                ('account_CCCD', models.CharField(blank=True, max_length=20, null=True)),
                ('account_address', models.CharField(blank=True, max_length=100, null=True)),
                ('account_createdate', models.DateTimeField(auto_now_add=True, null=True)),
                ('account_editdate', models.DateTimeField(auto_now_add=True, null=True)),
                ('account_enable', models.BooleanField(default=True)),
                ('account_picture', models.CharField(max_length=100, null=True)),
                ('forget_password_token', models.CharField(max_length=100, null=True)),
                ('accounttype', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='homepage.accounttype')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
