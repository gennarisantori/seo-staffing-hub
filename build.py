# -*- coding: utf-8 -*-
# Rebuilds index.html from _original.html:
#  - JAKALA blue palette
#  - Auth identical to SEO Quotation Hub (email/password, signup, reset,
#    @jakala.com gate, Firestore user profile + role, bootstrap admin)
#  - JAKALA branding + signed-in user display in header
import io, os, re

SRC = 'C:/Users/fgennari/Downloads/seo-staffing-hub/_original.html'
OUT = 'C:/Users/fgennari/Downloads/seo-staffing-hub/index.html'

with io.open(SRC, encoding='utf-8') as f:
    html = f.read()

# ── A0. Replace the seed data (people + projects) with the one generated from the
#     GM Digital Experience / OG People-on-projects workbooks (see seed_js.txt).
SEED = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'seed_js.txt')
if os.path.exists(SEED):
    seed_js = io.open(SEED, encoding='utf-8').read()
    a = html.index('const IM=[')
    b = html.index('const IP=IPR.map(')
    b = html.index(';', b) + 1
    html = html[:a] + seed_js + html[b:]

# ── A. Palette: indigo -> JAKALA blue ──
html = html.replace('--ac: #6366f1', '--ac: #185FA5')
html = html.replace('--a2: #818cf8', '--a2: #4A9FE0')
html = html.replace('--bh: rgba(99,102,241,.3)', '--bh: rgba(24,95,165,.3)')
html = html.replace("'Outfit',system-ui,sans-serif", "'Inter',system-ui,sans-serif")
html = html.replace('background: rgb(79, 70, 229)', 'background:#1256a0')
for a, b in [
    ('rgba(99,102,241,.15)', 'rgba(24,95,165,.18)'),
    ('rgba(99,102,241,.12)', 'rgba(24,95,165,.15)'),
    ('rgba(99,102,241,.08)', 'rgba(24,95,165,.10)'),
    ('rgba(99,102,241,.06)', 'rgba(24,95,165,.08)'),
    ('rgba(99,102,241,.03)', 'rgba(24,95,165,.05)'),
    ('rgba(139,92,246,.06)', 'rgba(24,95,165,.05)'),
]:
    html = html.replace(a, b)

# ── B. Login CSS (mirrors Quotation Hub global.css) ──
login_css = (
    "#LS{background:#ffffff!important}"
    ".login-card{background:#fff;border:1px solid #e5e5e0;border-radius:16px;padding:40px 48px;width:380px;text-align:center;box-shadow:0 2px 16px rgba(0,0,0,.06);animation:fu .6s ease}"
    ".login-jk{font-size:11px;font-weight:800;color:#185FA5;letter-spacing:.08em;margin-bottom:14px;display:block}"
    ".login-logo{font-size:20px;font-weight:700;margin-bottom:8px;color:#1a1a1a}"
    ".login-subtitle{font-size:13px;color:#6e6e6e;margin-bottom:32px}"
    ".login-field{text-align:left;margin-bottom:12px}"
    ".login-field label{display:block;font-size:12px;color:#595959;margin-bottom:4px}"
    ".login-field input{width:100%;padding:9px 12px;border:1px solid #ddd;border-radius:8px;font-size:14px;color:#1a1a1a;background:#fff}"
    ".login-field input:focus{outline:none;border-color:#185fa5}"
    ".login-submit{width:100%;margin-top:6px;padding:10px;border-radius:8px;background:#185FA5;color:#fff;border:none;font-size:14px;font-weight:600;cursor:pointer}"
    ".login-submit:hover{background:#1256a0}"
    ".login-footer{display:flex;justify-content:center;align-items:center;gap:8px;margin-top:14px;font-size:12px}"
    ".login-footer a{color:#185fa5;text-decoration:none;cursor:pointer}"
    ".login-footer a:hover{text-decoration:underline}"
    ".login-footer .dot{color:#767676}"
    ".login-error{background:#fff3f3;border:1px solid #f5c6c6;border-radius:8px;padding:10px 14px;font-size:13px;color:#c0392b;margin-bottom:16px;text-align:left}"
    ".login-info{background:#effbf3;border:1px solid #c6f0d2;border-radius:8px;padding:10px 14px;font-size:13px;color:#1e7a3a;margin-bottom:16px;text-align:left}"
    ".login-hint{font-size:11px;color:#6e6e6e;margin:-4px 0 8px;text-align:left}"
    ".login-note{font-size:11px;color:#767676;margin-top:16px}"
)
html = html.replace('</style>', login_css + '</style>', 1)

# ── C. Firebase Auth + Firestore compat SDKs ──
html = html.replace(
    'firebase-database-compat.js"></script>',
    'firebase-database-compat.js"></script>\n'
    '<script src="https://www.gstatic.com/firebasejs/10.12.0/firebase-auth-compat.js"></script>\n'
    '<script src="https://www.gstatic.com/firebasejs/10.12.0/firebase-firestore-compat.js"></script>',
    1,
)

# ── D. Empty the login container (filled by liRender) ──
ls = html.index('<div id="LS">')
ap = html.index('<div id="AP">')
html = html[:ls] + '<div id="LS"></div>' + html[ap:]

# ── E. Drop the old password constant ──
html = html.replace('const PW="seo-team-2026";', '')

# ── F. Replace doLogin() with full email/password auth ──
auth_js = r"""// === Firebase Auth (identical model to SEO Quotation Hub) ===
const _auth=firebase.auth();
const _fs=firebase.firestore();
const BOOTSTRAP_ADMINS=['federico.gennari@jakala.com'];
let _user=null,_profile=null,_liMode='signin';

function displayNameFromEmail(email){
  const local=(email||'').split('@')[0]||'';
  if(!local)return email||'';
  return local.split(/[._-]+/).filter(Boolean).map(p=>p.charAt(0).toUpperCase()+p.slice(1).toLowerCase()).join(' ');
}
function liFriendly(err){
  const code=err&&err.code||'';
  const map={'auth/invalid-email':'Invalid email address.','auth/invalid-credential':'Incorrect email or password.','auth/user-not-found':'No account found for this email.','auth/wrong-password':'Incorrect password.','auth/email-already-in-use':'An account already exists for this email.','auth/weak-password':'Password too weak (min. 8 characters).','auth/too-many-requests':'Too many attempts. Try again later.','auth/network-request-failed':'Network error. Check your connection.'};
  return map[code]||(err&&err.message)||'Something went wrong. Please try again.';
}
function liSetMode(m){_liMode=m;liRender('','');}
function liRender(err,info){
  const isReset=_liMode==='reset',isSignup=_liMode==='signup';
  const submitLabel=_liMode==='signin'?'Sign in':isSignup?'Create account':'Send reset email';
  const footer=_liMode==='signin'
    ?'<a onclick="liSetMode(\'reset\')">Forgot password?</a><span class="dot">.</span><a onclick="liSetMode(\'signup\')">Create account</a>'
    :'<a onclick="liSetMode(\'signin\')">Back to sign in</a>';
  const pwField=isReset?'':'<div class="login-field"><label>Password'+(isSignup?' (min. 8 chars)':'')+'</label><input id="li-password" type="password" autocomplete="'+(isSignup?'new-password':'current-password')+'"></div>';
  const hint=isSignup?'<p class="login-hint">Your display name will be set from your email address.</p>':'';
  const LS=document.getElementById('LS');
  LS.style.display='flex';
  LS.innerHTML='<div class="login-card">'
    +'<span class="login-jk">JAKALA</span>'
    +'<div class="login-logo">SEO Staffing Hub</div>'
    +'<p class="login-subtitle">SEO &amp; GEO team, internal use only</p>'
    +(err?'<div class="login-error">'+err+'</div>':'')
    +(info?'<div class="login-info">'+info+'</div>':'')
    +'<form id="li-form" autocomplete="on">'
      +'<div class="login-field"><label>Email</label><input id="li-email" type="email" placeholder="name'+(isSignup?'.surname':'')+'@jakala.com" autocomplete="email"></div>'
      +pwField+hint
      +'<button type="submit" class="login-submit">'+submitLabel+'</button>'
    +'</form>'
    +'<div class="login-footer">'+footer+'</div>'
    +'<p class="login-note">Access restricted to @jakala.com accounts.</p>'
  +'</div>';
  document.getElementById('li-form').addEventListener('submit',liSubmit);
}
async function liSubmit(e){
  e.preventDefault();
  const email=((document.getElementById('li-email')||{}).value||'').trim();
  const password=(document.getElementById('li-password')||{}).value||'';
  try{
    if(!email.toLowerCase().endsWith('@jakala.com'))throw new Error('Only @jakala.com addresses are allowed.');
    if(_liMode==='signin'){await _auth.signInWithEmailAndPassword(email,password);}
    else if(_liMode==='signup'){if(password.length<8)throw new Error('Password must be at least 8 characters.');await _auth.createUserWithEmailAndPassword(email,password);}
    else if(_liMode==='reset'){await _auth.sendPasswordResetEmail(email);liRender('','Reset email sent. Check your inbox.');}
  }catch(err){liRender(liFriendly(err),'');}
}
function fbSignOut(){_auth.signOut();}
function isAdmin(){return !!(_profile&&_profile.role==='admin');}

// ── Access management: invite allowlist (config/access) + users (same model as Quotation Hub) ──
async function uGetInvites(){
  try{
    const s=await _fs.collection('config').doc('access').get();
    if(!s.exists)return[];
    const d=s.data();
    if(Array.isArray(d.invites))return d.invites.map(e=>({email:String(e.email).toLowerCase(),role:e.role==='admin'?'admin':'member'}));
    if(Array.isArray(d.emails))return d.emails.map(e=>({email:String(e).toLowerCase(),role:'member'}));
    return[];
  }catch(e){console.error('uGetInvites',e);return[];}
}
async function uSaveInvites(invites){await _fs.collection('config').doc('access').set({invites,updatedAt:firebase.firestore.FieldValue.serverTimestamp()},{merge:true});}
async function uAddInvite(email,role){
  const e=String(email).trim().toLowerCase();
  if(!e.endsWith('@jakala.com'))throw new Error('Solo indirizzi @jakala.com possono essere invitati.');
  const r=role==='admin'?'admin':'member';
  const inv=await uGetInvites();const i=inv.findIndex(x=>x.email===e);
  if(i>=0)inv[i].role=r;else inv.push({email:e,role:r});
  await uSaveInvites(inv);
}
async function uRemoveInvite(email){const e=String(email).trim().toLowerCase();await uSaveInvites((await uGetInvites()).filter(x=>x.email!==e));}
async function uSetInviteRole(email,role){await uAddInvite(email,role);}
async function uListUsers(){
  try{const s=await _fs.collection('users').orderBy('displayName').get();return s.docs.map(d=>Object.assign({uid:d.id},d.data()));}
  catch(e){console.error('uListUsers',e);return[];}
}
async function uSetUserRole(uid,role){await _fs.collection('users').doc(uid).set({role:role==='admin'?'admin':'member',updatedAt:firebase.firestore.FieldValue.serverTimestamp()},{merge:true});}
async function uSetUserActive(uid,active){await _fs.collection('users').doc(uid).set({active:!!active,updatedAt:firebase.firestore.FieldValue.serverTimestamp()},{merge:true});}

_auth.onAuthStateChanged(async function(fu){
  if(!fu){_user=null;_profile=null;document.getElementById('AP').style.display='none';liRender('','');return;}
  if(!fu.email||!fu.email.toLowerCase().endsWith('@jakala.com')){await _auth.signOut();liRender('Only @jakala.com addresses are allowed.','');return;}
  try{
    const ref=_fs.collection('users').doc(fu.uid);
    const snap=await ref.get();
    const isBoot=BOOTSTRAP_ADMINS.indexOf(fu.email.toLowerCase())>=0;
    const autoName=displayNameFromEmail(fu.email);
    const TS=firebase.firestore.FieldValue.serverTimestamp;
    if(!snap.exists){
      // First appearance: gate by the invite allowlist (bootstrap admins always allowed)
      let invitedRole=null;
      if(!isBoot){const inv=await uGetInvites();const f=inv.find(x=>x.email===fu.email.toLowerCase());invitedRole=f?f.role:null;}
      if(!(isBoot||invitedRole!=null)){await _auth.signOut();liRender('Questo indirizzo non risulta invitato. Chiedi a un amministratore di aggiungerti.','');return;}
      const profile={email:fu.email,displayName:autoName,role:isBoot?'admin':(invitedRole||'member'),active:true,createdAt:TS(),updatedAt:TS()};
      await ref.set(profile);_profile=profile;
    }else{
      const data=snap.data();
      if(data.active===false){await _auth.signOut();liRender('Your account has been disabled. Contact an administrator.','');return;}
      const updates={};
      if(isBoot&&data.role!=='admin')updates.role='admin';
      if(!data.displayName||data.displayName===data.email)updates.displayName=autoName;
      if(Object.keys(updates).length){updates.updatedAt=TS();await ref.set(updates,{merge:true});}
      _profile=Object.assign({},data,updates);
    }
  }catch(ex){console.error('Profile load error:',ex);_profile={email:fu.email,displayName:displayNameFromEmail(fu.email),role:'member'};}
  _user=fu;
  document.getElementById('LS').style.display='none';
  document.getElementById('AP').style.display='block';
  document.getElementById('AP').innerHTML='<div style="display:flex;align-items:center;justify-content:center;height:80vh;color:var(--t2);font-size:16px">Caricamento dati...</div>';
  ld(function(){R();});
});
liRender('','');

"""
dl = html.index('function doLogin()')
sh = html.index('// Sort helper')
html = html[:dl] + auth_js + html[sh:]

