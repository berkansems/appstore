from django.contrib import admin
from .models import App

@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'price', 'verification_status', 'created_at')
    list_filter = ('verification_status', 'created_at')
    search_fields = ('title', 'owner__username')
    ordering = ('-created_at',)
    actions = ['verify_apps']

    @admin.action(description="Verify selected apps")
    def verify_apps(self, request, queryset):
        """
        Custom admin action to verify selected apps.
        Apps that are already verified will be skipped.
        """
        count = 0
        for app in queryset:
            if not app.verified_date:  # Skip already verified apps
                app.verify()
                count += 1

        self.message_user(request, f"{count} app(s) verified successfully.")