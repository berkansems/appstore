from django.contrib.auth import get_user_model
from django.db import models
from apps.models import App


class Order(models.Model):
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='user_orders')
    app = models.ForeignKey(App, on_delete=models.CASCADE, related_name='orders')
    purchase_date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-purchase_date']
        constraints = [
            models.UniqueConstraint(fields=['owner', 'app'], name='unique_owner_app_order')
        ]

    def __str__(self):
        return f"{self.owner.email} purchased the app '{self.app.title}'"
