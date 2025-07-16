#!/usr/bin/env python3
"""
Azure AI DeepSeek Connection Test Script
Run this to test your Azure credentials independently
"""

import sys
from pathlib import Path

# Try to import required modules
try:
    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.models import SystemMessage, UserMessage
    from azure.core.credentials import AzureKeyCredential
    print("✅ Azure modules imported successfully")
except ImportError as e:
    print(f"❌ Missing Azure modules: {e}")
    print("Install with: pip install azure-ai-inference azure-core")
    sys.exit(1)

def test_azure_connection():
    """Test Azure AI DeepSeek connection with detailed diagnostics"""
    
    print("🧪 Azure AI DeepSeek Connection Test")
    print("=" * 50)
    print("⚠️  Note: This test will consume a small amount of tokens")
    print("=" * 50)
    
    # Test credentials - replace with your actual values
    ENDPOINT = ""
    API_KEY = ""
    MODEL = "DeepSeek-V3-0324"
    
    print(f"📡 Endpoint: {ENDPOINT}")
    print(f"🔑 API Key: {API_KEY[:20]}...{API_KEY[-10:]}")
    print(f"🤖 Model: {MODEL}")
    print()
    
    try:
        print("🔧 Step 1: Validating credentials format...")
        if not ENDPOINT or not API_KEY:
            print("❌ Missing endpoint or API key")
            return False
            
        if not ENDPOINT.startswith("https://"):
            print("❌ Endpoint should start with https://")
            return False
            
        if len(API_KEY) < 20:
            print("❌ API key seems too short")
            return False
            
        print("✅ Credentials format valid")
        
        print("\n🔧 Step 2: Creating client...")
        client = ChatCompletionsClient(
            endpoint=ENDPOINT,
            credential=AzureKeyCredential(API_KEY),
            api_version="2024-05-01-preview"
        )
        print("✅ Client created successfully")
        
        print("\n🔧 Step 3: Testing actual connection (this uses tokens)...")
        response = client.complete(
            messages=[
                SystemMessage(content="You are a Korean-to-English translator."),
                UserMessage(content="Translate this Korean to English: '안녕하세요' Be brief.")
            ],
            max_tokens=50,
            temperature=0.1,
            top_p=0.95,
            presence_penalty=0.0,
            frequency_penalty=0.0,
            model=MODEL
        )
        
        print("✅ Request sent successfully")
        
        print("\n🔧 Step 4: Checking response...")
        if response and response.choices and len(response.choices) > 0:
            result = response.choices[0].message.content
            print(f"✅ Translation successful: '{result}'")
            print("\n🎉 Azure AI DeepSeek is working correctly!")
            return True
        else:
            print("❌ No response or empty response")
            print(f"Response object: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Common error diagnostics
        error_str = str(e).lower()
        print("\n🔍 Diagnostic suggestions:")
        
        if "authentication" in error_str or "unauthorized" in error_str:
            print("- ❌ API Key might be invalid or expired")
            print("- Check your Azure AI Studio for the correct API key")
            
        elif "not found" in error_str or "404" in error_str:
            print("- ❌ Endpoint URL might be incorrect")
            print("- Check your Azure deployment name")
            print("- Ensure the URL ends with '/models'")
            
        elif "timeout" in error_str or "connection" in error_str:
            print("- ❌ Network connectivity issue")
            print("- Check your internet connection")
            print("- Try again in a few minutes")
            
        elif "model" in error_str:
            print("- ❌ Model name might be incorrect")
            print("- Check if 'DeepSeek-V3-0324' is available in your deployment")
            
        else:
            print("- ❌ Unexpected error - check Azure service status")
            
        return False

def test_config_file():
    """Test loading from config file"""
    print("\n📁 Testing config file loading...")
    
    config_file = Path("azure_config.txt")
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                lines = f.read().strip().split('\n')
                if len(lines) >= 2:
                    endpoint = lines[0].split('=', 1)[1].strip() if '=' in lines[0] else lines[0].strip()
                    api_key = lines[1].split('=', 1)[1].strip() if '=' in lines[1] else lines[1].strip()
                    print(f"✅ Config file loaded:")
                    print(f"   Endpoint: {endpoint}")
                    print(f"   API Key: {api_key[:20]}...{api_key[-10:]}")
                    return endpoint, api_key
                else:
                    print("❌ Config file format incorrect")
        except Exception as e:
            print(f"❌ Error reading config file: {e}")
    else:
        print("❌ azure_config.txt not found")
        print("💡 Create it with:")
        print("   ENDPOINT=your-endpoint-here")
        print("   API_KEY=your-api-key-here")
    
    return None, None

def create_sample_config():
    """Create a sample config file"""
    config_content = """ENDPOINT=
API_KEY=

# Instructions:
# 1. Replace the values above with your actual Azure credentials
# 2. Save this file as 'azure_config.txt'
# 3. Keep this file secure and don't share it
"""
    try:
        with open("azure_config.txt", "w", encoding="utf-8") as f:
            f.write(config_content)
        print("✅ Created azure_config.txt with your credentials")
    except Exception as e:
        print(f"❌ Error creating config file: {e}")

if __name__ == "__main__":
    print("Starting Azure AI DeepSeek diagnostics...\n")
    
    # Test direct connection
    success = test_azure_connection()
    
    # Test config file
    endpoint, api_key = test_config_file()
    
    # Create sample config if needed
    if not Path("azure_config.txt").exists():
        print("\n📝 Creating sample config file...")
        create_sample_config()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 RESULT: Azure AI DeepSeek is working!")
        print("Your application should work correctly.")
    else:
        print("❌ RESULT: Connection failed")
        print("Please check the diagnostic suggestions above.")
        
    print("\n💡 Next steps:")
    print("1. Fix any issues identified above")
    print("2. Ensure azure_config.txt exists with correct credentials")
    print("3. Run your translator application")
    
    input("\nPress Enter to exit...")