import google.generativeai as genai
import os

# Replace this with your actual API key for testing
TEST_API_KEY = "YOUR_API_KEY_HERE"

def test_simple():
    """Simple test without input()"""
    
    # Set environment variable
    os.environ['GOOGLE_API_KEY'] = TEST_API_KEY
    
    try:
        # Configure
        genai.configure(api_key=TEST_API_KEY)
        
        # List models
        models = list(genai.list_models())
        print(f"Found {len(models)} models")
        
        # Test generation
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Say hello")
        print(f"Response: {response.text}")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    if TEST_API_KEY == "YOUR_API_KEY_HERE":
        print("Please edit the script and replace YOUR_API_KEY_HERE with your actual API key")
    else:
        test_simple() 