import random

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from faker import Faker

from blog.models import Blog, Comment


class Command(BaseCommand):
    help = 'Create 50-blogs, 10-users, 150-comments'

    def handle(self, *args, **options):
        Blog.objects.all().delete()
        Comment.objects.all().delete()
        User.objects.exclude(username='admin').delete()

        fake = Faker()

        users = User.objects.bulk_create([User(
            username=fake.name(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            password=make_password(fake.password())
        ) for _ in range(10)])

        for u in users:
            list_date = sorted([fake.date() for _ in range(5)])
            blogs = Blog.objects.bulk_create([Blog(
                title=fake.text(max_nb_chars=20),
                text=fake.paragraph(nb_sentences=5),
                author=u,
                post_date=list_date[i],
                is_posted=random.choice([True, False]),
            ) for i in range(5)])

            for b in blogs:
                Comment.objects.bulk_create([Comment(
                    author=u,
                    blog=b,
                    text=fake.paragraph(nb_sentences=1),
                    is_published=random.choice([True, False]),
                )for _ in range(3)])

        self.stdout.write(self.style.SUCCESS("Created 50-blogs, 10-users, 150-comments"))