# ── G. Header: JAKALA branding + signed-in user display ──
uhtml_decl = (
    'var _uHtml=_user?('
    "'<div style=\"display:flex;align-items:center;gap:8px\">'"
    "+'<span style=\"font-size:11px;color:var(--t2)\">'+((_profile&&_profile.displayName)||_user.email)+'</span>'"
    "+'<button class=\"b bo\" onclick=\"fbSignOut()\" style=\"font-size:10px;padding:4px 8px\">Esci</button></div>'"
    "):'';\n"
)
anchor = 'let h=`<div class="hdr"><div><h1>'
hi = html.index(anchor)
h1end = html.index('</h1>', hi)
new_h1 = ('let h=`<div class="hdr"><div><h1 style="display:flex;align-items:center;gap:9px">'
          '<img src="jakala-logo.png" alt="JAKALA" style="height:30px;width:auto;display:block">'
          '<span style="color:#15171c;font-weight:700;font-size:17px;letter-spacing:-.01em">SEO Staffing Hub</span></h1>')
html = html[:hi] + uhtml_decl + new_h1 + html[h1end + len('</h1>'):]

# Insert user chip into header actions
html = html.replace(
    '<div class="ha"><button class="b bo" onclick="rst()">',
    '<div class="ha">${_uHtml}<button class="b bo" onclick="rst()">',
    1,
)

# ── H. LIGHT THEME: convert the dark dashboard to the Quotation Hub look ──

# H1. Raleway web font (same family/weights as the Quotation Hub)
html = html.replace(
    '</head>',
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Raleway:wght@300;400;500;600;700;800&display=swap">'
    '</head>',
    1,
)

# H2. Light design tokens — white background, strong contrast (Quotation Hub feel)
light_root = ('@charset "utf-8";\n:root { '
    '--bg:#ffffff; --sf:#ffffff; --s2:#ffffff; --bd:#d7d6ce; --bh:#185fa5; '
    '--tx:#15171c; --t2:#42454c; --t3:#6b6e76; --ac:#185fa5; --a2:#185fa5; '
    '--gn:#2f6e12; --yl:#8a5a0c; --or:#c2410c; --rd:#b32a1c; '
    "--mn:'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace; "
    "--sn:'Raleway',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; }")
html = re.sub(r'@charset "utf-8";\s*:root\s*\{[^}]*\}', light_root, html, count=1)

# H3. Any leftover indigo (spaced / 0.x alpha variants) -> JAKALA blue
html = re.sub(r'99,\s*102,\s*241', '24, 95, 165', html)
html = re.sub(r'129,\s*140,\s*248', '24, 95, 165', html)
html = re.sub(r'199,\s*210,\s*254', '13, 74, 130', html)

# H4. Translucent WHITE overlays (made for a dark bg) -> translucent BLACK
html = re.sub(r'rgba\(255,\s*255,\s*255,\s*([0-9.]+)\)', r'rgba(0,0,0,\1)', html)

# H5. Header bar: dark gradient -> white (like the Quotation Hub topnav)
html = html.replace(
    'background: linear-gradient(135deg, rgb(15, 23, 42), rgba(30, 27, 75, 0.6));',
    'background:#ffffff;')

# H6. Buttons: hover + outline variant for a light surface
html = html.replace('.b:hover { filter: brightness(1.2); }',
                    '.b:hover { filter: brightness(0.96); }')
html = html.replace('.bo { background: rgba(0,0,0,0.05); color: var(--t2); }',
                    '.bo { background:#fff; border:1px solid #d8d6cd; color:#595959; }')

# H7. Status colour scale -> readable on white
html = html.replace(
    'function sc(p){return p>100?"#dc2626":p>90?"#ef4444":p>75?"#f97316":p>50?"#eab308":"#22c55e"}',
    'function sc(p){return p>100?"#b32a1c":p>90?"#d24b3a":p>75?"#c2410c":p>50?"#a16207":"#2f6e12"}')

# H8. Role / Price-Level colour maps -> darker, readable on white
html = html.replace(
    'const RC={Director:"#dc2626","Senior Expert Lead":"#f87171","Senior Manager":"#818cf8",Manager:"#60a5fa","Expert Lead":"#38bdf8","Associate Manager":"#34d399","Senior Consultant":"#fbbf24","Senior Associate":"#a3e635",Associate:"#a78bfa",Consultant:"#c084fc","Junior Associate":"#f472b6","Junior Consultant":"#fb923c",Analyst:"#94a3b8"};',
    'const RC={Director:"#b32a1c","Senior Expert Lead":"#c0392b","Senior Manager":"#185fa5",Manager:"#1d6fb8","Expert Lead":"#0e7490","Associate Manager":"#2f6e12","Senior Consultant":"#8a5a0c","Senior Associate":"#5a7d0a",Associate:"#6d4ba8",Consultant:"#8a3fb0","Junior Associate":"#a83a6f","Junior Consultant":"#c2410c",Analyst:"#5f6b7a"};')
html = html.replace(
    'const PLC={4:"#f87171",3:"#60a5fa",2:"#34d399",1:"#a78bfa"};',
    'const PLC={4:"#b32a1c",3:"#185fa5",2:"#2f6e12",1:"#6d4ba8"};')

