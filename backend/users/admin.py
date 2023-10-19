from django.contrib import admin

from recipe.admin import BaseAdmin
from users.models import User, Follow


@admin.register(User)
class UserAdmin(BaseAdmin):
    pass


@admin.register(Follow)
class FollowAdmin(BaseAdmin):
    pass
