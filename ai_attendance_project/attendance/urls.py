from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('mark/', views.mark_attendance, name='mark_attendance'),
    path('report/', views.attendance_report, name='attendance_report'),
]



# Added by assistant: face recognition pages
from . import views as attendance_views
from django.urls import path

urlpatterns += [
    path('face/', attendance_views.face_recognize_page, name='face_recognize_page'),
    path('face_api/', attendance_views.face_recognize_api, name='face_recognize_api'),
]
