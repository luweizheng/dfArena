#!/usr/bin/env python3
import argparse,json,re,subprocess,time
from pathlib import Path
BACKENDS={"pandas":"Use pandas as the main dataframe backend for loading, transformation, and computation.","polars":"Use Polars as the main dataframe backend for loading, transformation, and computation. Do not use pandas for the main workflow. Pandas may be used only for an explicit final interoperability boundary when required.","ibis":"Use Ibis with DuckDB as the main dataframe backend for loading, filtering, joins, aggregation, sorting, and date handling. Keep relational computation lazy until final materialization where practical. Do not use pandas for the main workflow. A small final boundary conversion is allowed only when required for answer serialization."}
def main():
 p=argparse.ArgumentParser(); p.add_argument('--dataset',type=Path,required=True); p.add_argument('--task',required=True); p.add_argument('--agent-model',default='codex_gpt-6'); p.add_argument('--backend',choices=BACKENDS,default='pandas'); p.add_argument('--image',default='dfarena-agent-sandbox:latest'); p.add_argument('--model'); p.add_argument('--codex-config-dir',default='~/.codex'); p.add_argument('--run-dir',type=Path,required=True); p.add_argument('--timeout',type=int,default=600); a=p.parse_args()
 ds=a.dataset.resolve(); task=json.loads((ds/'tasks'/a.task/'task.json').read_text()); sol=a.run_dir/'solution'; detail=a.run_dir/'detail'; work=a.run_dir/'work'; sol.mkdir(parents=True,exist_ok=True); detail.mkdir(parents=True,exist_ok=True); work.mkdir(exist_ok=True)
 prompt=f'''Solve this DataAgentBench task. Read only /workspace/data, /workspace/context, and /workspace/task.json. Put code and intermediate files under /workspace/work. Do not modify /workspace/data. Do not read hidden answers, validators, reference solutions, or other runs. Use this backend: {BACKENDS[a.backend]} Generate /workspace/work/solution.py, execute it, repair failures, and write /workspace/work/answer.json with exactly {{"answer": "<concise final answer>"}}. Do not hard-code the answer.\n\nContext: {task.get("context","")}\nQuestion: {task.get("query","")}'''
 cmd=['docker','run','--rm','-e','HOME=/root','-v',f'{(ds/"data").resolve()}:/workspace/data:ro','-v',f'{(ds/"context").resolve()}:/workspace/context:ro','-v',f'{(ds/"tasks"/a.task/"task.json").resolve()}:/workspace/task.json:ro','-v',f'{work.resolve()}:/workspace/work:rw','-v',f'{Path(a.codex_config_dir).expanduser().resolve()}:/root/.codex:rw','-w','/workspace',a.image,'codex','exec','--json','--dangerously-bypass-approvals-and-sandbox','--skip-git-repo-check','--cd','/workspace/work',prompt]
 if a.model: cmd.insert(-1,a.model)
 t=time.perf_counter(); out=[]; proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,text=True,bufsize=1)
 with (detail/'codex_stdout.jsonl').open('w') as f:
  for line in proc.stdout: f.write(line); f.flush(); out.append(line)
 rc=proc.wait(); elapsed=time.perf_counter()-t
 if (work/'solution.py').exists(): (sol/'solution.py').write_bytes((work/'solution.py').read_bytes())
 if (work/'answer.json').exists(): (sol/'answer.json').write_bytes((work/'answer.json').read_bytes())
 usage=None
 for l in reversed(out):
  try:
   x=json.loads(l)
   if x.get('type')=='turn.completed': usage=x.get('usage'); break
  except: pass
 result={'status':'success' if rc==0 and (sol/'solution.py').exists() and (sol/'answer.json').exists() else 'failure','returncode':rc,'elapsed_seconds':elapsed,'token_usage':usage}; (detail/'result.json').write_text(json.dumps(result,indent=2))
 return 0 if result['status']=='success' else 1
if __name__=='__main__': raise SystemExit(main())
