import random
from django.utils import timezone


# 匿名昵称生成器
def generate_anonymous_name():
    """
    生成随机匿名昵称
    格式：某同学A-Z 或 可爱昵称
    """
    
    # 同学编号列表
    student_letters = [chr(i) for i in range(65, 91)]  # A-Z
    
    # 可爱昵称列表
    cute_prefixes = [
        '神秘', '匿名', '隐藏的', '害羞的', '低调的', 
        '沉默的', '安静的', '悄悄的', '小小的', '可爱的'
    ]
    
    cute_animals = [
        '小熊', '企鹅', '猫咪', '兔子', '狐狸', 
        '松鼠', '考拉', '海豚', '熊猫', '小鹿',
        '小狗', '小鸟', '仓鼠', '浣熊', '刺猬'
    ]
    
    # 随机选择生成方式
    choice = random.choice(['student', 'cute'])
    
    if choice == 'student':
        # 生成"某同学X"格式
        letter = random.choice(student_letters)
        return f"某同学{letter}"
    else:
        # 生成可爱昵称格式
        prefix = random.choice(cute_prefixes)
        animal = random.choice(cute_animals)
        return f"{prefix}{animal}"


def should_refresh_anonymous_name(expires_at):
    """
    检查匿名昵称是否需要刷新（是否已过期）
    
    Args:
        expires_at: 昵称过期时间
    
    Returns:
        bool: True 如果需要刷新，False 否则
    """
    if not expires_at:
        return True
    return timezone.now() >= expires_at
