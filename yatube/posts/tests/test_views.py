# yatube/tests/test_views.py
import tempfile
import shutil


from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Post, Group, Follow

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
image_gif = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ViewsPagesTests(TestCase):
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
            image=SimpleUploadedFile(
                name='small.gif',
                content=image_gif,
                content_type='image/gif'
            )
        )
        cls.follow_user = User.objects.create_user(
            username='Подписавшийся user'
        )
        cls.unfollow_user = User.objects.create_user(
            username='Отписавшийся user'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='User1')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(ViewsPagesTests.user)

    def test_uses_correct_template_pages(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': ViewsPagesTests.user}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': ViewsPagesTests.post.id}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': ViewsPagesTests.post.id}
            ): 'posts/create_post.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_show_correct_context_index_group_list_profile(self):
        """
        Шаблоны index, group_list, profile  сформированы
        с правильным контекстом.
        """
        reverse_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse(
                'posts:profile',
                kwargs={'username': ViewsPagesTests.user}
            ),
        ]
        for reverse_name in reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                object = response.context['page_obj'][0]
                test_text = object.text
                test_author = object.author
                test_group = object.group
                test_pub_date = object.pub_date
                test_post_id = object.id
                test_image = object.image
                self.assertEqual(test_text, self.post.text)
                self.assertEqual(test_author, ViewsPagesTests.user)
                self.assertEqual(test_group, self.group)
                self.assertEqual(test_pub_date, self.post.pub_date)
                self.assertEqual(test_post_id, self.post.id)
                self.assertEqual(test_image, self.post.image)

    def test_show_correct_context_group_list(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        object = response.context['group']
        self.assertEqual(object, self.group)

    def test_show_correct_context_profile(self):
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': ViewsPagesTests.user}
            )
        )
        object = response.context['author']
        self.assertEqual(object, ViewsPagesTests.user)

    def test_show_correct_context_post_create_form(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_show_correct_context_post_edit(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.author_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': ViewsPagesTests.post.id}
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_show_correct_context_is_edit_in_post_edit(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.author_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': ViewsPagesTests.post.id}
        ))
        form_field = response.context.get('is_edit')
        self.assertTrue(form_field)

    def test_show_correct_context_post_detail(self):
        """Шаблоны post_detail сформированы с правильным контекстом."""
        with self.subTest('posts:post_detail'):
            object = self.post
            test_text = object.text
            test_author = object.author
            test_group = object.group
            test_pub_date = object.pub_date
            test_image = object.image
            self.assertEqual(test_text, self.post.text)
            self.assertEqual(test_author, ViewsPagesTests.user)
            self.assertEqual(test_group, self.group)
            self.assertEqual(test_pub_date, self.post.pub_date)
            self.assertEqual(test_image, ViewsPagesTests.post.image)

    def test_cashe_index_page(self):
        response_1 = self.authorized_client.get(reverse('posts:index'))
        form_data = {
            'text': 'Тестовый текст cache',
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertNotContains(response_1, 'Тестовый текст cache')
        cache.clear()
        response_2 = self.authorized_client.get(reverse('posts:index'))
        self.assertContains(response_2, 'Тестовый текст cache')

    def test_following(self):
        follower_cnt = Follow.objects.count()
        self.authorized_client.post(
            reverse('posts:profile_follow', args=[ViewsPagesTests.user])
        )
        self.assertEqual(Follow.objects.count(), follower_cnt + 1)

    def test_unfollowing(self):
        self.authorized_client.post(
            reverse('posts:profile_follow', args=[ViewsPagesTests.user])
        )
        follower_cnt = Follow.objects.count()
        self.authorized_client.post(
            reverse('posts:profile_unfollow', args=[ViewsPagesTests.user])
        )
        self.assertEqual(Follow.objects.count(), follower_cnt - 1)

    def test_followers_see_followed_author_post(self):
        """Новая запись пользователя появляется в ленте тех, кто на него
        подписан"""
        follow_user = ViewsPagesTests.follow_user

        Follow.objects.create(
            author=ViewsPagesTests.user,
            user=follow_user
        )
        authorized_subscribed = Client()
        authorized_subscribed.force_login(follow_user)
        response_subscribed = authorized_subscribed.get(
            reverse('posts:follow_index')
        )
        page_object = response_subscribed.context['page_obj'][0]
        self.assertEqual(page_object.text, ViewsPagesTests.post.text)

    def test_unfollowers_dont_see_author_posts(self):
        """Новая запись пользователя не появляется в ленте тех, кто на него
        не подписан"""
        follow_user = ViewsPagesTests.follow_user
        unfollow_user = ViewsPagesTests.unfollow_user
        Follow.objects.create(
            author=ViewsPagesTests.user,
            user=unfollow_user
        )
        Post.objects.create(
            text='Пост третьего пользователя',
            author=follow_user,
        )
        authorized_unsubscribed = Client()
        authorized_unsubscribed.force_login(unfollow_user)
        response_unsubscribed = authorized_unsubscribed.get(
            reverse('posts:follow_index')
        )
        page_object_unsub = response_unsubscribed.context['page_obj'][0]
        self.assertEqual(page_object_unsub.text, ViewsPagesTests.post.text)
