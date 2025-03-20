from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('base/',views.base,name='base'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('search/', views.search_trains, name='search_trains'),
    path('book/<int:train_id>/', views.book_ticket, name='book_ticket'),

    path("search-station/", views.station_suggestions, name="station_suggestions"),

    path('payment/<int:booking_id>/', views.payment, name='payment'),

    path('confirmation/<str:pnr>/', views.booking_confirmation, name='booking_confirmation'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),

    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('booking/<str:pnr>/', views.booking_detail, name='booking_detail'),
    path("pnr-status/", views.pnr_status, name="pnr_status"),
]
