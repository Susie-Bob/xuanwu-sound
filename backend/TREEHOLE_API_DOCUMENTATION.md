# 树洞 API 文档

## 概述

树洞模块提供匿名发帖、评论和点赞功能。用户可以在树洞中匿名分享心情、表白或吐槽，系统会为每个用户生成随机昵称，24小时后自动更新。

**基础路径**: `/api/treehole/`

**认证方式**: JWT Token (Bearer Token)

## 核心特性

- ✅ 完全匿名发帖（前台显示随机昵称）
- ✅ 后台实名记录（管理员可见真实作者）
- ✅ 每24小时自动刷新匿名昵称
- ✅ 支持帖子类型分类（表白/吐槽/心情/其他）
- ✅ 支持多图上传（最多9张）
- ✅ 支持点赞和评论
- ✅ 支持楼中楼回复
- ✅ 管理员可折叠违规内容

## API 接口

### 1. 帖子相关接口

#### 1.1 获取帖子列表

```http
GET /api/treehole/posts/
```

**查询参数**:
- `post_type` (可选): 帖子类型筛选 (`CONFESSION`, `COMPLAINT`, `MOOD`, `OTHER`)
- `search` (可选): 搜索内容关键词
- `ordering` (可选): 排序字段 (`created_at`, `-created_at`, `likes_count`, `-likes_count`, `comments_count`, `-comments_count`)
- `page` (可选): 页码，默认为 1
- `page_size` (可选): 每页数量，默认为 20

**响应示例**:
```json
{
  "count": 100,
  "next": "http://example.com/api/treehole/posts/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "anonymous_name": "神秘小熊",
      "content": "今天心情很好，想和大家分享...",
      "post_type": "MOOD",
      "post_type_display": "心情",
      "likes_count": 15,
      "comments_count": 8,
      "created_at": "2024-01-01T12:00:00Z",
      "is_hidden": false
    }
  ]
}
```

#### 1.2 发布帖子

```http
POST /api/treehole/posts/
```

**请求体**:
```json
{
  "content": "帖子内容...",
  "images": ["图片URL1", "图片URL2"],
  "post_type": "MOOD"
}
```

**字段说明**:
- `content` (必填): 帖子内容
- `images` (可选): 图片URL列表，最多9张
- `post_type` (可选): 帖子类型，默认为 `OTHER`
  - `CONFESSION`: 表白
  - `COMPLAINT`: 吐槽
  - `MOOD`: 心情
  - `OTHER`: 其他

**响应示例**:
```json
{
  "id": 1,
  "anonymous_name": "某同学A",
  "content": "帖子内容...",
  "images": ["图片URL1", "图片URL2"],
  "post_type": "MOOD",
  "post_type_display": "心情",
  "likes_count": 0,
  "comments_count": 0,
  "is_liked": false,
  "comments": [],
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "is_hidden": false
}
```

#### 1.3 获取帖子详情

```http
GET /api/treehole/posts/{id}/
```

**响应示例**:
```json
{
  "id": 1,
  "anonymous_name": "神秘小熊",
  "content": "帖子内容...",
  "images": ["图片URL1"],
  "post_type": "MOOD",
  "post_type_display": "心情",
  "likes_count": 15,
  "comments_count": 8,
  "is_liked": true,
  "comments": [
    {
      "id": 1,
      "post": 1,
      "anonymous_name": "某同学B",
      "content": "评论内容...",
      "parent": null,
      "likes_count": 3,
      "is_liked": false,
      "replies": [
        {
          "id": 2,
          "post": 1,
          "anonymous_name": "隐藏的猫咪",
          "content": "回复内容...",
          "parent": 1,
          "likes_count": 1,
          "is_liked": false,
          "replies": [],
          "created_at": "2024-01-01T12:30:00Z",
          "is_hidden": false
        }
      ],
      "created_at": "2024-01-01T12:15:00Z",
      "is_hidden": false
    }
  ],
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "is_hidden": false
}
```

#### 1.4 删除帖子

```http
DELETE /api/treehole/posts/{id}/
```

**权限**: 仅作者本人或管理员可删除

**响应**: 204 No Content

#### 1.5 点赞/取消点赞帖子

```http
POST /api/treehole/posts/{id}/like/
```

**响应示例**:
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

#### 1.6 获取帖子评论

```http
GET /api/treehole/posts/{id}/comments/
```

**响应示例**:
```json
[
  {
    "id": 1,
    "post": 1,
    "anonymous_name": "某同学C",
    "content": "评论内容...",
    "parent": null,
    "likes_count": 5,
    "is_liked": true,
    "replies": [],
    "created_at": "2024-01-01T12:20:00Z",
    "is_hidden": false
  }
]
```

### 2. 评论相关接口

#### 2.1 发表评论

```http
POST /api/treehole/comments/
```