# H9. Final light-theme touch-ups (appended last so they win) — white bg + structure
theme_css = (
    # Header bar: white with a clear divider + shadow
    ".hdr{border-bottom:1px solid #e3e2da;box-shadow:0 1px 3px rgba(0,0,0,.05)}"
    # Dashboard KPI tiles: subtle card so they pop on white
    ".di{background:#fbfbfa;border:1px solid var(--bd);box-shadow:0 1px 2px rgba(0,0,0,.04)}"
    ".dt,.efbr,.rt,.rfl,.rev-bar{background:#e9e8e2}"
    # Tab group container
    ".nt{background:#eef0f3}"
    ".ntb.a{background:#e6f1fb;color:#185fa5}"
    # Main data tables: tinted sticky header + zebra rows for readability
    ".xtbl th{background:#eef0f3;border-bottom:2px solid #cfd4da;color:#42454c}"
    ".xtbl th .flt{background:#eef0f3;border-top-color:#dfe2e6}"
    ".xtbl tbody tr:nth-child(even){background:#f7f8fa}"
    ".xtbl tbody tr:hover{background:#eef4fb}"
    ".xtbl tbody tr.sel{background:#e1ecf8}"
    ".xtbl td{border-bottom:1px solid #ececea}"
    ".sc,.sh{background:#fff}"
    # Side panel / modal / list cards
    ".pn,.md{box-shadow:0 4px 20px rgba(0,0,0,.10)}"
    ".ap{background:#fff;box-shadow:0 1px 2px rgba(0,0,0,.04)}"
    ".ap:hover{border-color:#bcd3ec}"
    ".ap.sel{background:#e8f1fb;border-color:#185fa5}"
    ".mx.off{background:#f2f2ef;border:1px solid #e4e3dd;color:rgba(0,0,0,.25)}"
    ".pr2{background:#f6f6f3}"
    ".tchip{background:#eef0f3;color:#42454c}"
    ".si,.pi,.mxi{background:#fff;border:1px solid var(--bd)}"
    ".si::placeholder{color:#9a9aa0}"
    # Users / access-management view
    ".ucard{background:#fff;border:1px solid var(--bd);border-radius:12px;padding:20px 22px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,.05)}"
    ".uct{font-size:18px;font-weight:700;color:#15171c;margin-bottom:4px}"
    ".ucs{font-size:13px;color:var(--t2);margin-bottom:16px;line-height:1.5;max-width:80ch}"
    ".utbl{width:100%;border-collapse:collapse;font-size:13px}"
    ".utbl th{text-align:left;padding:9px 10px;background:#eef0f3;border-bottom:2px solid #cfd4da;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.4px;color:#42454c;white-space:nowrap}"
    ".utbl td{padding:9px 10px;border-bottom:1px solid #ececea;color:var(--tx);vertical-align:middle}"
    ".utbl tbody tr:nth-child(even){background:#f7f8fa}"
    ".utbl select{padding:5px 8px;border:1px solid var(--bd);border-radius:6px;background:#fff;color:var(--tx);font-size:12px;font-family:inherit}"
    ".utbl .ctr{text-align:center}"
    # Top navigation bar — identical to the Quotation Hub
    ".topnav{display:flex;align-items:center;justify-content:space-between;padding:10px 24px;background:#fff;border-bottom:1px solid #e5e5e0;position:sticky;top:0;z-index:100;flex-wrap:wrap;gap:10px}"
    ".topnav-left{display:flex;align-items:center;gap:16px;flex-wrap:wrap}"
    ".topnav-logo{display:flex;align-items:center;gap:6px;font-size:16px;font-weight:600;color:#1a1a1a;white-space:nowrap}"
    ".brand-mark{height:30px;width:auto;display:block;object-fit:contain}"
    ".topnav-nav{display:flex;gap:4px;flex-wrap:wrap}"
    ".nav-item{padding:6px 14px;border-radius:8px;font-size:13px;color:#595959;text-decoration:none;cursor:pointer;white-space:nowrap;transition:background .15s,color .15s}"
    ".nav-item:hover{background:#f5f4f0;color:#1a1a1a}"
    ".nav-item.active{background:#e6f1fb;color:#185fa5;font-weight:500}"
    ".topnav-right{display:flex;align-items:center;gap:8px}"
    ".avatar{width:28px;height:28px;border-radius:50%;background:#e6f1fb;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:600;color:#185fa5;text-transform:uppercase}"
    ".topnav-user{font-size:13px;color:#595959;white-space:nowrap}"
    ".signout-btn{padding:4px 10px;border-radius:6px;border:1px solid #ddd;background:transparent;font-size:12px;color:#6e6e6e;cursor:pointer}"
    ".signout-btn:hover{background:#f5f4f0;color:#1a1a1a}"
    # Search lives in the top nav (next to the tabs)
    ".topsearch{width:170px;padding:6px 11px;border:1px solid #d7d6ce;border-radius:8px;font-size:13px;color:#1a1a1a;background:#fff;font-family:inherit;outline:none}"
    ".topsearch:focus{border-color:#185fa5}"
    ".topsearch::placeholder{color:#9a9aa0}"
    # Tighten the gap between the top nav and the content
    ".ct{margin-top:6px!important;padding-top:8px!important}"
    # Admin view — enlarged overview metrics + Price-Level capacity
    ".ametrics{display:flex;gap:12px;flex-wrap:wrap}"
    ".ametric{flex:1;min-width:130px;background:#f8f9fb;border:1px solid var(--bd);border-radius:10px;padding:13px 15px}"
    ".aml{font-size:11px;color:var(--t3);font-weight:600;text-transform:uppercase;letter-spacing:.05em;margin-bottom:6px}"
    ".amv{font-size:25px;font-weight:700;color:#15171c;font-variant-numeric:tabular-nums;line-height:1.1}"
    ".acapgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px}"
    ".acap{background:#f8f9fb;border:1px solid var(--bd);border-radius:10px;padding:14px 16px}"
    ".acl{font-size:12px;color:var(--t2);font-weight:700;margin-bottom:8px;text-transform:uppercase;letter-spacing:.04em}"
    ".acv{font-size:21px;font-weight:700;margin-bottom:8px;font-variant-numeric:tabular-nums}"
    ".acv span{font-size:12px;color:var(--t3);font-weight:500}"
    ".acbar{height:6px;background:#e9e8e2;border-radius:3px;overflow:hidden;margin-bottom:6px}"
    ".acbar>div{height:100%;border-radius:3px;transition:width .5s}"
    ".acp{font-size:12px;font-weight:700;text-align:right;font-variant-numeric:tabular-nums}"
    # Admin sub-navigation + analytics tables
    ".admsub{display:flex;gap:4px;flex-wrap:wrap;margin:2px 0 14px;padding-bottom:10px;border-bottom:1px solid #e5e5e0}"
    ".utbl th.r,.utbl td.r{text-align:right}"
    ".utbl td{font-variant-numeric:tabular-nums}"
    ".utbl tr.grp td{background:#eef4fb;font-weight:700;color:#15171c;border-top:1px solid #cfd4da}"
    ".utbl tr.grp td:first-child{color:#185fa5}"
    ".utbl tr.tot td{background:#f2f3f5;font-weight:700;border-top:2px solid #cfd4da}"
    ".ametric .amv{white-space:nowrap}"
    ".admnote{margin-top:12px;padding:9px 12px;background:#f6f8fa;border-left:3px solid #185fa5;border-radius:0 6px 6px 0;font-size:12px;color:var(--t2);line-height:1.5}"
    ".admleg{display:flex;flex-wrap:wrap;gap:8px 18px;margin-top:12px;font-size:11.5px;color:var(--t2);line-height:1.5}"
    ".admleg b{color:#15171c}"
    ".tgtrow{display:flex;gap:10px;flex-wrap:wrap}"
    ".tgtbox{flex:1;min-width:190px;display:flex;flex-direction:column;gap:3px;background:#f8f9fb;border:1px solid var(--bd);border-radius:10px;padding:11px 13px}"
    ".tgtbox>span:first-child{font-weight:700;font-size:12px;color:#15171c}"
    ".tgtin{display:flex;align-items:center;gap:5px;margin-top:4px;font-size:13px;color:var(--t2)}"
    ".tgtin input{width:70px;padding:6px 8px;border:1px solid var(--bd);border-radius:7px;background:#fff;color:var(--tx);font-family:inherit;font-size:14px;font-weight:700;text-align:right}"
    ".tgtin input:focus{outline:none;border-color:#185fa5}"
)
html = html.replace('</style>', theme_css + '</style>', 1)

# ── I. ACCESS MANAGEMENT: "Utenti" tab + invite-based user activation (Quotation Hub model) ──

# I1. Rebuild the header as a Quotation-Hub-style top nav (logo + title + inline tabs + user).
#     The overview stats and Price-Level tiles move out of the header into the Admin tab.
hstart = html.index('var _uHtml=')
hend_marker = '<div class="ct">`;'
hend = html.index(hend_marker, hstart) + len(hend_marker)
new_header = r"""var _nm=_user?((_profile&&_profile.displayName)||_user.email):'';
var _ini=_nm?_nm.split(/[ ._-]+/).filter(Boolean).slice(0,2).map(function(s){return s.charAt(0).toUpperCase();}).join(''):'';
var _uHtml=_user?('<div class="avatar">'+_ini+'</div><span class="topnav-user">'+esc(_nm)+'</span><button class="signout-btn" onclick="fbSignOut()">Esci</button>'):'';
const TABS=[["team","👥 Team"],["projects","📁 Progetti"],["matrix","🔢 Matrice"],["assign","⚡️ Assegna"]];
if(isAdmin())TABS.push(["admin","⚙️ Admin"]);
let h=`<div class="topnav"><div class="topnav-left"><span class="topnav-logo"><img class="brand-mark" src="jakala-logo.png" alt="JAKALA"><span>SEO Staffing Hub</span></span><div class="topnav-nav">${TABS.map(([k,l])=>`<a class="nav-item${S.vw===k?' active':''}" onclick="sw('${k}')">${l}</a>`).join('')}</div>${S.vw!=='admin'?`<input class="topsearch" placeholder="Cerca..." value="${esc(S.q)}" oninput="S.q=this.value;R()">`:''}</div><div class="topnav-right">${_uHtml}</div></div>`;
h+=`<div class="ct">`;"""
html = html[:hstart] + new_header + html[hend:]

# I2. Route the new view (load Firestore data, then render)
assert 'function sw(v){S.vw=v;S.sm=null;S.sp=null;R()}' in html, 'sw() anchor not found'
html = html.replace('function sw(v){S.vw=v;S.sm=null;S.sp=null;R()}',
                    "function sw(v){S.vw=v;S.sm=null;S.sp=null;if(v==='admin'){uLoad();return;}R()}", 1)

# I3. Render the Admin view inside the content area (admins only; nothing for others)
anchor_ap = 'h+=`</div>`;document.getElementById("AP").innerHTML=h;'
assert anchor_ap in html, 'AP render anchor not found'
admin_branch = r"""if(S.vw==='admin'&&isAdmin()){
h+='<div style="flex:1;min-width:0;max-width:1120px;margin:0 auto;width:100%">'+renderAdmin()+'</div>';
}
"""
html = html.replace(anchor_ap, admin_branch + anchor_ap, 1)

# I3b. Move the "+ Persona" / "+ Progetto" add buttons to the left, above the first column
html = html.replace(
    '<div style="display:flex;justify-content:flex-end;margin-bottom:6px;flex-shrink:0"><button class="b bg" onclick="amM()">+ Persona</button></div>',
    '<div style="display:flex;justify-content:flex-start;margin-bottom:8px;flex-shrink:0"><button class="b bg" onclick="amM()">+ Persona</button></div>', 1)
html = html.replace(
    '<div style="display:flex;justify-content:flex-end;margin-bottom:6px;flex-shrink:0"><button class="b ba" onclick="amP()">+ Progetto</button></div>',
    '<div style="display:flex;justify-content:flex-start;margin-bottom:8px;flex-shrink:0"><button class="b ba" onclick="amP()">+ Progetto</button></div>', 1)

