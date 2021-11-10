
import logging
import re
import os
from fastapi import FastAPI, WebSocket
from fastapi.responses import StreamingResponse
from starlette.websockets import WebSocketDisconnect
import pygtail
from . import settings

logging.basicConfig(level = logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

log_file_name = lambda nm: os.path.join(settings.SERVICES_DIRECTORY, nm+".log")

def stream_logfile(filename: str):
    with open(filename) as f:
        lines = f.readlines()
    yield lines

    tail = pygtail.Pygtail(filename)
    while True:
        yield [*tail]

@app.get("/log")
def list_logs():
    files = os.listdir(settings.SERVICES_DIRECTORY)
    return {"logs":[os.path.splitext(f)[0] for f in files if re.search("^[a-zA-Z0-9_-]+.log$",f)]}

@app.get("/log/{name}")
def get_log(name: str):
    def iterfile():
        with open(log_file_name(name)) as f:
            yield from f
    return StreamingResponse(iterfile(), media_type = "text/plain")

@app.websocket("/log/{name}/ws")
async def stream_log(name: str, websocket: WebSocket):
    await websocket.accept()

    try:
        stream = stream_logfile(log_file_name(name))
    except FileNotFoundError:
        websocket.close(status=4000)

    for lines in stream:
        try:
            await websocket.receive_text()
            if lines:
                for line in lines:
                    await websocket.send_text(line)
        except WebSocketDisconnect:
            break
