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
    ".perbar{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:14px;padding:10px 12px;background:#f2f4f7;border:1px solid var(--bd);border-radius:10px;font-size:12px;color:var(--t2)}"
    ".perbar>span:first-child{font-weight:700;color:#15171c;text-transform:uppercase;letter-spacing:.04em;font-size:11px}"
    ".perbtn{padding:5px 12px;border-radius:7px;border:1px solid var(--bd);background:#fff;color:var(--t2);font-family:inherit;font-size:12px;cursor:pointer}"
    ".perbtn:hover{border-color:#185fa5;color:#185fa5}"
    ".perbtn.on{background:#185fa5;border-color:#185fa5;color:#fff;font-weight:600}"
    ".perinfo{margin-left:auto;font-size:11px;color:var(--t3)}"
    ".wkchip{display:inline-flex;align-items:center;gap:5px;padding:5px 11px;border-radius:20px;background:#e6f1fb;color:#185fa5;font-size:12px;font-weight:600;white-space:nowrap}"
    ".wkbanner{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin:12px 24px 0;padding:11px 16px;background:#fff8e6;border:1px solid #f0d9a8;border-radius:10px;font-size:13px;color:#6b4c05}"
    ".wkbanner .b{margin-left:auto}"
    ".weekhead{display:flex;justify-content:space-between;align-items:flex-start;gap:20px;flex-wrap:wrap;margin-bottom:18px}"
    ".wh-t{font-size:20px;font-weight:700;color:#15171c;letter-spacing:-.01em}"
    ".wh-s{font-size:13px;color:var(--t2);margin-top:4px}"
    ".wh-b{min-width:210px}"
    ".wh-pct{font-size:26px;font-weight:700;text-align:right;line-height:1;font-variant-numeric:tabular-nums}"
    ".wh-bar{height:8px;background:#e9e8e2;border-radius:4px;overflow:hidden;margin:7px 0 5px}"
    ".wh-bar>div{height:100%;border-radius:4px;transition:width .3s}"
    ".wh-left{font-size:11.5px;color:var(--t2);text-align:right}"
    ".mywk td{vertical-align:middle}"
    ".wkin{width:70px;font-size:14px;font-weight:700;text-align:right;padding:6px 8px}"
    ".nbtag{font-size:9px;font-weight:700;color:var(--t3);border:1px solid var(--bd);border-radius:4px;padding:1px 4px}"
    ".wk-foot{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-top:18px;padding-top:14px;border-top:1px solid var(--bd)}"
    ".wk-ok{font-size:13px;font-weight:600;color:#2f6e12}"
    ".wk-hint{font-size:12px;color:var(--t3)}"
    ".wk-link{margin-left:auto;font-size:12.5px;color:#185fa5;cursor:pointer}"
    ".wk-link:hover{text-decoration:underline}"
    ".tgtrow{display:flex;gap:10px;flex-wrap:wrap}"
    ".tgtbox{flex:1;min-width:190px;display:flex;flex-direction:column;gap:3px;background:#f8f9fb;border:1px solid var(--bd);border-radius:10px;padding:11px 13px}"
    ".tgtbox>span:first-child{font-weight:700;font-size:12px;color:#15171c}"
    ".tgtin{display:flex;align-items:center;gap:5px;margin-top:4px;font-size:13px;color:var(--t2)}"
    ".tgtin input{width:70px;padding:6px 8px;border:1px solid var(--bd);border-radius:7px;background:#fff;color:var(--tx);font-family:inherit;font-size:14px;font-weight:700;text-align:right}"
    ".tgtin input:focus{outline:none;border-color:#185fa5}"
    # "i" help badge with a tooltip on hover / focus / tap
    ".ihelp{display:inline-flex;align-items:center;justify-content:center;width:14px;height:14px;margin-left:5px;border-radius:50%;background:#d7dde5;color:#42454c;font-size:9px;font-weight:800;font-style:italic;cursor:help;vertical-align:middle;position:relative;text-transform:none;letter-spacing:0;user-select:none}"
    ".ihelp:hover,.ihelp:focus{background:#185fa5;color:#fff;outline:none}"
    ".ihelp::after{content:attr(data-tip);position:absolute;bottom:calc(100% + 8px);left:50%;transform:translateX(-50%);width:270px;background:#15171c;color:#fff;font-size:11.5px;font-weight:400;font-style:normal;line-height:1.5;letter-spacing:0;text-align:left;text-transform:none;padding:9px 11px;border-radius:8px;box-shadow:0 6px 20px rgba(0,0,0,.22);opacity:0;visibility:hidden;transition:opacity .12s;z-index:60;pointer-events:none;white-space:normal}"
    ".ihelp::before{content:'';position:absolute;bottom:calc(100% + 2px);left:50%;transform:translateX(-50%);border:6px solid transparent;border-top-color:#15171c;opacity:0;visibility:hidden;transition:opacity .12s;z-index:61}"
    ".ihelp:hover::after,.ihelp:focus::after,.ihelp:hover::before,.ihelp:focus::before{opacity:1;visibility:visible}"
    ".utbl th .ihelp::after{width:250px}"
    ".utbl th:last-child .ihelp::after,.ametric:last-child .ihelp::after{left:auto;right:-6px;transform:none}"
    ".utbl th:last-child .ihelp::before,.ametric:last-child .ihelp::before{left:auto;right:4px;transform:none}"
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
const TABS=[["myweek","🗓 My week"],["team","👥 Team"],["projects","📁 Progetti"],["matrix","🔢 Matrice"],["assign","⚡️ Assegna"],["history","📅 History"]];
if(isAdmin())TABS.push(["admin","⚙️ Admin"]);
let h=`<div class="topnav"><div class="topnav-left"><span class="topnav-logo"><img class="brand-mark" src="jakala-logo.png" alt="JAKALA"><span>SEO Staffing Hub</span></span><div class="topnav-nav">${TABS.map(([k,l])=>`<a class="nav-item${S.vw===k?' active':''}" onclick="sw('${k}')">${l}</a>`).join('')}</div>${S.vw!=='admin'?`<input class="topsearch" placeholder="Cerca..." value="${esc(S.q)}" oninput="S.q=this.value;R()">`:''}</div><div class="topnav-right"><span class="wkchip" title="Every percentage you edit applies to this week">🗓 Week ${weekNo(S.wk)} · ${weekRange(S.wk)}</span>${_uHtml}</div></div>` + weekBanner();
h+=`<div class="ct">`;"""
html = html[:hstart] + new_header + html[hend:]

# I2. Route the new view (load Firestore data, then render)
assert 'function sw(v){S.vw=v;S.sm=null;S.sp=null;R()}' in html, 'sw() anchor not found'
html = html.replace('function sw(v){S.vw=v;S.sm=null;S.sp=null;R()}',
                    "function sw(v){S.vw=v;S.sm=null;S.sp=null;if(v==='admin'){uLoad();return;}R()}", 1)

# I3. Render the Admin view inside the content area (admins only; nothing for others)
anchor_ap = 'h+=`</div>`;document.getElementById("AP").innerHTML=h;'
assert anchor_ap in html, 'AP render anchor not found'
admin_branch = r"""if(S.vw==='myweek'){
h+='<div style="flex:1;min-width:0;max-width:920px;margin:0 auto;width:100%">'+renderMyWeek()+'</div>';
}
if(S.vw==='history'){
h+='<div style="flex:1;min-width:0;max-width:1100px;margin:0 auto;width:100%">'+renderHistory()+'</div>';
}
if(S.vw==='admin'&&isAdmin()){
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
function amCard(label,val,color,info){return '<div class="ametric"><div class="aml">'+label+(info?iHelp(info):'')+'</div><div class="amv"'+(color?(' style="color:'+color+'"'):'')+'>'+val+'</div></div>';}
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
  S.m.forEach(function(m){var r=rows[m.role];if(!r)return;var c=m.cap||220;var sh=periodShares(m.id);r.n++;r.cap+=c;r.bill+=sh.bill/100*c;r.nb+=sh.nb/100*c;});
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
// Admin figures read either the week being forecast or the average of the last N weeks.
function periodShares(mid){
  var per=S.aPer===undefined?1:S.aPer;
  if(per===1)return {bill:mEfBill(mid),nb:mEfNB(mid)};
  return avgShares(mid,per===0?0:per);
}
function periodLabel(){
  var per=S.aPer===undefined?1:S.aPer;
  return per===1?('current week ('+weekLabel(S.wk)+')'):per===0?'all recorded weeks':('last '+per+' weeks');
}
function periodPicker(){
  var per=S.aPer===undefined?1:S.aPer,ws=weeksAvailable().length,c=complianceOf(S.wk);
  return '<div class="perbar"><span>Period'+iHelp('period')+'</span>'
    +[[1,'Current week'],[4,'Last 4 weeks'],[12,'Last 12 weeks'],[0,'All weeks']].map(function(o){
        return '<button class="perbtn'+(per===o[0]?' on':'')+'" onclick="S.aPer='+o[0]+';R()">'+o[1]+'</button>';}).join('')
    +'<span class="perinfo">'+ws+' week'+(ws===1?'':'s')+' recorded · '+c.done+'/'+c.total+' people filled in '+weekLabel(S.wk)+'</span></div>';
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
  utilization:'Utilization rate = billable days the team reports divided by sellable capacity. It shows whether people report as much client work as their billability target expects. Above 100% they report more client work than planned, below 100% less.',
  sellable:'Sellable capacity = capacity x the billability target of the Price Level: the days that can realistically be billed to clients, once the time planned for internal work, management, presale, training and leave is set aside.',
  period:'Reported figures come from weekly forecasts: each person states how the coming week will be split. Over a period the weeks a person filled in are averaged, and that average is projected onto their yearly capacity. Weeks left empty are not counted as zero, they are simply missing, so coverage is shown next to the picker.',
  target:'Billability target = the share of the year a Price Level is expected to sell to clients. Editable in the Saturation view; it drives sellable capacity, utilization and saturation.',
  saturation:'Saturation = days quoted on projects for '+YEAR+' divided by sellable capacity, so it compares what has been sold with the time the team can realistically bill. Above 100% the level is oversold.'
};
function admNote(txt){return '<div class="admnote">'+txt+'</div>';}
// Small "i" that reveals a metric definition on hover, focus or tap.
function iHelp(key){var t=ADMDEF[key];if(!t)return '';return '<span class="ihelp" tabindex="0" role="button" aria-label="What is this?" data-tip="'+esc(t)+'">i</span>';}
function admLegend(items){return '<div class="admleg">'+items.map(function(x){return '<span><b>'+x[0]+'</b> '+x[1]+'</span>';}).join('')+'</div>';}
function renderAdmin(){
  var t=S.aTab||'overview';
  var h='<div class="admsub">'+admSub('overview','Overview')+admSub('perceived','Perceived')+admSub('billability','Billability')+admSub('utilization','Utilization')+admSub('saturation','Saturation')+admSub('people','People')+admSub('users','Users')+'</div>';
  // Reported figures are weekly forecasts, so every view built on them carries a period picker.
  if(['overview','perceived','billability','utilization','people'].indexOf(t)>=0)h+=periodPicker();
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
  var sat=tS?tQ/tS*100:0,gsat=tC?tQ/tC*100:0,util=tS?tB/tS*100:0,perc=tC?(tB+tNb)/tC*100:0;
  var h='<div class="ucard"><div class="uct">Overview '+YEAR+'</div><div class="ucs">Headcount, active projects and the four headline metrics for the year. Every figure is expressed in working days. Hover the i next to a metric for its definition.</div>'
   +'<div class="ametrics">'+amCard('People',tN,'')+amCard('Projects',D.nProjects,'')+amCard('Capacity (d)',_d0(tC),'','capacity')+amCard('Sellable (d)',_d0(tS),'','sellable')+amCard('Quoted '+YEAR+' (d)',_d0(tQ),'#185fa5','quoted')+'</div>'
   +'<div class="ametrics" style="margin-top:10px">'+amCard('Perceived',_p0(perc),sc(perc),'perceived')+amCard('Billable share',_p0(tB+tNb?tB/(tB+tNb)*100:0),'#185fa5','billability')+amCard('Utilization rate',_p0(util),sc(util),'utilization')+amCard('Real saturation',_p0(sat),sc(sat),'saturation')+'</div>'
   +admNote('Saturation is measured against sellable capacity; on gross capacity it would read '+_p0(gsat)+'.')+'</div>';
  h+='<div class="ucard"><div class="uct">By Price Level</div><div class="ucs">'+ADMDEF.capacity+' '+ADMDEF.quoted+'</div>'
   +'<table class="utbl"><thead><tr><th>Price Level</th><th>HR ranks</th><th class="r">People</th><th class="r">Capacity (d)'+iHelp('capacity')+'</th><th class="r">Target'+iHelp('target')+'</th><th class="r">Sellable (d)'+iHelp('sellable')+'</th><th class="r">Quoted '+YEAR+' (d)'+iHelp('quoted')+'</th><th class="r">Perceived'+iHelp('perceived')+'</th><th class="r">Utilization'+iHelp('utilization')+'</th><th class="r">Real saturation'+iHelp('saturation')+'</th></tr></thead><tbody>';
  PLkeys.forEach(function(k){
    var cap=D.plCap[k],sell=D.plSell[k],q=D.quoted[k],b=D.plBill[k],nb=D.plNb[k];
    var pe=cap?(b+nb)/cap*100:0,u=sell?b/sell*100:0,s=sell?q/sell*100:(q>0?999:0);
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
   +'<table class="utbl"><thead><tr><th>Price Level</th><th>HR ranks</th><th class="r">People</th><th class="r">Capacity (d)'+iHelp('capacity')+'</th><th class="r">Reported (d)</th><th class="r">Perceived'+iHelp('perceived')+'</th></tr></thead><tbody>';
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
   +'<table class="utbl"><thead><tr><th>Price Level</th><th>HR ranks</th><th class="r">People</th><th class="r">Reported (d)</th><th class="r">Billable (d)</th><th class="r">Non-billable (d)</th><th class="r">Billable share'+iHelp('billability')+'</th></tr></thead><tbody>';
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
// ── Utilization: billable days reported against sellable capacity ──
function admUtilization(){
  var D=admData(),tb=0,tc=0,ts=0,tN=0;
  var h='<div class="ucard"><div class="uct">Utilization rate</div><div class="ucs">'+ADMDEF.utilization+' '+ADMDEF.sellable+'</div>'
   +'<table class="utbl"><thead><tr><th>Price Level</th><th class="r">People</th><th class="r">Capacity (d)'+iHelp('capacity')+'</th><th class="r">Target'+iHelp('target')+'</th><th class="r">Sellable (d)'+iHelp('sellable')+'</th><th class="r">Billable reported (d)</th><th class="r">Utilization rate'+iHelp('utilization')+'</th></tr></thead><tbody>';
  PLkeys.forEach(function(k){
    var cap=D.plCap[k],sell=D.plSell[k],b=D.plBill[k],u=sell?b/sell*100:0;
    tb+=b;tc+=cap;ts+=sell;tN+=D.plN[k];
    h+='<tr><td><b>'+plLabel(k)+'</b><div style="font-size:10px;color:var(--t3);font-weight:400">'+esc(plRanksTxt(D,k))+'</div></td><td class="r">'+D.plN[k]+'</td><td class="r">'+_d0(cap)+'</td><td class="r">'+_p0(D.tgt[k])+'</td><td class="r">'+_d0(sell)+'</td><td class="r" style="color:#185fa5">'+_d0(b)+'</td><td class="r"><b style="color:'+sc(u)+'">'+_p0(u)+'</b>'+_bar(u,sc(u))+'</td></tr>';
  });
  h+='<tr class="tot"><td>Total</td><td class="r">'+tN+'</td><td class="r">'+_d0(tc)+'</td><td class="r">'+_p0(tc?ts/tc*100:0)+'</td><td class="r">'+_d0(ts)+'</td><td class="r">'+_d0(tb)+'</td><td class="r">'+_p0(ts?tb/ts*100:0)+'</td></tr></tbody></table>'
   +admLegend([['Sellable','capacity x the billability target'],['Billable reported','days on client projects, from the percentages people set'],['Utilization rate','billable reported / sellable capacity']])
   +admNote('100% means the team reports exactly the client work its targets expect. Below 100% part of the billable time is not showing up on projects; above 100% people report more client work than planned.')+'</div>';
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
   +'<table class="utbl"><thead><tr><th>Price Level</th><th class="r">People</th><th class="r">Capacity (d)'+iHelp('capacity')+'</th><th class="r">Target'+iHelp('target')+'</th><th class="r">Sellable (d)'+iHelp('sellable')+'</th><th class="r">Quoted '+YEAR+' (d)'+iHelp('quoted')+'</th><th class="r">Real saturation'+iHelp('saturation')+'</th><th class="r">On gross capacity</th></tr></thead><tbody>';
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
   +'<table class="utbl"><thead><tr><th>Price Level</th><th class="r">Quoted '+YEAR+' (d)'+iHelp('quoted')+'</th><th class="r">Billable reported (d)</th><th class="r">Difference</th></tr></thead><tbody>';
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
    var c=m.cap||220,ef=mEf(m.id),_sh=periodShares(m.id),eb=_sh.bill,enb=_sh.nb;
    return {m:m,cap:c,ef:ef,bill:eb/100*c,nb:enb/100*c,util:eb,alloc:Math.round(ef/100*c*10)/10,
            avail:100-ef,pc:S.p.filter(function(p){return p.asgn&&p.asgn[m.id]>0&&!p.nb;}).length,status:sl(ef)};
  }).sort(function(a,b){return b.util-a.util;});
  // distance from each person's own billability target
  var below=[],above=[],onTgt=0;
  rows.forEach(function(x){
    var t=tgtOf('PL'+rPL(x.m.role)),tgtD=x.cap*t/100,gap=x.bill-tgtD,gp=x.cap?gap/x.cap*100:0;
    x.tgt=t;x.tgtD=tgtD;x.gap=gap;x.gp=gp;
    if(gp<=-5)below.push(x);else if(gp>=5)above.push(x);else onTgt++;
  });
  var h='<div class="ucard"><div class="uct">Distance from the billability target</div><div class="ucs">'+ADMDEF.target+' Each person is measured against the target of their own Price Level: the gap is the billable days they report minus the days the target expects. People within 5 points of their target count as on track.</div>'
   +'<div class="ametrics">'+amCard('Below target',below.length,below.length?'#b32a1c':'')+amCard('On target (+/-5pp)',onTgt,'#2f6e12')+amCard('Above target',above.length,above.length?'#185fa5':'')+'</div>';
  function gapTable(list,title,note){
    if(!list.length)return '<div class="admnote" style="margin-top:16px"><b>'+title+':</b> nobody.</div>';
    var t='<div class="uct" style="font-size:14px;margin-top:20px">'+title+'</div><div class="ucs" style="margin-bottom:10px">'+note+'</div>'
     +'<table class="utbl"><thead><tr><th>Name</th><th>HR rank</th><th class="r">Capacity (days)</th><th class="r">Target'+iHelp('target')+'</th><th class="r">Target (days)</th><th class="r">Billable reported (days)</th><th class="r">Gap (days)</th><th class="r">Gap (pp)</th></tr></thead><tbody>';
    list.sort(function(a,b){return Math.abs(b.gp)-Math.abs(a.gp);}).forEach(function(x){
      var col=x.gap<0?'#b32a1c':'#185fa5';
      t+='<tr><td style="font-weight:600">'+esc(x.m.name)+'</td><td style="color:'+(RC[x.m.role]||'#999')+';font-size:11px">'+esc(x.m.role)+'</td><td class="r">'+_d0(x.cap)+'</td><td class="r">'+_p0(x.tgt)+'</td><td class="r">'+_d0(x.tgtD)+'</td><td class="r">'+_d0(x.bill)+'</td><td class="r" style="color:'+col+'"><b>'+(x.gap>0?'+':'')+_d0(x.gap)+'</b></td><td class="r" style="color:'+col+'">'+(x.gp>0?'+':'')+_p0(x.gp)+'</td></tr>';
    });
    return t+'</tbody></table>';
  }
  h+=gapTable(below,'Below target','They report less client work than their target expects: either they are genuinely under-loaded, or billable work is not being recorded.');
  h+=gapTable(above,'Above target','They report more client work than their target expects, leaving little room for internal work, presale and training.');
  h+='</div>';
  h+='<div class="ucard"><div class="uct">People</div><div class="ucs">The same metrics for each team member: perceived load, billable split, utilization against their own target and how many projects they are on.</div>'
   +'<table class="utbl"><thead><tr><th>Name</th><th>HR rank</th><th class="r">Capacity (d)'+iHelp('capacity')+'</th><th class="r">Reported (d)</th><th class="r">Perceived'+iHelp('perceived')+'</th><th class="r">Billable (d)</th><th class="r">Non-bill. (d)</th><th class="r">Billable share'+iHelp('billability')+'</th><th class="r">Utilization'+iHelp('utilization')+'</th><th class="r">Projects</th><th>Status</th></tr></thead><tbody>';
  rows.forEach(function(x){
    var rep=x.bill+x.nb,pe=x.cap?rep/x.cap*100:0,bs=rep?x.bill/rep*100:0,ut=x.tgtD?x.bill/x.tgtD*100:0;
    h+='<tr><td style="font-weight:600">'+esc(x.m.name)+'</td><td style="color:'+(RC[x.m.role]||'#999')+';font-size:11px">'+esc(x.m.role)+'</td><td class="r">'+_d0(x.cap)+'</td><td class="r">'+_d0(rep)+'</td><td class="r" style="color:'+sc(pe)+'">'+_p0(pe)+'</td><td class="r" style="color:#185fa5">'+_d0(x.bill)+'</td><td class="r" style="color:var(--t3)">'+_d0(x.nb)+'</td><td class="r">'+_p0(bs)+'</td><td class="r"><b style="color:'+sc(ut)+'">'+_p0(ut)+'</b></td><td class="r">'+x.pc+'</td><td><span class="sb" style="background:'+sc(x.ef)+'18;color:'+sc(x.ef)+'">'+x.status+'</span></td></tr>';
  });
  return h+'</tbody></table>'
   +admLegend([['Capacity','the person\'s yearly working days'],['Reported','days from the percentages they set (billable + non-billable)'],['Perceived','reported days / capacity'],['Billable share','billable / reported days'],['Utilization','billable days / the days their own target expects'],['Status','load band based on the total percentage assigned']])+'</div>';
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

# ── W. Weekly forecasting: percentages describe the week ahead, are archived every
#       week and carried forward, so yearly figures come from the weekly average.
WEEK_JS = r"""
// ── Weekly forecast plumbing ──────────────────────────────────────────────
// A member fills in how the coming week will be split. On Friday the target
// moves to the next week: the forecast just closed is archived and the
// percentages are carried forward as the starting point.
function isoWeek(d){
  var t=new Date(Date.UTC(d.getFullYear(),d.getMonth(),d.getDate()));
  t.setUTCDate(t.getUTCDate()+4-(t.getUTCDay()||7));                 // Thursday of that week
  var y0=new Date(Date.UTC(t.getUTCFullYear(),0,1));
  var n=Math.ceil(((t-y0)/864e5+1)/7);
  return t.getUTCFullYear()+'-W'+(n<10?'0'+n:n);
}
// From Friday on, the forecast being edited is for the week ahead.
function targetWeek(now){
  var d=now||new Date(),day=d.getDay();                              // 0 Sun .. 6 Sat
  var fwd=new Date(d);
  if(day===0)fwd.setDate(d.getDate()+1);                             // Sunday -> next week
  else if(day>=5)fwd.setDate(d.getDate()+(8-day));                   // Fri/Sat -> next Monday
  return isoWeek(fwd);
}
function weekLabel(w){return w?w.replace('-W',' W'):'';}
// Monday..Sunday of an ISO week, written out: "Mon 6 - Sun 12 July".
var _MON=['January','February','March','April','May','June','July','August','September','October','November','December'];
var _DNAM=['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
function weekMonday(w){
  var m=/(\d{4})-W(\d{1,2})/.exec(w||'');if(!m)return null;
  var jan4=new Date(Date.UTC(+m[1],0,4));
  var mon=new Date(jan4);
  mon.setUTCDate(jan4.getUTCDate()-((jan4.getUTCDay()||7)-1)+(+m[2]-1)*7);
  return mon;
}
function weekRange(w,long){
  var mon=weekMonday(w);if(!mon)return '';
  var sun=new Date(mon);sun.setUTCDate(mon.getUTCDate()+6);
  var sameMonth=mon.getUTCMonth()===sun.getUTCMonth();
  var mm=_MON[mon.getUTCMonth()],sm=_MON[sun.getUTCMonth()];
  if(!long)return mon.getUTCDate()+(sameMonth?'':' '+mm.slice(0,3))+' - '+sun.getUTCDate()+' '+sm.slice(0,3);
  return _DNAM[mon.getUTCDay()]+' '+mon.getUTCDate()+(sameMonth?'':' '+mm)+' - '+_DNAM[sun.getUTCDay()]+' '+sun.getUTCDate()+' '+sm;
}
function weekNo(w){var m=/-W(\d{1,2})/.exec(w||'');return m?+m[1]:'';}
// A week counts as filled in only once the person has touched or confirmed it.
function weekTouched(mid,w){w=w||S.wk;return !!(S.touched&&S.touched[w]&&S.touched[w][mid]);}
function markTouched(mid,w){
  w=w||S.wk;if(!w||!mid)return;
  S.touched=S.touched||{};S.touched[w]=Object.assign({},S.touched[w]);
  S.touched[w][mid]=Date.now();
}
function confirmWeek(){
  var ids=isAdmin()?myResourceIds():myResourceIds();
  if(!ids.length)return;
  ids.forEach(function(id){markTouched(id);});
  sv();R();
}
function lastTouched(mid,w){
  var ts=S.touched&&S.touched[w||S.wk]&&S.touched[w||S.wk][mid];
  if(!ts)return null;
  var d=new Date(ts);
  return _DNAM[d.getDay()]+' '+d.getDate()+' '+_MON[d.getMonth()].slice(0,3);
}
function snapshotAlloc(){
  var snap={};
  S.p.forEach(function(p){
    if(!p.asgn)return;
    Object.keys(p.asgn).forEach(function(mid){
      if(p.asgn[mid]>0){(snap[mid]=snap[mid]||{})[p.id]=p.asgn[mid];}
    });
  });
  return snap;
}
// Close the week that just ended and keep its percentages as the new starting point.
function rollWeek(){
  var cur=targetWeek();
  if(!S.wk){S.wk=cur;return false;}
  if(S.wk===cur)return false;
  S.hist=S.hist||{};
  S.hist[S.wk]=snapshotAlloc();
  S.wk=cur;
  return true;
}
// Percentages a person had on a given week (falls back to the live forecast).
function allocOfWeek(mid,w){
  if(!w||w===S.wk){var cur={};S.p.forEach(function(p){if(p.asgn&&p.asgn[mid]>0)cur[p.id]=p.asgn[mid];});return cur;}
  return (S.hist&&S.hist[w]&&S.hist[w][mid])||{};
}
function weeksAvailable(){
  var ws=Object.keys(S.hist||{});
  if(S.wk&&ws.indexOf(S.wk)<0)ws.push(S.wk);
  return ws.sort();
}
// Average billable / non-billable share over the last n weeks (0 = every week).
function avgShares(mid,n){
  var ws=weeksAvailable();
  if(n>0)ws=ws.slice(-n);
  if(!ws.length)return {bill:0,nb:0,weeks:0,filled:0};
  var b=0,nb=0,filled=0;
  ws.forEach(function(w){
    var a=allocOfWeek(mid,w),wb=0,wn=0,any=false;
    Object.keys(a).forEach(function(pid){
      var p=S.p.find(function(x){return x.id===pid;});
      if(!p)return;
      any=true;
      if(p.nb)wn+=a[pid];else wb+=a[pid];
    });
    if(any){filled++;b+=wb;nb+=wn;}
  });
  // Average over the weeks the person actually filled in: a missing week is not
  // zero effort, it is no data, and counting it as zero would understate everyone
  // who joined later or skipped an update. Coverage is reported separately.
  return {bill:filled?b/filled:0,nb:filled?nb/filled:0,weeks:ws.length,filled:filled};
}
// How many people filled in the current week.
function complianceOf(w){
  var done=0;
  S.m.forEach(function(m){if(weekTouched(m.id,w))done++;});
  return {done:done,total:S.m.length};
}
// Edit a past week: a forecast can be corrected once reality disagreed with it.
function setWeekE(mid,w,pid,val){
  var pct=parseFloat(val)||0;
  if(w===S.wk){setE(pid,mid,pct);return;}
  if(!(isAdmin()||myResourceIds().indexOf(mid)>=0))return;
  S.hist=S.hist||{};S.hist[w]=S.hist[w]||{};S.hist[w][mid]=Object.assign({},S.hist[w][mid]);
  var mine=S.hist[w][mid],other=0;
  Object.keys(mine).forEach(function(k){if(k!==pid)other+=mine[k];});
  if(pct+other>100){
    var room=Math.max(100-other,0);
    alert('Percentages split that week, so they add up to 100%.\n\nAssigned elsewhere that week: '+other.toFixed(0)+'%\nStill free: '+room.toFixed(0)+'%');
    pct=room;
  }
  if(pct>0)mine[pid]=Math.round(pct*10)/10;else delete mine[pid];
  if(!Object.keys(mine).length)delete S.hist[w][mid];else S.hist[w][mid]=mine;
  sv();R();
}
// ── My week: where everyone, admins included, files the forecast for the week ahead ──
function renderMyWeek(){
  var ids=myResourceIds(),mid=ids[0];
  if(!mid)return '<div class="ucard"><div class="uct">My week</div><div class="ucs">Your account is not linked to a team member yet, so there is nothing to fill in. An administrator can align your name or email in the Team tab.</div></div>';
  var me=S.m.find(function(x){return x.id===mid;})||{};
  var mine=S.p.filter(function(p){return p.asgn&&p.asgn[mid]>0;})
              .sort(function(a,b){return (b.asgn[mid]||0)-(a.asgn[mid]||0);});
  var used=mine.reduce(function(t,p){return t+(p.asgn[mid]||0);},0);
  var left=Math.max(100-used,0);
  var done=weekTouched(mid),ts=lastTouched(mid);
  var col=used>100?'#b32a1c':used===100?'#2f6e12':'#8a5a0c';
  var h='<div class="ucard"><div class="weekhead">'
   +'<div><div class="wh-t">Your forecast for <b>'+weekRange(S.wk,true)+'</b></div>'
   +'<div class="wh-s">Week '+weekNo(S.wk)+' · how will you split your time? The total has to reach 100%.</div></div>'
   +'<div class="wh-b"><div class="wh-pct" style="color:'+col+'">'+used.toFixed(0)+'%</div>'
   +'<div class="wh-bar"><div style="width:'+Math.min(used,100)+'%;background:'+col+'"></div></div>'
   +'<div class="wh-left">'+(used>100?'over by '+(used-100).toFixed(0)+'%':left>0?left.toFixed(0)+'% still free':'fully assigned')+'</div></div></div>';
  h+='<table class="utbl mywk"><thead><tr><th>Project</th><th class="r" style="width:130px">Share of the week</th><th style="width:40px"></th></tr></thead><tbody>';
  mine.forEach(function(p){
    var v=p.asgn[mid]||0;
    h+='<tr><td><div style="font-weight:600">'+(p.nb?'<span class="nbtag">NB</span> ':'')+esc(p.client||p.name)+'</div>'
      +'<div style="font-size:10px;color:var(--t3)">'+esc(p.name)+'</div></td>'
      +'<td class="r"><input class="pi wkin" type="number" min="0" max="100" step="5" value="'+v+'" onchange="setE(\''+p.id+'\',\''+mid+'\',parseFloat(this.value)||0)"> %</td>'
      +'<td class="r"><button class="rb" onclick="rmE(\''+p.id+'\',\''+mid+'\')">×</button></td></tr>';
  });
  h+='<tr class="tot"><td>Total</td><td class="r" style="color:'+col+'">'+used.toFixed(0)+'%</td><td></td></tr>';
  h+='</tbody></table>';
  // add a project
  var avail=S.p.filter(function(p){return !(p.asgn&&p.asgn[mid]>0);})
               .sort(function(a,b){return (a.nb?-1:0)-(b.nb?-1:0)||b.totalDays-a.totalDays;}).slice(0,40);
  h+='<div class="psc" style="margin-top:16px">Add a project</div><div class="ac">'
   +avail.map(function(p){return '<span class="ach" onclick="setE(\''+p.id+'\',\''+mid+'\','+Math.min(left||5,10)+')">+ '+esc(p.client||p.name)+'</span>';}).join('')
   +'</div>';
  h+='<div class="wk-foot">'
   +(done?'<span class="wk-ok">Filed'+(ts?' on '+ts:'')+'</span>':'<button class="b bg" onclick="confirmWeek()">Confirm this week</button><span class="wk-hint">Nothing to change? Confirm so the week counts as filed.</span>')
   +'<a class="wk-link" onclick="sw(\'history\')">See previous weeks</a></div>';
  return h+'</div>';
}
// Reminder shown on every page until the current week is filed.
function weekBanner(){
  var mid=myResourceIds()[0];
  if(!mid||weekTouched(mid))return '';
  return '<div class="wkbanner">Your forecast for <b>'+weekRange(S.wk,true)+'</b> has not been filed yet.'
    +'<button class="b bg" onclick="sw(\'myweek\')">Fill it in</button></div>';
}
function histPerson(){
  if(isAdmin())return S.hSel||(myResourceIds()[0])||(S.m[0]&&S.m[0].id);
  return myResourceIds()[0]||null;
}
// ── History view: the weeks a person forecast, and the room to correct them ──
function renderHistory(){
  var mid=histPerson();
  if(!mid)return '<div class="ucard"><div class="uct">History</div><div class="ucs">Your account is not linked to a team member yet, so there is no forecast history to show. An administrator can align your name or email in the Team tab.</div></div>';
  var me=S.m.find(function(x){return x.id===mid;})||{};
  var ws=weeksAvailable().slice(-10).reverse();
  var editable=isAdmin()||myResourceIds().indexOf(mid)>=0;
  // every project this person touched over the shown weeks
  var pids=[];
  ws.forEach(function(w){Object.keys(allocOfWeek(mid,w)).forEach(function(pid){if(pids.indexOf(pid)<0)pids.push(pid);});});
  var picker=isAdmin()?'<select class="si" style="width:220px" onchange="S.hSel=this.value;R()">'+S.m.slice().sort(function(a,b){return a.name.localeCompare(b.name);}).map(function(m){return '<option value="'+m.id+'"'+(m.id===mid?' selected':'')+'>'+esc(m.name)+'</option>';}).join('')+'</select>':'';
  var h='<div class="ucard"><div class="uct">Forecast history</div><div class="ucs">Percentages describe how a week is split, filled in for the week ahead. '+(editable?'You can correct a past week when reality turned out differently: totals stay capped at 100%.':'Read only: you can correct your own weeks.')+'</div>'
   +(picker?'<div style="margin-bottom:12px">'+picker+'</div>':'')
   +'<div style="font-size:13px;color:var(--t2);margin-bottom:10px"><b style="color:#15171c">'+esc(me.name||'')+'</b> · '+esc(me.role||'')+' · current week <b>'+weekLabel(S.wk)+'</b></div>';
  if(!pids.length)return h+'<div class="admnote">No forecast recorded yet.</div></div>';
  h+='<div style="overflow-x:auto"><table class="utbl"><thead><tr><th style="min-width:220px">Project</th>'
   +ws.map(function(w){return '<th class="r">'+weekLabel(w)+(w===S.wk?' <span style="font-size:9px;color:#185fa5">now</span>':'')+'</th>';}).join('')+'</tr></thead><tbody>';
  pids.forEach(function(pid){
    var p=S.p.find(function(x){return x.id===pid;});if(!p)return;
    h+='<tr><td><div style="font-weight:600">'+(p.nb?'<span style="font-size:9px;color:var(--t3)">NB </span>':'')+esc(p.client||p.name)+'</div><div style="font-size:10px;color:var(--t3)">'+esc(p.name)+'</div></td>';
    ws.forEach(function(w){
      var v=allocOfWeek(mid,w)[pid]||0;
      h+='<td class="r">'+(editable
        ? '<input class="pi" type="number" min="0" max="100" step="5" value="'+v+'" onchange="setWeekE(\''+mid+'\',\''+w+'\',\''+pid+'\',this.value)">'
        : (v?v+'%':'<span style="color:var(--t3)">-</span>'))+'</td>';
    });
    h+='</tr>';
  });
  h+='<tr class="tot"><td>Total</td>'+ws.map(function(w){
    var a=allocOfWeek(mid,w),t=0;Object.keys(a).forEach(function(k){t+=a[k];});
    return '<td class="r" style="color:'+(t>100?'#b32a1c':t<100?'#8a5a0c':'#2f6e12')+'">'+t.toFixed(0)+'%</td>';
  }).join('')+'</tr>';
  return h+'</tbody></table></div>'
   +admNote('A week that adds up to less than 100% means part of that time was never assigned.')+'</div>';
}
"""
html = html.replace('function mEf(mid){', WEEK_JS + '\nfunction mEf(mid){', 1)

# State + persistence for the weekly archive
# targetWeek() is a hoisted function declaration, so the current week is known even
# before anything is loaded from Firebase.
html = html.replace('let S={m:JSON.parse(JSON.stringify(IM)),p:JSON.parse(JSON.stringify(IP)),',
                    'let S={m:JSON.parse(JSON.stringify(IM)),p:JSON.parse(JSON.stringify(IP)),wk:targetWeek(),hist:{},touched:{},', 1)

# ── P. Billability targets per Price Level (editable, shared through Firebase) ──
# P1. Defaults + state
html = html.replace('const PLkeys=',
                    'const DEFT={PL4:50,PL3:75,PL2:80,PL1:90};\nconst PLkeys=', 1)
html = html.replace('let S={m:JSON.parse(JSON.stringify(IM)),p:JSON.parse(JSON.stringify(IP)),',
                    'let S={m:JSON.parse(JSON.stringify(IM)),p:JSON.parse(JSON.stringify(IP)),t:Object.assign({},DEFT),', 1)
# P2. Persist them on save (loading is wired further down, once step N has run)
html = html.replace('dbRef.set({m:S.m,p:S.p})', 'dbRef.set({m:S.m,p:S.p,t:S.t,wk:S.wk,hist:S.hist,touched:S.touched||{}})', 1)
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

# ── Q. Percentages are a split of a person's own year, so they cannot exceed 100%.
#       The cap applies to everyone: to give a project more, take it off another one.
html = html.replace(
    'function setE(pid,mid,pct){if(!canEditProjectId(pid))return;const p=S.p.find(x=>x.id===pid);if(!p)return;if(!p.asgn)p.asgn={};const cur=p.asgn[mid]||0;const totO=mEf(mid)-cur;'
    'if(pct+totO>100&&pct>cur){const ok=confirm(`Warning: total effort will be ${(pct+totO).toFixed(0)}% (over 100%).\\nThe overload will be highlighted. Proceed?`);if(!ok)return}',
    'function setE(pid,mid,pct){if(!canEditProjectId(pid))return;const p=S.p.find(x=>x.id===pid);if(!p)return;if(!p.asgn)p.asgn={};const cur=p.asgn[mid]||0;const totO=mEf(mid)-cur;'
    'const mm=S.m.find(x=>x.id===mid);const capD=(mm&&mm.cap)||220;'
    'if(pct+totO>100){const room=Math.max(100-totO,0);'
    'alert("Percentages split your own year, so they add up to 100%.\\n\\n'
    'Assigned elsewhere: "+totO.toFixed(0)+"% ("+(totO/100*capD).toFixed(0)+" of "+capD+" days)\\n'
    'Still free: "+room.toFixed(0)+"% ("+(room/100*capD).toFixed(0)+" days)\\n\\n'
    'To give this project more, lower another one first.");'
    'pct=room;if(pct<=0){delete p.asgn[mid];sv();R();return}}', 1)

# Person panel: the effort/billability summary is an admin-only read. Members get
# the project list to fill in, without a load figure for themselves or anyone else.
PANEL_SUMMARY = ('<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px"><span style="font-size:11px;color:var(--t2)">Total effort:</span>'
                 '<span style="font-family:var(--mn);font-size:16px;font-weight:700;color:${efC}">${ef.toFixed(0)}%</span>'
                 '<span style="font-size:10px;color:var(--t3)">· ${d} d · Avail: ${(100-ef).toFixed(0)}%</span></div>\n'
                 '<div style="display:flex;gap:12px;font-size:10px;margin-bottom:8px"><span style="color:var(--a2)">Billable: <b>${eb.toFixed(0)}%</b></span>'
                 '<span style="color:var(--t3)">Non bill.: <b>${enb.toFixed(0)}%</b></span></div>')
assert PANEL_SUMMARY in html, 'person panel summary not found'
html = html.replace(PANEL_SUMMARY, '${isAdmin()?`' + PANEL_SUMMARY + '`:``}', 1)

# Person panel rows carry the percentage weight only, no day conversion.
PERSON_ROW_DAYS = '<span style="font-family:var(--mn);font-size:9px;color:var(--a2)">${de.toFixed(0)}d</span>'
assert PERSON_ROW_DAYS in html, 'person panel day span not found'
html = html.replace(PERSON_ROW_DAYS, '', 1)

# Same rule everywhere else a per-person load figure is on screen.
# Assign > by person: hide the load badge and the effort bar in the people list.
ASSIGN_BADGE = ('<span class="sb" style="background:${sc(ef)}18;color:${sc(ef)};font-size:8px">${sl(ef)}</span>')
assert ASSIGN_BADGE in html, 'assign person badge not found'
html = html.replace(ASSIGN_BADGE, '${isAdmin()?`' + ASSIGN_BADGE + '`:``}', 1)
# Assign > candidate rows (both the per-Price-Level list and the "Other" list):
# hide "Effort: x%" and the availability figure.
CAND_EFFORT = '<br><span>Effort: ${ef.toFixed(0)}%</span>'
CAND_AVAIL = '<div class="cavail" style="color:${sc(ef)}">${av.toFixed(0)}%</div>'
assert html.count(CAND_EFFORT) == 2, 'candidate effort spans: %d' % html.count(CAND_EFFORT)
assert html.count(CAND_AVAIL) == 2, 'candidate avail cells: %d' % html.count(CAND_AVAIL)
html = html.replace(CAND_EFFORT, '${isAdmin()?`' + CAND_EFFORT + '`:``}')
html = html.replace(CAND_AVAIL, '${isAdmin()?`' + CAND_AVAIL + '`:``}')
# Matrix: the closing "TOTAL EFFORT" row is a per-person load ranking.
MATRIX_TOTAL = ('h+=`<tr><td class="sc" style="padding:6px 8px;border-top:2px solid var(--bh);font-weight:700;font-size:10px;color:var(--t2);text-align:left">TOTAL EFFORT</td>`;\n'
                'mm.forEach(m=>{const ef=mEf(m.id);h+=`<td style="border-top:2px solid var(--bh);text-align:center;font-family:var(--mn);font-size:9px;font-weight:700;color:${sc(ef)}">${ef.toFixed(0)}%</td>`});\n'
                'h+=`</tr>')
assert MATRIX_TOTAL in html, 'matrix total row not found'
html = html.replace(MATRIX_TOTAL, 'if(isAdmin()){' + MATRIX_TOTAL + '`;}\nh+=`', 1)

# Editing a percentage anywhere (My week, Team panel, project panel, matrix) files the week.
MARK_TOUCHED = 'else delete p.asgn[mid];sv();R()}'
assert MARK_TOUCHED in html, 'setE tail not found'
html = html.replace(MARK_TOUCHED, 'else delete p.asgn[mid];try{markTouched(mid);}catch(e){}sv();R()}', 1)

# Team tab: drop the per-person load columns (with the cap in place they are always
# 100% and invite comparison). Keep the roster: name, role, capacity, projects.
TEAM_TH_EFFORT = ('<th${ts.col===\'ef\'?\' class="sorted"\':\'\'}><div class="thw" ${thH(\'t\',\'ef\')}>Total effort ${arrI(\'t\',\'ef\')}</div>'
                  '<div class="flt"><select onchange="S.tFlt.status=this.value;R()" onclick="event.stopPropagation()"><option value="">All</option>'
                  '${statuses.map(s=>`<option value="${s}"${tf.status===s?\' selected\':\'\'}>${s}</option>`).join(\'\')}</select></div></th>')
assert TEAM_TH_EFFORT in html, 'team effort header not found'
html = html.replace(TEAM_TH_EFFORT,
                    '<th${ts.col===\'cap\'?\' class="sorted"\':\'\'}><div class="thw" ${thH(\'t\',\'cap\')}>Capacity (days) ${arrI(\'t\',\'cap\')}</div></th>', 1)
for th in ['<th${ts.col===\'eb\'?\' class="sorted"\':\'\'}><div class="thw" ${thH(\'t\',\'eb\')}>Billable ${arrI(\'t\',\'eb\')}</div></th>',
           '<th${ts.col===\'enb\'?\' class="sorted"\':\'\'}><div class="thw" ${thH(\'t\',\'enb\')}>Non-bill. ${arrI(\'t\',\'enb\')}</div></th>']:
    assert th in html, 'team header not found: %s' % th[:60]
    html = html.replace(th, '', 1)
TEAM_TD_LOAD = ('<td><div class="efb"><span class="epct" style="color:${c}">${m.ef.toFixed(0)}%</span><div class="efbr">'
                '<div class="f" style="width:${Math.min(m.ef/1.2,100)}%;background:${c}"></div>'
                '<div class="m" style="left:${100/1.2}%"></div></div></div></td>\n'
                '<td class="num" style="color:var(--a2)">${m.eb.toFixed(0)}%</td>\n'
                '<td class="num" style="color:var(--t3)">${m.enb.toFixed(0)}%</td>')
assert TEAM_TD_LOAD in html, 'team load cells not found'
html = html.replace(TEAM_TD_LOAD, '<td class="num">${m.cap}</td>', 1)

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
# Restore targets and the weekly archive, then close any week that has ended.
LOAD_EXTRA = ('if(d&&d.t)S.t=Object.assign({},DEFT,d.t);'
              'if(d){S.wk=d.wk||S.wk;S.hist=d.hist||S.hist||{};S.touched=d.touched||S.touched||{};}'
              'try{if(rollWeek())sv();}catch(e){}')
html = html.replace(LOAD_ANCHOR, LOAD_ANCHOR + LOAD_EXTRA)
LIVE_ANCHOR = 'if(d?.m&&d?.p){S.m=d.m;S.p=d.p;try{_migrateTeam();}catch(e){}R()}'
assert LIVE_ANCHOR in html, 'realtime load site not found'
html = html.replace(LIVE_ANCHOR,
                    'if(d?.m&&d?.p){S.m=d.m;S.p=d.p;try{_migrateTeam();}catch(e){}}'
                    'if(d&&d.t)S.t=Object.assign({},DEFT,d.t);'
                    'if(d){S.wk=d.wk||S.wk;S.hist=d.hist||S.hist||{};S.touched=d.touched||S.touched||{};}R()', 1)

with io.open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)
print('OK', len(html), 'chars written')
