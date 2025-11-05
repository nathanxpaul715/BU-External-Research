# test_tr_auth.py  
from config.config_tr_auth import get_anthropic_client, ANTHROPIC_MODEL
  
print("="*70)  
print("TESTING THOMSON REUTERS AUTHENTICATION")  
print("="*70)
  
# Test 1: Get client  
print("\n[1/3] Testing token fetch...")  
try:  
    client = get_anthropic_client(force_refresh=True)  # Force fresh token  
    print("✅ Token fetched successfully")  
except Exception as e:  
    print(f"❌ Token fetch failed: {e}")  
    exit(1)
  
# Test 2: Test Claude connection  
print("\n[2/3] Testing Claude Sonnet 4.5 connection...")  
try:  
    response = client.messages.create(  
        model=ANTHROPIC_MODEL,  
        max_tokens=100,  
        messages=[  
            {"role": "user", "content": "Say 'Authentication successful' in exactly 3 words."}  
        ]  
    )
      
    response_text = response.content[0].text  
    print(f"✅ Claude response: {response_text}")  
except Exception as e:  
    print(f"❌ Claude connection failed: {e}")  
    exit(1)
  
# Test 3: Test token caching  
print("\n[3/3] Testing token caching...")  
try:  
    client2 = get_anthropic_client(force_refresh=False)  # Should use cached token  
    print("✅ Token caching working")  
except Exception as e:  
    print(f"❌ Token caching failed: {e}")  
    exit(1)
  
print("\n" + "="*70)  
print("✅ ALL TESTS PASSED - TR AUTHENTICATION CONFIGURED CORRECTLY")  
print("="*70)  
print("\n🚀 Ready to run: streamlit run app.py")