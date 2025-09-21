from django.urls import path
from events.views import manager_dashboard , user_dashboard , create_event , update_event , delete_event , manage_category , manage_event , delete_category , add_category , update_category , event_detail, rsvp_event , show_rsvp , remove_rsvp
from core.views import no_permission

urlpatterns = [
    path('manager-dashboard/' , manager_dashboard, name="manager-dashboard" ),
    path('user-dashboard/', user_dashboard , name="user-dashboard"), 
    path('create-event/' , create_event , name="create-event"),
    path('update-event/<int:id>/', update_event, name="update-event"),
    path('delete-event/<int:id>/', delete_event, name="delete-event"),
    path('manage-event/', manage_event , name='manage-event'),
    path('manage-categories/', manage_category, name='manage-category'),
    path('add-category/', add_category, name='add-category'),
    path('update-category/<int:id>/', update_category, name='update-category'),
    path('delete-category/<int:id>/', delete_category, name='delete-category'),
    path('no-permission/', no_permission , name='no-permission'),
    path('event_detail/<int:id>/', event_detail , name='event_detail'),
    path('rsvp_event/<int:event_id>/' , rsvp_event , name='rsvp-event') ,
    path('show-rsvp/', show_rsvp , name='show-rsvp'),
    path("remove-rsvp/<int:id>/", remove_rsvp, name="remove-rsvp")
]
