#! /bin/bash

export DB_CONTAINER_NAME="sql_dev_container"
export DB_NAME="go-test"
export DB_PASSWORD="password"
export DB_PORT=3306

BACKEND_PID=""
FRONTEND_PID=""

cleanup(){
    echo "Stopping Servers..."
    # Check if variables are set before killing
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID
    fi
    
    echo "Stopping MySQL Container..."
    docker stop $DB_CONTAINER_NAME
    exit
}

trap cleanup SIGINT

echo "Starting WL_Project_Alpha_Development"

echo "Setting up MySQL Database..."
# Remove old container if it exists
docker rm -f $DB_CONTAINER_NAME 2> /dev/null 

# Docker run command to start MySQL container
docker run -d --name "$DB_CONTAINER_NAME" \
-e MYSQL_ROOT_PASSWORD="$DB_PASSWORD" \
-e MYSQL_DATABASE="$DB_NAME" \
-p "$DB_PORT:3306" \
-v "$(pwd)/scripts/mysql.sql:/docker-entrypoint-initdb.d/init.sql" mysql:8.0

echo "Waiting for Database to start..."
sleep 10

echo "Starting backend server..."
go mod tidy
go run main.go & 
BACKEND_PID=$!

echo "Starting frontend server..."
cd web
npm install
npm run dev & 
FRONTEND_PID=$!

cd ..
echo "Both services running (PIDs: Backend=$BACKEND_PID, Frontend=$FRONTEND_PID)."
echo "Press Ctrl+C to stop."
wait
