from pathlib import Path
import hashlib,json,tarfile,tempfile,sys
HERE=Path(__file__).resolve().parent
M=json.loads((HERE/'BUNDLE_MANIFEST.json').read_text())
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
for rel,meta in M['files'].items():
 p=HERE/rel
 assert p.exists(), rel
 assert sha(p)==meta['sha256'], rel
with tempfile.TemporaryDirectory() as td:
 with tarfile.open(HERE/'base/VENUS_RB1_CANONICAL_REBIRTH_RELEASE_2026-09-24.tar.gz','r:gz') as tf: tf.extractall(td)
 roots=list(Path(td).rglob('runtime')); assert roots, 'runtime missing'
 root=roots[0]; sys.path.insert(0,str(root))
 from venus_seed_v0.kernel_r196 import CanonicalTransformationKernelR196
 j=HERE/'current/VENUS_IG10_MODEL_SPECIFIC_F_SUCCESSOR.jsonl'
 k=CanonicalTransformationKernelR196.boot(root,successor_journal=j)
 assert len(k.vm.journal.events)==1308
 assert k.vm.journal.head==M['current']['head']
 assert sha(j)==M['current']['journal_sha256']
 st=k.vmk2.state['ig10:model-specific-F'].value
 assert st['candidate_family']['status']=='PHYSICALLY_GROUNDED_BOUNDED_WITNESS'
 assert st['candidate_family']['tests'][0]['id']=='T_Var4'
 assert st['candidate_family']['complete']=='NOT_ESTABLISHED'
 assert st['candidate_family']['separating_full_state_space']=='NOT_ESTABLISHED'
 assert st['routing']['scheduler']=='WITHHOLD_TEST_FAMILY_COMPLETENESS_AND_SEMICLASSICAL_VALIDATION'
 assert st['routing']['ready_queue']==[]
 assert k.vmk2.state['ig10:model-specific-F'].root==M['current']['state_root']
print('PASS_IG10_CURRENT_DEVELOPED_VM')
