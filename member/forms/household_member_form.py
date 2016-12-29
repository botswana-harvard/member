from django import forms
from django.forms import Select
from django.forms.utils import ErrorList
from django.forms.utils import flatatt
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from edc_constants.constants import DEAD, NO, YES, FEMALE, MALE

from household.models.household_structure import HouseholdStructure
from ..choices import RELATIONS, FEMALE_RELATIONS, MALE_RELATIONS
from ..constants import HEAD_OF_HOUSEHOLD
from ..models import HouseholdMember, EnrollmentChecklist
from ..exceptions import MemberValidationError


class ReadOnlySelect(Select):
    """
    This should replace the Select widget with a disabled text widget displaying the value,
    and hidden field with the actual id
    """
    def render(self, name, value, attrs=None, choices=()):
        final_attrs = self.build_attrs(attrs, name=name)
        display = value
        output = format_html('<input type=text value="%s" disabled="disabled" ><input type="hidden" value="%s"  %s> ' % (display, value, flatatt(final_attrs)))
        return mark_safe(output)


class HouseholdMemberForm(forms.ModelForm):

    household_structure = forms.ModelChoiceField(
        queryset=HouseholdStructure.objects.all(),
        widget=ReadOnlySelect)

    def validate_on_gender(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('gender') == MALE:
            if cleaned_data.get('relation') not in [item[0] for item in RELATIONS if item not in FEMALE_RELATIONS]:
                raise forms.ValidationError(
                    'Member is Male but you selected a female relation. Got {0}.'.format(
                        [item[1] for item in RELATIONS if item[0] == cleaned_data.get('relation')][0]))
        if cleaned_data.get('gender') == FEMALE:
            if cleaned_data.get('relation') not in [item[0] for item in RELATIONS if item not in MALE_RELATIONS]:
                raise forms.ValidationError(
                    'Member is Female but you selected a male relation. Got {0}.'.format(
                        [item[1] for item in RELATIONS if item[0] == cleaned_data.get('relation')][0]))

    def clean(self):
        cleaned_data = super(HouseholdMemberForm, self).clean()
        if cleaned_data.get('relation') == HEAD_OF_HOUSEHOLD and not cleaned_data.get('age_in_years') >= 18:
            raise forms.ValidationError('Head of Household must be 18 years or older.')
        if cleaned_data.get('eligible_hoh') and cleaned_data.get('age_in_years') < 18:
            raise forms.ValidationError('This household member completed the HoH questionnaire. '
                                        'You cannot change their age to less than 18. '
                                        'Got {0}.'.format(cleaned_data.get('age_in_years')))
        self.validate_on_gender()

        if cleaned_data.get('survival_status') == DEAD:
            if not cleaned_data.get('present_today') == NO:
                self._errors["present_today"] = ErrorList([u"Please, select No."])
            if cleaned_data.get('study_resident') == NO or cleaned_data.get('study_resident') == YES:
                self._errors["study_resident"] = ErrorList([u"Please, select don't want to answer "])

        if cleaned_data.get('personal_details_changed') == YES:
            if not cleaned_data.get('details_change_reason'):
                raise forms.ValidationError(
                    'Provide why personal details has changed.')
        try:
            enrollment_checklist = EnrollmentChecklist.objects.get(household_member=self.instance)
            enrollment_checklist.matches_household_member_values(
                enrollment_checklist, HouseholdMember(**cleaned_data), exception_cls=forms.ValidationError)
        except EnrollmentChecklist.DoesNotExist:
            pass
        try:
            instance = self._meta.model(id=self.instance.id, **cleaned_data)
            instance.common_clean()
        except MemberValidationError as e:
            raise forms.ValidationError(str(e))
        return cleaned_data

    class Meta:
        model = HouseholdMember
        fields = '__all__'
