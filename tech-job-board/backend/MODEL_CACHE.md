# Sentence Transformer Model Caching

## Overview

The resume matching feature uses the `all-MiniLM-L6-v2` Sentence Transformer model for semantic similarity calculations. To eliminate first-use latency, the model is pre-downloaded during Railway deployment.

## Model Details

- **Model**: `all-MiniLM-L6-v2`
- **Size**: ~90MB
- **Purpose**: Semantic similarity matching between resumes and job descriptions
- **Performance**: 384-dimensional embeddings, optimized for speed and quality

## How It Works

1. **Build Time**: During Railway deployment, `download_model.py` runs automatically
2. **Caching**: The model is downloaded and cached in the container's filesystem
3. **Runtime**: First resume match is instant (no download needed)
4. **Persistence**: Model stays cached as long as the container is running

## Storage & Cost Impact

### Railway Storage
- **Model Size**: ~90MB
- **Railway Free Tier**: 1GB disk space included
- **Impact**: Uses ~9% of free tier storage
- **Cost**: $0 on free tier, minimal on paid plans

### Railway Pricing Context
- **Free Tier**: $5/month credit (500 hours of execution time)
- **Paid Plans**: Start at $5/month for Hobby plan
- **Storage**: Included in all plans, no extra charge for cached models
- **Build Time**: Adds ~30-60 seconds to deployment (one-time per deploy)

## Benefits

✅ **Instant Resume Matching**: No 30-60 second wait on first match  
✅ **Better UX**: Users get immediate results  
✅ **Cost Effective**: ~90MB is negligible on Railway  
✅ **Production Ready**: Model is always available  

## Trade-offs

- **Build Time**: +30-60 seconds per deployment (acceptable)
- **Storage**: +90MB (negligible - 9% of 1GB free tier)
- **Memory**: Model loads into RAM (~90MB) when first used

## Verification

After deployment, check Railway logs for:
```
Downloading Sentence Transformer model: all-MiniLM-L6-v2
✓ Model downloaded successfully!
✓ Model size: ~90MB
Resume matching will now be instant on first use!
```

## Alternative Approaches Considered

1. **Lazy Loading (Current Before Fix)**: Downloads on first use - causes 30-60s latency ❌
2. **Pre-download at Build (Implemented)**: Downloads during deployment - instant matching ✅
3. **External Model Storage**: S3/Cloud Storage - adds complexity and latency ❌
4. **Smaller Model**: Less accurate matching - not worth the trade-off ❌

## Conclusion

Pre-downloading the model during Railway deployment is the optimal solution:
- **Cost**: Negligible (~$0)
- **Performance**: Eliminates first-use latency
- **User Experience**: Instant resume matching
- **Maintenance**: Zero - works automatically

The 90MB storage is well within Railway's generous limits and provides significant UX improvements.
