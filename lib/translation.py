import requests

class Translator:
    def __init__(self):
        # LibreTranslate API endpoint
        self.api_url = "http://localhost:5000/translate"
        
    def translate(self, word, timeout=2):
        """
        Translate a Spanish word to English using LibreTranslate API.
        Args:
            word: The word to translate
            timeout: Timeout in seconds (default: 2)
        Returns the translation if successful, otherwise returns None.
        """
        try:
            # Prepare the request data
            data = {
                "q": word,
                "source": "es",
                "target": "en",
                "format": "text",
                "alternatives": 3,
                "api_key": ""
            }
            
            # Set headers
            headers = {
                "Content-Type": "application/json"
            }
            
            # Make the API request with timeout and headers
            response = requests.post(self.api_url, json=data, headers=headers, timeout=timeout)
            
            # Check if the request was successful
            if response.status_code == 200:
                result = response.json()
                return result.get('translatedText')
            else:
                print(f"Translation failed with status code: {response.status_code}")
                return None
                
        except requests.Timeout:
            print(f"Translation request timed out after {timeout} seconds")
            return None
        except Exception as e:
            print(f"Error during translation: {str(e)}")
            return None

# Create a singleton instance
translator = Translator() 