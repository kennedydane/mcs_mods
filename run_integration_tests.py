#!/usr/bin/env python3

import subprocess
import sys
import time
from pathlib import Path

def run_integration_tests():
    """Run integration tests against Docker container"""
    print("🐳 Running Integration Tests...")
    print("=" * 50)
    
    project_dir = Path(__file__).parent
    
    try:
        # Build the image first
        print("🔨 Building Docker image...")
        build_result = subprocess.run([
            "docker", "compose", "build"
        ], cwd=project_dir, check=True, capture_output=True, text=True)
        
        print("✅ Docker image built successfully")
        
        # Run integration tests using uv
        print("🧪 Running integration tests...")
        result = subprocess.run([
            "uv", "run", "pytest", 
            "-v",
            "-m", "integration",
            "--tb=short",
            "tests/test_integration.py"
        ], cwd=project_dir)
        
        if result.returncode == 0:
            print("\n✅ All integration tests passed!")
            return True
        else:
            print(f"\n❌ Integration tests failed with exit code {result.returncode}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker build failed: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False
    except FileNotFoundError as e:
        print(f"❌ Required tool not found: {e}")
        return False

def cleanup_test_containers():
    """Clean up any leftover test containers"""
    print("🧹 Cleaning up test containers...")
    
    try:
        subprocess.run([
            "docker", "compose", "-f", "docker-compose.test.yml", "down", "-v"
        ], capture_output=True)
        
        print("✅ Cleanup completed")
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--cleanup":
        cleanup_test_containers()
        return
    
    # Cleanup any existing test containers first
    cleanup_test_containers()
    
    success = run_integration_tests()
    
    # Cleanup after tests
    cleanup_test_containers()
    
    if not success:
        print("\n💡 Tips:")
        print("- Make sure Docker is running")
        print("- Try: docker compose build")
        print("- Check container logs: docker compose -f docker-compose.test.yml logs")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()