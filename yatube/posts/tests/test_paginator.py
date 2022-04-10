# yatube/tests/test_paginator.py
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group

User = get_user_model()


class ViewsPaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Unit1')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.posts = []
        POST_COUNT = 13
        for i in range(0, POST_COUNT):
            cls.posts.append(Post(
                text=f'Тестовый пост {i}',
                author=cls.author,
                group=cls.group))
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='User1')

    def test_first_page_contains_ten_records(self):
        urls_names = {
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.author})
        }
        POST_CNT_IN_1_PAGE = 10
        for test_url in urls_names:
            response = self.guest_client.get(test_url)
            self.assertEqual(
                len(response.context['page_obj']),
                POST_CNT_IN_1_PAGE)

    def test_first_page_contains_three_records(self):
        urls_names = {
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.author})
        }
        POST_CNT_DIFF = 3
        for test_url in urls_names:
            response = self.guest_client.get(test_url + '?page=2')
            self.assertEqual(len(response.context['page_obj']), POST_CNT_DIFF)
