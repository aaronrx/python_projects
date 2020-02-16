from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Topic(models.Model):
    """A topic the user is learning about."""
    text = models.CharField(max_length=200)

    # The argument auto_add_now=True tells Django to automatically set this attribute
    # to the current date and time whenever the user creates a new topic.
    date_added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        """Return a string representation of the model."""
        return self.text


class Entry(models.Model):
    """Something specific learned about a topic"""
    # Foreign key is a database term; it’s a reference to another record in the database.
    # This is the code that connects each entry to a specific topic.
    topic = models.ForeignKey(Topic, on_delete=models.DO_NOTHING,)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta holds extra information for managing a model; here it allows us to set
           a special attribute telling Django to use Entries when it needs to refer to
           more than one entry. (Without this, Django would refer to multiple entries
           as Entrys.)"""
        verbose_name_plural = 'entries'

    def __str__(self):
        """Return a string representation of the model."""
        if len(self.text) <= 50:
            return self.text
        return self.text[:50] + "..."
