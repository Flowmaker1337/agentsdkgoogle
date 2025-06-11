#!/usr/bin/env python3
"""
ElevenLabs Voice Integration dla MetaHuman Business Assistant
Generowanie naturalnego głosu dla avatara w UE5
"""

import os
import requests
import asyncio
import aiohttp
import io
from typing import Optional, Dict, List
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ElevenLabsVoiceManager:
    """Manager dla integracji z ElevenLabs API"""
    
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.base_url = "https://api.elevenlabs.io/v1"
        self.default_voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel - professional female voice
        self.business_voice_id = "pNInz6obpgDQGcFmaJgB"  # Adam - professional male voice
        
        # Voice settings dla business avatar
        self.voice_settings = {
            "stability": 0.8,       # Stabilność głosu (0.0-1.0)
            "similarity_boost": 0.8, # Podobieństwo do oryginalnego głosu  
            "style": 0.2,           # Styl wypowiedzi (0.0-1.0)
            "use_speaker_boost": True
        }
        
        self.model_id = "eleven_multilingual_v2"  # Model wspierający polski
        
    async def get_available_voices(self) -> List[Dict]:
        """Pobiera listę dostępnych głosów"""
        headers = {
            "Accept": "application/json",
            "xi-api-key": self.api_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/voices", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("voices", [])
                else:
                    print(f"❌ Błąd pobierania głosów: {response.status}")
                    return []
    
    async def generate_speech(self, text: str, voice_id: Optional[str] = None, save_path: Optional[str] = None) -> bytes:
        """
        Generuje mowę z tekstu używając ElevenLabs
        
        Args:
            text: Tekst do wypowiedzenia
            voice_id: ID głosu (opcjonalnie)
            save_path: Ścieżka do zapisu pliku audio (opcjonalnie)
            
        Returns:
            Dane audio w formacie bytes
        """
        if not voice_id:
            voice_id = self.business_voice_id
            
        url = f"{self.base_url}/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": self.model_id,
            "voice_settings": self.voice_settings
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    audio_data = await response.read()
                    
                    # Zapis do pliku jeśli podano ścieżkę
                    if save_path:
                        with open(save_path, 'wb') as f:
                            f.write(audio_data)
                        print(f"✅ Audio zapisane: {save_path}")
                    
                    return audio_data
                else:
                    error_text = await response.text()
                    print(f"❌ Błąd generowania mowy: {response.status} - {error_text}")
                    return b""
    
    async def generate_speech_stream(self, text: str, voice_id: Optional[str] = None):
        """
        Generuje streaming audio dla real-time komunikacji z UE5
        """
        if not voice_id:
            voice_id = self.business_voice_id
            
        url = f"{self.base_url}/text-to-speech/{voice_id}/stream"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json", 
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": self.model_id,
            "voice_settings": self.voice_settings
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    async for chunk in response.content.iter_chunked(1024):
                        yield chunk
                else:
                    error_text = await response.text()
                    print(f"❌ Błąd streaming: {response.status} - {error_text}")
    
    async def clone_voice_from_sample(self, voice_name: str, audio_files: List[str]) -> Optional[str]:
        """
        Klonuje głos z próbek audio (dla personalizacji avatara)
        
        Args:
            voice_name: Nazwa nowego głosu
            audio_files: Lista ścieżek do plików audio
            
        Returns:
            ID nowego głosu lub None w przypadku błędu
        """
        url = f"{self.base_url}/voices/add"
        
        headers = {
            "Accept": "application/json",
            "xi-api-key": self.api_key
        }
        
        # Przygotowanie plików
        files = []
        for i, file_path in enumerate(audio_files):
            if os.path.exists(file_path):
                files.append(('files', (f'sample_{i}.mp3', open(file_path, 'rb'), 'audio/mpeg')))
        
        data = {
            'name': voice_name,
            'description': f'Custom voice for MetaHuman Business Avatar - {voice_name}',
            'labels': '{"use_case": "business_avatar", "language": "polish"}'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        voice_id = result.get('voice_id')
                        print(f"✅ Głos sklonowany: {voice_name} (ID: {voice_id})")
                        return voice_id
                    else:
                        error_text = await response.text()  
                        print(f"❌ Błąd klonowania głosu: {response.status} - {error_text}")
                        return None
        finally:
            # Zamknij pliki
            for file_tuple in files:
                file_tuple[1][1].close()
    
    def get_voice_for_emotion(self, emotion: str = "neutral") -> str:
        """
        Zwraca odpowiedni voice_id dla danej emocji/kontekstu
        """
        emotion_voices = {
            "professional": self.business_voice_id,     # Profesjonalny ton
            "friendly": self.default_voice_id,          # Przyjazny ton
            "excited": "pNInz6obpgDQGcFmaJgB",         # Entuzjastyczny
            "calm": "21m00Tcm4TlvDq8ikWAM",            # Spokojny
            "neutral": self.business_voice_id           # Neutralny
        }
        
        return emotion_voices.get(emotion, self.business_voice_id)
    
    async def optimize_for_realtime(self, text: str) -> str:
        """
        Optymalizuje tekst dla lepszej jakości TTS w czasie rzeczywistym
        """
        # Usuń nadmierne formatting
        text = text.replace("📊", "").replace("✅", "").replace("🎯", "")
        text = text.replace("📅", "").replace("⏰", "").replace("📋", "")
        
        # Dodaj pauzy dla lepszej dykcji
        text = text.replace(".", ". ")
        text = text.replace("!", "! ")
        text = text.replace("?", "? ")
        
        # Skróć długie teksty
        if len(text) > 500:
            sentences = text.split(". ")
            text = ". ".join(sentences[:3]) + "."
        
        return text.strip()

class UE5AudioStreamer:
    """Streamer audio dla integracji z UE5"""
    
    def __init__(self, voice_manager: ElevenLabsVoiceManager):
        self.voice_manager = voice_manager
        self.audio_queue = asyncio.Queue()
        
    async def stream_to_ue5(self, text: str, websocket=None):
        """
        Streamuje audio do UE5 przez WebSocket
        """
        try:
            # Optymalizuj tekst dla TTS
            optimized_text = await self.voice_manager.optimize_for_realtime(text)
            
            # Generuj audio
            audio_data = await self.voice_manager.generate_speech(optimized_text)
            
            if audio_data and websocket:
                # Wyślij audio jako base64 do UE5
                import base64
                audio_b64 = base64.b64encode(audio_data).decode('utf-8')
                
                audio_message = {
                    "type": "audio",
                    "data": audio_b64,
                    "format": "mp3",
                    "text": text,
                    "timestamp": datetime.now().isoformat()
                }
                
                await websocket.send(str(audio_message))
                print(f"🔊 Audio wysłane do UE5: {len(audio_data)} bytes")
                
        except Exception as e:
            print(f"❌ Błąd streaming audio: {e}")

# Test funkcji
async def test_elevenlabs():
    """Test podstawowych funkcji ElevenLabs"""
    print("🎤 Test ElevenLabs Voice Integration")
    print("=" * 50)
    
    voice_manager = ElevenLabsVoiceManager()
    
    # Test dostępnych głosów
    print("📋 Pobieranie dostępnych głosów...")
    voices = await voice_manager.get_available_voices()
    print(f"✅ Znaleziono {len(voices)} głosów")
    
    for voice in voices[:3]:  # Pokaż pierwsze 3
        print(f"   - {voice.get('name', 'Unknown')} ({voice.get('voice_id', 'No ID')})")
    
    # Test generowania mowy
    print("\n🗣️  Test generowania mowy...")
    test_text = "Witaj! Jestem Twoim asystentem biznesowym MetaHuman. Jak mogę Ci dziś pomóc?"
    
    audio_data = await voice_manager.generate_speech(
        test_text,
        save_path="test_voice.mp3"
    )
    
    if audio_data:
        print(f"✅ Wygenerowano audio: {len(audio_data)} bytes")
        print("💾 Zapisano jako: test_voice.mp3")
    else:
        print("❌ Błąd generowania audio")

if __name__ == "__main__":
    asyncio.run(test_elevenlabs()) 