#!/usr/bin/env python3
"""
Test Google ADK Business Agent
Sprawdza czy agent działa poprawnie
"""

import os
import sys
import asyncio
from pathlib import Path

# Dodaj ścieżkę do Google ADK
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'adk-python', 'src'))

async def test_google_adk_import():
    """Test importu Google ADK"""
    print("🧪 Test 1: Import Google ADK")
    
    try:
        from google.adk.agents import LlmAgent
        from google.adk.models import Gemini
        from google.adk.tools import FunctionTool, BaseTool
        print("✅ Import Google ADK - OK")
        return True
    except ImportError as e:
        print(f"❌ Import Google ADK - BŁĄD: {e}")
        return False

async def test_business_agent_creation():
    """Test tworzenia agenta biznesowego"""
    print("\n🧪 Test 2: Tworzenie Business Agent")
    
    try:
        from google_adk_business_agent import GoogleADKBusinessAgent
        agent = GoogleADKBusinessAgent()
        await agent.setup_agent()
        print("✅ Tworzenie agenta - OK")
        return True
    except Exception as e:
        print(f"❌ Tworzenie agenta - BŁĄD: {e}")
        return False

async def test_toolset():
    """Test toolsetu biznesowego"""
    print("\n🧪 Test 3: Business Toolset")
    
    try:
        from google_adk_business_agent import schedule_meeting
        
        # Test schedule_meeting
        result = await schedule_meeting(
            title="Test Meeting",
            date="2024-12-30",
            time="10:00",
            participants=["test@example.com"],
            description="Test spotkania"
        )
        
        if result.get("success"):
            print("✅ Business Tools - OK")
            return True
        else:
            print("❌ Business Tools - BŁĄD: Brak sukcesu")
            return False
            
    except Exception as e:
        print(f"❌ Business Tools - BŁĄD: {e}")
        return False

async def test_environment():
    """Test zmiennych środowiskowych"""
    print("\n🧪 Test 4: Google Cloud Credentials")
    
    credentials_path = "google_cloud_credentials.json"
    if os.path.exists(credentials_path):
        print("✅ Google Cloud Service Account - OK")
        return True
    else:
        print("❌ Google Cloud Service Account - Brak pliku google_cloud_credentials.json")
        return False

async def test_agent_basic_functionality():
    """Test podstawowej funkcjonalności agenta"""
    print("\n🧪 Test 5: Podstawowa funkcjonalność")
    
    if not os.path.exists("google_cloud_credentials.json"):
        print("⚠️  Pomijam test - brak Google Cloud credentials")
        return True
    
    try:
        from google_adk_business_agent import GoogleADKBusinessAgent
        agent = GoogleADKBusinessAgent()
        await agent.setup_agent()
        
        # Sprawdź czy agent został utworzony
        if agent.agent is not None:
            print("✅ Agent funkcjonalny - OK")
            return True
        else:
            print("❌ Agent funkcjonalny - Agent nie został utworzony")
            return False
            
    except Exception as e:
        print(f"❌ Agent funkcjonalny - BŁĄD: {e}")
        return False

async def main():
    """Główna funkcja testowa"""
    print("""
🧪 Google ADK Business Agent - Testy
===================================
    """)
    
    tests = [
        test_google_adk_import,
        test_business_agent_creation,
        test_toolset,
        test_environment,
        test_agent_basic_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ Test nieudany: {e}")
    
    print(f"\n📊 Wyniki testów: {passed}/{total} przeszło")
    
    if passed == total:
        print("🎉 Wszystkie testy przeszły pomyślnie!")
        print("\n🚀 Możesz uruchomić agenta:")
        print("   python start_google_adk_agent.py")
    else:
        print("⚠️  Niektóre testy nie przeszły. Sprawdź konfigurację.")
        
        if not os.path.exists("google_cloud_credentials.json"):
            print("\n💡 Potrzebujesz pliku google_cloud_credentials.json z Google Cloud Service Account")

if __name__ == "__main__":
    asyncio.run(main()) 