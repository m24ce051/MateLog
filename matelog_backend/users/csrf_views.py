from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
@ensure_csrf_cookie
def get_csrf_token(request):
    """
    Vista para obtener el token CSRF.
    El decorador ensure_csrf_cookie asegura que se envíe la cookie.
    """
    return JsonResponse({'detail': 'CSRF cookie set'})
