# Python Rewrite Specification: Weave Web Application

**Date**: January 2026  
**Source**: Go Codebase Analysis (v1.0)  
**Module**: github.com/makeok/go-web-init

---

## Table of Contents
1. [Application Overview](#application-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [API Endpoints](#api-endpoints)
4. [Database Models](#database-models)
5. [Authentication & Authorization](#authentication--authorization)
6. [Middleware Pipeline](#middleware-pipeline)
7. [External Integrations](#external-integrations)
8. [Configuration](#configuration)
9. [Dependencies & Libraries](#dependencies--libraries)
10. [Service Layer](#service-layer)

---

## Application Overview

**Application Name**: Weave Server  
**Type**: RESTful API + Dashboard Backend  
**Language**: Go → **Python (target)**  
**Framework**: Gin → **FastAPI/Flask (recommended: FastAPI)**  
**Database**: MySQL (primary), PostgreSQL, SQLite (supported)  
**Caching**: Redis (optional)  
**Port**: 8080 (default)

### Core Features
- User management with authentication/authorization
- Role-based access control (RBAC)
- OAuth2 integration (GitHub, WeChat)
- Docker container management
- Kubernetes resource management
- Blog/Post management (with comments, likes, tags, categories)
- Group management
- Rate limiting
- Metrics/Monitoring (Prometheus)
- Request tracing

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Applications                       │
│                    (Web UI, API Consumers)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────▼─────────┐
                    │  Gin Web Server  │
                    │    (:8080)       │
                    └────────┬─────────┘
                             │
    ┌────────────────────────┼────────────────────────┐
    │         MIDDLEWARE PIPELINE                     │
    │  ┌──────────────────────────────────────────┐   │
    │  │ 1. Recovery                              │   │
    │  │ 2. Rate Limiting (server & IP-based)    │   │
    │  │ 3. Static File Server                    │   │
    │  │ 4. Monitoring/Metrics                    │   │
    │  │ 5. CORS                                  │   │
    │  │ 6. Request Info Extraction               │   │
    │  │ 7. Logging                               │   │
    │  │ 8. JWT Authentication                    │   │
    │  │ 9. Authorization (RBAC)                  │   │
    │  │10. Tracing                               │   │
    │  └──────────────────────────────────────────┘   │
    └────────────────────────┬────────────────────────┘
                             │
    ┌────────────────────────▼────────────────────────┐
    │           CONTROLLERS (API Routes)              │
    │  ├─ AuthController          (/auth/*)          │
    │  ├─ UserController          (/users/*)         │
    │  ├─ GroupController         (/groups/*)        │
    │  ├─ PostController          (/posts/*)         │
    │  ├─ RBACController          (/roles/*)         │
    │  ├─ ContainerController     (/containers/*)    │
    │  └─ KubeController          (/namespaces/*)    │
    └────────────────────────┬────────────────────────┘
                             │
    ┌────────────────────────▼────────────────────────┐
    │           SERVICE LAYER (Business Logic)        │
    │  ├─ UserService                                 │
    │  ├─ GroupService                                │
    │  ├─ PostService                                 │
    │  ├─ RBACService                                 │
    │  └─ OAuthManager                                │
    └────────────────────────┬────────────────────────┘
                             │
    ┌────────────────────────▼────────────────────────┐
    │         REPOSITORY LAYER (Data Access)          │
    │  ├─ UserRepository                              │
    │  ├─ GroupRepository                             │
    │  ├─ PostRepository                              │
    │  └─ RBACRepository                              │
    └────────────────────────┬────────────────────────┘
                             │
    ┌────────────────────────▼────────────────────────┐
    │           DATABASE LAYER                        │
    │  ┌──────────────────────────────────────────┐   │
    │  │ GORM ORM                                 │   │
    │  │ ├─ MySQL Driver (primary)                │   │
    │  │ ├─ PostgreSQL Driver                     │   │
    │  │ └─ SQLite Driver                         │   │
    │  └──────────────────────────────────────────┘   │
    │  ┌──────────────────────────────────────────┐   │
    │  │ Redis (Caching)                          │   │
    │  │ ├─ User Cache (HSet)                     │   │
    │  │ └─ Token Storage                         │   │
    │  └──────────────────────────────────────────┘   │
    └────────────────────────┬────────────────────────┘
                             │
    ┌────────────────────────▼────────────────────────┐
    │       EXTERNAL INTEGRATIONS                     │
    │  ├─ Docker API Client                           │
    │  ├─ Kubernetes Client                           │
    │  └─ OAuth2 (GitHub, WeChat)                     │
    └─────────────────────────────────────────────────┘
```

---

## API Endpoints

### Base URL: `/api/v1`

### Health & System Endpoints
| Method | Path | Handler | Purpose |
|--------|------|---------|---------|
| GET | `/healthz` | `Server.Ping()` | Health check |
| GET | `/version` | `version.Get()` | Get version info |
| GET | `/metrics` | Prometheus handler | Metrics export |
| GET | `/api/list` | `Server.getRoutes()` | List all routes |
| GET | `/api/index` | `Index()` | Home page HTML |
| ANY | `/debug/pprof/*` | Go pprof | CPU/memory profiling |
| GET | `/swagger/*` | Swagger UI | API documentation |

### Authentication Endpoints
| Method | Path | Controller | Function | Auth Required | Purpose |
|--------|------|-----------|----------|--------------|---------|
| POST | `/auth/token` | AuthController | `Login()` | ❌ | User login |
| DELETE | `/auth/token` | AuthController | `Logout()` | ❌ | User logout |
| POST | `/auth/user` | AuthController | `Register()` | ❌ | User registration |

**Login Payload**:
```json
{
  "name": "string",
  "password": "string",
  "setCookie": "boolean",
  "authType": "github|wechat|nil",
  "authCode": "string"
}
```

**Response**:
```json
{
  "token": "jwt_token_string",
  "describe": "set token in Authorization Header, [Authorization: Bearer {token}]"
}
```

### User Management Endpoints
| Method | Path | Controller | Function | Auth Required | Purpose |
|--------|------|-----------|----------|--------------|---------|
| GET | `/users` | UserController | `List()` | ✅ | List all users |
| GET | `/users/{id}` | UserController | `Get()` | ✅ | Get user by ID |
| POST | `/users` | UserController | `Create()` | ✅ | Create new user |
| PUT | `/users/{id}` | UserController | `Update()` | ✅ | Update user |
| DELETE | `/users/{id}` | UserController | `Delete()` | ✅ | Delete user |
| GET | `/users/{id}/groups` | UserController | `GetGroups()` | ✅ | Get user's groups |
| POST | `/users/{id}/roles/{rid}` | UserController | `AddRole()` | ✅ | Assign role to user |
| DELETE | `/users/{id}/roles/{rid}` | UserController | `DelRole()` | ✅ | Remove role from user |

### Group Management Endpoints
| Method | Path | Controller | Function | Auth Required | Purpose |
|--------|------|-----------|----------|--------------|---------|
| GET | `/groups` | GroupController | `List()` | ✅ | List all groups |
| GET | `/groups/{id}` | GroupController | `Get()` | ✅ | Get group by ID |
| POST | `/groups` | GroupController | `Create()` | ✅ | Create new group |
| PUT | `/groups/{id}` | GroupController | `Update()` | ✅ | Update group |
| DELETE | `/groups/{id}` | GroupController | `Delete()` | ✅ | Delete group |

### Post Management Endpoints
| Method | Path | Controller | Function | Auth Required | Purpose |
|--------|------|-----------|----------|--------------|---------|
| GET | `/posts` | PostController | `List()` | ✅ | List all posts |
| GET | `/posts/{id}` | PostController | `Get()` | ✅ | Get post by ID |
| POST | `/posts` | PostController | `Create()` | ✅ | Create new post |
| PUT | `/posts/{id}` | PostController | `Update()` | ✅ | Update post |
| DELETE | `/posts/{id}` | PostController | `Delete()` | ✅ | Delete post |

### RBAC (Role-Based Access Control) Endpoints
| Method | Path | Controller | Function | Auth Required | Purpose |
|--------|------|-----------|----------|--------------|---------|
| GET | `/roles` | RBACController | `List()` | ✅ | List all roles |
| POST | `/roles` | RBACController | `Create()` | ✅ | Create new role |
| GET | `/roles/{id}` | RBACController | `Get()` | ✅ | Get role by ID |
| PUT | `/roles/{id}` | RBACController | `Update()` | ✅ | Update role |
| DELETE | `/roles/{id}` | RBACController | `Delete()` | ✅ | Delete role |
| GET | `/resources` | RBACController | `ListResources()` | ✅ | List available resources |
| GET | `/operations` | RBACController | `ListOperations()` | ✅ | List available operations |

### Container Management Endpoints (Docker)
| Method | Path | Controller | Function | Auth Required | Purpose | Enabled If |
|--------|------|-----------|----------|--------------|---------|-----------|
| GET | `/containers` | ContainerController | `List()` | ✅ | List containers | docker.enable=true |
| POST | `/containers` | ContainerController | `Create()` | ✅ | Create container | docker.enable=true |
| GET | `/containers/{id}` | ContainerController | `Get()` | ✅ | Get container details | docker.enable=true |
| POST | `/containers/{id}` | ContainerController | `Operate()` | ✅ | Control container (start/stop/restart) | docker.enable=true |
| PUT | `/containers/{id}` | ContainerController | `Update()` | ✅ | Update container | docker.enable=true |
| DELETE | `/containers/{id}` | ContainerController | `Delete()` | ✅ | Delete container | docker.enable=true |
| GET | `/containers/{id}/logs` | ContainerController | `GetLogs()` | ✅ | Get container logs | docker.enable=true |
| GET | `/containers/{id}/stats` | ContainerController | `GetStats()` | ✅ | Get container stats | docker.enable=true |

**Container Operations** (query param `verb`):
- `start` - Start a container
- `stop` - Stop a container
- `restart` - Restart a container

### Kubernetes Endpoints
| Method | Path | Controller | Function | Auth Required | Purpose | Enabled If |
|--------|------|-----------|----------|--------------|---------|-----------|
| GET | `/namespaces` | KubeController | `List()` | ✅ | List namespaces | k8s.enable=true |
| POST | `/namespaces/:namespace/:resource` | KubeController | `Create()` | ✅ | Create K8s resource | k8s.enable=true |
| GET | `/namespaces/:namespace/:resource` | KubeController | `List()` | ✅ | List K8s resources | k8s.enable=true |
| GET | `/namespaces/:namespace/:resource/:name` | KubeController | `Get()` | ✅ | Get K8s resource | k8s.enable=true |
| PUT | `/namespaces/:namespace/:resource/:name` | KubeController | `Update()` | ✅ | Update K8s resource | k8s.enable=true |
| DELETE | `/namespaces/:namespace/:resource/:name` | KubeController | `Delete()` | ✅ | Delete K8s resource | k8s.enable=true |

**Supported K8s Resources**:
- Deployments (deployments)
- StatefulSets (statefulsets)
- DaemonSets (daemonsets)
- Pods (pods)
- Services (services)
- Ingresses (ingresses)
- Namespaces (namespaces) - cluster-wide

---

## Database Models

### 1. User Model
**Table**: `users`  
**Soft Delete**: Yes (via `deleted_at`)

| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| id | UINT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| name | VARCHAR(100) | UNIQUE, NOT NULL | Username |
| password | VARCHAR(256) | - | Bcrypt hashed password |
| email | VARCHAR(256) | - | User email |
| avatar | VARCHAR(256) | - | Avatar URL |
| created_at | DATETIME | - | Record creation time |
| updated_at | DATETIME | - | Last update time |
| deleted_at | DATETIME | NULL | Soft delete timestamp |

**Relationships**:
- `AuthInfos` (1:N) → AuthInfo table (ForeignKey: user_id)
- `Groups` (M:N) → Group table (Join table: user_groups)
- `Roles` (M:N) → Role table (Join table: user_roles)

**Methods**:
- `List()` - Get all users with auth info and groups
- `Create(user)` - Create new user
- `GetUserByID(id)` - Get user by ID with roles and groups
- `GetUserByName(name)` - Get user by username
- `GetUserByAuthID(authType, authId)` - Get user by OAuth ID
- `Update(user)` - Update user fields
- `Delete(user)` - Soft delete user
- `AddAuthInfo(authInfo)` - Add OAuth auth info
- `DelAuthInfo(authInfo)` - Remove OAuth auth info
- `AddRole(role, user)` - Assign role to user
- `DelRole(role, user)` - Remove role from user
- `GetGroups(user)` - Get user's groups

### 2. AuthInfo Model
**Table**: `auth_infos`

| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| id | UINT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| user_id | UINT | FOREIGN KEY | Reference to user |
| url | VARCHAR(256) | - | OAuth provider URL |
| auth_type | VARCHAR(256) | - | Type: "github", "wechat" |
| auth_id | VARCHAR(256) | - | OAuth provider's user ID |
| access_token | VARCHAR(256) | - | OAuth access token |
| refresh_token | VARCHAR(256) | - | OAuth refresh token |
| expiry | DATETIME | - | Token expiration time |
| created_at | DATETIME | - | Creation time |
| updated_at | DATETIME | - | Update time |
| deleted_at | DATETIME | NULL | Soft delete timestamp |

### 3. Group Model
**Table**: `groups`

| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| id | UINT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| name | VARCHAR(100) | UNIQUE, NOT NULL | Group name |
| kind | VARCHAR(100) | - | Group kind |
| describe | VARCHAR(1024) | - | Group description |
| creator_id | UINT | - | User who created group |
| updater_id | UINT | - | User who last updated group |
| created_at | DATETIME | - | Creation time |
| updated_at | DATETIME | - | Update time |
| deleted_at | DATETIME | NULL | Soft delete timestamp |

**System Groups**:
- `root` - Root group
- `system:authenticated` - All authenticated users
- `system:unauthenticated` - Unauthenticated users
- `system` - System group
- `custom` - Custom user groups

**Relationships**:
- `Users` (M:N) → User table (Join table: user_groups)
- `Roles` (M:N) → Role table (Join table: group_roles)

**Methods**:
- `List()` - Get all groups with roles
- `Create(user, group)` - Create new group
- `GetGroupByID(id)` - Get group by ID
- `GetGroupByName(name)` - Get group by name
- `Update(group)` - Update group
- `Delete(id)` - Delete group
- `GetUsers(group)` - Get group members
- `AddUser(user, group)` - Add user to group
- `DelUser(user, group)` - Remove user from group
- `AddRole(role, group)` - Assign role to group
- `DelRole(role, group)` - Remove role from group

### 4. Post Model
**Table**: `posts`

| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| id | UINT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| name | VARCHAR(256) | UNIQUE, NOT NULL | Post title |
| content | TEXT | NOT NULL | Post content |
| summary | VARCHAR(512) | - | Post summary |
| creator_id | UINT | FOREIGN KEY | User who created post |
| views | UINT | DEFAULT 0 | View count |
| created_at | DATETIME | - | Creation time |
| updated_at | DATETIME | - | Update time |
| deleted_at | DATETIME | NULL | Soft delete timestamp |

**Runtime Fields** (not persisted):
- `likes` - Like count
- `userLiked` - Whether current user liked

**Relationships**:
- `Creator` (1:N) → User table (ForeignKey: creator_id)
- `Tags` (M:N) → Tag table (Join table: tag_posts)
- `Categories` (M:N) → Category table (Join table: category_posts)
- `Comments` (1:N) → Comment table (ForeignKey: post_id)
- `Likes` (M:M) → Like table (post_id, user_id)

**Methods**:
- `List()` - Get all posts with creator, tags, categories (omit content)
- `Create(user, post)` - Create new post
- `GetPostByID(id)` - Get post with all relationships
- `GetPostByName(name)` - Get post by title
- `Update(post)` - Update post
- `Delete(id)` - Delete post
- `IncView(id)` - Increment view count
- `AddLike(postId, userId)` - Add like
- `DelLike(postId, userId)` - Remove like
- `GetLike(postId, userId)` - Check if user liked
- `GetLikeByUser(userId)` - Get user's likes
- `AddComment(comment)` - Add comment
- `DelComment(id)` - Delete comment
- `ListComment(postId)` - Get post's comments

### 5. Tag Model
**Table**: `tags`

| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| id | UINT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| name | VARCHAR(256) | UNIQUE, NOT NULL | Tag name |

### 6. Category Model
**Table**: `categories`

| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| id | UINT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| name | VARCHAR(256) | UNIQUE, NOT NULL | Category name |

### 7. Like Model
**Table**: `likes`

| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| id | UINT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| user_id | UINT | FOREIGN KEY, UNIQUE INDEX | User who liked |
| post_id | UINT | FOREIGN KEY, UNIQUE INDEX | Liked post |

**Composite Unique Index**: (user_id, post_id)

### 8. Comment Model
**Table**: `comments`

| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| id | UINT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| parent_id | UINT | FOREIGN KEY | Parent comment (for nested comments) |
| user_id | UINT | FOREIGN KEY | Comment author |
| post_id | UINT | FOREIGN KEY | Post being commented on |
| content | VARCHAR(1024) | - | Comment text |
| created_at | DATETIME | - | Creation time |
| updated_at | DATETIME | - | Update time |

**Relationships**:
- `Parent` (M:1) → Comment (self-referencing)
- `User` (M:1) → User
- `Post` (M:1) → Post

### 9. Role Model
**Table**: `roles`

| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| id | UINT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| name | VARCHAR(100) | UNIQUE, NOT NULL | Role name |
| scope | VARCHAR(100) | - | Scope: "cluster" or "namespace" |
| namespace | VARCHAR(100) | - | Target namespace (if namespace-scoped) |
| rules | JSON | - | Array of Rule objects |
| created_at | DATETIME | - | Creation time |
| updated_at | DATETIME | - | Update time |
| deleted_at | DATETIME | NULL | Soft delete timestamp |

**System Roles**:
- `cluster-admin` - Full cluster access

**Rule Structure**:
```json
{
  "resource": "string or '*'",
  "operation": "view|edit|*|specific_verb"
}
```

**Operations**:
- `*` - All operations
- `view` - GET, LIST
- `edit` - CREATE, UPDATE, DELETE, PATCH, GET, LIST
- Specific verbs: CREATE, DELETE, UPDATE, PATCH, GET, LIST

**Methods**:
- `List()` - Get all roles
- `Create(role)` - Create new role
- `GetRoleByID(id)` - Get role by ID
- `GetRoleByName(name)` - Get role by name
- `Update(role)` - Update role
- `Delete(id)` - Delete role

### 10. Resource Model
**Table**: `resources`

| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| id | UINT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| name | VARCHAR(256) | UNIQUE, NOT NULL | Resource name |
| scope | VARCHAR | - | Scope: cluster or namespace |
| kind | VARCHAR(256) | - | Type: "resource" or "menu" |

**Predefined Resources**:
- `containers` - Docker containers
- `posts` - Blog posts
- `users` - User management
- `groups` - Group management
- `roles` - Role management
- `auth` - Authentication resources
- `namespaces` - Kubernetes namespaces

### Join Tables
- **user_groups** (user_id, group_id)
- **user_roles** (user_id, role_id)
- **group_roles** (group_id, role_id)
- **tag_posts** (tag_id, post_id)
- **category_posts** (category_id, post_id)

---

## Authentication & Authorization

### JWT Implementation

**Service**: `JWTService`

**Configuration**:
- **Algorithm**: HS256 (HMAC SHA-256)
- **Issuer**: "weave.io"
- **Duration**: 7 days (604800 seconds)
- **Secret Key**: From config (`server.jwtSecret`)

**Token Claims**:
```go
type CustomClaims struct {
    ID   uint   `json:"id"`
    Name string `json:"name"`
    jwt.RegisteredClaims {
        ExpiresAt: time.Now() + 7 days
        NotBefore: time.Now() - 1000 seconds
        ID: user.ID as string
        Issuer: "weave.io"
    }
}
```

**Methods**:
- `CreateToken(user)` - Generate JWT token for user
- `ParseToken(tokenString)` - Parse and validate JWT token

**Token Usage**:
- **Header**: `Authorization: Bearer {token}`
- **Cookie**: `token` (optional, if `setCookie=true` in login)

### Authorization (RBAC)

**Service**: `authorization` package

**Authorization Flow**:
1. Extract user from context
2. Get request information (resource, verb, namespace)
3. If unauthenticated, assign `system:unauthenticated` group
4. If authenticated, assign `system:authenticated` group
5. Load user's roles and all groups' roles
6. For each role, check if rules allow the operation
7. Rule matching: `(resource="*" OR resource=requested) AND operation.matches(verb)`

**Permission Hierarchy**:
```
User
├─ Direct Roles
│  └─ Rules
└─ Group Memberships
   └─ Group Roles
      └─ Rules
```

**Special Roles**:
- `cluster-admin` - Unrestricted access

**Authorization Function**:
```go
Authorize(user *User, requestInfo *RequestInfo) (bool, error)
```

**RequestInfo Structure**:
- `Verb` - HTTP method: GET, POST, PUT, DELETE, PATCH, LIST, CREATE, UPDATE
- `Resource` - API resource: users, posts, containers, etc.
- `Namespace` - For namespaced resources (K8s)
- `Name` - Specific resource name
- `IsResourceRequest` - Whether it's an API resource request

---

## Middleware Pipeline

**Execution Order** (from request to response):

1. **Recovery Middleware**
   - Catches panics and returns 500 error
   - Part of Gin's default middleware

2. **Rate Limiting Middleware** (`RateLimitMiddleware`)
   - Validates against configured rate limits
   - Supports two types:
     - Server-wide: `limitType: server`
     - Per-IP: `limitType: ip`
   - Default: Server (100 QPS, 500 burst), IP (10 QPS, 50 burst)
   - Returns: 429 Too Many Requests

3. **Static File Server** (`ServerStatic`)
   - Serves frontend files from `dist` folder
   - In debug mode: serves from filesystem
   - In release mode: serves from embedded FS

4. **Monitoring Middleware** (`MonitorMiddleware`)
   - Tracks Prometheus metrics
   - Records: inflight requests, total requests, request duration
   - Labels: method, path, status code

5. **CORS Middleware** (`CORSMiddleware`)
   - Allows all origins
   - Allowed Methods: PUT, PATCH, GET, DELETE, POST, OPTIONS
   - Allowed Headers: Origin, Authorization, Content-Length, Content-Type
   - Expose Headers: Content-Length
   - MaxAge: 12 hours
   - Allows WebSockets

6. **Request Info Middleware** (`RequestInfoMiddleware`)
   - Parses request into structured `RequestInfo`
   - Extracts: verb, resource, namespace, name
   - Stores in context for authorization

7. **Logging Middleware** (`LogMiddleware`)
   - Logs HTTP requests/responses
   - Includes: method, path, status, latency, client IP
   - Log levels: INFO (2xx-3xx), WARN (4xx), ERROR (5xx+)
   - Hostname included in logs

8. **Authentication Middleware** (`AuthenticationMiddleware`)
   - Extracts JWT token from Authorization header or cookie
   - Parses token and loads full user from database
   - Sets user in context (or nil if not authenticated)
   - Never fails - continues with nil user

9. **Authorization Middleware** (`AuthorizationMiddleware`)
   - Checks if user is authorized for requested resource
   - Returns 401 (unauthenticated) or 403 (forbidden)
   - Only applies to API resource requests
   - Non-resource requests (swagger, metrics) bypass

10. **Trace Middleware** (`TraceMiddleware`)
    - Initializes request-scoped tracing
    - Logs slow requests (>100ms)
    - Includes: method, path in trace

---

## External Integrations

### Docker Integration

**Client**: `docker.Client`  
**Configuration**: `docker.enable`, `docker.host`  
**Default Host**: `unix:///var/run/docker.sock`

**Capabilities**:
- List containers (with labels filter)
- Create containers
- Inspect containers
- Start/Stop/Restart containers
- Remove containers
- Get container logs (WebSocket)
- Get container stats

**Container Filtering**:
- Filters by label: `weave.io=true`
- Labels set on creation:
  - `weave.io/platform: true`
  - `app: {container_name}`

**Port Configuration**:
- Exposed ports: based on `CreatedContainer.Port`
- Restart policy: `on-failure` (max retries: 5)

**Container Model** → Docker API Model:
```go
type CreatedContainer struct {
    Name  string   // Container name
    Image string   // Docker image
    Cmd   []string // Command/entrypoint
    Port  int      // Port to expose
}
```

**Methods**:
- `ContainerList()` - List running/stopped containers
- `ContainerCreate()` - Create container
- `ContainerInspect()` - Get container details
- `ContainerStart()` - Start container
- `ContainerStop()` - Stop container
- `ContainerRestart()` - Restart container
- `ContainerRemove()` - Remove container
- `ContainerLogs()` - Stream logs
- `ContainerStats()` - Get stats

### Kubernetes Integration

**Client**: `kubernetes.KubeClient`  
**Configuration**: `kubernetes.enable`, `kubernetes.watchResources`  
**Config Source**: `KUBECONFIG` environment variable

**Capabilities**:
- Create K8s resources (Deployment, Pod, Service, etc.)
- List K8s resources
- Get specific resource
- Update K8s resource
- Delete K8s resource
- Watch for changes on configured resources

**Supported Resources**:
- Deployments
- StatefulSets
- DaemonSets
- Pods
- Services
- Ingresses
- Namespaces (cluster-wide)

**Watch Configuration**:
- Configurable via `kubernetes.watchResources`
- Format: `Kind.version.group` (e.g., "Deployment.v1.apps")
- Watches are cached and tracked

**Methods**:
- `Create(ctx, object)` - Create K8s resource
- `Get(ctx, key, object)` - Get resource by name/namespace
- `List(ctx, list)` - List resources
- `Update(ctx, object)` - Update resource
- `Delete(ctx, object)` - Delete resource
- `Watch(object)` - Start watching resource type
- `StartCache()` - Initialize cache
- `GetConfig()` - Get REST config

**Default Labels/Annotations**:
- Creator label: `weave.io/creator: {username}`
- Updater label: `weave.io/updater: {username}`
- Platform label: `weave.io/platform: true`

### OAuth2 Integration

**Managers**: `OAuthManager`, `AuthProvider` interface

**Supported Providers**:
1. **GitHub**
   - Scope: `user:email`, `read:user`
   - Endpoint: https://github.com/login/oauth/
   - User Info: https://api.github.com/user

2. **WeChat**
   - Endpoint: https://open.weixin.qq.com/
   - User Info: WeChat's user API

**OAuth Flow**:
1. Client calls `/api/v1/auth/token` with `authType` and `authCode`
2. AuthController calls `OAuthManager.GetAuthProvider(authType)`
3. Provider exchanges code for access token via OAuth2
4. Provider fetches user info from OAuth provider
5. System creates/updates user with auth info
6. JWT token issued

**AuthInfo Storage**:
- `authType`: "github" or "wechat"
- `authId`: Provider's user ID
- `accessToken`: OAuth access token
- `refreshToken`: Optional refresh token
- `expiry`: Token expiration time

---

## Configuration

**File**: `config/app.yaml`

### Server Configuration
```yaml
server:
  env: "debug"                    # debug, release
  address: "127.0.0.1"           # Bind address
  port: 8080                      # Port
  gracefulShutdownPeriod: 30      # Shutdown timeout (seconds)
  jwtSecret: "weaveserver"        # JWT signing secret
  dbType: "mysql"                 # mysql, postgres, sqlite
  rateLimits:
    - limitType: "server"         # Server-wide rate limit
      burst: 500
      qps: 100
      cacheSize: 1
    - limitType: "ip"             # Per-IP rate limit
      burst: 50
      qps: 10
      cacheSize: 2048
```

### Database Configuration
```yaml
mysql:
  host: "localhost"
  port: 3306
  name: "go-test"
  user: "root"
  password: "1234567"
  migrate: true                   # Auto-migrate schema

postgres:
  host: "localhost"
  port: 5432
  name: "go-test-weave"
  user: "go-test"
  password: "go-test"
  migrate: false

sqlite:
  file: "./config/sqlite.db"
  migrate: false
```

### Redis Configuration
```yaml
redis:
  enable: true
  host: "localhost"
  port: 6379
  password: "123456"
```

### Docker Configuration
```yaml
docker:
  enable: true                    # Enable Docker integration
  host: "unix:///var/run/docker.sock"
```

### Kubernetes Configuration
```yaml
kubernetes:
  enable: true                    # Enable K8s integration
  watchResources:                 # Resources to watch
    - "Deployment.v1.apps"
    - "Pod.v1."
    - "Namespace.v1."
```

### OAuth Configuration
```yaml
oauth:
  github:
    clientId: "85db232fde2c9320ece7"
    clientSecret: ""              # Set before deployment
```

---

## Dependencies & Libraries

### Core Framework & HTTP
| Package | Version | Purpose |
|---------|---------|---------|
| gin-gonic/gin | 1.9.0 | Web framework |
| gin-contrib/cors | 1.4.0 | CORS middleware |
| gorilla/websocket | 1.5.0 | WebSocket support |

### Database & ORM
| Package | Version | Purpose |
|---------|---------|---------|
| gorm.io/gorm | 1.25.7 | ORM layer |
| gorm.io/driver/mysql | 1.5.3 | MySQL driver |
| gorm.io/driver/postgres | 1.5.0 | PostgreSQL driver |
| gorm.io/driver/sqlite | 1.5.5 | SQLite driver |

### Caching
| Package | Version | Purpose |
|---------|---------|---------|
| go-redis/redis | 8.11.5 | Redis client |

### Authentication & Crypto
| Package | Version | Purpose |
|---------|---------|---------|
| golang-jwt/jwt | 4.5.0 | JWT tokens |
| golang.org/x/crypto | 0.17.0 | Password hashing (bcrypt) |
| golang.org/x/oauth2 | 0.8.0 | OAuth2 flow |

### Kubernetes
| Package | Version | Purpose |
|---------|---------|---------|
| k8s.io/api | 0.26.1 | K8s API types |
| k8s.io/client-go | 0.26.1 | K8s client |
| k8s.io/apimachinery | 0.26.1 | K8s utilities |
| sigs.k8s.io/controller-runtime | 0.14.6 | K8s controller helpers |

### Docker
| Package | Version | Purpose |
|---------|---------|---------|
| docker/docker | 23.0.6 | Docker API client |
| docker/go-connections | 0.4.0 | Docker networking |

### Monitoring & Metrics
| Package | Version | Purpose |
|---------|---------|---------|
| prometheus/client_golang | 1.15.1 | Prometheus metrics |

### Logging & Tracing
| Package | Version | Purpose |
|---------|---------|---------|
| sirupsen/logrus | 1.9.0 | Structured logging |
| go-logr/logr | 1.2.4 | Log interface |
| bombsimon/logrusr | 2.0.1 | Logrus adapter for logr |

### API Documentation
| Package | Version | Purpose |
|---------|---------|---------|
| swaggo/swag | 1.16.1 | Swagger code generation |
| swaggo/gin-swagger | 1.6.0 | Swagger UI for Gin |
| swaggo/files | 1.0.1 | Swagger UI files |

### Utilities
| Package | Version | Purpose |
|---------|---------|---------|
| golang.org/x/time | 0.3.0 | Rate limiting |
| hashicorp/golang-lru | 2.0.2 | LRU cache |
| pkg/errors | 0.9.1 | Error handling |
| stretchr/testify | 1.8.2 | Testing assertions |

### Configuration
| Package | Version | Purpose |
|---------|---------|---------|
| gopkg.in/yaml.v2 | 2.4.0 | YAML parsing |

---

## Service Layer

### UserService

**Methods**:
- `List()` → `[]User` - Get all users
- `Get(id)` → `User` - Get user by ID
- `Create(user)` → `User` - Create new user with bcrypt password hashing
- `Update(id, user)` → `User` - Update user (re-hash password if provided)
- `Delete(id)` → error - Delete user
- `Validate(user)` → error - Validate user creation (name, password length)
- `Default(user)` → void - Set defaults (email if empty)
- `Auth(authUser)` → `User` - Authenticate with username/password
- `CreateOAuthUser(user)` → `User` - Create/get user from OAuth provider
- `GetGroups(id)` → `[]Group` - Get user's groups
- `AddRole(userId, roleId)` → error - Assign role to user
- `DelRole(userId, roleId)` → error - Remove role from user

**Validation Rules**:
- Username: required, not empty
- Password: minimum 6 characters (for creation)
- Email: auto-generated if empty (format: `{username}@qinng.io`)

### GroupService

**Methods**:
- `List()` → `[]Group` - Get all groups
- `Get(id)` → `Group` - Get group by ID
- `Create(user, group)` → `Group` - Create group (creates default roles)
- `Update(id, group)` → `Group` - Update group
- `Delete(id)` → error - Delete group
- `GetUsers(id)` → `[]User` - Get group members
- `AddUser(user, id)` → error - Add user to group
- `DelUser(user, id)` → error - Remove user from group

### PostService

**Methods**:
- `List()` → `[]Post` - Get all posts with like counts
- `Get(user, id)` → `Post` - Get post with like status for user
- `Create(user, post)` → `Post` - Create post
- `Update(id, post)` → `Post` - Update post
- `Delete(id)` → error - Delete post
- `IncView(id)` → error - Increment view count
- `AddLike(userId, postId)` → error - Like post
- `DelLike(userId, postId)` → error - Unlike post
- `GetLike(userId, postId)` → bool - Check if liked

### RBACService

**Methods**:
- `List()` → `[]Role` - Get all roles
- `Create(role)` → `Role` - Create role
- `Get(id)` → `Role` - Get role
- `Update(id, role)` → `Role` - Update role
- `Delete(id)` → error - Delete role
- `ListResources()` → `[]Resource` - Get available resources
- `ListOperations()` → `[]Operation` - Get available operations

### OAuthManager

**Methods**:
- `GetAuthProvider(authType)` → `AuthProvider` - Get OAuth provider (github/wechat)

**AuthProvider Interface**:
- `GetToken(code)` → `*oauth2.Token` - Exchange code for token
- `GetUserInfo(token)` → `*UserInfo` - Get user info from provider

---

## Entry Point & Server Startup

**Main Entry**: `main.go`

**Startup Process**:
1. Parse configuration from `config/app.yaml`
2. Initialize logger (logrus)
3. Create server instance:
   - Initialize database (MySQL/PostgreSQL/SQLite)
   - Initialize Redis client (if enabled)
   - Create Docker client (if enabled)
   - Create Kubernetes client (if enabled)
   - Create services and controllers
   - Initialize authorization system
4. Configure Gin engine:
   - Set mode (debug/release)
   - Add middleware in order
   - Register routes from controllers
5. Listen on `{address}:{port}`
6. Handle graceful shutdown (30 seconds by default)

**Graceful Shutdown**:
- Listens for SIGINT/SIGTERM
- Closes repository (database/cache)
- Closes containers client
- Shuts down HTTP server with timeout

---

## Key Implementation Details

### Password Hashing
- **Algorithm**: bcrypt (golang.org/x/crypto/bcrypt)
- **Cost**: DefaultCost (10)
- **Storage**: Only hashed passwords stored in database
- **Comparison**: bcrypt.CompareHashAndPassword()

### Soft Deletes
- Uses GORM soft delete feature
- Field: `deleted_at DATETIME NULL`
- Queries automatically exclude soft-deleted records
- Can be forcefully included with `.Unscoped()`

### Caching
- **Implementation**: Redis HSet (for user objects)
- **Cache Key Format**: `{table}:id`
- **Field**: User ID as string
- **Limitation**: No expiration (manual invalidation on update)
- **Fallback**: Queries database if cache miss

### Response Format
**Success** (Status 200):
```json
{
  "data": {...},
  "code": 0,
  "message": "success"
}
```

**Error** (Status varies):
```json
{
  "code": 1,
  "message": "error description"
}
```

### Request Tracing
- **ID**: Unique per request
- **Fields**: Method, path
- **Logging**: Slow requests >100ms
- **Logger**: Logrus integration

---

## Database Connection Patterns

### GORM Preloading
- `Preload("AuthInfos")` - Load associated auth info
- `Preload("Groups")` - Load user's groups
- `Preload("Roles")` - Load roles
- `Preload("Creator")` - Load creator user
- Nested: `Preload("Groups.Roles")` - Load groups and their roles

### Transactions
- Not explicitly shown in controllers
- Could be needed for multi-table operations

### Indexes
- Unique constraints on name fields
- Composite unique index on (user_id, post_id) for likes

---

## Metrics Exported (Prometheus)

Via `pkg/metrics/http.go`:

- `http_inflight_requests` - Gauge (method, path)
- `http_requests_total` - Counter (method, path, status_code)
- `http_requests_duration_seconds` - Histogram (method, path)

---

## Error Handling

**Pattern**:
- Most functions return `(*Type, error)` tuple
- Errors wrapped with context using `pkg/errors`
- Services validate before repository calls
- Controllers return appropriate HTTP status codes:
  - 200 - OK
  - 400 - Bad Request (validation, binding errors)
  - 401 - Unauthorized (no auth)
  - 403 - Forbidden (no permission)
  - 404 - Not Found
  - 500 - Internal Server Error (unexpected errors)
  - 429 - Too Many Requests (rate limit exceeded)

---

## Testing Considerations

**Test Files Present**:
- `pkg/authentication/jwt_test.go`
- `pkg/common/context_test.go`
- `pkg/common/helper_test.go`
- `pkg/common/response_test.go`

**Testing Framework**: testify/assert

---

## Python Rewrite Recommendations

### Framework Choice
**Recommended**: FastAPI
- Async support
- Auto OpenAPI/Swagger
- Type hints (matches Go's type safety)
- High performance
- Similar middleware pattern

**Alternative**: Flask with extensions
- Simpler if async not needed
- More Python-like

### Database ORM
**Recommended**: SQLAlchemy 2.0
- Multiple database support (MySQL, PostgreSQL, SQLite)
- Similar to GORM in functionality
- Rich ecosystem

### Authentication
**Recommended**: PyJWT + python-jose
- JWT handling
- Crypto operations

### Caching
**Recommended**: redis-py
- Direct Redis access
- Similar to Go implementation

### Kubernetes
**Recommended**: kubernetes-client
- Official K8s Python client

### Docker
**Recommended**: docker-py
- Official Docker Python client

### Monitoring
**Recommended**: prometheus-client
- Native Prometheus support

### Logging
**Recommended**: loguru or structlog
- Structured logging
- Similar to logrus

---

## Summary

This application is a **comprehensive web platform** with:
- **Core**: User/group/role management with RBAC
- **Content**: Blog/post system with likes/comments
- **Infrastructure**: Docker & Kubernetes integration
- **Security**: JWT-based auth, OAuth2 providers, authorization checks
- **Scalability**: Redis caching, rate limiting, monitoring
- **Flexibility**: Multiple database backends, configurable features

The architecture is **layered** (Controller → Service → Repository → DB) making it suitable for a straightforward Python rewrite using similar patterns.

