# 论坛模块 API 文档

## 概述
论坛模块提供完整的社区讨论功能，包括分类、帖子、评论和点赞。

## 基础URL
```
http://localhost:8000/api/forum/
```

## 认证方式
使用JWT认证。在需要认证的接口请求头中添加：
```
Authorization: ******
```

---

## 分类 API

### 1. 获取分类列表
**端点**: `GET /api/forum/categories/`

**权限**: 无需认证

**响应** (200 OK):
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "学习交流",
      "description": "分享学习心得和资料",
      "icon": "book",
      "order": 1,
      "post_count": 10,
      "created_at": "2025-12-09T15:40:29.056750+08:00"
    }
  ]
}
```

### 2. 创建分类（仅管理员）
**端点**: `POST /api/forum/categories/`

**权限**: 管理员

**请求体**:
```json
{
  "name": "学习交流",
  "description": "分享学习心得和资料",
  "icon": "book",
  "order": 1
}
```

---

## 帖子 API

### 1. 获取帖子列表
**端点**: `GET /api/forum/posts/`

**权限**: 无需认证

**查询参数**:
- `category` - 按分类ID筛选
- `author` - 按作者ID筛选
- `search` - 搜索标题和内容
- `ordering` - 排序字段（created_at, view_count, updated_at）
- `page` - 页码

**响应** (200 OK):
```json
{
  "count": 20,
  "next": "http://localhost:8000/api/forum/posts/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "分享一下数据结构学习心得",
      "author": {
        "id": 1,
        "username": "forumuser",
        "real_name": "论坛测试用户"
      },
      "category": 1,
      "category_name": "学习交流",
      "is_pinned": false,
      "view_count": 10,
      "comment_count": 5,
      "like_count": 3,
      "created_at": "2025-12-09T15:40:56.195379+08:00",
      "updated_at": "2025-12-09T15:40:56.195403+08:00"
    }
  ]
}
```

### 2. 获取帖子详情
**端点**: `GET /api/forum/posts/{id}/`

**权限**: 无需认证

**响应** (200 OK):
```json
{
  "id": 1,
  "title": "分享一下数据结构学习心得",
  "content": "最近在学习数据结构，发现树这一章节特别重要。大家有什么好的学习资料推荐吗？",
  "author": {
    "id": 1,
    "username": "forumuser",
    "real_name": "论坛测试用户"
  },
  "category": 1,
  "category_name": "学习交流",
  "images": [],
  "is_pinned": false,
  "is_locked": false,
  "view_count": 10,
  "comment_count": 2,
  "like_count": 3,
  "is_liked": true,
  "comments": [
    {
      "id": 1,
      "author": {...},
      "content": "我推荐《算法导论》这本书",
      "parent": null,
      "like_count": 2,
      "is_liked": false,
      "replies": [
        {
          "id": 2,
          "content": "感谢推荐！",
          "parent": 1,
          ...
        }
      ],
      "created_at": "2025-12-09T15:41:19.984954+08:00"
    }
  ],
  "created_at": "2025-12-09T15:40:56.195379+08:00",
  "updated_at": "2025-12-09T15:40:56.195403+08:00"
}
```

**说明**: 访问帖子详情会自动增加浏览次数

### 3. 创建帖子
**端点**: `POST /api/forum/posts/`

**权限**: 需要认证

**请求体**:
```json
{
  "title": "分享一下数据结构学习心得",
  "content": "最近在学习数据结构...",
  "category": 1,
  "images": ["url1", "url2"]
}
```

**响应** (201 Created):
```json
{
  "title": "分享一下数据结构学习心得",
  "content": "最近在学习数据结构...",
  "category": 1,
  "images": ["url1", "url2"]
}
```

### 4. 更新帖子
**端点**: `PATCH /api/forum/posts/{id}/`

**权限**: 需要认证（仅作者或管理员）

**请求体**:
```json
{
  "title": "更新后的标题",
  "content": "更新后的内容"
}
```

### 5. 删除帖子
**端点**: `DELETE /api/forum/posts/{id}/`

**权限**: 需要认证（仅作者或管理员）

**响应** (204 No Content)

### 6. 点赞/取消点赞帖子
**端点**: `POST /api/forum/posts/{id}/like/`

**权限**: 需要认证

**响应** (200 OK):
```json
{
  "message": "点赞成功",
  "liked": true
}
```

或

```json
{
  "message": "已取消点赞",
  "liked": false
}
```

### 7. 获取我的帖子
**端点**: `GET /api/forum/posts/my_posts/`

**权限**: 需要认证

**响应**: 与帖子列表格式相同

---

## 评论 API

### 1. 获取评论列表
**端点**: `GET /api/forum/comments/`

**权限**: 无需认证

**查询参数**:
- `post` - 按帖子ID筛选

**响应** (200 OK):
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "post": 1,
      "author": {...},
      "content": "我推荐《算法导论》这本书",
      "parent": null,
      "like_count": 2,
      "is_liked": false,
      "replies": [...],
      "created_at": "2025-12-09T15:41:19.984954+08:00",
      "updated_at": "2025-12-09T15:41:19.984979+08:00"
    }
  ]
}
```

