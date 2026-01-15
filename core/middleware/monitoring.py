"""
Middleware de Monitoring
Mesure les performances et log les requêtes
"""
import time
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Mesure le temps de réponse de chaque requête
    """
    
    def process_request(self, request):
        request._start_time = time.time()
        return None
    
    def process_response(self, request, response):
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            
            # Log si la requête est lente (> 1s)
            if duration > 1.0:
                logger.warning(
                    f"Slow request: {request.method} {request.path}",
                    extra={
                        'duration': duration,
                        'method': request.method,
                        'path': request.path,
                        'status_code': response.status_code,
                        'user_id': request.user.id if request.user.is_authenticated else None,
                    }
                )
            
            # Ajouter header de performance
            response['X-Response-Time'] = f"{duration:.3f}s"
        
        return response


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Log toutes les requêtes avec contexte
    """
    
    def process_request(self, request):
        logger.info(
            f"Request: {request.method} {request.path}",
            extra={
                'method': request.method,
                'path': request.path,
                'user_id': request.user.id if request.user.is_authenticated else None,
                'ip': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            }
        )
        return None
    
    @staticmethod
    def get_client_ip(request):
        """Récupère l'IP réelle du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
