from django.shortcuts import render , redirect
from django.http import HttpResponse
from events.forms import EventModelForm , ParticipantForm
from django.contrib import messages
from datetime import date
from django.db.models import Q, Count, Max, Min, Avg
from events.models import Category , Participant , Event

def start(request):
    return render(request, 'start.html')

def manager_dashboard(request):
    type = request.GET.get('type', 'all')
    query = request.GET.get('q', '')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    counts = Event.objects.aggregate(
        total=Count('id'),
        upcoming=Count('id', filter=Q(date__gte=date.today())),
        past=Count('id', filter=Q(date__lt=date.today())),
        participants=Count('included_in', distinct=True)
    )

    base_query = Event.objects.select_related("category").prefetch_related("included_in")

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
    }
    return render(request, "dashboard/manager-dashboard.html", context)

def user_dashboard(request):
    type = request.GET.get('type', 'all')
    query = request.GET.get('q', '')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    counts = Event.objects.aggregate(
        total=Count('id'),
        upcoming=Count('id', filter=Q(date__gte=date.today())),
        past=Count('id', filter=Q(date__lt=date.today())),
        participants=Count('included_in', distinct=True)
    )

    base_query = Event.objects.select_related("category").prefetch_related("included_in")

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
    }
    return render(request, "dashboard/user-dashboard.html" , context)

def create_event(request):
    categories = Category.objects.all()
    participants = Participant.objects.all()
    event_form = EventModelForm(categories=categories, participants=participants)

    if request.method == "POST":
        event_form = EventModelForm(request.POST, categories=categories, participants=participants)
        if event_form.is_valid():
            event_form.save()
            messages.success(request, "Event Created Successfully")
            return redirect('create-event')
        
    context = {"event_form": event_form}
    return render(request, "event_form.html", context)
 
def update_event(request, id):
    event = Event.objects.get(id=id)
    categories = Category.objects.all()
    participants = Participant.objects.all()
    event_form = EventModelForm(categories=categories, participants=participants, instance=event)

    if request.method == "POST":
        event_form = EventModelForm(request.POST,categories=categories,participants=participants,instance=event)

        if event_form.is_valid():
            event_form.save()
            messages.success(request, "Event Updated Successfully")
            return redirect('update-event', id)

    context = {"event_form": event_form}
    return render(request, "event_form.html", context)

def delete_event(request, id):
    if request.method == 'POST':
        event = Event.objects.get(id=id)
        event.delete()
        return redirect('manager-dashboard')
    else:
        messages.error(request, 'Something went wrong')
        return redirect('manager-dashboard')

def add_participant(request):
    form = ParticipantForm()

    if request.method == "POST":
        form = ParticipantForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "participant created Successfully")
            return redirect('add-participant') 
        
    return render(request, "add_participant.html", {
        "participant_form": form
    })