#!/usr/bin/env python3
import argparse,json,subprocess,time
from pathlib import Path
def main():
 p=argparse.ArgumentParser(); p.add_argument('--dataset',type=Path,required=True); p.add_argument('--task',required=True); p.add_argument('--agent-model',default='codex_gpt-6'); p.add_argument('--backend',default='pandas'); p.add_argument('--codex-config-dir',default='~/.codex'); a=p.parse_args(); root=a.dataset/'output'/a.task/a.agent_model/a.backend; root.mkdir(parents=True,exist_ok=True); ids=[int(x.name[1:]) for x in root.glob('r*') if x.name[1:].isdigit()]; run=root/f'r{max(ids,default=0)+1:03d}'; run.mkdir(); t=time.perf_counter(); g=subprocess.run(['python3',str(Path(__file__).with_name('generate.py')),'--dataset',str(a.dataset),'--task',a.task,'--agent-model',a.agent_model,'--backend',a.backend,'--codex-config-dir',a.codex_config_dir,'--run-dir',str(run)]); e=None
 e=None
 if g.returncode==0: e=subprocess.run(['python3',str(Path(__file__).with_name('evaluate.py')),'--dataset',str(a.dataset),'--task',a.task,'--run-dir',str(run)])
 generation=json.loads((run/'detail'/'result.json').read_text()) if (run/'detail'/'result.json').exists() else {}
 evaluation=json.loads((run/'evaluation.json').read_text()) if (run/'evaluation.json').exists() else {'passed':False,'message':'generation failed'}
 usage=generation.get('token_usage') or {}
 usage['total_tokens']=sum(int(usage.get(k,0) or 0) for k in ('input_tokens','output_tokens'))
 result={'passed':bool(evaluation.get('passed',False)),'answer':evaluation.get('answer'),'total_elapsed_seconds':time.perf_counter()-t,'token_usage':usage,'evaluation':evaluation}
 (run/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)); (run/'evaluation.json').unlink(missing_ok=True); print(run); return 0
if __name__=='__main__': raise SystemExit(main())
