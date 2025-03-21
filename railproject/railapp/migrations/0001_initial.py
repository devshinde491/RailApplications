# Generated by Django 5.1.7 on 2025-03-20 03:24

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Station',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('code', models.CharField(max_length=10, unique=True)),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('zone', models.CharField(blank=True, max_length=50, null=True)),
                ('station_type', models.CharField(max_length=50)),
                ('number_of_platforms', models.IntegerField(blank=True, default=1, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('has_wifi', models.BooleanField(default=False)),
                ('has_retiring_room', models.BooleanField(default=False)),
                ('has_food_plaza', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='TrainClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('capacity', models.IntegerField(default=100)),
            ],
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('journey_date', models.DateField()),
                ('num_passengers', models.IntegerField(default=1)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('CONFIRMED', 'Confirmed'), ('CANCELLED', 'Cancelled')], default='PENDING', max_length=20)),
                ('contact_email', models.EmailField(default='default@example.com', max_length=254)),
                ('contact_phone', models.CharField(default='+91 0000000000', max_length=15)),
                ('total_fare', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('pnr', models.CharField(blank=True, max_length=10, unique=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Passenger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('age', models.IntegerField(default=18)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], max_length=1)),
                ('berth_preference', models.CharField(choices=[('LOWER', 'Lower'), ('MIDDLE', 'Middle'), ('UPPER', 'Upper'), ('SIDE_LOWER', 'Side Lower'), ('SIDE_UPPER', 'Side Upper')], max_length=20)),
                ('is_senior_citizen', models.BooleanField(default=False)),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='passengers', to='railapp.booking')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_method', models.CharField(choices=[('CARD', 'Card'), ('UPI', 'UPI'), ('NETBANKING', 'Net Banking')], max_length=50)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed')], default='PENDING', max_length=20)),
                ('transaction_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('booking', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='railapp.booking')),
            ],
        ),
        migrations.CreateModel(
            name='Train',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('train_number', models.CharField(max_length=10, unique=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('train_type', models.CharField(choices=[('express', 'Express'), ('local', 'Local'), ('superfast', 'Superfast'), ('shatabdi', 'Shatabdi')], max_length=50)),
                ('departure_time', models.TimeField()),
                ('arrival_time', models.TimeField()),
                ('runs_on', models.CharField(default='daily', max_length=20)),
                ('destination', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='arriving_trains', to='railapp.station')),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='departing_trains', to='railapp.station')),
            ],
        ),
        migrations.AddField(
            model_name='booking',
            name='train',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='railapp.train'),
        ),
        migrations.AddField(
            model_name='booking',
            name='train_class',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='railapp.trainclass'),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=15)),
                ('address', models.TextField()),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('id_proof_type', models.CharField(choices=[('PASSPORT', 'Passport'), ('DRIVING_LICENSE', 'Driving License'), ('VOTER_ID', 'Voter ID'), ('AADHAR', 'Aadhar Card')], max_length=20)),
                ('id_proof_number', models.CharField(max_length=50)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TrainClassAvailability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, null=True)),
                ('available_seats', models.IntegerField(default=0)),
                ('total_seats', models.IntegerField(default=0)),
                ('train', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='railapp.train')),
                ('train_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='railapp.trainclass')),
            ],
            options={
                'unique_together': {('train', 'train_class', 'date')},
            },
        ),
        migrations.CreateModel(
            name='TrainRoute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arrival_time', models.TimeField()),
                ('departure_time', models.TimeField()),
                ('stop_number', models.IntegerField()),
                ('station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='railapp.station')),
                ('train', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='railapp.train')),
            ],
            options={
                'unique_together': {('train', 'station')},
            },
        ),
    ]
