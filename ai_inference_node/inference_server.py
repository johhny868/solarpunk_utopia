"""
AI Inference Node - Provide AI capabilities to the mesh network

This service allows anyone to contribute AI inference to the mesh network.
Just run this on any machine with a GPU (or CPU) and it will automatically
register with the mesh and start serving inference requests.

Supports:
- Ollama (recommended - easy setup)
- llama.cpp (direct model loading)
- OpenAI-compatible APIs
- Custom model endpoints
"""

import os
import json
import asyncio
import httpx
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import structlog

# Configure logging
logger = structlog.get_logger()

app = FastAPI(
    title="AI Inference Node",
    description="Distributed AI inference for mesh networks",
    version="1.0.0"
)

# CORS for mesh network access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Mesh network - open access
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Configuration
class InferenceConfig:
    """Configuration for the inference node"""

    def __init__(self):
        self.node_id = os.getenv("NODE_ID", f"inference-node-{os.urandom(4).hex()}")
        self.backend_type = os.getenv("INFERENCE_BACKEND", "ollama")  # ollama, llamacpp, openai
        self.backend_url = os.getenv("INFERENCE_URL", "http://localhost:11434")
        self.default_model = os.getenv("DEFAULT_MODEL", "llama3.2:3b")

        # Resource limits
        self.max_concurrent_requests = int(os.getenv("MAX_CONCURRENT", "5"))
        self.max_tokens = int(os.getenv("MAX_TOKENS", "2048"))
        self.timeout_seconds = int(os.getenv("TIMEOUT", "120"))

        # Mesh integration
        self.dtn_bundle_url = os.getenv("DTN_BUNDLE_URL", "http://localhost:8000")
        self.register_with_mesh = os.getenv("REGISTER_WITH_MESH", "true").lower() == "true"

        # Gift economy tracking
        self.track_contributions = os.getenv("TRACK_CONTRIBUTIONS", "true").lower() == "true"


config = InferenceConfig()

# Request tracking
inference_stats = {
    "total_requests": 0,
    "total_tokens": 0,
    "models_served": set(),
    "started_at": datetime.utcnow().isoformat(),
}


# API Models
class InferenceRequest(BaseModel):
    """Request for AI inference"""
    prompt: str
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = 0.7
    system_prompt: Optional[str] = None

    # Requester info (for gift economy tracking)
    requester_id: Optional[str] = None
    requester_location: Optional[str] = None


class InferenceResponse(BaseModel):
    """Response from inference"""
    response: str
    model: str
    tokens_used: int
    provider_node: str
    timestamp: str


class NodeStatus(BaseModel):
    """Status of this inference node"""
    node_id: str
    backend: str
    available_models: List[str]
    max_concurrent: int
    current_load: int
    total_served: int
    uptime_seconds: float


# Inference backends
async def ollama_inference(prompt: str, model: str, **kwargs) -> Dict[str, Any]:
    """Run inference using Ollama"""
    async with httpx.AsyncClient(timeout=config.timeout_seconds) as client:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.7),
                "num_predict": kwargs.get("max_tokens", config.max_tokens),
            }
        }

        if system := kwargs.get("system_prompt"):
            payload["system"] = system

        response = await client.post(
            f"{config.backend_url}/api/generate",
            json=payload
        )
        response.raise_for_status()
        data = response.json()

        return {
            "response": data.get("response", ""),
            "tokens": data.get("eval_count", 0),
        }


async def openai_inference(prompt: str, model: str, **kwargs) -> Dict[str, Any]:
    """Run inference using OpenAI-compatible API"""
    async with httpx.AsyncClient(timeout=config.timeout_seconds) as client:
        messages = []

        if system := kwargs.get("system_prompt"):
            messages.append({"role": "system", "content": system})

        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", config.max_tokens),
        }

        response = await client.post(
            f"{config.backend_url}/v1/chat/completions",
            json=payload,
            headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY', '')}"}
        )
        response.raise_for_status()
        data = response.json()

        choice = data["choices"][0]
        return {
            "response": choice["message"]["content"],
            "tokens": data["usage"]["total_tokens"],
        }


