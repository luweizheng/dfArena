#!/usr/bin/env python3
import argparse,json,subprocess,time
from pathlib import Path
def main():
 p=argparse.ArgumentParser(); p.add_argument('--dataset',type=Path,required=True); p.add_argument('--task',required=True); p.add_argument('--run-dir',type=Path,required=True); p.add_argument('--image',default='dfarena-agent-sandbox:latest'); a=p.parse_args(); ds=a.dataset.resolve(); task=ds/'tasks'/a.task; out=a.run_dir/'evaluation.json'; t=time.perf_counter()
 cmd=['docker','run','--rm','-v',f'{(ds/"data").resolve()}:/workspace/data:ro','-v',f'{(ds/"context").resolve()}:/workspace/context:ro','-v',f'{(a.run_dir/"solution").resolve()}:/workspace/solution:rw','-v',f'{(task/"answer").resolve()}:/workspace/answer:ro','-w','/workspace/solution',a.image,'python','-c','import json,sys;sys.path.insert(0,"/workspace/answer");import validate; ans=json.load(open("/workspace/solution/answer.json"))["answer"]; ok,msg=validate.validate(ans); print(json.dumps({"passed":bool(ok),"message":str(msg),"answer":ans}))']
 cp=subprocess.run(cmd,text=True,capture_output=True); payload={'passed':False,'message':cp.stderr or cp.stdout,'elapsed_seconds':time.perf_counter()-t}
 for l in reversed(cp.stdout.splitlines()):
  try: payload.update(json.loads(l)); break
  except: pass
 out.write_text(json.dumps(payload,indent=2)); return 0 if payload.get('passed') else 1
if __name__=='__main__': raise SystemExit(main())
