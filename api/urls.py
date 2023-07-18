from django.urls import path, include


urlpatterns = [
    path("", include("activity.urls")),
    path("auth/", include("dj_rest_auth.urls")),
    path("auth/", include("dj_rest_auth.registration.urls")),
    path("auth/", include("authentication.urls")),
]
