from google import genai

# PASTE YOUR KEY HERE
KEY = 'AIzaSyBwYG8mNIrR_qMdZkQVzec03NizwpMvR5I' 

try:
    # 1. Initialize the new Client
    client = genai.Client(api_key=KEY)
    
    print("Testing connection with Gemini 2.0 Flash...")
    
    # 2. Generate content using the NEW model name
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Say 'Hello' if you can hear me."
    )
    
    print("SUCCESS! The API responded:")
    print(response.text)

except Exception as e:
    print("\nFAILED. Here is the error:")
    print(e)