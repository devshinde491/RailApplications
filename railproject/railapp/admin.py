from django.contrib import admin
from .models import (
    Station, Train, UserProfile, Booking,
    Passenger, TrainClass, TrainClassAvailability
)


@admin.register(TrainClass)
class TrainClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity')
    search_fields = ('name',)

class TrainClassAvailabilityInline(admin.TabularInline):
    model = TrainClassAvailability
    extra = 1

@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = ('train_number', 'name', 'train_type', 'get_source', 'get_destination', 'departure_time', 'arrival_time')
    list_filter = ('train_type',)

    def get_source(self, obj):
        return obj.source.name  # or obj.source.code
    get_source.admin_order_field = 'source'
    get_source.short_description = 'Source'

    def get_destination(self, obj):
        return obj.destination.name  # or obj.destination.code
    get_destination.admin_order_field = 'destination'
    get_destination.short_description = 'Destination'

@admin.register(TrainClassAvailability)
class TrainClassAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('train', 'train_class', 'total_seats', 'available_seats')
    search_fields = ('train__name', 'train__train_number', 'train_class__name')
    list_filter = ('train_class',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'id_proof_type')
    search_fields = ('user__username', 'user__email', 'phone_number')

class PassengerInline(admin.TabularInline):
    model = Passenger
    extra = 1

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
        list_display = ("name", "code", "city", "state", "zone", "number_of_platforms")
        search_fields = ("name", "code", "city")

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('pnr', 'user', 'train', 'train_class', 'journey_date', 'status', 'total_fare')
    search_fields = ('pnr', 'user__username')
    list_filter = ('status', 'journey_date', 'train_class')
    inlines = [PassengerInline]

@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ('name', 'booking', 'age', 'gender', 'berth_preference')
    search_fields = ('name', 'booking__pnr')
    list_filter = ('gender', 'berth_preference')
