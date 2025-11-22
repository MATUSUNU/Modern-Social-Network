from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from django.views.generic import (
  TemplateView, ListView, DetailView,
  CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.core.paginator import Paginator

from .models import Group, Membership

from django.template.loader import render_to_string


class GroupListView(ListView):
  template_name = "group/group_list.html"
  context_object_name = "groups"
  model = Group


class GroupDetailView(DetailView):
  template_name = "group/group_detail.html"
  context_object_name = "group"
  model = Group

  # def get_template_names(self):
  #   if self.request.headers.get('HX-Request'):
  #     return ['post/partials/group_posts.html']
  #   return [self.template_name]

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['is_owner'] = self.request.user == self.object.created_by

    # context["posts"] = self.object.posts.all()
    posts = self.object.posts.all()
    paginator = Paginator(posts, 3)
    page_obj = paginator.get_page(1)

    context["posts"] = page_obj.object_list
    context["page_obj"] = page_obj
    return context


class GroupCreateView(LoginRequiredMixin, CreateView):
  template_name = "group/group_form.html"
  model = Group
  fields = ["name", "description"]
  success_url = reverse_lazy("group:group_list")

  def form_valid(self, form):
    form.instance.created_by = self.request.user
    response = super().form_valid(form)

    Membership.objects.get_or_create(
        user=self.request.user,
        group=self.object
    )
    return response


class GroupUpdateView(LoginRequiredMixin, UpdateView):
  template_name = "group/group_form.html"
  model = Group
  fields = ["name", "description"]
  success_url = reverse_lazy("group:group_list")


class GroupDeleteView(LoginRequiredMixin, DeleteView):
  template_name = "group/group_confirm_delete.html"
  model = Group
  success_url = reverse_lazy("group:group_list")


@login_required
def member_group(request, pk):
  group = get_object_or_404(Group, pk=pk)

  member, created = group.memberships.get_or_create(
    user = request.user,
    group = group
  )
  if not created:
    member.delete()

  group = get_object_or_404(Group, pk=pk)

  if request.headers.get('HX-Request'):
      context = {
          'group': group,
          'request': request,
          'is_owner': request.user == group.created_by,
      }
      html = render_to_string('group/partials/group_header_content.html', context)
      return HttpResponse(html)
  return redirect("group:group_detail", pk=group.id)

def group_posts(request, pk):

    # For Dev
    import time
    time.sleep(1)

    group = get_object_or_404(Group, pk=pk)

    posts = group.posts.all()
    # Optimized query
    # posts = group.posts.all().select_related('user').prefetch_related(
    #     'likes', 'comments'
    # ).order_by('-created_at')

    paginator = Paginator(posts, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'posts': page_obj.object_list,
        'page_obj': page_obj,
        'group': group,
        'request': request,
    }

    template = 'group/partials/group_posts.html'
    return render(request, template, context)
