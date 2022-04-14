from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        help_texts = {
            'group': 'Группа, к которой будет относиться пост',
            'text': 'Введите текст поста',
            'image': 'Выберите картинку'
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        # Работаю на доп заданием, изучаю материалы,
        # но пока не совсем то что нужно((
