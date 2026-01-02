"""Docker API endpoints"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.rbac_service import RBACService
from app.utils.errors import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/docker", tags=["docker"])

try:
    import docker
    docker_available = True
except ImportError:
    docker_available = False
    logger.warning("Docker SDK not available")


def get_docker_client():
    """Get Docker client"""
    if not docker_available:
        raise BadRequestException("Docker SDK not available")
    
    try:
        return docker.from_env()
    except Exception as e:
        raise BadRequestException(f"Failed to connect to Docker: {str(e)}")


@router.get("/containers")
async def list_containers(filters: Optional[str] = None):
    """List Docker containers"""
    if not docker_available:
        raise BadRequestException("Docker is not enabled")
    
    try:
        client = get_docker_client()
        containers = client.containers.list(all=True)
        
        return {
            "success": True,
            "data": [
                {
                    "id": c.id[:12],
                    "name": c.name,
                    "image": c.image.tags[0] if c.image.tags else "unknown",
                    "status": c.status,
                    "state": c.state,
                }
                for c in containers
            ]
        }
    except Exception as e:
        logger.error(f"Failed to list containers: {e}")
        raise BadRequestException(f"Failed to list containers: {str(e)}")


@router.get("/containers/{container_id}")
async def get_container(container_id: str):
    """Get container details"""
    if not docker_available:
        raise BadRequestException("Docker is not enabled")
    
    try:
        client = get_docker_client()
        container = client.containers.get(container_id)
        
        return {
            "success": True,
            "data": {
                "id": container.id[:12],
                "name": container.name,
                "image": container.image.tags[0] if container.image.tags else "unknown",
                "status": container.status,
                "state": container.state,
                "ports": container.ports,
                "labels": container.labels,
            }
        }
    except docker.errors.NotFound:
        raise NotFoundException(f"Container {container_id} not found")
    except Exception as e:
        logger.error(f"Failed to get container: {e}")
        raise BadRequestException(f"Failed to get container: {str(e)}")


@router.post("/containers/{container_id}/start")
async def start_container(container_id: str):
    """Start a container"""
    if not docker_available:
        raise BadRequestException("Docker is not enabled")
    
    try:
        client = get_docker_client()
        container = client.containers.get(container_id)
        container.start()
        
        return {"success": True, "message": "Container started"}
    except docker.errors.NotFound:
        raise NotFoundException(f"Container {container_id} not found")
    except Exception as e:
        logger.error(f"Failed to start container: {e}")
        raise BadRequestException(f"Failed to start container: {str(e)}")


@router.post("/containers/{container_id}/stop")
async def stop_container(container_id: str):
    """Stop a container"""
    if not docker_available:
        raise BadRequestException("Docker is not enabled")
    
    try:
        client = get_docker_client()
        container = client.containers.get(container_id)
        container.stop()
        
        return {"success": True, "message": "Container stopped"}
    except docker.errors.NotFound:
        raise NotFoundException(f"Container {container_id} not found")
    except Exception as e:
        logger.error(f"Failed to stop container: {e}")
        raise BadRequestException(f"Failed to stop container: {str(e)}")


@router.delete("/containers/{container_id}")
async def delete_container(container_id: str):
    """Delete a container"""
    if not docker_available:
        raise BadRequestException("Docker is not enabled")
    
    try:
        client = get_docker_client()
        container = client.containers.get(container_id)
        container.remove(force=True)
        
        return {"success": True, "message": "Container deleted"}
    except docker.errors.NotFound:
        raise NotFoundException(f"Container {container_id} not found")
    except Exception as e:
        logger.error(f"Failed to delete container: {e}")
        raise BadRequestException(f"Failed to delete container: {str(e)}")
