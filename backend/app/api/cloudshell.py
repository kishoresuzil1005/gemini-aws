from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import pexpect

router = APIRouter(prefix="")

@router.get("/cloudshell-health")
async def health():
    return {"status": "ok"}

@router.websocket("/ws/cloudshell")
async def cloudshell(ws: WebSocket):
    await ws.accept()

    try:
        while True:
            msg = await ws.receive_text()
            await ws.send_text(f"echo: {msg}")
    except WebSocketDisconnect:
        pass
