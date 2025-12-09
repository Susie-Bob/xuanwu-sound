# 评价系统 API 文档

## 概述
评价系统提供对教师和食堂窗口的评分和评论功能，支持星级评分、文字评论和标签系统。

## 基础URL
```
http://localhost:8000/api/ratings/
```

## 认证方式
使用JWT认证。评价功能需要实名认证用户。
```
Authorization: ******
```

---

## 标签 API

### 1. 获取标签列表
**端点**: `GET /api/ratings/tags/`

**权限**: 无需认证

**查询参数**:
- `category` - 按分类筛选 (teacher/canteen)

**响应** (200 OK):
```json
{
  "count": 8,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "讲课清晰",
      "category": "TEACHER",
      "category_display": "教师",
      "color": "green",
      "order": 1
    }
  ]
}
```

---

## 教师 API

### 1. 获取教师列表
**端点**: `GET /api/ratings/teachers/`

**权限**: 无需认证

**查询参数**:
- `search` - 搜索教师姓名、院系、课程
- `department` - 按院系筛选
- `ordering` - 排序字段（name, department, created_at）

**响应** (200 OK):
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "张教授",
      "department": "计算机科学与技术学院",
      "title": "教授",
      "courses": "数据结构与算法、操作系统",
      "image": null,
      "average_rating": 4.5,
      "rating_count": 10
    }
  ]
}
```

### 2. 获取教师详情
**端点**: `GET /api/ratings/teachers/{id}/`

**权限**: 无需认证

**响应** (200 OK):
```json
{
  "id": 1,
  "name": "张教授",
  "department": "计算机科学与技术学院",
  "title": "教授",
  "courses": "数据结构与算法、操作系统",
  "bio": "20年教学经验，主要研究方向为算法设计与分析",
  "image": null,
  "email": "zhang@university.edu.cn",
  "office": "计算机楼301",
  "average_rating": 4.5,
  "rating_count": 10,
  "created_at": "2025-12-09T16:02:50.123456+08:00",
  "updated_at": "2025-12-09T16:02:50.123456+08:00"
}
```

### 3. 获取教师评价列表
**端点**: `GET /api/ratings/teachers/{id}/ratings/`

**权限**: 无需认证

**响应** (200 OK):
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": {...},
      "user_display": {...},
      "score": 5,
      "comment": "讲课非常清晰，作业量适中",
      "tags": [1, 2],
      "tags_detail": [
        {"id": 1, "name": "讲课清晰", ...}
      ],
      "is_anonymous": false,
      "helpful_count": 5,
      "is_helpful": false,
      "target_type": "teacher",
      "target_name": "张教授 - 计算机科学与技术学院",
      "created_at": "2025-12-09T16:02:50.123456+08:00",
      "updated_at": "2025-12-09T16:02:50.123456+08:00"
    }
  ]
}
```

### 4. 获取教师评价统计
**端点**: `GET /api/ratings/teachers/{id}/statistics/`

**权限**: 无需认证

**响应** (200 OK):
```json
{
  "average_rating": 4.5,
  "total_ratings": 10,
  "score_distribution": {
    "1星": 0,
    "2星": 1,
    "3星": 2,
    "4星": 3,
    "5星": 4
  },
  "popular_tags": [
    ["讲课清晰", 8],
    ["作业适量", 6],
    ["幽默风趣", 5]
  ]
}
```

### 5. 创建教师（仅管理员）
**端点**: `POST /api/ratings/teachers/`

**权限**: 管理员

**请求体**:
```json
{
  "name": "张教授",
  "department": "计算机科学与技术学院",
  "title": "教授",
  "courses": "数据结构与算法、操作系统",
  "bio": "20年教学经验",
  "email": "zhang@university.edu.cn",
  "office": "计算机楼301"
}
```

---

## 食堂窗口 API

### 1. 获取食堂窗口列表
**端点**: `GET /api/ratings/canteen/`

**权限**: 无需认证

**查询参数**:
- `search` - 搜索窗口名称、食堂、特色菜品
- `building` - 按食堂楼号筛选
- `ordering` - 排序字段（name, canteen_building, created_at）

