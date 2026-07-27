#!/usr/bin/env python3
"""Debug script for RAG agent"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test if all imports work"""
    print("🔍 Testing imports...")
    
    try:
        from llm.agents import rag_agent, build_rag_agent
        print("✅ Successfully imported rag_agent and build_rag_agent")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    try:
        from vdb.access import search_langchain
        print("✅ Successfully imported search_langchain")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    try:
        import langchain
        print(f"✅ langchain version: {langchain.__version__}")
    except ImportError as e:
        print(f"❌ langchain not installed: {e}")
        return False
    
    return True


def test_search_langchain():
    """Test search_langchain function"""
    print("\n🔍 Testing search_langchain...")
    
    try:
        from vdb.access import search_langchain, client
        
        # Get available collections
        collections = client.get_collections()
        if not collections.collections:
            print("❌ No collections found in Qdrant")
            return False
        
        coll_name = collections.collections[0].name
        print(f"✅ Found collection: {coll_name}")
        
        # Test search
        test_query = "test query"
        results = search_langchain(test_query, k=1, coll_name=coll_name)
        print(f"✅ search_langchain returned {len(results)} results")
        
        if results:
            print(f"   - First result page_content: {results[0].page_content[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ Error testing search_langchain: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rag_agent():
    """Test RAG agent"""
    print("\n🔍 Testing RAG agent...")
    
    try:
        from llm.agents import rag_agent
        from vdb.access import client
        
        # Get available collections
        collections = client.get_collections()
        if not collections.collections:
            print("❌ No collections found in Qdrant")
            return False
        
        coll_name = collections.collections[0].name
        print(f"✅ Using collection: {coll_name}")
        
        # Test agent
        test_query = "What is the main topic?"
        print(f"📝 Testing query: {test_query}")
        
        response = rag_agent(test_query, coll_name=coll_name)
        print(f"✅ RAG agent response received")
        print(f"   Response: {response[:200]}...")
        
        return True
    except Exception as e:
        print(f"❌ Error testing RAG agent: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("RAG Agent Debug Script")
    print("=" * 60)
    
    # Test 1: Imports
    if not test_imports():
        print("\n⚠️  Import tests failed. Install missing packages:")
        print("   pip install langchain langchain-core langchain-community")
        return
    
    # Test 2: search_langchain
    if not test_search_langchain():
        print("\n⚠️  search_langchain test failed")
        return
    
    # Test 3: RAG agent
    if not test_rag_agent():
        print("\n⚠️  RAG agent test failed")
        return
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
