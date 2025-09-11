
from django.contrib import admin
from .models import Syllabus, ClassTiming,Course

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name',)   # tuple with one element
    search_fields = ('name',)


@admin.register(Syllabus)
class SyllabusAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    ordering = ('order',)

@admin.register(ClassTiming)
class ClassTimingAdmin(admin.ModelAdmin):
    list_display = ('subject', 'day', 'start_time', 'end_time')
