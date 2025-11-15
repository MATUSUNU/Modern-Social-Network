from django.shortcuts import render, redirect, get_object_or_404

from django.views.generic import (
  TemplateView, ListView, DetailView,
  CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied

from .models import Post, Comment
from apps.group.models import Group


class PostListView(ListView):
  template_name = "post/post_list.html"
  context_object_name = "posts"
  model = Post


class PostDetailView(DeleteView):
  template_name = "post/post_detail.html"
  model = Post

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['comments'] = self.object.comments.all()
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
  return redirect("post:post_list")

@login_required
def comment_create(request, pk):
  post = get_object_or_404(Post, pk=pk)

  if request.method == "POST":
    content = request.POST['content']

    if content:
      Comment.objects.create(
        user = request.user,
        post = post,
        content = content
      )
  return redirect("post:post_detail", pk=post.id)

@login_required
def comment_delete(request, pk):
  comment = get_object_or_404(Comment, pk=pk)

  if request.method == "POST":
    comment.delete()

  return redirect("post:post_detail", pk=comment.post.id)
