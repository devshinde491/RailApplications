from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserProfile, Passenger, Booking, Train, TrainClass, Station, Payment, TrainClassAvailability


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15)
    address = forms.CharField(widget=forms.Textarea)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    id_proof_type = forms.ChoiceField(choices=[
        ('PASSPORT', 'Passport'),
        ('DRIVING_LICENSE', 'Driving License'),
        ('VOTER_ID', 'Voter ID'),
        ('AADHAR', 'Aadhar Card')
    ])
    id_proof_number = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2',
                  'phone_number', 'address', 'date_of_birth', 'id_proof_type', 'id_proof_number']


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'})
    )


class TrainSearchForm(forms.Form):
    source = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_source', 'placeholder': 'Enter Source Station'})
    )
    destination = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_destination', 'placeholder': 'Enter Destination Station'})
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'id_date'})
    )
    train_type = forms.ChoiceField(
        choices=[
            ('', 'All Types'),  # Default empty option
            ('express', 'Express'),
            ('local', 'Local'),
            ('superfast', 'Superfast'),
            ('shatabdi', 'Shatabdi')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_train_type'})
    )


class BookingForm(forms.ModelForm):
    journey_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    train_class = forms.ModelChoiceField(queryset=TrainClass.objects.none(), required=True)
    num_passengers = forms.IntegerField(min_value=1, max_value=6, required=True)

    def __init__(self, *args, **kwargs):
        train = kwargs.pop('train', None)
        super(BookingForm, self).__init__(*args, **kwargs)

        if train:
            self.fields['train_class'].queryset = TrainClass.objects.filter(
                trainclassavailability__train=train,
                trainclassavailability__available_seats__gt=0
            )

    class Meta:
        model = Booking
        fields = ['journey_date', 'train_class', 'num_passengers']


class PassengerForm(forms.ModelForm):
    id_proof_number = forms.CharField(max_length=50, required=False)
    is_senior_citizen = forms.BooleanField(required=False)

    class Meta:
        model = Passenger
        fields = ['name', 'age', 'gender', 'berth_preference']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name as per ID proof'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '120'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'berth_preference': forms.Select(attrs={'class': 'form-select'}),
        }


PassengerFormSet = forms.formset_factory(PassengerForm, extra=1)


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_method']