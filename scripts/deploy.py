#!/usr/bin/env python3
"""
WolfPy Deployment Script

This script handles deployment of WolfPy applications to various environments
including Docker, cloud platforms, and traditional servers.

Usage:
    python scripts/deploy.py --help
    python scripts/deploy.py docker --build
    python scripts/deploy.py docker --push
    python scripts/deploy.py heroku
    python scripts/deploy.py aws
"""

import argparse
import os
import subprocess
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional


class WolfPyDeployer:
    """WolfPy application deployer."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.docker_image = "wolfpy-app"
        self.docker_tag = "latest"
    
    def check_docker(self):
        """Check if Docker is available."""
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Docker not found. Please install Docker first.")
            return False
    
    def build_docker_image(self, tag: Optional[str] = None):
        """Build Docker image."""
        if not self.check_docker():
            return False
        
        tag = tag or self.docker_tag
        image_name = f"{self.docker_image}:{tag}"
        
        print(f"🐳 Building Docker image: {image_name}")
        
        try:
            subprocess.run(
                ["docker", "build", "-t", image_name, "."],
                cwd=self.project_root,
                check=True
            )
            print(f"✅ Docker image built: {image_name}")
            return True
        except subprocess.CalledProcessError:
            print("❌ Docker build failed")
            return False
    
    def push_docker_image(self, registry: str, tag: Optional[str] = None):
        """Push Docker image to registry."""
        if not self.check_docker():
            return False
        
        tag = tag or self.docker_tag
        local_image = f"{self.docker_image}:{tag}"
        remote_image = f"{registry}/{self.docker_image}:{tag}"
        
        print(f"🚀 Pushing Docker image to {registry}")
        
        try:
            # Tag for registry
            subprocess.run(
                ["docker", "tag", local_image, remote_image],
                check=True
            )
            
            # Push to registry
            subprocess.run(
                ["docker", "push", remote_image],
                check=True
            )
            
            print(f"✅ Image pushed: {remote_image}")
            return True
        except subprocess.CalledProcessError:
            print("❌ Docker push failed")
            return False
    
    def run_docker_container(self, port: int = 8000, env_file: Optional[str] = None):
        """Run Docker container locally."""
        if not self.check_docker():
            return False
        
        image_name = f"{self.docker_image}:{self.docker_tag}"
        
        cmd = [
            "docker", "run",
            "-p", f"{port}:8000",
            "--rm",
            "--name", "wolfpy-app-local"
        ]
        
        if env_file and Path(env_file).exists():
            cmd.extend(["--env-file", env_file])
        
        cmd.append(image_name)
        
        print(f"🐳 Running Docker container on port {port}")
        print("   Press Ctrl+C to stop")
        
        try:
            subprocess.run(cmd, cwd=self.project_root)
            return True
        except KeyboardInterrupt:
            print("\n⏹️  Container stopped")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to run container")
            return False
    
    def deploy_to_heroku(self):
        """Deploy to Heroku."""
        print("🚀 Deploying to Heroku...")
        
        # Check if Heroku CLI is available
        try:
            subprocess.run(["heroku", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Heroku CLI not found. Please install it first.")
            return False
        
        # Create Procfile if it doesn't exist
        procfile_path = self.project_root / "Procfile"
        if not procfile_path.exists():
            with open(procfile_path, "w") as f:
                f.write("web: gunicorn --config gunicorn.conf.py app:app\n")
            print("✅ Created Procfile")
        
        # Create runtime.txt if it doesn't exist
        runtime_path = self.project_root / "runtime.txt"
        if not runtime_path.exists():
            with open(runtime_path, "w") as f:
                f.write("python-3.11.6\n")
            print("✅ Created runtime.txt")
        
        # Deploy
        try:
            subprocess.run(["git", "add", "."], cwd=self.project_root, check=True)
            subprocess.run(
                ["git", "commit", "-m", "Deploy to Heroku"],
                cwd=self.project_root
            )
            subprocess.run(
                ["git", "push", "heroku", "main"],
                cwd=self.project_root,
                check=True
            )
            print("✅ Deployed to Heroku successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Heroku deployment failed")
            return False
    
    def create_kubernetes_manifests(self):
        """Create Kubernetes deployment manifests."""
        print("☸️  Creating Kubernetes manifests...")
        
        k8s_dir = self.project_root / "k8s"
        k8s_dir.mkdir(exist_ok=True)
        
        # Deployment manifest
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "wolfpy-app"},
            "spec": {
                "replicas": 3,
                "selector": {"matchLabels": {"app": "wolfpy-app"}},
                "template": {
                    "metadata": {"labels": {"app": "wolfpy-app"}},
                    "spec": {
                        "containers": [{
                            "name": "wolfpy-app",
                            "image": f"{self.docker_image}:{self.docker_tag}",
                            "ports": [{"containerPort": 8000}],
                            "env": [
                                {"name": "WOLFPY_ENV", "value": "production"},
                                {"name": "PORT", "value": "8000"}
                            ],
                            "livenessProbe": {
                                "httpGet": {"path": "/health", "port": 8000},
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10
                            },
                            "readinessProbe": {
                                "httpGet": {"path": "/health", "port": 8000},
                                "initialDelaySeconds": 5,
                                "periodSeconds": 5
                            }
                        }]
                    }
                }
            }
        }
        
        # Service manifest
        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": "wolfpy-service"},
            "spec": {
                "selector": {"app": "wolfpy-app"},
                "ports": [{"port": 80, "targetPort": 8000}],
                "type": "LoadBalancer"
            }
        }
        
        # Ingress manifest
        ingress = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": "wolfpy-ingress",
                "annotations": {
                    "kubernetes.io/ingress.class": "nginx",
                    "cert-manager.io/cluster-issuer": "letsencrypt-prod"
                }
            },
            "spec": {
                "tls": [{
                    "hosts": ["your-domain.com"],
                    "secretName": "wolfpy-tls"
                }],
                "rules": [{
                    "host": "your-domain.com",
                    "http": {
                        "paths": [{
                            "path": "/",
                            "pathType": "Prefix",
                            "backend": {
                                "service": {
                                    "name": "wolfpy-service",
                                    "port": {"number": 80}
                                }
                            }
                        }]
                    }
                }]
            }
        }
        
        # Write manifests
        with open(k8s_dir / "deployment.yaml", "w") as f:
            yaml.dump(deployment, f, default_flow_style=False)
        
        with open(k8s_dir / "service.yaml", "w") as f:
            yaml.dump(service, f, default_flow_style=False)
        
        with open(k8s_dir / "ingress.yaml", "w") as f:
            yaml.dump(ingress, f, default_flow_style=False)
        
        print("✅ Kubernetes manifests created in k8s/ directory")
        print("   Update the ingress host and apply with:")
        print("   kubectl apply -f k8s/")
        
        return True
    
    def create_docker_compose_production(self):
        """Create production docker-compose configuration."""
        print("🐳 Creating production docker-compose configuration...")
        
        compose_prod = {
            "version": "3.8",
            "services": {
                "web": {
                    "image": f"{self.docker_image}:{self.docker_tag}",
                    "ports": ["80:8000"],
                    "environment": [
                        "WOLFPY_ENV=production",
                        "DEBUG=False"
                    ],
                    "restart": "unless-stopped",
                    "depends_on": ["redis", "postgres"]
                },
                "redis": {
                    "image": "redis:7-alpine",
                    "restart": "unless-stopped"
                },
                "postgres": {
                    "image": "postgres:15-alpine",
                    "environment": [
                        "POSTGRES_DB=wolfpy",
                        "POSTGRES_USER=wolfpy",
                        "POSTGRES_PASSWORD=${POSTGRES_PASSWORD}"
                    ],
                    "volumes": ["postgres_data:/var/lib/postgresql/data"],
                    "restart": "unless-stopped"
                }
            },
            "volumes": {
                "postgres_data": None
            }
        }
        
        with open(self.project_root / "docker-compose.prod.yml", "w") as f:
            yaml.dump(compose_prod, f, default_flow_style=False)
        
        print("✅ Production docker-compose.prod.yml created")
        return True
    
    def generate_env_template(self):
        """Generate environment variables template."""
        print("📝 Generating environment template...")
        
        env_template = """# WolfPy Environment Configuration
