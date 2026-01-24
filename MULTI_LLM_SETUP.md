# 🚀 MULTI-LLM SETUP GUIDE
## Get Unlimited Free LLM Requests!

---

## ⚡ QUICK START (5 Minutes)

### Step 1: Get Free API Keys

Visit these sites and get your FREE API keys:

1. **Groq** (FASTEST, 14,400 req/day)
   - Go to: https://console.groq.com/keys
   - Click "Create API Key"
   - Copy the key: `gsk_...`

2. **OpenRouter** (50+ models, 50 req/day each)
   - Go to: https://openrouter.ai/keys
   - Click "Create Key"
   - Copy the key: `sk-or-v1-...`

3. **Together AI** ($25 free credit = ~1M tokens)
   - Go to: https://together.ai/app
   - Sign up → API Keys
   - Copy the key

4. **DeepInfra** (Free tier)
   - Go to: https://deepinfra.com
   - Settings → API Keys
   - Copy the key

5. **Gemini** (1,500 req/day)
   - Go to: https://aistudio.google.com/app/apikey
   - Get API Key
   - Copy the key: `AIza...`

6. **Hugging Face** (Rate-limited free)
   - Go to: https://huggingface.co/settings/tokens
   - New Token → Read
   - Copy the key: `hf_...`

---

### Step 2: Update `.env` File

Copy `.env.example` to `.env` and add your actual API keys:

```bash
# Copy the example file
cp .env.example .env

# Then edit .env with your actual keys:
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
DEEPINFRA_API_KEY=your_deepinfra_api_key_here
```

**Minimum Required:** Just add **ONE** API key to get started (Groq or OpenRouter recommended)

---

### Step 3: Test the Router

```powershell
# Test the multi-LLM router
python multi_llm_router.py
```

You should see:
```
🚀 Multi-LLM Router Initialized
✅ Active Providers: 6
   - Groq
   - OpenRouter
   - Together AI
   - DeepInfra
   - Gemini
   - Hugging Face
```

---

### Step 4: Run the New Server

```powershell
# Stop old server
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Start new multi-LLM server
python ultimate_server_multi_llm.py
```

You should see:
```
🚀 ULTIMATE SERVER WITH MULTI-LLM ROUTER
📍 URL: http://localhost:5000

💡 Features:
   ✅ Unlimited free requests (6 LLM providers)
   ✅ Automatic failover & load balancing
   ✅ Page-specific RAG queries
   ✅ RAW mode for exact text
```

---

### Step 5: Test It!

1. **Upload PDF:**
   - Go to http://localhost:5000
   - Upload `computer 12ch2.pdf`

2. **Test RAW mode:**
   ```
   RAW page 2
   ```
   ✅ Should show exact NCERT text

3. **Test EXPLAIN mode:**
   ```
   explain page 2
   ```
   ✅ Should get beautiful explanation

4. **Test failover:**
   ```
   page 3
   page 5
   page 6
   page 8
   ```
   ✅ Should work even if one API hits rate limit!

---

## 🎯 How It Works

### Automatic Failover:
1. Try **Groq** first (fastest)
2. If rate limited → try **OpenRouter**
3. If that fails → try **Together AI**
4. If that fails → try **DeepInfra**
5. If that fails → try **Gemini**
6. If that fails → try **Hugging Face**

### Load Balancing:
- Rotates between providers automatically
- Spreads requests across all APIs
- Tracks usage per provider

### Total Free Capacity:
- **Groq:** 14,400 req/day
- **OpenRouter:** 50 req/day (but 50+ models)
- **Together AI:** ~1M tokens ($25 credit)
- **DeepInfra:** Free tier
- **Gemini:** 1,500 req/day
- **Hugging Face:** Rate-limited

**TOTAL: ~20,000+ requests/day!**

---

## 📊 Check Status

Visit: http://localhost:5000/api/status

You'll see:
```json
{
  "llm_providers": ["Groq", "OpenRouter", "Together AI", ...],
  "total_requests": 42,
  "request_count": {
    "Groq": 25,
    "OpenRouter": 10,
    "Together AI": 7
  }
}
```

---

## 🔧 Troubleshooting

### "No LLM providers available"
- Add at least ONE API key to `.env`
- Restart the server

### "All providers failed"
- Check your API keys are correct
- Wait a few minutes for rate limits to reset
- Add more API keys

### One provider keeps failing
- That's OK! The router will skip it and use others
- Check if the API key is valid

---

## ✅ Success Checklist

- [ ] Got at least 2 API keys
- [ ] Updated `.env` file
- [ ] Tested `multi_llm_router.py`
- [ ] Started `ultimate_server_multi_llm.py`
- [ ] Uploaded PDF successfully
- [ ] Tested "RAW page 2" - works!
- [ ] Tested "explain page 2" - works!
- [ ] Tested multiple pages - no rate limits!

---

## 🎉 You're Done!

You now have **unlimited free LLM requests** with automatic failover!

No more quota errors! 🚀
