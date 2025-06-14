#!/usr/bin/env python3
"""
WolfPy Release Script

This script automates the release process for WolfPy, including:
- Version bumping
- Changelog updates
- Git tagging
- PyPI publishing
- GitHub release creation
"""

import os
import sys
import subprocess
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    import requests
    import toml
except ImportError:
    print("Missing dependencies. Install with: pip install requests toml")
    sys.exit(1)


class ReleaseManager:
    """Manages the release process for WolfPy."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.pyproject_path = project_root / "pyproject.toml"
        self.changelog_path = project_root / "CHANGELOG.md"
        
    def get_current_version(self) -> str:
        """Get the current version from pyproject.toml."""
        with open(self.pyproject_path, 'r') as f:
            data = toml.load(f)
        return data['project']['version']
    
    def bump_version(self, version_type: str) -> str:
        """Bump version based on type (major, minor, patch)."""
        current = self.get_current_version()
        major, minor, patch = map(int, current.split('.'))
        
        if version_type == 'major':
            major += 1
            minor = 0
            patch = 0
        elif version_type == 'minor':
            minor += 1
            patch = 0
        elif version_type == 'patch':
            patch += 1
        else:
            raise ValueError(f"Invalid version type: {version_type}")
        
        new_version = f"{major}.{minor}.{patch}"
        
        # Update pyproject.toml
        with open(self.pyproject_path, 'r') as f:
            content = f.read()
        
        content = re.sub(
            r'version = "[^"]*"',
            f'version = "{new_version}"',
            content
        )
        
        with open(self.pyproject_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Version bumped from {current} to {new_version}")
        return new_version
    
    def update_changelog(self, version: str, changes: str):
        """Update CHANGELOG.md with new version."""
        date = datetime.now().strftime("%Y-%m-%d")
        
        with open(self.changelog_path, 'r') as f:
            content = f.read()
        
        # Find the first ## heading and insert new version before it
        new_entry = f"""## [{version}] - {date}

{changes}

"""
        
        # Insert after the first line (title)
        lines = content.split('\n')
        lines.insert(2, new_entry)
        
        with open(self.changelog_path, 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"✅ Updated CHANGELOG.md for version {version}")
    
    def run_tests(self) -> bool:
        """Run the test suite."""
        print("🧪 Running tests...")
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/", "-v"],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ All tests passed")
            return True
        else:
            print("❌ Tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False
    
    def run_linting(self) -> bool:
        """Run linting checks."""
        print("🔍 Running linting checks...")
        
        # Run flake8
        result = subprocess.run(
            ["flake8", "src/wolfpy", "tests"],
            cwd=self.project_root,
            capture_output=True
        )
        
        if result.returncode != 0:
            print("❌ Linting failed")
            return False
        
        # Run black check
        result = subprocess.run(
            ["black", "--check", "src/wolfpy", "tests"],
            cwd=self.project_root,
            capture_output=True
        )
        
        if result.returncode != 0:
            print("❌ Code formatting check failed")
            return False
        
        print("✅ Linting passed")
        return True
    
    def build_package(self) -> bool:
        """Build the package for distribution."""
        print("📦 Building package...")
        
        # Clean previous builds
        subprocess.run(["rm", "-rf", "dist/", "build/"], cwd=self.project_root)
        
        # Build package
        result = subprocess.run(
            ["python", "-m", "build"],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Package built successfully")
            return True
        else:
            print("❌ Package build failed:")
            print(result.stdout)
            print(result.stderr)
            return False
    
    def publish_to_pypi(self, test: bool = False) -> bool:
        """Publish package to PyPI."""
        repository = "testpypi" if test else "pypi"
        print(f"🚀 Publishing to {'Test ' if test else ''}PyPI...")
        
        cmd = ["python", "-m", "twine", "upload"]
        if test:
            cmd.extend(["--repository", "testpypi"])
        cmd.append("dist/*")
        
        result = subprocess.run(cmd, cwd=self.project_root)
        
        if result.returncode == 0:
            print(f"✅ Published to {'Test ' if test else ''}PyPI successfully")
            return True
        else:
            print(f"❌ Failed to publish to {'Test ' if test else ''}PyPI")
            return False
    
    def create_git_tag(self, version: str):
        """Create and push git tag."""
        print(f"🏷️ Creating git tag v{version}...")
        
        subprocess.run(["git", "add", "."], cwd=self.project_root)
        subprocess.run(
            ["git", "commit", "-m", f"chore: release v{version}"],
            cwd=self.project_root
        )
        subprocess.run(
            ["git", "tag", f"v{version}"],
            cwd=self.project_root
        )
        subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=self.project_root
        )
        subprocess.run(
            ["git", "push", "origin", f"v{version}"],
            cwd=self.project_root
        )
        
        print(f"✅ Git tag v{version} created and pushed")
    
    def create_github_release(self, version: str, changes: str) -> bool:
        """Create GitHub release."""
        print(f"🐙 Creating GitHub release for v{version}...")
        
        # This would require GitHub API token
        # For now, just print instructions
        print(f"""
📋 Manual GitHub Release Steps:
1. Go to https://github.com/manish12ys/wolfpy/releases/new
2. Tag: v{version}
3. Title: WolfPy v{version}
4. Description:
{changes}
5. Upload dist/ files as assets
6. Publish release
        """)
        
        return True


def main():
    """Main release function."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/release.py <major|minor|patch> [--test]")
        sys.exit(1)
    
    version_type = sys.argv[1]
    test_mode = "--test" in sys.argv
    
    if version_type not in ['major', 'minor', 'patch']:
        print("Version type must be: major, minor, or patch")
        sys.exit(1)
    
    project_root = Path(__file__).parent.parent
    release_manager = ReleaseManager(project_root)
    
    print(f"🚀 Starting {'test ' if test_mode else ''}release process...")
    
    # Get changelog input
    print("\nEnter changelog for this release (end with empty line):")
    changes_lines = []
    while True:
        line = input()
        if not line:
            break
        changes_lines.append(line)
    
    changes = '\n'.join(changes_lines)
    
    # Run pre-release checks
    if not release_manager.run_tests():
        print("❌ Tests failed. Aborting release.")
        sys.exit(1)
    
    if not release_manager.run_linting():
        print("❌ Linting failed. Aborting release.")
        sys.exit(1)
    
    # Bump version
    new_version = release_manager.bump_version(version_type)
    
    # Update changelog
    release_manager.update_changelog(new_version, changes)
    
    # Build package
    if not release_manager.build_package():
        print("❌ Package build failed. Aborting release.")
        sys.exit(1)
    
    # Publish to PyPI
    if not release_manager.publish_to_pypi(test=test_mode):
        print("❌ PyPI publish failed. Aborting release.")
        sys.exit(1)
    
    # Create git tag (only for real releases)
    if not test_mode:
        release_manager.create_git_tag(new_version)
        release_manager.create_github_release(new_version, changes)
    
    print(f"🎉 Release v{new_version} completed successfully!")
    
    if test_mode:
        print("📝 This was a test release. For production:")
        print("python scripts/release.py <version_type>")


if __name__ == "__main__":
    main()
