from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .models import Syllabus, ClassTiming
import os
import json

# Optional OpenAI import; keep the app running even if not installed
OPENAI_AVAILABLE = True
try:
    from openai import OpenAI
except Exception:
    OPENAI_AVAILABLE = False
    OpenAI = None

def chat_page(request):
    return render(request, 'tutor/chat.html')

@csrf_exempt
def ask_tutor(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        data = json.loads(request.body.decode('utf-8'))
        question = data.get('question', '').strip()
    except Exception:
        question = request.POST.get('question', '').strip()
    if not question:
        return JsonResponse({'answer': 'Please ask a question.'})

    # Fallback response if OpenAI not configured
    if not OPENAI_AVAILABLE or not os.getenv('OPENAI_API_KEY'):
        # Very small rule-based tutor
        if 'attendance' in question.lower():
            answer = 'Attendance is marked when your face is recognized via webcam and saved to the database with timestamp.'
        else:
            answer = 'AI Tutor offline mode: I need an OpenAI API key set in OPENAI_API_KEY to give detailed answers.'
        return JsonResponse({'answer': answer})

    # Use OpenAI API
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    try:
        completion = client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL','gpt-3.5-turbo'),
            messages=[
                {'role':'system','content':'You are a helpful AI tutor for students using a Face Recognition Attendance app. Explain clearly and concisely.'},
                {'role':'user','content':question}
            ],
            temperature=0.2
        )
        answer = completion.choices[0].message.content
        return JsonResponse({'answer': answer})
    except Exception as e:
        return JsonResponse({'answer': f'Error from AI service: {e}'})


# -- Added by ChatGPT --
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def chat_view(request):
    syllabus = None
    if hasattr(request.user, 'student') and request.user.student.course:
        syllabus = request.user.student.course.syllabus

    return render(request, 'tutor/chat.html', {
        'syllabus': syllabus,
        'timings': [],  # you can extend later
    })




# def chat_view(request):
#     syllabus = Syllabus.objects.all()
#     timings = ClassTiming.objects.all()
#     return render(request, "tutor/chat.html", {
#         "syllabus": syllabus,
#         "timings": timings
#     })
