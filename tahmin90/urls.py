"""
URL configuration for tahmin90 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from tahmin90app.views import answer_question, match_questions, thanks, submit_predictions

urlpatterns = [
    path('admin/', admin.site.urls),
    path('question/<int:question_id>/', answer_question, name='answer_question'),
    path('match/<int:match_id>/', match_questions, name='match_questions'),
    path('predict/<int:match_id>/', submit_predictions, name='submit_predictions'),
    path('thanks/', thanks, name='thanks'),
]
