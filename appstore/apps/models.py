from django.contrib.auth import get_user_model
from django.db import models
from model_utils import FieldTracker
from django.utils.timezone import now


class App(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_VERIFIED = 'verified'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_VERIFIED, 'Verified'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    title = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='apps', db_index=True)
    verification_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_date = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Track changes to verification_status
    tracker = FieldTracker()

    def verify(self):
        if not self.verified_date:  # if not already verified
            self.verification_status = self.STATUS_VERIFIED
            self.save()

    def save(self, *args, **kwargs):
        if self.tracker.has_changed('verification_status') and not self.verified_date:
            if self.verification_status == self.STATUS_VERIFIED:
                self.verified_date = now()

        super(App, self).save(*args, **kwargs)

    def __str__(self):
        return self.title
