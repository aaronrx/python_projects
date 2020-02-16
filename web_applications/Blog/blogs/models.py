from django.db import models


# Create your models here.
class BlogPost(models.Model):
    """A Blog post entered by the user."""
    title = models.CharField(max_length=50)
    text = models.CharField(max_length=200)

    # The argument auto_add_now=True tells Django to automatically set this attribute
    # to the current date and time whenever the user creates a new topic.
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a string representation of the model."""
        return self.text
