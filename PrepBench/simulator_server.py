"""Single-worker HTTP adapter; simulator assets stay outside the agent container."""
import json
import os
import secrets
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

repo = Path(os.environ.get('DFARENA_CASE_ROOT', str(Path(__file__).resolve().parent))).resolve()
from simulator import LocalUserSimulatorAPI

app = FastAPI(title='dfArena PrepBench Simulator', docs_url=None, redoc_url=None)
api = LocalUserSimulatorAPI(data_root=repo)
lock = threading.Lock()
admin_token = os.environ['DFARENA_ADMIN_TOKEN']
trace = Path(os.environ['DFARENA_TRACE'])

class Start(BaseModel):
    case_id: str
    run_id: str

class Ask(BaseModel):
    session_id: str
    questions: list[str] = Field(min_length=1)
    round: int | None = None

@app.get('/health')
def health():
    return {'ok': True}

@app.post('/session/start')
def start(req: Start, authorization: str = Header(default='')):
    if not secrets.compare_digest(authorization, 'Bearer ' + admin_token):
        raise HTTPException(403, 'Runner authorization required')
    with lock:
        return api.start_session(case_id=req.case_id, run_id=req.run_id)

@app.post('/session/ask')
def ask(req: Ask):
    with lock:
        if req.session_id not in api._sessions:
            raise HTTPException(404, 'Unknown session')
        record = {'time': datetime.now(timezone.utc).isoformat(), 'request': req.model_dump()}
        try:
            reply = api.ask(session_id=req.session_id, questions=req.questions, round=req.round)
            record['response'] = reply
        except Exception as exc:
            record['error_type'] = type(exc).__name__
            raise HTTPException(502, 'Simulator call failed; see server trace') from exc
        finally:
            with trace.open('a') as f:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        return reply
