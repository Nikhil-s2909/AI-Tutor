from django.contrib import admin
from .models import Student, Attendance

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user','student_id')
    search_fields = ('user__username','student_id')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student','date','time','status')
    list_filter = ('date','status')
    search_fields = ('student__user__username','student__student_id')
