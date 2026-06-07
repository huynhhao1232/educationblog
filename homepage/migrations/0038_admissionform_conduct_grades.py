from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0028_examroomshiftconfig'),
    ]

    operations = [
        migrations.AddField(
            model_name='admissionform',
            name='conduct_6',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='KQRL lớp 6'),
        ),
        migrations.AddField(
            model_name='admissionform',
            name='conduct_7',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='KQRL lớp 7'),
        ),
        migrations.AddField(
            model_name='admissionform',
            name='conduct_8',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='KQRL lớp 8'),
        ),
        migrations.AddField(
            model_name='admissionform',
            name='conduct_9',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='KQRL lớp 9'),
        ),
    ]
