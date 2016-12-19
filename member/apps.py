from django.apps import AppConfig as DjangoApponfig


class AppConfig(DjangoApponfig):
    name = 'member'

    def ready(self):
        from member.signals import household_member_on_post_save, household_head_eligibility_on_post_save