**响应** (200 OK):
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "川菜窗口",
      "canteen_building": "第一食堂",
      "location": "一楼东侧",
      "specialties": "麻婆豆腐、回锅肉、水煮鱼",
      "image": null,
      "price_range": "10-15元",
      "average_rating": 4.2,
      "rating_count": 15
    }
  ]
}
```

### 2. 获取食堂窗口详情
**端点**: `GET /api/ratings/canteen/{id}/`

**权限**: 无需认证

**响应** (200 OK):
```json
{
  "id": 1,
  "name": "川菜窗口",
  "canteen_building": "第一食堂",
  "location": "一楼东侧",
  "description": "主打川菜，口味地道",
  "specialties": "麻婆豆腐、回锅肉、水煮鱼",
  "image": null,
  "price_range": "10-15元",
  "opening_hours": "7:00-20:00",
  "average_rating": 4.2,
  "rating_count": 15,
  "created_at": "2025-12-09T16:02:50.123456+08:00",
  "updated_at": "2025-12-09T16:02:50.123456+08:00"
}
```

### 3. 获取食堂窗口评价列表
**端点**: `GET /api/ratings/canteen/{id}/ratings/`

**权限**: 无需认证

### 4. 获取食堂窗口评价统计
**端点**: `GET /api/ratings/canteen/{id}/statistics/`

**权限**: 无需认证

---

## 评价 API

### 1. 创建评价
**端点**: `POST /api/ratings/ratings/`

**权限**: 需要认证且实名验证

**请求体**:
```json
{
  "target_type": "teacher",
  "target_id": 1,
  "score": 5,
  "comment": "讲课非常清晰，作业量适中",
  "tags": [1, 2],
  "is_anonymous": false
}
```

或者评价食堂:
```json
{
  "target_type": "canteen",
  "target_id": 1,
  "score": 4,
  "comment": "菜品很好吃，价格合理",
  "tags": [5, 6],
  "is_anonymous": false
}
```

**响应** (201 Created):
```json
{
  "id": 1,
  "user": {...},
  "user_display": {...},
  "score": 5,
  "comment": "讲课非常清晰，作业量适中",
  "tags": [1, 2],
  "tags_detail": [...],
  "is_anonymous": false,
  "helpful_count": 0,
  "is_helpful": false,
  "target_type": "teacher",
  "target_name": "张教授 - 计算机科学与技术学院",
  "created_at": "2025-12-09T16:02:50.123456+08:00",
  "updated_at": "2025-12-09T16:02:50.123456+08:00"
}
```

### 2. 更新评价
**端点**: `PATCH /api/ratings/ratings/{id}/`

**权限**: 需要认证（仅作者）

**请求体**:
```json
{
  "score": 4,
  "comment": "更新后的评论",
  "tags": [1, 3]
}
```

### 3. 删除评价
**端点**: `DELETE /api/ratings/ratings/{id}/`

**权限**: 需要认证（仅作者或管理员）

**响应** (204 No Content)

### 4. 标记评价为有用
**端点**: `POST /api/ratings/ratings/{id}/mark_helpful/`

**权限**: 需要认证

**响应** (200 OK):
```json
{
  "message": "已标记为有用",
  "marked": true
}
```

或取消标记:
```json
{
  "message": "已取消标记",
  "marked": false
}
```

### 5. 获取我的评价
**端点**: `GET /api/ratings/ratings/my_ratings/`

**权限**: 需要认证

**响应**: 与评价列表格式相同

### 6. 获取评价列表
**端点**: `GET /api/ratings/ratings/`

**权限**: 无需认证

**查询参数**:
- `target_type` - 筛选评价类型 (teacher/canteen)
- `target_id` - 筛选评价对象ID

---

## 权限说明

### 查看权限
- **所有人**: 可以查看教师、食堂、标签、评价列表

### 评价权限
- **实名认证用户**: 可以创建评价、标记有用
- **评价作者**: 可以编辑/删除自己的评价
- **管理员**: 可以删除任何评价

### 管理权限
- **管理员**: 可以创建/编辑/删除教师和食堂信息

---

## 特性

### 实名认证要求
- 只有通过实名认证（`is_verified=True`）的用户才能评价
- 未认证用户会收到错误提示："您需要完成实名认证才能评价"

### 防重复评价
- 每个用户对同一个对象只能评价一次
- 重复评价会返回错误："您已经评价过该对象"

### 匿名评价
- 用户可以选择匿名评价
- 匿名评价显示为"匿名用户"，不显示真实身份

### 标签系统
- 预定义标签，方便快速评价
- 教师标签：讲课清晰、幽默风趣、严格认真、作业适量等
- 食堂标签：菜品美味、分量充足、价格实惠、环境整洁等
- 标签统计显示最受欢迎的评价维度

### 有用标记
- 用户可以标记评价为"有用"
- 系统统计有用数量
- 防止重复标记

### 评分统计
- 自动计算平均评分
- 统计评分分布（1-5星）
- 统计热门标签
- 评价数量统计

---

## 错误响应

### 400 Bad Request
```json
{
  "score": ["评分必须在1到5之间"]
}
```

### 401 Unauthorized
```json
{
  "detail": "身份认证信息未提供。"
}
```

### 403 Forbidden
```json
{
  "detail": "您需要完成实名认证才能评价"
}
```

或

```json
{
  "detail": "您没有权限修改此评价"
}
```

### 404 Not Found
```json
{
  "detail": "未找到。"
}
```

---

## 使用示例

### Python (requests)
```python
import requests

# 获取教师列表
response = requests.get('http://localhost:8000/api/ratings/teachers/')
teachers = response.json()['results']

# 创建评价（需要JWT token）
headers = {'Authorization': '******'}
data = {
    'target_type': 'teacher',
    'target_id': 1,
    'score': 5,
    'comment': '讲课非常清晰',
    'tags': [1, 2],
    'is_anonymous': False
}
response = requests.post(
    'http://localhost:8000/api/ratings/ratings/',
    json=data,
    headers=headers
)

# 获取统计信息
response = requests.get('http://localhost:8000/api/ratings/teachers/1/statistics/')
stats = response.json()
print(f"平均分: {stats['average_rating']}")
print(f"评价数: {stats['total_ratings']}")
```
