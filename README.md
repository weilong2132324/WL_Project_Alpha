# WL-Project-Alpha

## <ins>Technology Stack<ins>
Frontend - Vue3
Backend - Go
Database - SQL

## <ins>Features<ins>
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

## <ins>Get started<ins>
Before starting, install the following:  
(1) Golang (https://go.dev/)  
(2) Docker (https://docs.docker.com/engine/install/)  
(3) NodeJS (https://nodejs.org/en/download/)  

### <ins>Getting the Project running<ins>

### Running the containers individually
#### <ins>FE<ins>
If you have not downloaded the dependencies:  
- npm install  
  --> Reads the package.json file. Downloads all listed dependencies into a folder named node_modules. Creates or updates the package-lock.json file to lock in specific versions.

If all dependencies are already downloaded, run the following commands:  
- npm run dev

#### <ins>BE<ins>
If you have not downloaded the dependencies:  
- go mod tidy

If all dependencies are already downloaded, run the following commands:
- go run main.go

#### <ins>SQL<ins>
 To get the database container up and running, run this command:

 docker run --name mysql-new -e MYSQL_ROOT_PASSWORD=password -e MYSQL_DATABASE=go-test -v $(pwd)/scripts/mysql.sql:/docker-entrypoint-initdb.d/init.sql mysql:8.0

### Running the containers together
docker compose up --build