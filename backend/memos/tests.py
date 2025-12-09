from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Memo

User = get_user_model()


class MemoModelTest(TestCase):
    """Test the Memo model"""
    
    def setUp(self):
        """Set up test user"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_create_memo(self):
        """Test creating a memo"""
        memo = Memo.objects.create(
            content='Test memo content',
            owner=self.user
        )
        self.assertEqual(memo.content, 'Test memo content')
        self.assertEqual(memo.owner, self.user)
        self.assertFalse(memo.is_completed)
        self.assertIsNotNone(memo.created_at)
        self.assertIsNotNone(memo.updated_at)
    
    def test_memo_str_method(self):
        """Test memo string representation"""
        memo = Memo.objects.create(
            content='Test memo',
            owner=self.user
        )
        self.assertIn(self.user.username, str(memo))
        self.assertIn('Test memo', str(memo))
    
    def test_memo_is_completed_default(self):
        """Test that is_completed defaults to False"""
        memo = Memo.objects.create(
            content='Test',
            owner=self.user
        )
        self.assertFalse(memo.is_completed)
    
    def test_memo_ordering(self):
        """Test that memos are ordered by created_at descending"""
        memo1 = Memo.objects.create(content='First', owner=self.user)
        memo2 = Memo.objects.create(content='Second', owner=self.user)
        memos = list(Memo.objects.all())
        self.assertEqual(memos[0], memo2)
        self.assertEqual(memos[1], memo1)
