# 用户认证 API 文档

## 概述
此API提供完整的用户认证和管理功能，包括注册、登录、个人资料管理等。

## 基础URL
```
http://localhost:8000/api/users/
```

## 认证方式
使用JWT (JSON Web Token) 进行身份认证。在需要认证的接口请求头中添加：
```
Authorization: Bearer <access_token>
```

---

## API 端点

### 1. 用户注册
**端点**: `POST /api/users/register/`

**权限**: 无需认证

**请求体**:
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "TestPass123!",
  "password2": "TestPass123!",
  "real_name": "张三",           // 可选
  "student_id": "2024001",       // 可选
  "identity_type": "UNDERGRAD"   // 可选: UNDERGRAD/POSTGRAD/TEACHER/ALUMNI
}
```

**响应** (201 Created):
```json
{
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "real_name": "张三",
    "student_id": "2024001",
    "identity_type": "UNDERGRAD",
    "identity_type_display": "本科生",
    "is_verified": false,
    "avatar": null,
    "date_joined": "2025-12-09T15:28:03.065358+08:00"
  },
  "message": "注册成功"
}
```

---

### 2. 获取访问令牌（登录）
**端点**: `POST /api/users/token/`

**权限**: 无需认证

**请求体**:
```json
{
  "username": "testuser",
  "password": "TestPass123!"
}
```

**响应** (200 OK):
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**说明**:
- `access`: 访问令牌，有效期1小时
- `refresh`: 刷新令牌，有效期7天

---

### 3. 刷新访问令牌
**端点**: `POST /api/users/token/refresh/`

**权限**: 无需认证

**请求体**:
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**响应** (200 OK):
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### 4. 获取个人资料
**端点**: `GET /api/users/profile/`

**权限**: 需要认证

**请求头**:
```
Authorization: Bearer <access_token>
```

**响应** (200 OK):
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "real_name": "张三",
  "student_id": "2024001",
  "identity_type": "UNDERGRAD",
  "identity_type_display": "本科生",
  "is_verified": false,
  "avatar": null,
  "date_joined": "2025-12-09T15:28:03.065358+08:00"
}
```

---

### 5. 更新个人资料
**端点**: `PATCH /api/users/profile/`

**权限**: 需要认证

**请求头**:
```
Authorization: Bearer <access_token>
```

**请求体** (可部分更新):
```json
{
  "real_name": "李四",
  "student_id": "2024002",
  "identity_type": "POSTGRAD"
}
```

**响应** (200 OK):
```json
{
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "real_name": "李四",
    "student_id": "2024002",
    "identity_type": "POSTGRAD",
    "identity_type_display": "研究生",
    "is_verified": false,
    "avatar": null,
    "date_joined": "2025-12-09T15:28:03.065358+08:00"
  },
  "message": "个人资料更新成功"
}
```

---

### 6. 修改密码
**端点**: `POST /api/users/change-password/`

**权限**: 需要认证

**请求头**:
```
Authorization: Bearer <access_token>
```

**请求体**:
```json
{
  "old_password": "TestPass123!",
  "new_password": "NewPass456!",
  "new_password2": "NewPass456!"
}
```

**响应** (200 OK):
```json
{
  "message": "密码修改成功，请重新登录"
}
```

---

### 7. 用户列表（测试用）
**端点**: `GET /api/users/list/`

**权限**: 需要认证

**请求头**:
```
Authorization: Bearer <access_token>
```

**响应** (200 OK):
```json
{
  "count": 10,
  "next": "http://localhost:8000/api/users/list/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com",
      "real_name": "张三",
      "student_id": "2024001",
      "identity_type": "UNDERGRAD",
      "identity_type_display": "本科生",
      "is_verified": false,
      "avatar": null,
      "date_joined": "2025-12-09T15:28:03.065358+08:00"
    }
  ]
}
```

---

## 身份类型选项

| 代码 | 显示名称 |
|------|----------|
| UNDERGRAD | 本科生 |
| POSTGRAD | 研究生 |
| TEACHER | 教职工 |
| ALUMNI | 校友 |

---

## 错误响应

### 400 Bad Request
```json
{
  "password": ["两次输入的密码不一致"]
}
```

### 401 Unauthorized
```json
{
  "detail": "未提供认证凭据。"
}
```

### 403 Forbidden
```json
{
  "detail": "您没有执行该操作的权限。"
}
```

---

## 使用示例

### Python (requests)
```python
import requests

# 注册
response = requests.post('http://localhost:8000/api/users/register/', json={
    'username': 'newuser',
    'email': 'new@example.com',
    'password': 'TestPass123!',
    'password2': 'TestPass123!'
})

# 登录
response = requests.post('http://localhost:8000/api/users/token/', json={
    'username': 'newuser',
    'password': 'TestPass123!'
})
tokens = response.json()

# 获取个人资料
headers = {'Authorization': f'Bearer {tokens["access"]}'}
response = requests.get('http://localhost:8000/api/users/profile/', headers=headers)
profile = response.json()
```

### JavaScript (fetch)
```javascript
// 注册
const registerResponse = await fetch('http://localhost:8000/api/users/register/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    username: 'newuser',
    email: 'new@example.com',
    password: 'TestPass123!',
    password2: 'TestPass123!'
  })
});

// 登录
const loginResponse = await fetch('http://localhost:8000/api/users/token/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    username: 'newuser',
    password: 'TestPass123!'
  })
});
const tokens = await loginResponse.json();

// 获取个人资料
const profileResponse = await fetch('http://localhost:8000/api/users/profile/', {
  headers: {'Authorization': `Bearer ${tokens.access}`}
});
const profile = await profileResponse.json();
```

---

## 安全建议

1. **生产环境**：确保使用HTTPS协议
2. **密钥管理**：将SECRET_KEY移至环境变量
3. **令牌存储**：安全存储JWT令牌（如HttpOnly cookies）
4. **令牌刷新**：在access_token过期前使用refresh_token获取新令牌
5. **密码强度**：使用Django的密码验证器确保密码安全
