# yatube/posts/tests/test_forms.py
import shutil
import tempfile
import datetime

from http.client import OK

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Post, Group, Comment


User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='User1')
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_slug",
            description="Тестовое описание"
        )
        cls.post = Post.objects.create(
            text='Текст тестового поста',
            pub_date=datetime.datetime.now(),
            author=PostCreateFormTest.user,
            group=PostCreateFormTest.group,
            image=SimpleUploadedFile(
                name='small.gif',
                content=(
                    b'\x47\x49\x46\x38\x39\x61\x02\x00'
                    b'\x01\x00\x80\x00\x00\x00\x00\x00'
                    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                    b'\x0A\x00\x3B'
                ),
                content_type='image/gif'
            )
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user_author = User.objects.create_user(username='Unit1')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.user_author)

    def test_post_create(self):
        '''Проверка создания поста'''
        post_count = Post.objects.count()
        form_data = {
            'text': 'Текст формы',
            'group': PostCreateFormTest.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        error_1 = 'Ошибка добавления в БД'
        self.assertEqual(
            Post.objects.count(),
            post_count + 1,
            error_1
        )
        error_2 = 'Ошибка совпадения'
        self.assertEqual(response.status_code, OK)
        self.assertTrue(
            Post.objects.filter(
                text='Текст формы',
                group=PostCreateFormTest.group.id,
                author=PostCreateFormTest.user,
            ).exists(),
            error_2
        )

    def test_post_create_without_group(self):
        post_count = Post.objects.count()
        new_post_create = self.authorized_client.post(
            reverse('posts:post_create'),
            data={
                'text': 'Test text post',
            },
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        post_exist = Post.objects.filter(
            text='Test text post',
            group=PostCreateFormTest.group,
            author=PostCreateFormTest.user
        ).exists()
        self.assertEqual(post_exist, False)
        self.assertEqual(new_post_create.status_code, OK)

    def test_post_create_for_guest_user(self):
        post_count = Post.objects.count()
        new_post_create = self.guest_client.post(
            reverse('posts:post_create'),
            data={
                'text': 'Test text',
                'group': PostCreateFormTest.group.id,
            }
        )
        self.assertEqual(Post.objects.count(), post_count)
        login_url = reverse('users:login')
        new_post_url = reverse('posts:post_create')
        redirect_url = f'{login_url}?next={new_post_url}'
        self.assertRedirects(
            new_post_create,
            redirect_url
        )

    def test_post_edit_with_text_and_group(self):
        """
        Проверка редактирования поста с изменением
        текста и группы.
        """
        data = {
            'text': 'Редактированные текст и группа',
            'group': PostCreateFormTest.group.id
        }
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                author=PostCreateFormTest.user,
                pub_date=PostCreateFormTest.post.pub_date,
                text='Редактированные текст и группа',
                group=PostCreateFormTest.group.id
            ).exists()
        )

    def test_post_edit_with_text_and_without_group(self):
        """
        Проверка редактирования поста с изменением
        текста и без изменения группы.
        """
        data = {
            'text': 'Редактированный текст без изменения группы',
            'group': PostCreateFormTest.group.id,
        }
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                author=PostCreateFormTest.user,
                pub_date=PostCreateFormTest.post.pub_date,
                text='Редактированный текст без изменения группы',
                group=PostCreateFormTest.group.id
            ).exists()
        )

    def test_comment_create(self):
        coms_cnt = Comment.objects.count()
        form_data = {
            'text': 'Текст комментария',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(Comment.objects.count(), coms_cnt + 1)
        self.assertTrue(
            Comment.objects.filter(text='Текст комментария',).exists()
        )
