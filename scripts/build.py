#!/usr/bin/env python3
"""
WolfPy Build Script

This script handles building and packaging WolfPy for distribution.
It supports building for different environments and publishing to PyPI.

Usage:
    python scripts/build.py --help
    python scripts/build.py build
    python scripts/build.py publish --test
    python scripts/build.py publish --production
"""

import argparse
import os
import subprocess
import sys
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional


class WolfPyBuilder:
    """WolfPy package builder and publisher."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.dist_dir = project_root / "dist"
        self.build_dir = project_root / "build"
        
    def clean(self):
        """Clean build artifacts."""
        print("🧹 Cleaning build artifacts...")
        
        # Remove build directories
        for dir_path in [self.dist_dir, self.build_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"   Removed {dir_path}")
        
        # Remove egg-info directories
        for egg_info in self.project_root.glob("*.egg-info"):
            if egg_info.is_dir():
                shutil.rmtree(egg_info)
                print(f"   Removed {egg_info}")
        
        # Remove __pycache__ directories
        for pycache in self.project_root.rglob("__pycache__"):
            if pycache.is_dir():
                shutil.rmtree(pycache)
        
        print("✅ Clean completed")
    
    def check_dependencies(self):
        """Check if required build dependencies are installed."""
        print("🔍 Checking build dependencies...")
        
        required_packages = ["build", "twine", "wheel"]
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"   ✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"   ❌ {package}")
        
        if missing_packages:
            print(f"\n❌ Missing required packages: {', '.join(missing_packages)}")
            print("Install them with:")
            print(f"   pip install {' '.join(missing_packages)}")
            return False
        
        print("✅ All dependencies available")
        return True
    
    def validate_project(self):
        """Validate project structure and configuration."""
        print("🔍 Validating project structure...")
        
        required_files = [
            "pyproject.toml",
            "README.md",
            "LICENSE",
            "src/wolfpy/__init__.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
                print(f"   ❌ {file_path}")
            else:
                print(f"   ✅ {file_path}")
        
        if missing_files:
            print(f"\n❌ Missing required files: {', '.join(missing_files)}")
            return False
        
        # Check if version is set
        try:
            result = subprocess.run(
                [sys.executable, "-c", "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            version = result.stdout.strip()
            print(f"   ✅ Version: {version}")
        except Exception as e:
            print(f"   ❌ Could not read version: {e}")
            return False
        
        print("✅ Project validation passed")
        return True
    
    def run_tests(self):
        """Run tests before building."""
        print("🧪 Running tests...")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
                cwd=self.project_root,
                check=True
            )
            print("✅ All tests passed")
            return True
        except subprocess.CalledProcessError:
            print("❌ Tests failed")
            return False
        except FileNotFoundError:
            print("⚠️  pytest not found, skipping tests")
            return True
    
    def build_package(self):
        """Build the package."""
        print("📦 Building package...")
        
        try:
            # Build source distribution and wheel
            subprocess.run(
                [sys.executable, "-m", "build"],
                cwd=self.project_root,
                check=True
            )
            
            # List built files
            if self.dist_dir.exists():
                built_files = list(self.dist_dir.glob("*"))
                print("✅ Package built successfully:")
                for file_path in built_files:
                    size = file_path.stat().st_size
                    print(f"   📄 {file_path.name} ({size:,} bytes)")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Build failed: {e}")
            return False
    
    def check_package(self):
        """Check the built package with twine."""
        print("🔍 Checking package...")
        
        try:
            subprocess.run(
                [sys.executable, "-m", "twine", "check", "dist/*"],
                cwd=self.project_root,
                check=True
            )
            print("✅ Package check passed")
            return True
        except subprocess.CalledProcessError:
            print("❌ Package check failed")
            return False
    
    def publish_to_testpypi(self):
        """Publish package to TestPyPI."""
        print("🚀 Publishing to TestPyPI...")
        
        try:
            subprocess.run(
                [
                    sys.executable, "-m", "twine", "upload",
                    "--repository", "testpypi",
                    "dist/*"
                ],
                cwd=self.project_root,
                check=True
            )
            print("✅ Published to TestPyPI successfully")
            print("🔗 Check your package at: https://test.pypi.org/project/wolfpy/")
            return True
        except subprocess.CalledProcessError:
            print("❌ TestPyPI upload failed")
            return False
    
    def publish_to_pypi(self):
        """Publish package to PyPI."""
        print("🚀 Publishing to PyPI...")
        
        # Confirm with user
        confirm = input("⚠️  This will publish to production PyPI. Continue? (yes/no): ")
        if confirm.lower() != "yes":
            print("❌ Publication cancelled")
            return False
        
        try:
            subprocess.run(
                [sys.executable, "-m", "twine", "upload", "dist/*"],
                cwd=self.project_root,
                check=True
            )
            print("✅ Published to PyPI successfully")
            print("🔗 Check your package at: https://pypi.org/project/wolfpy/")
            return True
        except subprocess.CalledProcessError:
            print("❌ PyPI upload failed")
            return False
    
    def build_workflow(self, run_tests: bool = True):
        """Complete build workflow."""
        print("🐺 Starting WolfPy build workflow...")
        print("=" * 50)
        
        steps = [
            ("Clean", self.clean),
            ("Check dependencies", self.check_dependencies),
            ("Validate project", self.validate_project),
        ]
        
        if run_tests:
            steps.append(("Run tests", self.run_tests))
        
        steps.extend([
            ("Build package", self.build_package),
            ("Check package", self.check_package),
        ])
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            if not step_func():
                print(f"\n❌ Build failed at step: {step_name}")
                return False
        
        print("\n🎉 Build completed successfully!")
        return True
    
    def publish_workflow(self, target: str):
        """Complete publish workflow."""
        print(f"🐺 Starting WolfPy publish workflow (target: {target})...")
        print("=" * 50)
        
        # First build if needed
        if not self.dist_dir.exists() or not list(self.dist_dir.glob("*")):
            if not self.build_workflow():
                return False
        
        # Publish
        if target == "testpypi":
            return self.publish_to_testpypi()
        elif target == "pypi":
            return self.publish_to_pypi()
        else:
            print(f"❌ Unknown publish target: {target}")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="WolfPy build and publish tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Build command
    build_parser = subparsers.add_parser("build", help="Build the package")
    build_parser.add_argument("--no-tests", action="store_true", help="Skip running tests")
    
    # Publish command
    publish_parser = subparsers.add_parser("publish", help="Publish the package")
    publish_group = publish_parser.add_mutually_exclusive_group(required=True)
    publish_group.add_argument("--test", action="store_true", help="Publish to TestPyPI")
    publish_group.add_argument("--production", action="store_true", help="Publish to PyPI")
    
    # Clean command
    subparsers.add_parser("clean", help="Clean build artifacts")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Find project root
    project_root = Path(__file__).parent.parent
    builder = WolfPyBuilder(project_root)
    
    if args.command == "build":
        success = builder.build_workflow(run_tests=not args.no_tests)
    elif args.command == "publish":
        target = "testpypi" if args.test else "pypi"
        success = builder.publish_workflow(target)
    elif args.command == "clean":
        builder.clean()
        success = True
    else:
        print(f"❌ Unknown command: {args.command}")
        success = False
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
