from django.shortcuts import render


def index(request):
    """
    messages.info(request,
                  "This platform is under development! It may contain bugs and not all features are functional. If "
                  "some pages are not showing correctly, please switch to a newer browser, like Google Chrome.")
    """

    return render(request, 'covid/index.html')


