from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from blog.models import Post


class PostListView(ListView):
    model = Post


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ('title', 'body',)
    success_url = reverse_lazy('blog:post_list')

    def form_valid(self, form):
        self.object = form.save()
        self.object.owner = self.request.user
        self.object.save()
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ('title', 'body',)

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if not self.request.user.is_superuser or self.object.owner != self.request.user:
            raise Http404
        return self.object

    def get_success_url(self):
        return reverse('blog:post_view', args=[self.kwargs.get('pk')])


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:post_list')

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if self.object.owner != self.request.user:
            raise Http404
        return self.object