# I4. Append the access-management UI + actions before the closing </script>
users_js = r"""
// ===== Access management view (admins invite by email + role; the invited person sets their own password via the shared app link) =====
let _uUsers=null,_uInvites=null,_uLoading=false;
function uLoad(){_uLoading=true;R();Promise.all([uListUsers(),uGetInvites()]).then(function(r){_uUsers=r[0];_uInvites=r[1];_uLoading=false;R();}).catch(function(){_uUsers=[];_uInvites=[];_uLoading=false;R();});}
function uRoleBadge(role){return role==='admin'?'<span class="sb" style="background:rgba(24,95,165,.12);color:#185fa5">Admin</span>':'<span class="sb" style="background:rgba(0,0,0,.06);color:#42454c">Member</span>';}
function renderUsers(){
  var adm=isAdmin();
  if(_uLoading||_uUsers===null||_uInvites===null)return '<div style="flex:1;text-align:center;padding:50px;color:var(--t2);font-size:14px">Caricamento utenti...</div>';
  var me=_user?_user.uid:null;
  var invRows=_uInvites.length?_uInvites.map(function(i){
    var roleCell=adm?'<select onchange="uChgInviteRole(\''+esc(i.email)+'\',this.value)"><option value="member"'+(i.role!=='admin'?' selected':'')+'>Member</option><option value="admin"'+(i.role==='admin'?' selected':'')+'>Admin</option></select>':uRoleBadge(i.role);
    var act=adm?'<button class="b br" onclick="uRmInvite(\''+esc(i.email)+'\')">Rimuovi</button>':'';
    return '<tr><td>'+esc(i.email)+'</td><td>'+roleCell+'</td><td class="ctr">'+act+'</td></tr>';
  }).join(''):'<tr><td colspan="3" style="text-align:center;color:var(--t3);padding:14px">Nessuna email invitata.</td></tr>';
  var inviteForm=adm?'<div style="display:flex;gap:8px;margin-bottom:14px;flex-wrap:wrap"><input id="u-email" type="email" placeholder="nome.cognome@jakala.com" class="si" style="flex:1;min-width:240px;width:auto"><select id="u-role" class="si" style="width:120px"><option value="member">Member</option><option value="admin">Admin</option></select><button class="b ba" onclick="uDoInvite()">Invita</button></div>':'';
  var usrRows=_uUsers.length?_uUsers.map(function(u){
    var active=u.active!==false,isMe=u.uid===me;
    var roleCell=(adm&&!isMe)?'<select onchange="uChgUserRole(\''+u.uid+'\',this.value)"><option value="member"'+(u.role==='member'?' selected':'')+'>Member</option><option value="admin"'+(u.role==='admin'?' selected':'')+'>Admin</option></select>':uRoleBadge(u.role);
    var statusCell=active?'<span class="sb" style="background:rgba(47,110,18,.12);color:#2f6e12">Attivo</span>':'<span class="sb" style="background:rgba(0,0,0,.06);color:#42454c">Disabilitato</span>';
    var act=(adm&&!isMe)?(active?'<button class="b br" onclick="uDisable(\''+u.uid+'\')">Disabilita</button>':'<button class="b bg" onclick="uEnable(\''+u.uid+'\')">Riattiva</button>'):(isMe?'<span style="font-size:10px;color:var(--t3)">(tu)</span>':'');
    return '<tr style="'+(active?'':'opacity:.55')+'"><td>'+esc(u.displayName||'')+'</td><td>'+esc(u.email||'')+'</td><td>'+roleCell+'</td><td>'+statusCell+'</td><td class="ctr">'+act+'</td></tr>';
  }).join(''):'<tr><td colspan="5" style="text-align:center;color:var(--t3);padding:18px">Nessun utente ancora.</td></tr>';
  return '<div class="ucard"><div class="uct">Invited emails (access list)</div><div class="ucs">Only invited emails can register and sign in. Choose the role at invite time: the person receives it on first login. Then share the app link and the invited person registers, setting their own password.</div>'+inviteForm+'<table class="utbl"><thead><tr><th>Email</th><th>Role on first login</th><th class="ctr">Action</th></tr></thead><tbody>'+invRows+'</tbody></table></div>'
    +'<div class="ucard"><div class="uct">Users</div><div class="ucs">Users appear here automatically after their first login. From here you can change their role or disable their access.</div><table class="utbl"><thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Status</th><th class="ctr">Actions</th></tr></thead><tbody>'+usrRows+'</tbody></table></div>';
}
function amCard(label,val,color){return '<div class="ametric"><div class="aml">'+label+'</div><div class="amv"'+(color?(' style="color:'+color+'"'):'')+'>'+val+'</div></div>';}
function uDoInvite(){var e=(document.getElementById('u-email')||{}).value||'';var r=(document.getElementById('u-role')||{}).value||'member';if(!e.trim())return;uAddInvite(e,r).then(uLoad).catch(function(err){alert('Invito fallito: '+(err.message||err));});}
function uRmInvite(e){if(!confirm('Remove the invite for '+e+'?'))return;uRemoveInvite(e).then(uLoad).catch(function(err){alert(err.message||err);});}
function uChgInviteRole(e,r){uSetInviteRole(e,r).then(uLoad).catch(function(err){alert(err.message||err);});}
function uChgUserRole(uid,r){uSetUserRole(uid,r).then(uLoad).catch(function(err){alert(err.message||err);});}
function uDisable(uid){uSetUserActive(uid,false).then(uLoad).catch(function(err){alert(err.message||err);});}
function uEnable(uid){uSetUserActive(uid,true).then(uLoad).catch(function(err){alert(err.message||err);});}

// ===== Admin analytics: Overview / Billability / Allocation / Perception / People =====
function _d0(x){return Math.round(x||0).toLocaleString('en-US');}
function _p0(x){return (x||0).toFixed(0)+'%';}
function _bar(pct,col){var w=Math.max(0,Math.min(pct||0,100));return '<div class="acbar" style="margin:4px 0 0"><div style="width:'+w+'%;background:'+col+'"></div></div>';}
// Share of a project's quoted days that falls inside the current year (2026).
var YEAR=2026, _Y0=Date.UTC(YEAR,0,1), _Y1=Date.UTC(YEAR,11,31), _DAY=864e5;
function yearShare(p){
  var s=Date.parse(p.startDate),e=Date.parse(p.endDate);
  if(isNaN(s)||isNaN(e)||e<s)return 1;              // no usable dates: count in full
  var os=Math.max(s,_Y0),oe=Math.min(e,_Y1);
  if(oe<os)return 0;                                 // project doesn't touch this year
  return (oe-os+_DAY)/(e-s+_DAY);
}
// Aggregate capacity/effort per Price Level + quoted days for the current year
function admData(){
  var rows={},order=[];
  RH.forEach(function(r){rows[r]={rank:r,pl:rPL(r),n:0,cap:0,bill:0,nb:0};order.push(r);});
  S.m.forEach(function(m){var r=rows[m.role];if(!r)return;var c=m.cap||220;r.n++;r.cap+=c;r.bill+=mEfBill(m.id)/100*c;r.nb+=mEfNB(m.id)/100*c;});
  var quoted={PL4:0,PL3:0,PL2:0,PL1:0},quotedAll={PL4:0,PL3:0,PL2:0,PL1:0},np=0;
  S.p.forEach(function(p){
    if(p.nb)return;
    var sh=yearShare(p);
    if(sh>0)np++;
    PLkeys.forEach(function(k){var v=(p.daysByRole&&p.daysByRole[k])||0;quoted[k]+=v*sh;quotedAll[k]+=v;});
  });
  var used=order.filter(function(r){return rows[r].n>0;});
  var plCap={PL4:0,PL3:0,PL2:0,PL1:0},plBill={PL4:0,PL3:0,PL2:0,PL1:0},plNb={PL4:0,PL3:0,PL2:0,PL1:0},plN={PL4:0,PL3:0,PL2:0,PL1:0},plRanks={PL4:[],PL3:[],PL2:[],PL1:[]};
  used.forEach(function(r){var k='PL'+rows[r].pl;plCap[k]+=rows[r].cap;plBill[k]+=rows[r].bill;plNb[k]+=rows[r].nb;plN[k]+=rows[r].n;plRanks[k].push(r);});
  // Sellable capacity = capacity x the billability target set for that Price Level
  var tgt={},plSell={PL4:0,PL3:0,PL2:0,PL1:0};
  PLkeys.forEach(function(k){tgt[k]=tgtOf(k);plSell[k]=plCap[k]*tgt[k]/100;});
  return {rows:rows,used:used,quoted:quoted,quotedAll:quotedAll,nProjects:np,
          plCap:plCap,plBill:plBill,plNb:plNb,plN:plN,plRanks:plRanks,tgt:tgt,plSell:plSell};
}
function tgtOf(k){var v=(S.t&&S.t[k]);v=parseFloat(v);return (isFinite(v)&&v>0)?v:DEFT[k];}
function setTgt(k,v){v=parseFloat(v);if(!isFinite(v)||v<=0||v>100)return;S.t=Object.assign({},S.t);S.t[k]=v;sv();R();}
function resetTgt(){S.t=Object.assign({},DEFT);sv();R();}
function plLabel(k){return 'Price Level '+k.replace('PL','');}
function plRanksTxt(D,k){return D.plRanks[k].length?D.plRanks[k].join(', '):'-';}
function admSub(k,l){return '<a class="nav-item'+((S.aTab||'overview')===k?' active':'')+'" onclick="S.aTab=\''+k+'\';R()">'+l+'</a>';}
// Plain-English definition of every metric, shown next to the figures it explains.
var ADMDEF={
  capacity:'Capacity (available days) = number of people x their yearly working days (220 by default).',
  quoted:'Quoted days = days sold on the price quotes, counted pro rata for '+YEAR+': a project running beyond the year contributes only the share of its contract that falls inside it.',
  perceived:'Perceived = days people report they spend, billable and non-billable together, derived from the percentage weight each of them set on every project, compared with their capacity. It shows how loaded the team believes it is.',
  billability:'Billability = how the reported days split between billable client work and non-billable work (internal, management, presale, training, leave).',
  utilization:'Utilization rate = billable days divided by available capacity. It shows how much of the total available time goes to client work.',
  sellable:'Sellable capacity = capacity x the billability target of the Price Level: the days that can realistically be billed to clients, once the time planned for internal work, management, presale, training and leave is set aside.',
  saturation:'Saturation = days quoted on projects for '+YEAR+' divided by sellable capacity, so it compares what has been sold with the time the team can realistically bill. Above 100% the level is oversold.'
};
function admNote(txt){return '<div class="admnote">'+txt+'</div>';}
function admLegend(items){return '<div class="admleg">'+items.map(function(x){return '<span><b>'+x[0]+'</b> '+x[1]+'</span>';}).join('')+'</div>';}
function renderAdmin(){
  var t=S.aTab||'overview';
  var h='<div class="admsub">'+admSub('overview','Overview')+admSub('perceived','Perceived')+admSub('billability','Billability')+admSub('utilization','Utilization')+admSub('saturation','Saturation')+admSub('people','People')+admSub('users','Users')+'</div>';
  if(t==='perceived')h+=admPerceived();
  else if(t==='billability')h+=admBillability();
  else if(t==='utilization')h+=admUtilization();
  else if(t==='saturation')h+=admSaturation();
  else if(t==='people')h+=admPeople();
  else if(t==='users'){h+=renderUsers();h+='<div class="ucard"><div class="uct">Maintenance</div><div class="ucs">Reset people and projects to their initial values. This cannot be undone.</div><button class="b br" onclick="rst()">Reset data</button></div>';}
  else h+=admOverview();
  return h;
}
// ── Overview: the four headline metrics side by side, per Price Level ──
function admOverview(){
  var D=admData(),tQ=0,tQA=0,tC=0,tB=0,tNb=0,tN=0,tS=0;
  PLkeys.forEach(function(k){tQ+=D.quoted[k];tQA+=D.quotedAll[k];tC+=D.plCap[k];tB+=D.plBill[k];tNb+=D.plNb[k];tN+=D.plN[k];tS+=D.plSell[k];});
  var sat=tS?tQ/tS*100:0,gsat=tC?tQ/tC*100:0,util=tC?tB/tC*100:0,perc=tC?(tB+tNb)/tC*100:0;
  var h='<div class="ucard"><div class="uct">Overview '+YEAR+'</div><div class="ucs">Headcount, active projects and the four headline metrics for the year. Every figure is expressed in working days.</div>'
   +'<div class="ametrics">'+amCard('People',tN,'')+amCard('Projects',D.nProjects,'')+amCard('Capacity (d)',_d0(tC),'')+amCard('Sellable (d)',_d0(tS),'')+amCard('Quoted '+YEAR+' (d)',_d0(tQ),'#185fa5')+'</div>'
   +'<div class="ametrics" style="margin-top:10px">'+amCard('Perceived',_p0(perc),sc(perc))+amCard('Billable share',_p0(tB+tNb?tB/(tB+tNb)*100:0),'#185fa5')+amCard('Utilization rate',_p0(util),sc(util))+amCard('Real saturation',_p0(sat),sc(sat))+'</div>'
   +admLegend([['Perceived','reported days / capacity'],['Billable share','billable / reported days'],['Utilization rate','billable days / capacity'],['Sellable','capacity x the billability target of each Price Level'],['Real saturation','quoted days / sellable days ('+_p0(gsat)+' on gross capacity)']])+'</div>';
  h+='<div class="ucard"><div class="uct">By Price Level</div><div class="ucs">'+ADMDEF.capacity+' '+ADMDEF.quoted+'</div>'
   +'<table class="utbl"><thead><tr><th>Price Level</th><th>HR ranks</th><th class="r">People</th><th class="r">Capacity (d)</th><th class="r">Target</th><th class="r">Sellable (d)</th><th class="r">Quoted '+YEAR+' (d)</th><th class="r">Perceived</th><th class="r">Utilization</th><th class="r">Real saturation</th></tr></thead><tbody>';
  PLkeys.forEach(function(k){
    var cap=D.plCap[k],sell=D.plSell[k],q=D.quoted[k],b=D.plBill[k],nb=D.plNb[k];
    var pe=cap?(b+nb)/cap*100:0,u=cap?b/cap*100:0,s=sell?q/sell*100:(q>0?999:0);
    h+='<tr><td><b>'+plLabel(k)+'</b></td><td style="font-size:11px;color:var(--t2)">'+esc(plRanksTxt(D,k))+'</td><td class="r">'+D.plN[k]+'</td><td class="r">'+_d0(cap)+'</td><td class="r">'+_p0(D.tgt[k])+'</td><td class="r">'+_d0(sell)+'</td><td class="r">'+_d0(q)+'</td><td class="r" style="color:'+sc(pe)+'">'+_p0(pe)+'</td><td class="r" style="color:'+sc(u)+'">'+_p0(u)+'</td><td class="r"><b style="color:'+sc(s)+'">'+(s>900?'no capacity':_p0(s))+'</b></td></tr>';
  });
  h+='<tr class="tot"><td>Total</td><td></td><td class="r">'+tN+'</td><td class="r">'+_d0(tC)+'</td><td class="r">'+_p0(tC?tS/tC*100:0)+'</td><td class="r">'+_d0(tS)+'</td><td class="r">'+_d0(tQ)+'</td><td class="r">'+_p0(perc)+'</td><td class="r">'+_p0(util)+'</td><td class="r">'+_p0(sat)+'</td></tr>';
  h+='</tbody></table>'+admNote('Quoted days for the full contract length, ignoring the year split, add up to '+_d0(tQA)+' days.')+'</div>';
  return h;
}
// ── Perceived: reported days (billable + non-billable) against capacity ──
function admPerceived(){
  var D=admData(),tc=0,tp=0,tN=0;
  var h='<div class="ucard"><div class="uct">Perceived</div><div class="ucs">'+ADMDEF.perceived+'</div>'
   +'<table class="utbl"><thead><tr><th>Price Level</th><th>HR ranks</th><th class="r">People</th><th class="r">Capacity (d)</th><th class="r">Reported (d)</th><th class="r">Perceived</th></tr></thead><tbody>';
  PLkeys.forEach(function(k){
    var cap=D.plCap[k],rep=D.plBill[k]+D.plNb[k],p=cap?rep/cap*100:0;
    tc+=cap;tp+=rep;tN+=D.plN[k];
    h+='<tr><td><b>'+plLabel(k)+'</b></td><td style="font-size:11px;color:var(--t2)">'+esc(plRanksTxt(D,k))+'</td><td class="r">'+D.plN[k]+'</td><td class="r">'+_d0(cap)+'</td><td class="r">'+_d0(rep)+'</td><td class="r"><b style="color:'+sc(p)+'">'+_p0(p)+'</b>'+_bar(p,sc(p))+'</td></tr>';
  });
  h+='<tr class="tot"><td>Total</td><td></td><td class="r">'+tN+'</td><td class="r">'+_d0(tc)+'</td><td class="r">'+_d0(tp)+'</td><td class="r">'+_p0(tc?tp/tc*100:0)+'</td></tr></tbody></table>'
   +admLegend([['Capacity','people x 220 working days'],['Reported','sum of the percentages people set, converted into days'],['Perceived','reported days / capacity']])
   +admNote('Above 100% means people report more work than the time they have; below 100% means part of their time is unaccounted for.')+'</div>';
  return h;
}
// ── Billability: how reported days split between billable and non-billable ──
function admBillability(){
  var D=admData(),tb=0,tn=0,tN=0;
  var h='<div class="ucard"><div class="uct">Billability</div><div class="ucs">'+ADMDEF.billability+'</div>'
   +'<table class="utbl"><thead><tr><th>Price Level</th><th>HR ranks</th><th class="r">People</th><th class="r">Reported (d)</th><th class="r">Billable (d)</th><th class="r">Non-billable (d)</th><th class="r">Billable share</th></tr></thead><tbody>';
  PLkeys.forEach(function(k){
    var b=D.plBill[k],nb=D.plNb[k],rep=b+nb,s=rep?b/rep*100:0;
    tb+=b;tn+=nb;tN+=D.plN[k];
    h+='<tr><td><b>'+plLabel(k)+'</b></td><td style="font-size:11px;color:var(--t2)">'+esc(plRanksTxt(D,k))+'</td><td class="r">'+D.plN[k]+'</td><td class="r">'+_d0(rep)+'</td><td class="r" style="color:#185fa5">'+_d0(b)+'</td><td class="r" style="color:var(--t3)">'+_d0(nb)+'</td><td class="r"><b>'+_p0(s)+'</b>'+_bar(s,'#185fa5')+'<span style="display:block;font-size:10px;color:var(--t3);margin-top:2px">non-billable '+_p0(100-s)+'</span></td></tr>';
  });
  var rep=tb+tn;
  h+='<tr class="tot"><td>Total</td><td></td><td class="r">'+tN+'</td><td class="r">'+_d0(rep)+'</td><td class="r">'+_d0(tb)+'</td><td class="r">'+_d0(tn)+'</td><td class="r">'+_p0(rep?tb/rep*100:0)+'</td></tr></tbody></table>'
   +admLegend([['Billable','days on client projects'],['Non-billable','internal work, management, presale, training and leave'],['Billable share','billable days / reported days']])
   +admNote('This view splits the days people report. To compare billable days with the time actually available, see Utilization.')+'</div>';
  return h;
}
// ── Utilization: billable days against capacity ──
function admUtilization(){
  var D=admData(),tb=0,tc=0,tN=0;
  var h='<div class="ucard"><div class="uct">Utilization rate</div><div class="ucs">'+ADMDEF.utilization+'</div>'
   +'<table class="utbl"><thead><tr><th>Price Level</th><th>HR ranks</th><th class="r">People</th><th class="r">Capacity (d)</th><th class="r">Billable (d)</th><th class="r">Utilization rate</th></tr></thead><tbody>';
  PLkeys.forEach(function(k){
    var cap=D.plCap[k],b=D.plBill[k],u=cap?b/cap*100:0;
    tb+=b;tc+=cap;tN+=D.plN[k];
    h+='<tr><td><b>'+plLabel(k)+'</b></td><td style="font-size:11px;color:var(--t2)">'+esc(plRanksTxt(D,k))+'</td><td class="r">'+D.plN[k]+'</td><td class="r">'+_d0(cap)+'</td><td class="r" style="color:#185fa5">'+_d0(b)+'</td><td class="r"><b style="color:'+sc(u)+'">'+_p0(u)+'</b>'+_bar(u,sc(u))+'</td></tr>';
  });
  h+='<tr class="tot"><td>Total</td><td></td><td class="r">'+tN+'</td><td class="r">'+_d0(tc)+'</td><td class="r">'+_d0(tb)+'</td><td class="r">'+_p0(tc?tb/tc*100:0)+'</td></tr></tbody></table>'
   +admLegend([['Capacity','people x 220 working days'],['Billable','days on client projects'],['Utilization rate','billable days / capacity']])
   +admNote('The gap to 100% is the share of available time not sold to clients: internal work, presale, training, leave or idle capacity.')+'</div>';
  return h;
}
// ── Saturation: quoted days against the sellable capacity implied by the targets ──
function admSaturation(){
  var D=admData(),tc=0,tq=0,tb=0,tN=0,ts=0;
  // editable billability targets
  var h='<div class="ucard"><div class="uct">Billability targets</div><div class="ucs">Share of the year each Price Level is expected to sell to clients. The rest is planned for internal work, management, presale, training and leave. These targets set the sellable capacity used by the real saturation below.</div><div class="tgtrow">';
  PLkeys.forEach(function(k){
    h+='<label class="tgtbox"><span>'+plLabel(k)+'</span><span style="font-size:10px;color:var(--t3)">'+esc(plRanksTxt(D,k))+'</span><span class="tgtin"><input type="number" min="1" max="100" step="5" value="'+tgtOf(k)+'" onchange="setTgt(\''+k+'\',this.value)">%</span></label>';
  });
  h+='</div><button class="b bo" style="margin-top:10px" onclick="resetTgt()">Reset to defaults</button></div>';
  h+='<div class="ucard"><div class="uct">Saturation '+YEAR+'</div><div class="ucs">'+ADMDEF.saturation+' '+ADMDEF.sellable+' '+ADMDEF.quoted+'</div>'
   +'<table class="utbl"><thead><tr><th>Price Level</th><th class="r">People</th><th class="r">Capacity (d)</th><th class="r">Target</th><th class="r">Sellable (d)</th><th class="r">Quoted '+YEAR+' (d)</th><th class="r">Real saturation</th><th class="r">On gross capacity</th></tr></thead><tbody>';
  PLkeys.forEach(function(k){
    var cap=D.plCap[k],sell=D.plSell[k],q=D.quoted[k];
    var s=sell?q/sell*100:(q>0?999:0),g=cap?q/cap*100:(q>0?999:0);
    tc+=cap;tq+=q;tb+=D.plBill[k];tN+=D.plN[k];ts+=sell;
    h+='<tr><td><b>'+plLabel(k)+'</b><div style="font-size:10px;color:var(--t3);font-weight:400">'+esc(plRanksTxt(D,k))+'</div></td><td class="r">'+D.plN[k]+'</td><td class="r">'+_d0(cap)+'</td><td class="r">'+_p0(D.tgt[k])+'</td><td class="r"><b>'+_d0(sell)+'</b></td><td class="r">'+_d0(q)+'</td><td class="r"><b style="color:'+sc(s)+'">'+(s>900?'no capacity':_p0(s))+'</b>'+_bar(s,sc(s))+'</td><td class="r" style="color:var(--t3)">'+(g>900?'-':_p0(g))+'</td></tr>';
  });
  h+='<tr class="tot"><td>Total</td><td class="r">'+tN+'</td><td class="r">'+_d0(tc)+'</td><td class="r">'+_p0(tc?ts/tc*100:0)+'</td><td class="r">'+_d0(ts)+'</td><td class="r">'+_d0(tq)+'</td><td class="r">'+_p0(ts?tq/ts*100:0)+'</td><td class="r">'+_p0(tc?tq/tc*100:0)+'</td></tr></tbody></table>'
   +admLegend([['Capacity','people x 220 working days'],['Target','share of the year expected to be billable'],['Sellable','capacity x target, the days that can actually be sold'],['Quoted '+YEAR,'days sold on the quotes, pro rata for the year'],['Real saturation','quoted days / sellable days'],['On gross capacity','quoted days / capacity, ignoring the target']])
   +admNote('Real saturation is the meaningful one: above 100% the level is sold beyond the time it can realistically bill, so the work has to be covered by other levels, external resources or a longer schedule.')+'</div>';
  // quoted versus what the team reports
  h+='<div class="ucard"><div class="uct">Quoted versus billable reported</div><div class="ucs">What was sold on the quotes for '+YEAR+' compared with the billable days the team reports. A large gap means quoted work is not reflected in what people say they are doing.</div>'
   +'<table class="utbl"><thead><tr><th>Price Level</th><th class="r">Quoted '+YEAR+' (d)</th><th class="r">Billable reported (d)</th><th class="r">Difference</th></tr></thead><tbody>';
  PLkeys.forEach(function(k){
    var q=D.quoted[k],b=D.plBill[k],df=b-q;
    h+='<tr><td><b>'+plLabel(k)+'</b></td><td class="r">'+_d0(q)+'</td><td class="r">'+_d0(b)+'</td><td class="r" style="color:'+(df>=0?'#2f6e12':'#b32a1c')+'">'+(df>0?'+':'')+_d0(df)+'</td></tr>';
  });
  h+='<tr class="tot"><td>Total</td><td class="r">'+_d0(tq)+'</td><td class="r">'+_d0(tb)+'</td><td class="r">'+((tb-tq)>0?'+':'')+_d0(tb-tq)+'</td></tr>';
  return h+'</tbody></table></div>';
}
// ── People: billability / allocation / perception per team member ──
function admPeople(){
  var rows=S.m.map(function(m){
    var c=m.cap||220,ef=mEf(m.id),eb=mEfBill(m.id),enb=mEfNB(m.id);
    return {m:m,cap:c,ef:ef,bill:eb/100*c,nb:enb/100*c,util:eb,alloc:Math.round(ef/100*c*10)/10,
            avail:100-ef,pc:S.p.filter(function(p){return p.asgn&&p.asgn[m.id]>0&&!p.nb;}).length,status:sl(ef)};
  }).sort(function(a,b){return b.util-a.util;});
  var h='<div class="ucard"><div class="uct">People</div><div class="ucs">The same metrics for each team member: perceived load, billable split, utilization rate and how many projects they are on.</div>'
   +'<table class="utbl"><thead><tr><th>Name</th><th>HR rank</th><th class="r">Capacity (d)</th><th class="r">Reported (d)</th><th class="r">Perceived</th><th class="r">Billable (d)</th><th class="r">Non-bill. (d)</th><th class="r">Billable share</th><th class="r">Utilization</th><th class="r">Projects</th><th>Status</th></tr></thead><tbody>';
  rows.forEach(function(x){
    var rep=x.bill+x.nb,pe=x.cap?rep/x.cap*100:0,bs=rep?x.bill/rep*100:0;
    h+='<tr><td style="font-weight:600">'+esc(x.m.name)+'</td><td style="color:'+(RC[x.m.role]||'#999')+';font-size:11px">'+esc(x.m.role)+'</td><td class="r">'+_d0(x.cap)+'</td><td class="r">'+_d0(rep)+'</td><td class="r" style="color:'+sc(pe)+'">'+_p0(pe)+'</td><td class="r" style="color:#185fa5">'+_d0(x.bill)+'</td><td class="r" style="color:var(--t3)">'+_d0(x.nb)+'</td><td class="r">'+_p0(bs)+'</td><td class="r"><b style="color:'+sc(x.util)+'">'+_p0(x.util)+'</b></td><td class="r">'+x.pc+'</td><td><span class="sb" style="background:'+sc(x.ef)+'18;color:'+sc(x.ef)+'">'+x.status+'</span></td></tr>';
  });
  return h+'</tbody></table>'
   +admLegend([['Capacity','the person\'s yearly working days'],['Reported','days from the percentages they set (billable + non-billable)'],['Perceived','reported days / capacity'],['Billable share','billable / reported days'],['Utilization','billable days / capacity'],['Status','load band based on the total percentage assigned']])+'</div>';
}
"""
cut = html.rindex('</script>')
html = html[:cut] + users_js + '\n' + html[cut:]

