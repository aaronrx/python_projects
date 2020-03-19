from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import BlogPost
from .forms import BlogPostForm


def check_post_owner(blogpost, request):
    """Check owner of the blogpost to make sure it belongs to the current user"""
    if blogpost.owner != request.user:
        raise Http404


# Create your views here.
def index(request):
    """blogsite index page"""
    return render(request, 'blogs/index.html')


@login_required
def home(request):
    """The home page for your awesome blogsite showing all of user's posts"""
    blogposts = BlogPost.objects.filter(owner=request.user).order_by('-date_added')

    context = {'blogposts': blogposts}
    return render(request, 'blogs/home.html', context)


@login_required
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
        new_post = form.save(commit=False)
        new_post.owner = request.user
        new_post.save()

        # Go back to the topics page.
        return HttpResponseRedirect(reverse('blogs:home'))

    # Return a blank form
    context = {'form': form}
    return render(request, 'blogs/new_post.html', context)


@login_required
def edit_post(request, blogpost_id):
    """Edit an existing post."""
    blogpost = get_object_or_404(BlogPost, id=blogpost_id)
    check_post_owner(blogpost, request)

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
