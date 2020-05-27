from django.urls import path

from covid import views

app_name = 'covid'

urlpatterns = [
    path('', views.index, name='index'),
]
