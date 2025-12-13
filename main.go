package main

import (
	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()

	// LOGIN
	r.POST("/api/v1/auth/token", func(c *gin.Context) {
		if c.PostForm("username") == "admin" && c.PostForm("password") == "123456" {
			c.JSON(200, gin.H{"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE5OTk5OTk5OTl9.signature"})
			return
		}
		c.JSON(401, gin.H{"message": "invalid credentials"})
	})

	// DASHBOARD ENDPOINTS (FRONTEND NEEDS THESE)
	r.GET("/healthz", func(c *gin.Context) { c.JSON(200, gin.H{"status": "ok"}) })
	r.GET("/api/v1/namespaces", func(c *gin.Context) { c.JSON(200, gin.H{"items": []gin.H{{"metadata": gin.H{"name": "default"}}}}) })
	r.GET("/api/v1/users", func(c *gin.Context) {
		c.JSON(200, gin.H{"items": []gin.H{{"id": 1, "username": "admin", "group_id": 1}}})
	})
	r.GET("/api/v1/groups", func(c *gin.Context) { c.JSON(200, gin.H{"items": []gin.H{{"id": 1, "name": "root"}}}) })
	r.GET("/api/v1/containers", func(c *gin.Context) {
		c.JSON(200, gin.H{"items": []gin.H{{"id": "go-mysql", "name": "go-mysql", "status": "running"}}})
	})
	r.GET("/api/v1/posts", func(c *gin.Context) {
		c.JSON(200, gin.H{"items": []gin.H{{"id": 1, "title": "Welcome!", "content": "Dashboard working!"}}})
	})
	r.GET("/api/v1/resources", func(c *gin.Context) { c.JSON(200, gin.H{"items": []gin.H{{"name": "dashboard"}}}) })

	r.Run(":8080")
}
