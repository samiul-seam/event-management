from django.http import HttpResponse
from events.forms import EventModelForm , CategoryForm , ParticipantForm
from django.contrib import messages
from datetime import date
from django.db.models import Q, Count
from events.models import Category , Event , RSVP
from django.shortcuts import render , redirect
from django.contrib.auth.decorators import user_passes_test, login_required, permission_required
from users.views import is_admin

from django.contrib.auth.mixins import LoginRequiredMixin , PermissionRequiredMixin
from django.views.generic import TemplateView, UpdateView
from django.views.generic import CreateView , DeleteView
from django.views.generic.base import ContextMixin , View
from django.urls import reverse_lazy

from django.contrib.auth import get_user_model
User = get_user_model()


def is_organizer(user):
    return user.groups.filter(name='Organizer').exists()

def is_participant(user):
    return user.groups.filter(name='User').exists()


# Updated to class-based view
class Dashboard(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'events.view_event'
    login_url = 'sign-in'
    template_name = 'dashboard/main-dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request

        type = request.GET.get('type', 'all')
        query = request.GET.get('q', '')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        counts = Event.objects.aggregate(
            total_events=Count('id'),
            upcoming=Count('id', filter=Q(date__gte=date.today())),
            past=Count('id', filter=Q(date__lt=date.today())),
            today=Count('id', filter=Q(date=date.today()))
        )

        base_query = Event.objects.select_related("category").prefetch_related("participants")

        if type == "today":
            base_query = base_query.filter(date=date.today())
        elif type == "upcoming":
            base_query = base_query.filter(date__gte=date.today())
        elif type == "past":
            base_query = base_query.filter(date__lt=date.today())

        if query:
            base_query = base_query.filter(
                Q(name__icontains=query) |
                Q(location__icontains=query) |
                Q(category__name__icontains=query)
            )

        if start_date and end_date:
            base_query = base_query.filter(date__range=[start_date, end_date])
        elif start_date:
            base_query = base_query.filter(date__gte=start_date)
        elif end_date:
            base_query = base_query.filter(date__lte=end_date)

        events = base_query.all()

        user_groups = set(request.user.groups.values_list('name', flat=True))

        context.update({
            "events": events,
            "counts": counts,
            "selected_type": type,
            "query": query,
            "start_date": start_date,
            "end_date": end_date,
            "today": date.today(),
            "is_admin": "Admin" in user_groups,
            "is_organizer": "Organizer" in user_groups,
            "is_participant": "User" in user_groups,
        })

        return context


# Updated to class-based view
class CreateEvent(ContextMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'events.add_event'
    login_url = 'sign-in'
    template_name = 'event_form.html'
    success_url = 'manage-event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event_form'] = kwargs.get('event_form', EventModelForm())
        context['categories'] = Category.objects.all()
        context['participants'] = User.objects.all()
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        event_form = EventModelForm(request.POST, request.FILES)

        if event_form.is_valid():
            event_form.save()
            messages.success(request, "Event Created Successfully")
            return redirect(self.success_url)

        context = self.get_context_data(event_form=event_form)
        return render(request, self.template_name, context)



# Updated to class-based view
class UpdateEvent(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required ='events.change_event'
    login_url = 'sign-in'
    model = Event
    form_class = EventModelForm
    template_name = 'event_form.html'
    context_object_name = 'event'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event_form"] = self.get_form()
        context['categories'] = Category.objects.all()
        context['participants'] = User.objects.all()

        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        event_form = EventModelForm(request.POST, request.FILES, instance=self.object)

        if event_form.is_valid():
            event_form.save()
            messages.success(request, "Event Updated Successfully")
            return redirect('manage-event')



# Updated to class-based view
class DeleteEvent(LoginRequiredMixin, PermissionRequiredMixin , DeleteView):
    permission_required = 'events.delete_event'
    login_url = 'sign-in'
    model = Event
    success_url = reverse_lazy('dashboard') 
    pk_url_kwarg = 'id'

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Event Deleted Successfully')
        return super().delete(request, *args, **kwargs)


@login_required
@permission_required("events.add_category", login_url='no-permission')
def add_category(request):
    form = CategoryForm()

    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Category created successfully!")
                return redirect('manage-category')
            except:
                messages.error(request, "This category already exists.")
        else:
            messages.error(request, "Invalid input. Please try again.")

    return render(request, "category_form.html", {"categoryform": form})


def manage_event(request):
    events = Event.objects.all()
    return render(request, 'manage_event.html' , {'events': events})


def manage_category(request):
    categories = Category.objects.all()
    form = CategoryForm()

    return render(request, 'manage_category.html', {
        'categories': categories,
        'category_form': form,
    })


@login_required
@permission_required("events.delete_category", login_url='no-permission')
def delete_category(request, id):
    if request.method == 'POST':
       category = Category.objects.get(id=id)
       category.delete()
       return redirect('manage-category')
    else:
        messages.error(request, 'Something went wrong')
        return redirect('manage-category')
   

@login_required
@permission_required("events.change_category", login_url='no-permission')
def update_category(request, id):
    category = Category.objects.get(id=id)
    category_form = CategoryForm(instance=category)

    if request.method == "POST":
        category_form = CategoryForm(request.POST, instance=category)
        if category_form.is_valid():
            category_form.save()
            messages.success(request, "Category Updated Successfully")
            return redirect('manage-category')

    context = {"category_form": category_form}
    return render(request, "category_form.html", context)



@login_required
def event_detail(request, id):
    try:
        event = Event.objects.get(id=id)
    except Event.DoesNotExist:
        return HttpResponse("Event not found.")

    participants = event.participants.all()

    context = {
        "event": event,
        "participants": participants
    }

    return render(request, "details.html", context)


@login_required
@permission_required('events.view_event', login_url='no-permission')
def rsvp_event(request, event_id):
    if request.method == "POST":
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return HttpResponse("Event not found.")

        rsvp, created = RSVP.objects.get_or_create(event=event, user=request.user)

        if created:
            messages.success(request, f"You have successfully RSVP'd for {event.name}.")
        else:
            messages.info(request, f"You already RSVP'd for {event.name}.")

    return redirect("dashboard")



@login_required
def show_rsvp(request):
    events = request.user.events.all() 
    context = {
        'events': events
    }
    return render(request, 'show_rsvp.html', context)

@login_required
def remove_rsvp(request, id):
    if request.method == "POST":
        try:
            event = Event.objects.get(id=id)
            rsvp = RSVP.objects.get(event=event, user=request.user)
            rsvp.delete()
            event.participants.remove(request.user)  # keep sync
            messages.success(request, "You have removed your RSVP from this event.")
        except (Event.DoesNotExist, RSVP.DoesNotExist):
            messages.error(request, "Something went wrong.")
    else:
        messages.error(request, "Invalid request method.")

    return redirect('dashboard')
