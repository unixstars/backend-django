"""
URL configuration for config project.

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
import os
from dotenv import load_dotenv
from django.contrib import admin
from django.urls import path, include
from . import views
from api.views import AppConfigurationView

# .env 파일 로드
load_dotenv()

ENV_ROLE = os.getenv("ENV_ROLE")

urlpatterns = [
    path("", views.health_check),
    path("app-config/", AppConfigurationView.as_view()),
    path("api/v1/", include("api.urls")),
]

if ENV_ROLE == "development" or ENV_ROLE == "production":
    urlpatterns.insert(1, path("admin/", admin.site.urls))
