from django import forms
from django.forms.widgets import Select

from ..choices import HOUSEHOLD_MEMBER_PARTICIPATION


class ParticipationForm(forms.Form):
    """A form to select the type of participation for a household member.

    ...note:: configured and referenced directly on the household_member
              model via method participation_form()"""
    status = forms.ChoiceField(
        required=False,
        choices=HOUSEHOLD_MEMBER_PARTICIPATION,
        widget=Select(attrs={'onchange': 'this.form.submit();'})
    )
    household_member = forms.CharField(widget=forms.HiddenInput())
    dashboard_type = forms.CharField(widget=forms.HiddenInput())
    dashboard_id = forms.CharField(widget=forms.HiddenInput())
    dashboard_model = forms.CharField(widget=forms.HiddenInput())

    def as_table(self):
        "Returns this form rendered as HTML <tr>s -- excluding the <table></table>."
        return self._html_output(
            normal_row=u'<td>%(errors)s%(field)s%(help_text)s</td>',
            error_row=u'<tr><td colspan="2">%s</td></tr>',
            row_ender=u'</td>',
            help_text_html=u'<br /><span class="helptext">%s</span>',
            errors_on_separate_row=False)