### 2. 创建评论
**端点**: `POST /api/forum/comments/`

**权限**: 需要认证

**请求体**:
```json
{
  "post": 1,
  "content": "这是一条评论",
  "parent": null
}
```

**回复评论**:
```json
{
  "post": 1,
  "content": "这是一条回复",
  "parent": 1
}
```

**响应** (201 Created):
```json
{
  "id": 1,
  "post": 1,
  "author": {...},
  "content": "这是一条评论",
  "parent": null,
  "like_count": 0,
  "is_liked": false,
  "replies": [],
  "created_at": "2025-12-09T15:41:19.984954+08:00",
  "updated_at": "2025-12-09T15:41:19.984979+08:00"
}
```

### 3. 更新评论
**端点**: `PATCH /api/forum/comments/{id}/`

**权限**: 需要认证（仅作者）

**请求体**:
```json
{
  "content": "更新后的评论内容"
}
```

### 4. 删除评论
**端点**: `DELETE /api/forum/comments/{id}/`

**权限**: 需要认证（仅作者或管理员）

**响应** (204 No Content)

### 5. 点赞/取消点赞评论
**端点**: `POST /api/forum/comments/{id}/like/`

**权限**: 需要认证

**响应** (200 OK):
```json
{
  "message": "点赞成功",
  "liked": true
}
```

---

## 特性

### 嵌套评论
评论支持多级嵌套回复：
- 顶级评论的 `parent` 为 `null`
- 回复评论时设置 `parent` 为要回复的评论ID
- 在帖子详情中，顶级评论的 `replies` 字段包含所有回复

### 点赞系统
- 支持对帖子和评论点赞
- 同一用户对同一内容只能点赞一次
- 再次点赞会取消之前的点赞

### 权限控制
- **查看**: 所有人可以查看帖子、评论、分类
- **发帖/评论**: 需要登录认证
- **编辑/删除**: 仅作者本人或管理员
- **管理分类**: 仅管理员

### 搜索和筛选
- 支持按标题和内容搜索帖子
- 支持按分类、作者筛选
- 支持按创建时间、浏览次数、更新时间排序
- 支持分页（默认20条/页）

---

## 数据模型

### Category（分类）
- `id` - 分类ID
- `name` - 分类名称（唯一）
- `description` - 分类描述
- `icon` - 图标名称
- `order` - 排序序号
- `created_at` - 创建时间

### Post（帖子）
- `id` - 帖子ID
- `title` - 标题
- `content` - 内容
- `author` - 作者（外键到User）
- `category` - 分类（外键到Category）
- `images` - 图片列表（JSON字段）
- `is_pinned` - 是否置顶
- `is_locked` - 是否锁定
- `view_count` - 浏览次数
- `created_at` - 创建时间
- `updated_at` - 更新时间

### Comment（评论）
- `id` - 评论ID
- `post` - 所属帖子（外键到Post）
- `author` - 作者（外键到User）
- `content` - 内容
- `parent` - 父评论（外键到Comment，自引用）
- `created_at` - 创建时间
- `updated_at` - 更新时间

### Like（点赞）
- `id` - 点赞ID
- `user` - 用户（外键到User）
- `content_type` - 内容类型（Post或Comment）
- `object_id` - 对象ID
- `created_at` - 创建时间

---

## 错误响应

### 400 Bad Request
```json
{
  "title": ["标题不能为空"]
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
  "detail": "您没有权限修改此帖子"
}
```

### 404 Not Found
```json
{
  "detail": "未找到。"
}
```
