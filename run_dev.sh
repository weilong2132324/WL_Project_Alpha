#! /bin/bash

cleanup(){
    echo "Stopping Servers..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit
}

trap cleanup SIGINT

echo "Starting WL_Project_Alpha_Development"

echo "Starting Go backend"
go mod tidy & go run go run main.go & BACKEND_PID=$!

echo "Starting Vue Frontend"
cd web
npm run install & npm run dev & FRONTEND_PID=$!

echo "Both services running. Press Ctrl+C to stop." 
wait