# Copy this file to .env and fill in your values

# Application
WOLFPY_ENV=production
DEBUG=False
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/wolfpy
POSTGRES_DB=wolfpy
POSTGRES_USER=wolfpy
POSTGRES_PASSWORD=your-postgres-password

# Redis
REDIS_URL=redis://localhost:6379/0

# Server
PORT=8000
GUNICORN_WORKERS=4

# Monitoring (optional)
GRAFANA_PASSWORD=admin

# SSL (optional)
SSL_CERTFILE=/path/to/cert.pem
SSL_KEYFILE=/path/to/key.pem
"""
        
        with open(self.project_root / ".env.template", "w") as f:
            f.write(env_template)
        
        print("✅ Environment template created: .env.template")
        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="WolfPy deployment tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Docker commands
    docker_parser = subparsers.add_parser("docker", help="Docker operations")
    docker_group = docker_parser.add_mutually_exclusive_group(required=True)
    docker_group.add_argument("--build", action="store_true", help="Build Docker image")
    docker_group.add_argument("--run", action="store_true", help="Run Docker container")
    docker_group.add_argument("--push", type=str, help="Push to registry")
    docker_parser.add_argument("--tag", type=str, help="Docker tag")
    docker_parser.add_argument("--port", type=int, default=8000, help="Port for local run")
    
    # Platform deployments
    subparsers.add_parser("heroku", help="Deploy to Heroku")
    subparsers.add_parser("k8s", help="Generate Kubernetes manifests")
    
    # Configuration generators
    subparsers.add_parser("env", help="Generate environment template")
    subparsers.add_parser("compose-prod", help="Generate production docker-compose")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Find project root
    project_root = Path(__file__).parent.parent
    deployer = WolfPyDeployer(project_root)
    
    success = True
    
    if args.command == "docker":
        if args.build:
            success = deployer.build_docker_image(args.tag)
        elif args.run:
            success = deployer.run_docker_container(args.port)
        elif args.push:
            success = deployer.push_docker_image(args.push, args.tag)
    elif args.command == "heroku":
        success = deployer.deploy_to_heroku()
    elif args.command == "k8s":
        success = deployer.create_kubernetes_manifests()
    elif args.command == "env":
        success = deployer.generate_env_template()
    elif args.command == "compose-prod":
        success = deployer.create_docker_compose_production()
    else:
        print(f"❌ Unknown command: {args.command}")
        success = False
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
