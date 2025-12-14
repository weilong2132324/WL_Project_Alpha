FROM golang:1.21-alpine AS build
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o app main.go

FROM alpine:latest AS runtime
WORKDIR /app
COPY --from=build /app/app .
EXPOSE 8080
CMD ["./app"]