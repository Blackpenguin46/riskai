#!/usr/bin/env python3
"""
RiskAI Installation Test Script

Tests if the RiskAI installation is working correctly.
"""

import sys
import importlib
import subprocess
from pathlib import Path

def test_python_version():
    """Test Python version"""
    print("🐍 Testing Python version...")
    
    version = sys.version_info
    print(f"   Python: {version.major}.{version.minor}.{version.micro}")
    
    if version < (3, 9):
        print("   ❌ Python 3.9+ required")
        return False
    else:
        print("   ✅ Python version OK")
        return True

def test_essential_packages():
    """Test essential packages"""
    print("\n📦 Testing essential packages...")
    
    packages = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("requests", "Requests"),
        ("numpy", "NumPy"),
        ("pandas", "Pandas"),
        ("sqlalchemy", "SQLAlchemy"),
    ]
    
    success = True
    
    for package, name in packages:
        try:
            importlib.import_module(package)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name} - not installed")
            success = False
    
    return success

def test_ai_packages():
    """Test AI/ML packages"""
    print("\n🤖 Testing AI/ML packages...")
    
    packages = [
        ("transformers", "Transformers"),
        ("sentence_transformers", "Sentence Transformers"),
        ("torch", "PyTorch"),
    ]
    
    success = True
    
    for package, name in packages:
        try:
            importlib.import_module(package)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ⚠️  {name} - not installed (optional)")
    
    return success

def test_backend_structure():
    """Test backend file structure"""
    print("\n📁 Testing backend structure...")
    
    backend_dir = Path("backend")
    required_files = [
        "api.py",
        "main.py",
        "requirements.txt",
        "requirements-fixed.txt",
        "rag_pipeline/",
        "scoring/",
        "database/",
        "analytics/",
        "data_pipeline/",
        "benchmarks/",
    ]
    
    success = True
    
    for file_path in required_files:
        full_path = backend_dir / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - missing")
            success = False
    
    return success

def test_frontend_structure():
    """Test frontend file structure"""
    print("\n🌐 Testing frontend structure...")
    
    frontend_dir = Path("frontend")
    required_files = [
        "package.json",
        "pages/",
        "public/",
        "lib/",
    ]
    
    success = True
    
    for file_path in required_files:
        full_path = frontend_dir / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - missing")
            success = False
    
    return success

def test_node_environment():
    """Test Node.js environment"""
    print("\n📦 Testing Node.js environment...")
    
    try:
        # Check Node.js
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Node.js: {result.stdout.strip()}")
        else:
            print("   ❌ Node.js not working")
            return False
            
        # Check npm
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ npm: {result.stdout.strip()}")
        else:
            print("   ❌ npm not working")
            return False
            
        return True
        
    except FileNotFoundError:
        print("   ❌ Node.js/npm not found")
        return False

def test_data_directories():
    """Test data directories"""
    print("\n📂 Testing data directories...")
    
    directories = [
        "backend/data",
        "backend/vectordb",
        "backend/database_data",
    ]
    
    success = True
    
    for dir_path in directories:
        path = Path(dir_path)
        if path.exists():
            print(f"   ✅ {dir_path}")
        else:
            print(f"   ⚠️  {dir_path} - will be created")
            try:
                path.mkdir(parents=True, exist_ok=True)
                print(f"   ✅ Created {dir_path}")
            except Exception as e:
                print(f"   ❌ Failed to create {dir_path}: {e}")
                success = False
    
    return success

def test_fallback_system():
    """Test fallback vector store system"""
    print("\n🔄 Testing fallback system...")
    
    try:
        # Test fallback vector store
        sys.path.insert(0, str(Path("backend")))
        
        from rag_pipeline.vector_store_fallback import get_embedder, get_vector_store
        
        # Test embedder
        embedder = get_embedder()
        test_text = "This is a test document"
        embedding = embedder.embed_query(test_text)
        
        if embedding and len(embedding) > 0:
            print("   ✅ Fallback embedder working")
        else:
            print("   ❌ Fallback embedder failed")
            return False
        
        # Test vector store
        vector_store = get_vector_store()
        if vector_store:
            print("   ✅ Fallback vector store working")
        else:
            print("   ❌ Fallback vector store failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Fallback system failed: {e}")
        return False

def generate_report():
    """Generate test report"""
    print("\n" + "="*50)
    print("🧪 RiskAI Installation Test Report")
    print("="*50)
    
    tests = [
        ("Python Version", test_python_version),
        ("Essential Packages", test_essential_packages),
        ("AI/ML Packages", test_ai_packages),
        ("Backend Structure", test_backend_structure),
        ("Frontend Structure", test_frontend_structure),
        ("Node.js Environment", test_node_environment),
        ("Data Directories", test_data_directories),
        ("Fallback System", test_fallback_system),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Summary:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! RiskAI is ready to use.")
        print("\n🚀 Next steps:")
        print("1. Run: python start_riskai.py")
        print("2. Open browser to: http://localhost:3000")
        print("3. Start your risk assessment!")
    else:
        print("\n⚠️  Some tests failed. RiskAI may have limited functionality.")
        print("\n🔧 Troubleshooting:")
        print("1. Run: python install_riskai.py")
        print("2. Check QUICK_START.md for installation help")
        print("3. Try Docker installation for easier setup")
    
    return passed == total

if __name__ == "__main__":
    success = generate_report()
    sys.exit(0 if success else 1)