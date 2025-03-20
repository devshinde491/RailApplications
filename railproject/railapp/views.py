# views.py
import datetime
import random
from datetime import datetime, timedelta

from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse
from django.utils.timezone import now
from django.db import OperationalError
from .models import Train, Station, Booking, Passenger, UserProfile, Payment, TrainClass, TrainClassAvailability
from .forms import UserRegistrationForm, BookingForm, LoginForm

def home(request):
    return render(request, 'home.html')

def base(request):
    return render(request, 'base.html')

def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('home')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.success(request, "Logout successful!")
    return redirect('home')



# views.py
def search_trains(request):
    trains = None
    today=now().date()
    if request.method == 'POST':
        source = request.POST.get('source')
        destination = request.POST.get('destination')
        date_str = request.POST.get('date_of_journey')
        train_type = request.POST.get('train_type', 'ALL')

        # Extract station names (ignoring city in parentheses)
        source_name = source.split(' (')[0]
        destination_name = destination.split(' (')[0]

        # Convert date string to datetime.date object
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            messages.error(request, "Invalid date format. Please select a valid date.")
            return render(request, 'search_trains.html', {'trains': None})

        # Filter trains based on source, destination
        trains = Train.objects.filter(
            source__name=source_name,
            destination__name=destination_name,
        )

        # Filter by train type if specified
        if train_type != 'ALL':
            trains = trains.filter(train_type=train_type)

        # Fetch availability for each train on the specific date
        for train in trains:
            train.availabilities = TrainClassAvailability.objects.filter(
                train=train,
                date=date
            )
            # Calculate duration
            departure = datetime.combine(date, train.departure_time)
            arrival = datetime.combine(date, train.arrival_time)
            if arrival < departure:
                arrival += timedelta(days=1)  # Handle overnight trains
            duration = arrival - departure
            hours, remainder = divmod(duration.seconds, 3600)
            minutes = remainder // 60
            train.duration = f"{hours}h {minutes}m"

    return render(request, 'search_trains.html', {'trains': trains})

# Remove the train_list view since it's no longer needed
# def train_list(request):
#     ... (remove this function)
def station_suggestions(request):
    query = request.GET.get("q", "").strip()
    suggestions = []

    if query:
        stations = Station.objects.filter(
            Q(name__icontains=query) | Q(city__icontains=query)
        )[:10]
        # Return station name with city for better user experience
        suggestions = [{"id": s.id, "name": f"{s.name} ({s.city})"} for s in stations]

    return JsonResponse({"stations": suggestions})



def pnr_status(request):
    pnr = request.GET.get('pnr', '').strip()
    booking = None

    if pnr:
        try:
            booking = Booking.objects.get(pnr=pnr)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # AJAX check
                return JsonResponse({
                    'status': booking.status,
                    'train': booking.train.name,
                    'departure': booking.train.departure_time.strftime("%Y-%m-%d %H:%M"),
                    'seats': booking.num_passengers,
                })
        except Booking.DoesNotExist:
            messages.error(request, "PNR not found.")
            return render(request, 'pnr_status.html', {'booking': None, 'pnr': pnr})

    return render(request, 'pnr_status.html', {'booking': booking, 'pnr': pnr})

@login_required
def book_ticket(request, train_id, ticket_class_id):
    train = get_object_or_404(Train, id=train_id)
    train_class_availability = get_object_or_404(TrainClassAvailability, id=ticket_class_id, train=train)

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            num_passengers = form.cleaned_data['num_passengers']

            if train_class_availability.available_seats >= num_passengers:
                train_class_availability.available_seats -= num_passengers
                train_class_availability.save()

                pnr = random.randint(1000000000, 9999999999)
                booking = form.save(commit=False)
                booking.user = request.user
                booking.train = train
                booking.train_class = train_class_availability.train_class
                booking.journey_date = train_class_availability.date  # Set journey_date from TrainClassAvailability
                booking.pnr = pnr
                booking.num_passengers = num_passengers
                booking.total_fare = num_passengers * train_class_availability.train_class.price
                booking.save()

                messages.success(request, f"Booking successful! Your PNR is {pnr}")
                return redirect('booking_confirmation', pnr=pnr)
            else:
                messages.error(request, "Not enough seats available!")
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = BookingForm(initial={'train_class': train_class_availability.train_class})

    return render(request, 'book_ticket.html', {
        'form': form,
        'train': train,
        'train_class_availability': train_class_availability
    })

def payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == "POST":
        messages.success(request, "Payment successful! Booking confirmed.")
        booking.status = "CONFIRMED"
        booking.save()
        return redirect('booking_confirmation', pnr=booking.pnr)
    return render(request, 'payment.html', {'booking': booking})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if request.method == "POST":
        booking.status = 'CANCELLED'
        booking.save()

        # Restore seats in TrainClassAvailability
        availability = TrainClassAvailability.objects.filter(train=booking.train, train_class=booking.train_class).first()
        if availability:
            availability.available_seats += booking.num_passengers
            availability.save()

        messages.success(request, "Your booking has been cancelled successfully.")
        return redirect('user_dashboard')

    return render(request, 'cancel_booking.html', {'booking': booking})

@login_required
def booking_confirmation(request, pnr):
    booking = get_object_or_404(Booking, pnr=pnr, user=request.user)
    return render(request, 'booking_confirmation.html', {'booking': booking})

@login_required
def booking_detail(request, pnr):
    booking = get_object_or_404(Booking, pnr=pnr, user=request.user)
    return render(request, 'booking_detail.html', {'booking': booking})

@login_required
def user_dashboard(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'user_dashboard.html', {'bookings': bookings})