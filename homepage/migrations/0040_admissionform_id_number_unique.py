from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0039_vocational_training'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admissionform',
            name='id_number',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
