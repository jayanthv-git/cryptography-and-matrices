"""Local, stateless API. Uploaded survey contents are never written to disk."""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from starlette.exceptions import HTTPException
from backend.api.models import (
    CipherRequest, CipherResponse, KeyRequest, KeyReport, RecoveryRequest,
    RecoveryResponse, ExperimentRequest, ExperimentResponse, SurveyRequest,
    SurveyResponse, ErrorResponse,
)
from backend.core.hill_cipher import CipherError, validate_key
from backend.core.matrix_operations import MatrixError
from backend.core.explanation_engine import explain_cipher
from backend.core.cryptanalysis import recover_key
from backend.core.experiments import run_experiments
from backend.core.survey import analyze_survey, SCHEMA


def error_response(code, message, status=422, details=None):
    return JSONResponse(status_code=status, content={"error": {"code": code, "message": message, "details": details or []}})


class BodyLimit:
    """Bound requests before JSON parsing, including chunked bodies."""
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        chunks, size = [], 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            size += len(message.get("body", b""))
            if size > 1_100_000:
                return await error_response("body_too_large", "Request exceeds 1.1 MB. CSV files must be no larger than 1 MiB.", 413)(scope, receive, send)
            chunks.append(message)
            if not message.get("more_body", False):
                break
        async def replay():
            return chunks.pop(0) if chunks else await receive()
        await self.app(scope, replay, send)


app = FastAPI(title="MatrixCrypt Lab", version="1.0.0", responses={422: {"model": ErrorResponse}, 413: {"model": ErrorResponse}})
app.add_middleware(BodyLimit)

@app.exception_handler(RequestValidationError)
async def request_error(request: Request, exc: RequestValidationError):
    details = [{"field": ".".join(str(p) for p in e["loc"] if p != "body"), "message": e["msg"]} for e in exc.errors()]
    return error_response("validation_error", "Check the highlighted input constraints.", details=details)

@app.exception_handler(CipherError)
@app.exception_handler(MatrixError)
async def calculation_error(request: Request, exc: ValueError):
    return error_response(getattr(exc, "code", "calculation_error"), str(exc))

@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    return error_response("http_error", str(exc.detail), exc.status_code)

@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.post("/api/key/validate", response_model=KeyReport)
def key_validate(body: KeyRequest):
    return validate_key(body.key)

@app.post("/api/cipher", response_model=CipherResponse, response_model_exclude_none=True)
def cipher(body: CipherRequest):
    return explain_cipher(**body.model_dump())

@app.post("/api/recover", response_model=RecoveryResponse)
def recovery(body: RecoveryRequest):
    return recover_key([pair.model_dump() for pair in body.pairs])

@app.post("/api/experiments", response_model=ExperimentResponse)
def experiments(body: ExperimentRequest):
    return run_experiments(**body.model_dump())

@app.post("/api/survey", response_model=SurveyResponse)
def survey(body: SurveyRequest):
    return analyze_survey(body.csv)

@app.get("/api/survey/template", response_class=Response)
def template():
    return Response(",".join(SCHEMA) + "\n", media_type="text/csv", headers={"Content-Disposition": 'attachment; filename="matrixcrypt-survey-template.csv"'})
