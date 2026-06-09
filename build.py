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
    "#LS{background:#f5f4f0!important}"
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
      const profile={email:fu.email,displayName:autoName,role:isBoot?'admin':'member',active:true,createdAt:TS(),updatedAt:TS()};
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
new_h1 = ('let h=`<div class="hdr"><div><h1>'
          '<span style="color:var(--ac);font-weight:800;letter-spacing:-.02em">JAKALA</span> '
          '<span style="color:var(--t2);font-weight:400;font-size:13px">Staffing Hub</span></h1>')
html = html[:hi] + uhtml_decl + new_h1 + html[h1end + len('</h1>'):]

# Insert user chip into header actions
html = html.replace(
    '<div class="ha"><button class="b bo" onclick="rst()">',
    '<div class="ha">${_uHtml}<button class="b bo" onclick="rst()">',
    1,
)

with io.open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)
print('OK', len(html), 'chars written')
