from django.shortcuts import render, redirect, get_object_or_404

from django.views.generic import (
  TemplateView, ListView, DetailView,
  CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

from .models import Group, Membership


class GroupListView(ListView):
  template_name = "group/group_list.html"
  context_object_name = "groups"
  model = Group


class GroupDetailView(DetailView):
  template_name = "group/group_detail.html"
  context_object_name = "group"
  model = Group

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    if self.request.user == self.object.created_by:
      context["is_owner"] = True
    else:
      context["is_owner"] = False
    context["posts"] = self.object.posts.all()
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
  return redirect("group:group_detail", pk=group.id)
