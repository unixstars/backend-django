from django.urls import path, include


urlpatterns = [
    path("", include("activity.urls")),
    path("auth/", include("dj_rest_auth.urls")),
    path("auth/", include("dj_rest_auth.registration.urls")),
    path("allauth/", include("allauth.urls")),
    path("auth/", include("authentication.urls")),
]
