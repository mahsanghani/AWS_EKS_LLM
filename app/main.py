apiVersion: v1
kind: ConfigMap
metadata:
  name: app-code
  namespace: llm-deployment
data:
  main.py: |
    import os
    import torch
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import uvicorn
    import logging
    from typing import Optional
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Configuration
    MODEL_NAME = os.getenv("MODEL_NAME", "microsoft/DialoGPT-medium")
    MAX_LENGTH = int(os.getenv("MAX_LENGTH", "512"))
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    
    app = FastAPI(title="LLM API", version="1.0.0")
    
    # Request/Response models
    class GenerateRequest(BaseModel):
        prompt: str
        max_length: Optional[int] = 100
        temperature: Optional[float] = 0.7
        top_p: Optional[float] = 0.9
        do_sample: Optional[bool] = True
    
    class GenerateResponse(BaseModel):
        generated_text: str
        model_name: str
        processing_time: float
    
    class HealthResponse(BaseModel):
        status: str
        model_loaded: bool
        device: str
    
    # Global variables for model and tokenizer
    model = None
    tokenizer = None
    executor = ThreadPoolExecutor(max_workers=4)
    
    @app.on_event("startup")
    async def load_model():
        global model, tokenizer
        logger.info(f"Loading model: {MODEL_NAME}")
        
        try:
            tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            model = AutoModelForCausalLM.from_pretrained(
                MODEL_NAME,
                torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
                device_map="auto" if DEVICE == "cuda" else None
            )
            
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
                
            logger.info(f"Model loaded successfully on {DEVICE}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def generate_text(prompt: str, max_length: int, temperature: float, top_p: float, do_sample: bool):
        """Generate text using the loaded model"""
        try:
            inputs = tokenizer.encode(prompt, return_tensors="pt")
            if DEVICE == "cuda":
                inputs = inputs.to(DEVICE)
            
            with torch.no_grad():
                outputs = model.generate(
                    inputs,
                    max_length=max_length,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=do_sample,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            return generated_text[len(prompt):].strip()
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise
    
    @app.post("/generate", response_model=GenerateResponse)
    async def generate_endpoint(request: GenerateRequest):
        if model is None or tokenizer is None:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        import time
        start_time = time.time()
        
        try:
            # Run generation in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            generated_text = await loop.run_in_executor(
                executor,
                generate_text,
                request.prompt,
                request.max_length,
                request.temperature,
                request.top_p,
                request.do_sample
            )
            
            processing_time = time.time() - start_time
            
            return GenerateResponse(
                generated_text=generated_text,
                model_name=MODEL_NAME,
                processing_time=processing_time
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        return HealthResponse(
            status="healthy",
            model_loaded=model is not None,
            device=DEVICE
        )
    
    @app.get("/")
    async def root():
        return {"message": "LLM API is running", "model": MODEL_NAME}
    
    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=8000)