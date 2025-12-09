# 玄武 (Xuanwu) - 校园交流平台后端

## 环境配置

### 环境变量设置

本项目使用 `python-decouple` 管理环境变量。首次运行前需要配置环境变量：

1. 复制 `.env.example` 文件为 `.env`：
   ```bash
   cp .env.example .env
   ```

2. 编辑 `.env` 文件，设置必要的环境变量：
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

3. **生产环境必须设置新的 SECRET_KEY**：
   ```bash
   python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
   ```

### 安装依赖

```bash
pip install -r requirements.txt
```

### 数据库迁移

```bash
python manage.py migrate
```

### 运行开发服务器

```bash
python manage.py runserver
```

### 创建超级用户

```bash
python manage.py createsuperuser
```

## 环境变量说明

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `SECRET_KEY` | Django 密钥 | 开发默认值 | 生产环境必需 |
| `DEBUG` | 调试模式 | `True` | 否 |
| `ALLOWED_HOSTS` | 允许的主机（逗号分隔） | 空 | 生产环境必需 |

## 安全提示

- **永远不要**将包含真实密钥的 `.env` 文件提交到版本控制
- 生产环境必须设置强随机的 `SECRET_KEY`
- 生产环境必须设置 `DEBUG=False`
- 生产环境必须正确配置 `ALLOWED_HOSTS`

## API 文档

- 用户认证: `API_DOCUMENTATION.md`
- 论坛模块: `FORUM_API_DOCUMENTATION.md`
- 评价系统: `RATINGS_API_DOCUMENTATION.md`
- 资源平台: `RESOURCES_API_DOCUMENTATION.md`
