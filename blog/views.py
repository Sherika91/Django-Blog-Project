from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView

from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class PostListView(ListView):
    """ Alternatife for post_list but using classes """

    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

    def paginate_queryset(self, queryset, page_size):
        paginator = self.get_paginator(queryset, page_size)
        page_kwarg = self.page_kwarg
        page = self.request.GET.get(page_kwarg, 1)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            # If page_number is not an integer deliver the first page
            posts = paginator.page(1)
        except EmptyPage:
            # If page_number is out of range deliver last page of results
            posts = paginator.page(paginator.num_pages)
        return paginator, posts, posts.object_list, posts.has_other_pages()


# def post_list(request):
#     """ List all published posts. """
#     post_list = Post.published.all()
#     # Pagination with 3 posts per page
#     paginator = Paginator(post_list, 3)
#     page_number = request.GET.get('page', 1)
#     try:
#         posts = paginator.page(page_number)
#     except PageNotAnInteger:
#         # If page_number is not an integer deliver the first page
#         posts = paginator.page(1)
#     except EmptyPage:
#         # If page_number is out of range deliver last page of results
#         posts = paginator.page(paginator.num_pages)
#     return render(request,
#                   'blog/post/list.html',
#                   {'posts': posts})


def post_detail(request, year, month, day, post):
    """ Display a single post. """
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    return render(request,
                  'blog/post/detail.html',
                  {'post': post})
