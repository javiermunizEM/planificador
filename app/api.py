import os
import shutil
import tempfile

from threading import Lock
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response

from app.runner import run_pipeline_in_workspace

app = FastAPI()
PIPELINE_LOCK = Lock()

def require_api_key(request: Request) -> None:
    x_api_key = (
        request.headers.get("x-api-key")
        or request.headers.get("X-API-KEY")
        or request.headers.get("X-Api-Key")
    )

    expected = os.environ.get("API_KEY")
    if not expected:
        raise RuntimeError("API_KEY no configurada en variables de entorno")

    if not x_api_key or x_api_key != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.post("/v1/generate-pdf")
def generate_pdf(payload: dict, request: Request):
    require_api_key(request)

    workspace = tempfile.mkdtemp(prefix="em_pdf_")
    try:
        with PIPELINE_LOCK:
            pdf_path = run_pipeline_in_workspace(payload, workspace)

        # 1) LEER el PDF (antes de borrar)
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        # 2) DEVOLVER los bytes
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="planificador.pdf"'}
        )

    finally:
        # 3) BORRAR el workspace (ya no afecta)
        shutil.rmtree(workspace, ignore_errors=True)
