from django.shortcuts import render
from .models import Pizza, Topping


# Create your views here.
def index(request):
    """The home page for Pizzeria"""
    return render(request, 'pizzas/index.html')


def menu(request):
    """Show all pizzas"""
    pizzas = Pizza.objects.order_by('date_added')
    context = {'pizzas': pizzas}
    return render(request, 'pizzas/menu.html', context)


def pizza(request, pizza_id):
    """Show available toppings of a pizza"""
    pizza = Pizza.objects.get(id=pizza_id)
    toppings = pizza.topping_set.order_by('-date_added')
    context = {'pizza': pizza, 'toppings': toppings}
    return render(request, 'pizzas/pizza.html', context)
