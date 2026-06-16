from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import pexpect

router = APIRouter()

@router.get("/cloudshell-health")
async def health():
    return {"status": "ok"}


@router.websocket("/ws/cloudshell")
async def cloudshell(ws: WebSocket):

    await ws.accept()

    shell = pexpect.spawn(
        "docker exec -it cloud-shell bash",
        encoding="utf-8",
        echo=False
    )

    async def stream_output():
        while True:
            try:
                output = shell.read_nonblocking(
                    size=4096,
                    timeout=0.1
                )

                if output:
                    await ws.send_text(output)

            except pexpect.TIMEOUT:
                await asyncio.sleep(0.02)

            except Exception:
                break

    output_task = asyncio.create_task(
        stream_output()
    )

    try:
        while True:

            command = await ws.receive_text()

            shell.send(command)

    except WebSocketDisconnect:
        pass

    finally:
        output_task.cancel()

        try:
            shell.close(force=True)
        except:
            pass
