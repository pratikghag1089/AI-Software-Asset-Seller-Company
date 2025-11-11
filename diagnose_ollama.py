#!/usr/bin/env python3
"""
Quick Ollama diagnostics and fix script
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import subprocess
import json

print("=" * 80)
print("OLLAMA DIAGNOSTICS")
print("=" * 80)

# Check if Ollama is running
print("\n[1/5] Checking Ollama service...")
try:
    result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        print("✓ Ollama is running")
        print("\nInstalled models:")
        print(result.stdout)
    else:
        print("❌ Ollama not responding properly")
        print(result.stderr)
except Exception as e:
    print(f"❌ Ollama not found: {e}")
    print("\nTo install Ollama:")
    print("  curl -fsSL https://ollama.com/install.sh | sh")
    sys.exit(1)

# Check if gpt-oss model exists
print("\n[2/5] Checking gpt-oss:latest model...")
if 'gpt-oss:latest' in result.stdout or 'gpt-oss' in result.stdout:
    print("✓ gpt-oss model found")
else:
    print("⚠ gpt-oss:latest not found")
    print("\nDownloading gpt-oss:latest...")
    print("This may take a few minutes...")
    try:
        subprocess.run(['ollama', 'pull', 'gpt-oss:latest'], check=True)
        print("✓ Model downloaded successfully")
    except Exception as e:
        print(f"❌ Failed to download: {e}")
        sys.exit(1)

# Test basic generation
print("\n[3/5] Testing basic generation...")
try:
    result = subprocess.run(
        ['ollama', 'run', 'gpt-oss:latest', 'Say just "OK" and nothing else'],
        capture_output=True,
        text=True,
        timeout=30
    )
    if result.returncode == 0 and result.stdout.strip():
        print(f"✓ Basic generation works: {result.stdout.strip()[:50]}")
    else:
        print(f"❌ Generation failed: {result.stderr}")
        sys.exit(1)
except subprocess.TimeoutExpired:
    print("❌ Generation timed out (model too slow or stuck)")
    sys.exit(1)
except Exception as e:
    print(f"❌ Test failed: {e}")
    sys.exit(1)

# Check system resources
print("\n[4/5] Checking system resources...")
try:
    import psutil
    ram = psutil.virtual_memory()
    print(f"  RAM: {ram.available / (1024**3):.1f} GB available / {ram.total / (1024**3):.1f} GB total")
    print(f"  RAM Usage: {ram.percent}%")

    if ram.available < 2 * (1024**3):  # Less than 2GB available
        print("⚠ Low RAM available - model may be slow or fail")
except:
    print("  (psutil not installed, skipping)")

# Try with Python ollama client
print("\n[5/5] Testing Python ollama client...")
try:
    from core.ollama_client import get_ollama_client
    ollama = get_ollama_client()
    response = ollama.generate("Say 'Hello' only", temperature=0.5, max_tokens=10)
    print(f"✓ Python client works: {response[:50]}")
except Exception as e:
    print(f"❌ Python client failed: {e}")
    print("\nTrying alternative model (llama3.2 - smaller, more stable)...")
    print("Would you like to try llama3.2 instead? (smaller, more reliable)")

print("\n" + "=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)

# Check model size
print("\nIf gpt-oss:latest is causing issues, try these alternatives:")
print("  1. llama3.2:latest (3B params, more stable)")
print("     ollama pull llama3.2:latest")
print("     Then edit .env: OLLAMA_MODEL=llama3.2:latest")
print()
print("  2. qwen2.5:3b (3B params, fast)")
print("     ollama pull qwen2.5:3b")
print("     Then edit .env: OLLAMA_MODEL=qwen2.5:3b")
print()
print("  3. phi3:mini (3.8B params)")
print("     ollama pull phi3:mini")
print("     Then edit .env: OLLAMA_MODEL=phi3:mini")

print("\n" + "=" * 80)
