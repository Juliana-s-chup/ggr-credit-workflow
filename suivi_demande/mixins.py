"""
Mixins rÃ©utilisables pour les vues avec gestion d'erreurs.
"""

from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import Http404
from django.core.exceptions import PermissionDenied
import logging

logger = logging.getLogger(__name__)


class SafeObjectMixin:
    """
    Mixin pour rÃ©cupÃ©rer des objets de maniÃ¨re sÃ©curisÃ©e.
    Remplace les .get() dangereux par get_object_or_404().
    """

    def get_object_safe(self, model, **kwargs):
        """
        RÃ©cupÃ¨re un objet de maniÃ¨re sÃ©curisÃ©e.

        Args:
            model: ModÃ¨le Django
            **kwargs: Filtres (ex: id=1, reference='DOS-001')

        Returns:
            Instance du modÃ¨le ou 404

        Example:
            dossier = self.get_object_safe(DossierCredit, id=dossier_id)
        """
        try:
            return get_object_or_404(model, **kwargs)
        except Http404:
            logger.warning(f"Objet {model.__name__} non trouvÃ©: {kwargs}")
            raise

    def get_object_or_none(self, model, **kwargs):
        """
        RÃ©cupÃ¨re un objet ou retourne None (pas d'erreur).

        Args:
            model: ModÃ¨le Django
            **kwargs: Filtres

        Returns:
            Instance du modÃ¨le ou None

        Example:
            dossier = self.get_object_or_none(DossierCredit, id=dossier_id)
            if dossier is None:
                messages.error(request, "Dossier introuvable")
        """
        try:
            return model.objects.get(**kwargs)
        except model.DoesNotExist:
            logger.info(f"Objet {model.__name__} non trouvÃ©: {kwargs}")
            return None
        except Exception as e:
            logger.error(f"Erreur get_object_or_none: {e}")
            return None


class ErrorHandlingMixin:
    """
    Mixin pour gÃ©rer les erreurs de maniÃ¨re uniforme.
    """

    def handle_error(self, request, error, user_message="Une erreur est survenue"):
        """
        GÃ¨re une erreur de maniÃ¨re uniforme.

        Args:
            request: RequÃªte Django
            error: Exception
            user_message: Message Ã  afficher Ã  l'utilisateur
        """
        # Logger l'erreur technique
        logger.error(f"Erreur dans {self.__class__.__name__}: {error}", exc_info=True)

        # Afficher un message user-friendly
        messages.error(request, user_message)

    def handle_permission_denied(self, request, message="Vous n'avez pas les droits nÃ©cessaires"):
        """
        GÃ¨re un refus de permission.

        Args:
            request: RequÃªte Django
            message: Message Ã  afficher
        """
        logger.warning(f"Permission refusÃ©e pour {request.user}: {message}")
        messages.error(request, message)
        raise PermissionDenied(message)


class ValidationMixin:
    """
    Mixin pour valider les donnÃ©es de maniÃ¨re sÃ©curisÃ©e.
    """

    def validate_positive_number(self, value, field_name="valeur"):
        """
        Valide qu'un nombre est positif.

        Args:
            value: Valeur Ã  valider
            field_name: Nom du champ (pour le message d'erreur)

        Returns:
            True si valide

        Raises:
            ValueError si invalide
        """
        try:
            num = float(value)
            if num <= 0:
                raise ValueError(f"{field_name} doit Ãªtre positif")
            return True
        except (TypeError, ValueError) as e:
            logger.warning(f"Validation Ã©chouÃ©e pour {field_name}: {e}")
            raise ValueError(f"{field_name} invalide")

    def validate_required_fields(self, data, required_fields):
        """
        Valide que tous les champs requis sont prÃ©sents.

        Args:
            data: Dictionnaire de donnÃ©es (ex: request.POST)
            required_fields: Liste des champs requis

        Returns:
            True si tous prÃ©sents

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
            # âœ… RÃ©cupÃ©ration sÃ©curisÃ©e
            dossier = self.get_object_safe(DossierCredit, id=dossier_id)

            # âœ… Validation
            self.validate_positive_number(dossier.montant, "montant")

            # Logique mÃ©tier...

        except Http404:
            messages.error(request, "Dossier introuvable")
            return redirect("dashboard")
        except ValueError as e:
            self.handle_error(request, e, str(e))
            return redirect("dashboard")
        except Exception as e:
            self.handle_error(request, e, "Erreur lors du chargement du dossier")
            return redirect("dashboard")
