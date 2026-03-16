from django.contrib import admin
from .models import (
    Location, Teacher, ClassRoom, ScheduleVersion, Schedule, AttendanceOverride,
    JournalTeacher, SchoolConfig, ClassJournal,
    JournalClass, SubjectJournal, JournalWeek, JournalRow, JournalEntry,
)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('teacher_code', 'full_name', 'display_subject')
    search_fields = ('teacher_code', 'full_name')


@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'class_size', 'managing_campus', 'location')
    list_filter = ('grade',)


@admin.register(ScheduleVersion)
class ScheduleVersionAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'month', 'week', 'effective_from', 'effective_to', 'created_at')
    list_filter = ('year', 'month', 'week')


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'classroom', 'day_of_week', 'period', 'subject_name', 'session', 'version')
    list_filter = ('day_of_week', 'session', 'version')
    search_fields = ('teacher__teacher_code', 'teacher__full_name', 'classroom__name')


@admin.register(AttendanceOverride)
class AttendanceOverrideAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'year', 'month', 'day', 'value')
    list_filter = ('year', 'month')


@admin.register(JournalTeacher)
class JournalTeacherAdmin(admin.ModelAdmin):
    list_display = ('access_code', 'full_name', 'subject', 'num_classes')
    search_fields = ('access_code', 'full_name', 'subject')


@admin.register(JournalClass)
class JournalClassAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(SubjectJournal)
class SubjectJournalAdmin(admin.ModelAdmin):
    list_display = ('subject', 'year', 'week1_start_date')
    list_filter = ('year', 'subject')


@admin.register(JournalWeek)
class JournalWeekAdmin(admin.ModelAdmin):
    list_display = ('subject_journal', 'week_number', 'start_date', 'end_date', 'is_locked')
    list_filter = ('is_locked',)


@admin.register(JournalRow)
class JournalRowAdmin(admin.ModelAdmin):
    list_display = ('subject_journal', 'row_order', 'teacher')
    list_filter = ('subject_journal',)


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ('journal_row', 'week_number', 'lesson_date', 'period', 'classes_taught', 'lesson_title')
    list_filter = ('week_number',)


@admin.register(SchoolConfig)
class SchoolConfigAdmin(admin.ModelAdmin):
    list_display = ('current_date', 'current_week', 'updated_at')


@admin.register(ClassJournal)
class ClassJournalAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'lesson_date', 'week', 'subject', 'lesson_title', 'rating', 'completed')
    list_filter = ('week', 'rating', 'completed')
    search_fields = ('teacher__full_name', 'lesson_title', 'absent_students')
