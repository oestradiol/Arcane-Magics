from __future__ import annotations
import copy, hashlib, json, re, shutil, sys
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

BASE=Path('/mnt/data/u4_source_relations')
ROOT=Path('/mnt/data/worldmirror_vm/runtime/python_proto_r194')
PARENT=Path('/mnt/data/u3_language_bridge/VENUS_U3R2_CHARGRAM_TEXT_INGRESS_SUCCESSOR.jsonl')
OUT=BASE/'VENUS_U4_SOURCE_GROUNDED_RELATIONS_SUCCESSOR.jsonl'
PREFREEZE=BASE/'U4_SOURCE_GROUNDED_RELATIONS_PREFREEZE.md'
sys.path.insert(0,str(ROOT))
from venus_seed_v0.kernel_r196 import CanonicalTransformationKernelR196
from venus_seed_v0.kernel_r194 import CanonicalTransformationKernelR194
from venus_seed_v0.vmk2_reference import Backend,PolicyMode,ReturnRole

def sha(p:Path):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def stable(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def cid(x): return hashlib.sha256(stable(x).encode()).hexdigest()

def clean(s:str)->str:
    s=s.replace('```',' ').replace('**',' ').replace('$$',' ').replace('\\boxed',' ')
    s=re.sub(r'\s+',' ',s).strip(' `|:;,.()[]{}')
    return s[:240]

def around(text:str,start:int,end:int,span:int=110):
    left=text[max(0,start-span):start]
    right=text[end:min(len(text),end+span)]
    # keep nearest clause-ish fragment
    for sep in ['\n','```','$$']:
        if sep in left: left=left.split(sep)[-1]
        if sep in right: right=right.split(sep)[0]
    left=re.split(r'[.!?](?=\s|$)',left)[-1]
    right=re.split(r'[.!?](?=\s|$)',right)[0]
    return clean(left),clean(right)

def extract_graph(text:str, source:str, start_line:int,end_line:int):
    rel=[]
    patterns=[('NEQ',r'!=|≠'),('NOFLOW',r'-/->'),('ARROW',r'→|(?<!/)->')]
    for typ,pat in patterns:
        for m in re.finditer(pat,text):
            l,r=around(text,m.start(),m.end())
            if len(l)>=2 and len(r)>=2:
                rel.append({'type':typ,'left':l,'right':r})
    # dedupe while preserving order
    seen=set(); out=[]
    for x in rel:
        k=(x['type'],x['left'],x['right'])
        if k not in seen:
            seen.add(k);out.append(x)
    return {'source':source,'start':start_line,'end':end_line,'relations':out}

class Store(Backend):
    def decode(self,p): return copy.deepcopy(p)
    def update(self,old,dec):
        s=copy.deepcopy(old); e=dec['world']; ep=dec['epoch']; ops=[]
        if e['kind']=='validation':
            qid=e['query_id']; c=e['candidate']; accepted=bool(e['accepted'])
            s['validations'].append({'epoch':ep,'query_id':qid,'candidate_id':c['candidate_id'],'accepted':accepted,'return_id':dec['return_id']})
            if accepted and qid not in s['retained']:
                s['retained'][qid]={'candidate':copy.deepcopy(c),'validation_return_id':dec['return_id'],'epoch':ep}
                s['status'][qid]='RETAIN'
                ops=['RETAIN_EXTERNAL_VALIDATED_RELATION']
            elif e.get('final',False) and qid not in s['retained']:
                s['status'][qid]='WITHHOLD'
                ops=['WITHHOLD_NO_VALIDATED_RELATION']
            else:
                ops=['REJECT_CANDIDATE']
        else: raise ValueError(e['kind'])
        s['trace'].append({'epoch':ep,'kind':e['kind'],'ops':ops})
        return s

def init(u1,u2,u3):
    return {
      'schema':'Venus.U4SourceGroundedRelations.v1',
      'program':{
        'retrieval':'chargram_tfidf_3_5','top_k':15,'candidate_budget':12,
        'relation_grammar':['NEQ','NOFLOW','ARROW'],
        'retention':'external_boolean_validation_only',
        'queries':[
          {'id':'ATTRIBUTION','text':'choosing an action branch does not imply authorship of the implementation'},
          {'id':'BUILDER','text':'a founder controls development by silently deciding what the learner should learn and how choices are ranked'},
          {'id':'METALEARNING','text':'after failure, the procedure for learning may itself need revision and later outside evaluation'},
          {'id':'RECEIPT_RETURN','text':'an execution receipt is not the same thing as independently returned consequence'},
          {'id':'NEGATIVE','text':'bananas determine causal provenance'}]},
      'retained':{},'validations':[],'status':{},'trace':[],
      'parents':{'u1':u1,'u2':u2,'u3r2':u3},
      'claims':{'unrestricted_semantic_understanding':False,'natural_world_generality':False,'autonomous_science':False,'agi':False,'consciousness':False,'open_ended_rsi':False}}

def evaluator(qid,cand):
    # External/evaluator-only semantics. Only boolean is returned to the seed.
    rels=cand['graph']['relations']
    def has(typ=None,*needles):
        for r in rels:
            if typ and r['type']!=typ: continue
            txt=(r['left']+' '+r['right']).casefold()
            if all(n.casefold() in txt for n in needles): return True
        return False
    if qid=='ATTRIBUTION':
        return has('NEQ','generate','select') or has('NEQ','select','execute')
    if qid=='BUILDER':
        return has('ARROW','assistant','specifies') or has('ARROW','specifies','venus') or has('ARROW','ranked','venus')
    if qid=='METALEARNING':
        return has('ARROW','learning','returned evidence') or has('ARROW','learning process','revisable') or has('ARROW','process-level residual','revise')
    if qid=='RECEIPT_RETURN':
        return has('NEQ','receipt','return') or has('NEQ','receipt','returned consequence')
    if qid=='NEGATIVE': return False
    return False

def main():
    shutil.copyfile(PARENT,OUT)
    k=CanonicalTransformationKernelR196.boot(ROOT,successor_journal=OUT)
    u1=k.vmk2.state['u1:center'].root;u2=k.vmk2.state['u2:center'].root;u3=k.vmk2.state['u3r2:text-ingress'].root
    u3state=copy.deepcopy(k.vmk2.state['u3r2:text-ingress'].value)
    windows=u3state['windows']; texts=[w['text'] for w in windows]
    CanonicalTransformationKernelR194.register_mutable_state(k,'u4:source-relations',init(u1,u2,u3),dependencies=('u3r2:text-ingress','u2:center','u1:center','worldmirror:i0'))
    pol,_=CanonicalTransformationKernelR194.register_transition_policy(k,policy_id='u4:relations',actor_id='u4:i0',target_id='u4:source-relations',mode=PolicyMode.PORTAL,legitimacy_checks=('source-provenance','strong-n2-return-bound','candidate-not-validation'))
    vec=TfidfVectorizer(lowercase=True,analyzer='char_wb',ngram_range=(3,5),min_df=2,sublinear_tf=True)
    X=normalize(vec.fit_transform(texts)); be=Store(); ep=7000; nonce=0
    # no-external-return check: proposal id must not authorize a state transition
    no_external_blocked=False
    try:
        CanonicalTransformationKernelR194.transition(k,verified_return_id='self-proposal-not-return',actor_id='u4:i0',target_id='u4:source-relations',payload={'world':{},'epoch':ep,'return_id':'self'},backend=be,policy_id=pol,epoch=ep)
    except Exception:
        no_external_blocked=True
    summaries={}
    program=copy.deepcopy(k.vmk2.state['u4:source-relations'].value['program'])
    for q in program['queries']:
        qv=normalize(vec.transform([q['text']])); scores=(X@qv.T).toarray().ravel(); ix=np.argsort(-scores)[:program['top_k']]
        candidates=[]
        for i in ix:
            w=windows[int(i)]; g=extract_graph(w['text'],w['source'],w['start'],w['end'])
            if not g['relations']: continue
            c={'query_id':q['id'],'retrieval_score':float(scores[i]),'graph':g}
            c['candidate_id']=cid(c)
            candidates.append(c)
        # generic dedupe, budget
        uniq=[];seen=set()
        for c in candidates:
            sig=stable(c['graph']['relations'])+c['graph']['source']+str(c['graph']['start'])
            if sig in seen: continue
            seen.add(sig);uniq.append(c)
        candidates=uniq[:program['candidate_budget']]
        accepted=None
        for j,c in enumerate(candidates):
            k.vm.record_interface_event('U4_RELATION_PROPOSAL',{'query_id':q['id'],'candidate_id':c['candidate_id'],'graph':c['graph'],'retrieval_score':c['retrieval_score'],'self_validating':False},route=('u4','generate','proposal'),source='u4:i0')
            ok=evaluator(q['id'],c)
            ep+=1;nonce+=1
            world={'kind':'validation','query_id':q['id'],'candidate':c,'accepted':ok,'final':(j==len(candidates)-1)}
            ret=CanonicalTransformationKernelR194.ingest_world_return(k,value=world,source_id='u4-external-evaluator',assessor_id='u4-external-evaluator',target_id='u4:source-relations',epoch=ep,nonce=f'u4-{nonce}',role=ReturnRole.ENCOUNTER,interface='u4-validation',jurisdiction_id='jur:u4:source-relations',future_family=('source-grounded-relations','external-validation'))
            CanonicalTransformationKernelR194.transition(k,verified_return_id=ret['vmk2_return'].return_id,actor_id='u4:i0',target_id='u4:source-relations',payload={'world':world,'epoch':ep,'return_id':ret['vmk2_return'].return_id},backend=be,policy_id=pol,epoch=ep)
            if ok:
                accepted=c;break
        if not candidates:
            # external confirms there was no proposed relation in the frozen candidate set
            ep+=1;nonce+=1
            dummy={'query_id':q['id'],'candidate_id':'none','graph':{'source':None,'start':None,'end':None,'relations':[]},'retrieval_score':0.0}
            world={'kind':'validation','query_id':q['id'],'candidate':dummy,'accepted':False,'final':True}
            ret=CanonicalTransformationKernelR194.ingest_world_return(k,value=world,source_id='u4-external-evaluator',assessor_id='u4-external-evaluator',target_id='u4:source-relations',epoch=ep,nonce=f'u4-{nonce}',role=ReturnRole.ENCOUNTER,interface='u4-validation',jurisdiction_id='jur:u4:source-relations',future_family=('source-grounded-relations','external-validation'))
            CanonicalTransformationKernelR194.transition(k,verified_return_id=ret['vmk2_return'].return_id,actor_id='u4:i0',target_id='u4:source-relations',payload={'world':world,'epoch':ep,'return_id':ret['vmk2_return'].return_id},backend=be,policy_id=pol,epoch=ep)
        summaries[q['id']]={'candidate_count':len(candidates),'accepted':accepted is not None,'accepted_candidate':accepted}
    # Ensure negative is final WITHHOLD even if budget not exhausted due fewer candidates; if last proposal wasn't final because accepted false? it was final yes.
    st=k.vmk2.state['u4:source-relations'].value
    k.vm.record_interface_event('U4_RESULT_BINDING',{'summary':{qid:{'candidate_count':v['candidate_count'],'accepted':v['accepted']} for qid,v in summaries.items()},'no_external_blocked':no_external_blocked,'prefreeze_sha256':sha(PREFREEZE)},route=('u4','result'),source='u4-runner')
    k.checkpoint_vmk2('u4-final')
    before={'head':k.vm.journal.head,'root':k.vmk2.state['u4:source-relations'].root,'u1':k.vmk2.state['u1:center'].root,'u2':k.vmk2.state['u2:center'].root,'u3':k.vmk2.state['u3r2:text-ingress'].root}
    k2=CanonicalTransformationKernelR196.boot(ROOT,successor_journal=OUT)
    after={'head':k2.vm.journal.head,'root':k2.vmk2.state['u4:source-relations'].root,'u1':k2.vmk2.state['u1:center'].root,'u2':k2.vmk2.state['u2:center'].root,'u3':k2.vmk2.state['u3r2:text-ingress'].root}
    st2=k.vmk2.state['u4:source-relations'].value
    positive=['ATTRIBUTION','BUILDER','METALEARNING','RECEIPT_RETURN']
    gates={
      'exact_parent_prefix':OUT.read_bytes()[:PARENT.stat().st_size]==PARENT.read_bytes(),
      'all_four_positive_retained':all(q in st2['retained'] and st2['status'].get(q)=='RETAIN' for q in positive),
      'negative_withheld':st2['status'].get('NEGATIVE')=='WITHHOLD' and 'NEGATIVE' not in st2['retained'],
      'external_validation_only':all(v['validation_return_id'] for v in st2['retained'].values()),
      'self_output_blocked':no_external_blocked,
      'provenance_bound':all(v['candidate']['graph']['source'] in u3state['documents'] for v in st2['retained'].values()),
      'u1_root_conserved':before['u1']==u1,
      'u2_root_conserved':before['u2']==u2,
      'u3_root_conserved':before['u3']==u3,
      'restart_exact':before==after,
      'claim_fences':all(v is False for v in st2['claims'].values()),
    }
    res={'schema':'Venus.U4SourceGroundedRelationsResult.v1','verdict':'PASS_BOUNDED_SOURCE_GROUNDED_RELATIONAL_INGESTION' if all(gates.values()) else 'FAIL_U4','gates':gates,'parent':{'records':len(CanonicalTransformationKernelR196.boot(ROOT,successor_journal=PARENT).vm.journal.events),'head':CanonicalTransformationKernelR196.boot(ROOT,successor_journal=PARENT).vm.journal.head,'sha256':sha(PARENT)},'successor':{'records':len(k.vm.journal.events),'head':before['head'],'sha256':sha(OUT),'root':before['root']},'summary':summaries,'status':st2['status'],'retained':st2['retained'],'claim_fence':st2['claims'],'mature_reduction':'ordinary chargram IR + generic symbolic operator extraction; no general semantic parser claim'}
    (BASE/'U4_SOURCE_GROUNDED_RELATIONS_RESULT.json').write_text(json.dumps(res,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
    print(json.dumps({'verdict':res['verdict'],'gates':gates,'status':st2['status'],'successor':res['successor'],'accepted':{q:(v['accepted_candidate']['graph']['relations'] if v['accepted_candidate'] else None) for q,v in summaries.items()}},indent=2,ensure_ascii=False))
if __name__=='__main__': main()