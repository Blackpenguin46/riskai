# AI Service Configuration

## Overview

RiskAI includes **two AI services** that work differently:

### 1. **AI Feedback Generator** (Works WITHOUT API keys)
- **Location**: Assessment results page after completing the 120-question assessment
- **Technology**: Rule-based AI + RAG pipeline with cybersecurity knowledge base
- **Requirements**: None - works out of the box
- **Features**:
  - Comprehensive feedback on assessment results
  - Industry-specific recommendations
  - Framework-aligned guidance (NIST, ISO 27001, CIS Controls)
  - Risk prioritization
  - Implementation roadmaps

**This service is ALWAYS available** and uses the 80+ cybersecurity research papers and frameworks stored in the `/data` directory.

### 2. **AI Chatbot Consultant** (Optional - Requires OpenAI API key)
- **Location**: `/chatbot` page - Interactive conversation interface
- **Technology**: OpenAI GPT models
- **Requirements**: OpenAI API key (optional)
- **Features**:
  - Interactive cybersecurity consultation
  - Real-time Q&A
  - Custom advice based on your situation
  - Planning assistance

## Using Without OpenAI API Key

**Good news**: The core AI functionality (assessment feedback) works **without any API keys**!

The chatbot will show a fallback message if no API key is provided, but **all assessment features work fully**.

## Adding OpenAI API Key (Optional)

If you want to enable the interactive chatbot:

### Docker Deployment

Add to `docker-compose.yml`:

```yaml
services:
  backend:
    environment:
      - OPENAI_API_KEY=your_api_key_here
```

Or use an `.env` file:

```bash
# .env file
OPENAI_API_KEY=your_api_key_here
```

Then:
```bash
docker-compose up -d
```

### Manual Installation

```bash
export OPENAI_API_KEY=your_api_key_here  # Linux/macOS
# OR
set OPENAI_API_KEY=your_api_key_here     # Windows CMD
# OR
$env:OPENAI_API_KEY="your_api_key_here"  # Windows PowerShell
```

## Getting an OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Create a new API key
4. Add billing information (pay-as-you-go)
5. Copy the key and add to your environment

**Cost**: Typically $0.01-0.10 per conversation depending on length

## What Works Without API Keys

✅ **WORKS WITHOUT API KEY:**
- ✅ 120-question enterprise assessment
- ✅ Dynamic scoring with industry benchmarks
- ✅ AI-powered feedback and recommendations
- ✅ RAG-enhanced guidance from research papers
- ✅ Framework-aligned recommendations
- ✅ Risk categorization and prioritization
- ✅ Implementation roadmaps
- ✅ Industry comparisons

❌ **REQUIRES API KEY:**
- ❌ Interactive chatbot conversations
- ❌ Real-time Q&A with AI consultant

## Verification

Check if AI services are working:

```bash
# Check backend logs
docker-compose logs backend | grep -i "rag\|feedback"

# Should see:
# "RAG pipeline initialized successfully"
# "AI feedback generated successfully"
```

Test the assessment feedback:
1. Complete an assessment at http://localhost:3000/real-assessment
2. Submit your answers
3. View comprehensive AI feedback in results

## Troubleshooting

**"RAG pipeline not initialized"**
- Check that `/app/data` directory exists in container
- Verify PDFs were copied during Docker build
- Check logs: `docker-compose logs backend`

**"AI feedback is generic"**
- This is expected without RAG pipeline
- Ensure data files are in Docker image
- Rebuild: `docker-compose up --build`

**"Chatbot says service unavailable"**
- This is normal without OpenAI API key
- Assessment feedback still works
- Add API key if you want chatbot

## Summary

**You DO NOT need any API keys or local LLMs to use RiskAI!**

The AI feedback system works entirely with:
- Rule-based analysis
- Industry benchmarks
- Framework mappings
- RAG pipeline with research papers

The optional chatbot requires OpenAI but is **NOT required** for the core platform functionality.