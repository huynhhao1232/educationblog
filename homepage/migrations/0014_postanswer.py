# Generated by Django 4.2.7 on 2024-11-29 09:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0013_gv_enable'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostAnswer',
            fields=[
                ('post_id', models.AutoField(primary_key=True, serialize=False)),
                ('post_title', models.CharField(max_length=100, null=True)),
                ('post_content', models.TextField(max_length=100, null=True)),
                ('post_approved', models.BooleanField(default=False)),
                ('post_enable', models.BooleanField(default=False)),
                ('post_createdate', models.DateTimeField(auto_now_add=True, null=True)),
                ('post_editdate', models.DateTimeField(auto_now_add=True, null=True)),
                ('account', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='homepage.account')),
            ],
        ),
    ]