# ── J. Status column visible to admins only (Team table) ──
html = html.replace('<th>Stato</th>', "${isAdmin()?'<th>Status</th>':''}", 1)
html = html.replace(
    '<td><span class="sb" style="background:${c}18;color:${c}">${m.status}</span></td>',
    '${isAdmin()?`<td><span class="sb" style="background:${c}18;color:${c}">${m.status}</span></td>`:``}', 1)

# ── K. Translate the whole UI to English ──
TR = [
    # Long sentences (most specific first)
    ("Solo le email invitate possono registrarsi e accedere. Scegli il ruolo al momento dell'invito: la persona lo riceve al primo accesso. Poi condividi il link dell'app: l'invitato si registra impostando la propria password.",
     "Only invited emails can register and sign in. Choose the role at invite time: the person receives it on first login. Then share the app link and the invited person registers, setting their own password."),
    ("Gli utenti compaiono qui automaticamente dopo il primo accesso. Da qui puoi cambiarne il ruolo o disabilitarne l'accesso.",
     "Users appear here automatically after their first login. From here you can change their role or disable their access."),
    ("Ripristina persone e progetti ai valori iniziali. Operazione irreversibile.",
     "Reset people and projects to their initial values. This cannot be undone."),
    ("Questo indirizzo non risulta invitato. Chiedi a un amministratore di aggiungerti.",
     "This email has not been invited. Ask an administrator to add you."),
    ("Il tuo account è stato disabilitato. Contatta un amministratore.",
     "Your account has been disabled. Contact an administrator."),
    ("Solo indirizzi @jakala.com possono essere invitati.", "Only @jakala.com addresses can be invited."),
    ("Attenzione: effort totale sarà ", "Warning: total effort will be "),
    ("Il sovraccarico verrà evidenziato. Procedere?", "The overload will be highlighted. Proceed?"),
    ("(supera 100%).", "(over 100%)."),
    ("Rimuovere l'invito per ", "Remove the invite for "),
    ("Invito fallito: ", "Invite failed: "),
    ("Resettare tutto?", "Reset everything?"),
    # Panels / cards / view titles
    ("Email invitate (lista accessi)", "Invited emails (access list)"),
    ("Capacità per Price Level", "Capacity by Price Level"),
    ("GG PQ per Price Level", "Quoted days per Price Level"),
    ("Ruolo al primo accesso", "Role on first login"),
    ("Nessuna email invitata.", "No invited emails."),
    ("Nessun utente ancora.", "No users yet."),
    ("Caricamento utenti...", "Loading users..."),
    ("Caricamento dati...", "Loading data..."),
    ("Seleziona un progetto", "Select a project"),
    ("Seleziona una persona", "Select a person"),
    ("Panoramica team", "Team overview"),
    ("Capacità gg/anno", "Capacity (days/year)"),
    ("Aggiungi Persona", "Add person"), ("Modifica Persona", "Edit person"),
    ("Aggiungi Progetto", "Add project"), ("Modifica Progetto", "Edit project"),
    ("Tutti i clienti", "All clients"),
    ("Effort tot. medio", "Avg total effort"),
    ("Effort totale:", "Total effort:"),
    ("EFFORT TOT.", "TOTAL EFFORT"),
    ("Reset dati", "Reset data"), ("Manutenzione", "Maintenance"),
    # Assign view
    ("Per Progetto", "By project"), ("Per Persona", "By person"),
    ("Cerca progetto...", "Search project..."), ("Cerca persona...", "Search person..."),
    ("Filtra progetto...", "Filter project..."),
    ("Progetti che richiedono ", "Projects requiring "),
    ("Altri progetti (", "Other projects ("),
    ("Progetti assegnati (", "Assigned projects ("),
    ("Ricalcola", "Recalculate"), ("Calcola %", "Calculate %"),
    ("Revisione", "Review"), ("← Associa", "← Link"), ("Altri (", "Other ("),
    # Status labels
    ("SOVRACCARICO", "OVERLOADED"), ("CRITICO", "CRITICAL"),
    ('"ALTO"', '"HIGH"'), ('"MEDIO"', '"MEDIUM"'), ("DISPONIBILE", "AVAILABLE"),
    # Tabs
    ("📁 Progetti", "📁 Projects"), ("🔢 Matrice", "🔢 Matrix"), ("⚡️ Assegna", "⚡️ Assign"),
    # Day units / GG
    ("GG allocati", "Allocated days"), ("GG venduti", "Sold days"),
    ("GG Alloc.", "Alloc. days"), ("GG Alloc", "Alloc. days"), ("GG PQ", "Quoted days"),
    (" gg/anno", " days/yr"),
    # Table headers (anchored to avoid touching code)
    (">Nome ", ">Name "), (">Ruolo ", ">Role "), (">Cliente ", ">Client "),
    (">Inizio ", ">Start "), (">Fine ", ">End "), (">Progetti ", ">Projects "),
    (">Progetto ", ">Project "),
    ("Effort Tot.", "Total effort"), ("Disponib.", "Available"),
    ("Non Bill.", "Non-bill."), ("Copertura", "Coverage"), ("copertura", "coverage"),
    # Filters / options / placeholders
    (">Tutti</option>", ">All</option>"), ("Filtra...", "Filter..."),
    ("Cerca...", "Search..."),
    # Matrix sort + footer
    ("Nome A→Z", "Name A→Z"), ("Cliente A→Z", "Client A→Z"),
    ("N° Persone ↓", "# People ↓"), ("Ruolo (rank)", "Role (rank)"),
    ("Persone:", "People:"), ("Progetti:", "Projects:"),
    ("} progetti · ", "} projects · "), ("} persone</span>", "} people</span>"),
    # Add buttons
    ("+ Persona", "+ Person"), ("+ Progetto", "+ Project"),
    # Users / admin labels
    (">Utenti<", ">Users<"), (">Invita<", ">Invite<"),
    ("Rimuovi", "Remove"), ("Disabilitato", "Disabled"), ("Disabilita", "Disable"),
    ("Riattiva", "Re-enable"), (">Attivo<", ">Active<"),
    (">Azioni<", ">Actions<"), (">Azione<", ">Action<"), ("oltre 100%", "over 100%"),
    (">Persone<", ">People<"), (">Progetti<", ">Projects<"),
    # Modals
    (">Nome</label>", ">Name</label>"), (">Cliente</label>", ">Client</label>"),
    (">Inizio</label>", ">Start</label>"), (">Fine</label>", ">End</label>"),
    (">Ruolo</label>", ">Role</label>"),
    ("Annulla", "Cancel"), (">Aggiungi<", ">Add<"), (">Salva<", ">Save<"),
    ('"Nome!"', '"Name!"'),
    # Person panel + day units
    (" gg · Disp:", " d · Avail:"), ("}gg", "}d"), ("'gg'", "'d'"), (" GG ", " d "),
    ("Progetti (", "Projects ("), ("Esci", "Sign out"), ("(tu)", "(you)"),
    ("Non billable", "Non-billable"),
    # Admin metric labels + matrix project header
    ("amCard('Persone'", "amCard('People'"), ("amCard('Progetti'", "amCard('Projects'"),
    (">Progetto</th>", ">Project</th>"),
    ('"Rimuovere?"', '"Remove?"'),
    (">Assegna</div>", ">Assign</div>"),
    ("nome.cognome@jakala.com", "name.surname@jakala.com"),
    # Title
    ("SEO Staffing Hub", "SEO/GEO Staffing Hub"),
    ("Eliminare?", "Delete?"),
]
for it, en in TR:
    html = html.replace(it, en)
