from fastapi import FastAPI, Depends, Body, HTTPException, APIRouter
from pathlib import Path
import base64
import os
import gradio as gr
from modules.api.api import Api
from modules.call_queue import queue_lock
import logging
import subprocess
from modules import shared

logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="/myapi")


def create_api(_: gr.Blocks, app: FastAPI):
    api = Api(app, queue_lock)
    deps = None
    if shared.cmd_opts.api_auth:
        deps = [Depends(api.auth)]


    @router.post("/model", dependencies=deps)
    async def uploadModel(
        chunkNumber: int = Body(..., title='chunk number'),
        content: str = Body(..., title='chunk content'),
        filename: str = Body(..., title='filename'),
        modelType: str = Body(..., title='model type'),
        paths: str = Body(..., title='models subdir path'),
        overwrite: bool = Body(False, title='overwrite'),
    ):

        pathsList = paths.split('/')
        if len(pathsList) > 3:
            raise HTTPException(
                status_code=400, detail="Path exceeds the maximum depth of 3")
        if any('..' in p or p.startswith('/') for p in pathsList):
            raise HTTPException(status_code=400, detail="Invalid path")

        if modelType == "lora":
            subDir = "Lora"
        elif modelType == "checkpoint":
            subDir = "Stable-diffusion"
        elif modelType == "vae":
            subDir = "VAE"
        else:
            raise HTTPException(status_code=400, detail="Invalid model type")
        modelDir = Path(os.getcwd(), 'models', subDir, *pathsList)
        modelDir.mkdir(parents=True, exist_ok=True)
        filepath = modelDir / filename

        try:
            if chunkNumber == 1 and filepath.exists() and not overwrite:
                return {"code": "1", "message": "File already exists and overwrite is false"}

            mode = 'wb' if chunkNumber == 1 else 'ab'
            with open(filepath, mode) as f:
                f.write(base64.b64decode(content))

            if chunkNumber == -1:
                return {"code": "0", "message": "Upload successful"}

        except Exception as e:
            logging.error(f"Error in uploadModel: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/modelByUrl", dependencies=deps)
    async def uploadModelByUrl(
        url: str = Body(..., title='model url'),
        filename: str = Body(..., title='filename'),
        modelType: str = Body(..., title='model type'),
        paths: str = Body(..., title='models subdir path'),
        overwrite: bool = Body(False, title='overwrite'),
    ):

        pathsList = paths.split('/')
        if len(pathsList) > 3:
            raise HTTPException(
                status_code=400, detail="Path exceeds the maximum depth of 3")
        if any('..' in p or p.startswith('/') for p in pathsList):
            raise HTTPException(status_code=400, detail="Invalid path")

        if modelType == "lora":
            subDir = "Lora"
        elif modelType == "checkpoint":
            subDir = "Stable-diffusion"
        elif modelType == "vae":
            subDir = "VAE"
        else:
            raise HTTPException(status_code=400, detail="Invalid model type")
        modelDir = Path(os.getcwd(), 'models', subDir, *pathsList)
        modelDir.mkdir(parents=True, exist_ok=True)
        filepath = modelDir / filename

        if not overwrite and filepath.exists():
            return {"code": "1", "message": "File already exists and overwrite is false"}

        try:
            # 使用wget下载文件
            subprocess.run(["wget", "-O", str(filepath), url], check=True)
            return {"code": "0", "message": "Upload successful"}
        except subprocess.CalledProcessError as e:
            logging.error(f"Error downloading file: {e}")
            raise HTTPException(status_code=500, detail=f"Error downloading file: {e}")
        except Exception as e:
            logging.error(f"Error in uploadModel: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.delete("/model/{filename}", dependencies=deps)
    async def deleteModel(filename: str, modelType: str, paths: str):

        pathsList = paths.split('/')
        if len(pathsList) > 3:
            raise HTTPException(
                status_code=400, detail="Path exceeds the maximum depth of 3")
        if any('..' in p or p.startswith('/') for p in pathsList):
            raise HTTPException(status_code=400, detail="Invalid path")

        if modelType == "lora":
            subDir = "Lora"
        elif modelType == "checkpoint":
            subDir = "Stable-diffusion"
        elif modelType == "vae":
            subDir = "VAE"
        else:
            raise HTTPException(status_code=400, detail="Invalid model type")
        file_path = Path(os.getcwd(), 'models', subDir, *pathsList, filename)

        try:
            if file_path.exists():
                file_path.unlink()
                return {"code": "0", "message": "File deleted"}
            else:
                return {"code": "1", "message": "File not found"}
        except Exception as e:
            logging.error(f"Error in deleteModel: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/gpu/info", dependencies=deps)
    async def getGpuInfo():
        try:
            nvidia_smi_output = subprocess.check_output(['nvidia-smi', '--query-gpu=gpu_name,utilization.gpu,memory.used,memory.total', '--format=csv,noheader,nounits'], encoding='utf-8')
            gpu_infos = []
            for line in nvidia_smi_output.strip().split('\n'):
                gpu_name, utilization, memory_used, memory_total = line.split(', ')
                gpu_info = {
                    "type": gpu_name.strip(),
                    "utilization": int(utilization.strip()),
                    "used": int(memory_used.strip()),
                    "total": int(memory_total.strip())
                }
                gpu_infos.append(gpu_info)

            return {"code": "0", "data": gpu_infos, "message": "success"}

        except Exception as e:
            logging.error(f"Error in getGpuInfo: {e}")
            raise HTTPException(status_code=500, detail=str(e))


    app.include_router(router)


try:
    import modules.script_callbacks as script_callbacks
    script_callbacks.on_app_started(create_api)
except ImportError:
    pass
