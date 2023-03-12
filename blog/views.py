from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.views import generic

from blog.forms import RegisterForm, EmailForm
from blog.models import Blog, Comment
from blog.tasks import send_email_task, send_email_task_to_client

# User = get_user_model()


def index(request):
    num_blogs = Blog.objects.filter(is_posted=True).count()
    num_comments = Comment.objects.filter(is_published=True).count()
    num_authors = User.objects.count()

    return render(
        request,
        "index.html",
        context={
            'num_blogs': num_blogs,
            'num_comments': num_comments,
            'num_authors': num_authors
        }
    )


def email_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            from_email = form.cleaned_data['from_email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            send_email_task.delay(from_email, subject, message)

        else:
            data['form_is_valid'] = False

    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


def email_create(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
    else:
        form = EmailForm()
    return email_form(request, form, 'send_mail/contact.html')


class BlogListView(generic.ListView):
    model = Blog
    paginate_by = 10

    queryset = Blog.objects.prefetch_related(
        Prefetch('comment_set', queryset=Comment.objects.filter(is_published=True))
    ).select_related(
        "author"
    ).filter(is_posted=True).order_by('-post_date')


class BlogDetailView(generic.DetailView):
    model = Blog
    queryset = Blog.objects.select_related('author').prefetch_related(
        Prefetch('comment_set', queryset=Comment.objects.filter(is_published=True))
    )


class MyBlogListView(LoginRequiredMixin, generic.ListView):
    model = Blog
    template_name = 'blog/myblog_list_user.html'
    paginate_by = 10

    def get_queryset(self):
        return Blog.objects.prefetch_related(
            Prefetch('comment_set', queryset=Comment.objects.filter(is_published=True))
        ).filter(
            author=self.request.user
        ).order_by('post_date')


class BlogCreate(LoginRequiredMixin, generic.CreateView):
    model = Blog
    fields = ['title', 'text', 'post_date', 'is_posted']

    def form_valid(self, form):
        form.instance.author = self.request.user
        from_email = self.request.user.email
        subject = form.cleaned_data.get('title')
        message = f"{super(BlogCreate, self).form_valid(form)} {form.cleaned_data.get('text')}"
        send_email_task.delay(from_email, subject, message)
        return super(BlogCreate, self).form_valid(form)


class BlogUpdate(LoginRequiredMixin, generic.UpdateView):
    model = Blog
    fields = ['title', 'text', 'post_date', 'is_posted']

    def get_queryset(self):
        return Blog.objects.filter(author=self.request.user)


class CommentCreate(generic.CreateView):
    model = Comment
    fields = ['text']

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.author = self.request.user
        form.instance.blog = get_object_or_404(Blog, pk=self.kwargs['pk'])

        from_email = 'admin@example.com'
        post_url = self.request.build_absolute_uri(reverse('blog-detail', kwargs={'pk': self.kwargs['pk'], }))
        subject = 'comment'
        message = f"{post_url}  {form.cleaned_data.get('text')}"
        send_email_task.delay(from_email, subject, message)
        from_email = form.instance.blog.author.email
        send_email_task_to_client.delay(from_email, subject, message)

        return super(CommentCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse('blog-detail', kwargs={'pk': self.kwargs['pk'], })


class UserListView(generic.ListView):
    model = User
    template_name = 'blog/user_list.html'
    paginate_by = 10
    queryset = User.objects.prefetch_related(
        Prefetch('blog_set', queryset=Blog.objects.filter(is_posted=True))
    ).order_by('username')


class UserDetailView(generic.DetailView):
    template_name = 'blog/user_detail.html'
    model = User
    queryset = User.objects.prefetch_related(
        Prefetch('blog_set', queryset=Blog.objects.prefetch_related(
            Prefetch('comment_set', queryset=Comment.objects.filter(is_published=True))))
    )


class RegisterFormView(generic.FormView):
    template_name = "registration/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        user = form.save()
        user = authenticate(self.request, username=user.username, password=form.cleaned_data.get("password1"))
        login(self.request, user)
        return super(RegisterFormView, self).form_valid(form)


class UserProfile(LoginRequiredMixin, generic.DetailView):
    model = User
    template_name = "registration/profile.html"

    def get_object(self, queryset=None):
        user = self.request.user
        return user


class UpdateProfile(LoginRequiredMixin, SuccessMessageMixin, generic.UpdateView):
    model = User
    fields = ["first_name", "last_name", "email"]
    template_name = "registration/update_profile.html"
    success_url = reverse_lazy("index")
    success_message = "Profile updated"

    def get_object(self, queryset=None):
        user = self.request.user
        return user
