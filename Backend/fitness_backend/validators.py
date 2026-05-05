from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_age(value):
    """Validate age is within a reasonable range."""
    if value < 13 or value > 120:
        raise ValidationError(_('Age must be between 13 and 120 years.'))


def validate_weight(value):
    """Validate weight in kg."""
    if value < 20 or value > 500:
        raise ValidationError(_('Weight must be between 20 and 500 kg.'))


def validate_height(value):
    """Validate height in cm."""
    if value < 50 or value > 300:
        raise ValidationError(_('Height must be between 50 and 300 cm.'))


def validate_bmi(value):
    """Validate BMI is within a calculable range."""
    if value < 5 or value > 100:
        raise ValidationError(_('BMI must be between 5 and 100.'))
