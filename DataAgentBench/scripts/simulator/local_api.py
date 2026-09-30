from __future__ import annotations
from dataclasses import dataclass
import math
from pathlib import Path
from typing import Any
from uuid import uuid4
from .user_simulator import UserSimulator

@dataclass
class _TaskView:
    dataset_id: str
    task_id: str
    task_text: str
    description: str
    hints: str

@dataclass
class _Session:
    session_id: str
    run_id: str
    view: _TaskView
    max_rounds: int
    max_questions: int
    max_questions_per_ask: int
    used_rounds: int = 0
    used_questions: int = 0
    done: bool = False

class LocalUserSimulatorAPI:
    def __init__(self, *, data_root: str | Path, max_rounds: int = 3,
                 max_questions: int = 25, max_questions_per_ask: int = 10):
        self.data_root = Path(data_root).resolve()
        self.user_simulator = UserSimulator()
        self.max_rounds = int(max_rounds)
        self.max_questions = int(max_questions)
        self.max_questions_per_ask = int(max_questions_per_ask)
        if min(self.max_rounds, self.max_questions, self.max_questions_per_ask) <= 0:
            raise ValueError('Simulator budgets must be positive')
        self._sessions: dict[str, _Session] = {}

    def _load(self, dataset_id: str, task_id: str) -> _TaskView:
        ds = self.data_root / dataset_id
        task_path = ds / 'tasks' / task_id / 'query.md'
        if not task_path.is_file():
            raise FileNotFoundError(f'Task not found: {task_path}')
        task_text = task_path.read_text(encoding='utf-8')
        def read(name):
            path = ds / name
            if not path.is_file():
                raise FileNotFoundError(f'Context file not found: {path}')
            return path.read_text(encoding='utf-8')
        return _TaskView(dataset_id, task_id, task_text, read('description.md'), read('hints.md'))

    def start_session(self, *, dataset_id: str, task_id: str, run_id: str) -> dict[str, Any]:
        view = self._load(dataset_id, task_id)
        sid = f'sess_{uuid4().hex[:16]}'
        self._sessions[sid] = _Session(sid, run_id, view, self.max_rounds, self.max_questions, self.max_questions_per_ask)
        return {'session_id': sid, 'dataset_id': dataset_id, 'task_id': task_id, 'run_id': run_id,
                'max_rounds': self.max_rounds, 'max_questions': self.max_questions,
                'max_questions_per_ask': self.max_questions_per_ask}

    def ask(self, *, session_id: str, questions: list[str], round: int | None = None) -> dict[str, Any]:
        state = self._sessions.get(session_id)
        if state is None: raise KeyError(f'Unknown session_id: {session_id}')
        idx = state.used_rounds + 1 if round is None else int(round)
        if state.done:
            return {'session_id': session_id, 'dataset_id': state.view.dataset_id, 'task_id': state.view.task_id,
                    'round': idx, 'answers': [], 'done': True, 'next_round': None,
                    'budget': self._budget(state), 'parse_error': None}
        if idx != state.used_rounds + 1: raise ValueError(f'Round mismatch: expected {state.used_rounds + 1}, got {idx}')
        qs = [q.strip() for q in questions if isinstance(q, str) and q.strip()]
        if not qs: raise ValueError('questions must contain at least one non-empty string')
        qs = qs[:self.max_questions_per_ask][:max(state.max_questions-state.used_questions, 0)]
        payload = '\n'.join(f'q{i+1}: {q}' for i, q in enumerate(qs))
        result = self.user_simulator.answer(task_text=state.view.task_text, description=state.view.description,
                                            hints=state.view.hints, question=payload,
                                            expected_sub_questions=qs, runtime_feedback='')
        state.used_rounds += 1; state.used_questions += len(qs)
        state.done = state.used_rounds >= state.max_rounds or state.used_questions >= state.max_questions
        return {'session_id': session_id, 'dataset_id': state.view.dataset_id, 'task_id': state.view.task_id,
                'run_id': state.run_id, 'round': idx,
                'answers': [{'sub_question': a.sub_question, 'classification': a.classification,
                             'source': a.source, 'answer': a.answer, 'ref': a.ref} for a in result.answers],
                'budget': self._budget(state), 'done': state.done,
                'next_round': None if state.done else state.used_rounds + 1,
                'parse_error': result.parse_error}

    @staticmethod
    def _budget(s):
        return {'max_rounds': s.max_rounds, 'used_rounds': s.used_rounds,
                'max_questions': s.max_questions, 'used_questions': s.used_questions,
                'remaining_questions': max(s.max_questions-s.used_questions, 0)}
