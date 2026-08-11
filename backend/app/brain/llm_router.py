"""
Ultron Core Multi-Client LLM Router
Handles caching checks, async HTTPX connection pooling, automatic rate-limit rotations,
and absolute failover cascade logic from Groq to Gemini.
Employs Dependency Injection to delegate cache bypass decisions to a BaseCachePolicy.
"""

import hashlib
import json
import httpx
from typing import Dict, Any, Optional

from backend.app.brain.api_key_manager import APIKeyManager
from backend.app.brain.smart_cache import SmartCache
from backend.app.brain.cache_policy import BaseCachePolicy, HeuristicKeywordCachePolicy

class LLMRouter:
    def __init__(
        self,
        key_manager: Optional[APIKeyManager] = None,
        cache: Optional[SmartCache] = None,
        cache_policy: Optional[BaseCachePolicy] = None
    ) -> None:
        self.key_manager = key_manager or APIKeyManager()
        self.cache = cache or SmartCache()
        # Decoupled Cache Policy Dependency Injection (SOLID compliant)
        self.cache_policy = cache_policy or HeuristicKeywordCachePolicy()
        
        # Standardize asynchronous HTTPX client configurations
        self.limits = httpx.Limits(max_keepalive_connections=5, max_connections=20)
        self.client = httpx.AsyncClient(limits=self.limits, timeout=30.0)

    def _generate_cache_hash(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Generates unique SHA-256 identifier hash to map request payload configurations."""
        payload = f"{system_prompt}|||{user_prompt}|||{temperature}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    async def get_completions(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        provider_preference: str = "groq"
    ) -> str:
        """
        Main query router. Asks the decoupled cache policy whether caching should
        be bypassed, keeping the router completely blind to the policy's implementation rules.
        """
        cache_key = self._generate_cache_hash(system_prompt, user_prompt, temperature)
        
        # 1. Ask the decoupled policy whether to bypass cache
        cache_skip = self.cache_policy.should_bypass_cache(system_prompt, user_prompt)
        
        # 2. Query Local Smart Cache First (If permitted by the policy)
        if not cache_skip:
            cached_val = self.cache.get(cache_key)
            if cached_val:
                print("[LLM_ROUTER] Smart Cache Hit. Resolving response in <1ms.")
                return cached_val
        else:
            print("[LLM_ROUTER] Cache Policy triggered bypass. Querying live brain client.")

        # 3. Process Cascade Flow
        try:
            if provider_preference.lower() == "groq":
                response = await self._execute_groq_pipeline(system_prompt, user_prompt, temperature)
            else:
                response = await self._execute_gemini_pipeline(system_prompt, user_prompt, temperature)
                
            # Update cache registry upon successful API execution (if permitted by the policy)
            if not cache_skip:
                self.cache.set(cache_key, response)
            return response
            
        except Exception as e:
            # If primary path failed, fall back automatically to backup system channel
            fallback_provider = "gemini" if provider_preference.lower() == "groq" else "groq"
            print(f"[LLM_ROUTER] Primary path failed: {e}. Executing immediate failover cascade to {fallback_provider}...")
            
            try:
                if fallback_provider == "gemini":
                    response = await self._execute_gemini_pipeline(system_prompt, user_prompt, temperature)
                else:
                    response = await self._execute_groq_pipeline(system_prompt, user_prompt, temperature)
                    
                if not cache_skip:
                    self.cache.set(cache_key, response)
                return response
            except Exception as final_err:
                raise RuntimeError(f"Global key pool depletion error. All providers failed: {final_err}")

    async def _execute_groq_pipeline(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Dispatches async query to Groq chat completions. Handles automatic 429 rotation."""
        url = "https://api.groq.com/openai/v1/chat/completions"
        max_attempts = 3
        
        for attempt in range(max_attempts):
            api_key = self.key_manager.get_active_key("groq")
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": temperature,
                "max_tokens": 80
            }
            
            try:
                # Custom bypass for local diagnostics testing if dummy_key is passed
                if "dummy_fallback" in api_key:
                    return f"[Mock Groq Response] Query parsed successfully: {user_prompt[:20]}..."
                
                response = await self.client.post(url, headers=headers, json=payload, timeout=20.0)
                
                # Check for rate-limiting
                if response.status_code == 429:
                    self.key_manager.mark_key_cooling("groq", api_key, cooldown_duration_sec=60)
                    continue  # Triggers next iteration loop with next active key
                    
                if response.status_code != 200:
                    self.key_manager.mark_key_failed("groq", api_key)
                    continue
                    
                res_data = response.json()
                return res_data["choices"][0]["message"]["content"]
                
            except (httpx.RequestError, KeyError) as e:
                # Catch network level or key mapping failures and transition key state
                self.key_manager.mark_key_cooling("groq", api_key, duration_sec=30)
                if attempt == max_attempts - 1:
                    raise RuntimeError(f"All Groq retry attempts exhausted. Final exception: {e}")
                    
        raise RuntimeError("Failed to resolve completions via Groq key rotation pool.")

    async def _execute_gemini_pipeline(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Dispatches async query to Gemini v1beta API. Handles automatic error rotation."""
        model = "gemini-1.5-flash"
        max_attempts = 2
        
        for attempt in range(max_attempts):
            api_key = self.key_manager.get_active_key("gemini")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            
            payload = {
                "contents": [{
                    "parts": [{"text": f"System Guidelines: {system_prompt}\n\nUser Query: {user_prompt}"}]
                }],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": 80
                }
            }
            
            try:
                if "dummy_fallback" in api_key:
                    return f"[Mock Gemini Response] Query processed: {user_prompt[:20]}..."
                
                response = await self.client.post(url, headers=headers, json=payload, timeout=25.0)
                
                if response.status_code == 429:
                    self.key_manager.mark_key_cooling("gemini", api_key, duration_sec=60)
                    continue
                    
                if response.status_code != 200:
                    self.key_manager.mark_key_failed("gemini", api_key)
                    continue
                    
                res_data = response.json()
                return res_data["candidates"][0]["content"]["parts"][0]["text"]
                
            except (httpx.RequestError, KeyError) as e:
                self.key_manager.mark_key_cooling("gemini", api_key, duration_sec=30)
                if attempt == max_attempts - 1:
                    raise RuntimeError(f"Gemini connection attempts exhausted. Exception: {e}")
                    
        raise RuntimeError("Failed to resolve completions via Gemini key rotation pool.")

    async def close(self) -> None:
        """Cleanly releases and closes underlying HTTPX client connection pools."""
        await self.client.aclose()
