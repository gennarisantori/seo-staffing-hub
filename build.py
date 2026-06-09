# -*- coding: utf-8 -*-
# Rebuilds index.html from _original.html:
#  - JAKALA blue palette
#  - Auth identical to SEO Quotation Hub (email/password, signup, reset,
#    @jakala.com gate, Firestore user profile + role, bootstrap admin)
#  - JAKALA branding + signed-in user display in header
import io, re

SRC = 'C:/Users/fgennari/Downloads/seo-staffing-hub/_original.html'
OUT = 'C:/Users/fgennari/Downloads/seo-staffing-hub/index.html'

with io.open(SRC, encoding='utf-8') as f:
    html = f.read()

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
)
html = html.replace('</style>', theme_css + '</style>', 1)

# ── I. ACCESS MANAGEMENT: "Utenti" tab + invite-based user activation (Quotation Hub model) ──

# I1. Add the nav tab
assert '["assign","⚡ Assegna"]]' in html, 'nav tabs anchor not found'
html = html.replace('["assign","⚡ Assegna"]]',
                    '["assign","⚡ Assegna"],["users","⚙ Utenti"]]', 1)

# I2. Route the new view (load Firestore data, then render)
assert 'function sw(v){S.vw=v;S.sm=null;S.sp=null;R()}' in html, 'sw() anchor not found'
html = html.replace('function sw(v){S.vw=v;S.sm=null;S.sp=null;R()}',
                    "function sw(v){S.vw=v;S.sm=null;S.sp=null;if(v==='users'){uLoad();return;}R()}", 1)

# I3. Render the view inside the content area
anchor_ap = 'h+=`</div>`;document.getElementById("AP").innerHTML=h;'
assert anchor_ap in html, 'AP render anchor not found'
html = html.replace(anchor_ap, "if(S.vw==='users'){h+=renderUsers();}\n" + anchor_ap, 1)

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
  return '<div style="flex:1;min-width:0;max-width:960px;margin:0 auto;width:100%">'
    +'<div class="ucard"><div class="uct">Email invitate (lista accessi)</div><div class="ucs">Solo le email invitate possono registrarsi e accedere. Scegli il ruolo al momento dell\'invito: la persona lo riceve al primo accesso. Poi condividi il link dell\'app: l\'invitato si registra impostando la propria password.</div>'+inviteForm+'<table class="utbl"><thead><tr><th>Email</th><th>Ruolo al primo accesso</th><th class="ctr">Azione</th></tr></thead><tbody>'+invRows+'</tbody></table></div>'
    +'<div class="ucard"><div class="uct">Utenti</div><div class="ucs">Gli utenti compaiono qui automaticamente dopo il primo accesso. Da qui puoi cambiarne il ruolo o disabilitarne l\'accesso.</div><table class="utbl"><thead><tr><th>Nome</th><th>Email</th><th>Ruolo</th><th>Stato</th><th class="ctr">Azioni</th></tr></thead><tbody>'+usrRows+'</tbody></table></div>'
    +(adm?'':'<div style="font-size:12px;color:var(--t3);text-align:center;margin-top:4px">Vista in sola lettura: solo gli amministratori possono invitare o modificare gli utenti.</div>')
    +'</div>';
}
function uDoInvite(){var e=(document.getElementById('u-email')||{}).value||'';var r=(document.getElementById('u-role')||{}).value||'member';if(!e.trim())return;uAddInvite(e,r).then(uLoad).catch(function(err){alert('Invito fallito: '+(err.message||err));});}
function uRmInvite(e){if(!confirm('Rimuovere l\'invito per '+e+'?'))return;uRemoveInvite(e).then(uLoad).catch(function(err){alert(err.message||err);});}
function uChgInviteRole(e,r){uSetInviteRole(e,r).then(uLoad).catch(function(err){alert(err.message||err);});}
function uChgUserRole(uid,r){uSetUserRole(uid,r).then(uLoad).catch(function(err){alert(err.message||err);});}
function uDisable(uid){uSetUserActive(uid,false).then(uLoad).catch(function(err){alert(err.message||err);});}
function uEnable(uid){uSetUserActive(uid,true).then(uLoad).catch(function(err){alert(err.message||err);});}
"""
cut = html.rindex('</script>')
html = html[:cut] + users_js + '\n' + html[cut:]

with io.open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)
print('OK', len(html), 'chars written')
