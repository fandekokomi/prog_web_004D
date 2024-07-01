from django.contrib import admin
from libs.multi_captcha_admin.forms import MultiCaptchaAdminAuthenticationForm

admin.AdminSite.login_form = MultiCaptchaAdminAuthenticationForm
