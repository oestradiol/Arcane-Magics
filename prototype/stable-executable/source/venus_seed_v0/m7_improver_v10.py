from __future__ import annotations
import hashlib,random
import numpy as np
K=9;MIN_TRAIN=40

def fit_policy(rows):
 src={r.get('source_world_id') for r in rows}
 if len(rows)<MIN_TRAIN:return {'decision':'WITHHOLD','reason':'RESOURCE_BOUND','state':None,'source_world_id':next(iter(src)) if len(src)==1 else None}
 if len(src)!=1:return {'decision':'WITHHOLD','reason':'PROVENANCE_MIXED','state':None,'source_world_id':None}
 X=np.stack([np.asarray(r['x'],float) for r in rows]);y=np.array([r['gain'] for r in rows],float);mu=X.mean(0);sd=X.std(0);sd=np.where(sd<1e-8,1.,sd)
 return {'decision':'PROPOSE','reason':None,'state':{'X':(X-mu)/sd,'y':y,'mu':mu,'sd':sd},'source_world_id':next(iter(src))}
def i0(x):
 x=np.asarray(x,float);return float(.85*x[0]+.20*x[1]-.10*x[2])
def knn_score(s,x):
 z=(np.asarray(x,float)-s['mu'])/s['sd'];d=np.sum((s['X']-z)**2,axis=1);k=min(K,len(d));idx=np.argpartition(d,k-1)[:k];ww=1/(d[idx]+.10);return float(np.sum(ww*s['y'][idx])/np.sum(ww))
def choose_public(pool,state=None):
 assert all('gain' not in c for c in pool);scores=[i0(c['x']) if state is None else knn_score(state,c['x']) for c in pool];j=max(range(len(pool)),key=lambda q:scores[q]);return 0 if scores[j]<=0 else j
def evaluate_returned(P,T,state=None):
 gs=[];ids=[];ors=[]
 for p,t in zip(P,T):
  j=choose_public(p,state);cid=p[j]['id'];ids.append(cid);gs.append(t[cid]);ors.append(max(t.values()))
 a=np.array(gs);o=np.array(ors)
 return {'mean_gain':float(a.mean()),'positive_fraction':float((a>0).mean()),'destructive_fraction':float((a<0).mean()),'mean_regret':float((o-a).mean()),'selection_ids':ids,'oracle_mean_gain':float(o.mean())}
def govern(prop,P,T,target_world_id):
 if prop.get('source_world_id')!=target_world_id:return {'decision':'WITHHOLD','reason':'PROVENANCE_MISMATCH','state':None,'validation':None}
 if prop['decision']!='PROPOSE':return {'decision':'WITHHOLD','reason':prop['reason'],'state':None,'validation':None}
 b=evaluate_returned(P,T,None);n=evaluate_returned(P,T,prop['state']);d=n['mean_gain']-b['mean_gain'];safe=n['destructive_fraction']<=min(.08,b['destructive_fraction']+.02);use=d>=.15 and n['positive_fraction']>=b['positive_fraction'] and n['mean_regret']<b['mean_regret']
 return {'decision':'RETAIN' if safe and use else 'WITHHOLD','reason':None if safe and use else 'VALIDATION_FAIL','state':prop['state'] if safe and use else None,'validation_gain':d if safe and use else d}
def shuffled(rows,world_id):
 ys=[r['gain'] for r in rows];h=hashlib.sha256(f'M7-v10-shuffle|{world_id}'.encode()).digest();rr=random.Random(int.from_bytes(h[:8],'big'));rr.shuffle(ys);return [{**r,'gain':y} for r,y in zip(rows,ys)]
def commit_ids(pools,state=None):
 return [p[choose_public(p,state)]['id'] for p in pools]
