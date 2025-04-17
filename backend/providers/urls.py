from django.urls import path
from .views import providers_list

urlpatterns = [
    path('', providers_list, name='providers-list'),
]
