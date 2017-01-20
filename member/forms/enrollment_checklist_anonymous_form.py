from django import forms
from faker import Faker

from edc_constants.constants import NOT_APPLICABLE, YES, ALIVE, MALE, NO

from household.models.household_structure.household_structure import HouseholdStructure
from member.models.household_member.household_member import HouseholdMember
from member.models.household_member.utils import is_minor, is_adult, is_child
from plot.utils import get_anonymous_plot

from ..models import EnrollmentChecklistAnonymous

fake = Faker()


class EnrollmentChecklistAnonymousForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('age_in_years'):
            self.validate_age()

        if cleaned_data.get('citizen'):
            if cleaned_data.get('citizen') == YES:
                raise forms.ValidationError({
                    'citizen': 'Subject is not eligible for anonymous participation.'})
        if cleaned_data.get('literacy'):
            if cleaned_data.get('literacy') == NO:
                raise forms.ValidationError({
                    'literacy': 'Subject is not eligible.'})
        if cleaned_data.get('study_participation'):
            if cleaned_data.get('study_participation') == YES:
                raise forms.ValidationError({
                    'study_participation': 'Subject is not eligible.'})
        if cleaned_data.get('part_time_resident'):
            if cleaned_data.get('part_time_resident') == NO:
                raise forms.ValidationError({
                    'part_time_resident': 'Subject is not eligible.'})

        # insert Household Member a new household member into
        # cleaned_data
        household_member = cleaned_data.get('household_member')
        if not household_member and not self.instance.id:
            household_member = self.get_anonymous_member()
        else:
            raise forms.ValidationError('Household member is required')
        if household_member.is_consented:
            raise forms.ValidationError(
                'Household member has consented. Enrollment Checklist may not be modified')

        self.cleaned_data['household_member'] = household_member

        return cleaned_data

    def get_anonymous_member(self):
        plot = get_anonymous_plot()
        household_structure = HouseholdStructure.objects.get(household__plot=plot)
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
            inability_to_participate=NOT_APPLICABLE,
            first_name=first_name,
            initials=initials,
        )
        return household_member

    def validate_age(self):
        cleaned_data = self.cleaned_data
        age_in_years = cleaned_data.get('age_in_years')
        if is_child(age_in_years):
            raise forms.ValidationError(
                {'age_in_years': 'Subject is a child. Got {}y.'.format(age_in_years)})
        if is_minor(age_in_years) and cleaned_data.get('guardian') in [NO, NOT_APPLICABLE]:
            raise forms.ValidationError(
                {'guardian': 'Subject a minor. Got {}y'.format(age_in_years)})
        if is_adult(age_in_years) and not cleaned_data.get('guardian') in [YES, NO]:
            raise forms.ValidationError(
                {'guardian': 'Subject a not minor. Got {}y'.format(age_in_years)})

    class Meta:
        model = EnrollmentChecklistAnonymous
        fields = '__all__'
