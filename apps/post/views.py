from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from django.views.generic import (
  TemplateView, ListView, DetailView,
  CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator

from .models import Post, Comment
from apps.group.models import Group

import time


class PostListView(ListView):
  template_name = "post/post_list.html"
  context_object_name = "posts"
  paginate_by = 3
  model = Post

  def get_queryset(self):
      time.sleep(1)
      return super().get_queryset()

  def get_template_names(self):
    if self.request.headers.get('HX-Request'):
        return ['post/partials/post_list_items.html']
    return [self.template_name]


class PostDetailView(DetailView):
  template_name = "post/post_detail.html"
  model = Post

  def get_template_names(self):
    if self.request.headers.get('HX-Request'):
      return ['post/partials/post_detail.html']
    return [self.template_name]

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)

    comments = self.object.comments.all().order_by('created_at')
    paginator = Paginator(comments, 3)
    # page_num = self.request.GET.get('page', 1)
    page_obj = paginator.get_page(1)

    context['comments'] = page_obj.object_list
    context['page_obj'] = page_obj

    # context['comments'] = self.object.comments.all()
    return context


class PostCreateView(LoginRequiredMixin, CreateView):
  template_name = "post/post_form.html"
  model = Post
  fields = ["content", "image"]

  def get_success_url(self):
    group_id = self.kwargs.get('group_id')
    if group_id:
      return reverse_lazy('group:group_detail', kwargs={'pk': group_id})
    return reverse_lazy('post:post_list')

  def form_valid(self, form):
    group_id = self.kwargs.get('group_id')
    if group_id:
      group = get_object_or_404(Group, id=group_id)
      # check membership
      if not group.memberships.filter(user=self.request.user).exists():
        # raise PermissionDenied("You must be member first!")
        messages.error(self.request, "You must join the group before posting.")
        # messages.error(self.request, "You must join the group before posting.", extra_tags="membership")
        return self.form_invalid(form)
        # return redirect('group:group_detail', pk=group_id)
      form.instance.group = group
    form.instance.user = self.request.user
    return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
  template_name = "post/post_form.html"
  model = Post
  fields = ["content", "image"]
  success_url = reverse_lazy("post:post_list")


class PostDeleteView(LoginRequiredMixin, DeleteView):
  template_name = "post/post_confirm_delete.html"
  model = Post
  success_url = reverse_lazy("post:post_list")


@login_required
def like_post(request, pk):
  post = get_object_or_404(Post, pk=pk)
  like, created = post.likes.get_or_create(user=request.user, post=post)
  if not created:
    like.delete()

  post = get_object_or_404(Post, pk=pk)

  if request.headers.get('HX-Request'):
      from django.template.loader import render_to_string
      html = render_to_string('post/partials/like_button.html', {
          'post': post,
          'request': request,
          'user': request.user
      })
      return HttpResponse(html)

  return redirect("post:post_list")

@login_required
def comment_create(request, pk):
  post = get_object_or_404(Post, pk=pk)

  if request.method == "POST":
    content = request.POST['content']

    if content:
      comment = Comment.objects.create(
        user = request.user,
        post = post,
        content = content
      )

      if request.headers.get('HX-Request'):
          from django.template.loader import render_to_string
          from django.template.context_processors import csrf

          # html = render_to_string('post/partials/comment_item.html', {
          #     'comment': comment,
          #     'request': request
          # })
          context = {
            'comment': comment,
            'request': request,
          }
          context.update(csrf(request))
          comment_html = render_to_string('post/partials/comment_item.html', context)

          fresh_count = Comment.objects.filter(post=post).count()
          count_html = f'<span class="badge bg-secondary ms-2" id="comment-count" hx-swap-oob="true">{fresh_count}</span>'
          # count_html = f'<span class="badge bg-secondary ms-2" id="comment-count" hx-swap-oob="true">{post.comments.count()}</span>'
          return HttpResponse(comment_html + count_html)

  return redirect("post:post_detail", pk=post.id)

@login_required
def comment_delete(request, pk):
  comment = get_object_or_404(Comment, pk=pk)

  if request.method == "POST":
    comment.delete()

    if request.headers.get('HX-Request'):
      fresh_count = Comment.objects.filter(post_id=comment.post.id).count()
      count_html = f'<span class="badge bg-secondary ms-2" id="comment-count" hx-swap-oob="true">{fresh_count}</span>'

      return HttpResponse(count_html)

  return redirect("post:post_detail", pk=comment.post.id)

def post_comments(request, pk):

  import time
  time.sleep(1)

  post = get_object_or_404(Post, pk=pk)

  comments = post.comments.all().order_by('created_at')
  paginator = Paginator(comments, 3)
  page_num = request.GET.get('page')
  page_obj = paginator.get_page(page_num)

  context = {
    'post': post,
    'comments': page_obj.object_list,
    'page_obj': page_obj,
    'request': request
  }

  template = 'post/partials/comment_item.html'
  return render(request, template, context)
