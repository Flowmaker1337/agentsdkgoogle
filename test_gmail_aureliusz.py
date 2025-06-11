#!/usr/bin/env python3

import asyncio
from custom_google_tools import get_gmail_messages, get_gmail_message_content

async def test_gmail():
    print('🔍 Szukam emaili od Aureliusza...')
    
    # Test 1: Ogólne wyszukiwanie "aureliusz"
    result1 = await get_gmail_messages(query='from:aureliusz', max_results=5)
    print('\n📧 Wyniki dla "from:aureliusz":')
    print(f"Success: {result1.get('success')}")
    print(f"Liczba: {result1.get('messages_count')}")
    
    if result1.get('success') and result1.get('messages'):
        for i, msg in enumerate(result1['messages'][:3]):
            print(f"\n--- Email {i+1} ---")
            print(f"ID: {msg['id']}")  
            print(f"Od: {msg['sender']}")
            print(f"Temat: {msg['subject']}")
            print(f"Data: {msg['date']}")
            print(f"Fragment: {msg['snippet'][:100]}...")
            
            # Test pobierania treści pierwszego emaila
            if i == 0:
                print(f"\n🔍 Pobieram pełną treść emaila {msg['id']}...")
                content_result = await get_gmail_message_content(msg['id'])
                if content_result.get('success'):
                    print(f"Treść: {content_result['body'][:200]}...")
                else:
                    print(f"Błąd: {content_result.get('error')}")
    
    # Test 2: Wyszukiwanie "Górski"
    print('\n\n🔍 Szukam emaili z "górski"...')
    result2 = await get_gmail_messages(query='górski', max_results=3)
    print(f"Success: {result2.get('success')}")
    print(f"Liczba: {result2.get('messages_count')}")
    
    if result2.get('success') and result2.get('messages'):
        for msg in result2['messages']:
            print(f"Od: {msg['sender']}")
            print(f"Temat: {msg['subject']}")

if __name__ == "__main__":
    asyncio.run(test_gmail()) 