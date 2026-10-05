import json, logging, os, secrets, threading, time
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from simulator import LocalUserSimulatorAPI
from simulator.user_simulator import _load_dotenv
_load_dotenv()
repo = Path(os.environ['DFARENA_DAB_ROOT']).resolve()
app = FastAPI(title='dfArena DataAgentBench Simulator', docs_url=None, redoc_url=None)
logger = logging.getLogger('uvicorn.error')
api = LocalUserSimulatorAPI(data_root=repo,
    max_rounds=int(os.environ.get('SIMULATOR_MAX_ROUNDS') or os.environ.get('DFARENA_SIMULATOR_MAX_ROUNDS', '3')),
    max_questions=int(os.environ.get('SIMULATOR_MAX_QUESTIONS') or os.environ.get('DFARENA_SIMULATOR_MAX_QUESTIONS', '25')))
lock = threading.Lock(); admin_token = os.environ['DFARENA_ADMIN_TOKEN']; trace = Path(os.environ['DFARENA_TRACE'])
class Start(BaseModel):
    dataset_id: str
    task_id: str
    run_id: str
class Ask(BaseModel):
    session_id: str
    questions: list[str] = Field(min_length=1)
    round: int | None = None
def _public(reply):
    answers=[{'question':x['sub_question'],'answer':x['answer']} for x in reply.get('answers',[])]
    if not answers and reply.get('done'): answers=[{'answer':'The clarification quota has been reached. Proceed using the answers already provided.'}]
    return {'answers':answers}
@app.get('/health')
def health(): return {'ok': True}
@app.post('/session/start')
def start(req: Start, authorization: str = Header(default='')):
    if not secrets.compare_digest(authorization, 'Bearer '+admin_token): raise HTTPException(403, 'Runner authorization required')
    with lock: return api.start_session(dataset_id=req.dataset_id, task_id=req.task_id, run_id=req.run_id)
@app.post('/session/ask')
def ask(req: Ask):
    started_at=datetime.now(timezone.utc); started=time.perf_counter(); record={'time':started_at.isoformat(),'started_at':started_at.isoformat(),'request':req.model_dump()}
    with lock:
        try: reply=api.ask(session_id=req.session_id, questions=req.questions, round=req.round); record['response']=reply
        except Exception as exc: record['error_type']=type(exc).__name__; raise HTTPException(502, 'Simulator call failed; see server trace') from exc
        finally:
            finished=datetime.now(timezone.utc); record['finished_at']=finished.isoformat(); record['elapsed_seconds']=time.perf_counter()-started; trace.parent.mkdir(parents=True,exist_ok=True)
            with trace.open('a',encoding='utf-8') as f: f.write(json.dumps(record,ensure_ascii=False)+'\\n')
    return _public(reply)
