from django.forms import ValidationError

from edc_constants.constants import YES, NO, NOT_APPLICABLE


class AgeHelper:

    def __init__(self, age_in_years=None, guardian=None, **kwargs):
        self.age_in_years = age_in_years
        self.guardian = guardian
        self.is_child = self.age_in_years < 16
        self.is_minor = 16 <= self.age_in_years < 18
        self.is_adult = 18 <= self.age_in_years
        self.is_age_eligible = 16 <= self.age_in_years <= 64

    def validate_or_raise(self):
        if self.is_child:
            raise ValidationError(
                {'age_in_years': f'Subject is a child. Got {self.age_in_years}y.'})
        elif self.is_minor and self.guardian in [NO, NOT_APPLICABLE]:
            raise ValidationError(
                {'guardian': f'Subject a minor. Got {self.age_in_years}y'})
        elif self.is_adult and self.guardian in [YES, NO]:
            raise ValidationError(
                {'guardian': f'Subject a not minor. Got {self.age_in_years}y'})