# The translation table works on raw text, so a short entry can corrupt code
# (e.g. "(tu)" -> "(you)" inside an expression). Catch that here.
assert '(you)' not in html.replace('>(you)<', ''), 'translation leaked into code: (you)'

# ── O. Team table: move Alloc. days / Available / Projects / Status to the Admin > People view ──
for frag in [
    """<th${ts.col==='d'?' class="sorted"':''}><div class="thw" ${thH('t','d')}>Alloc. days ${arrI('t','d')}</div></th>""",
    """<th${ts.col==='avail'?' class="sorted"':''}><div class="thw" ${thH('t','avail')}>Available ${arrI('t','avail')}</div></th>""",
    """<th${ts.col==='pc'?' class="sorted"':''}><div class="thw" ${thH('t','pc')}>Projects ${arrI('t','pc')}</div></th>""",
    """${isAdmin()?'<th>Status</th>':''}""",
    """<td class="num">${m.d}</td>""",
    """<td class="num" style="color:${av>=0?'var(--gn)':'var(--rd)'}">${av.toFixed(0)}%</td>""",
    """<td class="num">${m.pc}</td>""",
    """${isAdmin()?`<td><span class="sb" style="background:${c}18;color:${c}">${m.status}</span></td>`:``}""",
]:
    assert frag in html, 'team column fragment not found: ' + frag[:60]
    html = html.replace(frag, '', 1)

