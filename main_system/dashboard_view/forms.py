from django import forms

class ForecastForm(forms.Form):
    FORECAST_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    forecast_period = forms.ChoiceField(
        choices=FORECAST_CHOICES,
        label="Forecast Period",
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='monthly',
    )