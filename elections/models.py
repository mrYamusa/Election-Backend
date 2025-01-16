from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Position(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

from django.db import models
from django.contrib.auth.models import User


class Candidate(models.Model):
    candidate_name = models.CharField(max_length=255, null=True, blank=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)  # The position they are running for
    # bio = models.TextField()  # Bio or description of the candidate
    profile_picture = models.ImageField(upload_to='candidate_photos/', null=True, blank=True)  # Profile picture
    created_at = models.DateTimeField(auto_now_add=True)
    vote_count = models.PositiveIntegerField(default=0)  # Initialize vote count to zero

    def __str__(self):
        return f"{self.candidate_name} - {self.position.name}"



class Election(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('active', 'Active'), ('completed', 'Completed')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Vote(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    voter = models.ForeignKey(User, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('election', 'voter', 'position')  # Ensure one vote per voter per position

    def __str__(self):
        return f"Vote by {self.voter} for {self.candidate} in {self.position}"

class Student(models.Model):
    reg_no = models.IntegerField(unique=True)
    web_mail = models.EmailField(unique=True)

class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Changed to ForeignKey to remove unique constraint
    registration_number = models.CharField(max_length=25, unique=True)
    web_mail = models.EmailField(unique=True)

    def __str__(self):
        return self.user.username