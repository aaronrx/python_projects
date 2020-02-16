from django.db import models


# Create your models here.
class Pizza(models.Model):
    """A pizza the customer wants to order."""
    name = models.CharField(max_length=30)

    # The argument auto_add_now=True tells Django to automatically set this attribute
    # to the current date and time whenever the user creates a new topic.
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a string representation of the model."""
        return self.name


class Topping(models.Model):
    """Toppings the customer want on the pizza."""
    # Foreign key is a database term; it’s a reference to another record in the database.
    # This is the code that connects each entry to a specific topic.
    pizza = models.ForeignKey(Pizza, on_delete=models.DO_NOTHING,)
    name = models.CharField(max_length=20)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta holds extra information for managing a model; here it allows us to set
           a special attribute telling Django to use toppings when it needs to refer to
           more than one entry. (Without this, Django would refer to multiple entries
           as Toppings.)"""
        verbose_name_plural = 'toppings'

    def __str__(self):
        """Return a string representation of the model."""
        return self.name
