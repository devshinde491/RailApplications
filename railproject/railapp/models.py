# models.py
from django.db import models
from django.contrib.auth.models import User
import random
import string
from django.utils.timezone import now

class Station(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zone = models.CharField(max_length=50, null=True, blank=True)
    station_type = models.CharField(max_length=50)
    number_of_platforms = models.IntegerField(null=True, blank=True, default=1)
    address = models.TextField(null=True, blank=True)
    has_wifi = models.BooleanField(default=False)
    has_retiring_room = models.BooleanField(default=False)
    has_food_plaza = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.code})"

class Train(models.Model):
    train_number = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100, unique=True)
    TRAIN_TYPES = [
        ('express', 'Express'),
        ('local', 'Local'),
        ('superfast', 'Superfast'),
        ('shatabdi', 'Shatabdi'),
    ]
    train_type = models.CharField(max_length=50, choices=TRAIN_TYPES)
    source = models.ForeignKey(Station, related_name="departing_trains", on_delete=models.CASCADE)
    destination = models.ForeignKey(Station, related_name="arriving_trains", on_delete=models.CASCADE)
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    runs_on = models.CharField(max_length=20, default="daily")

    def __str__(self):
        return f"{self.train_number} - {self.name}"

class TrainClass(models.Model):
    name = models.CharField(max_length=50)  # Example: 'Sleeper', 'AC 1st Class'
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Ticket Price
    capacity = models.IntegerField(default=100)

    def __str__(self):
        return f"{self.name} (₹{self.price})"

class TrainClassAvailability(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    train_class = models.ForeignKey(TrainClass, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True) # Added to track availability for specific dates
    available_seats = models.IntegerField(default=0)
    total_seats = models.IntegerField(default=0)

    class Meta:
        unique_together = ('train', 'train_class', 'date')  # Ensure uniqueness for train, class, and date

    def __str__(self):
        return f"{self.train} - {self.train_class} ({self.available_seats} available on {self.date})"

class TrainRoute(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    arrival_time = models.TimeField()
    departure_time = models.TimeField()
    stop_number = models.IntegerField()  # Order of stops

    class Meta:
        unique_together = ('train', 'station')

    def __str__(self):
        return f"{self.train.name} - {self.station.name}"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    train_class = models.ForeignKey(TrainClass, on_delete=models.CASCADE)
    journey_date = models.DateField()
    num_passengers = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    contact_email = models.EmailField(default='default@example.com')
    contact_phone = models.CharField(max_length=15, default="+91 0000000000")
    total_fare = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pnr = models.CharField(max_length=10, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pnr:
            while True:
                pnr = ''.join(random.choices(string.digits, k=10))
                if not Booking.objects.filter(pnr=pnr).exists():
                    self.pnr = pnr
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking {self.pnr} - {self.user.username}"

class UserProfile(models.Model):
    ID_PROOF_TYPES = [
        ('PASSPORT', 'Passport'),
        ('DRIVING_LICENSE', 'Driving License'),
        ('VOTER_ID', 'Voter ID'),
        ('AADHAR', 'Aadhar Card'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    date_of_birth = models.DateField(null=True, blank=True)
    id_proof_type = models.CharField(max_length=20, choices=ID_PROOF_TYPES)
    id_proof_number = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Passenger(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    BERTH_PREFERENCES = [
        ('LOWER', 'Lower'),
        ('MIDDLE', 'Middle'),
        ('UPPER', 'Upper'),
        ('SIDE_LOWER', 'Side Lower'),
        ('SIDE_UPPER', 'Side Upper'),
    ]

    booking = models.ForeignKey(Booking, related_name='passengers', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    age = models.IntegerField(default=18)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    berth_preference = models.CharField(max_length=20, choices=BERTH_PREFERENCES)
    is_senior_citizen = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.booking.pnr}"

class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=[('CARD', 'Card'), ('UPI', 'UPI'), ('NETBANKING', 'Net Banking')])
    status = models.CharField(max_length=20, choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed')], default='PENDING')
    transaction_date = models.DateTimeField(default=now)

    def __str__(self):
        return f"Payment for {self.booking.pnr} - {self.status}"