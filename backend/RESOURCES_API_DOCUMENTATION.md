# 资源交流平台 API 文档

## 概述
资源交流平台提供学习资料的上传、下载、评论和搜索功能，支持考试真题、课件、笔记等多种资源类型。

## 基础URL
```
http://localhost:8000/api/resources/
```

## 认证方式
使用JWT认证。上传资源需要认证。
```
Authorization: ******
```

---

## 资源分类 API

### 1. 获取分类列表
**端点**: `GET /api/resources/categories/`

**权限**: 无需认证

**响应** (200 OK):
```json
{
  "count": 4,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "考试真题",
      "description": "各科目历年考试真题",
      "icon": "exam",
      "order": 1,
      "resource_count": 15,
      "created_at": "2025-12-09T16:30:00.000000+08:00"
    }
  ]
}
```

### 2. 创建分类（仅管理员）
**端点**: `POST /api/resources/categories/`

**权限**: 管理员

---

## 资源 API

### 1. 获取资源列表
**端点**: `GET /api/resources/resources/`

**权限**: 无需认证

**查询参数**:
- `search` - 搜索标题、描述、课程、标签
- `category` - 按分类ID筛选
- `uploader` - 按上传者ID筛选
- `course` - 按课程名称筛选
- `year` - 按年份筛选
- `file_type` - 按文件类型筛选 (pdf, doc, ppt等)
- `ordering` - 排序 (created_at, download_count, title)
- `page` - 页码

**响应** (200 OK):
```json
{
  "count": 20,
  "next": "http://localhost:8000/api/resources/resources/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "数据结构期末考试真题2024",
      "description": "数据结构课程2024年期末考试真题及答案",
      "category": 1,
      "category_name": "考试真题",
      "uploader": {
        "id": 1,
        "username": "student01",
        "real_name": "张三"
      },
      "course": "数据结构",
      "year": 2024,
      "semester": "秋季学期",
      "tags": "数据结构,期末考试,真题",
      "file_extension": "pdf",
      "file_size_mb": 2.5,
      "download_count": 150,
      "average_rating": 4.5,
      "comment_count": 10,
      "created_at": "2025-12-09T16:30:00.000000+08:00"
    }
  ]
}
```

### 2. 获取资源详情
**端点**: `GET /api/resources/resources/{id}/`

**权限**: 无需认证

**响应** (200 OK):
```json
{
  "id": 1,
  "title": "数据结构期末考试真题2024",
  "description": "数据结构课程2024年期末考试真题及答案",
  "file_url": "http://localhost:8000/media/resources/考试真题/1_exam.pdf",
  "category": 1,
  "category_name": "考试真题",
  "uploader": {...},
  "course": "数据结构",
  "year": 2024,
  "semester": "秋季学期",
  "tags": "数据结构,期末考试,真题",
  "file_extension": "pdf",
  "file_size": 2621440,
  "file_size_mb": 2.5,
  "download_count": 150,
  "average_rating": 4.5,
  "comment_count": 10,
  "is_approved": true,
  "created_at": "2025-12-09T16:30:00.000000+08:00",
  "updated_at": "2025-12-09T16:30:00.000000+08:00"
}
```

### 3. 上传资源
**端点**: `POST /api/resources/resources/`

**权限**: 需要认证

**请求**: multipart/form-data
```
title: 数据结构期末考试真题2024
description: 数据结构课程2024年期末考试真题及答案
file: [二进制文件]
category: 1
course: 数据结构
year: 2024
semester: 秋季学期
tags: 数据结构,期末考试,真题
```

**文件要求**:
- 最大大小: 100MB
- 支持格式: pdf, doc, docx, ppt, pptx, zip, rar, txt, jpg, jpeg, png, xls, xlsx

**响应** (201 Created):
```json
{
  "title": "数据结构期末考试真题2024",
  "description": "数据结构课程2024年期末考试真题及答案",
  "file": "/media/resources/考试真题/1_exam.pdf",
  "category": 1,
  "course": "数据结构",
  "year": 2024,
  "semester": "秋季学期",
  "tags": "数据结构,期末考试,真题"
}
```

### 4. 更新资源
**端点**: `PATCH /api/resources/resources/{id}/`

**权限**: 需要认证（仅上传者或管理员）

**请求体**:
```json
{
  "title": "更新后的标题",
  "description": "更新后的描述",
  "category": 2
}
```

### 5. 删除资源
**端点**: `DELETE /api/resources/resources/{id}/`

**权限**: 需要认证（仅上传者或管理员）

**响应** (204 No Content)

### 6. 下载资源
**端点**: `GET /api/resources/resources/{id}/download/`

**权限**: 无需认证

**说明**:
- 返回文件流供下载
- 如果用户已认证，会记录下载历史并增加下载次数

**响应**: 文件下载

### 7. 获取资源评论
**端点**: `GET /api/resources/resources/{id}/comments/`

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
      "resource": 1,
      "user": {...},
      "content": "非常有用的资料，感谢分享！",
      "rating": 5,
      "created_at": "2025-12-09T16:30:00.000000+08:00",
      "updated_at": "2025-12-09T16:30:00.000000+08:00"
    }
  ]
}
```

### 8. 我上传的资源
**端点**: `GET /api/resources/resources/my_uploads/`

**权限**: 需要认证

**响应**: 与资源列表格式相同

### 9. 我下载的资源
**端点**: `GET /api/resources/resources/my_downloads/`

**权限**: 需要认证

**响应** (200 OK):
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "resource": 1,
      "resource_title": "数据结构期末考试真题2024",
      "user": {...},
      "downloaded_at": "2025-12-09T16:30:00.000000+08:00",
      "ip_address": "192.168.1.1"
    }
  ]
}
```

