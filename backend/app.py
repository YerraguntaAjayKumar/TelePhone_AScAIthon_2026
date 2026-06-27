import asyncio
import os
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from perception.afferens_client import AfferensClient
from perception.scene_builder import SceneBuilder

app = FastAPI()

# Enable CORS so your frontend can communicate with your backend code safely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Session Metrics State Matrix
session_data = {
    "is_active": True,
    "current_state": "INITIALIZING",
    "detected_objects": [],
    "study_seconds": 0,
    "distracted_seconds": 0,
    "distraction_incidents": 0
}

async def background_telemetry_loop():
    """Persistent background task that actively reads from MCP and maintains state."""
    global session_data
    was_distracted_last_frame = False
    
    async with AfferensClient() as client:
        while True:
            try:
                perception = await client.get_vision()
                
                # If the dashboard stream isn't sending data, pause tracking gracefully
                if perception.get("status") == 404 or "error" in perception:
                    session_data["current_state"] = "PAUSED (OFFLINE)"
                    await asyncio.sleep(2.0)
                    continue
                
                scene = SceneBuilder.build(perception)
                session_data["detected_objects"] = scene.objects
                
                # State Analytics Rules
                if not scene.person or scene.phone:
                    current_distracted = True
                    session_data["distracted_seconds"] += 1
                    session_data["current_state"] = "DISTRACTED"
                else:
                    current_distracted = False
                    session_data["study_seconds"] += 1
                    session_data["current_state"] = "STUDYING"
                
                # Track state transitions to calculate incident boundaries
                if current_distracted and not was_distracted_last_frame:
                    session_data["distraction_incidents"] += 1
                    
                was_distracted_last_frame = current_distracted
                
            except Exception as e:
                print(f"Telemetry engine background exception: {e}")
                
            await asyncio.sleep(1.0)

@app.on_event("startup")
async def startup_event():
    """Starts the background processing script thread immediately on application launch."""
    asyncio.create_task(background_telemetry_loop())

@app.get("/api/telemetry")
async def get_telemetry():
    """API Endpoint for the frontend interface to pull real-time student statistics."""
    return session_data