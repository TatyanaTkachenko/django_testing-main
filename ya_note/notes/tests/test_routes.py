from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.other_user = User.objects.create(username='Другой пользователь')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='Slug',
            author=cls.author
        )

    def test_pages_availability(self):
        routes = [
            (reverse('notes:home'), None, self.client, HTTPStatus.OK),
            (reverse('users:signup'), None, self.client, HTTPStatus.OK),
            (reverse('users:login'), None, self.client, HTTPStatus.OK),
            (reverse('users:logout'), None, self.client, HTTPStatus.OK),
            (reverse('notes:list'), None, self.author, HTTPStatus.OK),
            (reverse('notes:add'), None, self.author, HTTPStatus.OK),
            (reverse('notes:success'), None, self.author, HTTPStatus.OK),
            (reverse('notes:detail'), (self.note.slug,), self.author,
             HTTPStatus.OK),
            (reverse('notes:edit'), (self.note.slug,), self.author,
             HTTPStatus.OK),
            (reverse('notes:delete'), (self.note.slug,), self.author,
             HTTPStatus.OK),
            (reverse('notes:detail'), (self.note.slug,),
             self.other_user, HTTPStatus.NOT_FOUND),
            (reverse('notes:edit'), (self.note.slug,),
             self.other_user, HTTPStatus.NOT_FOUND),
            (reverse('notes:delete'), (self.note.slug,),
             self.other_user, HTTPStatus.NOT_FOUND),
        ]

        for name, args, user, expected_status in routes:
            if user != self.client:
                self.client.force_login(user)
            url = (name, args)
            with self.subTest(name=name, user=user):
                response = self.client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_redirect_for_anon(self):
        login_url = reverse('users:login')
        urls = (
            (reverse('notes:detail'), (self.note.slug,)),
            (reverse('notes:edit'), (self.note.slug,)),
            (reverse('notes:delete'), (self.note.slug,)),
            (reverse('notes:add'), None),
            (reverse('notes:success'), None),
            (reverse('notes:list'), None)
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = (name, args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
