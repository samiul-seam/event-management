from django.urls import path
from users.views import SignUp, SignIn, ActiveUser,AdminDashboard , GroupList , CreateGroup , assign_role , delete_group , ProfileView , EditProfileView , changePassword , CustomPasswordResetView , CustomPasswordResetConfirmView
from django.contrib.auth.views import LogoutView , PasswordChangeDoneView


urlpatterns = [
    path('sign-up/', SignUp.as_view() , name='sign-up'),
    path('sign-in/', SignIn.as_view() , name='sign-in'),
    path('sign-out/', LogoutView.as_view(), name='logout'),
    path('activate/<int:user_id>/<str:token>/', ActiveUser.as_view() , name='active_user'),
    path('admin/admin-dashboard/', AdminDashboard.as_view() , name='admin-dashboard'),
    path('admin/group-list/', GroupList.as_view() , name='group-list'),
    path('admin/create-group/', CreateGroup.as_view(), name='create-group'),
    path('admin/<int:user_id>/assign-role/', assign_role, name='assign-role'),
    path('delete-group/<int:group_id>/', delete_group, name='delete-group'),
    path('profile/' , ProfileView.as_view(), name='profile'),
    path('edit-profile/' , EditProfileView.as_view(), name='edit_profile'),
    path('change-password' , changePassword.as_view() , name='password_change'),
    path('password-change/done/', PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]

