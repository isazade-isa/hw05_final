# core/views.py
from http.client import FORBIDDEN, INTERNAL_SERVER_ERROR, NOT_FOUND
from django.shortcuts import render


def page_not_found(request, exception):
    return render(
        request, 'core/404.html',
        {'path': request.path},
        status=NOT_FOUND
    )


def permission_denied(request, exception):
    return render(request, 'core/403csrf.html', status=FORBIDDEN)


def server_error(request):
    return render(request, 'core/500.html', status=INTERNAL_SERVER_ERROR)
