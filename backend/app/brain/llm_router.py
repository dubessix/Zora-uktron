"""
Ultron Core Multi-Client LLM Router
Handles caching checks, async HTTPX connection pooling, automatic rate-limit rotations,
and absolute failover cascade logic from Groq to Gemini.
Employs Dependency Injection to delegate cache bypass decisions to a BaseCachePolicy.
"""

import hashlib
import httpx
from typing import Optional

from backend.app.brain.api_key_manager import APIKeyManager
from backend.app.brain.smart_cache import SmartCache
from backend.app.brain.cache_policy import BaseCachePolicy, HeuristicKeywordCachePolicy
from backend.app.brain.model_config import get_model

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

    # Ordered failover cascade per primary preference. Each list defines the
    # fallback order when the preferred provider fails or rate-limits.
    _CASCADE = {
        "groq":   ["groq", "gemini", "nvidia"],
        "gemini": ["gemini", "groq", "nvidia"],
        "nvidia": ["nvidia", "groq", "gemini"],
    }

    def _provider_executor(self, provider: str):
        """Return the async executor callable for a provider name."""
        if provider == "groq":
            return self._execute_groq_pipeline
        if provider == "gemini":
            return self._execute_gemini_pipeline
        if provider == "nvidia":
            return self._execute_nvidia_pipeline
        raise ValueError(f"Unsupported provider: {provider}")

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
        Executes providers in the failover cascade order.
        """
        cache_key = self._generate_cache_hash(system_prompt, user_prompt, temperature)
        pref = provider_preference.lower() if provider_preference.lower() in self._CASCADE else "groq"

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

        # 3. Process Cascade Flow (ordered failover). A provider with no real key
        #    configured is SKIPPED entirely — it must not return a fake mock that
        #    shadows a later provider which actually has a working key.
        cascade = self._CASCADE[pref]
        last_err = None
        used_any = False
        for idx, provider in enumerate(cascade):
            if not self.key_manager.has_real_key(provider):
                print(f"[LLM_ROUTER] No configured key for '{provider}' — skipping to fallback.")
                continue
            used_any = True
            try:
                executor = self._provider_executor(provider)
                response = await executor(system_prompt, user_prompt, temperature)
                if not cache_skip:
                    self.cache.set(cache_key, response)
                return response
            except Exception as e:
                last_err = e
                if idx < len(cascade) - 1:
                    print(f"[LLM_ROUTER] Provider '{provider}' failed: {e}. Failing over to '{cascade[idx+1]}'...")

        # If NO real key exists anywhere, this is a fully-offline/local install.
        # Return an honest local mock so the assistant still works without the
        # internet — never pretend a provider was used.
        if not used_any:
            print("[LLM_ROUTER] No real API keys configured anywhere — using local offline mock.")
            return f"[Mock {pref.upper()} Response] Query parsed successfully: {user_prompt[:20]}..."
        raise RuntimeError(f"Global key pool depletion error. All providers failed: {last_err}")

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
                "model": get_model("groq"),
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": temperature,
                # Room for both a short human answer AND the [TOOL_CALLS] JSON block.
                # Answer length is kept short by the personality system-prompt (25-40 words),
                # NOT by the token cap, so tool-calling no longer gets truncated.
                "max_tokens": 512
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
        # Config-driven (env GEMINI_CHAT_MODEL / config.yaml). Default gemini-3.5-flash
        # is a stable, long-runway replacement for the retired gemini-1.5-flash.
        model = get_model("gemini")
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
                    # Answer length is kept short by the personality system-prompt (25-40 words).
                    # 512 leaves room for the [TOOL_CALLS] JSON block so tool-calling isn't cut off.
                    "maxOutputTokens": 512
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

    async def _execute_nvidia_pipeline(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Dispatches async query to NVIDIA Build (NIM) OpenAI-compatible endpoint.
        Best-of-breed coding model. Handles automatic 429 key rotation + cooling."""
        url = "https://integrate.api.nvidia.com/v1/chat/completions"
        # Nemotron 3 Ultra 550B: NVIDIA's strongest agent/coding-focused open model.
        # NOTE: the `:free` suffix is an OpenRouter convention and is NOT valid on
        # NVIDIA's native build endpoint. Config-driven (env NVIDIA_CHAT_MODEL).
        model = get_model("nvidia")
        max_attempts = 3

        for attempt in range(max_attempts):
            api_key = self.key_manager.get_active_key("nvidia")
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": temperature,
                "max_tokens": 1024
            }

            try:
                if "dummy_fallback" in api_key:
                    return f"[Mock NVIDIA Response] Query processed: {user_prompt[:20]}..."
                response = await self.client.post(url, headers=headers, json=payload, timeout=40.0)
                if response.status_code == 429:
                    self.key_manager.mark_key_cooling("nvidia", api_key, cooldown_duration_sec=60)
                    continue
                if response.status_code != 200:
                    self.key_manager.mark_key_failed("nvidia", api_key)
                    continue
                res_data = response.json()
                return res_data["choices"][0]["message"]["content"]
            except (httpx.RequestError, KeyError) as e:
                self.key_manager.mark_key_cooling("nvidia", api_key, duration_sec=30)
                if attempt == max_attempts - 1:
                    raise RuntimeError(f"NVIDIA connection attempts exhausted. Exception: {e}")

        raise RuntimeError("Failed to resolve completions via NVIDIA key rotation pool.")

    async def close(self) -> None:
        """Cleanly releases and closes underlying HTTPX client connection pools."""
        await self.client.aclose()
