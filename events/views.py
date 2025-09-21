from django.http import HttpResponse
from events.forms import EventModelForm , CategoryForm , ParticipantForm
from django.contrib import messages
from datetime import date
from django.db.models import Q, Count, Max, Min, Avg
from events.models import Category , Event , RSVP
from django.shortcuts import render , redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test, login_required, permission_required
from users.views import is_admin


def is_organizer(user):
    return user.groups.filter(name='Organizer').exists()

def is_participant(user):
    return user.groups.filter(name='User').exists()


@permission_required('events.view_event' , login_url='no-permission')
def manager_dashboard(request):
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

    context = {
        "events": events,
        "counts": counts,
        "selected_type": type,
        "query": query,
        "start_date": start_date,
        "end_date": end_date,
        "today": date.today(),
        "is_admin": request.user.groups.filter(name="Admin").exists(),
        "is_organizer": request.user.groups.filter(name="Organizer").exists(),
        "is_participant": request.user.groups.filter(name="User").exists(),
    }
    return render(request, "dashboard/manager-dashboard.html", context)

@user_passes_test(is_participant, login_url='no-permission')
def user_dashboard(request):
    return render(request, "dashboard/user-dashboard.html")


@login_required
@permission_required("events.add_event", login_url='no-permission')
def create_event(request):
    categories = Category.objects.all()
    participants = User.objects.all()

    if request.method == "POST":
        event_form = EventModelForm(request.POST, request.FILES, categories=categories, participants=participants)
        if event_form.is_valid():
            event_form.save()
            messages.success(request, "Event Created Successfully")
            return redirect('manage-event')
    else:
        event_form = EventModelForm(categories=categories, participants=participants)

    return render(request, "event_form.html", {"event_form": event_form})
 

@login_required
@permission_required("events.change_event", login_url='no-permission')
def update_event(request, id):
    event = Event.objects.get(id=id)
    categories = Category.objects.all()
    participants = User.objects.all()
    event_form = EventModelForm(categories=categories, participants=participants, instance=event)

    if request.method == "POST":
        event_form = EventModelForm(request.POST,categories=categories,participants=participants,instance=event)

        if event_form.is_valid():
            event_form.save()
            messages.success(request, "Event Updated Successfully")
            return redirect('manage-event')

    context = {"event_form": event_form}
    return render(request, "event_form.html", context)


@login_required
@permission_required("events.delete_event", login_url='no-permission')
def delete_event(request, id):
    if request.method == 'POST':
        event = Event.objects.get(id=id)
        event.delete()
        return redirect('manage-event')
    else:
        messages.error(request, 'Something went wrong')
        return redirect('manage-event')


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


@login_required
@user_passes_test(is_organizer, login_url='no-permission')
def manage_event(request):
    events = Event.objects.all()
    return render(request, 'manage_event.html' , {'events': events})


@login_required
@user_passes_test(is_organizer, login_url='no-permission')
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

    return redirect("manager-dashboard")



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

    return redirect('manager-dashboard')
