const $=s=>document.querySelector(s);
let currentSession=null;
let selectedEvent=null;
let status=null;

async function api(path,opts={}) {
  const r=await fetch(path,opts);
  const data=await r.json();
  if(!r.ok) throw new Error(data.error||r.statusText);
  return data;
}

function shortHash(x){return x?x.slice(0,12)+"…":""}
function esc(s){return String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]))}

async function refreshStatus(){
  try{
    status=await api("/api/status");
    $("#connection-dot").classList.add("ok");
    $("#connection-label").textContent="local surface online";
    $("#process-badge").textContent=status.process_bridge_enabled?"process on":"process off";
    $("#run-process").disabled=!status.process_bridge_enabled;
    renderStatus();
  }catch(e){
    $("#connection-label").textContent="offline";
  }
}

function renderStatus(){
  const box=$("#status-inspector");
  const rows=[
    ["process bridge",status?.process_bridge_enabled],
    ["agent backend",status?.agent_backend_bound],
    ["fabricated reply",status?.fabricated_agent_reply],
    ["claim fence",status?.claim_fence]
  ];
  box.innerHTML=rows.map(([k,v])=>'<div class="row"><b>'+esc(k)+'</b><span>'+esc(v)+'</span></div>').join("");
}

async function refreshSessions(){
  const data=await api("/api/sessions");
  const box=$("#sessions");
  box.innerHTML="";
  for(const s of data.sessions){
    const b=document.createElement("button");
    b.className="session"+(s.session_id===currentSession?" active":"");
    b.textContent=s.title||("session "+shortHash(s.session_id));
    b.onclick=()=>selectSession(s.session_id,s.title);
    box.appendChild(b);
  }
}

async function createSession(){
  const data=await api("/api/sessions",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({title:"conversation"})});
  await refreshSessions();
  await selectSession(data.session_id,"conversation");
}

async function selectSession(id,title){
  currentSession=id;
  $("#session-title").textContent=title||"Conversation";
  $("#empty-state").classList.add("hidden");
  $("#messages").classList.remove("hidden");
  $("#composer").classList.remove("hidden");
  $("#agent-note").classList.remove("hidden");
  await refreshSessions();
  await refreshEvents();
}

async function refreshEvents(){
  if(!currentSession)return;
  const data=await api("/api/events?session_id="+encodeURIComponent(currentSession));
  const box=$("#messages");
  box.innerHTML="";
  for(const e of data.events){
    const el=document.createElement("article");
    el.className="message "+(e.actor==="machine"?"machine":"human");
    el.innerHTML='<div class="avatar">'+(e.actor==="machine"?"WM":"YOU")+'</div><div class="bubble">'+
      '<div class="meta">'+esc(e.actor)+" · "+esc(e.kind)+'</div>'+
      '<div class="text">'+esc(e.decoded_text??("[binary "+e.raw_bytes+" bytes]"))+'</div>'+
      '<div class="hash">raw '+esc(shortHash(e.raw_sha256))+' · semantic '+esc(shortHash(e.semantic_digest))+'</div></div>';
    el.onclick=()=>inspectEvent(e);
    box.appendChild(el);
  }
  box.scrollTop=box.scrollHeight;
}

function inspectEvent(e){
  selectedEvent=e;
  const fields=["event_id","session_id","actor","kind","media_type","raw_sha256","raw_bytes","semantic_digest","created_ns","parent_event_id"];
  $("#event-inspector").classList.remove("empty");
  $("#event-inspector").innerHTML=fields.map(k=>'<div class="row"><b>'+esc(k)+'</b><span>'+esc(e[k])+'</span></div>').join("");
}

$("#composer").addEventListener("submit",async e=>{
  e.preventDefault();
  const input=$("#message");
  const text=input.value;
  if(!text.trim()||!currentSession)return;
  input.value="";
  input.style.height="auto";
  try{
    await api("/api/raw",{
      method:"POST",
      headers:{
        "Content-Type":"text/plain; charset=utf-8",
        "X-WorldMirror-Session":currentSession,
        "X-WorldMirror-Actor":"human",
        "X-WorldMirror-Kind":"CHAT_MESSAGE"
      },
      body:new TextEncoder().encode(text)
    });
    await refreshEvents();
  }catch(err){alert(err.message)}
});
$("#message").addEventListener("input",e=>{
  e.target.style.height="auto";
  e.target.style.height=Math.min(180,e.target.scrollHeight)+"px";
});
$("#new-session").onclick=createSession;

document.querySelectorAll(".tabs button").forEach(b=>b.onclick=()=>{
  document.querySelectorAll(".tabs button").forEach(x=>x.classList.toggle("active",x===b));
  document.querySelectorAll(".panel").forEach(x=>x.classList.remove("active"));
  $("#tab-"+b.dataset.tab).classList.add("active");
});

$("#run-process").onclick=async()=>{
  try{
    const argv=JSON.parse($("#argv").value);
    const data=await api("/api/process",{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({argv,cwd:$("#cwd").value,stdin_base64:""})
    });
    $("#process-output").textContent=JSON.stringify(data.receipt,null,2)+"\n\nstdout:\n"+data.stdout_text+"\n\nstderr:\n"+data.stderr_text;
  }catch(e){$("#process-output").textContent=String(e)}
};

(async()=>{
  await refreshStatus();
  await refreshSessions();
})();
