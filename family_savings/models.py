from django.db import models
from users.models import User

# class FamilyMember(models.Model):
#     full_name = models.CharField(max_length=100)
#     is_active = models.BooleanField(default=True)

#     def __str__(self):
#         return self.full_name

class MonthlySaving(models.Model):
    MONTHS = [
        (1, 'Jan'), (2, 'Feb'),(3, 'Mar'), (4, 'Apr'), (5, 'May'), (6, 'Jun'), (7, 'Jul'), (8, 'Aug'), (9, 'Sep'), (10, 'Oct'), (11, 'Nov'), (12, 'Dec')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="savings")
    year = models.IntegerField()
    month = models.IntegerField(choices=MONTHS)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, help_text="When this record was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="When this record was last updated")

    class Meta:
        unique_together = ("user", "year", "month")

    def __str__(self):
        # Show username and month/year for easier identification
        return f"{self.user.username} - {self.month}/{self.year}"
