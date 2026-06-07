from django.db import migrations, models


def seed_room_sort_order(apps, schema_editor):
    ExamSort2Room = apps.get_model('homepage', 'ExamSort2Room')
    by_venue: dict[int, list] = {}
    for room in ExamSort2Room.objects.order_by('venue_id', 'name', 'pk'):
        by_venue.setdefault(room.venue_id, []).append(room)
    for rooms in by_venue.values():
        for idx, room in enumerate(rooms, start=1):
            if not room.sort_order:
                room.sort_order = idx
                room.save(update_fields=['sort_order'])


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0042_exam_sort2_elective_subjects'),
    ]

    operations = [
        migrations.AddField(
            model_name='examsort2candidate',
            name='exam_number',
            field=models.CharField(blank=True, default='', max_length=12, verbose_name='Số báo danh'),
        ),
        migrations.AddField(
            model_name='examsort2room',
            name='sort_order',
            field=models.PositiveIntegerField(default=0, verbose_name='STT'),
        ),
        migrations.AlterModelOptions(
            name='examsort2room',
            options={
                'ordering': ['sort_order', 'name'],
                'verbose_name': 'Phòng thi (SXPT II)',
                'verbose_name_plural': 'Phòng thi (SXPT II)',
            },
        ),
        migrations.RunPython(seed_room_sort_order, migrations.RunPython.noop),
    ]
