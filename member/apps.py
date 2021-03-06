from django.apps import AppConfig as DjangoApponfig
from django.conf import settings


class AppConfig(DjangoApponfig):
    name = 'member'
    admin_site_name = 'member_admin'

    def ready(self):
        from member.signals import (
            absent_member_on_post_delete,
            absent_member_on_post_save,
            deceased_member_on_post_delete,
            deceased_member_on_post_save,
            enrollment_checklist_on_post_save,
            enrollment_loss_on_post_delete,
            enrollment_loss_on_post_save,
            household_head_eligibility_on_post_save,
            household_member_on_post_save,
            moved_member_on_post_delete,
            moved_member_on_post_save,
            refused_member_on_post_delete,
            refused_member_on_post_save,
            undecided_member_on_post_delete,
            undecided_member_on_post_save
        )


if settings.APP_NAME == 'member':

    from edc_map.apps import AppConfig as BaseEdcMapAppConfig

    class EdcMapAppConfig(BaseEdcMapAppConfig):
        verbose_name = 'Test Mappers'
        mapper_model = 'plot.plot'
        landmark_model = []
        verify_point_on_save = False
        zoom_levels = ['14', '15', '16', '17', '18']
        identifier_field_attr = 'plot_identifier'
        extra_filter_field_attr = 'enrolled'
