import markdown
from django.contrib.auth.models import User
from django.template.defaultfilters import truncatewords_html
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils import timezone
from taggit.models import Tag

from .feeds import LatestPostsFeed
from .forms import CommentForm, SearchForm, EmailPostForm
from .models import Post
from .sitemaps import PostSitemap
from .views import post_list, post_detail, post_share, post_comment, post_search


class BlogViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpass',
                                             first_name='Test User name', email='Test@gmail.com')
        self.tag = Tag.objects.create(name='Test Tag')
        self.post = Post.objects.create(title='Test Post', slug='test-post', body='Test Body', author=self.user,
                                        status='PB', publish=timezone.now())
        self.post.tags.add(self.tag)

    def tearDown(self):
        self.user.delete()
        self.tag.delete()
        self.post.delete()

    def test_post_list_view(self):
        request = self.factory.get(reverse('blog:post_list'))
        request.user = self.user
        response = post_list(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')
        self.assertContains(response, 'Test Body')

    def test_post_list_view_with_tag(self):
        request = self.factory.get(reverse('blog:post_list_by_tag', args=[self.tag.slug]))
        request.user = self.user
        response = post_list(request, tag_slug=self.tag.slug)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')
        self.assertContains(response, 'Test Body')
        self.assertContains(response, 'Test Tag')

    def test_post_detail_view(self):
        request = self.factory.get(reverse('blog:post_detail', args=[self.post.publish.year,
                                                                     self.post.publish.month,
                                                                     self.post.publish.day,
                                                                     self.post.slug]))
        request.user = self.user
        response = post_detail(request, self.post.publish.year, self.post.publish.month, self.post.publish.day,
                               self.post.slug)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')

    def test_post_share_view(self):
        data = {'name': self.user.first_name, 'email': self.user.email,
                'to': 'example@gmail.com', 'body': 'Check this post out'}
        request = self.factory.post(reverse('blog:post_share', args=[self.post.id]),
                                    data=data)
        form = EmailPostForm(data=data)
        request.user = self.user
        response = post_share(request, post_id=self.post.id)

        self.assertTrue(form.is_valid())
        self.assertEqual(response.status_code, 200)

    def test_post_comment_view(self):
        data = {'name': self.user.first_name, 'email': self.user.email, 'body': 'Test Body'}
        form = CommentForm(data=data)
        request = self.factory.post(reverse('blog:post_comment', args=[self.post.id]), data)
        request.user = self.user
        response = post_comment(request, post_id=self.post.id)

        self.assertTrue(form.is_valid())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.post.comments.count(), 1)

    def test_post_search_view(self):
        request = self.factory.post(reverse('blog:post_search'), {'query': 'Test Post'})
        request.user = self.user
        form = SearchForm(data={'query': 'Test Query'})
        response = post_search(request)

        self.assertTrue((form.is_valid()))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')


class FeedTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.posts = [
            Post.objects.create(title=f'Test Post {i}', slug=f'test-post-{i}', body='Test Body', author=self.user,
                                status='PB', publish=timezone.now())
            for i in range(10)
        ]

    def tearDown(self):
        self.user.delete()
        for post in self.posts:
            post.delete()

    def test_items(self):
        feed = LatestPostsFeed()
        self.assertEqual(list(feed.items()), self.posts[::-1][:5])

    def test_item_title(self):
        feed = LatestPostsFeed()
        for post in self.posts[:5]:
            self.assertEqual(feed.item_title(post), post.title)

    def test_item_description(self):
        feed = LatestPostsFeed()
        for post in self.posts[::-1][:5]:
            self.assertEqual(feed.item_description(post), truncatewords_html(markdown.markdown(post.body), 30))

    def test_item_pubdate(self):
        feed = LatestPostsFeed()
        for post in self.posts[::-1][:5]:
            self.assertEqual(feed.item_pubdate(post), post.publish)


class SiteMapsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.posts = [
            Post.objects.create(title=f'Test Post {i}', slug=f'test-post-{i}', body='Test Body', author=self.user,
                                status='PB', publish=timezone.now())
            for i in range(10)
        ]

    def tearDown(self):
        self.user.delete()
        for post in self.posts:
            post.delete()

    def test_items(self):
        sitemap = PostSitemap()
        self.assertEqual(list(sitemap.items()), self.posts[::-1])

    def test_lastmod(self):
        sitemap = PostSitemap()
        for post in self.posts[::-1]:
            self.assertEqual(sitemap.lastmod(post), post.updated)
