import google.generativeai as genai
import os

def test_gemini_api(api_key):
    """Test Gemini API with detailed error reporting"""
    print(f"Testing API key: {api_key[:10]}...")
    
    try:
        # Try setting environment variable first
        os.environ['GOOGLE_API_KEY'] = api_key
        print("✅ Environment variable set")
        
        # Configure the API
        genai.configure(api_key=api_key)
        print("✅ API configured successfully")
        
        # Test listing models
        print("📋 Testing model listing...")
        models = list(genai.list_models())
        print(f"✅ Found {len(models)} models")
        
        # Show available models
        for model in models[:3]:
            print(f"   - {model.name}")
            if hasattr(model, 'supported_generation_methods'):
                print(f"     Methods: {model.supported_generation_methods}")
        
        # Test model creation
        print("\n🤖 Testing model creation...")
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            print("✅ gemini-1.5-flash model created")
        except Exception as e:
            print(f"❌ gemini-1.5-flash failed: {e}")
            try:
                model = genai.GenerativeModel('gemini-pro')
                print("✅ gemini-pro model created")
            except Exception as e2:
                print(f"❌ gemini-pro failed: {e2}")
                return False
        
        # Test content generation
        print("\n💬 Testing content generation...")
        response = model.generate_content("Hello, respond with 'OK' if you can see this.")
        
        if not response:
            print("❌ No response received")
            return False
            
        if not response.text:
            print("❌ Empty response text")
            if hasattr(response, 'candidates'):
                for i, candidate in enumerate(response.candidates):
                    print(f"   Candidate {i}: {candidate}")
                    if hasattr(candidate, 'finish_reason'):
                        print(f"   Finish reason: {candidate.finish_reason}")
            return False
            
        print(f"✅ Response received: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    # Test with the API key that works in React
    api_key = input("Enter your Gemini API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        exit(1)
    
    print(f"API key length: {len(api_key)}")
    print(f"API key starts with: {api_key[:10] if len(api_key) > 10 else api_key}")
    
    success = test_gemini_api(api_key)
    print(f"\n{'✅ API test PASSED' if success else '❌ API test FAILED'}") 