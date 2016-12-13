from django.contrib import admin

from edc_base.modeladmin_mixins import StackedInlineMixin

from ..admin_site import member_admin
from ..forms import UndecidedMemberEntryForm
from ..models import UndecidedMember, UndecidedMemberEntry

from .modeladmin_mixins import HouseholdMemberAdminMixin


@admin.register(UndecidedMemberEntry, site=member_admin)
class UndecidedMemberEntryAdmin(HouseholdMemberAdminMixin, admin.ModelAdmin):

    fields = (
        'undecided_member',
        'report_datetime',
        'next_appt_datetime',
        'next_appt_datetime_source',
        'reason',
        'reason_other',
        'contact_details')

    list_display = (
        'undecided_member',
        'report_datetime',
        'next_appt_datetime',
        'contact_details')

    radio_fields = {
        "reason": admin.VERTICAL,
        "next_appt_datetime_source": admin.VERTICAL}

    list_filter = ('report_datetime', )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "undecided_member":
            kwargs["queryset"] = UndecidedMember.objects.filter(id__exact=request.GET.get('undecided_member', 0))
        return super(UndecidedMemberEntryAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class UndecidedMemberEntryInline(StackedInlineMixin, admin.StackedInline):
    form = UndecidedMemberEntryForm
    model = UndecidedMemberEntry
    max_num = 2
    extra = 1
