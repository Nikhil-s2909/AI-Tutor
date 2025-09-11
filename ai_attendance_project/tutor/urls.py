from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat_page, name='chat_page'),
    path('ask/', views.ask_tutor, name='ask_tutor'),
]


# Added by ChatGPT
from .views import chat_view
urlpatterns += [ path('ai-chat/', chat_view, name='ai_chat') ]
