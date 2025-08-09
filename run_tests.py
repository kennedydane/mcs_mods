#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path

def run_tests():
    """Run the test suite"""
    print("🧪 Running Minecraft Server Tests...")
    print("=" * 50)
    
    try:
        # Run pytest with verbose output
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "-v",
            "--tb=short",
            "tests/"
        ], check=True, cwd=Path(__file__).parent)
        
        print("\n✅ All tests passed!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ pytest not found. Install with: uv add --dev pytest")
        return False

def run_coverage():
    """Run tests with coverage (if available)"""
    print("\n🔍 Running tests with coverage...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "--cov=server_wrapper",
            "--cov=manage",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "tests/"
        ], cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print("\n📊 Coverage report generated in htmlcov/")
        
    except FileNotFoundError:
        print("📊 Coverage not available. Install with: uv add --dev pytest-cov")

if __name__ == "__main__":
    success = run_tests()
    
    if success and "--coverage" in sys.argv:
        run_coverage()
    
    sys.exit(0 if success else 1)