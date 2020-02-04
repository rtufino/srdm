from django.shortcuts import redirect, render


def registro(request, hash):

    return render(request, 'tutoria/home.html')
