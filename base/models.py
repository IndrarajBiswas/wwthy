"""Database models for storing submissions and recommendations."""

from django.db import models


class forminput(models.Model):
    """Persist submissions for the group recommendation form.

    The legacy lowercase class name is preserved to keep the existing database
    migrations functional.
    """

    email = models.EmailField()
    audiences = models.IntegerField(default=1)
    ageranges = models.CharField(max_length=4, default="-1")
    gp = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)


class singleforminput(models.Model):
    """Persist submissions for the single-user recommendation form."""

    email = models.EmailField()
    age = models.IntegerField(default=1)
    sum = models.IntegerField(default=0)
    gp = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)


