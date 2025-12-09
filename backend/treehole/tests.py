from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from .models import TreeholePost, TreeholeComment, TreeholeLike
from .utils import generate_anonymous_name, should_refresh_anonymous_name

User = get_user_model()


class AnonymousNameGeneratorTests(TestCase):
    """测试匿名昵称生成器"""
    
    def test_generate_anonymous_name(self):
        """测试生成匿名昵称"""
        name = generate_anonymous_name()
        self.assertIsNotNone(name)
        self.assertIsInstance(name, str)
        self.assertGreater(len(name), 0)
    
    def test_generate_multiple_names(self):
        """测试生成多个不同的昵称"""
        names = [generate_anonymous_name() for _ in range(10)]
        # At least some should be different
        self.assertGreater(len(set(names)), 1)
    
    def test_should_refresh_anonymous_name_expired(self):
        """测试过期昵称检测"""
        expired_time = timezone.now() - timedelta(hours=1)
        self.assertTrue(should_refresh_anonymous_name(expired_time))
    
    def test_should_refresh_anonymous_name_not_expired(self):
        """测试未过期昵称检测"""
        future_time = timezone.now() + timedelta(hours=1)
        self.assertFalse(should_refresh_anonymous_name(future_time))
    
    def test_should_refresh_anonymous_name_none(self):
        """测试None值处理"""
        self.assertTrue(should_refresh_anonymous_name(None))


class TreeholePostModelTests(TestCase):
    """测试树洞帖子模型"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_create_post(self):
        """测试创建帖子"""
        post = TreeholePost.objects.create(
            author=self.user,
            content='测试内容',
            anonymous_name='某同学A',
            post_type='MOOD'
        )
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.content, '测试内容')
        self.assertEqual(post.anonymous_name, '某同学A')
        self.assertIsNotNone(post.anonymous_name_expires)
    
    def test_post_auto_set_expiration(self):
        """测试帖子自动设置过期时间"""
        post = TreeholePost.objects.create(
            author=self.user,
            content='测试内容',
            anonymous_name='某同学A'
        )
        self.assertIsNotNone(post.anonymous_name_expires)
        # Should expire in about 24 hours
        time_diff = post.anonymous_name_expires - timezone.now()
        self.assertGreater(time_diff.total_seconds(), 23 * 3600)
        self.assertLess(time_diff.total_seconds(), 25 * 3600)


class TreeholeCommentModelTests(TestCase):
    """测试树洞评论模型"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.post = TreeholePost.objects.create(
            author=self.user,
            content='测试帖子',
            anonymous_name='某同学A'
        )
    
    def test_create_comment(self):
        """测试创建评论"""
        comment = TreeholeComment.objects.create(
            post=self.post,
            author=self.user,
            content='测试评论',
            anonymous_name='某同学B'
        )
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.content, '测试评论')
    
    def test_comment_auto_set_expiration(self):
        """测试评论自动设置过期时间"""
        comment = TreeholeComment.objects.create(
            post=self.post,
            author=self.user,
            content='测试评论',
            anonymous_name='某同学B'
        )
        self.assertIsNotNone(comment.anonymous_name_expires)


class TreeholeLikeModelTests(TestCase):
    """测试树洞点赞模型"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.post = TreeholePost.objects.create(
            author=self.user,
            content='测试帖子',
            anonymous_name='某同学A'
        )
    
    def test_like_post(self):
        """测试点赞帖子"""
        like = TreeholeLike.objects.create(
            user=self.user,
            post=self.post
        )
        self.assertEqual(like.user, self.user)
        self.assertEqual(like.post, self.post)
        self.assertIsNone(like.comment)


class TreeholeAPITests(TestCase):
    """测试树洞API接口"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_post_authenticated(self):
        """测试认证用户创建帖子"""
        data = {
            'content': '测试树洞帖子',
            'post_type': 'MOOD',
            'images': []
        }
        response = self.client.post('/api/treehole/posts/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('anonymous_name', response.data)
        self.assertEqual(response.data['content'], '测试树洞帖子')
    
    def test_create_post_unauthenticated(self):
        """测试未认证用户无法创建帖子"""
        self.client.force_authenticate(user=None)
        data = {
            'content': '测试树洞帖子',
            'post_type': 'MOOD'
        }
        response = self.client.post('/api/treehole/posts/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_posts(self):
        """测试获取帖子列表"""
        TreeholePost.objects.create(
            author=self.user,
            content='测试帖子1',
            anonymous_name='某同学A'
        )
        TreeholePost.objects.create(
            author=self.user,
            content='测试帖子2',
            anonymous_name='某同学B'
        )
        
        response = self.client.get('/api/treehole/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_delete_own_post(self):
        """测试删除自己的帖子"""
        post = TreeholePost.objects.create(
            author=self.user,
            content='测试帖子',
            anonymous_name='某同学A'
        )
        response = self.client.delete(f'/api/treehole/posts/{post.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TreeholePost.objects.filter(id=post.id).exists())
    
    def test_cannot_delete_others_post(self):
        """测试无法删除他人帖子"""
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        post = TreeholePost.objects.create(
            author=other_user,
            content='他人的帖子',
            anonymous_name='某同学B'
        )
        response = self.client.delete(f'/api/treehole/posts/{post.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_like_post(self):
        """测试点赞帖子"""
        post = TreeholePost.objects.create(
            author=self.user,
            content='测试帖子',
            anonymous_name='某同学A'
        )
        response = self.client.post(f'/api/treehole/posts/{post.id}/like/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['liked'])
    
    def test_unlike_post(self):
        """测试取消点赞帖子"""
        post = TreeholePost.objects.create(
            author=self.user,
            content='测试帖子',
            anonymous_name='某同学A'
        )
        # First like
        TreeholeLike.objects.create(user=self.user, post=post)
        # Then unlike
        response = self.client.post(f'/api/treehole/posts/{post.id}/like/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['liked'])
    
    def test_create_comment(self):
        """测试创建评论"""
        post = TreeholePost.objects.create(
            author=self.user,
            content='测试帖子',
            anonymous_name='某同学A'
        )
        data = {
            'post': post.id,
            'content': '测试评论'
        }
        response = self.client.post('/api/treehole/comments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('anonymous_name', response.data)
    
    def test_hidden_posts_not_shown(self):
        """测试隐藏的帖子不显示"""
        TreeholePost.objects.create(
            author=self.user,
            content='正常帖子',
            anonymous_name='某同学A'
        )
        TreeholePost.objects.create(
            author=self.user,
            content='隐藏帖子',
            anonymous_name='某同学B',
            is_hidden=True
        )
        
        response = self.client.get('/api/treehole/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['content'], '正常帖子')
