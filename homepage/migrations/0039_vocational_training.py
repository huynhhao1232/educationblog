import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0038_admissionform_conduct_grades'),
    ]

    operations = [
        migrations.CreateModel(
            name='VocationalCampus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('code', models.CharField(blank=True, max_length=20, unique=True)),
                ('address', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Cơ sở dạy nghề',
                'verbose_name_plural': 'Cơ sở dạy nghề',
            },
        ),
        migrations.CreateModel(
            name='VocationalTrade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('vocational_campus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trades', to='homepage.vocationalcampus')),
            ],
            options={
                'verbose_name': 'Nghề',
                'verbose_name_plural': 'Nghề',
                'unique_together': {('vocational_campus', 'name')},
            },
        ),
        migrations.CreateModel(
            name='CampusVocationalLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('admission_campus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vocational_links', to='homepage.campus')),
                ('vocational_campus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='admission_links', to='homepage.vocationalcampus')),
            ],
            options={
                'verbose_name': 'Liên kết cơ sở dạy nghề',
                'verbose_name_plural': 'Liên kết cơ sở dạy nghề',
                'unique_together': {('admission_campus', 'vocational_campus')},
            },
        ),
        migrations.AddField(
            model_name='admissionform',
            name='study_vocational',
            field=models.CharField(choices=[('no', 'Không học nghề'), ('yes', 'Học nghề')], default='no', max_length=3),
        ),
        migrations.AddField(
            model_name='admissionform',
            name='vocational_campus',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='admissions', to='homepage.vocationalcampus'),
        ),
        migrations.AddField(
            model_name='admissionform',
            name='vocational_trade',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='admissions', to='homepage.vocationaltrade'),
        ),
    ]
