from django.urls import path
from events.views import manager_dashboard , user_dashboard , create_event , update_event , delete_event , add_participant

urlpatterns = [
    path('manager-dashboard/' , manager_dashboard, name="manager-dashboard" ),
    path('user-dashboard/', user_dashboard , name="user-dashboard"), 
    path('create-event/' , create_event , name="create-event"),
    path('update-event/<int:id>/', update_event, name="update-event"),
    path('delete-event/<int:id>/', delete_event, name="delete-event"),
    path('add-participant/', add_participant, name='add-participant')
]
