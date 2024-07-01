from django.shortcuts import redirect
from functools import wraps

def usuario_de_tipo(*tipos):
    """
    Decorador para verificar si el usuario tiene uno de los tipos especificados.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('/accounts/login/')
            if request.user.tipo_usuario.nom_tipo not in tipos:
                return redirect('index')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator