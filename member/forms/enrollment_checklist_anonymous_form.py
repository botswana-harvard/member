from faker import Faker

from django import forms
from django.apps import apps as django_apps
from django.conf import settings

from edc_constants.constants import YES, ALIVE, MALE, NO

from household.models.household_structure.household_structure import HouseholdStructure
from member.models import HouseholdMember
from plot.utils import get_anonymous_plot

from ..models import EnrollmentChecklistAnonymous
from ..constants import ABLE_TO_PARTICIPATE
from ..age_helper import AgeHelper

fake = Faker()


class EnrollmentChecklistAnonymousForm(forms.ModelForm):

    age_helper_cls = AgeHelper

    def clean(self):
        cleaned_data = super().clean()

        if not settings.ANONYMOUS_ENABLED:
            raise forms.ValidationError(
                'Non-citizens may not be enrolled at this time')

        self.validate_age()
        if cleaned_data.get('part_time_resident') == NO:
            raise forms.ValidationError({
                'part_time_resident': 'Subject is not eligible.'})
        elif cleaned_data.get('literacy') == NO:
            raise forms.ValidationError({
                'literacy': 'Subject is not eligible.'})
        else:
            # insert Household Member a new household member into
            # cleaned_data
            household_member = cleaned_data.get('household_member')
            if not household_member and not self.instance.id:
                household_member = self.get_anonymous_member()
            else:
                raise forms.ValidationError('Household member is required')
            if household_member.is_consented:
                raise forms.ValidationError(
                    'Household member has consented. '
                    'Enrollment Checklist may not be modified')
            self.cleaned_data['household_member'] = household_member

        return cleaned_data

    def get_anonymous_member(self):
        current_survey_schedule = django_apps.get_app_config(
            'survey').current_survey_schedule
        plot = get_anonymous_plot()
        household_structure = HouseholdStructure.objects.get(
            household__plot=plot,
            survey_schedule=current_survey_schedule)
        if self.cleaned_data.get('gender') == MALE:
            first_name = fake.first_name_male().upper()
        else:
            first_name = fake.first_name_female().upper()
        initials = (first_name[0] + fake.random_letter()).upper()
        household_member = HouseholdMember.objects.create(
            household_structure=household_structure,
            gender=self.cleaned_data.get('gender'),
            report_datetime=self.cleaned_data.get('report_datetime'),
            age_in_years=self.cleaned_data.get('age_in_years'),
            present_today=YES,
            survival_status=ALIVE,
            study_resident=YES,
            inability_to_participate=ABLE_TO_PARTICIPATE,
            relation='UNKNOWN',
            first_name=first_name,
            initials=initials,
            non_citizen=True,
        )
        return household_member

    def validate_age(self):
        cleaned_data = self.cleaned_data
        age_helper = self.age_helper_cls(**cleaned_data)
        age_helper.validate_or_raise()

    class Meta:
        model = EnrollmentChecklistAnonymous
        fields = '__all__'
