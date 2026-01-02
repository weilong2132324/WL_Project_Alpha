"""Kubernetes API endpoints"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.errors import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/kubernetes", tags=["kubernetes"])

try:
    from kubernetes import client, config, watch
    kubernetes_available = True
except ImportError:
    kubernetes_available = False
    logger.warning("Kubernetes client not available")


def get_kubernetes_client():
    """Get Kubernetes API client"""
    if not kubernetes_available:
        raise BadRequestException("Kubernetes client not available")
    
    try:
        config.load_incluster_config()
    except config.config_exception.ConfigException:
        try:
            config.load_kube_config()
        except config.config_exception.ConfigException:
            raise BadRequestException("Failed to load Kubernetes configuration")
    
    return client.CoreV1Api(), client.AppsV1Api()


@router.get("/namespaces")
async def list_namespaces():
    """List Kubernetes namespaces"""
    if not kubernetes_available:
        raise BadRequestException("Kubernetes is not enabled")
    
    try:
        v1, _ = get_kubernetes_client()
        namespaces = v1.list_namespace()
        
        return {
            "success": True,
            "data": [
                {
                    "name": ns.metadata.name,
                    "status": ns.status.phase,
                    "created_at": ns.metadata.creation_timestamp,
                }
                for ns in namespaces.items
            ]
        }
    except Exception as e:
        logger.error(f"Failed to list namespaces: {e}")
        raise BadRequestException(f"Failed to list namespaces: {str(e)}")


@router.get("/pods")
async def list_pods(namespace: str = "default"):
    """List pods in namespace"""
    if not kubernetes_available:
        raise BadRequestException("Kubernetes is not enabled")
    
    try:
        v1, _ = get_kubernetes_client()
        pods = v1.list_namespaced_pod(namespace)
        
        return {
            "success": True,
            "data": [
                {
                    "name": pod.metadata.name,
                    "status": pod.status.phase,
                    "namespace": pod.metadata.namespace,
                    "containers": [c.name for c in pod.spec.containers],
                }
                for pod in pods.items
            ]
        }
    except Exception as e:
        logger.error(f"Failed to list pods: {e}")
        raise BadRequestException(f"Failed to list pods: {str(e)}")


@router.get("/deployments")
async def list_deployments(namespace: str = "default"):
    """List deployments in namespace"""
    if not kubernetes_available:
        raise BadRequestException("Kubernetes is not enabled")
    
    try:
        _, apps_v1 = get_kubernetes_client()
        deployments = apps_v1.list_namespaced_deployment(namespace)
        
        return {
            "success": True,
            "data": [
                {
                    "name": dep.metadata.name,
                    "namespace": dep.metadata.namespace,
                    "replicas": dep.spec.replicas,
                    "ready_replicas": dep.status.ready_replicas or 0,
                }
                for dep in deployments.items
            ]
        }
    except Exception as e:
        logger.error(f"Failed to list deployments: {e}")
        raise BadRequestException(f"Failed to list deployments: {str(e)}")


@router.get("/pods/{pod_id}")
async def get_pod(pod_id: str, namespace: str = "default"):
    """Get pod details"""
    if not kubernetes_available:
        raise BadRequestException("Kubernetes is not enabled")
    
    try:
        v1, _ = get_kubernetes_client()
        pod = v1.read_namespaced_pod(pod_id, namespace)
        
        return {
            "success": True,
            "data": {
                "name": pod.metadata.name,
                "status": pod.status.phase,
                "namespace": pod.metadata.namespace,
                "containers": [
                    {
                        "name": c.name,
                        "image": c.image,
                        "ports": [p.container_port for p in (c.ports or [])],
                    }
                    for c in pod.spec.containers
                ],
            }
        }
    except Exception as e:
        logger.error(f"Failed to get pod: {e}")
        raise NotFoundException(f"Pod {pod_id} not found")


@router.delete("/pods/{pod_id}")
async def delete_pod(pod_id: str, namespace: str = "default"):
    """Delete a pod"""
    if not kubernetes_available:
        raise BadRequestException("Kubernetes is not enabled")
    
    try:
        v1, _ = get_kubernetes_client()
        v1.delete_namespaced_pod(pod_id, namespace)
        
        return {"success": True, "message": "Pod deleted"}
    except Exception as e:
        logger.error(f"Failed to delete pod: {e}")
        raise BadRequestException(f"Failed to delete pod: {str(e)}")
