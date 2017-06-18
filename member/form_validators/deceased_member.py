from edc_base.modelform_validators import FormValidator


class DeceasedMemberFormValidator(FormValidator):

    def clean(self):
        self.validate_other_specify(
            'death_cause_info', 'death_cause_info_other')
        return self.cleaned_data
