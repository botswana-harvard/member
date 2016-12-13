from django.contrib.admin import AdminSite


class MemberAdminSite(AdminSite):
    site_title = 'Member'
    site_header = 'Member'
    index_title = 'Member'
    site_url = '/'
member_admin = MemberAdminSite(name='member_admin')
