"""
Mixins reutilisables pour les vues avec gestion d'erreurs.
"""

from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import Http404
from django.core.exceptions import PermissionDenied
import logging

logger = logging.getLogger(__name__)


class SafeObjectMixin:
    """
    Mixin pour recuperer des objets de maniere securisee.
    Remplace les .get() dangereux par get_object_or_404().
    """

    def get_object_safe(self, model, **kwargs):
        """
        Recupere un objet de maniere securisee.

        Args:
            model: Modele Django
            **kwargs: Filtres (ex: id=1, reference='DOS-001')

        Returns:
            Instance du modele ou 404

        Example:
            dossier = self.get_object_safe(DossierCredit, id=dossier_id)
        """
        try:
            return get_object_or_404(model, **kwargs)
        except Http404:
            logger.warning(f"Objet {model.__name__} non trouve: {kwargs}")
            raise

    def get_object_or_none(self, model, **kwargs):
        """
        Recupere un objet ou retourne None (pas d'erreur).

        Args:
            model: Modele Django
            **kwargs: Filtres

        Returns:
            Instance du modele ou None

        Example:
            dossier = self.get_object_or_none(DossierCredit, id=dossier_id)
            if dossier is None:
                messages.error(request, "Dossier introuvable")
        """
        try:
            return model.objects.get(**kwargs)
        except model.DoesNotExist:
            logger.info(f"Objet {model.__name__} non trouve: {kwargs}")
            return None
        except Exception as e:
            logger.error(f"Erreur get_object_or_none: {e}")
            return None


class ErrorHandlingMixin:
    """
    Mixin pour gerer les erreurs de maniere uniforme.
    """

    def handle_error(self, request, error, user_message="Une erreur est survenue"):
        """
        Gere une erreur de maniere uniforme.

        Args:
            request: Requete Django
            error: Exception
            user_message: Message e  afficher e  l'utilisateur
        """
        # Logger l'erreur technique
        logger.error(f"Erreur dans {self.__class__.__name__}: {error}", exc_info=True)

        # Afficher un message user-friendly
        messages.error(request, user_message)

    def handle_permission_denied(self, request, message="Vous n'avez pas les droits necessaires"):
        """
        Gere un refus de permission.

        Args:
            request: Requete Django
            message: Message e  afficher
        """
        logger.warning(f"Permission refusee pour {request.user}: {message}")
        messages.error(request, message)
        raise PermissionDenied(message)


class ValidationMixin:
    """
    Mixin pour valider les donnees de maniere securisee.
    """

    def validate_positive_number(self, value, field_name="valeur"):
        """
        Valide qu'un nombre est positif.

        Args:
            value: Valeur e  valider
            field_name: Nom du champ (pour le message d'erreur)

        Returns:
            True si valide

        Raises:
            ValueError si invalide
        """
        try:
            num = float(value)
            if num <= 0:
                raise ValueError(f"{field_name} doit etre positif")
            return True
        except (TypeError, ValueError) as e:
            logger.warning(f"Validation echouee pour {field_name}: {e}")
            raise ValueError(f"{field_name} invalide")

    def validate_required_fields(self, data, required_fields):
        """
        Valide que tous les champs requis sont presents.

        Args:
            data: Dictionnaire de donnees (ex: request.POST)
            required_fields: Liste des champs requis

        Returns:
            True si tous presents

        Raises:
            ValueError si champ manquant
        """
        missing = [field for field in required_fields if not data.get(field)]
        if missing:
            raise ValueError(f"Champs manquants: {', '.join(missing)}")
        return True


# Exemple d'utilisation dans une vue
class ExampleView(SafeObjectMixin, ErrorHandlingMixin, ValidationMixin):
    """
    Exemple d'utilisation des mixins.
    """

    def get(self, request, dossier_id):
        try:
            # âœ… Recuperation securisee
            dossier = self.get_object_safe(DossierCredit, id=dossier_id)

            # âœ… Validation
            self.validate_positive_number(dossier.montant, "montant")

            # Logique metier...

        except Http404:
            messages.error(request, "Dossier introuvable")
            return redirect("dashboard")
        except ValueError as e:
            self.handle_error(request, e, str(e))
            return redirect("dashboard")
        except Exception as e:
            self.handle_error(request, e, "Erreur lors du chargement du dossier")
            return redirect("dashboard")
