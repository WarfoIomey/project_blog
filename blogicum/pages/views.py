from django.shortcuts import render


def about(request):
    """О проекте"""
    template = 'pages/about.html'
    return render(request, template)


def rules(request):
    """Правила"""
    template = 'pages/rules.html'
    return render(request, template)


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


def failure_server(request):
    return render(request, 'pages/500.html', status=500)