# ── L. Members are read-only on the TEAM list (only admins add/edit/delete team people) ──
html = html.replace(
    '<div style="display:flex;justify-content:flex-start;margin-bottom:8px;flex-shrink:0"><button class="b bg" onclick="amM()">+ Person</button></div>',
    '${isAdmin()?`<div style="display:flex;justify-content:flex-start;margin-bottom:8px;flex-shrink:0"><button class="b bg" onclick="amM()">+ Person</button></div>`:``}', 1)
html = html.replace(
    '<button class="b ba" onclick="emM(\'${m.id}\')">✎</button><button class="b br" onclick="dM(\'${m.id}\')">✕</button>',
    '${isAdmin()?`<button class="b ba" onclick="emM(\'${m.id}\')">✎</button><button class="b br" onclick="dM(\'${m.id}\')">✕</button>`:``}', 1)
for fn in ['function amM(', 'function doAM(', 'function doEM(', 'function dM(']:
    html = html.replace(fn + '){', fn + "){if(!isAdmin())return;", 1)
html = html.replace(
    'function emM(id){const m=S.m.find(x=>x.id===id);if(!m)return;',
    'function emM(id){if(!isAdmin())return;const m=S.m.find(x=>x.id===id);if(!m)return;', 1)

# ── M. Members can edit ONLY projects they created or are involved in (have an allocation); admins: all ──
# M1. Permission helpers (a signed-in user is mapped to team resources by name-token match).
helpers = (
    r"function _nmTok(s){return String(s||'').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/\[ext\]/g,' ').replace(/[^a-z\s]/g,' ').split(/\s+/).filter(Boolean);}"
    r"function _emailFromName(n){var t=_nmTok(n);return t.length?t.join('.')+'@jakala.com':'';}"
    r"function _resEmail(m){return (m&&m.email&&String(m.email).toLowerCase())||_emailFromName(m&&m.name);}"
    r"function myResourceIds(){if(!_user)return[];var em=String(_user.email||'').toLowerCase();var mine=_nmTok((_profile&&_profile.displayName)||_user.email);return S.m.filter(function(m){if(em&&_resEmail(m)===em)return true;return mine.length&&mine.every(function(t){return _nmTok(m.name).indexOf(t)>=0;});}).map(function(m){return m.id;});}"
    r"function canEditProject(p){if(isAdmin())return true;if(!p||!_user)return false;if(p.createdBy&&p.createdBy===_user.uid)return true;var ids=myResourceIds();return ids.some(function(id){return p.asgn&&p.asgn[id]>0;});}"
    r"function canEditProjectId(pid){return canEditProject(S.p.find(function(x){return x.id===pid;}));}"
    r"function _migrateTeam(){var ch=false;(S.m||[]).forEach(function(m){if(m.name==='Federico Gennari Santori'){m.name='Federico Gennari';ch=true;}if(!m.email){m.email=_emailFromName(m.name);ch=true;}});"
    # Drop the spreadsheet summary rows ("Totale") that an early import stored as
    # projects: they carry huge phantom quoted days and wreck every metric.
    r"var before=(S.p||[]).length;S.p=(S.p||[]).filter(function(p){if(p.nb)return true;return !/^\s*total/i.test(p.name||'');});if(S.p.length!==before)ch=true;"
    r"if(ch&&typeof isAdmin==='function'&&isAdmin()){try{sv();}catch(e){}}}"
)
html = html.replace('function mEf(mid){', helpers + '\nfunction mEf(mid){', 1)

# M2. Stamp the creator when a project is created.
html = html.replace(',daysByRole:dr,asgn:{}})', ',daysByRole:dr,asgn:{},createdBy:(_user&&_user.uid)||null})', 1)

