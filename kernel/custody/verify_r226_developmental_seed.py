from pathlib import Path
import hashlib,json,shutil,sys,tarfile,tempfile
def sha(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1<<20),b''):h.update(c)
 return h.hexdigest()
s=Path(sys.argv[1]);m=json.load(open(s/'SEED_MANIFEST.json'));rec=json.load(open(s/'state/CURRENT_STATE_RECEIPT.json'));bad=[x['path'] for x in m['files'] if not (s/x['path']).is_file() or sha(s/x['path'])!=x['sha256']];checks={'hashes':not bad,'execution_sprints':(s/'constitution_and_routing/EXECUTION_SPRINTS.md').is_file(),'public_private':(s/'private_state/R226_CURRENT_DEVELOPED_SUCCESSOR.jsonl').is_file() and any((s/'public').glob('*.tar.gz'))};
with tempfile.TemporaryDirectory(prefix='r226_seed_') as td:
 td=Path(td);
 with tarfile.open(s/'runtime/R196_DEVELOPED_CARRIER.tar.gz','r:gz') as t:t.extractall(td/'c')
 root=list((td/'c').rglob('kernel_r196.py'))[0].parent.parent;sys.path.insert(0,str(root));from venus_seed_v0.kernel_r196 import CanonicalTransformationKernelR196;from venus_seed_v0.canonical import digest;j=td/'j.jsonl';shutil.copy2(s/'private_state/R226_CURRENT_DEVELOPED_SUCCESSOR.jsonl',j);k=CanonicalTransformationKernelR196.boot(root,successor_journal=j);r=k.vmk2.state['r199:rsm_state'].value;checks.update({'head':k.vm.journal.head==rec['journal_head'],'records':len(k.vm.journal.events)==rec['journal_records'],'vmk2':k.vmk2_digest()==rec['vmk2_digest'],'project':digest(k.vm.project_state)==rec['project_state_digest'],'cycle':r['cycle']==28,'stopped':r['ready_queue']==[] and r['chosen_next'] is None and r['scheduler_state']=='WITHHOLD_NO_DECLARED_READY_TASK','r206':r['candidate_generation']['active_improver']['revision']=='R206','openended_false':r['candidate_generation']['active_improver']['open_ended_rsi'] is False});k2=CanonicalTransformationKernelR196.boot(root,successor_journal=j);checks['second_restart']=k2.vm.journal.head==k.vm.journal.head and k2.vmk2_digest()==k.vmk2_digest()
print(json.dumps({'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'bad':bad},indent=2,sort_keys=True));raise SystemExit(0 if all(checks.values()) else 2)
