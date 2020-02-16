from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import BlogPost
from .forms import BlogPostForm


# Create your views here.
def index(request):
    """The home page for your awesome blogsite showing all your posts"""
    blogposts = BlogPost.objects.order_by('date_added')
    context = {'blogposts': blogposts}
    return render(request, 'blogs/index.html', context)


def new_post(request):
    """Create a new post."""
    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = BlogPostForm()
    else:
        # POST data submitted; process data.
        form = BlogPostForm(request.POST)

    # Check if all required fields are filled in and are valid.
    if form.is_valid():
        # Save the data from the form to the database.
        form.save()

        # Go back to the topics page.
        return HttpResponseRedirect(reverse('blogs:index'))

    # Return a blank form
    context = {'form': form}
    return render(request, 'blogs/new_post.html', context)


def edit_post(request, blogpost_id):
    """Edit an existing post."""
    blogpost = BlogPost.objects.get(id=blogpost_id)

    if request.method != 'POST':
        # Initial request; pre-fill form with the current entry.
        form = BlogPostForm(instance=blogpost)
    else:
        # POST data submitted; process data.
        form = BlogPostForm(instance=blogpost, data=request.POST)

    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('blogs:index'))

    context = {'blogpost': blogpost, 'form': form}
    return render(request, 'blogs/edit_post.html', context)
