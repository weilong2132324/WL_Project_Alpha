# go-web-init


Run ui with docker(no server and databases)
```bash
docker run -d -p 8080:80 --name go-frontend makeok/go-frontend:mock
```

## Features
Server support features:
- Restful api, write by gin
- MVC structure
- Postgres/mysql/sqlite storage, via gorm
- Swagger doc, support by swag
- Structured log, support by logrus
- Prometheus monitor
- PProf debug
- Graceful shutdown
- Authentication, support jwt
- Request rate limit, server level or user ip
- OAuth Login and store hashed password
- Redis cache
- RBAC supported
- Container application management, support docker and kubernetes
- Post management

Frontend support features:
- Vue3 supported
- UI with element-plus
- Build with vite
- Charts integration, support by echarts
- WebShell supported
- Windi CSS
- OAuth Login
- Web code editor, support by codemirror
- MarkDown preview and editor

## Get started
Before starting, install the following:
(1) Golang (https://go.dev/)
(2) Docker (https://docs.docker.com/engine/install/)
(3) NodeJS (https://nodejs.org/en/download/)

### Run server

Env:
- golang (1.18 or later)

Install dependencies, postgresql/mysql/sqlite, redis, swag 
```bash
make init
```

run locally
```bash
make run
```

run server in docker
```bash
# build image
make docker-build-server
# run server
make docker-run-server
```

> For Windows, you can run script in [Makefile](./Makefile) manually

### Test api
See more api in http://localhost:8080/index
See swagger http://localhost:8080/swagger/index.html#/

Register user
```bash
curl -XPOST http://localhost:8080/api/v1/auth/user -d '{"name": "zhang3", "email": "zhang3@t.com","password": "123456"}'
```

Login, get jwt token
> Only admin user can access any apis, other user need create RBAC policy
```bash
curl -XPOST http://localhost:8080/api/v1/auth/token -d '{"name": "admin", "password": "123456"}'
```
Response as follows, set token in `Authorization` Header
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "token": "xxx",
    "describe": "set token in Authorization Header, [Authorization: Bearer {token}]"
  }
}
```

Get users
```bash
token=xxx
curl -X 'GET' 'http://localhost:8080/api/v1/users' -H "Authorization: Bearer $token"
```

### Run UI
Assume you have installed `Nodejs`, if not, install it by [nvm](https://github.com/nvm-sh/nvm#install--update-script)

Run ui with mockjs
```bash
cd web
npm run mock
```

If your frontend deploy in the remote, please change `server.host` and `server.https` in [vite.config.js](./web/vite.config.js).

Run ui with command `make ui` or
```bash
cd web
npm i
npm run dev 
```

Default admin user `admin/123456`
or demo user `demo/123456`

> Only admin user can access all api, other user must config RBAC at first

Explore in http://127.0.0.1:8081

run frontend in docker
```bash
# build image
make docker-build-ui
# run frontend
make docker-run-ui
```

More ui in [img](./document/img/)

- Login page
![login](./document/img/login.png)

- Dashboard page
![dashboard](./document/img/dashboard.png)

- App page
![app](./document/img/app.png)

- Webshell page
![webshell](./document/img/webshell.png)

- Blog list
![Blog](./document/img/blog.png)

- Article
![article](./document/img/document.png)

### Documents
- [Contributing](./CONTRIBUTING.md), contributing details
- [Config](./config/app.yaml), your can enable docker/kubernetes in config
- [OAuth](./document/oauth.md)
- [RBAC](./document/authentication.md)
