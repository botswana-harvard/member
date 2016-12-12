from ..models import SubjectUndecided, SubjectUndecidedEntry

from .base_membership_form import BaseMembershipForm


class SubjectUndecidedEntryForm(BaseMembershipForm):

    household_member_fk = 'subject_undecided'

    class Meta:
        model = SubjectUndecidedEntry
        fields = '__all__'


class SubjectUndecidedForm(BaseMembershipForm):

    class Meta:
        model = SubjectUndecided
        fields = '__all__'
