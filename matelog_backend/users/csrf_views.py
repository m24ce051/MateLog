from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
@csrf_exempt
def get_csrf_token(request):
    """
    Vista para obtener el token CSRF.
    CSRF deshabilitado temporalmente para debugging.
    """
    return JsonResponse({'csrfToken': 'csrf-disabled', 'detail': 'CSRF temporarily disabled'})