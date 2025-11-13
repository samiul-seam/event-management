from django.urls import path
from events.views import Dashboard , CreateEvent , UpdateEvent , DeleteTask , manage_category , manage_event , delete_category , add_category , update_category , event_detail, rsvp_event , show_rsvp , remove_rsvp
from core.views import no_permission

urlpatterns = [
    path('dashboard/' , Dashboard.as_view(), name="dashboard" ),
    path('create-event/' , CreateEvent.as_view() , name="create-event"),
    path('update-event/<int:id>/', UpdateEvent.as_view(), name="update-event"),
    path('delete-event/<int:id>/', DeleteTask.as_view(), name="delete-event"),
    path('manage-event/', manage_event , name='manage-event'),
    path('manage-categories/', manage_category, name='manage-category'),
    path('add-category/', add_category, name='add-category'),
    path('update-category/<int:id>/', update_category, name='update-category'),
    path('delete-category/<int:id>/', delete_category, name='delete-category'),
    path('no-permission/', no_permission , name='no-permission'),
    path('event_detail/<int:id>/', event_detail , name='event_detail'),
    path('rsvp_event/<int:event_id>/' , rsvp_event , name='rsvp-event') ,
    path('show-rsvp/', show_rsvp , name='show-rsvp'),
    path("remove-rsvp/<int:id>/", remove_rsvp, name="remove-rsvp"),
]

