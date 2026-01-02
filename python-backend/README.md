# Python Backend Rewrite - Go Web Init

This is a complete Python rewrite of the Go backend using FastAPI, SQLAlchemy, and Redis.

## Features

- ✅ FastAPI web framework
- ✅ SQLAlchemy ORM with MySQL, PostgreSQL, SQLite support
- ✅ JWT authentication with bcrypt password hashing
- ✅ OAuth2 integration (GitHub, WeChat)
- ✅ RBAC (Role-Based Access Control) system
- ✅ Redis caching layer
- ✅ Docker integration
- ✅ Kubernetes integration
- ✅ Comprehensive middleware stack
- ✅ Error handling and validation
- ✅ Async/await support

## Project Structure

```
python-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app factory
│   ├── config.py               # Configuration management
│   ├── database.py             # Database setup
│   ├── schemas.py              # Pydantic models
│   ├── models/
│   │   └── __init__.py         # SQLAlchemy models
│   ├── controllers/            # API endpoints
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── groups.py
│   │   ├── posts.py
│   │   ├── rbac.py
│   │   ├── docker.py
│   │   └── kubernetes.py
│   ├── services/               # Business logic
│   │   ├── auth_service.py
│   │   └── rbac_service.py
│   ├── repositories/           # Data access layer
│   │   └── __init__.py
│   ├── middleware/             # Custom middleware
│   │   └── __init__.py
│   └── utils/                  # Utilities
│       ├── auth.py             # JWT/password utilities
│       ├── errors.py           # Exception handling
│       └── redis_client.py     # Redis wrapper
├── config/
│   └── app.yaml               # Configuration file
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker image
├── docker-compose.yml         # Docker Compose setup
└── README.md

```

## Installation

### Prerequisites

- Python 3.10+
- MySQL 8.0+ (or PostgreSQL/SQLite)
- Redis 6.0+
- Docker & Docker Compose (optional)

### Local Setup

1. **Clone and navigate**:
   ```bash
   cd python-backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure**:
   - Edit `config/app.yaml` with your database and Redis credentials

5. **Run migrations** (automatic on startup):
   ```bash
   python -m uvicorn app.main:app --reload
   ```

6. **Access API**:
   - http://localhost:8000
   - Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Docker Setup

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f python-backend

# Shut down
docker-compose down
```

## Configuration

Edit `config/app.yaml`:

