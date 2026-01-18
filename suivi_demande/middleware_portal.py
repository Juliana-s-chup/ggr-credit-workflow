"""
Middleware de contrÃ´le d'accÃ¨s par portail
EmpÃªche les clients d'accÃ©der au portail pro et vice-versa
"""

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponseForbidden

from .models import UserRoles


class PortalAccessMiddleware:
    """
    Middleware qui contrÃ´le l'accÃ¨s selon le type de portail et le rÃ´le utilisateur.

    RÃ¨gles :
    - Portail CLIENT : Seuls les utilisateurs avec rÃ´le CLIENT
    - Portail PRO : Tous les rÃ´les sauf CLIENT
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.portal_type = getattr(settings, "PORTAL_TYPE", None)
        self.allowed_roles = getattr(settings, "ALLOWED_ROLES", [])

    def __call__(self, request):
        # Ignorer pour statiques, mÃ©dias et endpoints d'auth
        if request.path.startswith(
            ("/static/", "/media/", "/accounts/login/", "/accounts/logout/", "/login/", "/logout/")
        ):
            return self.get_response(request)

        # DÃ©terminer le type de portail en fonction du host ou du chemin
        host = request.get_host().split(":")[0]
        path = request.path
        inferred_portal = None
        if "pro." in host or path.startswith("/pro/"):
            inferred_portal = "PRO"
        elif "client." in host or path.startswith("/client/"):
            inferred_portal = "CLIENT"

        # VÃ©rifier uniquement pour les utilisateurs authentifiÃ©s et si portail dÃ©duit
        if inferred_portal and request.user.is_authenticated:
            profile = getattr(request.user, "profile", None)
            user_role = getattr(profile, "role", None)

            if inferred_portal == "CLIENT":
                role_autorise = user_role == UserRoles.CLIENT
            else:  # PRO
                role_autorise = user_role != UserRoles.CLIENT

            if not role_autorise:
                messages.error(
                    request, "AccÃ¨s refusÃ©: votre rÃ´le n'est pas autorisÃ© sur ce portail."
                )
                # Option: dÃ©connexion douce
                try:
                    from django.contrib.auth import logout

                    logout(request)
                except Exception:
                    pass

                # Si on peut dÃ©duire l'autre portail, rediriger vers sa page de login locale
                if inferred_portal == "CLIENT":
                    # Utilisateur pro tentant le portail client
                    return HttpResponseForbidden("AccÃ¨s refusÃ© au portail client pour ce rÃ´le.")
                else:
                    # Utilisateur client tentant le portail pro
                    return HttpResponseForbidden(
                        "AccÃ¨s refusÃ© au portail professionnel pour ce rÃ´le."
                    )

        return self.get_response(request)


class PortalRedirectMiddleware:
    """
    Middleware qui redirige automatiquement vers le bon portail
    selon le domaine d'accÃ¨s initial
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # DÃ©tecter le sous-domaine
        host = request.get_host().split(":")[0]  # Enlever le port si prÃ©sent

        # Si accÃ¨s depuis le domaine principal, rediriger vers page de choix
        if host in ["ggr-credit.cg", "www.ggr-credit.cg", "localhost", "127.0.0.1"]:
            if request.path == "/" and not request.user.is_authenticated:
                # Afficher la page de choix de portail
                pass  # Laisser passer, c'est la home_landing.html

        response = self.get_response(request)
        return response
