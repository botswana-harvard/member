from django.apps import AppConfig as DjangoApponfig


class AppConfig(DjangoApponfig):
    name = 'member'
    list_template_name = None

    def ready(self):
        from member.signals import (
            absent_member_on_post_delete,
            absent_member_on_post_save,
            deceased_member_on_post_save,
            deceased_member_on_post_delete,
            enrollment_checklist_on_post_delete,
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