# Mesh network integration
async def register_with_mesh():
    """Register this inference node with the mesh network"""
    if not config.register_with_mesh:
        return

    try:
        async with httpx.AsyncClient() as client:
            # Register as a service provider in ValueFlows
            payload = {
                "agent_id": config.node_id,
                "service_type": "ai_inference",
                "capabilities": {
                    "backend": config.backend_type,
                    "default_model": config.default_model,
                    "max_concurrent": config.max_concurrent_requests,
                },
                "endpoint": f"http://localhost:8003",  # This service
            }

            # Try to register (may fail if VF not running - that's ok)
            await client.post(
                f"{config.dtn_bundle_url}/agents/register-service",
                json=payload,
                timeout=5.0
            )
            logger.info("registered_with_mesh", node_id=config.node_id)
    except Exception as e:
        logger.warning("mesh_registration_failed", error=str(e))


# API endpoints
@app.on_event("startup")
async def startup():
    """Start the inference node"""
    logger.info(
        "inference_node_starting",
        node_id=config.node_id,
        backend=config.backend_type,
        model=config.default_model,
    )

    # Register with mesh
    asyncio.create_task(register_with_mesh())


@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "running",
        "node_id": config.node_id,
        "backend": config.backend_type,
    }


@app.get("/status", response_model=NodeStatus)
async def get_status():
    """Get node status and capabilities"""
    uptime = (datetime.utcnow() - datetime.fromisoformat(inference_stats["started_at"])).total_seconds()

    # Try to get available models from backend
    available_models = [config.default_model]
    try:
        if config.backend_type == "ollama":
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{config.backend_url}/api/tags")
                data = resp.json()
                available_models = [m["name"] for m in data.get("models", [])]
    except:
        pass

    return NodeStatus(
        node_id=config.node_id,
        backend=config.backend_type,
        available_models=available_models,
        max_concurrent=config.max_concurrent_requests,
        current_load=0,  # TODO: track active requests
        total_served=inference_stats["total_requests"],
        uptime_seconds=uptime,
    )


@app.post("/inference", response_model=InferenceResponse)
async def run_inference(request: InferenceRequest):
    """Run inference on a prompt"""
    model = request.model or config.default_model

    logger.info(
        "inference_request",
        model=model,
        prompt_length=len(request.prompt),
        requester=request.requester_id,
    )

    try:
        # Route to appropriate backend
        if config.backend_type == "ollama":
            result = await ollama_inference(
                request.prompt,
                model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                system_prompt=request.system_prompt,
            )
        elif config.backend_type == "openai":
            result = await openai_inference(
                request.prompt,
                model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                system_prompt=request.system_prompt,
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported backend: {config.backend_type}")

        # Update stats
        inference_stats["total_requests"] += 1
        inference_stats["total_tokens"] += result["tokens"]
        inference_stats["models_served"].add(model)

        # Track contribution (gift economy)
        if config.track_contributions and request.requester_id:
            asyncio.create_task(track_contribution(
                provider=config.node_id,
                requester=request.requester_id,
                tokens=result["tokens"],
                model=model,
            ))

        return InferenceResponse(
            response=result["response"],
            model=model,
            tokens_used=result["tokens"],
            provider_node=config.node_id,
            timestamp=datetime.utcnow().isoformat(),
        )

    except httpx.HTTPError as e:
        logger.error("inference_failed", error=str(e))
        raise HTTPException(status_code=503, detail=f"Inference backend error: {str(e)}")


async def track_contribution(provider: str, requester: str, tokens: int, model: str):
    """Track AI inference contribution in gift economy"""
    try:
        async with httpx.AsyncClient() as client:
            # Log as a ValueFlows economic event
            await client.post(
                f"{config.dtn_bundle_url}/vf/events",
                json={
                    "event_type": "service_provided",
                    "provider_id": provider,
                    "receiver_id": requester,
                    "resource_type": "ai_inference",
                    "quantity": tokens,
                    "unit": "tokens",
                    "metadata": {
                        "model": model,
                        "service": "ai_inference",
                    }
                },
                timeout=5.0
            )
    except Exception as e:
        logger.warning("contribution_tracking_failed", error=str(e))


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8003"))

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