```yaml
server:
  env: "debug"              # debug or production
  address: "127.0.0.1"
  port: 8000
  jwt_secret: "weaveserver" # Change in production!
  db_type: "mysql"          # mysql, postgres, or sqlite

mysql:
  host: "localhost"
  port: 3306
  name: "go-test"
  user: "root"
  password: "1234567"
  migrate: true             # Auto-migrate on startup

redis:
  enable: true
  host: "localhost"
  port: 6379
  password: "123456"

docker:
  enable: true
  host: "unix:///var/run/docker.sock"

kubernetes:
  enable: true
  watch_resources:
    - "Deployment.v1.apps"
    - "Pod.v1."
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get token
- `POST /api/auth/logout` - Logout (requires auth)
- `POST /api/auth/refresh` - Refresh token
- `GET /api/auth/me` - Get current user

### Users
- `GET /api/users` - List all users
- `POST /api/users` - Create user
- `GET /api/users/{id}` - Get user
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user
- `POST /api/users/{id}/groups/{group_id}` - Add to group
- `DELETE /api/users/{id}/groups/{group_id}` - Remove from group
- `GET /api/users/{id}/groups` - List user's groups

### Groups
- `GET /api/groups` - List all groups
- `POST /api/groups` - Create group
- `GET /api/groups/{id}` - Get group
- `PUT /api/groups/{id}` - Update group
- `DELETE /api/groups/{id}` - Delete group

### Posts
- `GET /api/posts` - List all posts
- `POST /api/posts` - Create post
- `GET /api/posts/{id}` - Get post
- `PUT /api/posts/{id}` - Update post
- `DELETE /api/posts/{id}` - Delete post

### RBAC
- `POST /api/rbac/roles` - Create role
- `GET /api/rbac/roles` - List roles
- `GET /api/rbac/roles/{id}` - Get role
- `POST /api/rbac/rules` - Create rule
- `GET /api/rbac/rules` - List rules
- `GET /api/rbac/rules/{id}` - Get rule
- `POST /api/rbac/users/{user_id}/roles/{role_id}` - Assign role to user
- `DELETE /api/rbac/users/{user_id}/roles/{role_id}` - Remove role from user
- `POST /api/rbac/roles/{role_id}/rules/{rule_id}` - Assign rule to role
- `GET /api/rbac/users/{user_id}/permissions` - Get user permissions
- `POST /api/rbac/check` - Check permission

### Docker (if enabled)
- `GET /api/docker/containers` - List containers
- `GET /api/docker/containers/{id}` - Get container
- `POST /api/docker/containers/{id}/start` - Start container
- `POST /api/docker/containers/{id}/stop` - Stop container
- `DELETE /api/docker/containers/{id}` - Delete container

### Kubernetes (if enabled)
- `GET /api/kubernetes/namespaces` - List namespaces
- `GET /api/kubernetes/pods` - List pods
- `GET /api/kubernetes/pods/{id}` - Get pod
- `DELETE /api/kubernetes/pods/{id}` - Delete pod
- `GET /api/kubernetes/deployments` - List deployments

## Authentication

All protected endpoints require JWT token in Authorization header:

```bash
Authorization: Bearer <token>
```

Get token via login:

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'
```

## Development

### Run tests
```bash
pytest
```

### Run with auto-reload
```bash
python -m uvicorn app.main:app --reload
```

### Debug mode
```bash
# Edit config/app.yaml and set env: "debug"
```

## Key Differences from Go Version

| Feature | Go | Python |
|---------|-------|--------|
| Framework | Gin | FastAPI |
| ORM | GORM | SQLAlchemy |
| Password Hashing | bcrypt | passlib + bcrypt |
| JWT | golang-jwt | python-jose |
| Redis | go-redis | redis-py |
| Docker SDK | docker/docker-sdk | docker-sdk-python |
| Async | goroutines | async/await |

## Performance Considerations

- FastAPI is very performant (nearly matches Go in benchmarks)
- Use uvicorn workers for production: `uvicorn app.main:app --workers 4`
- Redis caching reduces database load
- Connection pooling configured for all databases
- Async middleware for non-blocking operations

## Production Deployment

### Using Gunicorn + Uvicorn

```bash
pip install gunicorn
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker Production Build

```bash
docker build -t weave-backend:latest .
docker run -d --name weave -e DATABASE_URL=mysql://... weave-backend:latest
```

### Environment Variables

```bash
# Override config values
DATABASE_URL=mysql+pymysql://user:pass@host/db
REDIS_HOST=localhost
REDIS_PORT=6379
JWT_SECRET=your-secret-key
```

## Troubleshooting

### Database Connection Error
- Verify MySQL is running: `mysql -u root -p`
- Check credentials in `config/app.yaml`
- Ensure database exists: `CREATE DATABASE go-test;`

### Redis Connection Error
- Verify Redis is running: `redis-cli ping`
- Check host and port in config
- For Docker: ensure Redis container is healthy

### Authorization Header Missing
- All endpoints except `/api/auth/` require valid JWT
- Login first to get token
- Include `Authorization: Bearer <token>` header

## License

Same as parent Go project

## Next Steps

1. ✅ Complete core backend implementation
2. Deploy and test with frontend
3. Add monitoring/metrics endpoints
4. Performance profiling and optimization
5. Add comprehensive test suite
6. API versioning (v2, v3, etc.)