**请求体**:
```json
{
  "post": 1,
  "content": "评论内容...",
  "parent": null
}
```

**字段说明**:
- `post` (必填): 帖子ID
- `content` (必填): 评论内容
- `parent` (可选): 父评论ID，用于楼中楼回复

**响应示例**:
```json
{
  "id": 1,
  "post": 1,
  "anonymous_name": "匿名企鹅",
  "content": "评论内容...",
  "parent": null,
  "likes_count": 0,
  "is_liked": false,
  "replies": [],
  "created_at": "2024-01-01T12:20:00Z",
  "is_hidden": false
}
```

#### 2.2 删除评论

```http
DELETE /api/treehole/comments/{id}/
```

**权限**: 仅作者本人或管理员可删除

**响应**: 204 No Content

#### 2.3 点赞/取消点赞评论

```http
POST /api/treehole/comments/{id}/like/
```

**响应示例**:
```json
{
  "message": "点赞成功",
  "liked": true
}
```

## 匿名机制说明

### 前台匿名
- 所有帖子和评论在前端显示随机生成的匿名昵称
- 昵称格式：
  - "某同学A-Z"（如：某同学A、某同学B）
  - 可爱昵称（如：神秘小熊、匿名企鹅、隐藏的猫咪）

### 后台实名
- 数据库中完整记录真实用户ID
- 管理员可在后台查看真实作者信息
- 用于法律合规和内容审查

### 昵称刷新机制
- 每个帖子和评论的匿名昵称有24小时有效期
- 24小时后系统自动重新生成新的随机昵称
- 防止通过昵称追踪用户身份

## 权限说明

| 操作 | 游客 | 登录用户 | 作者 | 管理员 |
|------|------|----------|------|--------|
| 查看帖子列表 | ✅ | ✅ | ✅ | ✅ |
| 查看帖子详情 | ✅ | ✅ | ✅ | ✅ |
| 发布帖子 | ❌ | ✅ | ✅ | ✅ |
| 删除帖子 | ❌ | ❌ | ✅ | ✅ |
| 点赞帖子 | ❌ | ✅ | ✅ | ✅ |
| 发表评论 | ❌ | ✅ | ✅ | ✅ |
| 删除评论 | ❌ | ❌ | ✅ | ✅ |
| 点赞评论 | ❌ | ✅ | ✅ | ✅ |
| 折叠内容 | ❌ | ❌ | ❌ | ✅ |
| 查看真实作者 | ❌ | ❌ | ❌ | ✅ |

## 错误码说明

| HTTP状态码 | 说明 |
|-----------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 204 | 删除成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |

## 使用示例

### 发布匿名帖子

```bash
curl -X POST http://example.com/api/treehole/posts/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "今天想匿名表白一下隔壁班的TA...",
    "post_type": "CONFESSION",
    "images": []
  }'
```

### 发表匿名评论

```bash
curl -X POST http://example.com/api/treehole/comments/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "post": 1,
    "content": "加油！勇敢去表白！",
    "parent": null
  }'
```

### 点赞帖子

```bash
curl -X POST http://example.com/api/treehole/posts/1/like/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 注意事项

1. **认证要求**: 除了查看帖子列表和详情，所有操作都需要登录
2. **图片限制**: 每个帖子最多上传9张图片
3. **匿名保护**: 前端不会显示任何真实用户信息
4. **内容审查**: 管理员可以折叠违规内容（`is_hidden=True`）
5. **删除权限**: 用户只能删除自己发布的内容，管理员可以删除任何内容
6. **昵称有效期**: 匿名昵称24小时后自动刷新
7. **楼中楼**: 评论支持最多一层嵌套（父评论-子评论）

## 数据模型

### TreeholePost（树洞帖子）
- `id`: 主键
- `author`: 真实作者（外键，仅后台可见）
- `anonymous_name`: 随机匿名昵称
- `anonymous_name_expires`: 昵称过期时间
- `content`: 帖子内容
- `images`: 图片列表（JSON）
- `post_type`: 帖子类型
- `likes_count`: 点赞数
- `comments_count`: 评论数
- `is_hidden`: 是否被折叠
- `created_at`: 创建时间
- `updated_at`: 更新时间

### TreeholeComment（树洞评论）
- `id`: 主键
- `post`: 所属帖子（外键）
- `author`: 真实作者（外键，仅后台可见）
- `anonymous_name`: 随机匿名昵称
- `anonymous_name_expires`: 昵称过期时间
- `content`: 评论内容
- `parent`: 父评论（外键，可空）
- `likes_count`: 点赞数
- `is_hidden`: 是否被折叠
- `created_at`: 创建时间

### TreeholeLike（点赞记录）
- `id`: 主键
- `user`: 用户（外键）
- `post`: 帖子（外键，可空）
- `comment`: 评论（外键，可空）
- `created_at`: 创建时间
