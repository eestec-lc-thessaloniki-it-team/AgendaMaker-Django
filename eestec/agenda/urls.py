from django.urls import path

from . import views

app_name="agenda"
urlpatterns = [

    path('create-agenda/', views.create_agenda, name='create-agenda'),

    path('create-section/', views.createSection, name='create-section'),

    path('create-topic/', views.createTopic, name='create-topic'),

    path('<int:agenda_id>/', views.getAgendaByID, name='get-agenda-id'),

    path('update-agenda/', views.updateAgenda, name="update-agenda"),
    path('update-section/', views.updateSection, name="update-section"),
    path('update-topic/', views.updateTopic, name="update-topic"),

    path('delete-agenda/', views.deleteAgenda, name="delete-agenda"),
    path('delete-section/', views.deleteSection, name="update-section"),
    path('delete-topic/', views.deleteTopic, name="delete-topic"),
]
