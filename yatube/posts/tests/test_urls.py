# yatube/posts/tests/test_urls.py
from http.client import FOUND, NOT_FOUND, OK
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class UrlPostTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Unit1')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Текст тестового поста',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='User1')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(UrlPostTests.user)

    def test_correct_templates_in_urls(self):
        templates_urls_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html'
        }
        for url, template in templates_urls_names.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_create_redirect(self):
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    def test_urls_guest_client(self):
        url_status = {
            '/': OK,
            f'/group/{self.group.slug}/': OK,
            f'/profile/{self.user.username}/': OK,
            f'/posts/{self.post.pk}/': OK,
            '/create/': FOUND,
            f'/posts/{self.post.pk}/edit/': FOUND,
            '/unexisting_page/': NOT_FOUND,
            f'/profile/{self.user.username}/follow/': FOUND,
            f'/profile/{self.user.username}/unfollow/': FOUND
        }
        for url, status in url_status.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_post_edit_url_for_author(self):
        """Проверка доступа к редактированию поста для автора"""
        response = self.author_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, OK)

    def test_post_edit_url_for_non_author(self):
        """Проверка доступа к редактированию поста для НЕавтора"""
        response = self.authorized_client.get(
            f'/posts/{UrlPostTests.post.id}/edit/'
        )
        self.assertEqual(response.status_code, FOUND)
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.user},
            )
        )

    def test_post_edit_for_guest_user(self):
        post = Post.objects.create(
            text='Текст тестового поста',
            author=self.user
        )
        response = self.guest_client.get(
            f'/posts/{post.id}/edit/'
        )
        self.assertEqual(response.status_code, FOUND)
