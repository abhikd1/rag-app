"""
🚀 MULTI-PROVIDER LLM ROUTER
Automatically rotates between 6 free LLM APIs for unlimited requests!
"""
import os
import requests
import time
from typing import Optional, Dict, List
import random

class MultiLLMRouter:
    """Smart router that automatically switches between free LLM providers"""
    
    def __init__(self):
        self.providers = self._init_providers()
        self.current_index = 0
        self.request_count = {}
        print(f"\n{'='*60}")
        print(f"🚀 Multi-LLM Router Initialized")
        print(f"{'='*60}")
        print(f"✅ Active Providers: {len(self.providers)}")
        for p in self.providers:
            print(f"   - {p['name']}")
        print(f"{'='*60}\n")
    
    def _init_providers(self) -> List[Dict]:
        """Initialize all available LLM providers"""
        providers = []
        
        # 1. GROQ (14,400 req/day, FASTEST)
        if os.getenv('GROQ_API_KEY'):
            providers.append({
                'name': 'Groq',
                'url': 'https://api.groq.com/openai/v1/chat/completions',
                'model': 'llama-3.3-70b-versatile',
                'headers': {
                    'Authorization': f"Bearer {os.getenv('GROQ_API_KEY')}",
                    'Content-Type': 'application/json'
                },
                'priority': 1  # Highest priority (fastest)
            })
        
        # 2. OPENROUTER (50+ models, 50 req/day per model)
        if os.getenv('OPENROUTER_API_KEY'):
            providers.append({
                'name': 'OpenRouter',
                'url': 'https://openrouter.ai/api/v1/chat/completions',
                'model': 'meta-llama/llama-3.3-70b-instruct:free',
                'headers': {
                    'Authorization': f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                    'Content-Type': 'application/json',
                    'HTTP-Referer': 'http://localhost:5000',
                    'X-Title': 'RAG App'
                },
                'priority': 2
            })
        
        
        # 3. DEEPINFRA (Free tier)
        if os.getenv('DEEPINFRA_API_KEY'):
            providers.append({
                'name': 'DeepInfra',
                'url': 'https://api.deepinfra.com/v1/openai/chat/completions',
                'model': 'meta-llama/Meta-Llama-3.1-70B-Instruct',
                'headers': {
                    'Authorization': f"Bearer {os.getenv('DEEPINFRA_API_KEY')}",
                    'Content-Type': 'application/json'
                },
                'priority': 3
            })
        
        # 4. GEMINI (1,500 req/day)
        if os.getenv('GEMINI_API_KEY'):
            providers.append({
                'name': 'Gemini',
                'url': f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={os.getenv('GEMINI_API_KEY')}",
                'model': 'gemini-2.0-flash-exp',
                'headers': {'Content-Type': 'application/json'},
                'priority': 4,
                'is_gemini': True  # Special handling
            })
        
        # 5. HUGGING FACE (Rate-limited free)
        if os.getenv('HUGGINGFACE_API_KEY'):
            providers.append({
                'name': 'Hugging Face',
                'url': 'https://api-inference.huggingface.co/models/meta-llama/Llama-3.1-70B-Instruct',
                'model': 'meta-llama/Llama-3.1-70B-Instruct',
                'headers': {
                    'Authorization': f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}",
                    'Content-Type': 'application/json'
                },
                'priority': 5,
                'is_hf': True  # Special handling
            })
        
        # Sort by priority (lower = better)
        providers.sort(key=lambda x: x['priority'])
        return providers
    
    def _call_provider(self, provider: Dict, prompt: str, temperature: float = 0.1) -> Optional[str]:
        """Call a specific provider"""
        try:
            # Handle Gemini's different API format
            if provider.get('is_gemini'):
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": temperature}
                }
                response = requests.post(provider['url'], json=payload, headers=provider['headers'], timeout=30)
                if response.status_code == 200:
                    return response.json()['candidates'][0]['content']['parts'][0]['text']
            
            # Handle Hugging Face's different format
            elif provider.get('is_hf'):
                payload = {"inputs": prompt, "parameters": {"temperature": temperature, "max_new_tokens": 2048}}
                response = requests.post(provider['url'], json=payload, headers=provider['headers'], timeout=30)
                if response.status_code == 200:
                    return response.json()[0]['generated_text']
            
            # Standard OpenAI-compatible format (Groq, OpenRouter, Together, DeepInfra)
            else:
                payload = {
                    "model": provider['model'],
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "max_tokens": 2048
                }
                response = requests.post(provider['url'], json=payload, headers=provider['headers'], timeout=30)
                if response.status_code == 200:
                    return response.json()['choices'][0]['message']['content']
            
            # Handle errors
            if response.status_code == 429:
                print(f"⚠️  {provider['name']}: Rate limit hit")
                return None
            elif response.status_code >= 400:
                print(f"⚠️  {provider['name']}: Error {response.status_code}")
                return None
                
        except Exception as e:
            print(f"⚠️  {provider['name']}: {str(e)[:100]}")
            return None
    
    def ask(self, prompt: str, temperature: float = 0.1, max_retries: int = None) -> str:
        """
        Ask question with automatic failover across all providers
        
        Args:
            prompt: The question/prompt to send
            temperature: LLM temperature (0.0-1.0)
            max_retries: Max providers to try (default: all)
        
        Returns:
            LLM response or error message
        """
        if not self.providers:
            return "❌ No LLM providers configured. Add API keys to .env file."
        
        max_retries = max_retries or len(self.providers)
        attempts = 0
        
        # Try providers in priority order, with rotation
        tried_providers = []
        
        while attempts < max_retries:
            # Get next provider (round-robin with priority)
            provider = self.providers[self.current_index % len(self.providers)]
            self.current_index += 1
            
            if provider['name'] in tried_providers:
                attempts += 1
                continue
            
            tried_providers.append(provider['name'])
            print(f"🤖 Trying {provider['name']}...")
            
            response = self._call_provider(provider, prompt, temperature)
            
            if response:
                # Track usage
                self.request_count[provider['name']] = self.request_count.get(provider['name'], 0) + 1
                print(f"✅ {provider['name']} responded ({self.request_count[provider['name']]} requests)")
                return response
            
            attempts += 1
        
        # All providers failed
        return f"❌ All {len(tried_providers)} providers failed. Please check API keys or wait for rate limits to reset."
    
    def get_stats(self) -> Dict:
        """Get usage statistics"""
        return {
            'total_providers': len(self.providers),
            'active_providers': [p['name'] for p in self.providers],
            'request_count': self.request_count,
            'total_requests': sum(self.request_count.values())
        }


# Global instance
_router = None

def get_llm_router() -> MultiLLMRouter:
    """Get or create the global LLM router instance"""
    global _router
    if _router is None:
        _router = MultiLLMRouter()
    return _router


# Simple interface for your existing code
def ask_llm(prompt: str, temperature: float = 0.1) -> str:
    """Simple function to ask any available LLM"""
    router = get_llm_router()
    return router.ask(prompt, temperature)


if __name__ == "__main__":
    # Test the router
    router = MultiLLMRouter()
    
    print("\n" + "="*60)
    print("🧪 TESTING MULTI-LLM ROUTER")
    print("="*60 + "\n")
    
    test_prompt = "Explain what a text file is in 2 sentences."
    response = router.ask(test_prompt)
    
    print(f"\n📝 Response:\n{response}\n")
    print("="*60)
    print("📊 Stats:", router.get_stats())
    print("="*60)
