from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from .models import Student, Attendance
from tutor.models import Course

import os
import cv2

# Optional face_recognition (requires dlib); we guard import
FR_AVAILABLE = True
try:
    import face_recognition
except Exception:
    FR_AVAILABLE = False

def home(request):
    return render(request, 'attendance/home.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        student_id = request.POST.get('student_id')
        file = request.FILES.get('face_image')
        course_id = request.POST.get('course') 
        if not (username and password and student_id and file):
            messages.error(request, 'All fields are required.')
            return redirect('register')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')
        if Student.objects.filter(student_id=student_id).exists():
            messages.error(request, 'Student ID already exists.')
            return redirect('register')
        user = User.objects.create_user(username=username, password=password)
        course = Course.objects.filter(id=course_id).first()
        Student.objects.create(user=user, student_id=student_id, face_image=file,course=course)
        messages.success(request, 'Registration successful. Please login.')
        return redirect('login')
    courses = Course.objects.all()
    return render(request, 'attendance/register.html',{'courses': courses})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        messages.error(request, 'Invalid credentials.')
        return redirect('login')
    return render(request, 'attendance/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def mark_attendance(request):
    # Build known encodings on the fly (for demo)
    students = Student.objects.all()
    known_encodings = []
    student_ids = []
    if FR_AVAILABLE:
        for s in students:
            try:
                img = face_recognition.load_image_file(s.face_image.path)
                encs = face_recognition.face_encodings(img)
                if encs:
                    known_encodings.append(encs[0])
                    student_ids.append(s.id)
            except Exception:
                continue
    else:
        messages.error(request, 'face_recognition library not available. Please install dlib & face_recognition, or switch to an alternative approach.')
        return redirect('attendance_report')

    # Capture a single frame
    cap = cv2.VideoCapture(0)
    ok, frame = cap.read()
    cap.release()
    if not ok:
        messages.error(request, 'Could not access webcam.')
        return redirect('attendance_report')

    rgb = frame[:, :, ::-1]
    faces = face_recognition.face_locations(rgb)
    encs = face_recognition.face_encodings(rgb, faces)

    for enc in encs:
        matches = face_recognition.compare_faces(known_encodings, enc)
        if True in matches:
            idx = matches.index(True)
            student = Student.objects.get(id=student_ids[idx])
            Attendance.objects.create(student=student, date=now().date(), time=now().time(), status='Present')
            messages.success(request, f'Attendance marked for {student.user.username}')
            return redirect('attendance_report')

    messages.error(request, 'Face not recognized.')
    return redirect('attendance_report')

@login_required
def attendance_report(request):
    user = request.user
    if user.is_superuser:
        records = Attendance.objects.select_related('student','student__user').order_by('-date','-time')
    else:
        try:
            student = Student.objects.get(user=user)
            records = Attendance.objects.filter(student=student).order_by('-date','-time')
        except Student.DoesNotExist:
            records = []
    return render(request, 'attendance/report.html', {'records': records})



from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest
import base64, re, io
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

def face_recognize_page(request):
    """Render the face recognition page which captures webcam image and posts to API."""
    return render(request, 'attendance/face_recognition.html')

@csrf_exempt
def face_recognize_api(request):
    """Accepts a POSTed JSON with a dataURL image; attempts to recognize and mark attendance.
    This implementation will try to call a project-specific recognition function if available.
    It expects a function `recognize_face_from_image_bytes(image_bytes)` that returns a dict like {'success':True,'name':'Alice','user_id':1}.
"""
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')
    import json
    try:
        payload = json.loads(request.body.decode('utf-8'))
        dataurl = payload.get('image')
        if not dataurl:
            return JsonResponse({'success': False, 'message': 'No image provided'})
        # decode data URL
        header, encoded = dataurl.split(',', 1)
        image_bytes = base64.b64decode(encoded)
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Invalid image data: ' + str(e)})
    # Try to find an existing recognition function in the project
    recognized = None
    try:
        # common places
        from . import face_recog as fr
        if hasattr(fr, 'recognize_face_from_image_bytes'):
            recognized = fr.recognize_face_from_image_bytes(image_bytes)
    except Exception:
        recognized = None
    # If not recognized by project function, fallback to a dummy not-recognized response
    if not recognized:
        return JsonResponse({'success': False, 'message': 'No recognition function found in project. Please integrate your face recognition logic into attendance/face_recog.py as recognize_face_from_image_bytes(image_bytes)'})
    # recognized should be a dict with keys 'success' and optionally 'name' and 'user_id'
    if recognized.get('success'):
        name = recognized.get('name','Unknown')
        user_id = recognized.get('user_id', None)
        # Attempt to mark attendance in database if Attendance model exists
        try:
            from .models import Attendance
            from django.contrib.auth import get_user_model
            User = get_user_model()
            # Determine user: try user_id or match by username/name
            user = None
            if user_id:
                try:
                    user = User.objects.get(pk=user_id)
                except Exception:
                    user = None
            if not user and name:
                try:
                    user = User.objects.filter(username__iexact=name).first()
                except Exception:
                    user = None
            if user:
                Attendance.objects.create(user=user)
        except Exception:
            # if any error, continue; marking attendance is best-effort
            pass
        # Build redirect to attendance report - attempt common named url 'attendance_report' or 'report'
        try:
            redirect_url = reverse('attendance_report')
        except Exception:
            try:
                redirect_url = reverse('attendance_report')
            except Exception:
                redirect_url = '/'
        return JsonResponse({'success': True, 'name': name, 'redirect_url': redirect_url})
    else:
        return JsonResponse({'success': False, 'message': recognized.get('message','Not recognized')})
