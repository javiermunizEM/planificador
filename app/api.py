import os
import shutil
import tempfile
import logging
from threading import Lock

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response

from app.runner import run_pipeline_in_workspace

logger = logging.getLogger("uvicorn.error")

app = FastAPI()
PIPELINE_LOCK = Lock()


def require_api_key(request: Request) -> None:
    x_api_key = (
        request.headers.get("x-api-key")
        or request.headers.get("X-API-KEY")
        or request.headers.get("X-Api-Key")
    )

    expected = os.environ.get("API_KEY")

    # Log (no revela secretos)
    logger.info("API_KEY present=%s len=%s", bool(expected), (len(expected) if expected else 0))
    logger.info("Header X-API-KEY present=%s len=%s", bool(x_api_key), (len(x_api_key) if x_api_key else 0))

    if not expected:
        raise RuntimeError("API_KEY no configurada en variables de entorno")
    if not x_api_key or x_api_key != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/v1/debug-auth")
def debug_auth(request: Request):
    x_api_key = (
        request.headers.get("x-api-key")
        or request.headers.get("X-API-KEY")
        or request.headers.get("X-Api-Key")
    )
    expected = os.environ.get("API_KEY")
    return {
        "has_env_api_key": bool(expected),
        "env_api_key_len": len(expected) if expected else 0,
        "has_header_api_key": bool(x_api_key),
        "header_api_key_len": len(x_api_key) if x_api_key else 0,
    }


@app.post("/v1/generate-pdf")
def generate_pdf(payload: dict, request: Request):
    require_api_key(request)

    workspace = tempfile.mkdtemp(prefix="em_pdf_")
    try:
        with PIPELINE_LOCK:
            pdf_path = run_pipeline_in_workspace(payload, workspace)

        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="planificador.pdf"'}
        )

    finally:
        shutil.rmtree(workspace, ignore_errors=True)
