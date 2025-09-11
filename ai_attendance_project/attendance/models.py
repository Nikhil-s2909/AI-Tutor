from django.db import models
from django.contrib.auth.models import User
from tutor.models import Course  # import at top

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    face_image = models.ImageField(upload_to='faces/')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.student_id}"



class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    status = models.CharField(max_length=10, default='Present')

    def __str__(self):
        return f"{self.student.user.username} - {self.date} {self.time} - {self.status}"
