"""
URL configuration for ggr_credit_workflow project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def health_check(request):
    """Endpoint de sante pour Docker healthcheck."""
    return JsonResponse({"status": "ok"})


try:
    from django.contrib import admin

    ADMIN_AVAILABLE = "django.contrib.admin" in settings.INSTALLED_APPS
except Exception:
    admin = None
    ADMIN_AVAILABLE = False

urlpatterns = [
    # Health check pour Docker
    path("health/", health_check, name="health_check"),
    # Auth URLs (login, logout, password reset, etc.)
    path("accounts/", include("django.contrib.auth.urls")),
    # Convenience redirects
    path("login/", RedirectView.as_view(url="/accounts/login/", permanent=False)),
    path("logout/", RedirectView.as_view(url="/accounts/logout/", permanent=False)),
    # Portail professionnel
    path("pro/", include(("suivi_demande.urls_pro", "pro"), namespace="pro")),
    # Portail client
    path(
        "client/", include(("suivi_demande.urls_client", "client"), namespace="client")
    ),
    # URLs principales (minimal: redirections/entrees generiques)
    path("", include(("suivi_demande.urls", "suivi"), namespace="suivi")),
]

if ADMIN_AVAILABLE and admin is not None:
    urlpatterns.insert(0, path("admin/", admin.site.urls))

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
