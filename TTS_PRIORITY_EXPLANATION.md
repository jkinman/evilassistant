# 🔥 Evil Assistant TTS Priority System

## Current Provider Priority (Cost-Optimized)

### Priority 0: gTTS Demonic (PRIMARY - FREE)
- **Provider**: Google Text-to-Speech + SoX Effects
- **Cost**: 100% FREE ✅
- **Quality**: Proven demonic voice with excellent effects
- **Speed**: Fast (~300ms generation)
- **Availability**: Always available with internet
- **Effects**: Deep pitch shift, reverb, bass boost, distortion

### Priority 1: Piper (FALLBACK - FREE)
- **Provider**: Neural TTS (local)
- **Cost**: 100% FREE ✅
- **Quality**: High-quality neural voices
- **Speed**: Very fast (local processing)
- **Availability**: Always available (offline)
- **Effects**: Configurable voice profiles

### Priority 2: Espeak (EMERGENCY FALLBACK - FREE)
- **Provider**: System TTS
- **Cost**: 100% FREE ✅
- **Quality**: Basic but functional
- **Speed**: Very fast
- **Availability**: Always available
- **Effects**: Basic demonic transformation

### Priority 3: ElevenLabs (PREMIUM ONLY - EXPENSIVE)
- **Provider**: ElevenLabs API
- **Cost**: 💰 EXPENSIVE (pay per character)
- **Quality**: Premium AI voice
- **Speed**: Depends on API
- **Availability**: Only when `USE_ELEVENLABS_PREMIUM=true`
- **Usage**: Manual override only for special occasions

## How to Enable ElevenLabs (if needed)

ElevenLabs is now **disabled by default** to prevent unexpected costs.

### To enable ElevenLabs premium:
```bash
# Add to .env file
USE_ELEVENLABS_PREMIUM=true
ELEVENLABS_API_KEY=your_key_here
```

### Cost Protection:
- ElevenLabs only activates with explicit `USE_ELEVENLABS_PREMIUM=true` flag
- No accidental usage
- All other providers are free
- System falls back gracefully if ElevenLabs fails

## Default Behavior

**Normal operation** (no flags):
1. gTTS Demonic (free, high quality)
2. Piper (free, fast)
3. Espeak (free, basic)

**Premium operation** (with `USE_ELEVENLABS_PREMIUM=true`):
1. gTTS Demonic (free, high quality)
2. Piper (free, fast)
3. Espeak (free, basic)
4. ElevenLabs (expensive, premium)

## Benefits

✅ **Cost Control**: No unexpected charges
✅ **Quality**: gTTS Demonic proven to work excellently
✅ **Reliability**: Multiple free fallbacks
✅ **Performance**: Fast, local options available
✅ **Flexibility**: Premium option available when needed

The Evil Assistant now runs cost-effectively while maintaining excellent demonic voice quality! 🔥