# M3. Function-level guards on project + assignment mutations (the real enforcement).
html = html.replace('function doEP(id){const p=S.p.find(x=>x.id===id);if(!p)return;',
                    'function doEP(id){if(!canEditProjectId(id))return;const p=S.p.find(x=>x.id===id);if(!p)return;', 1)
html = html.replace('function epM(id){const p=S.p.find(x=>x.id===id);if(!p)return;',
                    'function epM(id){if(!canEditProjectId(id))return;const p=S.p.find(x=>x.id===id);if(!p)return;', 1)
html = html.replace('function dP(id){if(!confirm("Delete?"))return;',
                    'function dP(id){if(!canEditProjectId(id))return;if(!confirm("Delete?"))return;', 1)
html = html.replace('function setE(pid,mid,pct){const p=S.p.find(x=>x.id===pid);if(!p)return;',
                    'function setE(pid,mid,pct){if(!canEditProjectId(pid))return;const p=S.p.find(x=>x.id===pid);if(!p)return;', 1)
html = html.replace('function rmE(pid,mid){const p=S.p.find(x=>x.id===pid);',
                    'function rmE(pid,mid){if(!canEditProjectId(pid))return;const p=S.p.find(x=>x.id===pid);', 1)
html = html.replace('function togLink(pid,mid){\n  const p=S.p.find(x=>x.id===pid);if(!p)return;',
                    'function togLink(pid,mid){\n  if(!canEditProjectId(pid))return;const p=S.p.find(x=>x.id===pid);if(!p)return;', 1)
html = html.replace('function autoCalc(pid){\n  const p=S.p.find(x=>x.id===pid);if(!p)return;',
                    'function autoCalc(pid){\n  if(!canEditProjectId(pid))return;const p=S.p.find(x=>x.id===pid);if(!p)return;', 1)
html = html.replace('function oMx(pid,mid){S._ec={pid,mid};R()}',
                    'function oMx(pid,mid){if(!canEditProjectId(pid))return;S._ec={pid,mid};R()}', 1)
html = html.replace('const linkedPs=S.p.filter(p=>p.asgn?.[mid]>0);',
                    'const linkedPs=S.p.filter(p=>p.asgn?.[mid]>0&&canEditProject(p));', 1)
html = html.replace('function rst(){if(!confirm("Reset everything?"))return;',
                    'function rst(){if(!isAdmin())return;if(!confirm("Reset everything?"))return;', 1)

# M4. Project panel: compute editability once and hide the edit controls when the user can't edit.
html = html.replace('x.id===S.sp);if(p){', 'x.id===S.sp);if(p){const _ce=canEditProject(p);', 1)
html = html.replace(
    """<button class="b ba" onclick="epM('${p.id}')">✎</button><button class="b br" onclick="dP('${p.id}')">✕</button>""",
    """${_ce?`<button class="b ba" onclick="epM('${p.id}')">✎</button><button class="b br" onclick="dP('${p.id}')">✕</button>`:``}""", 1)
html = html.replace(
    """<div style="display:flex;align-items:center;gap:3px"><input class="pi" type="number" min="0" max="100" step="5" value="${a.pct}" onchange="setE('${p.id}','${a.mid}',parseFloat(this.value)||0)"><span style="font-size:8px;color:var(--t3)">%</span><span style="font-family:var(--mn);font-size:8px;color:var(--a2)">${de.toFixed(0)}d</span><button class="rb" onclick="rmE('${p.id}','${a.mid}')">×</button></div>""",
    """<div style="display:flex;align-items:center;gap:3px">${_ce?`<input class="pi" type="number" min="0" max="100" step="5" value="${a.pct}" onchange="setE('${p.id}','${a.mid}',parseFloat(this.value)||0)">`:`<span class="pi" style="border-color:transparent;text-align:center">${a.pct}</span>`}<span style="font-size:8px;color:var(--t3)">%</span><span style="font-family:var(--mn);font-size:8px;color:var(--a2)">${de.toFixed(0)}d</span>${_ce?`<button class="rb" onclick="rmE('${p.id}','${a.mid}')">×</button>`:``}</div>""", 1)
html = html.replace(
    """h+=`<div class="psc">Add</div><div class="ac">`;\nms.filter(m=>!asg.find(a=>a.mid===m.id)).map(m=>({...m,av:100-mEf(m.id)})).forEach(m=>{h+=`<span class="ach" onclick="setE('${p.id}','${m.id}',10)"${m.av<=0?' style="opacity:.5"':''}>+ ${esc(m.name)} <span style="font-size:7px;opacity:.5">${m.av.toFixed(0)}%</span></span>`});\nh+=`</div></div>`}}}""",
    """if(_ce){h+=`<div class="psc">Add</div><div class="ac">`;\nms.filter(m=>!asg.find(a=>a.mid===m.id)).map(m=>({...m,av:100-mEf(m.id)})).forEach(m=>{h+=`<span class="ach" onclick="setE('${p.id}','${m.id}',10)"${m.av<=0?' style="opacity:.5"':''}>+ ${esc(m.name)} <span style="font-size:7px;opacity:.5">${m.av.toFixed(0)}%</span></span>`});\nh+=`</div>`;}\nh+=`</div>`}}}""", 1)

# M5. Assign "By project" list shows members only the projects they can edit.
html = html.replace('let fap=[...ps].filter(p=>p.totalDays>0);',
                    'let fap=[...ps].filter(p=>p.totalDays>0&&canEditProject(p));', 1)

# ── P. Billability targets per Price Level (editable, shared through Firebase) ──
# P1. Defaults + state
html = html.replace('const PLkeys=',
                    'const DEFT={PL4:50,PL3:75,PL2:80,PL1:90};\nconst PLkeys=', 1)
html = html.replace('let S={m:JSON.parse(JSON.stringify(IM)),p:JSON.parse(JSON.stringify(IP)),',
                    'let S={m:JSON.parse(JSON.stringify(IM)),p:JSON.parse(JSON.stringify(IP)),t:Object.assign({},DEFT),', 1)
# P2. Persist them on save (loading is wired further down, once step N has run)
html = html.replace('dbRef.set({m:S.m,p:S.p})', 'dbRef.set({m:S.m,p:S.p,t:S.t})', 1)
html = html.replace('localStorage.setItem("sfv11",JSON.stringify({m:S.m,p:S.p}))',
                    'localStorage.setItem("sfv11",JSON.stringify({m:S.m,p:S.p,t:S.t}))', 1)

# ── N. Email per team resource (robust user<->resource link) + rename in seed ──
# N1. Seed rename so resets/new data are correct too.
html = html.replace('name:"Federico Gennari Santori"', 'name:"Federico Gennari"', 1)
# N2. On load, backfill emails and apply the rename (persisted by an admin).
html = html.replace('if(d?.m&&d?.p){S.m=d.m;S.p=d.p}',
                    'if(d?.m&&d?.p){S.m=d.m;S.p=d.p;try{_migrateTeam();}catch(e){}}')   # once() + localStorage fallback
html = html.replace('if(d?.m&&d?.p){S.m=d.m;S.p=d.p;R()}',
                    'if(d?.m&&d?.p){S.m=d.m;S.p=d.p;try{_migrateTeam();}catch(e){}R()}', 1)  # realtime listener
# N3. Email field in the Add person modal.
html = html.replace(
    '<h2>Add person</h2><label>Name</label><input id="xn"><label>Role</label>',
    '<h2>Add person</h2><label>Name</label><input id="xn"><label>Email</label><input id="xe" type="email" placeholder="name.surname@jakala.com"><label>Role</label>', 1)
html = html.replace(
    'S.m.push({id:"m_"+Math.random().toString(36).slice(2,8),name:n,role:document.getElementById("xr").value,cap:parseInt(document.getElementById("xc").value)||220})',
    'S.m.push({id:"m_"+Math.random().toString(36).slice(2,8),name:n,role:document.getElementById("xr").value,cap:parseInt(document.getElementById("xc").value)||220,email:(document.getElementById("xe").value||"").trim().toLowerCase()||_emailFromName(n)})', 1)
# N4. Email field in the Edit person modal.
html = html.replace(
    '<h2>Edit person</h2><label>Name</label><input id="xn" value="${esc(m.name)}"><label>Role</label>',
    '<h2>Edit person</h2><label>Name</label><input id="xn" value="${esc(m.name)}"><label>Email</label><input id="xe" type="email" value="${esc(m.email||_emailFromName(m.name))}"><label>Role</label>', 1)
html = html.replace(
    'function doEM(id){const m=S.m.find(x=>x.id===id);if(!m)return;m.name=document.getElementById("xn").value;',
    'function doEM(id){const m=S.m.find(x=>x.id===id);if(!m)return;m.name=document.getElementById("xn").value;m.email=(document.getElementById("xe").value||"").trim().toLowerCase()||_emailFromName(m.name);', 1)

# ── P0. Spell the units and the "sellable" label out in full ──
html = html.replace(' (d)', ' (days)')
html = html.replace('Sellable (days)', 'Sellable capacity (days)')
html = html.replace("['Sellable','capacity x the billability target of each Price Level']",
                    "['Sellable capacity','capacity x the billability target: the days that can realistically be billed to clients']")
html = html.replace("['Sellable','capacity x target, the days that can actually be sold']",
                    "['Sellable capacity','capacity x target: the days that can realistically be billed to clients']")

# ── P3. Load the billability targets wherever people/projects are read ──
LOAD_ANCHOR = 'if(d?.m&&d?.p){S.m=d.m;S.p=d.p;try{_migrateTeam();}catch(e){}}'
assert html.count(LOAD_ANCHOR) == 2, 'unexpected load sites: %d' % html.count(LOAD_ANCHOR)
html = html.replace(LOAD_ANCHOR, LOAD_ANCHOR + 'if(d&&d.t)S.t=Object.assign({},DEFT,d.t);')
LIVE_ANCHOR = 'if(d?.m&&d?.p){S.m=d.m;S.p=d.p;try{_migrateTeam();}catch(e){}R()}'
assert LIVE_ANCHOR in html, 'realtime load site not found'
html = html.replace(LIVE_ANCHOR,
                    'if(d?.m&&d?.p){S.m=d.m;S.p=d.p;try{_migrateTeam();}catch(e){}}'
                    'if(d&&d.t)S.t=Object.assign({},DEFT,d.t);R()', 1)

with io.open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)
print('OK', len(html), 'chars written')
