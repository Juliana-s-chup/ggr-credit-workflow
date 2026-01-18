"""
Validators pour la securite des uploads et des donnees.
"""

import os
from typing import Tuple
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile

# Import optionnel de python-magic
try:
    import magic

    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False


# Taille maximale des fichiers (10 MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

# Types MIME autorises
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/jpg",
    "image/png",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

# Extensions autorisees
ALLOWED_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".doc",
    ".docx",
}


def validate_file_upload(uploaded_file: UploadedFile) -> Tuple[bool, str]:
    """
    Valide un fichier uploade (taille, type MIME, extension).

    Args:
        uploaded_file: Fichier Django UploadedFile

    Returns:
        Tuple[bool, str]: (is_valid, error_message)

    Raises:
        ValidationError: Si le fichier est invalide

    Examples:
        >>> is_valid, error = validate_file_upload(request.FILES['fichier'])
        >>> if not is_valid:
        ...     messages.error(request, error)
    """
    # Verifier la taille
    if uploaded_file.size > MAX_FILE_SIZE:
        return (
            False,
            f"Fichier trop volumineux ({uploaded_file.size / 1024 / 1024:.1f} MB). Maximum: 10 MB",
        )

    # Verifier l'extension
    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return (
            False,
            f"Extension '{file_ext}' non autorisee. Extensions acceptees: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Verifier le type MIME (protection contre renommage malveillant)
    try:
        # Lire les premiers octets pour detecter le vrai type
        file_content = uploaded_file.read(2048)
        uploaded_file.seek(0)  # Remettre le curseur au debut

        # Utiliser python-magic si disponible, sinon fallback sur content_type
        if MAGIC_AVAILABLE:
            try:
                mime_type = magic.from_buffer(file_content, mime=True)
            except Exception:
                # Fallback si magic echoue
                mime_type = uploaded_file.content_type
        else:
            # Fallback: utiliser le content_type declare
            mime_type = uploaded_file.content_type

        if mime_type not in ALLOWED_MIME_TYPES:
            return (
                False,
                f"Type de fichier '{mime_type}' non autorise. Types acceptes: PDF, JPG, PNG, DOC, DOCX",
            )

    except Exception as e:
        return False, f"Erreur lors de la validation du fichier: {str(e)}"

    return True, ""


def validate_file_upload_strict(uploaded_file: UploadedFile) -> None:
    """
    Version stricte qui leve une ValidationError.

    Args:
        uploaded_file: Fichier Django UploadedFile

    Raises:
        ValidationError: Si le fichier est invalide
    """
    is_valid, error_message = validate_file_upload(uploaded_file)
    if not is_valid:
        raise ValidationError(error_message)


def sanitize_filename(filename: str) -> str:
    """
    Nettoie un nom de fichier pour eviter les injections.

    Args:
        filename: Nom de fichier original

    Returns:
        str: Nom de fichier securise

    Examples:
        >>> sanitize_filename("../../etc/passwd.txt")
        'passwd.txt'
        >>> sanitize_filename("mon fichier (1).pdf")
        'mon_fichier_1.pdf'
    """
    # Supprimer les chemins
    filename = os.path.basename(filename)

    # Remplacer les caracteres dangereux
    dangerous_chars = ["/", "\\", "..", "<", ">", ":", '"', "|", "?", "*"]
    for char in dangerous_chars:
        filename = filename.replace(char, "_")

    # Limiter la longueur
    name, ext = os.path.splitext(filename)
    if len(name) > 100:
        name = name[:100]

    return f"{name}{ext}"


def validate_comment_length(comment: str, max_length: int = 1000) -> Tuple[bool, str]:
    """
    Valide la longueur d'un commentaire.

    Args:
        comment: Texte du commentaire
        max_length: Longueur maximale autorisee

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not comment or not comment.strip():
        return False, "Le commentaire ne peut pas etre vide"

    if len(comment) > max_length:
        return (
            False,
            f"Commentaire trop long ({len(comment)} caracteres). Maximum: {max_length}",
        )

    return True, ""
