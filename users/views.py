from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, logout
from users.forms import CustomRegistrationForm , CreateGroupForm , AssignRoleForm , EditProfileForm , CustomPasswordChangeForm , CustomPasswordResetConfirmForm , CustomPasswordResetForm
from django.contrib import messages
from django.contrib import messages
from users.forms import LoginForm
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required, user_passes_test

from django.contrib.auth.views import LoginView
from django.views.generic.edit import CreateView , FormView
from django.urls import reverse_lazy
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin , PermissionRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your views here.
def is_admin(user):
    return user.groups.filter(name='Admin').exists()

# Updated to class-based view
class SignUp(CreateView):
    form_class = CustomRegistrationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('sign-in')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data.get('password1'))
        user.is_active = False
        user.save()
        messages.success(self.request, 'A Confirmation mail sent. Please check your email')
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        print("form is not found")
        response = super().form_invalid(form)
    
    

class SignIn(LoginView):
    form_class = LoginForm

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        return next_url if next_url else super().get_success_url()



# Updated to class-based view
class ActiveUser(View):

    def get(self , request , token , user_id , *args, **kwargs):
        try:
            user = User.objects.get(pk=user_id)
            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                return redirect('sign-in')
            else:
                return HttpResponse('Invalid ID or Token')

        except User.DoesNotExist:
            return HttpResponse('This user does not exist')


# Updated to class-based view
class AdminDashboard(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'auth.add_group'
    login_url = 'sign-in'
    template_name = 'admin/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        users = User.objects.prefetch_related(Prefetch('groups', queryset=Group.objects.all(), to_attr='all_groups')).all()

        for user in users:
            if user.all_groups:
                user.group_name = user.all_groups[0].name
            else:
                user.group_name = 'No Group Assigned'

        context['users'] = users
        return context



# Updated to class-based view
class GroupList(LoginRequiredMixin, PermissionRequiredMixin , TemplateView ,View):
    permission_required = 'auth.view_group'
    login_url = 'sign-in'
    template_name = 'admin/group_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["groups"] = Group.objects.prefetch_related('permissions').all()
        return context
    


# Updated to class-based view
class CreateGroup(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'auth.add_group'
    login_url = 'sign-in'
    template_name = 'admin/create_group.html'

    def get_context_data(self, **kwargs):
        context = {}
        context["form"] = kwargs.get('form' , CreateGroupForm)
        return context
    
    def get(self, request , *args, **kwargs):
        context = self.get_context_data()
        return render(request , self.template_name , context)
    
    def post(self , request , *args, **kwargs):
        form = CreateGroupForm()
        if request.method == 'POST':
            form = CreateGroupForm(request.POST)
            if form.is_valid():
                group = form.save()
                messages.success(request, f"Group {group.name} has been created successfully")
                return redirect('create-group')
            else:
                context = self.get_context_data(form=form)
                return render(request, self.template_name, context)
    


@user_passes_test(is_admin, login_url='no-permission')
def delete_group(request, group_id):
    if request.method == 'POST':
        try:
            group = Group.objects.get(id=group_id)
            group_name = group.name
            group.delete()
            messages.success(request, f"Group '{group_name}' has been deleted successfully")
        except Group.DoesNotExist:
            messages.error(request, "Group not found!")
        
        return redirect('group-list')
    


@user_passes_test(is_admin, login_url='no-permission')
def assign_role(request, user_id):
    user = User.objects.get(id=user_id)
    form = AssignRoleForm()

    if request.method == 'POST':
        form = AssignRoleForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get('role')
            user.groups.clear()
            user.groups.add(role)
            messages.success(request, f"User {user.username} has been assigned to the {role.name} role")
            return redirect('admin-dashboard')

    return render(request, 'admin/assign_role.html', {"form": form})



class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        user_groups = set(self.request.user.groups.values_list('name', flat=True))

        context['username'] = user.username
        context['email'] = user.email
        context['name'] = user.get_full_name()
        context['profile_image'] = user.profile_image
        context['number'] = user.number
        context['member_since'] = user.date_joined
        context['last_login'] = user.last_login
        context['is_admin'] = "Admin" in user_groups
        context['is_organizer'] = "Organizer" in user_groups
        context['is_Participant'] = "Participant" in user_groups
        return context



class EditProfileView(UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'accounts/update_profile.html'
    context_object_name = 'form'

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        form.save()
        return redirect('profile')
    

class changePassword(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    form_class = CustomPasswordChangeForm



class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'registration/reset_password.html'
    success_url = reverse_lazy('sign-in')
    html_email_template_name = 'registration/reset_email.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['protocol'] = 'https' if self.request.is_secure() else 'http'
        context['domain'] = self.request.get_host()
        print(context)
        return context

    def form_valid(self, form):
        messages.success(
            self.request, 'A Reset email sent. Please check your email')
        return super().form_valid(form)
    

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomPasswordResetConfirmForm
    template_name = 'registration/reset_password.html'
    success_url = reverse_lazy('sign-in')

    def form_valid(self, form):
        messages.success(
            self.request, 'Password reset successfully')
        return super().form_valid(form)

