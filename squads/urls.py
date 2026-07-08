from django.urls import path
from . import views

urlpatterns = [
    path('', views.squad_list, name='squad_list'),
    path('create/', views.create_squad, name='create_squad'),
    path('<int:squad_id>/', views.squad_detail, name='squad_detail'),

    path(
        '<int:squad_id>/invite/',
        views.generate_invite,
        name='generate_invite'
    ),

path("join/<uuid:token>/", views.join_squad, name="join_squad")
]