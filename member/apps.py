from django.apps import AppConfig as DjangoApponfig
from django.conf import settings


class AppConfig(DjangoApponfig):
    name = 'member'
    listboard_template_name = 'member_dashboard/listboard.html'
    listboard_url_name = 'member_dashboard:listboard_url'
    base_template_name = 'edc_base/base.html'
    admin_site_name = 'member_admin'
    url_namespace = 'member_dashboard'
    anonymous_listboard_url_name = 'member_dashboard:anonymous_listboard_url'

    def ready(self):
        from member.signals import (
            absent_member_on_post_delete,
            absent_member_on_post_save,
            deceased_member_on_post_delete,
            deceased_member_on_post_save,
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
    from edc_device.apps import AppConfig as BaseEdcDeviceAppConfig, DevicePermission
    from edc_device.constants import CENTRAL_SERVER, CLIENT, NODE_SERVER

    class EdcMapAppConfig(BaseEdcMapAppConfig):
        verbose_name = 'Test Mappers'
        mapper_model = 'plot.plot'
        landmark_model = []
        verify_point_on_save = False
        zoom_levels = ['14', '15', '16', '17', '18']
        identifier_field_attr = 'plot_identifier'
        extra_filter_field_attr = 'enrolled'

    class EdcDeviceAppConfig(BaseEdcDeviceAppConfig):
        use_settings = True
        device_id = settings.DEVICE_ID
        device_role = settings.DEVICE_ROLE
        device_permissions = {
            'plot.plot': DevicePermission(
                model='plot.plot',
                create_roles=[CENTRAL_SERVER, CLIENT],
                change_roles=[NODE_SERVER, CENTRAL_SERVER, CLIENT])
        }
