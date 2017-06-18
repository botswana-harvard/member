from edc_base.modelform_validators import FormValidator
from edc_constants.constants import YES, NO


class HtcMemberFormValidator(FormValidator):

    def clean(self):
        self.required_if(
            NO, field='accepted', field_required='refusal_reason')
        self.applicable_if(YES, field='offered', field_applicable='referred')
        self.required_if(
            YES, field='referred', field_required='referral_clinic')
        return self.cleaned_data
