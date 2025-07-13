from django.contrib import admin
from .models import CustomUser, Post, Like, Comment, Notification, Message, Tag, Report
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'is_superuser', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('email',)
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('bio', 'profile_pic', 'followers')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('bio', 'profile_pic', 'followers')}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Notification)
admin.site.register(Message)
admin.site.register(Tag)
admin.site.register(Report)