### 10. 资源统计
**端点**: `GET /api/resources/resources/{id}/statistics/`

**权限**: 无需认证

**响应** (200 OK):
```json
{
  "total_downloads": 150,
  "average_rating": 4.5,
  "comment_count": 10,
  "download_by_identity": {
    "本科生": 80,
    "研究生": 50,
    "教职工": 15,
    "校友": 5
  }
}
```

---

## 评论 API

### 1. 创建评论
**端点**: `POST /api/resources/comments/`

**权限**: 需要认证

**请求体**:
```json
{
  "resource": 1,
  "content": "非常有用的资料，感谢分享！",
  "rating": 5
}
```

**字段说明**:
- `rating` - 可选，1-5星评分

**响应** (201 Created):
```json
{
  "id": 1,
  "resource": 1,
  "user": {...},
  "content": "非常有用的资料，感谢分享！",
  "rating": 5,
  "created_at": "2025-12-09T16:30:00.000000+08:00",
  "updated_at": "2025-12-09T16:30:00.000000+08:00"
}
```

### 2. 更新评论
**端点**: `PATCH /api/resources/comments/{id}/`

**权限**: 需要认证（仅评论作者）

### 3. 删除评论
**端点**: `DELETE /api/resources/comments/{id}/`

**权限**: 需要认证（仅评论作者或管理员）

### 4. 获取评论列表
**端点**: `GET /api/resources/comments/`

**查询参数**:
- `resource` - 按资源ID筛选

---

## 特性

### 文件管理
- **文件类型验证**: 支持常见文档、图片、压缩包格式
- **文件大小限制**: 单个文件最大100MB
- **自动分类存储**: 按资源分类自动组织文件目录

### 搜索和筛选
- **全文搜索**: 搜索标题、描述、课程名、标签
- **多维度筛选**: 按分类、课程、年份、文件类型筛选
- **灵活排序**: 按时间、下载量、标题排序

### 下载统计
- **下载计数**: 自动统计下载次数
- **下载记录**: 记录已认证用户的下载历史
- **统计分析**: 按用户身份类型统计下载量

### 评论评分
- **资源评论**: 用户可以对资源发表评论
- **星级评分**: 1-5星评分系统
- **平均评分**: 自动计算资源平均评分

### 权限控制
- **查看**: 所有人可以查看和下载资源
- **上传**: 需要登录认证
- **编辑/删除**: 仅上传者或管理员
- **审核**: 管理员可审核资源

---

## 错误响应

### 400 Bad Request
```json
{
  "file": ["文件大小不能超过100MB"]
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
  "detail": "您没有权限修改此资源"
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

# 获取资源列表
response = requests.get('http://localhost:8000/api/resources/resources/', 
                       params={'category': 1, 'course': '数据结构'})
resources = response.json()['results']

# 上传资源（需要JWT token）
headers = {'Authorization': '******'}
files = {'file': open('exam.pdf', 'rb')}
data = {
    'title': '数据结构期末考试真题2024',
    'description': '2024年期末考试真题',
    'category': 1,
    'course': '数据结构',
    'year': 2024,
    'tags': '数据结构,期末,真题'
}
response = requests.post(
    'http://localhost:8000/api/resources/resources/',
    headers=headers,
    files=files,
    data=data
)

# 下载资源
resource_id = 1
response = requests.get(
    f'http://localhost:8000/api/resources/resources/{resource_id}/download/',
    stream=True
)
with open('downloaded_file.pdf', 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)

# 发表评论
comment_data = {
    'resource': resource_id,
    'content': '非常有用的资料！',
    'rating': 5
}
response = requests.post(
    'http://localhost:8000/api/resources/comments/',
    headers=headers,
    json=comment_data
)
```

### JavaScript (fetch)
```javascript
// 获取资源列表
const response = await fetch('http://localhost:8000/api/resources/resources/?category=1');
const data = await response.json();
const resources = data.results;

// 上传资源
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('title', '数据结构期末考试真题2024');
formData.append('description', '2024年期末考试真题');
formData.append('category', 1);
formData.append('course', '数据结构');

const uploadResponse = await fetch('http://localhost:8000/api/resources/resources/', {
  method: 'POST',
  headers: {
    'Authorization': '******'
  },
  body: formData
});

// 下载资源
const downloadResponse = await fetch(
  `http://localhost:8000/api/resources/resources/${resourceId}/download/`
);
const blob = await downloadResponse.blob();
const url = window.URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'file.pdf';
a.click();
```

---

## 最佳实践

1. **文件命名**: 上传时使用描述性文件名
2. **标签使用**: 添加相关标签便于搜索
3. **分类选择**: 选择正确的资源分类
4. **课程信息**: 填写完整的课程、年份、学期信息
5. **文件压缩**: 大文件建议压缩后上传
6. **版权注意**: 仅上传允许分享的资料
7. **描述完整**: 提供详细的资源描述
