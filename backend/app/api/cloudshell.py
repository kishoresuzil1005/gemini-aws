from fastapi import APIRouter, WebSocket
import asyncio
import pexpect

router = APIRouter(prefix="")

@router.get("/cloudshell-health")
async def health():
    return {"status": "ok"}

@router.websocket("/ws/cloudshell")
async def cloudshell(ws: WebSocket):
    await ws.accept()

    shell = pexpect.spawn(
        "docker exec -it cloud-shell bash",
        encoding="utf-8"
    )

    async def reader():
        while True:
            try:
                data = shell.read_nonblocking(
                    size=1024,
                    timeout=0.1
                )

                await ws.send_text(data)

            except:
                await asyncio.sleep(0.05)

    asyncio.create_task(reader())

    while True:
        cmd = await ws.receive_text()
        shell.send(cmd + "\n")
