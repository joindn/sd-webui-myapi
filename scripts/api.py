from fastapi import FastAPI, Depends, Body, HTTPException, APIRouter
from pathlib import Path
import base64
import os
import gradio as gr
from modules.api.api import Api
from modules.call_queue import queue_lock
import logging

logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="/myapi")

def create_api(_: gr.Blocks, app: FastAPI):
    api = Api(app, queue_lock)
    
    @router.post("/model", dependencies=[Depends(api.auth)])
    async def uploadModel(
        chunkNumber: int = Body(..., title='chunk number'),
        content: str = Body(..., title='chunk content'),
        filename: str = Body(..., title='filename'),
        modelType: str = Body("Stable-diffusion", title='model type'),
        overwrite: bool = Body(False, title='overwrite'),
    ):
        model_dir = Path(os.getcwd()) / 'models' / modelType
        model_dir.mkdir(parents=True, exist_ok=True)
        file_path = model_dir / filename

        try:
            if chunkNumber == 1 and file_path.exists() and not overwrite:
                return {"code": "1", "message": "File already exists and overwrite is false"}

            mode = 'wb' if chunkNumber == 1 else 'ab'
            with open(file_path, mode) as f:
                f.write(base64.b64decode(content))

            if chunkNumber == -1:
                return {"code": "0", "message": "Upload successful"}

        except Exception as e:
            logging.error(f"Error in uploadModel: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.delete("/model/{modelName}", dependencies=[Depends(api.auth)])
    async def deleteModel(modelName: str, modelType: str = "Stable-diffusion"):
        model_dir = Path(os.getcwd()) / 'models' / modelType
        file_path = model_dir / modelName

        try:
            if file_path.exists():
                file_path.unlink()
                return {"code": "0", "message": "File deleted"}
            else:
                return {"code": "1", "message": "File not found"}
        except Exception as e:
            logging.error(f"Error in deleteModel: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    app.include_router(router)

try:
    import modules.script_callbacks as script_callbacks
    script_callbacks.on_app_started(create_api)
except ImportError:
    pass
