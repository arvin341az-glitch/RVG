# pages.py  -  RVG Gateway v9.2
# شامل: LOGIN_HTML, DASHBOARD_HTML, get_public_page_html()

LOGIN_HTML = r"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ورود · RVG Gateway</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.19.0/dist/tabler-icons.min.css">
<style>
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
:root{
  --bg:#080B14;--bg2:#0D1220;--card:rgba(13,18,32,0.86);--card-in:rgba(255,255,255,0.02);
  --accent:#4F6BFF;--accent2:#7C93FF;--signal:#2E8BFF;
  --text:#EEF2FF;--dim:#5A6690;--mid:#8B96C4;--border:rgba(124,147,255,0.16);
  --glow:rgba(79,107,255,.32);--glow-signal:rgba(46,139,255,.22);
  --danger:#FB7185;
}
[data-theme="light"]{
  --bg:#EEF1FA;--bg2:#E4E9F7;--card:rgba(255,255,255,0.88);--card-in:rgba(79,107,255,0.03);
  --accent:#3450E0;--accent2:#4F6BFF;--signal:#1465D8;
  --text:#111531;--dim:#7480AC;--mid:#4C5786;--border:rgba(52,80,224,0.14);
  --glow:rgba(52,80,224,.16);--glow-signal:rgba(20,101,216,.14);
}
html,body{height:100%;overflow:hidden}
body{
  font-family:'Vazirmatn',sans-serif;background:var(--bg);display:flex;align-items:center;justify-content:center;
  padding:20px;position:relative;transition:background .5s ease
}
.mono{font-family:'JetBrains Mono',ui-monospace,monospace}

/* ══════ پس‌زمینه ══════ */
.bg{position:fixed;inset:0;z-index:0;background:
  radial-gradient(ellipse 60% 46% at 18% 8%,var(--glow),transparent 68%),
  radial-gradient(ellipse 50% 40% at 88% 92%,var(--glow-signal),transparent 65%),
  var(--bg);transition:background .5s ease;animation:bgshift 14s ease-in-out infinite}
@keyframes bgshift{
  0%,100%{filter:hue-rotate(0deg) brightness(1)}
  50%{filter:hue-rotate(8deg) brightness(1.05)}
}
.grid{position:fixed;inset:0;z-index:0;background-image:
  linear-gradient(rgba(124,147,255,0.05) 1px,transparent 1px),
  linear-gradient(90deg,rgba(124,147,255,0.05) 1px,transparent 1px);
  background-size:44px 44px;
  mask-image:radial-gradient(ellipse 62% 62% at 50% 42%,black 25%,transparent 85%);
  animation:gridpan 30s linear infinite}
@keyframes gridpan{from{background-position:0 0}to{background-position:88px 88px}}

/* ذرات شناور — عنصر جدید */
.particles{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}
.particle{position:absolute;border-radius:50%;background:var(--signal);opacity:0;box-shadow:0 0 10px var(--signal);animation:floatp linear infinite}
@keyframes floatp{
  0%{transform:translateY(110vh) translateX(0) scale(.4);opacity:0}
  8%{opacity:.55}
  92%{opacity:.4}
  100%{transform:translateY(-10vh) translateX(var(--drift,40px)) scale(1);opacity:0}
}

/* مسیر سیگنال — عنصر امضادار: یک خط مسیر شبکه با پالس متحرک */
.route{position:fixed;inset:0;z-index:0;pointer-events:none;opacity:.55}
.route svg{width:100%;height:100%}
.route path{fill:none;stroke:var(--border);stroke-width:1;stroke-dasharray:2 7;stroke-linecap:round;animation:dashflow 6s linear infinite}
@keyframes dashflow{to{stroke-dashoffset:-90}}
.pulse-dot{filter:drop-shadow(0 0 6px var(--signal))}

/* ══════ سوییچ تم ══════ */
.theme-switch{position:fixed;top:22px;left:22px;z-index:50}
.theme-btn{
  width:42px;height:42px;border-radius:12px;background:var(--card);border:1px solid var(--border);
  color:var(--mid);display:flex;align-items:center;justify-content:center;font-size:18px;cursor:pointer;
  backdrop-filter:blur(16px);transition:all .25s cubic-bezier(.4,0,.2,1);position:relative;overflow:hidden
}
.theme-btn:hover{border-color:var(--accent);color:var(--accent2);transform:translateY(-2px)}
.theme-btn i{position:relative;z-index:1;transition:transform .45s cubic-bezier(.34,1.56,.64,1)}
.theme-btn.spin i{transform:rotate(300deg)}

/* نشان وضعیت برخط بودن گیت‌وی */
.status-badge{
  position:fixed;top:22px;right:22px;z-index:50;display:flex;align-items:center;gap:7px;
  background:var(--card);border:1px solid var(--border);border-radius:999px;padding:8px 14px 8px 12px;
  backdrop-filter:blur(16px);animation:badgein .6s cubic-bezier(.16,1,.3,1) .3s backwards
}
@keyframes badgein{from{opacity:0;transform:translateY(-10px)}to{opacity:1;transform:none}}
.status-dot{width:7px;height:7px;border-radius:50%;background:var(--signal);position:relative;flex-shrink:0}
.status-dot::after{content:'';position:absolute;inset:-4px;border-radius:50%;background:var(--signal);opacity:.4;animation:ping 1.8s cubic-bezier(0,0,.2,1) infinite}
@keyframes ping{0%{transform:scale(.6);opacity:.5}75%,100%{transform:scale(2.1);opacity:0}}
.status-badge span{font-size:10.5px;color:var(--mid);letter-spacing:.03em}

/* ══════ کارت ══════ */
.wrap{position:relative;z-index:10;width:100%;max-width:392px;animation:cardIn .65s cubic-bezier(.16,1,.3,1);perspective:900px}
@keyframes cardIn{from{opacity:0;transform:translateY(20px) scale(.975)}to{opacity:1;transform:none}}
.card{
  background:var(--card);border:1px solid var(--border);border-radius:20px;padding:38px 32px 30px;
  backdrop-filter:blur(30px);box-shadow:0 30px 80px -20px rgba(0,0,0,.55),0 0 0 1px var(--card-in) inset;
  position:relative;overflow:hidden;transition:transform .35s cubic-bezier(.16,1,.3,1),box-shadow .35s ease
}
.card:hover{box-shadow:0 34px 90px -18px rgba(0,0,0,.6),0 0 0 1px var(--card-in) inset,0 0 40px -6px var(--glow-signal)}
.card::before{
  content:'';position:absolute;top:0;left:16px;right:16px;height:1px;
  background:linear-gradient(90deg,transparent,var(--signal),transparent);
  animation:sheen 4s ease-in-out infinite
}
@keyframes sheen{0%,100%{opacity:.15;transform:translateX(-40%)}50%{opacity:.9;transform:translateX(40%)}}
/* حاشیه‌ی نور چرخان جدید */
.card::after{
  content:'';position:absolute;inset:-1px;border-radius:20px;padding:1px;z-index:-1;pointer-events:none;
  background:conic-gradient(from var(--ang,0deg),transparent 0%,var(--signal) 8%,transparent 22%,transparent 100%);
  -webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);
  -webkit-mask-composite:xor;mask-composite:exclude;opacity:.5;animation:rotang 5.5s linear infinite
}
@keyframes rotang{to{--ang:360deg}}
@property --ang{syntax:'<angle>';inherits:false;initial-value:0deg}

.brand{display:flex;align-items:center;gap:13px;margin-bottom:28px}
.brand-img{width:46px;height:46px;border-radius:13px;overflow:hidden;border:1px solid var(--border);flex-shrink:0;position:relative;box-shadow:0 0 0 4px var(--card-in);animation:brandpulse 3.2s ease-in-out infinite}
@keyframes brandpulse{0%,100%{box-shadow:0 0 0 4px var(--card-in)}50%{box-shadow:0 0 0 6px var(--glow-signal)}}
.brand-img img{width:100%;height:100%;object-fit:cover;display:block}
.brand-name{font-size:15.5px;font-weight:800;color:var(--text);letter-spacing:-.01em}
.brand-sub{font-size:10.5px;color:var(--dim);margin-top:3px;letter-spacing:.02em}
.brand-sub .mono{color:var(--signal);font-weight:600}

h1{font-size:21px;font-weight:800;color:var(--text);margin-bottom:5px;letter-spacing:-.02em;animation:fadeup .5s cubic-bezier(.16,1,.3,1) .1s backwards}
.sub{font-size:12.5px;color:var(--mid);margin-bottom:24px;line-height:1.7;animation:fadeup .5s cubic-bezier(.16,1,.3,1) .18s backwards}
@keyframes fadeup{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}

.hint{
  display:flex;align-items:center;gap:10px;background:var(--card-in);border:1px dashed var(--border);
  border-radius:12px;padding:10px 14px;margin-bottom:22px;animation:fadeup .5s cubic-bezier(.16,1,.3,1) .24s backwards
}
.hint i{color:var(--dim);font-size:15px}
.hint-label{font-size:11px;color:var(--dim);flex:1}
.hint-val{
  font-family:'JetBrains Mono',monospace;font-size:13px;font-weight:600;color:var(--signal);
  background:var(--glow-signal);border:1px solid rgba(46,139,255,0.3);padding:4px 11px;border-radius:7px;
  cursor:pointer;transition:.18s;letter-spacing:.06em
}
.hint-val:hover{filter:brightness(1.15);transform:translateY(-1px) scale(1.04)}
.hint-val:active{transform:translateY(0) scale(.96)}

.field{margin-bottom:18px;animation:fadeup .5s cubic-bezier(.16,1,.3,1) .3s backwards}
.field label{display:block;font-size:10.5px;font-weight:700;color:var(--mid);margin-bottom:8px;text-transform:uppercase;letter-spacing:.08em}
.inp-wrap{position:relative}
input[type=password],input[type=text]{
  width:100%;padding:13px 44px 13px 44px;border-radius:12px;border:1px solid var(--border);
  background:rgba(0,0,0,.18);color:var(--text);font-family:inherit;font-size:14.5px;outline:none;transition:.2s
}
[data-theme="light"] input[type=password],[data-theme="light"] input[type=text]{background:rgba(52,80,224,.035)}
input::placeholder{color:var(--dim)}
input:focus{border-color:var(--accent);background:rgba(79,107,255,.06);box-shadow:0 0 0 4px var(--glow)}
.ic-lock{position:absolute;right:15px;top:50%;transform:translateY(-50%);color:var(--dim);font-size:17px;pointer-events:none;transition:.2s}
input:focus~.ic-lock{color:var(--accent2);animation:wiggle .4s ease}
@keyframes wiggle{0%,100%{transform:translateY(-50%) rotate(0)}25%{transform:translateY(-50%) rotate(-12deg)}75%{transform:translateY(-50%) rotate(12deg)}}
.ic-eye{
  position:absolute;left:12px;top:50%;transform:translateY(-50%);color:var(--dim);font-size:17px;
  cursor:pointer;padding:6px;transition:.2s;line-height:0
}
.ic-eye:hover{color:var(--accent2);transform:translateY(-50%) scale(1.15)}

.err{display:none;background:rgba(251,113,133,.08);border:1px solid rgba(251,113,133,.25);border-radius:11px;padding:11px 14px;margin-bottom:16px;font-size:12.5px;color:var(--danger);align-items:center;gap:8px;animation:shake .35s}
.err.show{display:flex}
@keyframes shake{0%,100%{transform:translateX(0)}25%{transform:translateX(-6px)}75%{transform:translateX(6px)}}

.btn{
  width:100%;padding:13.5px;border-radius:12px;border:none;cursor:pointer;
  background:linear-gradient(135deg,var(--accent),var(--accent2),var(--signal));background-size:200% 200%;
  color:#fff;font-family:inherit;font-size:14.5px;font-weight:700;
  display:flex;align-items:center;justify-content:center;gap:9px;box-shadow:0 10px 26px -6px rgba(79,107,255,.55);
  transition:all .22s;position:relative;overflow:hidden;margin-top:6px;
  animation:btngrad 4s ease infinite,fadeup .5s cubic-bezier(.16,1,.3,1) .36s backwards
}
@keyframes btngrad{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}
.btn::before{content:'';position:absolute;inset:0;background:linear-gradient(120deg,transparent,rgba(255,255,255,.25),transparent);width:50%;transform:translateX(-160%)}
.btn:hover::before{animation:btnsheen 1s ease}
@keyframes btnsheen{to{transform:translateX(260%)}}
.btn:hover{transform:translateY(-2px);box-shadow:0 14px 32px -6px rgba(46,139,255,.65)}
.btn:active{transform:translateY(0) scale(.98)}
.btn:disabled{opacity:.55;cursor:not-allowed;transform:none;animation:btngrad 4s ease infinite}
.btn:focus-visible,input:focus-visible,.theme-btn:focus-visible,.hint-val:focus-visible{outline:2px solid var(--signal);outline-offset:2px}

.footer{margin-top:22px;padding-top:18px;border-top:1px solid var(--border);display:flex;align-items:center;justify-content:center;gap:8px;font-size:11.5px;color:var(--dim);animation:fadeup .5s cubic-bezier(.16,1,.3,1) .42s backwards}
.footer a{color:var(--accent2);font-weight:700;text-decoration:none;display:flex;align-items:center;gap:5px;transition:.18s}
.footer a:hover{filter:brightness(1.25);transform:translateY(-1px)}

@keyframes spin{to{transform:rotate(360deg)}}

@media (max-width:420px){
  .card{padding:30px 22px 24px;border-radius:18px}
  .status-badge span{display:none}
  .status-badge{padding:9px}
}
@media (prefers-reduced-motion:reduce){
  *{animation-duration:.001s !important;animation-iteration-count:1 !important}
}
</style>
</head>
<body>
<div class="bg"></div><div class="grid"></div>
<div class="particles" id="particles" aria-hidden="true"></div>
<div class="route" aria-hidden="true">
  <svg viewBox="0 0 1000 700" preserveAspectRatio="none">
    <path d="M -50 120 C 200 40, 350 220, 620 90 S 1050 40, 1100 130" />
    <path d="M -50 600 C 220 680, 420 480, 700 610 S 1000 700, 1080 560" />
    <circle class="pulse-dot" r="3" fill="var(--signal)">
      <animateMotion dur="7s" repeatCount="indefinite" path="M -50 120 C 200 40, 350 220, 620 90 S 1050 40, 1100 130" />
    </circle>
    <circle class="pulse-dot" r="2.4" fill="var(--accent2)">
      <animateMotion dur="9s" repeatCount="indefinite" path="M -50 600 C 220 680, 420 480, 700 610 S 1000 700, 1080 560" />
    </circle>
  </svg>
</div>

<div class="theme-switch">
  <button class="theme-btn" id="theme-btn" onclick="toggleTheme()" title="تغییر تم" aria-label="تغییر تم">
    <i class="ti ti-sun" id="theme-icon"></i>
  </button>
</div>
<div class="status-badge"><span class="status-dot"></span><span class="mono">GATEWAY ONLINE</span></div>

<div class="wrap" id="wrap">
  <div class="card" id="card">
    <div class="brand">
      <div class="brand-img"><img src="https://yt3.googleusercontent.com/vA6bYj1V386YmibpWRNFJtsRRqwfY_U9wnb7gmW90eRVXyNB7gAfjj1XPs5UX0cdKdQprrI=s160-c-k-c0x00ffffff-no-rj" alt="codebox"></div>
      <div><div class="brand-name">codebox</div><div class="brand-sub">RVG Gateway <span class="mono">· v9.2</span></div></div>
    </div>
    <h1>ورود به پنل</h1>
    <p class="sub">رمز عبور را برای دسترسی به داشبورد مدیریت وارد کنید</p>

    <div class="err" id="err" role="alert"><i class="ti ti-alert-circle"></i><span id="err-text"></span></div>

    <div class="hint">
      <i class="ti ti-info-circle"></i>
      <span class="hint-label">رمز پیش‌فرض سیستم</span>
      <span class="hint-val" tabindex="0" role="button" onclick="fillDefault()" onkeydown="if(event.key==='Enter')fillDefault()">123456</span>
    </div>

    <form id="form" novalidate>
      <div class="field">
        <label for="pw">رمز عبور</label>
        <div class="inp-wrap">
          <input type="password" id="pw" placeholder="رمز عبور را وارد کنید" autofocus required autocomplete="current-password">
          <i class="ti ti-lock ic-lock"></i>
          <i class="ti ti-eye ic-eye" id="eye-toggle" onclick="togglePw()" role="button" tabindex="0" aria-label="نمایش رمز عبور"></i>
        </div>
      </div>
      <button class="btn" type="submit" id="btn"><i class="ti ti-login-2"></i> ورود به داشبورد</button>
    </form>

    <div class="footer">کانال رسمی<a href="https://t.me/CodeBoxo" target="_blank" rel="noopener"><i class="ti ti-brand-telegram"></i>@CodeBoxo</a></div>
  </div>
</div>

<script>
/* ══════ تم روشن/تاریک ══════ */
let isDark = localStorage.getItem('rvg-login-theme') !== 'light';
function applyTheme(dark){
  document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
  document.getElementById('theme-icon').className = 'ti ' + (dark ? 'ti-sun' : 'ti-moon');
}
function toggleTheme(){
  isDark = !isDark;
  localStorage.setItem('rvg-login-theme', isDark ? 'dark' : 'light');
  const btn = document.getElementById('theme-btn');
  btn.classList.add('spin');
  setTimeout(()=>btn.classList.remove('spin'), 420);
  applyTheme(isDark);
}
applyTheme(isDark);

function fillDefault(){
  const pw = document.getElementById('pw');
  pw.value = '123456';
  pw.focus();
}

function togglePw(){
  const pw = document.getElementById('pw');
  const eye = document.getElementById('eye-toggle');
  const show = pw.type === 'password';
  pw.type = show ? 'text' : 'password';
  eye.className = 'ti ' + (show ? 'ti-eye-off' : 'ti-eye') + ' ic-eye';
}

/* ذرات شناور پس‌زمینه */
(function(){
  const box = document.getElementById('particles');
  const n = 22;
  for(let i=0;i<n;i++){
    const p = document.createElement('div');
    p.className = 'particle';
    const size = 2 + Math.random()*3;
    p.style.width = size+'px';
    p.style.height = size+'px';
    p.style.left = Math.random()*100+'vw';
    p.style.setProperty('--drift', (Math.random()*80-40)+'px');
    p.style.animationDuration = (10 + Math.random()*14)+'s';
    p.style.animationDelay = (Math.random()*14)+'s';
    box.appendChild(p);
  }
})();

/* افکت تیلت سه‌بعدی روی کارت با موس */
(function(){
  const wrap = document.getElementById('wrap');
  const card = document.getElementById('card');
  if(window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  if(window.matchMedia('(hover: none)').matches) return;
  wrap.addEventListener('mousemove', (e)=>{
    const r = wrap.getBoundingClientRect();
    const x = (e.clientX - r.left)/r.width - .5;
    const y = (e.clientY - r.top)/r.height - .5;
    card.style.transform = `rotateY(${x*6}deg) rotateX(${-y*6}deg) translateZ(0)`;
  });
  wrap.addEventListener('mouseleave', ()=>{
    card.style.transform = 'rotateY(0) rotateX(0)';
  });
})();

document.getElementById('form').addEventListener('submit', async e => {
  e.preventDefault();
  const btn = document.getElementById('btn'), err = document.getElementById('err'), et = document.getElementById('err-text');
  err.classList.remove('show'); btn.disabled = true;
  btn.innerHTML = '<i class="ti ti-loader-2" style="animation:spin 1s linear infinite"></i> در حال ورود...';
  try{
    const r = await fetch('/api/login', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({password: document.getElementById('pw').value})});
    if(!r.ok){ const d = await r.json().catch(()=>({})); throw new Error(d.detail || 'خطا در ورود'); }
    location.href = '/dashboard';
  }catch(e){
    et.textContent = e.message;
    err.classList.add('show');
    btn.disabled = false;
    btn.innerHTML = '<i class="ti ti-login-2"></i> ورود به داشبورد';
  }
});
</script>
</body></html>"""

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RVG Gateway · codebox</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.19.0/dist/tabler-icons.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#060f1d;--bg2:#0a1628;--bg3:#0e1e35;
  --card:#0d1b2e;--card-b:rgba(59,130,246,0.13);--card-bh:rgba(59,130,246,0.28);
  --accent:#3B82F6;--accent2:#60A5FA;--accent-d:rgba(59,130,246,0.12);
  --green:#10B981;--green-bg:rgba(16,185,129,0.1);--green-t:#34D399;
  --red:#EF4444;--red-bg:rgba(239,68,68,0.1);--red-t:#F87171;
  --amber:#F59E0B;--amber-bg:rgba(245,158,11,0.1);--amber-t:#FCD34D;
  --purple:#8B5CF6;--purple-bg:rgba(139,92,246,0.1);
  --t1:#E8F4FF;--t2:#7BAED4;--t3:#3D6B8E;
  --sidebar-w:248px;--radius:16px;
  --shadow:0 4px 24px rgba(0,0,0,0.35);
}
[data-theme="light"]{
  --bg:#F0F4FA;--bg2:#E4EDF9;--bg3:#D5E3F5;
  --card:#FFFFFF;--card-b:rgba(59,130,246,0.15);--card-bh:rgba(59,130,246,0.35);
  --accent:#2563EB;--accent2:#1D4ED8;--accent-d:rgba(37,99,235,0.08);
  --green:#059669;--green-bg:rgba(5,150,105,0.08);--green-t:#065F46;
  --red:#DC2626;--red-bg:rgba(220,38,38,0.08);--red-t:#991B1B;
  --amber:#D97706;--amber-bg:rgba(217,119,6,0.08);--amber-t:#92400E;
  --purple:#7C3AED;--purple-bg:rgba(124,58,237,0.08);
  --t1:#0F172A;--t2:#334155;--t3:#64748B;
  --shadow:0 4px 20px rgba(0,0,0,0.1);
}
html,body{height:100%}
body{font-family:'Vazirmatn',sans-serif;background:var(--bg);color:var(--t1);min-height:100vh;display:flex;font-size:14px;transition:background .3s,color .3s}
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--bg3);border-radius:3px}
a{color:inherit;text-decoration:none}
.sidebar{width:var(--sidebar-w);min-height:100vh;background:var(--bg2);border-left:1px solid var(--card-b);display:flex;flex-direction:column;flex-shrink:0;position:fixed;right:0;top:0;bottom:0;z-index:200;transition:transform .25s cubic-bezier(.4,0,.2,1),background .3s,border-color .3s}
.logo{display:flex;align-items:center;gap:12px;padding:20px 16px 16px;border-bottom:1px solid var(--card-b)}
.logo-img{width:38px;height:38px;border-radius:10px;overflow:hidden;border:1px solid var(--card-b);box-shadow:0 0 14px var(--accent-d);flex-shrink:0}
.logo-img img{width:100%;height:100%;object-fit:cover}
.logo-name{font-size:13.5px;font-weight:700;color:var(--t1)}
.logo-sub{font-size:10px;color:var(--t3);margin-top:1px}
.sb-close{display:none;position:absolute;left:12px;top:20px;background:var(--accent-d);border:1px solid var(--card-b);color:var(--t2);width:30px;height:30px;border-radius:8px;font-size:16px;align-items:center;justify-content:center;cursor:pointer}
.nav-wrap{flex:1;overflow-y:auto;padding:6px 0 8px}
.nav-sec{padding:14px 14px 4px;font-size:9px;letter-spacing:.14em;text-transform:uppercase;color:var(--t3);font-weight:700}
.nav-it{display:flex;align-items:center;gap:9px;padding:9px 14px;color:var(--t3);font-size:12.5px;cursor:pointer;border-right:2px solid transparent;transition:all .15s;margin:1px 6px}
.nav-it i{font-size:16px;width:18px;text-align:center;flex-shrink:0}
.nav-it:hover{background:var(--accent-d);color:var(--t2)}
.nav-it.on{background:var(--accent-d);color:var(--t1);border-right-color:var(--accent);font-weight:600}
.nav-badge{margin-right:auto;background:rgba(59,130,246,0.15);color:var(--accent2);font-size:9px;padding:1px 6px;border-radius:20px;font-weight:700}
.sb-foot{padding:12px 14px;border-top:1px solid var(--card-b)}
.tg-btn{display:flex;align-items:center;justify-content:center;gap:8px;background:linear-gradient(135deg,#0098e6,#0077bb);color:#fff;border-radius:9px;padding:10px;font-size:12.5px;font-weight:600;font-family:inherit;border:none;cursor:pointer;width:100%;transition:.15s}
.tg-btn:hover{filter:brightness(1.1)}
.theme-btn{display:flex;align-items:center;justify-content:center;gap:7px;background:var(--accent-d);color:var(--t2);border-radius:9px;padding:8px;font-size:12px;font-weight:500;font-family:inherit;border:1px solid var(--card-b);cursor:pointer;width:100%;transition:.15s;margin-bottom:7px}
.theme-btn:hover{background:var(--card-b);color:var(--t1)}
.logout-btn{display:flex;align-items:center;justify-content:center;gap:7px;background:var(--red-bg);color:var(--red-t);border-radius:9px;padding:8px;font-size:12px;font-weight:500;font-family:inherit;border:1px solid rgba(239,68,68,0.2);cursor:pointer;width:100%;transition:.15s;margin-top:6px}
.logout-btn:hover{background:rgba(239,68,68,0.2)}
.mob-top{display:none;position:fixed;top:0;right:0;left:0;height:52px;background:var(--bg2);border-bottom:1px solid var(--card-b);z-index:150;align-items:center;justify-content:space-between;padding:0 14px;transition:background .3s}
.mob-top .ml{display:flex;align-items:center;gap:9px}
.mob-logo{width:28px;height:28px;border-radius:7px;overflow:hidden}
.mob-logo img{width:100%;height:100%;object-fit:cover}
.mob-title{color:var(--t1);font-size:13px;font-weight:700}
.mob-right{display:flex;gap:6px}
.menu-btn,.theme-mob{background:var(--accent-d);border:1px solid var(--card-b);color:var(--t2);width:34px;height:34px;border-radius:8px;font-size:17px;display:flex;align-items:center;justify-content:center;cursor:pointer;transition:.15s}
.overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:190;backdrop-filter:blur(3px)}
.overlay.show{display:block}
.main{margin-right:var(--sidebar-w);flex:1;padding:28px 28px 60px;min-width:0;transition:margin .25s}
.pg{display:none}
.pg.on{display:block;animation:fi .2s ease}
@keyframes fi{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
.topbar{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:22px;flex-wrap:wrap;gap:12px}
.tb-title{font-size:18px;font-weight:700;color:var(--t1);display:flex;align-items:center;gap:8px;letter-spacing:-.02em}
.tb-title i{color:var(--accent);font-size:20px}
.tb-sub{font-size:11px;color:var(--t3);margin-top:4px}
.tb-right{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.badge{font-size:10px;padding:3px 10px;border-radius:20px;font-weight:700;display:inline-flex;align-items:center;gap:5px;white-space:nowrap}
.bg-green{background:var(--green-bg);color:var(--green-t)}
.bg-blue{background:var(--accent-d);color:var(--accent2)}
.bg-amber{background:var(--amber-bg);color:var(--amber-t)}
.bg-red{background:var(--red-bg);color:var(--red-t)}
.bg-purple{background:var(--purple-bg);color:#A78BFA}
.dot{width:6px;height:6px;border-radius:50%;flex-shrink:0;display:inline-block}
.dg{background:var(--green)}.dr{background:var(--red)}.da{background:var(--amber)}.db{background:var(--accent)}
.pulse{animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}
.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:13px;margin-bottom:18px}
.metric{background:var(--card);border:1px solid var(--card-b);border-radius:var(--radius);padding:17px 17px 14px;transition:all .2s;position:relative;overflow:hidden;cursor:default}
.metric::after{content:'';position:absolute;top:0;right:0;width:3px;height:100%;background:var(--accent);opacity:0;transition:.2s}
.metric:hover{border-color:var(--card-bh);transform:translateY(-2px);box-shadow:var(--shadow)}
.metric:hover::after{opacity:1}
.metric.suc::after{background:var(--green)}
.metric.dan::after{background:var(--red)}
/* ══════ صفحه ترافیک - ریدیزاین ══════ */
.traf-hero{display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;gap:13px;margin-bottom:18px}
.traf-main-stat{background:linear-gradient(155deg,var(--bg3) 0%,var(--card) 60%);border:1px solid var(--card-b);border-radius:20px;padding:22px 24px;position:relative;overflow:hidden}
.traf-main-stat::before{content:'';position:absolute;top:-50px;left:-50px;width:200px;height:200px;background:radial-gradient(circle,var(--accent-d),transparent 70%);pointer-events:none}
.traf-main-label{font-size:10.5px;color:var(--t3);font-weight:700;text-transform:uppercase;letter-spacing:.08em;display:flex;align-items:center;gap:6px;margin-bottom:10px;position:relative;z-index:1}
.traf-main-val{font-size:34px;font-weight:800;color:var(--t1);line-height:1;letter-spacing:-.02em;display:flex;align-items:baseline;gap:6px;position:relative;z-index:1}
.traf-main-val span{font-size:14px;font-weight:500;color:var(--t3)}
.traf-trend{display:inline-flex;align-items:center;gap:4px;font-size:11px;font-weight:700;padding:4px 10px;border-radius:20px;margin-top:12px;position:relative;z-index:1}
.traf-trend.up{background:var(--green-bg);color:var(--green-t)}
.traf-trend.down{background:var(--red-bg);color:var(--red-t)}
.traf-mini{background:var(--card);border:1px solid var(--card-b);border-radius:20px;padding:18px 19px;display:flex;flex-direction:column;justify-content:space-between;transition:.2s}
.traf-mini:hover{border-color:var(--card-bh);transform:translateY(-2px)}
.traf-mini-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}
.traf-mini-icon{width:32px;height:32px;border-radius:9px;background:var(--accent-d);color:var(--accent);display:flex;align-items:center;justify-content:center;font-size:15px}
.traf-mini-icon.pk{background:var(--amber-bg);color:var(--amber)}
.traf-mini-icon.lo{background:var(--purple-bg);color:var(--purple)}
.traf-mini-label{font-size:9.5px;color:var(--t3);font-weight:700;text-transform:uppercase;letter-spacing:.06em}
.traf-mini-val{font-size:21px;font-weight:800;color:var(--t1);letter-spacing:-.01em}
.traf-mini-sub{font-size:9.5px;color:var(--t3);margin-top:3px}

.traf-chart-card{background:var(--card);border:1px solid var(--card-b);border-radius:22px;padding:22px 24px 18px;box-shadow:var(--shadow);margin-bottom:16px}
.traf-chart-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;flex-wrap:wrap;gap:10px}
.traf-chart-title{font-size:14px;font-weight:800;color:var(--t1);display:flex;align-items:center;gap:8px}
.traf-chart-title i{color:var(--accent);font-size:18px}
.traf-chart-sub{font-size:10.5px;color:var(--t3);margin-top:3px}
.traf-legend{display:flex;gap:14px;align-items:center}
.traf-legend-item{display:flex;align-items:center;gap:6px;font-size:10.5px;color:var(--t2);font-weight:600}
.traf-legend-dot{width:8px;height:8px;border-radius:3px}
.traf-range-tabs{display:flex;gap:4px;background:var(--accent-d);padding:3px;border-radius:10px;border:1px solid var(--card-b)}
.traf-range-tab{padding:6px 13px;border-radius:8px;font-size:10.5px;font-weight:700;color:var(--t3);cursor:pointer;transition:.15s;border:none;background:transparent;font-family:inherit}
.traf-range-tab.on{background:var(--accent);color:#fff;box-shadow:0 2px 8px rgba(59,130,246,.35)}
.traf-chart-body{height:320px;margin-top:14px;position:relative}

/* ══════ ALPN & Fingerprint — کارت‌های جدید ══════ */
.fp-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:8px}
.fp-card{border:1.5px solid var(--card-b);border-radius:12px;padding:11px 8px;cursor:pointer;
  transition:.18s;text-align:center;background:rgba(0,0,0,.1);position:relative}
[data-theme="light"] .fp-card{background:#fff}
.fp-card:hover{border-color:var(--card-bh);transform:translateY(-1px)}
.fp-card.active{border-color:var(--accent);background:var(--accent-d);box-shadow:0 0 0 3px rgba(59,130,246,.1)}
.fp-card-icon{width:28px;height:28px;border-radius:8px;background:var(--accent-d);color:var(--accent);
  display:flex;align-items:center;justify-content:center;font-size:14px;margin:0 auto 6px}
.fp-card.active .fp-card-icon{background:var(--accent);color:#fff}
.fp-card-title{font-size:10.5px;font-weight:800;color:var(--t1)}
.fp-card-check{position:absolute;top:5px;left:5px;width:14px;height:14px;border-radius:50%;
  background:var(--accent);color:#fff;font-size:8px;display:flex;align-items:center;justify-content:center;
  opacity:0;transform:scale(.4);transition:.15s}
.fp-card.active .fp-card-check{opacity:1;transform:scale(1)}

.alpn-row{display:flex;gap:7px;flex-wrap:wrap;margin-top:8px}
.alpn-chip{display:flex;align-items:center;gap:6px;padding:7px 13px;border-radius:10px;
  border:1.5px solid var(--card-b);background:rgba(0,0,0,.1);cursor:pointer;transition:.15s;
  font-size:11px;font-weight:700;color:var(--t2)}
[data-theme="light"] .alpn-chip{background:#fff}
.alpn-chip:hover{border-color:var(--card-bh)}
.alpn-chip.active{border-color:var(--accent);background:var(--accent-d);color:var(--accent2)}
.alpn-chip-dot{width:14px;height:14px;border-radius:4px;border:1.5px solid var(--card-b);
  display:flex;align-items:center;justify-content:center;transition:.15s;flex-shrink:0}
.alpn-chip.active .alpn-chip-dot{background:var(--accent);border-color:var(--accent)}
.alpn-chip-dot i{font-size:9px;color:#fff;opacity:0;transform:scale(.5);transition:.15s}
.alpn-chip.active .alpn-chip-dot i{opacity:1;transform:scale(1)}

.stream-sub-label{font-size:10px;font-weight:800;color:var(--t3);text-transform:uppercase;
  letter-spacing:.06em;display:flex;align-items:center;gap:6px;margin-top:16px;margin-bottom:2px}
.stream-sub-label i{color:var(--accent);font-size:13px}

@media(max-width:900px){.traf-hero{grid-template-columns:1fr 1fr}}
@media(max-width:520px){.traf-hero{grid-template-columns:1fr}.traf-chart-body{height:260px}}
.m-icon{width:34px;height:34px;border-radius:8px;background:var(--accent-d);display:flex;align-items:center;justify-content:center;margin-bottom:11px;color:var(--accent);font-size:17px}
.m-icon.suc{background:var(--green-bg);color:var(--green)}
.m-icon.dan{background:var(--red-bg);color:var(--red)}
.m-icon.pur{background:var(--purple-bg);color:var(--purple)}
.m-label{font-size:10px;color:var(--t3);margin-bottom:4px;font-weight:600;text-transform:uppercase;letter-spacing:.05em}
.m-val{font-size:25px;font-weight:700;color:var(--t1);line-height:1;letter-spacing:-.02em}
.m-unit{font-size:12px;font-weight:400;color:var(--t3)}
.m-sub{font-size:10px;color:var(--t3);margin-top:6px;display:flex;align-items:center;gap:3px}
.vless-box{background:linear-gradient(135deg,var(--bg3) 0%,var(--bg2) 100%);border:1px solid var(--card-b);border-radius:18px;padding:20px 22px;margin-bottom:18px;box-shadow:var(--shadow);position:relative;overflow:hidden;transition:background .3s}
.vless-box::before{content:'';position:absolute;top:-50px;left:-50px;width:180px;height:180px;background:radial-gradient(circle,var(--accent-d),transparent 70%);pointer-events:none}
.vl-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:13px;flex-wrap:wrap;gap:8px}
.vl-title{color:var(--t2);font-size:11px;display:flex;align-items:center;gap:6px;font-weight:700;text-transform:uppercase;letter-spacing:.06em}
.vl-title i{color:var(--accent);font-size:15px}
.vl-code{background:rgba(0,0,0,.18);border:1px solid var(--card-b);border-radius:9px;padding:13px 15px;font-size:11px;font-family:ui-monospace,monospace;color:var(--accent2);word-break:break-all;line-height:1.8;letter-spacing:.01em}
[data-theme="light"] .vl-code{background:rgba(0,0,0,.04)}
.vl-actions{display:flex;gap:8px;margin-top:13px;flex-wrap:wrap}
.btn{font-family:inherit;font-size:12px;font-weight:500;border-radius:9px;padding:8px 14px;cursor:pointer;display:inline-flex;align-items:center;gap:5px;border:none;transition:all .15s;white-space:nowrap}
.btn i{font-size:13px}
.btn:disabled{opacity:.4;cursor:not-allowed}
.btn-p{background:var(--accent);color:#fff;box-shadow:0 2px 12px rgba(59,130,246,.3)}
.btn-p:hover{background:#2563EB;box-shadow:0 4px 18px rgba(59,130,246,.4)}
.btn-o{background:transparent;border:1px solid var(--card-b);color:var(--t2)}
.btn-o:hover{background:var(--accent-d);border-color:rgba(59,130,246,.3)}
.btn-g{background:var(--accent-d);color:var(--accent2);border:1px solid rgba(59,130,246,.15)}
.btn-g:hover{background:rgba(59,130,246,.22)}
.btn-d{background:var(--red-bg);color:var(--red-t);border:1px solid rgba(239,68,68,.2)}
.btn-d:hover{background:rgba(239,68,68,.2)}
.btn-pur{background:var(--purple-bg);color:#A78BFA;border:1px solid rgba(139,92,246,.2)}
.btn-pur:hover{background:rgba(139,92,246,.22)}
.btn-amber{background:var(--amber-bg);color:var(--amber-t);border:1px solid rgba(245,158,11,.2)}
.btn-amber:hover{background:rgba(245,158,11,.22)}
.btn-sm{padding:5px 9px;font-size:10.5px;border-radius:7px}
.btn-icon{width:30px;height:30px;padding:0;justify-content:center;border-radius:5px}
.card{background:var(--card);border:1px solid var(--card-b);border-radius:var(--radius);padding:18px 20px;transition:border-color .2s,background .3s}
.card:hover{border-color:var(--card-bh)}
.card-title{font-size:12.5px;font-weight:700;color:var(--t1);margin-bottom:15px;display:flex;align-items:center;gap:7px}
.card-title i{font-size:16px;color:var(--accent)}
.ml-auto{margin-right:auto}
.g2{display:grid;grid-template-columns:1fr 1fr;gap:13px;margin-bottom:16px}
.g3{display:grid;grid-template-columns:2fr 1fr;gap:13px;margin-bottom:16px}
.mb16{margin-bottom:16px}
.sr{display:flex;align-items:center;justify-content:space-between;padding:9px 0;border-bottom:1px solid rgba(59,130,246,0.05);font-size:12px}
.sr:last-child{border-bottom:none}
.sr-k{color:var(--t2);display:flex;align-items:center;gap:6px}
.sr-k i{font-size:13px;color:var(--t3)}
.sr-v{color:var(--t1);font-weight:600;font-size:11.5px}
.ch{position:relative;height:230px}
.ch-lg{position:relative;height:330px}
.ch-sm{position:relative;height:185px}
.exp-chip{font-size:9px;padding:3px 8px;border-radius:6px;font-weight:700;display:inline-flex;align-items:center;gap:3px}
.ec-ok{background:var(--green-bg);color:var(--green-t)}
.ec-warn{background:var(--amber-bg);color:var(--amber-t)}
.ec-exp{background:var(--red-bg);color:var(--red-t)}
.ec-inf{background:var(--accent-d);color:var(--accent2)}
.tog{width:19px;height:34px;border-radius:19px;background:rgba(100,116,139,0.25);position:relative;cursor:pointer;transition:.2s;flex-shrink:0;border:none}
.tog::after{content:'';position:absolute;width:13px;height:13px;border-radius:50%;background:#fff;left:3px;bottom:3px;transition:.2s;box-shadow:0 1px 3px rgba(0,0,0,.3)}
.tog.on{background:var(--green)}
.tog.on::after{bottom:18px}
.form-row{display:flex;gap:9px;flex-wrap:wrap;align-items:flex-end}
.fg{display:flex;flex-direction:column;gap:5px}
.fg label{font-size:10px;color:var(--t3);font-weight:700;text-transform:uppercase;letter-spacing:.06em}
.fi,.fs{padding:9px 12px;border-radius:9px;border:1px solid var(--card-b);background:rgba(0,0,0,.18);color:var(--t1);font-family:inherit;font-size:12px;outline:none;transition:.15s;min-width:100px}
[data-theme="light"] .fi,[data-theme="light"] .fs{background:rgba(0,0,0,.04)}
.fi::placeholder{color:var(--t3)}
.fi:focus,.fs:focus{border-color:rgba(59,130,246,.45);background:rgba(0,0,0,.25);box-shadow:0 0 0 3px rgba(59,130,246,.08)}
.fs option{background:var(--bg2)}
[data-theme="light"] .fs option{background:#fff}
.cl{background:var(--accent-d);border:1px solid rgba(59,130,246,.15);border-radius:10px;padding:11px 13px;font-size:11px;color:var(--t2);display:flex;gap:9px;align-items:flex-start;line-height:1.8;margin-top:12px}
.cl i{font-size:15px;color:var(--accent);margin-top:1px;flex-shrink:0}
.cl.amber{background:var(--amber-bg);border-color:rgba(245,158,11,.2);color:var(--amber-t)}
/* ══════ پنل ساخت کانفیگ - طراحی جدید ══════ */
.create-panel{background:linear-gradient(155deg,var(--bg3) 0%,var(--card) 55%);border:1px solid var(--card-b);border-radius:22px;padding:0;overflow:hidden;box-shadow:var(--shadow);margin-bottom:16px;position:relative}
.create-panel::before{content:'';position:absolute;top:-60px;left:-60px;width:220px;height:220px;background:radial-gradient(circle,var(--accent-d),transparent 70%);pointer-events:none}
.cp-head{display:flex;align-items:center;gap:13px;padding:22px 24px 18px;position:relative;z-index:1}
.cp-head-icon{width:44px;height:44px;border-radius:13px;background:linear-gradient(135deg,var(--accent),var(--accent2));display:flex;align-items:center;justify-content:center;color:#fff;font-size:20px;flex-shrink:0;box-shadow:0 6px 18px rgba(59,130,246,.35)}
.cp-head-text{flex:1;min-width:0}
.cp-head-title{font-size:15px;font-weight:800;color:var(--t1);letter-spacing:-.01em}
.cp-head-sub{font-size:11px;color:var(--t3);margin-top:2px}
.cp-body{padding:2px 24px 22px;position:relative;z-index:1}
.cp-row{display:grid;grid-template-columns:1.3fr 1fr;gap:14px;margin-bottom:16px}
.cp-block{background:rgba(0,0,0,.14);border:1px solid var(--card-b);border-radius:14px;padding:14px 16px}
[data-theme="light"] .cp-block{background:rgba(37,99,235,.03)}
.cp-block-label{font-size:10px;font-weight:800;color:var(--t2);text-transform:uppercase;letter-spacing:.08em;display:flex;align-items:center;gap:6px;margin-bottom:11px}
.cp-block-label i{color:var(--accent);font-size:14px}
.cp-input-full{width:100%;padding:10px 13px;border-radius:10px;border:1px solid var(--card-b);background:rgba(0,0,0,.18);color:var(--t1);font-family:inherit;font-size:12.5px;outline:none;transition:.15s}
[data-theme="light"] .cp-input-full{background:#fff}
.cp-input-full:focus{border-color:rgba(59,130,246,.5);box-shadow:0 0 0 3px rgba(59,130,246,.1)}
.cp-input-full::placeholder{color:var(--t3)}
.cp-mini-row{display:flex;gap:8px;margin-top:9px}
.cp-quota-inputs{display:flex;gap:8px}
.cp-quota-inputs .cp-input-full{flex:1}
.cp-quota-inputs select.cp-input-full{flex:0 0 76px}
.chip-row{display:flex;gap:6px;flex-wrap:wrap;margin-top:9px}
.chip{font-size:10.5px;font-weight:700;padding:5px 12px;border-radius:8px;background:var(--accent-d);color:var(--t2);border:1px solid var(--card-b);cursor:pointer;transition:.15s;white-space:nowrap}
.chip:hover{background:rgba(59,130,246,.18);color:var(--accent2)}
.chip.active{background:var(--accent);color:#fff;border-color:var(--accent);box-shadow:0 3px 10px rgba(59,130,246,.35)}
.proto-tabs{display:flex;gap:8px;flex-wrap:wrap}
.proto-step-label{font-size:10px;font-weight:800;color:var(--t2);text-transform:uppercase;letter-spacing:.06em;display:flex;align-items:center;gap:6px;margin-bottom:9px}
.proto-step-label i{color:var(--accent);font-size:14px}

.proto-base-cards{display:grid;grid-template-columns:1fr 1fr;gap:9px}
.proto-base-card{border:1.5px solid var(--card-b);border-radius:13px;padding:14px 12px;cursor:pointer;transition:.18s;text-align:center;position:relative;background:rgba(0,0,0,.1)}
[data-theme="light"] .proto-base-card{background:#fff}
.proto-base-card:hover{border-color:var(--card-bh);transform:translateY(-1px)}
.proto-base-card.active{border-color:var(--accent);background:var(--accent-d);box-shadow:0 0 0 3px rgba(59,130,246,.1)}
.proto-base-icon{width:34px;height:34px;border-radius:9px;background:var(--accent-d);color:var(--accent);display:flex;align-items:center;justify-content:center;font-size:17px;margin:0 auto 8px}
.proto-base-card.active .proto-base-icon{background:var(--accent);color:#fff}
.proto-base-title{font-size:12px;font-weight:800;color:var(--t1)}
.proto-base-desc{font-size:9.5px;color:var(--t3);margin-top:3px}

.proto-transport-cards{display:grid;grid-template-columns:repeat(3,1fr);gap:9px}
.proto-t-card{border:1.5px solid var(--card-b);border-radius:13px;padding:13px 10px;cursor:pointer;transition:.18s;text-align:center;position:relative;background:rgba(0,0,0,.1)}
[data-theme="light"] .proto-t-card{background:#fff}
.proto-t-card:hover{border-color:var(--card-bh);transform:translateY(-1px)}
.proto-t-card.active{border-color:var(--accent);background:var(--accent-d);box-shadow:0 0 0 3px rgba(59,130,246,.1)}
.proto-t-icon{width:30px;height:30px;border-radius:9px;background:var(--accent-d);color:var(--accent);display:flex;align-items:center;justify-content:center;font-size:15px;margin:0 auto 7px}
.proto-t-card.active .proto-t-icon{background:var(--accent);color:#fff}
.proto-t-title{font-size:10.5px;font-weight:800;color:var(--t1)}
.proto-t-desc{font-size:9px;color:var(--t3);margin-top:3px;line-height:1.4}

@media(max-width:760px){
  .proto-transport-cards{grid-template-columns:1fr}
}
.proto-tab{flex:1;min-width:120px;display:flex;align-items:center;justify-content:center;gap:7px;
  padding:11px 10px;border-radius:12px;border:1.5px solid var(--card-b);background:rgba(0,0,0,.1);
  color:var(--t2);font-family:inherit;font-size:11.5px;font-weight:700;cursor:pointer;transition:.15s}
.proto-tab.active{border-color:var(--accent);background:var(--accent-d);color:var(--accent2);
  box-shadow:0 0 0 3px rgba(59,130,246,.1)}
.proto-submodes{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px}
.proto-cards{display:grid;grid-template-columns:repeat(3,1fr);gap:9px}
.proto-card{border:1.5px solid var(--card-b);border-radius:13px;padding:13px 12px;cursor:pointer;transition:.18s;text-align:center;position:relative;background:rgba(0,0,0,.1)}
[data-theme="light"] .proto-card{background:#fff}
.proto-card:hover{border-color:var(--card-bh);transform:translateY(-1px)}
.proto-card.active{border-color:var(--accent);background:var(--accent-d);box-shadow:0 0 0 3px rgba(59,130,246,.1)}
.proto-card.active .proto-card-check{opacity:1;transform:scale(1)}
.proto-card-check{position:absolute;top:7px;left:7px;width:16px;height:16px;border-radius:50%;background:var(--accent);color:#fff;font-size:10px;display:flex;align-items:center;justify-content:center;opacity:0;transform:scale(.5);transition:.18s}
.proto-card-icon{width:32px;height:32px;border-radius:9px;background:var(--accent-d);color:var(--accent);display:flex;align-items:center;justify-content:center;font-size:16px;margin:0 auto 8px}
.proto-card.active .proto-card-icon{background:var(--accent);color:#fff}
.proto-card-title{font-size:11px;font-weight:800;color:var(--t1)}
.proto-card-desc{font-size:9px;color:var(--t3);margin-top:3px;line-height:1.5}
.cp-footer{display:flex;align-items:center;justify-content:space-between;gap:12px;padding-top:16px;border-top:1px solid var(--card-b);flex-wrap:wrap}
.cp-footer-note{display:flex;align-items:center;gap:8px;font-size:10.5px;color:var(--t3);line-height:1.7;flex:1;min-width:220px}
.cp-footer-note i{color:var(--accent);font-size:15px;flex-shrink:0}
.cp-submit-btn{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;border:none;border-radius:13px;padding:13px 26px;font-family:inherit;font-size:13px;font-weight:800;cursor:pointer;display:flex;align-items:center;gap:8px;box-shadow:0 6px 20px rgba(59,130,246,.35);transition:.18s;white-space:nowrap}
.cp-submit-btn:hover{transform:translateY(-2px);box-shadow:0 10px 26px rgba(59,130,246,.45)}
.cp-submit-btn:active{transform:translateY(0) scale(.98)}
@media(max-width:760px){
  .cp-row{grid-template-columns:1fr}
  .proto-cards{grid-template-columns:1fr}
  .cp-footer{flex-direction:column;align-items:stretch}
  .cp-submit-btn{justify-content:center}
}
/* ══════ پنل اطلاعات سرور ══════ */
.srv-panel{background:linear-gradient(155deg,var(--bg3) 0%,var(--card) 60%);border:1px solid var(--card-b);border-radius:22px;overflow:hidden;box-shadow:var(--shadow);position:relative}
.srv-panel::before{content:'';position:absolute;top:-60px;left:-60px;width:200px;height:200px;background:radial-gradient(circle,var(--accent-d),transparent 70%);pointer-events:none}
.srv-hero{display:flex;align-items:center;gap:14px;padding:22px 24px;position:relative;z-index:1;border-bottom:1px solid var(--card-b)}
.srv-hero-icon{width:50px;height:50px;border-radius:14px;background:linear-gradient(135deg,var(--accent),var(--accent2));display:flex;align-items:center;justify-content:center;color:#fff;font-size:22px;flex-shrink:0;box-shadow:0 6px 18px rgba(59,130,246,.35)}
.srv-hero-text{flex:1;min-width:0}
.srv-hero-domain{font-size:15px;font-weight:800;color:var(--t1);word-break:break-all}
.srv-hero-sub{font-size:10.5px;color:var(--t3);margin-top:4px;display:flex;align-items:center;gap:6px}
.srv-tiles{display:grid;grid-template-columns:1fr 1fr;gap:11px;padding:20px 22px 22px;position:relative;z-index:1}
.srv-tile{display:flex;align-items:center;gap:11px;background:rgba(0,0,0,.14);border:1px solid var(--card-b);border-radius:13px;padding:12px 14px;transition:.18s}
[data-theme="light"] .srv-tile{background:rgba(37,99,235,.03)}
.srv-tile:hover{border-color:var(--card-bh);transform:translateY(-1px)}
.srv-tile-icon{width:34px;height:34px;border-radius:10px;background:var(--accent-d);color:var(--accent);display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0}
.srv-tile-text{min-width:0}
.srv-tile-label{font-size:9.5px;color:var(--t3);font-weight:700;text-transform:uppercase;letter-spacing:.05em;margin-bottom:3px}
.srv-tile-val{font-size:12px;font-weight:700;color:var(--t1);word-break:break-word}

/* ══════ پنل تغییر رمز ══════ */
.pw-panel{background:linear-gradient(155deg,var(--bg3) 0%,var(--card) 60%);border:1px solid var(--card-b);border-radius:22px;overflow:hidden;box-shadow:var(--shadow);position:relative}
.pw-panel::before{content:'';position:absolute;top:-60px;right:-60px;width:200px;height:200px;background:radial-gradient(circle,var(--purple-bg),transparent 70%);pointer-events:none}
.pw-hero{display:flex;align-items:center;gap:14px;padding:22px 24px 18px;position:relative;z-index:1}
.pw-hero-icon{width:50px;height:50px;border-radius:14px;background:linear-gradient(135deg,var(--purple),#6D48D6);display:flex;align-items:center;justify-content:center;color:#fff;font-size:22px;flex-shrink:0;box-shadow:0 6px 18px rgba(139,92,246,.35)}
.pw-hero-text{flex:1;min-width:0}
.pw-hero-title{font-size:15px;font-weight:800;color:var(--t1)}
.pw-hero-sub{font-size:10.5px;color:var(--t3);margin-top:3px}
.pw-body{padding:2px 24px 22px;position:relative;z-index:1}
.pw-field{position:relative;margin-bottom:13px}
.pw-field label{display:block;font-size:10px;font-weight:700;color:var(--t2);text-transform:uppercase;letter-spacing:.06em;margin-bottom:7px}
.pw-input{width:100%;padding:11px 42px 11px 14px;border-radius:11px;border:1px solid var(--card-b);background:rgba(0,0,0,.18);color:var(--t1);font-family:inherit;font-size:12.5px;outline:none;transition:.15s}
[data-theme="light"] .pw-input{background:#fff}
.pw-input:focus{border-color:rgba(139,92,246,.5);box-shadow:0 0 0 3px rgba(139,92,246,.1)}
.pw-eye{position:absolute;left:12px;top:34px;background:none;border:none;color:var(--t3);cursor:pointer;font-size:16px;padding:4px;display:flex}
.pw-eye:hover{color:var(--purple)}
.pw-strength{height:4px;border-radius:3px;background:var(--accent-d);margin-top:8px;overflow:hidden;display:flex;gap:3px}
.pw-strength-seg{flex:1;height:100%;border-radius:3px;background:rgba(100,116,139,.2);transition:.25s}
.pw-strength-label{font-size:9.5px;color:var(--t3);margin-top:5px;display:flex;align-items:center;gap:5px}
.pw-reqs{display:flex;flex-wrap:wrap;gap:6px;margin-top:11px;margin-bottom:16px}
.pw-req{font-size:9.5px;padding:4px 10px;border-radius:7px;background:var(--accent-d);color:var(--t3);font-weight:600;display:flex;align-items:center;gap:4px;transition:.18s}
.pw-req.met{background:var(--green-bg);color:var(--green-t)}
.pw-submit{width:100%;justify-content:center;background:linear-gradient(135deg,var(--purple),#6D48D6);color:#fff;border:none;border-radius:12px;padding:12px;font-family:inherit;font-size:13px;font-weight:800;cursor:pointer;display:flex;align-items:center;gap:8px;box-shadow:0 6px 18px rgba(139,92,246,.32);transition:.18s}
.pw-submit:hover{transform:translateY(-2px);box-shadow:0 10px 24px rgba(139,92,246,.42)}
.pw-submit:active{transform:translateY(0) scale(.98)}

/* ══════ اتصالات فعال - نسخه پیشرفته ══════ */
.conn-hero{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:18px}
.conn-hero-tile{background:var(--card);border:1px solid var(--card-b);border-radius:16px;padding:16px 18px;position:relative;overflow:hidden;transition:.2s}
.conn-hero-tile:hover{border-color:var(--card-bh);transform:translateY(-2px);box-shadow:var(--shadow)}
.conn-hero-tile::after{content:'';position:absolute;bottom:0;left:0;right:0;height:2px;background:linear-gradient(90deg,var(--green),transparent)}
.conn-hero-icon{width:32px;height:32px;border-radius:9px;background:var(--green-bg);color:var(--green-t);display:flex;align-items:center;justify-content:center;font-size:15px;margin-bottom:10px}
.conn-hero-tile:nth-child(2) .conn-hero-icon{background:var(--accent-d);color:var(--accent)}
.conn-hero-tile:nth-child(3) .conn-hero-icon{background:var(--purple-bg);color:var(--purple)}
.conn-hero-tile:nth-child(4) .conn-hero-icon{background:var(--amber-bg);color:var(--amber)}
.conn-hero-label{font-size:9.5px;color:var(--t3);font-weight:700;text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px}
.conn-hero-val{font-size:21px;font-weight:800;color:var(--t1);line-height:1;letter-spacing:-.02em}
.conn-hero-unit{font-size:11px;color:var(--t3);font-weight:500}

.conn-toolbar{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:14px;flex-wrap:wrap}
.conn-toolbar-title{font-size:12px;font-weight:800;color:var(--t2);display:flex;align-items:center;gap:7px;text-transform:uppercase;letter-spacing:.06em}
.conn-toolbar-title i{color:var(--green);font-size:15px}
.conn-live-badge{display:flex;align-items:center;gap:6px;font-size:10.5px;font-weight:700;color:var(--green-t);background:var(--green-bg);padding:5px 12px;border-radius:20px;border:1px solid rgba(16,185,129,.2)}
.conn-live-dot{width:6px;height:6px;border-radius:50%;background:var(--green);animation:pulse 1.6s infinite}

.conn-grid-v2{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}
.conn-card-v2{background:var(--card);border:1px solid var(--card-b);border-radius:18px;padding:0;overflow:hidden;transition:all .22s cubic-bezier(.4,0,.2,1);position:relative}
.conn-card-v2:hover{border-color:var(--card-bh);transform:translateY(-3px);box-shadow:0 14px 32px rgba(0,0,0,.22)}
.conn-card-v2-glow{position:absolute;top:-40px;left:-40px;width:140px;height:140px;background:radial-gradient(circle,rgba(16,185,129,.1),transparent 70%);pointer-events:none}
.conn-card-v2-top{display:flex;align-items:center;gap:12px;padding:16px 17px 13px;position:relative;z-index:1}
.conn-avatar{width:42px;height:42px;border-radius:13px;background:linear-gradient(135deg,var(--green),#0D9668);display:flex;align-items:center;justify-content:center;color:#fff;font-size:18px;flex-shrink:0;position:relative;box-shadow:0 4px 14px rgba(16,185,129,.3)}
.conn-avatar::after{content:'';position:absolute;inset:-4px;border-radius:16px;border:1.5px solid var(--green);opacity:.4;animation:breathe2 2.4s ease-in-out infinite}
@keyframes breathe2{0%,100%{transform:scale(1);opacity:.4}50%{transform:scale(1.12);opacity:0}}
.conn-card-v2-id{flex:1;min-width:0}
.conn-ip-v2{font-family:ui-monospace,monospace;font-size:14px;font-weight:800;color:var(--t1);display:flex;align-items:center;gap:6px}
.conn-ip-copy{background:none;border:none;color:var(--t3);cursor:pointer;font-size:12px;padding:2px;display:flex;transition:.15s}
.conn-ip-copy:hover{color:var(--accent)}
.conn-label-v2{font-size:10.5px;color:var(--t3);margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.conn-status-pill{font-size:9px;font-weight:800;padding:4px 9px;border-radius:20px;background:var(--green-bg);color:var(--green-t);display:flex;align-items:center;gap:4px;white-space:nowrap;flex-shrink:0}
.conn-card-v2-divider{height:1px;background:linear-gradient(90deg,transparent,var(--card-b) 15%,var(--card-b) 85%,transparent);margin:0 17px}
.conn-card-v2-body{padding:14px 17px 16px}
.conn-proto-row{margin-bottom:12px}
.conn-stat-row{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px}
.conn-stat-box{display:flex;align-items:center;gap:8px}
.conn-stat-icon{width:26px;height:26px;border-radius:8px;background:var(--accent-d);color:var(--accent);display:flex;align-items:center;justify-content:center;font-size:12px;flex-shrink:0}
.conn-stat-icon.time{background:var(--purple-bg);color:var(--purple)}
.conn-stat-text-label{font-size:8.5px;color:var(--t3);font-weight:700;text-transform:uppercase;letter-spacing:.04em}
.conn-stat-text-val{font-size:11.5px;font-weight:700;color:var(--t1);margin-top:1px}
.conn-duration-track{height:5px;border-radius:4px;background:var(--accent-d);overflow:hidden;position:relative}
.conn-duration-fill{height:100%;border-radius:4px;background:linear-gradient(90deg,var(--green),#3FD79C);position:relative;overflow:hidden}
.conn-duration-fill::after{content:'';position:absolute;inset:0;background:linear-gradient(90deg,transparent,rgba(255,255,255,.35),transparent);width:40%;animation:shimmer 1.8s linear infinite}
@keyframes shimmer{0%{transform:translateX(-120%)}100%{transform:translateX(280%)}}

.conn-empty-v2{text-align:center;padding:70px 20px;background:var(--card);border:1px dashed var(--card-b);border-radius:20px}
.conn-empty-v2-icon{width:64px;height:64px;border-radius:18px;background:var(--accent-d);display:flex;align-items:center;justify-content:center;font-size:28px;color:var(--t3);margin:0 auto 16px}
.conn-empty-v2-title{font-size:13.5px;font-weight:700;color:var(--t2);margin-bottom:5px}
.conn-empty-v2-sub{font-size:11px;color:var(--t3)}

@media(max-width:760px){.conn-hero{grid-template-columns:1fr 1fr}}
@media(max-width:500px){.conn-grid-v2{grid-template-columns:1fr}}

@media(max-width:560px){.srv-tiles{grid-template-columns:1fr}}
.cl.amber i{color:var(--amber)}
.sub-box{background:rgba(139,92,246,.07);border:1px solid rgba(139,92,246,.2);border-radius:10px;padding:14px 16px;display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-top:11px}
.sub-url{font-family:ui-monospace,monospace;font-size:10.5px;color:#A78BFA;word-break:break-all;flex:1}
.spbar{height:4px;border-radius:3px;background:var(--accent-d);margin-top:5px;overflow:hidden}
.spfill{height:100%;border-radius:3px;background:linear-gradient(90deg,var(--accent),var(--accent2));transition:width 1s}
.empty{text-align:center;padding:50px 20px;color:var(--t3)}
.empty i{font-size:40px;opacity:.3;margin-bottom:12px;display:block}
.empty p{font-size:12.5px;margin-top:4px}
/* ══════ گروه‌های ساب - ریدیزاین کامل ══════ */
.subs-toolbar{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:16px;flex-wrap:wrap}
.subs-search{flex:1;min-width:200px;position:relative}
.subs-search input{width:100%;padding:11px 40px 11px 15px;border-radius:12px;border:1px solid var(--card-b);background:var(--card);color:var(--t1);font-family:inherit;font-size:12.5px;outline:none;transition:.15s}
.subs-search input:focus{border-color:rgba(139,92,246,.5);box-shadow:0 0 0 3px rgba(139,92,246,.1)}
.subs-search i{position:absolute;left:14px;top:50%;transform:translateY(-50%);color:var(--t3);font-size:15px}

.sub-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:16px;margin-bottom:18px}
.sub-card{background:var(--card);border:1px solid var(--card-b);border-radius:20px;padding:0;overflow:hidden;transition:all .25s cubic-bezier(.4,0,.2,1);position:relative}
.sub-card:hover{border-color:var(--card-bh);transform:translateY(-4px);box-shadow:0 16px 36px rgba(0,0,0,.24)}
.sub-card-top{background:linear-gradient(155deg,var(--purple-bg) 0%,transparent 65%);padding:20px 20px 16px;position:relative}
.sub-card-top::before{content:'';position:absolute;top:-30px;left:-30px;width:130px;height:130px;background:radial-gradient(circle,rgba(139,92,246,.14),transparent 70%);pointer-events:none}
.sub-card-head-v2{display:flex;align-items:flex-start;gap:13px;position:relative;z-index:1}
.sub-card-icon{width:46px;height:46px;border-radius:14px;background:linear-gradient(135deg,var(--purple),#6D48D6);display:flex;align-items:center;justify-content:center;color:#fff;font-size:20px;flex-shrink:0;box-shadow:0 6px 16px rgba(139,92,246,.35)}
.sub-card-titles{flex:1;min-width:0}
.sub-card-name-v2{font-size:15.5px;font-weight:800;color:var(--t1);letter-spacing:-.01em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sub-card-desc-v2{font-size:11px;color:var(--t3);margin-top:3px;line-height:1.6;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.sub-card-lock-badge{flex-shrink:0;width:26px;height:26px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:12px}
.sub-card-lock-badge.locked{background:var(--amber-bg);color:var(--amber-t)}
.sub-card-lock-badge.open{background:var(--green-bg);color:var(--green-t)}

.sub-card-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:0;position:relative;z-index:1;margin-top:16px;background:rgba(0,0,0,.14);border:1px solid var(--card-b);border-radius:13px;overflow:hidden}
[data-theme="light"] .sub-card-stats{background:rgba(124,58,237,.03)}
.sub-card-stat{padding:11px 8px;text-align:center;border-left:1px solid var(--card-b)}
.sub-card-stat:last-child{border-left:none}
.sub-card-stat-val{font-size:15px;font-weight:800;color:var(--t1);line-height:1.2}
.sub-card-stat-label{font-size:8.5px;color:var(--t3);font-weight:700;text-transform:uppercase;letter-spacing:.05em;margin-top:4px}

.sub-card-url-row{margin:14px 20px 0;background:rgba(139,92,246,.08);border:1px dashed rgba(139,92,246,.25);border-radius:11px;padding:9px 12px;display:flex;align-items:center;gap:8px}
.sub-card-url-text{font-family:ui-monospace,monospace;font-size:9.5px;color:#A78BFA;flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sub-card-url-copy{background:none;border:none;color:var(--purple);cursor:pointer;font-size:13px;padding:3px;display:flex;flex-shrink:0;transition:.15s}
.sub-card-url-copy:hover{color:#A78BFA;transform:scale(1.1)}

.sub-card-bottom{padding:14px 20px 18px;display:flex;gap:7px;flex-wrap:wrap}
.sub-card-bottom .btn{flex:1;justify-content:center;min-width:fit-content}

.subs-empty-v2{text-align:center;padding:70px 20px;background:var(--card);border:1px dashed var(--card-b);border-radius:20px;grid-column:1/-1}
.subs-empty-v2-icon{width:64px;height:64px;border-radius:18px;background:var(--purple-bg);display:flex;align-items:center;justify-content:center;font-size:28px;color:var(--purple);margin:0 auto 16px}
.subs-empty-v2-title{font-size:13.5px;font-weight:700;color:var(--t2);margin-bottom:5px}
.subs-empty-v2-sub{font-size:11px;color:var(--t3)}

/* ══════ مودال ساخت گروه - نسخه فشرده ══════ */
.modal-v2{background:var(--card);border:1px solid var(--card-b);border-radius:22px;padding:0;max-width:430px;width:calc(100% - 32px);max-height:92vh;overflow-y:auto;position:relative;animation:fi .2s ease;box-shadow:0 24px 70px rgba(0,0,0,.5)}
.modal-v2-head{background:linear-gradient(155deg,rgba(139,92,246,.14) 0%,transparent 65%);padding:18px 22px 14px;position:relative;overflow:hidden}
.modal-v2-head::before{content:'';position:absolute;top:-50px;left:-50px;width:160px;height:160px;background:radial-gradient(circle,rgba(139,92,246,.2),transparent 70%);pointer-events:none}
.modal-v2-close{position:absolute;top:14px;left:14px;background:var(--accent-d);border:1px solid var(--card-b);color:var(--t2);width:30px;height:30px;border-radius:9px;font-size:15px;display:flex;align-items:center;justify-content:center;cursor:pointer;z-index:2;transition:.15s}
.modal-v2-close:hover{background:var(--red-bg);color:var(--red-t);border-color:rgba(239,68,68,.25)}
.modal-v2-icon{width:42px;height:42px;border-radius:13px;background:linear-gradient(135deg,var(--purple),#6D48D6);display:flex;align-items:center;justify-content:center;color:#fff;font-size:19px;margin-bottom:10px;position:relative;z-index:1;box-shadow:0 8px 18px rgba(139,92,246,.4)}
.modal-v2-title{font-size:15.5px;font-weight:800;color:var(--t1);position:relative;z-index:1;letter-spacing:-.01em}
.modal-v2-sub{font-size:10.5px;color:var(--t3);margin-top:3px;position:relative;z-index:1;line-height:1.6}
.modal-v2-body{padding:16px 22px 20px;border-top:1px solid var(--card-b)}
.modal-v2-field{margin-bottom:11px}
.modal-v2-field label{display:flex;align-items:center;gap:5px;font-size:9.5px;font-weight:800;color:var(--t2);text-transform:uppercase;letter-spacing:.06em;margin-bottom:6px}
.modal-v2-field label i{color:var(--purple);font-size:13px}
.modal-v2-input-wrap{position:relative}
.modal-v2-input-wrap>i{position:absolute;right:13px;top:50%;transform:translateY(-50%);color:var(--t3);font-size:14px;pointer-events:none;transition:.15s;z-index:1}
.modal-v2-input{width:100%;padding:9px 38px 9px 13px;border-radius:11px;border:1px solid var(--card-b);background:rgba(0,0,0,.2);color:var(--t1);font-family:inherit;font-size:12.5px;outline:none;transition:.18s}
[data-theme="light"] .modal-v2-input{background:rgba(124,58,237,.04)}
.modal-v2-input::placeholder{color:var(--t3)}
.modal-v2-input:focus{border-color:rgba(139,92,246,.55);box-shadow:0 0 0 3px rgba(139,92,246,.12);background:rgba(0,0,0,.28)}
[data-theme="light"] .modal-v2-input:focus{background:#fff}
.modal-v2-input:focus~i{color:var(--purple)}
.modal-v2-hint{background:rgba(59,130,246,.08);border:1px solid rgba(59,130,246,.18);border-radius:11px;padding:9px 12px;font-size:10px;color:var(--t2);display:flex;gap:7px;align-items:flex-start;line-height:1.6;margin-top:2px}
.modal-v2-hint i{font-size:14px;color:var(--accent);margin-top:1px;flex-shrink:0}
.modal-v2-footer{display:flex;gap:8px;margin-top:15px}
.modal-v2-btn-cancel{flex:.75;justify-content:center;padding:10px;border-radius:11px;background:transparent;border:1px solid var(--card-b);color:var(--t2);font-family:inherit;font-size:12px;font-weight:700;cursor:pointer;transition:.15s;display:flex;align-items:center}
.modal-v2-btn-cancel:hover{background:var(--accent-d);color:var(--t1)}
.modal-v2-btn-submit{flex:1;justify-content:center;padding:10px;border-radius:11px;background:linear-gradient(135deg,var(--purple),#6D48D6);color:#fff;border:none;font-family:inherit;font-size:12px;font-weight:800;cursor:pointer;display:flex;align-items:center;gap:6px;box-shadow:0 6px 18px rgba(139,92,246,.4);transition:.18s}
.modal-v2-btn-submit:hover{transform:translateY(-2px);box-shadow:0 10px 24px rgba(139,92,246,.5)}
.modal-v2-btn-submit:active{transform:translateY(0) scale(.98)}

/* ══════ مودال انتخاب کانفیگ - نسخه پیشرفته ══════ */
.lmodal-head{background:linear-gradient(155deg,var(--accent-d) 0%,transparent 70%);padding:22px 24px 18px;position:relative;border-bottom:1px solid var(--card-b)}
.lmodal-icon-row{display:flex;align-items:center;gap:12px;position:relative;z-index:1}
.lmodal-icon{width:44px;height:44px;border-radius:13px;background:linear-gradient(135deg,var(--accent),var(--accent2));display:flex;align-items:center;justify-content:center;color:#fff;font-size:19px;flex-shrink:0;box-shadow:0 6px 16px rgba(59,130,246,.35)}
.lmodal-title-v2{font-size:14.5px;font-weight:800;color:var(--t1)}
.lmodal-sub-v2{font-size:10.5px;color:var(--t3);margin-top:2px}
.lmodal-search{margin-top:14px;position:relative}
.lmodal-search input{width:100%;padding:10px 38px 10px 13px;border-radius:11px;border:1px solid var(--card-b);background:rgba(0,0,0,.2);color:var(--t1);font-family:inherit;font-size:12px;outline:none}
[data-theme="light"] .lmodal-search input{background:#fff}
.lmodal-search input:focus{border-color:rgba(59,130,246,.5);box-shadow:0 0 0 3px rgba(59,130,246,.1)}
.lmodal-search i{position:absolute;left:12px;top:50%;transform:translateY(-50%);color:var(--t3);font-size:14px}
.lmodal-quickbar{display:flex;gap:8px;margin-top:11px;position:relative;z-index:1}
.lmodal-qbtn{font-size:10px;font-weight:700;padding:5px 11px;border-radius:8px;background:var(--accent-d);color:var(--accent2);border:1px solid var(--card-b);cursor:pointer;transition:.15s;font-family:inherit}
.lmodal-qbtn:hover{background:rgba(59,130,246,.2)}
.lmodal-count{margin-right:auto;font-size:10.5px;color:var(--t3);display:flex;align-items:center}

.lmodal-list{padding:10px 14px;max-height:360px;overflow-y:auto}
/* مودال مدیریت کانفیگ‌های گروه - لایه‌بندی flex برای حذف دوبل اسکرول */
#modal-links .modal-v2{overflow:hidden !important}
#modal-links .lmodal-list{max-height:none;flex:1;min-height:0}
.lrow-v2{display:flex;align-items:center;gap:11px;padding:11px 12px;border-radius:13px;cursor:pointer;transition:.15s;margin-bottom:4px;border:1px solid transparent}
.lrow-v2:hover{background:var(--accent-d)}
.lrow-v2.checked{background:rgba(59,130,246,.1);border-color:rgba(59,130,246,.25)}
.lrow-v2-check{width:20px;height:20px;border-radius:7px;border:2px solid var(--card-b);flex-shrink:0;display:flex;align-items:center;justify-content:center;transition:.15s;background:rgba(0,0,0,.14)}
.lrow-v2.checked .lrow-v2-check{background:var(--accent);border-color:var(--accent)}
.lrow-v2-check i{font-size:12px;color:#fff;opacity:0;transform:scale(.5);transition:.15s}
.lrow-v2.checked .lrow-v2-check i{opacity:1;transform:scale(1)}
.lrow-v2-avatar{width:34px;height:34px;border-radius:10px;background:var(--accent-d);color:var(--accent);display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0}
.lrow-v2.checked .lrow-v2-avatar{background:var(--accent);color:#fff}
.lrow-v2-info{flex:1;min-width:0}
.lrow-v2-name{font-size:12.5px;font-weight:700;color:var(--t1);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.lrow-v2-meta{font-size:9.5px;color:var(--t3);margin-top:2px;display:flex;align-items:center;gap:6px}
.lrow-v2-status{font-size:9px;font-weight:800;padding:3px 9px;border-radius:20px;flex-shrink:0;white-space:nowrap}
.lrow-v2-status.on{background:var(--green-bg);color:var(--green-t)}
.lrow-v2-status.off{background:var(--red-bg);color:var(--red-t)}

.lmodal-footer{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:16px 24px;border-top:1px solid var(--card-b)}
.lmodal-footer-info{font-size:10.5px;color:var(--t3);display:flex;align-items:center;gap:6px}
.lmodal-footer-info i{color:var(--accent)}
.lmodal-footer-btns{display:flex;gap:8px}

@media(max-width:500px){.sub-grid{grid-template-columns:1fr}.sub-card-stats{grid-template-columns:repeat(3,1fr)}}

.modal-bg{display:none;position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:500;align-items:center;justify-content:center;backdrop-filter:blur(4px)}
.modal-bg.open{display:flex}
.modal{background:var(--card);border:1px solid var(--card-b);border-radius:20px;padding:28px 26px;max-width:520px;width:calc(100% - 32px);max-height:90vh;overflow-y:auto;position:relative;animation:fi .2s ease}
.modal-close{position:absolute;top:14px;left:14px;background:var(--accent-d);border:1px solid var(--card-b);color:var(--t2);width:30px;height:30px;border-radius:8px;font-size:16px;display:flex;align-items:center;justify-content:center;cursor:pointer;border:none}
.modal-title{font-size:16px;font-weight:700;color:var(--t1);margin-bottom:18px;display:flex;align-items:center;gap:8px}
.modal-title i{color:var(--accent)}
.lrow{display:flex;align-items:center;gap:8px;padding:7px 0;border-bottom:1px solid rgba(59,130,246,.05)}
.lrow:last-child{border-bottom:none}
.lrow-check{width:16px;height:16px;border-radius:4px;cursor:pointer;accent-color:var(--accent)}
.lrow-label{flex:1;font-size:12px;color:var(--t1)}
.lrow-badge{font-size:9px;padding:2px 7px;border-radius:5px;background:var(--green-bg);color:var(--green-t);font-weight:700}
.toast{position:fixed;bottom:22px;left:50%;transform:translateX(-50%) translateY(40px);background:var(--card);border:1px solid var(--card-b);color:var(--t1);border-radius:10px;padding:10px 18px;font-size:12.5px;opacity:0;transition:all .25s;z-index:999;pointer-events:none;display:flex;align-items:center;gap:8px;box-shadow:var(--shadow);white-space:nowrap}
.toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
.toast.ok{border-color:rgba(16,185,129,.3);background:var(--green-bg);color:var(--green-t)}
.toast.err{border-color:rgba(239,68,68,.3);background:var(--red-bg);color:var(--red-t)}
/* ══════ نوار اعلان‌های همگانی ══════ */
.ann-banner-wrap{display:flex;flex-direction:column;gap:10px;margin-bottom:18px}
.ann-card{position:relative;display:flex;gap:13px;background:var(--card);border:1px solid var(--card-b);border-radius:16px;padding:15px 44px 15px 17px;box-shadow:var(--shadow);animation:fi .25s ease;overflow:hidden}
.ann-card::before{content:'';position:absolute;top:0;right:0;width:4px;height:100%}
.ann-card.news::before{background:var(--accent)}
.ann-card.ad::before{background:var(--purple)}
.ann-card.warning::before{background:var(--amber)}
.ann-card.urgent::before{background:var(--red)}
.ann-icon{width:38px;height:38px;border-radius:11px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0}
.ann-card.news .ann-icon{background:var(--accent-d);color:var(--accent2)}
.ann-card.ad .ann-icon{background:var(--purple-bg);color:var(--purple)}
.ann-card.warning .ann-icon{background:var(--amber-bg);color:var(--amber-t)}
.ann-card.urgent .ann-icon{background:var(--red-bg);color:var(--red-t)}
.ann-body{flex:1;min-width:0}
.ann-title{font-size:13px;font-weight:700;color:var(--t1);margin-bottom:4px}
.ann-text{font-size:12px;color:var(--t2);line-height:1.8}
.ann-img{max-width:100%;border-radius:10px;margin-top:10px;border:1px solid var(--card-b);display:block}
.ann-close{position:absolute;top:10px;left:10px;width:24px;height:24px;border-radius:7px;background:var(--accent-d);border:none;color:var(--t3);font-size:13px;display:flex;align-items:center;justify-content:center;cursor:pointer;transition:.15s}
.ann-close:hover{background:var(--red-bg);color:var(--red-t)}
.dash-footer{border-top:1px solid var(--card-b);margin-top:14px;padding-top:14px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px}
.df-text{font-size:10px;color:var(--t3)}
.df-link{font-size:11.5px;color:var(--accent2);display:flex;align-items:center;gap:5px;font-weight:600}

.info-strip{display:flex;align-items:center;background:var(--card);border:1px solid var(--card-b);border-radius:16px;padding:16px 22px;margin-bottom:16px;gap:0;flex-wrap:wrap;box-shadow:var(--shadow)}
.info-item{display:flex;flex-direction:column;gap:6px;flex:1;min-width:130px;padding:0 18px;position:relative}
.info-item:not(:first-child)::before{content:'';position:absolute;right:0;top:2px;bottom:2px;width:1px;background:var(--card-b)}
.info-item-label{font-size:10.5px;color:var(--t3);font-weight:700}
.info-item-val{display:flex;align-items:center;gap:7px;font-size:15px;font-weight:800;color:var(--t1);letter-spacing:-.01em}
.info-item-val i{color:var(--accent);font-size:16px}
.info-item-val .info-badge{font-size:11px;font-weight:800;background:var(--green-bg);color:var(--green-t);padding:2px 9px;border-radius:20px}
@media(max-width:760px){.info-strip{gap:14px}.info-item{min-width:45%;padding:0 0 10px}.info-item:not(:first-child)::before{display:none}}

/* ══════ کانفیگ‌ها - طراحی ردیفی حرفه‌ای ══════ */
.cfg-grid{display:flex;flex-direction:column;gap:10px}
.cfg-card{background:var(--card);border:1px solid var(--card-b);border-radius:14px;padding:0;transition:all .2s cubic-bezier(.4,0,.2,1);position:relative;overflow:hidden}
.cfg-card:hover{border-color:var(--card-bh);box-shadow:0 6px 24px rgba(0,0,0,.18)}
.cfg-card.is-off{opacity:.6}
.cfg-card.is-exp{opacity:.78}
.cfg-row{display:flex;align-items:center;gap:16px;padding:14px 18px}
.cfg-status-dot{width:9px;height:9px;border-radius:50%;background:var(--green);flex-shrink:0;box-shadow:0 0 0 3px var(--green-bg)}
.cfg-card.is-off .cfg-status-dot{background:var(--red);box-shadow:0 0 0 3px var(--red-bg)}
.cfg-card.is-exp .cfg-status-dot{background:var(--amber);box-shadow:0 0 0 3px var(--amber-bg)}
.cfg-identity{display:flex;flex-direction:column;gap:3px;min-width:150px;flex-shrink:0}
.cfg-label{font-size:13.5px;font-weight:700;color:var(--t1);display:flex;align-items:center;gap:7px}
.cfg-sub-meta{display:flex;align-items:center;gap:8px;font-size:10px;color:var(--t3)}
.cfg-uuid-mini{font-family:ui-monospace,monospace;font-size:9.5px;color:var(--accent2);background:var(--accent-d);padding:2px 7px;border-radius:5px;cursor:pointer;transition:.15s}
.cfg-uuid-mini:hover{background:rgba(59,130,246,.2)}
.cfg-divider-v{width:1px;align-self:stretch;background:var(--card-b);flex-shrink:0}
.cfg-usage-col{flex:1;min-width:160px;display:flex;flex-direction:column;gap:5px}
.ubar{height:5px;border-radius:4px;background:rgba(59,130,246,0.1);overflow:hidden}
.ubar-f{height:100%;border-radius:4px;transition:width .4s ease}
.utxt{font-size:10px;color:var(--t3);display:flex;justify-content:space-between}
.cfg-exp-col{flex-shrink:0;min-width:110px}
.cfg-badges-col{display:flex;flex-direction:column;gap:5px;flex-shrink:0;align-items:flex-end}
.cfg-actions{display:flex;gap:5px;flex-shrink:0}
.proto-chip{font-size:9px;padding:3px 8px;border-radius:6px;font-weight:700;white-space:nowrap}
.pc-ws{background:var(--accent-d);color:var(--accent2)}
.pc-xhttp{background:var(--purple-bg);color:#A78BFA}
.pc-ultra{background:var(--green-bg);color:var(--green-t)}
.pc-ss{background:var(--purple-bg);color:#A78BFA}
.cfg-sub-tag{font-size:9.5px;color:var(--t3);display:flex;align-items:center;gap:4px;white-space:nowrap}
.cfg-sub-tag i{color:var(--purple);font-size:11px}
.tog{width:19px;height:30px;border-radius:19px;background:rgba(100,116,139,0.25);position:relative;cursor:pointer;transition:.2s;flex-shrink:0;border:none}
.tog::after{content:'';position:absolute;width:13px;height:13px;border-radius:50%;background:#fff;left:3px;top:3px;transition:.2s;box-shadow:0 1px 3px rgba(0,0,0,.3)}
.tog.on::after{top:14px}
.tog.on{background:var(--green)}

/* ── انتخاب گروهی کانفیگ‌ها ── */
.cfg-check{width:19px;height:19px;border-radius:6px;border:2px solid var(--card-b);flex-shrink:0;display:flex;align-items:center;justify-content:center;cursor:pointer;transition:.15s;background:rgba(0,0,0,.14)}
.cfg-check:hover{border-color:var(--accent)}
.cfg-check.checked{background:var(--accent);border-color:var(--accent)}
.cfg-check i{font-size:11px;color:#fff;opacity:0;transform:scale(.5);transition:.15s}
.cfg-check.checked i{opacity:1;transform:scale(1)}
.cfg-card.selected{border-color:rgba(59,130,246,.5);box-shadow:0 0 0 2px rgba(59,130,246,.14)}
.links-selectall{display:flex;align-items:center;gap:7px;font-size:11px;color:var(--t3);cursor:pointer;user-select:none;padding:6px 4px;transition:.15s}
.links-selectall:hover{color:var(--t1)}
.links-bulkbar{display:none;align-items:center;gap:12px;background:var(--card);border:1px solid rgba(59,130,246,.3);border-radius:14px;padding:10px 16px;margin-bottom:12px;animation:bulkbarIn .18s ease}
.links-bulkbar.show{display:flex}
@keyframes bulkbarIn{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:translateY(0)}}
.links-bulkbar-count{font-size:12px;font-weight:700;color:var(--t1);display:flex;align-items:center;gap:6px;white-space:nowrap}
.links-bulkbar-count i{color:var(--accent)}
.links-bulkbar-actions{display:flex;gap:8px;margin-right:auto;flex-wrap:wrap}

/* ══════════════ صفحه‌ی نود — اتصال چند پنل به هم ══════════════ */
/* امضای بصری این بخش: نقشه‌ی «صورت‌فلکی» — نقطه‌ها (پنل‌ها) با خط‌چین متحرک (لینک نود) به هم وصل می‌شوند */
@keyframes nodeflow{to{stroke-dashoffset:-120}}
@keyframes nodering{0%{transform:scale(.86);opacity:.85}100%{transform:scale(1.45);opacity:0}}
@keyframes nodefloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}

.node-hero{position:relative;overflow:hidden;border-radius:18px;border:1px solid var(--card-b);
  background:linear-gradient(160deg,rgba(59,130,246,.11) 0%,rgba(139,92,246,.07) 48%,var(--card) 100%);
  padding:18px 20px 16px;margin-bottom:14px;isolation:isolate}
.node-hero-net{position:absolute;inset:0;z-index:0;opacity:.65;pointer-events:none}
.node-hero-net svg{width:100%;height:100%}
.node-hero-net .nh-line{stroke:var(--card-bh);stroke-width:1.1;fill:none;stroke-dasharray:2 7;animation:nodeflow 7s linear infinite}
.node-hero-net .nh-dot{fill:var(--accent2)}
.node-hero-top{position:relative;z-index:1;display:flex;align-items:flex-start;justify-content:space-between;gap:14px;flex-wrap:wrap}
.node-hero-title{display:flex;align-items:center;gap:14px}
.node-hero-icon{width:48px;height:48px;border-radius:15px;flex-shrink:0;position:relative;
  background:linear-gradient(135deg,var(--accent),var(--purple));display:flex;align-items:center;justify-content:center;
  color:#fff;font-size:22px;box-shadow:0 10px 22px -4px rgba(79,107,255,.45);animation:nodefloat 4.5s ease-in-out infinite}
.node-hero-icon::after{content:'';position:absolute;inset:-6px;border-radius:18px;border:1.5px solid rgba(139,146,255,.4);animation:nodering 2.6s ease-out infinite}
.node-hero .tb-title{font-size:18px}
.node-hero .tb-sub{max-width:420px}
.node-hero-metrics{position:relative;z-index:1;display:grid;grid-template-columns:repeat(4,1fr);gap:9px;margin-top:16px}
.node-metric{background:rgba(0,0,0,.14);border:1px solid var(--card-b);border-radius:12px;padding:10px 12px;transition:.2s}
.node-metric:hover{border-color:var(--card-bh);transform:translateY(-2px)}
.node-metric-top{display:flex;align-items:center;gap:7px;margin-bottom:8px}
.node-metric-top i{font-size:14px;color:var(--accent2)}
.node-metric-label{font-size:9.5px;color:var(--t3);font-weight:700;text-transform:uppercase;letter-spacing:.05em}
.node-metric-val{font-size:19px;font-weight:800;color:var(--t1);letter-spacing:-.02em;line-height:1}
.node-metric-sub{font-size:9.5px;color:var(--t3);margin-top:6px}

/* ── کلیدهای صادرشده (مینیمال) ── */
.node-keys-card{position:relative;border-radius:16px;padding:1px;background:linear-gradient(135deg,rgba(59,130,246,.28),rgba(139,92,246,.2));margin-bottom:16px}
.node-keys-card>.card{border-radius:15px;margin:0;border:none;background:var(--card)}
.node-key-row{display:flex;align-items:center;gap:11px;padding:11px 8px;border-bottom:1px solid rgba(59,130,246,.07);transition:.15s}
.node-key-row:last-child{border-bottom:none}
.node-key-row:hover{background:rgba(59,130,246,.035)}
.node-key-row.off{opacity:.55}
.node-key-dot{width:7px;height:7px;border-radius:50%;background:var(--green);flex-shrink:0;box-shadow:0 0 0 3px var(--green-bg)}
.node-key-row.off .node-key-dot{background:var(--t3);box-shadow:0 0 0 3px rgba(0,0,0,.12)}
.node-key-body{min-width:0;flex:1;display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.node-key-label{font-size:11.5px;font-weight:700;color:var(--t1);display:flex;align-items:center;gap:6px;white-space:nowrap;flex-shrink:0}
.node-key-label i{font-size:11px;color:var(--accent2)}
.node-key-val{font-family:ui-monospace,Menlo,monospace;font-size:10px;color:var(--t3);direction:ltr;
  background:rgba(0,0,0,.16);border:1px solid var(--card-b);border-radius:7px;padding:4px 10px;cursor:pointer;
  flex:1;min-width:90px;max-width:260px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;transition:.15s;
  display:inline-flex;align-items:center;gap:5px;line-height:1.6}
.node-key-val:hover{color:var(--t1);border-color:var(--accent)}
.node-key-val i{font-size:9.5px;color:var(--accent2);flex-shrink:0}
.node-key-state{font-size:9.5px;color:var(--t3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex-shrink:1}
.node-key-perms{display:flex;gap:4px;align-items:center;margin-top:6px;flex-wrap:wrap}
.node-perm-ic{width:19px;height:19px;border-radius:6px;background:var(--accent-d);color:var(--accent2);display:flex;align-items:center;justify-content:center;font-size:10px}
.node-perm-ic.off{background:rgba(0,0,0,.14);color:var(--t3);opacity:.45}
.node-perm-ic.manage{background:var(--amber-bg);color:var(--amber-t)}
.node-key-meta{font-size:9.5px;color:var(--t3);margin-right:auto;text-align:left;white-space:nowrap}
.node-key-actions{display:flex;gap:5px;flex-shrink:0;margin-right:auto}
@media(max-width:640px){
  .node-key-row{align-items:flex-start;flex-wrap:wrap}
  .node-key-body{flex-direction:column;align-items:flex-start;gap:5px}
  .node-key-val{max-width:100%;width:100%}
  .node-key-actions{margin-right:0;width:100%;justify-content:flex-end}
}

/* ── گرید نودهای متصل (طراحی جدید) ── */
.nodes-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:16px}
.node-card{background:var(--card);border:1px solid var(--card-b);border-radius:18px;overflow:hidden;
  display:flex;flex-direction:column;transition:.25s cubic-bezier(.2,.8,.3,1);position:relative;isolation:isolate}
.node-card::before{content:'';position:absolute;inset:0;z-index:0;opacity:0;transition:.25s;
  background:radial-gradient(120% 90% at 0% 0%,rgba(59,130,246,.08),transparent 60%)}
.node-card:hover{transform:translateY(-4px);border-color:var(--card-bh);box-shadow:0 16px 32px -14px rgba(0,0,0,.35)}
.node-card:hover::before{opacity:1}
.node-card-bar{height:3px;background:linear-gradient(90deg,var(--green),var(--accent2),var(--purple));background-size:200% 100%;animation:nodebarflow 4s linear infinite}
@keyframes nodebarflow{to{background-position:-200% 0}}
.node-card.is-off .node-card-bar{background:var(--t3);opacity:.3;animation:none}
.node-card.is-err .node-card-bar{background:var(--red);animation:none}
.node-card.is-off{opacity:.6}
.node-card.is-err{border-color:rgba(239,68,68,.3)}
.node-card-body{position:relative;z-index:1;padding:17px 18px 15px;display:flex;flex-direction:column;gap:15px}

.node-head{display:flex;align-items:flex-start;gap:12px}
.node-avatar{width:42px;height:42px;border-radius:13px;display:flex;align-items:center;justify-content:center;flex-shrink:0;position:relative;
  background:linear-gradient(135deg,var(--accent),var(--purple));box-shadow:0 6px 16px -4px rgba(79,107,255,.4)}
.node-avatar i{font-size:19px;color:#fff}
.node-card.is-off .node-avatar,.node-card.is-err .node-avatar{background:linear-gradient(135deg,var(--t3),#555);box-shadow:none}
.node-card.is-err .node-avatar{background:linear-gradient(135deg,var(--red),#B91C1C)}
.node-avatar.online::after{content:'';position:absolute;inset:-4px;border-radius:15px;border:1.5px solid var(--green);opacity:.7;animation:nodering 2.2s ease-out infinite}
.node-avatar-dot{position:absolute;bottom:-2px;left:-2px;width:12px;height:12px;border-radius:50%;background:var(--green);border:2.5px solid var(--card);box-shadow:0 0 0 1px rgba(16,185,129,.3)}
.node-card.is-off .node-avatar-dot{background:var(--t3)}
.node-card.is-err .node-avatar-dot{background:var(--red)}
.node-titles{min-width:0;flex:1;padding-top:1px}
.node-name{font-size:13.5px;font-weight:800;color:var(--t1);display:flex;align-items:center;gap:7px;flex-wrap:wrap;letter-spacing:-.01em}
.node-host{font-size:10px;color:var(--t3);direction:ltr;text-align:right;word-break:break-all;margin-top:4px;
  display:inline-flex;align-items:center;gap:4px;font-family:ui-monospace,Menlo,monospace;cursor:pointer;transition:.15s}
.node-host:hover{color:var(--t2)}
.node-host i{font-size:10px;color:var(--t3);flex-shrink:0}
.node-meta{font-size:9.5px;color:var(--t3);display:flex;align-items:center;gap:5px;margin-top:6px}
.node-meta i{font-size:10px;color:var(--accent2)}
.node-err{background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.2);border-radius:10px;padding:9px 11px;font-size:10.5px;color:var(--red-t);line-height:1.7;word-break:break-word;display:flex;gap:7px;align-items:flex-start}
.node-err i{margin-top:1px;flex-shrink:0}

.node-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.node-stat{background:rgba(0,0,0,.15);border:1px solid transparent;border-radius:12px;padding:11px 6px;text-align:center;transition:.18s}
.node-stat:hover{background:rgba(0,0,0,.25);border-color:var(--card-b);transform:translateY(-1px)}
.node-stat i{font-size:12px;color:var(--accent2);margin-bottom:5px;display:block}
.node-stat-val{font-size:12.5px;font-weight:800;color:var(--t1);letter-spacing:-.01em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.node-stat-label{font-size:8.5px;color:var(--t3);margin-top:3px}

.node-perms{display:flex;flex-wrap:wrap;gap:6px}
.node-perm{display:flex;align-items:center;gap:5px;font-size:9.5px;color:var(--t3);background:rgba(0,0,0,.12);border:1px solid var(--card-b);border-radius:18px;padding:4px 9px 4px 5px;cursor:pointer;user-select:none;transition:.15s}
.node-perm:hover{border-color:var(--accent);color:var(--t2)}
.node-perm.on{color:var(--t1);border-color:rgba(59,130,246,.35);background:var(--accent-d)}
.node-perm .cfg-check{width:13px;height:13px;border-radius:4px;border-width:2px}
.node-perm .cfg-check i{font-size:7.5px}

.node-foot{display:flex;align-items:center;gap:8px;border-top:1px solid var(--card-b);padding:11px 17px;background:rgba(0,0,0,.12);position:relative;z-index:1}
.node-foot .btn{flex:1;justify-content:center}
.node-origin{background:linear-gradient(135deg,rgba(139,92,246,.18),rgba(109,72,214,.12));color:#A78BFA;padding:3px 9px;border-radius:20px;border:1px solid rgba(139,92,246,.25);font-weight:700;font-size:10px;display:inline-flex;align-items:center;gap:4px}

/* ── دسترسی‌ها در مودال ساخت کلید: کاشی‌های انتخابی ── */
.nk-perm-grid{display:grid;grid-template-columns:1fr 1fr;gap:9px}
.nk-perm-tile{display:flex;align-items:center;gap:10px;padding:11px 12px;border-radius:13px;border:1px solid var(--card-b);background:rgba(0,0,0,.16);cursor:pointer;transition:.16s;user-select:none}
.nk-perm-tile:hover{border-color:var(--accent);transform:translateY(-1px)}
.nk-perm-tile.on{border-color:rgba(59,130,246,.5);background:var(--accent-d)}
.nk-perm-tile .nk-perm-tile-ic{width:30px;height:30px;border-radius:9px;background:rgba(0,0,0,.22);display:flex;align-items:center;justify-content:center;color:var(--t3);font-size:14px;flex-shrink:0;transition:.16s}
.nk-perm-tile.on .nk-perm-tile-ic{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff}
.nk-perm-tile-txt{min-width:0}
.nk-perm-tile-name{font-size:11px;font-weight:700;color:var(--t1)}
.nk-perm-tile-desc{font-size:9px;color:var(--t3);margin-top:2px;line-height:1.45}
.nk-perm-tile.manage{grid-column:1/-1;margin-top:2px;border-top:1px dashed var(--card-b);padding-top:14px;position:relative}
.nk-perm-tile.manage::before{content:'دسترسی نوشتن';position:absolute;top:-8px;right:12px;background:var(--card);padding:0 6px;font-size:8.5px;font-weight:800;color:var(--t3);letter-spacing:.04em;line-height:1.4;z-index:1}
.nk-perm-tile.manage.on{border-color:rgba(245,158,11,.55);background:var(--amber-bg)}
.nk-perm-tile.manage.on .nk-perm-tile-ic{background:linear-gradient(135deg,var(--amber),#D97706)}

/* ── پیش‌نمایش هاست در مودال اتصال ── */
.nc-host-chip{display:inline-flex;align-items:center;gap:7px;background:var(--accent-d);border:1px solid var(--card-b);
  border-radius:20px;padding:7px 13px;font-size:11px;color:var(--t2);direction:ltr;font-family:ui-monospace,Menlo,monospace;margin-top:8px}
.nc-host-chip i{color:var(--accent2);font-size:13px}

/* ── نمای خالی اختصاصی نود ── */
.node-empty-illust{width:74px;height:74px;margin:0 auto 16px;position:relative}
.node-empty-illust svg{width:100%;height:100%}
.node-empty-illust .ne-line{stroke:var(--card-bh);stroke-width:1.4;stroke-dasharray:3 6;fill:none;animation:nodeflow 5s linear infinite}
.node-empty-illust .ne-dot{fill:var(--accent2)}
.node-empty-illust .ne-dot.mid{fill:var(--purple)}

@media(max-width:880px){
  .cfg-row{flex-wrap:wrap}
  .cfg-divider-v{display:none}
  .cfg-usage-col{min-width:100%;order:5}
}

/* ── زیر ۷۶۸px: تبدیل کامل به کارت موبایل ── */
@media(max-width:768px){
  .cfg-grid{display:grid;grid-template-columns:1fr;gap:13px}
  .cfg-card{border-radius:16px}
  .cfg-row{flex-direction:column;align-items:stretch;gap:12px;padding:16px}
  .cfg-row-top{display:flex;align-items:center;justify-content:space-between;gap:10px}
  .cfg-identity{min-width:0;flex:1}
  .cfg-usage-col{min-width:0}
  .cfg-exp-col{min-width:0}
  .cfg-badges-col{flex-direction:row;align-items:center;flex-wrap:wrap}
  .cfg-actions{flex-wrap:wrap;border-top:1px solid var(--card-b);padding-top:10px;margin-top:2px;width:100%}
}

/* ══════ اتصالات فعال با IP ══════ */
.conn-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px}
.conn-card{background:var(--card);border:1px solid var(--card-b);border-radius:16px;padding:15px 17px;transition:.2s;position:relative;overflow:hidden}
.conn-card:hover{border-color:var(--card-bh);transform:translateY(-1px)}
.conn-card::before{content:'';position:absolute;top:0;right:0;width:3px;height:100%;background:var(--green)}
.conn-ip-row{display:flex;align-items:center;gap:8px;margin-bottom:10px}
.conn-ip-icon{width:32px;height:32px;border-radius:9px;background:var(--green-bg);color:var(--green-t);display:flex;align-items:center;justify-content:center;font-size:15px;flex-shrink:0}
.conn-ip{font-family:ui-monospace,monospace;font-size:13px;font-weight:700;color:var(--t1)}
.conn-label{font-size:10.5px;color:var(--t3);margin-top:1px}
.conn-meta{display:flex;justify-content:space-between;align-items:center;font-size:10px;color:var(--t3);padding-top:10px;border-top:1px solid var(--card-b)}

/* ══════ لاگ فعالیت‌ها ══════ */
.log-timeline{display:flex;flex-direction:column}
.log-item{display:flex;gap:12px;padding:11px 0;border-bottom:1px solid rgba(59,130,246,.05);position:relative}
.log-item:last-child{border-bottom:none}
.log-ic{width:30px;height:30px;border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0}
.log-ic.ok{background:var(--green-bg);color:var(--green-t)}
.log-ic.err{background:var(--red-bg);color:var(--red-t)}
.log-ic.warn{background:var(--amber-bg);color:var(--amber-t)}
.log-ic.info{background:var(--accent-d);color:var(--accent2)}
.log-body{flex:1;min-width:0}
.log-msg{font-size:12.5px;color:var(--t1);line-height:1.6}
.log-time{font-size:9.5px;color:var(--t3);margin-top:2px;display:flex;align-items:center;gap:5px}
.log-kind{font-size:8.5px;padding:1px 7px;border-radius:10px;background:var(--accent-d);color:var(--accent2);font-weight:700;text-transform:uppercase;letter-spacing:.04em}
.erow{padding:9px 0;border-bottom:1px solid rgba(59,130,246,.05)}
.erow:last-child{border-bottom:none}
.etime{color:var(--t3);font-size:9.5px;margin-bottom:3px;display:flex;align-items:center;gap:4px}
.emsg{color:var(--red-t);font-family:ui-monospace,monospace;background:var(--red-bg);padding:6px 9px;border-radius:6px;word-break:break-all;font-size:10.5px}

@media(max-width:1050px){
  .sidebar{transform:translateX(100%)}
  .sidebar.open{transform:translateX(0);box-shadow:-10px 0 40px rgba(0,0,0,.4)}
  .sb-close{display:flex}
  .main{margin-right:0;padding-top:70px}
  .mob-top{display:flex}
  .metrics{grid-template-columns:1fr 1fr}
  .g2,.g3{grid-template-columns:1fr}
}
@media(max-width:500px){
  .metrics{grid-template-columns:1fr}
  .main{padding:62px 12px 50px}
  .sub-grid,.cfg-grid,.conn-grid{grid-template-columns:1fr}
}
/* ══════ نسخه و بروزرسانی — دیزاین جدید ══════ */
.upd-hero{background:linear-gradient(150deg,var(--bg3) 0%,var(--card) 65%);border:1px solid var(--card-b);border-radius:24px;padding:26px 26px 22px;position:relative;overflow:hidden;box-shadow:var(--shadow);margin-bottom:16px}
.upd-hero-glow{position:absolute;top:-70px;left:-70px;width:260px;height:260px;background:radial-gradient(circle,rgba(59,130,246,.14),transparent 70%);pointer-events:none}
.upd-hero-top{display:flex;align-items:flex-start;justify-content:space-between;gap:14px;position:relative;z-index:1;flex-wrap:wrap;margin-bottom:14px}
.upd-hero-cur{display:flex;align-items:center;gap:14px}
.upd-hero-icon{width:52px;height:52px;border-radius:16px;background:linear-gradient(135deg,var(--accent),var(--accent2));display:flex;align-items:center;justify-content:center;color:#fff;font-size:24px;flex-shrink:0;box-shadow:0 8px 22px rgba(59,130,246,.35)}
.upd-hero-label{font-size:10.5px;color:var(--t3);font-weight:700;text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px}
.upd-hero-ver{font-size:26px;font-weight:800;color:var(--t1);letter-spacing:-.02em}
.upd-hero-desc{font-size:12.5px;color:var(--t2);line-height:1.8;position:relative;z-index:1;margin-bottom:14px;background:rgba(0,0,0,.14);border:1px solid var(--card-b);border-radius:12px;padding:12px 14px}
[data-theme="light"] .upd-hero-desc{background:rgba(37,99,235,.03)}
.upd-hero-meta{display:flex;gap:8px;flex-wrap:wrap;position:relative;z-index:1}
.upd-meta-chip{display:flex;align-items:center;gap:6px;font-size:10.5px;font-weight:700;color:var(--t2);background:var(--accent-d);border:1px solid var(--card-b);padding:6px 12px;border-radius:20px}
.upd-meta-chip i{color:var(--accent);font-size:13px}
.upd-pill{display:inline-flex;align-items:center;gap:6px;font-size:11px;font-weight:800;padding:6px 14px;border-radius:20px}
.upd-pill-blue{background:var(--accent-d);color:var(--accent2)}
.upd-pill-green{background:var(--green-bg);color:var(--green-t)}
.upd-pill-amber{background:var(--amber-bg);color:var(--amber-t)}
.upd-dot{width:6px;height:6px;border-radius:50%;background:currentColor;animation:pulse 1.6s infinite}

.upd-latest-card{background:linear-gradient(120deg,var(--amber) 0%,#D97706 100%);border-radius:22px;padding:20px 24px;display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-bottom:16px;box-shadow:0 12px 32px rgba(245,158,11,.28);position:relative;overflow:hidden}
.upd-latest-card::before{content:'';position:absolute;top:-40px;left:-40px;width:180px;height:180px;background:radial-gradient(circle,rgba(255,255,255,.18),transparent 70%);pointer-events:none}
.upd-latest-left{display:flex;align-items:center;gap:14px;position:relative;z-index:1;min-width:220px}
.upd-latest-icon{width:48px;height:48px;border-radius:14px;background:rgba(255,255,255,.22);display:flex;align-items:center;justify-content:center;color:#fff;font-size:22px;flex-shrink:0}
.upd-latest-title{font-size:13px;font-weight:800;color:#fff;opacity:.92}
.upd-latest-ver{font-size:18px;font-weight:800;color:#fff;margin-top:2px}
.upd-latest-desc{font-size:11.5px;color:rgba(255,255,255,.88);margin-top:4px;line-height:1.7;max-width:440px}
.upd-install-btn{background:#fff;color:#B45309;border:none;border-radius:14px;padding:13px 24px;font-family:inherit;font-size:13.5px;font-weight:800;cursor:pointer;display:flex;align-items:center;gap:8px;box-shadow:0 6px 18px rgba(0,0,0,.18);transition:.18s;position:relative;z-index:1;white-space:nowrap}
.upd-install-btn:hover{transform:translateY(-2px);box-shadow:0 10px 24px rgba(0,0,0,.24)}
.upd-install-btn:active{transform:translateY(0) scale(.98)}
.upd-install-btn:disabled{opacity:.6;cursor:not-allowed;transform:none}

.upd-progress-card{background:var(--card);border:1px solid var(--card-b);border-radius:18px;padding:18px 20px;margin-bottom:16px;box-shadow:var(--shadow)}
.upd-progress-head{display:flex;align-items:center;gap:12px;margin-bottom:12px}
.upd-progress-icon{width:38px;height:38px;border-radius:11px;background:var(--accent-d);color:var(--accent);display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0}
.upd-progress-title{font-size:13px;font-weight:800;color:var(--t1)}
.upd-progress-txt{font-size:10.5px;color:var(--t3);margin-top:2px}
.upd-progress-pct{font-size:16px;font-weight:800;color:var(--accent2);flex-shrink:0}
.upd-progress-track{height:8px;border-radius:6px;background:var(--accent-d);overflow:hidden}
.upd-progress-fill{height:100%;border-radius:6px;background:linear-gradient(90deg,var(--accent),var(--accent2));transition:width .4s ease;position:relative;overflow:hidden}
.upd-progress-fill::after{content:'';position:absolute;inset:0;background:linear-gradient(90deg,transparent,rgba(255,255,255,.4),transparent);width:40%;animation:shimmer 1.6s linear infinite}

.upd-log-card{background:var(--card);border:1px solid var(--card-b);border-radius:18px;padding:18px 20px;margin-bottom:20px;box-shadow:var(--shadow)}
.upd-log-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px}
.upd-log-title{font-size:12.5px;font-weight:800;color:var(--t1);display:flex;align-items:center;gap:7px}
.upd-log-title i{color:var(--accent);font-size:16px}
.upd-log-box{background:rgba(0,0,0,.3);border:1px solid var(--card-b);border-radius:12px;padding:14px 16px;max-height:240px;overflow-y:auto;font-family:ui-monospace,monospace;font-size:10.5px;line-height:2}
[data-theme="light"] .upd-log-box{background:rgba(0,0,0,.03)}
.upd-log-empty{color:var(--t3)}
.upd-log-line{color:var(--t2);white-space:pre-wrap;word-break:break-all}
.upd-log-line.err{color:var(--red-t)}
.upd-log-line.ok{color:var(--green-t)}

.upd-history-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}
.upd-history-title{font-size:13px;font-weight:800;color:var(--t1);display:flex;align-items:center;gap:7px}
.upd-history-title i{color:var(--accent);font-size:17px}

.upd-timeline{position:relative;display:flex;flex-direction:column;gap:0}
.upd-timeline::before{content:'';position:absolute;top:8px;bottom:8px;right:19px;width:2px;background:linear-gradient(180deg,var(--card-b),transparent)}
.upd-item{display:flex;gap:16px;padding:0 0 20px;position:relative}
.upd-item:last-child{padding-bottom:0}
.upd-item-dot-wrap{position:relative;z-index:1;flex-shrink:0}
.upd-item-dot{width:40px;height:40px;border-radius:13px;background:var(--card);border:2px solid var(--green);display:flex;align-items:center;justify-content:center;color:var(--green-t);font-size:17px;box-shadow:var(--shadow)}
.upd-item.err .upd-item-dot{border-color:var(--red);color:var(--red-t)}
.upd-item-card{flex:1;background:var(--card);border:1px solid var(--card-b);border-radius:16px;padding:14px 17px;transition:.18s;min-width:0}
.upd-item-card:hover{border-color:var(--card-bh);transform:translateY(-1px)}
.upd-item-head{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-bottom:6px}
.upd-item-versions{font-size:13.5px;font-weight:800;color:var(--t1);display:flex;align-items:center;gap:8px}
.upd-item-versions .arrow{color:var(--t3);font-size:14px}
.upd-item-versions .to{color:var(--accent2)}
.upd-item-time{font-size:10px;color:var(--t3);display:flex;align-items:center;gap:5px;white-space:nowrap}
.upd-item-desc{font-size:11.5px;color:var(--t2);line-height:1.8;margin-top:6px}
.upd-item-badge{font-size:9px;font-weight:800;padding:3px 9px;border-radius:20px;flex-shrink:0}
.upd-item-badge.ok{background:var(--green-bg);color:var(--green-t)}
.upd-item-badge.err{background:var(--red-bg);color:var(--red-t)}
.upd-item-err-box{margin-top:8px;background:var(--red-bg);border:1px solid rgba(239,68,68,.2);border-radius:9px;padding:8px 11px;font-size:10.5px;color:var(--red-t);font-family:ui-monospace,monospace;word-break:break-all}
.upd-history-empty{text-align:center;padding:50px 20px;color:var(--t3);background:var(--card);border:1px dashed var(--card-b);border-radius:18px}
.upd-history-empty i{font-size:36px;opacity:.35;margin-bottom:10px;display:block}

/* ══════ پشتیبانی کاربر — ری‌دیزاین ══════ */
.sup-wrap{max-width:1450px;background:var(--card);border:1px solid var(--card-b);border-radius:24px;overflow:hidden;box-shadow:var(--shadow);position:relative}
.sup-wrap::before{content:'';position:absolute;top:-60px;left:-60px;width:200px;height:200px;background:radial-gradient(circle,var(--accent-d),transparent 70%);pointer-events:none;z-index:0}
.sup-head{display:flex;align-items:center;gap:13px;padding:18px 22px;border-bottom:1px solid var(--card-b);background:linear-gradient(155deg,var(--accent-d) 0%,transparent 75%);position:relative;z-index:1}
.sup-head-icon{width:42px;height:42px;border-radius:13px;background:linear-gradient(135deg,var(--accent),var(--accent2));display:flex;align-items:center;justify-content:center;color:#fff;font-size:19px;flex-shrink:0;box-shadow:0 6px 16px rgba(59,130,246,.35);position:relative}
.sup-head-icon::after{content:'';position:absolute;inset:-5px;border-radius:16px;border:1.5px solid var(--accent);opacity:.4;animation:supBreathe 2.4s ease-in-out infinite}
@keyframes supBreathe{0%,100%{transform:scale(1);opacity:.4}50%{transform:scale(1.1);opacity:0}}
.sup-head-text{flex:1;min-width:0}
.sup-head-title{font-size:14.5px;font-weight:800;color:var(--t1);letter-spacing:-.01em}
.sup-head-sub{font-size:10.5px;color:var(--t3);margin-top:3px;display:flex;align-items:center;gap:6px}
.sup-head-sub .sdot{width:6px;height:6px;border-radius:50%;background:var(--green);animation:pulse 1.6s infinite;flex-shrink:0}
.sup-close-btn{background:var(--red-bg);color:var(--red-t);border:1px solid rgba(239,68,68,.2);border-radius:10px;padding:8px 14px;font-family:inherit;font-size:11px;font-weight:700;cursor:pointer;display:flex;align-items:center;gap:6px;transition:.15s}
.sup-close-btn:hover{background:rgba(239,68,68,.2);transform:translateY(-1px)}
.sup-blocked-banner{background:var(--red-bg);color:var(--red-t);font-size:11.5px;font-weight:700;padding:11px 22px;display:flex;align-items:center;gap:8px;border-bottom:1px solid var(--card-b);position:relative;z-index:1}
 
#support-msgs{height:370px;overflow-y:auto;display:flex;flex-direction:column;gap:2px;padding:20px;background:var(--bg2);position:relative;z-index:1;scroll-behavior:smooth}
#support-msgs::-webkit-scrollbar{width:5px}
#support-msgs::-webkit-scrollbar-thumb{background:var(--card-b);border-radius:3px}
 
.sup-date-sep{text-align:center;font-size:9.5px;color:var(--t3);font-weight:700;margin:14px 0 10px;position:relative}
.sup-date-sep span{background:var(--bg2);padding:0 12px;position:relative;z-index:1}
.sup-date-sep::before{content:'';position:absolute;top:50%;right:0;left:0;height:1px;background:var(--card-b);z-index:0}
 
.sup-msg-row{display:flex;align-items:flex-end;gap:8px;margin-bottom:10px;max-width:100%}
.sup-msg-row.client{margin-right:0;margin-left:auto;flex-direction:row-reverse}
.sup-msg-row.admin{margin-left:0; display: flex; justify-content: left}
.sup-avatar{width:26px;height:26px;border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:12px;flex-shrink:0;margin-bottom:2px}
.sup-avatar.admin{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff}
.sup-avatar.client{background:var(--purple-bg);color:var(--purple)}
.sup-msg{padding:10px 15px;border-radius:16px;font-size:12.8px;line-height:1.75;word-break:break-word;position:relative;box-shadow:0 1px 2px rgba(0,0,0,.06)}
.sup-msg.client{background:var(--accent);color:#fff;border-bottom-right-radius:5px}
.sup-msg.admin{background:var(--card);color:var(--t1);border:1px solid var(--card-b);border-bottom-left-radius:5px}
.sup-msg .sup-time{display:flex;align-items:center;gap:4px;font-size:9px;opacity:.68;margin-top:5px;justify-content:flex-end}
.sup-msg .sup-time i{font-size:12px}
.sup-msg.client .sup-time i.seen{color:#fff}
 
.sup-empty{color:var(--t3);font-size:12px;text-align:center;padding:60px 20px;display:flex;flex-direction:column;align-items:center;gap:12px}
.sup-empty i{font-size:38px;opacity:.35}
.sup-empty b{color:var(--t2);font-size:13px;font-weight:700}
 
.sup-input-row{display:flex;gap:10px;padding:16px 18px;background:var(--card);border-top:1px solid var(--card-b);position:relative;z-index:1}
.sup-input-row input{margin-bottom:0;border-radius:13px;padding:12px 16px}
.sup-input-row button{border-radius:13px;padding:0 18px;display:flex;align-items:center;justify-content:center}
.sup-input-row.disabled{opacity:.55;pointer-events:none}
 
.sup-new-badge{display:inline-flex;align-items:center;gap:4px;background:var(--red);color:#fff;font-size:9px;font-weight:800;padding:2px 8px;border-radius:20px;margin-right:6px;animation:pulse 1.6s infinite}

/* ══════ مودال ساخت کانفیگ - نسخه حرفه‌ای ══════ */
.cm-modal{max-width:620px;width:calc(100% - 32px);padding:0;border-radius:24px;overflow:hidden;
  max-height:92vh;display:flex;flex-direction:column}
/* مودال‌هایی که به‌جای cm-head/cm-body از ساختار modal-v2-head/modal-v2-body استفاده می‌کنند
   هم باید داخل cm-modal درست اسکرول شوند و هدرشان فشرده/همپوشان نشود */
.cm-modal.modal-v2 .modal-v2-head{flex-shrink:0}
.cm-modal.modal-v2 .modal-v2-body{flex:1;overflow-y:auto;min-height:0}
.cm-head{background:linear-gradient(155deg,rgba(59,130,246,.14) 0%,transparent 70%);
  padding:26px 28px 20px;position:relative;border-bottom:1px solid var(--card-b);flex-shrink:0}
.cm-head::before{content:'';position:absolute;top:-60px;left:-60px;width:200px;height:200px;
  background:radial-gradient(circle,rgba(59,130,246,.18),transparent 70%);pointer-events:none}
.cm-head-row{display:flex;align-items:center;gap:14px;position:relative;z-index:1}
.cm-head-icon{width:46px;height:46px;border-radius:14px;background:linear-gradient(135deg,var(--accent),var(--accent2));
  display:flex;align-items:center;justify-content:center;color:#fff;font-size:21px;flex-shrink:0;
  box-shadow:0 8px 20px rgba(59,130,246,.35)}
.cm-head-title{font-size:16.5px;font-weight:800;color:var(--t1);letter-spacing:-.01em}
.cm-head-sub{font-size:11px;color:var(--t3);margin-top:3px}
.cm-close{position:absolute;top:18px;left:18px;background:rgba(0,0,0,.18);border:1px solid var(--card-b);
  color:var(--t2);width:32px;height:32px;border-radius:10px;font-size:15px;display:flex;align-items:center;
  justify-content:center;cursor:pointer;z-index:2;transition:.15s}
.cm-close:hover{background:var(--red-bg);color:var(--red-t);border-color:rgba(239,68,68,.25)}

.cm-body{padding:22px 28px 8px;overflow-y:auto;flex:1}
.cm-section{margin-bottom:20px}
.cm-section-label{font-size:10.5px;font-weight:800;color:var(--t3);text-transform:uppercase;
  letter-spacing:.08em;display:flex;align-items:center;gap:6px;margin-bottom:10px}
.cm-section-label i{color:var(--accent);font-size:14px}

.cm-field{margin-bottom:14px}
.cm-field label{display:block;font-size:11px;font-weight:700;color:var(--t2);margin-bottom:7px}
.cm-input{width:100%;padding:11px 14px;border-radius:11px;border:1px solid var(--card-b);
  background:rgba(0,0,0,.18);color:var(--t1);font-family:inherit;font-size:12.8px;outline:none;transition:.15s}
[data-theme="light"] .cm-input{background:rgba(37,99,235,.03)}
.cm-input:focus{border-color:rgba(59,130,246,.5);box-shadow:0 0 0 3px rgba(59,130,246,.1)}
.cm-input::placeholder{color:var(--t3)}
.cm-row2{display:grid;grid-template-columns:1fr 1fr;gap:12px}

/* ── آکاردئون کشویی انتخاب پروتکل / ترابرد ── */
.cm-dd{border:1px solid var(--card-b);border-radius:14px;overflow:hidden;background:rgba(0,0,0,.1);transition:.18s}
[data-theme="light"] .cm-dd{background:#fff}
.cm-dd.open{border-color:var(--card-bh);box-shadow:0 0 0 3px rgba(59,130,246,.08)}
.cm-dd-trigger{display:flex;align-items:center;gap:12px;padding:13px 15px;cursor:pointer;user-select:none}
.cm-dd-icon{width:38px;height:38px;border-radius:11px;background:var(--accent-d);color:var(--accent);
  display:flex;align-items:center;justify-content:center;font-size:17px;flex-shrink:0;transition:.18s}
.cm-dd-text{flex:1;min-width:0}
.cm-dd-title{font-size:13px;font-weight:800;color:var(--t1)}
.cm-dd-desc{font-size:10px;color:var(--t3);margin-top:2px}
.cm-dd-chev{color:var(--t3);font-size:16px;transition:transform .2s;flex-shrink:0}
.cm-dd.open .cm-dd-chev{transform:rotate(180deg);color:var(--accent)}

.cm-dd-panel{display:grid;grid-template-rows:0fr;transition:grid-template-rows .22s ease}
.cm-dd.open .cm-dd-panel{grid-template-rows:1fr}
.cm-dd-panel-inner{overflow:hidden}
.cm-dd-list{border-top:1px solid var(--card-b);padding:6px}
.cm-opt{display:flex;align-items:center;gap:11px;padding:10px 11px;border-radius:10px;cursor:pointer;transition:.14s;margin-bottom:2px}
.cm-opt:hover{background:var(--accent-d)}
.cm-opt.sel{background:rgba(59,130,246,.12)}
.cm-opt-radio{width:18px;height:18px;border-radius:50%;border:2px solid var(--card-b);flex-shrink:0;
  display:flex;align-items:center;justify-content:center;transition:.14s}
.cm-opt.sel .cm-opt-radio{border-color:var(--accent)}
.cm-opt-radio::after{content:'';width:9px;height:9px;border-radius:50%;background:var(--accent);
  transform:scale(0);transition:.14s}
.cm-opt.sel .cm-opt-radio::after{transform:scale(1)}
.cm-opt-icon{width:30px;height:30px;border-radius:9px;background:var(--accent-d);color:var(--accent);
  display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0}
.cm-opt.sel .cm-opt-icon{background:var(--accent);color:#fff}
.cm-opt-text{flex:1;min-width:0}
.cm-opt-title{font-size:12px;font-weight:700;color:var(--t1)}
.cm-opt-desc{font-size:9.5px;color:var(--t3);margin-top:1px}
.cm-opt-tag{font-size:8.5px;font-weight:800;padding:2px 7px;border-radius:6px;background:var(--green-bg);
  color:var(--green-t);flex-shrink:0}

.cm-pills{display:flex;gap:6px;flex-wrap:wrap;margin-top:9px}
.cm-pill{padding:6px 13px;border-radius:20px;font-size:10.5px;font-weight:700;color:var(--t2);
  background:transparent;border:1px solid var(--card-b);cursor:pointer;transition:.15s;font-family:inherit}
.cm-pill:hover{background:var(--accent-d)}
.cm-pill.active{background:var(--accent);color:#fff;border-color:var(--accent);box-shadow:0 3px 10px rgba(59,130,246,.3)}

.cm-note{font-size:10.5px;color:var(--t3);display:flex;align-items:flex-start;gap:7px;
  background:var(--accent-d);border-radius:10px;padding:10px 13px;line-height:1.7;margin-top:4px}
.cm-note i{color:var(--accent);font-size:14px;flex-shrink:0;margin-top:1px}

.cm-footer{display:flex;gap:10px;padding:16px 28px;border-top:1px solid var(--card-b);flex-shrink:0;
  background:var(--card)}

/* ── تم اختصاصی فیروزه‌ای برای مودال Bot TCP Proxy (تمایز بصری از بقیه مودال‌ها) ── */
#modal-bot-tcp-proxy .cm-head{background:linear-gradient(155deg,rgba(20,184,166,.16) 0%,transparent 70%)}
#modal-bot-tcp-proxy .cm-head::before{background:radial-gradient(circle,rgba(20,184,166,.2),transparent 70%)}
#modal-bot-tcp-proxy .cm-head-icon{background:linear-gradient(135deg,#14b8a6,#0d9488);box-shadow:0 8px 20px rgba(20,184,166,.35)}
#modal-bot-tcp-proxy .cm-section-label i{color:#14b8a6}
#modal-bot-tcp-proxy .cm-pill.active{background:#14b8a6;border-color:#14b8a6;box-shadow:0 3px 10px rgba(20,184,166,.3)}
#modal-bot-tcp-proxy .cm-input:focus{border-color:rgba(20,184,166,.5);box-shadow:0 0 0 3px rgba(20,184,166,.1)}
#modal-bot-tcp-proxy #btp-status-note{background:var(--accent-d);border:1px solid var(--card-b);border-radius:12px;padding:12px 14px;transition:.2s}
#modal-bot-tcp-proxy #btp-status-note.st-run{background:rgba(20,184,166,.1);border-color:rgba(20,184,166,.3)}
#modal-bot-tcp-proxy #btp-status-note.st-run #btp-status-icon{color:#14b8a6}
#modal-bot-tcp-proxy #btp-status-note.st-ok{background:var(--green-bg);border-color:rgba(34,197,94,.3)}
#modal-bot-tcp-proxy #btp-status-note.st-ok #btp-status-icon{color:var(--green-t)}
#modal-bot-tcp-proxy #btp-status-note.st-err{background:var(--red-bg);border-color:rgba(239,68,68,.3)}
#modal-bot-tcp-proxy #btp-status-note.st-err #btp-status-icon{color:var(--red-t)}
#modal-bot-tcp-proxy #btp-status-note.st-warn{background:var(--amber-bg);border-color:rgba(245,158,11,.3)}
#modal-bot-tcp-proxy #btp-status-note.st-warn #btp-status-icon{color:var(--amber-t)}
#modal-bot-tcp-proxy #btp-status-text{color:var(--t1);font-weight:600}
#modal-bot-tcp-proxy #btp-ping-status-note{background:var(--accent-d);border:1px solid var(--card-b);border-radius:12px;padding:12px 14px;transition:.2s}
#modal-bot-tcp-proxy #btp-ping-status-note.st-run{background:rgba(20,184,166,.1);border-color:rgba(20,184,166,.3)}
#modal-bot-tcp-proxy #btp-ping-status-note.st-run #btp-ping-status-icon{color:#14b8a6}
#modal-bot-tcp-proxy #btp-ping-status-note.st-ok{background:var(--green-bg);border-color:rgba(34,197,94,.3)}
#modal-bot-tcp-proxy #btp-ping-status-note.st-ok #btp-ping-status-icon{color:var(--green-t)}
#modal-bot-tcp-proxy #btp-ping-status-note.st-err{background:var(--red-bg);border-color:rgba(239,68,68,.3)}
#modal-bot-tcp-proxy #btp-ping-status-note.st-err #btp-ping-status-icon{color:var(--red-t)}
#modal-bot-tcp-proxy #btp-ping-status-text{color:var(--t1);font-weight:600}
.cm-btn-cancel{flex:.55;justify-content:center;padding:12px;border-radius:12px;background:transparent;
  border:1px solid var(--card-b);color:var(--t2);font-family:inherit;font-size:12.5px;font-weight:700;
  cursor:pointer;transition:.15s;display:flex;align-items:center}
.cm-btn-cancel:hover{background:var(--accent-d);color:var(--t1)}
.cm-btn-submit{flex:1;justify-content:center;padding:12px;border-radius:12px;
  background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;border:none;
  font-family:inherit;font-size:13px;font-weight:800;cursor:pointer;display:flex;align-items:center;
  gap:7px;box-shadow:0 6px 18px rgba(59,130,246,.4);transition:.18s}
.cm-btn-submit:hover{transform:translateY(-2px);box-shadow:0 10px 24px rgba(59,130,246,.5)}
.cm-btn-submit:active{transform:translateY(0) scale(.98)}

/* دسکتاپ بزرگ‌تر */
@media(min-width:900px){
  .cm-modal{max-width:680px}
  .cm-body{padding:24px 34px 8px}
  .cm-head{padding:28px 34px 22px}
  .cm-footer{padding:18px 34px}
  #modal-bot-tcp-proxy .cm-modal{max-width:560px}
}

/* موبایل = باتم‌شیت */
@media(max-width:640px){
  #modal-create-link.modal-bg{align-items:flex-end}
  .cm-modal{max-width:100%;width:100%;border-radius:22px 22px 0 0;max-height:90vh;
    animation:cmSlideUp .28s cubic-bezier(.32,.72,0,1)}
  .cm-row2{grid-template-columns:1fr}
  .cm-head{padding:20px 18px 16px}
  .cm-body{padding:18px 18px 6px}
  .cm-footer{padding:14px 18px 18px}
}
@keyframes cmSlideUp{from{transform:translateY(100%)}to{transform:translateY(0)}}

</style>
</head>
<body>
<div class="toast" id="toast"></div>

<div class="modal-bg" id="modal-create-link">
  <div class="modal-v2 cm-modal">
    <button class="cm-close" onclick="closeModal('modal-create-link')"><i class="ti ti-x"></i></button>
    <div class="cm-head">
      <div class="cm-head-row">
        <div class="cm-head-icon" id="cm-head-icon"><i class="ti ti-square-rounded-plus"></i></div>
        <div>
          <div class="cm-head-title" id="cm-head-title">ساخت کانفیگ جدید</div>
          <div class="cm-head-sub" id="cm-head-sub">تنظیمات کامل پروتکل، ترابرد و محدودیت‌ها در یک صفحه</div>
        </div>
      </div>
    </div>

    <div class="cm-body">

      <!-- اطلاعات پایه -->
      <div class="cm-section">
        <div class="cm-section-label"><i class="ti ti-id-badge-2"></i> اطلاعات پایه</div>
        <div class="cm-field"><label>نام کانفیگ</label>
          <input class="cm-input" id="nl-label" placeholder="مثلاً: کاربر علی">
        </div>
        <div class="cm-field" id="nl-target-wrap" style="display:none">
          <label><i class="ti ti-topology-star-3"></i> پنل مقصد</label>
          <select class="cm-input" id="nl-target" onchange="onNlTargetChange()"><option value="">این پنل</option></select>
        </div>
        <div class="cm-row2">
          <div class="cm-field" id="nl-sub-wrap"><label>گروه ساب</label>
            <select class="cm-input" id="nl-sub"><option value="">— بدون گروه —</option></select>
          </div>
          <div class="cm-field"><label>یادداشت (اختیاری)</label>
            <input class="cm-input" id="nl-note" placeholder="توضیح کوتاه">
          </div>
        </div>
      </div>

      <!-- بخش ۱: پایه -->
      <div class="cm-section">
        <div class="cm-section-label"><i class="ti ti-plug-connected"></i> پروتکل پایه</div>
        <div class="cm-dd open" id="dd-base">
          <div class="cm-dd-trigger" onclick="cmToggleDD('dd-base')">
            <div class="cm-dd-icon" id="dd-base-icon"><i class="ti ti-bolt"></i></div>
            <div class="cm-dd-text">
              <div class="cm-dd-title">پروتکل پایه — <span id="dd-base-current">VLESS</span></div>
              <div class="cm-dd-desc" id="dd-base-current-desc">سبک، سریع و پرکاربردترین گزینه</div>
            </div>
            <i class="ti ti-chevron-down cm-dd-chev"></i>
          </div>
          <div class="cm-dd-panel"><div class="cm-dd-panel-inner"><div class="cm-dd-list">
            <div class="cm-opt sel" data-base="vless" onclick="cmSelectBase('vless',this)">
              <div class="cm-opt-radio"></div>
              <div class="cm-opt-icon"><i class="ti ti-bolt"></i></div>
              <div class="cm-opt-text"><div class="cm-opt-title">VLESS</div><div class="cm-opt-desc">سبک، سریع و پرکاربردترین گزینه</div></div>
              <span class="cm-opt-tag">پیشنهادی</span>
            </div>
            <div class="cm-opt" data-base="trojan" onclick="cmSelectBase('trojan',this)">
              <div class="cm-opt-radio"></div>
              <div class="cm-opt-icon"><i class="ti ti-shield-lock"></i></div>
              <div class="cm-opt-text"><div class="cm-opt-title">Trojan</div><div class="cm-opt-desc">شبیه‌سازی ترافیک HTTPS معمولی</div></div>
            </div>
            <div class="cm-opt" data-base="shadowsocks" onclick="cmSelectBase('shadowsocks',this)">
              <div class="cm-opt-radio"></div>
              <div class="cm-opt-icon"><i class="ti ti-shield-lock-filled"></i></div>
              <div class="cm-opt-text"><div class="cm-opt-title">Shadowsocks</div><div class="cm-opt-desc">رمزنگاری AEAD مستقیم، بدون نیاز به TLS خارجی</div></div>
              <span class="cm-opt-tag" style="background:var(--purple-bg);color:#A78BFA">AEAD</span>
            </div>
            <div class="cm-opt" data-base="telproxy" onclick="cmSelectBase('telproxy',this)">
              <div class="cm-opt-radio"></div>
              <div class="cm-opt-icon"><i class="ti ti-brand-telegram"></i></div>
              <div class="cm-opt-text"><div class="cm-opt-title">Telegram Proxy</div><div class="cm-opt-desc">پروکسی MTProto مستقیم روی یک پورت TCP اختصاصی</div></div>
              <span class="cm-opt-tag" style="background:var(--purple-bg);color:var(--purple-t)">MTProto</span>
            </div>
          </div></div></div>
        </div>
      </div>
      
      <!-- بخش ۲: استریم (ترابرد + فینگرپرینت + ALPN) — فقط برای VLESS/Trojan -->
      <div class="cm-section" id="stream-section">
        <div class="cm-section-label"><i class="ti ti-transfer"></i> استریم</div>
      
        <div class="cm-dd" id="dd-transport">
          <div class="cm-dd-trigger" onclick="cmToggleDD('dd-transport')">
            <div class="cm-dd-icon" id="dd-transport-icon"><i class="ti ti-link"></i></div>
            <div class="cm-dd-text">
              <div class="cm-dd-title">نوع ترابرد — <span id="dd-transport-current">WebSocket</span></div>
              <div class="cm-dd-desc" id="dd-transport-current-desc">پایدار و سازگار با همه شرایط شبکه</div>
            </div>
            <i class="ti ti-chevron-down cm-dd-chev"></i>
          </div>
          <div class="cm-dd-panel"><div class="cm-dd-panel-inner"><div class="cm-dd-list">
            <div class="cm-opt sel" data-t="ws" onclick="cmSelectTransport('ws',this)">
              <div class="cm-opt-radio"></div>
              <div class="cm-opt-icon"><i class="ti ti-link"></i></div>
              <div class="cm-opt-text"><div class="cm-opt-title">WebSocket</div><div class="cm-opt-desc">پایدار و سازگار با همه شرایط شبکه</div></div>
            </div>
            <div class="cm-opt" data-t="xhttp-packet-up" onclick="cmSelectTransport('xhttp-packet-up',this)">
              <div class="cm-opt-radio"></div>
              <div class="cm-opt-icon"><i class="ti ti-package"></i></div>
              <div class="cm-opt-text"><div class="cm-opt-title">XHTTP · packet-up</div><div class="cm-opt-desc">سازگاری بالا با CDN و پروکسی‌ها</div></div>
            </div>
            <div class="cm-opt" data-t="xhttp-stream-up" onclick="cmSelectTransport('xhttp-stream-up',this)">
              <div class="cm-opt-radio"></div>
              <div class="cm-opt-icon"><i class="ti ti-rocket"></i></div>
              <div class="cm-opt-text"><div class="cm-opt-title">XHTTP · stream-up</div><div class="cm-opt-desc">تاخیر پایین‌تر برای اتصال‌های پرسرعت</div></div>
            </div>
          </div></div></div>
        </div>
      
        <div style="height:10px"></div>
      
        <div class="stream-sub-label"><i class="ti ti-transfer-vertical"></i> ALPN</div>
        <div class="alpn-row" id="alpn-pills">
          <div class="alpn-chip active" data-alpn="h2" onclick="cmToggleAlpn('h2',this)">
            <span class="alpn-chip-dot"><i class="ti ti-check"></i></span> h2
          </div>
          <div class="alpn-chip active" data-alpn="http/1.1" onclick="cmToggleAlpn('http/1.1',this)">
            <span class="alpn-chip-dot"><i class="ti ti-check"></i></span> http/1.1
          </div>
          <div class="alpn-chip" data-alpn="h3" onclick="cmToggleAlpn('h3',this)">
            <span class="alpn-chip-dot"><i class="ti ti-check"></i></span> h3
          </div>
        </div>
        
        <div class="stream-sub-label"><i class="ti ti-fingerprint"></i> Fingerprint (TLS Client Hello)</div>
        <div class="fp-grid" id="fp-pills">
          <div class="fp-card active" data-fp="chrome" onclick="cmSetFp('chrome',this)">
            <div class="fp-card-check"><i class="ti ti-check"></i></div>
            <div class="fp-card-icon"><i class="ti ti-brand-chrome"></i></div>
            <div class="fp-card-title">Chrome</div>
          </div>
          <div class="fp-card" data-fp="firefox" onclick="cmSetFp('firefox',this)">
            <div class="fp-card-check"><i class="ti ti-check"></i></div>
            <div class="fp-card-icon"><i class="ti ti-brand-firefox"></i></div>
            <div class="fp-card-title">Firefox</div>
          </div>
          <div class="fp-card" data-fp="ios" onclick="cmSetFp('ios',this)">
            <div class="fp-card-check"><i class="ti ti-check"></i></div>
            <div class="fp-card-icon"><i class="ti ti-brand-apple"></i></div>
            <div class="fp-card-title">iOS / Safari</div>
          </div>
        </div>
        
        <input type="hidden" id="nl-alpn" value="h2,http/1.1">
        <input type="hidden" id="nl-fp" value="chrome">
      
        <input type="hidden" id="nl-proto" value="vless-ws">
        <div class="cm-note" style="margin-top:12px" id="transport-note"></div>
      </div>

      <!-- این سه بخش عمداً خارج از stream-section هستند: وقتی Telegram Proxy یا Shadowsocks
           انتخاب می‌شود stream-section مخفی می‌شود، اگر این بخش‌ها داخلش می‌ماندند با آن مخفی
           می‌شدند حتی وقتی display خودشان block/flex تنظیم می‌شد. -->
      <div class="cm-note" style="margin-top:12px;display:none" id="mtproto-note"></div>

      <div class="cm-section" id="ss-cipher-field" style="display:none;margin-bottom:0">
        <div class="cm-section-label"><i class="ti ti-key"></i> الگوریتم رمزنگاری</div>
        <div class="cm-pills">
          <span class="cm-pill active" data-ss-cipher="chacha20-ietf-poly1305" onclick="cmSetSsCipher('chacha20-ietf-poly1305',this)">ChaCha20-Poly1305</span>
          <span class="cm-pill" data-ss-cipher="aes-256-gcm" onclick="cmSetSsCipher('aes-256-gcm',this)">AES-256-GCM</span>
        </div>
        <input type="hidden" id="nl-ss-cipher" value="chacha20-ietf-poly1305">
        <div class="cm-note" style="margin-top:10px">
          <i class="ti ti-info-circle"></i>
          <span>پسورد به‌صورت خودکار و امن ساخته می‌شود؛ لینک <b>ss://</b> بعد از ساخت کانفیگ در دسترس است.</span>
        </div>
      </div>

      <div class="cm-section" id="mtproto-port-field" style="display:none;margin-bottom:0">
        <div id="auto-domain-box" style="margin-top:10px, display: none">
          <div id="auto-domain-token-wrap" style="display:none;margin-top:9px">
            <div class="cm-row2">
              <input class="cm-input" id="auto-domain-token" type="password" placeholder="Railway API Token">
              <button type="button" class="btn btn-p btn-sm" onclick="submitAutoDomainToken()"><i class="ti ti-check"></i> تایید و دریافت</button>
            </div>
          </div>
        </div>
        <div class="cm-row2">
          <div class="cm-field">
            <label><i class="ti ti-route" style="color:var(--accent);margin-left:4px"></i>پورت TCP</label>
            <input class="cm-input" id="nl-mtproto-port" type="number" min="1" max="65535" placeholder="خالی = خودکار">
          </div>
          <div class="cm-field">
            <label><i class="ti ti-server-2" style="color:var(--accent);margin-left:4px"></i>Fake TLS SNI</label>
            <input class="cm-input" id="nl-mtproto-domain" type="text" placeholder="www.cloudflare.com" oninput="cmClearSniPills()">
          </div>
        </div>
        <div class="cm-pills" style="margin-top:-4px;margin-bottom:10px">
          <span class="cm-pill active" onclick="cmSetSni('www.cloudflare.com',this)"><i class="ti ti-brand-cloudflare" style="margin-left:3px"></i>www.cloudflare.com</span>
          <span class="cm-pill" onclick="cmSetSni('www.google.com',this)">www.google.com</span>
          <span class="cm-pill" onclick="cmSetSni('www.microsoft.com',this)">www.microsoft.com</span>
          <span class="cm-pill" onclick="cmSetSni('www.amazon.com',this)">www.amazon.com</span>
        </div>
        <div class="cm-row2">
          <div class="cm-field">
            <label><i class="ti ti-world-bolt" style="color:var(--accent);margin-left:4px"></i>دامنه‌ی عمومی TCP Proxy</label>
            <input class="cm-input" id="nl-mtproto-public-host" type="text" placeholder="xxxx.proxy.rlwy.net">
          </div>
          <div class="cm-field">
            <label><i class="ti ti-plug-connected" style="color:var(--accent);margin-left:4px"></i>پورت عمومی TCP Proxy</label>
            <input class="cm-input" id="nl-mtproto-public-port" type="number" min="1" max="65535" placeholder="مثلاً 12345">
          </div>
        </div>
        <div style="font-size:11px;opacity:.7;margin:-4px 0 10px;line-height:1.7">
          اگر TCP Proxy را خودت از داشبورد Railway ساخته‌ای، دامنه و پورت عمومی‌اش را اینجا وارد کن
          (همانی که به پورت داخلی بالا map شده). بدون این، لینک از بیرون کار نمی‌کند.
        </div>
        <div class="cm-note" style="margin-top:0">
        </div>
      </div>


      <!-- محدودیت‌ها -->
      <div class="cm-section">
        <div class="cm-section-label"><i class="ti ti-adjustments"></i> محدودیت‌ها</div>
        <div class="cm-field">
          <label>سهمیه ترافیک</label>
          <div class="cm-row2">
            <input class="cm-input" id="nl-val" type="number" min="0" step="0.1" placeholder="0 = نامحدود">
            <select class="cm-input" id="nl-unit"><option value="GB">GB</option><option value="MB" selected>MB</option></select>
          </div>
          <div class="cm-pills">
            <span class="cm-pill" onclick="cmQuota(0,'GB',this)">نامحدود</span>
            <span class="cm-pill" onclick="cmQuota(500,'MB',this)">۵۰۰MB</span>
            <span class="cm-pill active" onclick="cmQuota(1,'GB',this)">۱GB</span>
            <span class="cm-pill" onclick="cmQuota(5,'GB',this)">۵GB</span>
            <span class="cm-pill" onclick="cmQuota(10,'GB',this)">۱۰GB</span>
            <span class="cm-pill" onclick="cmQuota(50,'GB',this)">۵۰GB</span>
          </div>
        </div>
        <div class="cm-field" style="margin-bottom:4px">
          <label>انقضا</label>
          <input class="cm-input" id="nl-exp" type="number" min="0" step="1" placeholder="روز · 0 = نامحدود">
          <div class="cm-pills">
            <span class="cm-pill" onclick="cmExpiry(0,this)">نامحدود</span>
            <span class="cm-pill" onclick="cmExpiry(7,this)">۷ روز</span>
            <span class="cm-pill active" onclick="cmExpiry(30,this)">۳۰ روز</span>
            <span class="cm-pill" onclick="cmExpiry(90,this)">۹۰ روز</span>
          </div>
        </div>
      </div>

    </div>

    <div class="cm-footer">
      <button class="cm-btn-cancel" onclick="closeModal('modal-create-link')">انصراف</button>
      <button class="cm-btn-submit" id="cm-submit-btn" onclick="createLink()"><i class="ti ti-link-plus" id="cm-submit-icon"></i> <span id="cm-submit-text">ساخت کانفیگ</span></button>    </div>
  </div>
</div>

<!-- مودال بروزرسانی -->
<div class="modal-bg" id="modal-update" style="z-index:9999">
  <div class="modal-v2" style="max-width:460px">
    <div class="modal-v2-head" style="background:linear-gradient(155deg,rgba(59,130,246,.16) 0%,transparent 65%)">
      <button class="modal-v2-close" onclick="closeModal('modal-update')"><i class="ti ti-x"></i></button>
      <div class="modal-v2-icon" style="background:linear-gradient(135deg,var(--accent),var(--accent2))"><i class="ti ti-cloud-download"></i></div>
      <div class="modal-v2-title">بروزرسانی جدید موجود است</div>
      <div class="modal-v2-sub">نسخه‌ی جدید <span id="update-modal-version">—</span> آماده نصب است</div>
    </div>
    <div class="modal-v2-body">
      <div class="cl" style="margin-top:0">
        <i class="ti ti-info-circle"></i>
        <span id="update-modal-desc">توضیحات بروزرسانی...</span>
      </div>
      <div class="modal-v2-footer">
        <button class="btn btn-o" onclick="dismissUpdate()" style="flex:.6">انصراف</button>
        <button class="btn btn-p" onclick="startUpdateFromModal()" style="flex:1;justify-content:center"><i class="ti ti-download"></i> نصب بروزرسانی</button>
      </div>
    </div>
  </div>
</div>
<div class="modal-bg" id="modal-links">
  <div class="modal-v2" style="max-width:520px;display:flex;flex-direction:column;max-height:88vh;overflow:hidden">
    <div class="lmodal-head" style="flex-shrink:0">
      <button class="modal-v2-close" onclick="closeModal('modal-links')"><i class="ti ti-x"></i></button>
      <div class="lmodal-icon-row">
        <div class="lmodal-icon"><i class="ti ti-link-plus"></i></div>
        <div>
          <div class="lmodal-title-v2">مدیریت کانفیگ‌های <span id="modal-sub-name" style="color:var(--accent2)">—</span></div>
          <div class="lmodal-sub-v2">کانفیگ‌هایی که می‌خواهید در این گروه باشند را انتخاب کنید</div>
        </div>
      </div>
      <div class="lmodal-search">
        <i class="ti ti-search"></i>
        <input type="text" id="lmodal-search-inp" placeholder="جستجوی کانفیگ..." oninput="filterLmodal(this.value)">
      </div>
      <div class="lmodal-quickbar">
        <button class="lmodal-qbtn" onclick="lmodalSelectAll(true)"><i class="ti ti-checks"></i> انتخاب همه</button>
        <button class="lmodal-qbtn" onclick="lmodalSelectAll(false)"><i class="ti ti-x"></i> لغو همه</button>
        <span class="lmodal-count" id="lmodal-count">۰ انتخاب شده</span>
      </div>
    </div>
    <div class="lmodal-list" id="modal-links-body" style="flex:1;overflow-y:auto;min-height:0;max-height:none">در حال بارگذاری...</div>
    <div class="lmodal-footer" style="flex-shrink:0">
      <div class="lmodal-footer-info"><i class="ti ti-info-circle"></i> تغییرات بلافاصله اعمال می‌شود</div>
      <div class="lmodal-footer-btns">
        <button class="btn btn-o" onclick="closeModal('modal-links')">بستن</button>
        <button class="btn btn-p" id="modal-save-btn" onclick="saveSubLinks()"><i class="ti ti-check"></i> ذخیره</button>
      </div>
    </div>
  </div>
</div>
<div class="modal-bg" id="modal-ad-tag">
  <div class="modal-v2 cm-modal" style="max-width:460px">
    <button class="cm-close" onclick="closeModal('modal-ad-tag')"><i class="ti ti-x"></i></button>

    <div class="cm-head">
      <div class="cm-head-row">
        <div class="cm-head-icon" style="background:linear-gradient(135deg,var(--purple),#6D48D6)"><i class="ti ti-speakerphone"></i></div>
        <div>
          <div class="cm-head-title">تبلیغ کانال روی پروکسی</div>
          <div class="cm-head-sub" id="at-label-sub">تنظیم ad-tag برای <span id="at-cfg-name" style="color:var(--accent2)">—</span></div>
        </div>
      </div>
    </div>

    <div class="cm-body">
      <div class="cm-section">
        <div class="cm-section-label"><i class="ti ti-tag"></i> کد تبلیغ (ad_tag)</div>
        <div class="cm-field" style="margin-bottom:8px">
          <input class="cm-input" id="at-tag" placeholder="مثلاً: 3AB4C5D6E7F8...">
        </div>
        <div class="cm-note">
          <i class="ti ti-info-circle"></i>
          <span>این کد را از ربات <b>@MTProxybot</b> در تلگرام دریافت کنید (با ارسال دستور <b>/newproxy</b> و ثبت لینک پروکسی). با تنظیم این کد، هر بار کاربر از این پروکسی استفاده کند، تبلیغ کانال شما در تلگرامش نمایش داده می‌شود.</span>
        </div>
        <div class="cm-note" style="background:var(--amber-bg);color:var(--amber-t);margin-top:8px">
          <i class="ti ti-alert-triangle"></i>
          <span>با ثبت یا تغییر کد، پروکسی برای چند ثانیه ری‌استارت می‌شود و اتصال کاربران فعلی به‌طور موقت قطع خواهد شد.</span>
        </div>
      </div>
    </div>

    <div class="cm-footer">
      <button class="cm-btn-cancel" onclick="closeModal('modal-ad-tag')">انصراف</button>
      <button class="cm-btn-submit" id="at-submit-btn" onclick="submitAdTag()">
        <i class="ti ti-check"></i> ذخیره و اعمال
      </button>
    </div>
  </div>
</div>
<div class="modal-bg" id="modal-mt-info">
  <div class="modal-v2 cm-modal" style="max-width:480px">
    <button class="cm-close" onclick="closeModal('modal-mt-info')"><i class="ti ti-x"></i></button>

    <div class="cm-head">
      <div class="cm-head-row">
        <div class="cm-head-icon" style="background:linear-gradient(135deg,var(--accent),var(--accent2))"><i class="ti ti-info-circle"></i></div>
        <div>
          <div class="cm-head-title">اطلاعات پروکسی تلگرام</div>
          <div class="cm-head-sub">مشخصات <span id="mti-cfg-name" style="color:var(--accent2)">—</span></div>
        </div>
      </div>
    </div>

    <div class="cm-body">
      <div class="cm-section">
        <div class="cm-section-label"><i class="ti ti-key"></i> سکرت (مناسب برای ثبت در ربات‌ها)</div>
        <div class="cm-field" style="margin-bottom:8px">
          <div class="cm-input" id="mti-secret" style="font-family:ui-monospace,monospace;font-size:11.5px;word-break:break-all;user-select:all;cursor:text">—</div>
        </div>
        <button class="btn btn-g" style="width:100%;justify-content:center" onclick="cpMtiField('mti-secret','سکرت کپی شد ✓')"><i class="ti ti-copy"></i> کپی سکرت</button>
        <div class="cm-note" style="margin-top:10px">
          <i class="ti ti-info-circle"></i>
          <span>این نسخه‌ی خالص سکرت است (بدون پیشوند fake-TLS و دامنه) — همان مقداری که ربات‌هایی مثل <b>@MTProxybot</b> برای ثبت پروکسی و دریافت لینک تبلیغ (ad_tag) نیاز دارند.</span>
        </div>
      </div>

      <div class="cm-section" style="margin-bottom:6px">
        <div class="cm-section-label"><i class="ti ti-link"></i> لینک کامل پروکسی</div>
        <div class="cm-field" style="margin-bottom:8px">
          <div class="cm-input" id="mti-link" style="font-family:ui-monospace,monospace;font-size:11px;word-break:break-all;user-select:all;cursor:text">—</div>
        </div>
        <button class="btn btn-p" style="width:100%;justify-content:center" onclick="cpMtiField('mti-link','لینک کپی شد ✓')"><i class="ti ti-copy"></i> کپی لینک کامل</button>
      </div>
    </div>

    <div class="cm-footer">
      <button class="cm-btn-cancel" style="flex:1;justify-content:center" onclick="closeModal('modal-mt-info')">بستن</button>
    </div>
  </div>
</div>
<div class="modal-bg" id="modal-domain-gen">
  <div class="modal-v2 cm-modal" style="max-width:460px">
    <button class="cm-close" onclick="closeModal('modal-domain-gen')"><i class="ti ti-x"></i></button>
    <div class="cm-head">
      <div class="cm-head-row">
        <div class="cm-head-icon"><i class="ti ti-repeat"></i></div>
        <div>
          <div class="cm-head-title">تولید انبوه دامنه</div>
          <div class="cm-head-sub">ساخت چند TCP Proxy روی Railway برای گرفتن چند دامنه‌ی متفاوت</div>
        </div>
      </div>
    </div>
    <div class="cm-body">
      <div class="cm-section" id="dg-token-section">
        <div class="cm-section-label"><i class="ti ti-key"></i> احراز هویت</div>
        <div class="cm-field">
          <label>Railway API Token</label>
          <input class="cm-input" id="dg-token" type="password" placeholder="توکن اکانت یا پروژه‌ی Railway">
        </div>
        <div class="cm-row2">
          <div class="cm-field" style="margin-bottom:0">
            <label>پورت داخلی اپلیکیشن (اختیاری)</label>
            <input class="cm-input" id="dg-port" type="number" placeholder="پیش‌فرض: پورت خودِ پنل">
          </div>
          <div class="cm-field" style="margin-bottom:0">
            <label>تعداد دامنه‌ی مورد نیاز</label>
            <input class="cm-input" id="dg-count" type="number" min="1" value="10">
          </div>
        </div>
      </div>
      <div class="cm-section" id="dg-token-saved-section" style="display:none">
        <div class="cm-note" style="margin-top:0">
          <i class="ti ti-shield-check"></i>
          <span>توکن Railway از قبل ذخیره شده و نیازی به وارد کردن دوباره نیست.
          <a href="javascript:void(0)" onclick="dgChangeToken()" style="color:var(--accent2);font-weight:700">تغییر توکن</a></span>
        </div>
      </div>
      <div class="cm-section" style="margin-bottom:6px">
        <div class="cm-section-label"><i class="ti ti-activity"></i> وضعیت اجرا</div>
        <div class="cm-note" id="dg-status-note">
          <i class="ti ti-info-circle" id="dg-status-icon"></i>
          <span id="dg-status-text">هنوز شروع نشده</span>
        </div>
        <div class="upd-log-box" id="dg-log-box" style="margin-top:10px;max-height:170px;display:none">
          <p class="upd-log-empty">لاگی موجود نیست</p>
        </div>
        <div id="dg-results" style="display:flex;flex-direction:column;gap:6px;margin-top:10px"></div>
      </div>
    </div>
    <div class="cm-footer">
      <button class="cm-btn-cancel" onclick="closeModal('modal-domain-gen')">بستن</button>
      <button class="cm-btn-cancel" id="dg-stop-btn" style="display:none;color:var(--red-t);border-color:rgba(239,68,68,.25)" onclick="stopDomainGen()">
        <i class="ti ti-player-stop"></i> توقف
      </button>
      <button class="cm-btn-submit" id="dg-start-btn" onclick="startDomainGen()">
        <i class="ti ti-player-play"></i> شروع ساخت
      </button>
    </div>
  </div>
</div>
<div class="modal-bg" id="modal-bot-tcp-proxy">
  <div class="modal-v2 cm-modal" style="max-width:560px">
    <button class="cm-close" onclick="btpCloseModal()"><i class="ti ti-x"></i></button>

    <div class="cm-head">
      <div class="cm-head-row">
        <div class="cm-head-icon"><i class="ti ti-server-2"></i></div>
        <div>
          <div class="cm-head-title">ساخت TCP Proxy اختصاصی</div>
          <div class="cm-head-sub">اتصال خودکار به Railway و ساخت پروکسی تلگرام</div>
        </div>
      </div>
    </div>

    <div class="cm-body">
      <!-- مرحله ۱: توکن و پورت -->
      <div id="btp-step-input">
        <div class="cm-section">
          <div class="cm-section-label"><i class="ti ti-key"></i> اطلاعات لازم</div>
          <div class="cm-field">
            <label>Railway API Token</label>
            <input class="cm-input" id="btp-token" type="password" placeholder="توکن اکانت یا پروژه‌ی Railway">
          </div>
          <div class="cm-field" id="btp-token-saved-note" style="display:none;margin-bottom:14px">
            <div class="cm-note" style="margin:0">
              <i class="ti ti-shield-check"></i>
              <span>توکن قبلی روی سرور ذخیره است؛ لازم نیست دوباره وارد کنی.
              <a href="javascript:void(0)" onclick="btpChangeToken()" style="color:var(--accent2);font-weight:700">تغییر توکن</a></span>
            </div>
          </div>
          <div class="cm-field" style="margin-bottom:0">
            <label>پورت</label>
            <input class="cm-input" id="btp-port" type="number" placeholder="مثلاً پورت داخلی پروکسی تلگرام">
          </div>
        </div>
      </div>

      <!-- مرحله ۲: هشدار خاموش کردن VPN -->
      <div id="btp-step-vpn" style="display:none;text-align:center;padding:10px 0">
        <i class="ti ti-shield-off" style="font-size:40px;color:var(--amber-t)"></i>
        <div style="font-weight:700;font-size:15px;margin-top:12px">اگر VPN روی این دستگاه روشن است، خاموشش کن</div>
        <div style="color:var(--t3);font-size:12.5px;margin-top:6px">برای این‌که تست اتصال درست انجام شود، باید بدون VPN باشی.</div>
      </div>

      <!-- مرحله ۳: پینگ‌گیری واقعی از دامنه‌ها -->
      <div id="btp-step-ping" style="display:none">
        <div class="cm-note" id="btp-ping-status-note">
          <i class="ti ti-loader-2" id="btp-ping-status-icon" style="animation:spin 1s linear infinite"></i>
          <span id="btp-ping-status-text">در حال تست دامنه‌ها...</span>
        </div>
        <div id="btp-ping-list" style="display:flex;flex-direction:column;gap:5px;margin-top:12px;max-height:260px;overflow-y:auto"></div>
      </div>

      <!-- مرحله ۴: در حال ساخت پروکسی -->
      <div id="btp-step-search" style="display:none">
        <div class="cm-note" id="btp-status-note">
          <i class="ti ti-info-circle" id="btp-status-icon"></i>
          <span id="btp-status-text">در حال جست‌وجو...</span>
        </div>
        <div id="btp-found-list" style="display:flex;flex-direction:column;gap:6px;margin-top:12px;max-height:260px;overflow-y:auto"></div>
      </div>

      <!-- مرحله ۵: نتیجه‌ی نهایی -->
      <div id="btp-step-done" style="display:none;text-align:center;padding:6px 0">
        <i class="ti ti-circle-check" style="font-size:40px;color:var(--green-t)"></i>
        <div style="font-weight:700;font-size:15px;margin-top:12px">پروکسی تلگرام ساخته شد</div>
        <div id="btp-done-domain" style="font-family:ui-monospace,monospace;font-size:12.5px;color:var(--t2);margin-top:8px"></div>
        <div id="btp-done-link-wrap" style="display:none;margin-top:14px">
          <div class="cm-field" style="margin-bottom:0">
            <input class="cm-input" id="btp-done-link" readonly style="text-align:left;direction:ltr;font-family:ui-monospace,monospace;font-size:11.5px">
          </div>
          <button class="btn btn-g" style="margin-top:8px" onclick="btpCopyLink()"><i class="ti ti-copy"></i> کپی لینک پروکسی</button>
        </div>
      </div>
    </div>

    <div class="cm-footer">
      <button class="cm-btn-cancel" id="btp-cancel-btn" onclick="btpCloseModal()">انصراف</button>
      <button class="cm-btn-cancel" id="btp-stop-btn" style="display:none;color:var(--red-t);border-color:rgba(239,68,68,.25)" onclick="stopBotTcpProxy()">
        <i class="ti ti-player-stop"></i> توقف
      </button>
      <button class="cm-btn-submit" id="btp-continue-btn" style="display:none">ادامه</button>
      <button class="cm-btn-submit" id="btp-start-btn" onclick="startBotTcpProxy()">
        <i class="ti ti-player-play"></i> شروع
      </button>
      <button class="cm-btn-submit" id="btp-close-done-btn" style="display:none" onclick="btpCloseModal()">بستن</button>
    </div>
  </div>
</div>
<div class="modal-bg" id="modal-zeus-proxy">
  <div class="modal-v2 cm-modal" style="max-width:500px">
    <button class="cm-close" onclick="zpCloseModal()"><i class="ti ti-x"></i></button>

    <div class="cm-head">
      <div class="cm-head-row">
        <div class="cm-head-icon"><i class="ti ti-bolt"></i></div>
        <div>
          <div class="cm-head-title">پروکسی Zeus</div>
          <div class="cm-head-sub">SOCKS5 اختصاصی با محدودیت حجم، انقضا و کنترل اتصال</div>
        </div>
      </div>
    </div>

    <!-- این مودال فقط برای ساخت است؛ بعد از ساخت، پروکسی مثل بقیه‌ی کانفیگ‌ها توی لیست نمایش داده می‌شود -->
    <div class="cm-body">
      <!-- مرحله ۱: توکن + کانفیگ -->
      <div id="zp-step-input">
        <div class="cm-section">
          <div class="cm-section-label"><i class="ti ti-key"></i> توکن Railway</div>
          <div class="cm-field">
            <label>Railway API Token</label>
            <input class="cm-input" id="zp-token" type="password" placeholder="توکن اکانت یا پروژه‌ی Railway">
          </div>
          <div class="cm-field" id="zp-token-saved-note" style="display:none;margin-bottom:0">
            <div class="cm-note" style="margin:0">
              <i class="ti ti-shield-check"></i>
              <span>توکن قبلی روی سرور ذخیره است (مشترک با Bot TCP Proxy)؛ لازم نیست دوباره وارد کنی.
              <a href="javascript:void(0)" onclick="zpChangeToken()" style="color:var(--accent2);font-weight:700">تغییر توکن</a></span>
            </div>
          </div>
        </div>

        <!-- ── کانفیگ‌های پروکسی ── -->
        <div class="cm-section" style="margin-top:10px">
          <div class="cm-section-label"><i class="ti ti-settings"></i> کانفیگ پروکسی</div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
            <div class="cm-field" style="margin:0">
              <label>محدودیت حجم (GB)</label>
              <input class="cm-input" id="zp-cfg-traffic" type="number" min="0" step="0.5" placeholder="مثلاً 10 — صفر = نامحدود">
            </div>
            <div class="cm-field" style="margin:0">
              <label>انقضا (روز)</label>
              <input class="cm-input" id="zp-cfg-days" type="number" min="0" step="1" placeholder="مثلاً 30 — صفر = بی‌انقضا">
            </div>
          </div>
          <div class="cm-field" style="margin-top:8px;margin-bottom:0">
            <label>حداکثر اتصال همزمان per IP</label>
            <input class="cm-input" id="zp-cfg-maxip" type="number" min="0" step="1" placeholder="مثلاً 3 — صفر = نامحدود">
          </div>
        </div>
      </div>

      <!-- مرحله ۲: در حال ساخت -->
      <div id="zp-step-building" style="display:none;text-align:center;padding:14px 0">
        <i class="ti ti-loader-2" style="font-size:34px;color:var(--accent);animation:spin 1s linear infinite"></i>
        <div style="font-weight:700;font-size:14.5px;margin-top:12px">در حال ساخت پروکسی...</div>
        <div style="color:var(--t3);font-size:12px;margin-top:4px">سرور SOCKS5 داخلی بالا می‌آید و TCP Proxy روی Railway ساخته می‌شود</div>
      </div>

      <!-- خطا -->
      <div id="zp-step-error" style="display:none">
        <div class="cm-note" style="background:var(--red-bg);border-color:rgba(239,68,68,.3)">
          <i class="ti ti-alert-triangle" style="color:var(--red-t)"></i>
          <span id="zp-error-text"></span>
        </div>
      </div>
    </div>

    <div class="cm-footer">
      <button class="cm-btn-cancel" id="zp-cancel-btn" onclick="zpCloseModal()">انصراف</button>
      <button class="cm-btn-submit" id="zp-start-btn" onclick="zpStart()">
        <i class="ti ti-player-play"></i> ساخت پروکسی
      </button>
    </div>
  </div>
</div>

<!-- مدیریت/ویرایش پروکسی Zeus — از روی کارت آن در لیست کانفیگ‌ها باز می‌شود -->
<div class="modal-bg" id="modal-zeus-manage">
  <div class="modal-v2 cm-modal" style="max-width:500px">
    <button class="cm-close" onclick="zpCloseManage()"><i class="ti ti-x"></i></button>

    <div class="cm-head">
      <div class="cm-head-row">
        <div class="cm-head-icon"><i class="ti ti-bolt"></i></div>
        <div>
          <div class="cm-head-title">مدیریت پروکسی Zeus</div>
          <div class="cm-head-sub">آمار مصرف و ویرایش کانفیگ</div>
        </div>
      </div>
    </div>

    <div class="cm-body">
      <div style="padding:6px 0">
        <div style="text-align:center">
          <i class="ti ti-circle-check" style="font-size:38px;color:var(--green-t)"></i>
          <div style="font-weight:700;font-size:15px;margin-top:10px">پروکسی Zeus فعال است</div>
          <div style="color:var(--t3);font-size:12px;margin-top:4px">این رشته را در فیلد user_socks5 پنل Zeus قرار بده</div>
          <div class="cm-field" style="margin-top:12px;margin-bottom:0">
            <input class="cm-input" id="zp-done-config" readonly style="text-align:left;direction:ltr;font-family:ui-monospace,monospace;font-size:11px">
          </div>
          <button class="btn btn-g" style="margin-top:7px" onclick="zpCopyConfig()"><i class="ti ti-copy"></i> کپی کانفیگ</button>
        </div>

        <!-- آمار لایو -->
        <div style="margin-top:14px;background:var(--card2,var(--card));border-radius:10px;padding:12px 14px">
          <div style="font-weight:700;font-size:12.5px;margin-bottom:8px;color:var(--t2)"><i class="ti ti-chart-bar"></i> آمار مصرف</div>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;text-align:center">
            <div>
              <div style="font-size:11px;color:var(--t3)">مصرف حجم</div>
              <div style="font-weight:700;font-size:13px" id="zp-stat-traffic">—</div>
            </div>
            <div>
              <div style="font-size:11px;color:var(--t3)">زمان مانده</div>
              <div style="font-weight:700;font-size:13px" id="zp-stat-expiry">—</div>
            </div>
            <div>
              <div style="font-size:11px;color:var(--t3)">اتصال فعال</div>
              <div style="font-weight:700;font-size:13px" id="zp-stat-conns">—</div>
            </div>
          </div>
          <!-- نوار حجم -->
          <div id="zp-traffic-bar-wrap" style="margin-top:9px;display:none">
            <div style="height:6px;background:var(--border2,#333);border-radius:3px;overflow:hidden">
              <div id="zp-traffic-bar" style="height:100%;background:var(--accent);border-radius:3px;transition:width .4s"></div>
            </div>
            <div style="font-size:10px;color:var(--t3);margin-top:3px;text-align:left" id="zp-traffic-bar-label"></div>
          </div>
        </div>

        <!-- ویرایش کانفیگ زنده -->
        <div style="margin-top:10px;background:var(--card2,var(--card));border-radius:10px;padding:12px 14px">
          <div style="font-weight:700;font-size:12.5px;margin-bottom:8px;color:var(--t2)"><i class="ti ti-adjustments"></i> تنظیم کانفیگ (اعمال فوری)</div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
            <div class="cm-field" style="margin:0">
              <label style="font-size:11px">حجم (GB) — صفر=نامحدود</label>
              <input class="cm-input" id="zp-edit-traffic" type="number" min="0" step="0.5">
            </div>
            <div class="cm-field" style="margin:0">
              <label style="font-size:11px">انقضا (روز) — صفر=بی‌انقضا</label>
              <input class="cm-input" id="zp-edit-days" type="number" min="0" step="1">
            </div>
          </div>
          <div class="cm-field" style="margin-top:8px;margin-bottom:8px">
            <label style="font-size:11px">حداکثر اتصال per IP — صفر=نامحدود</label>
            <input class="cm-input" id="zp-edit-maxip" type="number" min="0" step="1">
          </div>
          <button class="btn btn-g" style="width:100%;justify-content:center" onclick="zpSaveConfig()">
            <i class="ti ti-device-floppy"></i> ذخیره کانفیگ
          </button>
        </div>
      </div>
    </div>

    <div class="cm-footer">
      <button class="cm-btn-cancel" onclick="zpCloseManage()">بستن</button>
      <button class="btn" id="zp-delete-btn" style="background:var(--red-bg);color:var(--red-t);border:1px solid rgba(239,68,68,.3);border-radius:8px;padding:0 14px;font-size:13px;font-weight:600;cursor:pointer" onclick="zpDelete()">
        <i class="ti ti-trash"></i> حذف پروکسی
      </button>
    </div>
  </div>
</div>

<!-- آی‌پی‌های متصل به پروکسی Zeus — هر آی‌پی صرف‌نظر از تعداد اتصال‌هایش فقط یک بار شمرده می‌شود -->
<div class="modal-bg" id="modal-zeus-ips">
  <div class="modal-v2 cm-modal" style="max-width:420px">
    <button class="cm-close" onclick="zpCloseIps()"><i class="ti ti-x"></i></button>
    <div class="cm-head">
      <div class="cm-head-row">
        <div class="cm-head-icon"><i class="ti ti-network"></i></div>
        <div>
          <div class="cm-head-title">آی‌پی‌های متصل</div>
          <div class="cm-head-sub" id="zp-ips-sub">هر آی‌پی یک بار شمرده می‌شود</div>
        </div>
      </div>
    </div>
    <div class="cm-body">
      <div id="zp-ips-list" style="display:flex;flex-direction:column;gap:6px"></div>
      <div class="empty" id="zp-ips-empty" style="display:none;padding:20px 0;text-align:center">
        <i class="ti ti-plug-off" style="font-size:26px;color:var(--t3)"></i>
        <p style="margin-top:8px;font-size:12.5px;color:var(--t3)">در حال حاضر هیچ آی‌پی متصل نیست</p>
      </div>
    </div>
    <div class="cm-footer">
      <button class="cm-btn-submit" style="width:100%;justify-content:center" onclick="zpCloseIps()">بستن</button>
    </div>
  </div>
</div>
<div class="modal-bg" id="modal-domain-scan">
  <div class="modal-v2 cm-modal" style="max-width:480px">
    <button class="cm-close" onclick="closeModal('modal-domain-scan')"><i class="ti ti-x"></i></button>
    <div class="cm-head">
      <div class="cm-head-row">
        <div class="cm-head-icon"><i class="ti ti-search"></i></div>
        <div>
          <div class="cm-head-title">جستجوی دامنه‌ی دلخواه</div>
          <div class="cm-head-sub">دامنه‌های موردنظرت رو وارد کن، هر بار Enter بزن</div>
        </div>
      </div>
    </div>
    <div class="cm-body">
      <div class="cm-section" id="ds-token-section">
        <div class="cm-field">
          <label>Railway API Token</label>
          <input class="cm-input" id="ds-token" type="password" placeholder="در صورتی که قبلاً ذخیره نشده">
        </div>
      </div>
      <div class="cm-section">
        <div class="cm-field">
          <label>افزودن دامنه</label>
          <input class="cm-input" id="ds-domain-inp" placeholder="مثلاً nozomi.proxy.rlwy.net و Enter بزن"
                 onkeydown="if(event.key==='Enter'){event.preventDefault();dsAddDomain()}">
        </div>
        <div class="cm-pills" id="ds-domain-chips"></div>
      </div>
      <div class="cm-section" style="margin-bottom:6px">
        <div class="cm-note" id="ds-status-note">
          <i class="ti ti-info-circle"></i> <span id="ds-status-text">هنوز شروع نشده</span>
        </div>
        <div class="upd-log-box" id="ds-log-box" style="margin-top:10px;max-height:170px;display:none">
          <p class="upd-log-empty">لاگی موجود نیست</p>
        </div>
      </div>
    </div>
    <div class="cm-footer">
      <button class="cm-btn-cancel" onclick="closeModal('modal-domain-scan')">بستن</button>
      <button class="cm-btn-cancel" id="ds-stop-btn" style="display:none;color:var(--red-t)" onclick="stopDomainScan()"><i class="ti ti-player-stop"></i> توقف</button>
      <button class="cm-btn-submit" id="ds-start-btn" onclick="startDomainScan()"><i class="ti ti-player-play"></i> شروع اسکن</button>
    </div>
  </div>
</div>
<div class="modal-bg" id="modal-suggest-domain">
  <div class="modal-v2 cm-modal" style="max-width:420px">
    <button class="cm-close" onclick="closeModal('modal-suggest-domain')"><i class="ti ti-x"></i></button>
    <div class="cm-head">
      <div class="cm-head-row">
        <div class="cm-head-icon" style="background:linear-gradient(135deg,var(--purple),#6D48D6)"><i class="ti ti-send"></i></div>
        <div>
          <div class="cm-head-title">پیشنهاد دامنه به اپراتور</div>
          <div class="cm-head-sub">دامنه‌ای که سراغ داری رو برای بررسی بفرست</div>
        </div>
      </div>
    </div>
    <div class="cm-body">
      <div class="cm-field">
        <label>دامنه‌ی پیشنهادی</label>
        <input class="cm-input" id="sg-domain" placeholder="مثلاً: nozomi.proxy.rlwy.net">
      </div>
      <div class="cm-field" style="margin-bottom:6px">
        <label>یادداشت (اختیاری)</label>
        <input class="cm-input" id="sg-note" placeholder="مثلاً: با فیلترشکن X کار می‌کنه">
      </div>
      <div class="cm-note" id="sg-status-note">
        <i class="ti ti-info-circle"></i> <span id="sg-status-text">هنوز ارسال نشده</span>
      </div>
    </div>
    <div class="cm-footer">
      <button class="cm-btn-cancel" onclick="closeModal('modal-suggest-domain')">انصراف</button>
      <button class="cm-btn-submit" id="sg-submit-btn" onclick="submitDomainSuggestion()">
        <i class="ti ti-send"></i> ارسال پیشنهاد
      </button>
    </div>
  </div>
</div>
<div class="modal-bg" id="modal-create-sub">
  <div class="modal-v2">
    <div class="modal-v2-head">
      <button class="modal-v2-close" onclick="closeModal('modal-create-sub')"><i class="ti ti-x"></i></button>
      <div class="modal-v2-icon"><i class="ti ti-folder-plus"></i></div>
      <div class="modal-v2-title">ساخت گروه جدید</div>
      <div class="modal-v2-sub">یک صفحه پابلیک مجزا برای مدیریت کانفیگ‌ها بسازید</div>
    </div>
    <div class="modal-v2-body">
      <div class="modal-v2-field">
        <label><i class="ti ti-tag"></i> نام گروه</label>
        <input class="modal-v2-input" id="ns-name" placeholder="مثلاً: کانال تلگرام">
      </div>
      <div class="modal-v2-field" id="ns-target-wrap" style="display:none">
        <label><i class="ti ti-topology-star-3"></i> پنل مقصد</label>
        <select class="modal-v2-input" id="ns-target"><option value="">این پنل</option></select>
      </div>
      <div class="modal-v2-field">
        <label><i class="ti ti-align-left"></i> توضیحات (اختیاری)</label>
        <input class="modal-v2-input" id="ns-desc" placeholder="توضیح کوتاه درباره این گروه">
      </div>
      <div class="modal-v2-field" style="margin-bottom:0">
        <label><i class="ti ti-lock"></i> رمز صفحه پابلیک (اختیاری)</label>
        <input class="modal-v2-input" id="ns-pw" type="password" placeholder="خالی بگذارید = بدون رمز">
      </div>
      <div class="cl" style="margin-top:14px"><i class="ti ti-info-circle"></i><span>صفحه پابلیک این گروه با یک لینک منحصر‌به‌فرد در اینترنت در دسترس خواهد بود.</span></div>
      <div class="modal-v2-footer">
        <button class="btn btn-o" onclick="closeModal('modal-create-sub')" style="flex:.6">انصراف</button>
        <button class="btn btn-pur" onclick="createSub()"><i class="ti ti-folder-plus"></i> ساخت گروه</button>
      </div>
    </div>
  </div>
</div>
<div class="modal-bg" id="modal-node-key">
  <div class="modal-v2 cm-modal" style="max-width:560px">
    <div class="modal-v2-head">
      <button class="modal-v2-close" onclick="closeModal('modal-node-key')"><i class="ti ti-x"></i></button>
      <div class="modal-v2-icon"><i class="ti ti-key"></i></div>
      <div class="modal-v2-title">ساخت کلید اتصال</div>
      <div class="modal-v2-sub">این کلید را در پنل دیگر، بخش «متصل کردن» وارد کنید</div>
    </div>
    <div class="modal-v2-body">
      <div class="modal-v2-field">
        <label><i class="ti ti-tag"></i> برچسب کلید (اختیاری)</label>
        <input class="modal-v2-input" id="nk-label" placeholder="مثلاً: پنل تهران">
      </div>
      <div class="modal-v2-field">
        <label><i class="ti ti-shield-check"></i> دسترسی‌های این کلید</label>
        <div class="nk-perm-grid" id="nk-perms">
          <div class="nk-perm-tile on" data-perm="usage" onclick="toggleNkPerm(this)">
            <div class="nk-perm-tile-ic"><i class="ti ti-transfer"></i></div>
            <div class="nk-perm-tile-txt"><div class="nk-perm-tile-name">مصرف</div><div class="nk-perm-tile-desc">حجم و اتصال‌های فعال</div></div>
          </div>
          <div class="nk-perm-tile on" data-perm="links" onclick="toggleNkPerm(this)">
            <div class="nk-perm-tile-ic"><i class="ti ti-link"></i></div>
            <div class="nk-perm-tile-txt"><div class="nk-perm-tile-name">کانفیگ‌ها</div><div class="nk-perm-tile-desc">فهرست لینک‌های ساخته‌شده</div></div>
          </div>
          <div class="nk-perm-tile on" data-perm="subs" onclick="toggleNkPerm(this)">
            <div class="nk-perm-tile-ic"><i class="ti ti-folders"></i></div>
            <div class="nk-perm-tile-txt"><div class="nk-perm-tile-name">گروه‌های ساب</div><div class="nk-perm-tile-desc">فهرست گروه‌بندی‌ها</div></div>
          </div>
          <div class="nk-perm-tile on" data-perm="requests" onclick="toggleNkPerm(this)">
            <div class="nk-perm-tile-ic"><i class="ti ti-arrows-exchange"></i></div>
            <div class="nk-perm-tile-txt"><div class="nk-perm-tile-name">درخواست‌ها</div><div class="nk-perm-tile-desc">تعداد ریکوئست و خطا</div></div>
          </div>
          <div class="nk-perm-tile" data-perm="logs" onclick="toggleNkPerm(this)">
            <div class="nk-perm-tile-ic"><i class="ti ti-history"></i></div>
            <div class="nk-perm-tile-txt"><div class="nk-perm-tile-name">لاگ‌ها</div><div class="nk-perm-tile-desc">تاریخچه‌ی فعالیت پنل</div></div>
          </div>
          <div class="nk-perm-tile manage" data-perm="manage" onclick="toggleNkPerm(this)">
            <div class="nk-perm-tile-ic"><i class="ti ti-writing"></i></div>
            <div class="nk-perm-tile-txt"><div class="nk-perm-tile-name">ویرایش/حذف از راه دور</div><div class="nk-perm-tile-desc">تغییر کانفیگ‌های این پنل</div></div>
          </div>
        </div>
      </div>
      <div class="modal-v2-field">
        <label><i class="ti ti-lock"></i> رمز روی توکن (اختیاری)</label>
        <input class="modal-v2-input" id="nk-password" type="password" placeholder="خالی بگذارید = بدون رمز">
      </div>
      <div id="nk-result" style="display:none">
        <div class="vl-code" id="nk-key" style="margin-top:6px">—</div>
        <div style="display:flex;gap:8px;margin-top:10px">
          <button class="btn btn-p" onclick="cpText('nk-key')"><i class="ti ti-copy"></i> کپی کلید</button>
        </div>
      </div>
      <div class="cl amber"><i class="ti ti-shield-lock"></i><span>این کلید فقط به بخش‌های تیک‌خورده دسترسی می‌دهد؛ بدون «ویرایش/حذف از راه دور»، دارنده‌ی کلید فقط می‌تواند بخواند. هر زمان می‌توانید از لیست پایین غیرفعال یا حذفش کنید.</span></div>
      <div class="modal-v2-footer">
        <button class="btn btn-o" onclick="closeModal('modal-node-key')" style="flex:.6">بستن</button>
        <button class="btn btn-p" id="nk-gen-btn" onclick="genNodeKey()"><i class="ti ti-key"></i> ساخت کلید</button>
      </div>
    </div>
  </div>
</div>
<div class="modal-bg" id="modal-node-connect">
  <div class="modal-v2 cm-modal" style="max-width:560px">
    <div class="modal-v2-head" style="background:linear-gradient(155deg,rgba(34,197,94,.16) 0%,transparent 65%)">
      <button class="modal-v2-close" onclick="closeModal('modal-node-connect')"><i class="ti ti-x"></i></button>
      <div class="modal-v2-icon" style="background:linear-gradient(135deg,var(--green),#15803D)"><i class="ti ti-plug-connected"></i></div>
      <div class="modal-v2-title">متصل شدن به یک نود</div>
      <div class="modal-v2-sub">کلیدی که پنل مقابل ساخته را اینجا پیست کنید</div>
    </div>
    <div class="modal-v2-body">
      <div class="modal-v2-field">
        <label><i class="ti ti-key"></i> کلید اتصال</label>
        <textarea class="modal-v2-input" id="nc-key" rows="3" style="resize:vertical;direction:ltr;font-family:ui-monospace,Menlo,monospace;font-size:11px" placeholder="rvg-..." oninput="previewNodeKey()"></textarea>
        <div class="nc-host-chip"><i class="ti ti-server-2"></i><span id="nc-host-preview">دامنه‌ی پنل مقابل اینجا نمایش داده می‌شود</span></div>
      </div>
      <div class="modal-v2-field">
        <label><i class="ti ti-tag"></i> نام نمایشی نود (اختیاری)</label>
        <input class="modal-v2-input" id="nc-label" placeholder="مثلاً: نود آلمان">
      </div>
      <div class="modal-v2-field" style="margin-bottom:0">
        <label><i class="ti ti-lock"></i> رمز نود (فقط اگر روی این توکن رمز گذاشته شده)</label>
        <input class="modal-v2-input" id="nc-password" type="password" placeholder="اگر رمز نمی‌دانید خالی بگذارید">
      </div>
      <div class="cl"><i class="ti ti-info-circle"></i><span>دامنه‌ی پنل مقابل از داخل خود کلید خوانده می‌شود. بعد از اتصال می‌توانید با تیک‌ها مشخص کنید کدام اطلاعات ادغام و استفاده شود.</span></div>
      <div id="nc-error" style="display:none;align-items:flex-start;gap:7px;margin-top:11px;background:var(--red-bg);border:1px solid rgba(239,68,68,.3);border-radius:11px;padding:9px 12px;font-size:11px;color:var(--red-t);line-height:1.6"><i class="ti ti-alert-circle" style="font-size:14px;margin-top:1px;flex-shrink:0"></i><span></span></div>
      <div class="modal-v2-footer">
        <button class="btn btn-o" onclick="closeModal('modal-node-connect')" style="flex:.6">انصراف</button>
        <button class="btn btn-g" id="nc-btn" onclick="connectNode()"><i class="ti ti-plug-connected"></i> اتصال</button>
      </div>
    </div>
  </div>
</div>
<div class="modal-bg" id="modal-edit-link">
  <div class="modal-v2 cm-modal">
    <div class="modal-v2-head">
      <button class="modal-v2-close" onclick="closeModal('modal-edit-link')"><i class="ti ti-x"></i></button>
      <div class="modal-v2-icon"><i class="ti ti-edit"></i></div>
      <div class="modal-v2-title">ویرایش کانفیگ</div>
      <div class="modal-v2-sub">مشخصات کانفیگ انتخاب‌شده را تغییر دهید</div>
    </div>
    <div class="modal-v2-body">
      <input type="hidden" id="el-uuid">
      <input type="hidden" id="el-node-id">
      <div class="fg" id="el-node-notice" style="display:none;margin-bottom:13px"></div>
      <div class="modal-v2-field"><label><i class="ti ti-tag"></i> عنوان</label><input class="modal-v2-input" id="el-label"></div>
      <div class="form-row" style="display:flex;gap:10px">
        <div class="modal-v2-field" style="flex:1"><label><i class="ti ti-database"></i> سهمیه (0 = نامحدود)</label><input class="modal-v2-input" id="el-val" type="number" min="0" step="0.1"></div>
        <div class="modal-v2-field" style="flex:.6"><label><i class="ti ti-ruler"></i> واحد</label><select class="modal-v2-input fs" id="el-unit"><option value="GB">GB</option><option value="MB">MB</option></select></div>
      </div>
      <div class="modal-v2-field"><label><i class="ti ti-calendar-time"></i> انقضا (روز از الان، 0 = بدون تغییر/نامحدود)</label><input class="modal-v2-input" id="el-exp" type="number" min="0" step="1"></div>
      <div class="modal-v2-field" style="margin-bottom:0"><label><i class="ti ti-note"></i> یادداشت</label><input class="modal-v2-input" id="el-note"></div>
      <div class="modal-v2-hint" style="margin-top:11px"><i class="ti ti-info-circle"></i><span>برای حفظ انقضای فعلی، فیلد انقضا را صفر بگذارید.</span></div>
      <div class="modal-v2-footer">
        <button class="modal-v2-btn-cancel" onclick="closeModal('modal-edit-link')">انصراف</button>
        <button class="modal-v2-btn-submit" onclick="saveEditLink()"><i class="ti ti-check"></i> ذخیره تغییرات</button>
      </div>
    </div>
  </div>
</div>
<div class="mob-top">
  <div class="ml">
    <div class="mob-logo"><img src="https://yt3.googleusercontent.com/vA6bYj1V386YmibpWRNFJtsRRqwfY_U9wnb7gmW90eRVXyNB7gAfjj1XPs5UX0cdKdQprrI=s160-c-k-c0x00ffffff-no-rj" alt="cb"></div>
    <span class="mob-title">RVG Gateway</span>
  </div>
  <div class="mob-right">
    <button class="theme-mob" id="theme-mob-btn" onclick="toggleTheme()"><i class="ti ti-sun" id="theme-mob-icon"></i></button>
    <button class="menu-btn" id="open-sb"><i class="ti ti-menu-2"></i></button>
  </div>
</div>
<div class="overlay" id="overlay"></div>
<aside class="sidebar" id="sb">
  <button class="sb-close" id="close-sb"><i class="ti ti-x"></i></button>
  <div class="logo">
    <div class="logo-img"><img src="https://yt3.googleusercontent.com/vA6bYj1V386YmibpWRNFJtsRRqwfY_U9wnb7gmW90eRVXyNB7gAfjj1XPs5UX0cdKdQprrI=s160-c-k-c0x00ffffff-no-rj" alt="cb"></div>
    <div><div class="logo-name">codebox</div><div class="logo-sub">RVG Gateway · v9.2</div></div>
  </div>
  <div class="nav-wrap">
    <div class="nav-sec">پنل</div>
    <div class="nav-it on" data-pg="overview"><i class="ti ti-layout-dashboard"></i> داشبورد</div>
    <div class="nav-it" data-pg="links"><i class="ti ti-link-plus"></i> کانفیگ‌ها <span class="nav-badge" id="links-nb">0</span></div>
    <div class="nav-it" data-pg="subgroups"><i class="ti ti-folders"></i> گروه‌های ساب <span class="nav-badge" id="subs-nb">0</span></div>
    <div class="nav-it" data-pg="subscriptions"><i class="ti ti-rss"></i> سابسکریپشن</div>
    <div class="nav-it" data-pg="traffic"><i class="ti ti-chart-area"></i> ترافیک</div>
    <div class="nav-it" data-pg="connections"><i class="ti ti-plug-connected"></i> اتصالات <span class="nav-badge" id="conns-nb">0</span></div>
    <div class="nav-it" data-pg="nodes"><i class="ti ti-topology-star-3"></i> نود <span class="nav-badge" id="nodes-nb">0</span></div>
    <div class="nav-sec">سیستم</div>
    <div class="nav-it" data-pg="backup"><i class="ti ti-database-export"></i> بکاپ‌گیری</div>
    <div class="nav-it" data-pg="updates"><i class="ti ti-cloud-download"></i> نسخه و بروزرسانی <span class="nav-badge" id="update-nb" style="display:none">1</span></div>
    <div class="nav-it" data-pg="support"><i class="ti ti-headset"></i> پشتیبانی <span class="nav-badge" id="support-nb" style="display:none">●</span></div>
    <div class="nav-it" data-pg="logs"><i class="ti ti-history"></i> لاگ فعالیت‌ها</div>
    <div class="nav-it" data-pg="errors"><i class="ti ti-alert-triangle"></i> خطاها</div>
    <div class="nav-it" data-pg="settings"><i class="ti ti-settings"></i> تنظیمات</div>
  </div>
  <div class="sb-foot">
    <button class="theme-btn" onclick="toggleTheme()"><i class="ti ti-moon" id="theme-icon"></i> <span id="theme-label">تم روشن</span></button>
    <a class="tg-btn" href="https://t.me/CodeBoxo" target="_blank" rel="noopener"><i class="ti ti-brand-telegram"></i> @CodeBoxo</a>
    <button class="logout-btn" id="logout-btn"><i class="ti ti-logout"></i> خروج</button>
  </div>
</aside>
<main class="main">
<div class="ann-banner-wrap" id="ann-banner-wrap"></div>
<section class="pg on" id="pg-overview">
  <div class="topbar">
    <div><div class="tb-title"><i class="ti ti-layout-dashboard"></i> داشبورد</div><div class="tb-sub" id="last-upd">در حال بارگذاری...</div></div>
    <div class="tb-right">
      <span class="badge bg-green"><span class="dot dg pulse"></span> فعال</span>
      <span class="badge bg-blue" id="uptime-badge">—</span>
      <button class="btn btn-p btn-sm" onclick="refreshAll()"><i class="ti ti-refresh"></i> رفرش</button>
    </div>
  </div>
  <div class="metrics">
    <div class="metric"><div class="m-icon"><i class="ti ti-plug-connected"></i></div><div class="m-label">اتصالات فعال</div><div class="m-val" id="m-conns">—</div><div class="m-sub"><span class="dot dg pulse"></span> WebSocket / XHTTP زنده</div></div>
    <div class="metric"><div class="m-icon"><i class="ti ti-transfer"></i></div><div class="m-label">کل ترافیک</div><div class="m-val" id="m-traffic">—<span class="m-unit">MB</span></div><div class="m-sub">از راه‌اندازی</div></div>
    <div class="metric suc"><div class="m-icon suc"><i class="ti ti-link"></i></div><div class="m-label">کانفیگ فعال</div><div class="m-val" id="m-alinks">—</div><div class="m-sub" id="m-lsub">از کل</div></div>
    <div class="metric pur"><div class="m-icon pur"><i class="ti ti-folders"></i></div><div class="m-label">گروه‌های ساب</div><div class="m-val" id="m-subs">—</div><div class="m-sub">فعال</div></div>
  </div>
  <div class="vless-box">
    <div class="vl-header">
      <div class="vl-title"><i class="ti ti-link"></i> لینک پیش‌فرض (بدون محدودیت)</div>
      <span class="badge bg-blue"><span class="dot db"></span> TLS 443 · WS</span>
    </div>
    <div class="vl-code" id="vless-main">در حال دریافت...</div>
    <div class="vl-actions">
      <button class="btn btn-p" onclick="cpText('vless-main')"><i class="ti ti-copy"></i> کپی</button>
      <button class="btn btn-g" onclick="qrFor('vless-main')"><i class="ti ti-qrcode"></i> QR</button>
      <button class="btn btn-o" onclick="navTo('links')"><i class="ti ti-link-plus"></i> کانفیگ محدود</button>
      <button class="btn btn-pur" onclick="navTo('subgroups')"><i class="ti ti-folders"></i> گروه‌های ساب</button>
    </div>
  </div>
  <div class="g3">
    <div class="card"><div class="card-title"><i class="ti ti-chart-area"></i> ترافیک ساعتی (MB)</div><div class="ch"><canvas id="ch1"></canvas></div></div>
    <div class="card"><div class="card-title"><i class="ti ti-chart-donut"></i> توزیع</div><div class="ch-sm"><canvas id="ch2"></canvas></div></div>
  </div>
  <div class="g2">
    <div class="card">
      <div class="card-title"><i class="ti ti-activity"></i> وضعیت سرویس</div>
      <div class="sr"><span class="sr-k"><i class="ti ti-shield-check"></i> UUID Auth</span><span class="sr-v" style="color:var(--green-t)">● فعال · سخت‌گیرانه</span></div>
      <div class="sr"><span class="sr-k"><i class="ti ti-circle-check"></i> VLESS / WS Tunnel</span><span class="sr-v" style="color:var(--green-t)">● فعال</span></div>
      <div class="sr"><span class="sr-k"><i class="ti ti-bolt"></i> Siz10a XHTTP Ultra</span><span class="sr-v" style="color:var(--green-t)">● فعال · 3 mode</span></div>
      <div class="sr"><span class="sr-k"><i class="ti ti-folders"></i> Sub Groups</span><span class="sr-v" style="color:var(--green-t)">● فعال v9</span></div>
      <div class="sr"><span class="sr-k"><i class="ti ti-rss"></i> Subscription API</span><span class="sr-v" style="color:var(--green-t)">● فعال</span></div>
      <div class="sr"><span class="sr-k"><i class="ti ti-clock"></i> آپتایم</span><span class="sr-v" id="uptime-inline">—</span></div>
      <div class="sr" style="flex-direction:column;align-items:flex-start;gap:4px">
        <div style="width:100%;display:flex;justify-content:space-between"><span class="sr-k"><i class="ti ti-gauge"></i> بار نسبی</span><span class="sr-v" id="bw-pct">—%</span></div>
        <div class="spbar" style="width:100%"><div class="spfill" id="bw-bar" style="width:0%"></div></div>
      </div>
    </div>
    <div class="card">
      <div class="card-title"><i class="ti ti-list"></i> خلاصه کانفیگ‌ها <span class="ml-auto badge bg-blue" id="lsummary-badge">۰</span></div>
      <div id="lsummary">—</div>
    </div>
  </div>
  <div class="dash-footer">
    <span class="df-text">codebox RVG Gateway v9.2 · Railway · 2025</span>
    <a class="df-link" href="https://t.me/CodeBoxo" target="_blank"><i class="ti ti-brand-telegram"></i> t.me/CodeBoxo</a>
  </div>
</section>
<section class="pg" id="pg-links">
  <div class="topbar">
    <div style="display:flex;justify-content:flex-end;gap:8px;margin-bottom:16px">
      <button class="btn btn-p" onclick="openModal('modal-create-link')">
        <i class="ti ti-square-rounded-plus"></i> ساخت کانفیگ جدید
      </button>
      <button class="btn btn-g" style="margin-right:14px" onclick="openModal('modal-bot-tcp-proxy');btpCheckTokenState()">
        <i class="ti ti-server-2"></i> Bot tcp proxy
      </button>
      <button class="btn btn-g" id="zeus-nav-btn" style="margin-right:8px" onclick="openModal('modal-zeus-proxy');zpCheckTokenState()">
        <i class="ti ti-bolt"></i> Zeus proxy
      </button>
    </div>
    <div class="tb-right">
      <label class="links-selectall" id="links-selectall-wrap" style="display:none">
        <div class="cfg-check" id="links-selectall-check" onclick="toggleSelectAllLinks()"><i class="ti ti-check"></i></div>
        انتخاب همه
      </label>
      <span class="badge bg-blue" id="links-pg-cnt">۰ کانفیگ</span>
    </div>
  </div>

  <div class="links-bulkbar" id="links-bulkbar">
    <div class="links-bulkbar-count"><i class="ti ti-checks"></i> <span id="links-bulkbar-n">۰</span> کانفیگ انتخاب شده</div>
    <div class="links-bulkbar-actions">
      <button class="btn btn-sm btn-g" onclick="clearLinkSelection()"><i class="ti ti-x"></i> لغو انتخاب</button>
      <button class="btn btn-sm btn-d" onclick="bulkDeleteLinks()"><i class="ti ti-trash"></i> حذف انتخاب‌شده‌ها</button>
    </div>
  </div>

  <div class="info-strip">
    <div class="info-item">
      <span class="info-item-label">ارسال / دریافت لحظه‌ای</span>
      <span class="info-item-val"><i class="ti ti-arrows-exchange"></i> <span id="info-sent-recv">0 B / 0 B</span></span>
    </div>
    <div class="info-item">
      <span class="info-item-label">مصرف دوره فعلی</span>
      <span class="info-item-val"><i class="ti ti-chart-pie"></i> <span id="info-usage">0 B</span></span>
    </div>
    <div class="info-item">
      <span class="info-item-label">مصرف کل از ابتدا</span>
      <span class="info-item-val"><i class="ti ti-history"></i> <span id="info-alltime">0 B</span></span>
    </div>
    <div class="info-item">
      <span class="info-item-label">تعداد این‌باندها</span>
      <span class="info-item-val"><i class="ti ti-list-details"></i> <span id="info-inbounds">0</span></span>
    </div>
    <div class="info-item">
      <span class="info-item-label">کلاینت‌ها</span>
      <span class="info-item-val"><i class="ti ti-users"></i> <span class="info-badge" id="info-clients">0</span></span>
    </div>
  </div>

  <div class="cfg-grid" id="links-grid"></div>
  <div class="empty" id="links-empty" style="display:none"><i class="ti ti-link-off"></i><p>هنوز کانفیگی وجود ندارد</p></div>
</section>
<section class="pg" id="pg-subgroups">
  <div class="topbar">
    <div><div class="tb-title"><i class="ti ti-folders"></i> گروه‌های ساب</div><div class="tb-sub">هر گروه یک صفحه پابلیک مجزا با کانفیگ‌های خودش دارد</div></div>
    <div class="tb-right">
      <span class="badge bg-purple" id="subs-pg-cnt">۰ گروه</span>
      <button class="btn btn-pur" onclick="openCreateSubModal()"><i class="ti ti-folder-plus"></i> گروه جدید</button>
    </div>
  </div>
  <div class="subs-toolbar">
    <div class="subs-search">
      <i class="ti ti-search"></i>
      <input type="text" id="subs-search-inp" placeholder="جستجو در گروه‌ها..." oninput="filterSubs(this.value)">
    </div>
  </div>
  <div class="sub-grid" id="subs-grid">
    <div class="subs-empty-v2"><div class="subs-empty-v2-icon"><i class="ti ti-folders"></i></div><div class="subs-empty-v2-title">هنوز گروهی وجود ندارد</div><div class="subs-empty-v2-sub">یک گروه جدید بسازید تا کانفیگ‌ها را دسته‌بندی کنید</div></div>
  </div>
</section>
<section class="pg" id="pg-subscriptions">
  <div class="topbar"><div><div class="tb-title"><i class="ti ti-rss"></i> سابسکریپشن</div><div class="tb-sub">لینک‌های اشتراک برای اپ‌های v2ray</div></div></div>
  <div class="g2">
    <div class="card">
      <div class="card-title"><i class="ti ti-rss"></i> سابسکریپشن تکی (هر کانفیگ)</div>
      <p style="font-size:11.5px;color:var(--t3);line-height:1.8;margin-bottom:12px">هر کانفیگ URL سابسکریپشن مخصوص دارد. از کارت کانفیگ روی آیکون <i class="ti ti-rss"></i> کلیک کنید.</p>
    </div>
    <div class="card">
      <div class="card-title"><i class="ti ti-database"></i> سابسکریپشن کامل (ادمین)</div>
      <p style="font-size:11.5px;color:var(--t3);line-height:1.8;margin-bottom:4px">شامل تمام کانفیگ‌های فعال.</p>
      <div class="sub-box"><span class="sub-url" id="sub-all-url">در حال دریافت...</span><div style="display:flex;gap:6px"><button class="btn btn-sm btn-g" onclick="cpSubAll()"><i class="ti ti-copy"></i></button><button class="btn btn-sm btn-g" onclick="window.open(location.protocol+'//'+location.host+'/sub-all')"><i class="ti ti-external-link"></i></button></div></div>
      <div class="cl amber" style="margin-top:11px"><i class="ti ti-alert-triangle"></i><span>این آدرس فقط در مرورگری که به پنل وارد شده کار می‌کند (نیاز به کوکی سشن).</span></div>
    </div>
  </div>
  <div class="card">
    <div class="card-title"><i class="ti ti-folders"></i> لینک سابسکریپشن گروه‌ها</div>
    <div id="sub-groups-list">در حال بارگذاری...</div>
  </div>
</section>
<section class="pg" id="pg-traffic">
  <div class="topbar">
    <div><div class="tb-title"><i class="ti ti-chart-area"></i> ترافیک</div><div class="tb-sub">تحلیل و مانیتورینگ مصرف پهنای باند</div></div>
    <div class="tb-right"><button class="btn btn-p btn-sm" onclick="refreshAll()"><i class="ti ti-refresh"></i> رفرش</button></div>
  </div>

  <div class="traf-hero">
    <div class="traf-main-stat">
      <div class="traf-main-label"><i class="ti ti-database"></i> کل ترافیک مصرفی</div>
      <div class="traf-main-val" id="t-traffic">—<span>MB</span></div>
      <div class="traf-trend up" id="t-trend"><i class="ti ti-trending-up"></i> <span id="t-trend-val">—</span></div>
    </div>
    <div class="traf-mini">
      <div class="traf-mini-top"><div class="traf-mini-icon"><i class="ti ti-arrow-up-right"></i></div><span class="traf-mini-label">میانگین ساعتی</span></div>
      <div><div class="traf-mini-val" id="t-avg">—</div><div class="traf-mini-sub">MB در ساعت</div></div>
    </div>
    <div class="traf-mini">
      <div class="traf-mini-top"><div class="traf-mini-icon pk"><i class="ti ti-chart-bar"></i></div><span class="traf-mini-label">پیک مصرف</span></div>
      <div><div class="traf-mini-val" id="t-peak">—</div><div class="traf-mini-sub" id="t-peak-time">بالاترین ساعت</div></div>
    </div>
    <div class="traf-mini">
      <div class="traf-mini-top"><div class="traf-mini-icon lo"><i class="ti ti-clock-hour-4"></i></div><span class="traf-mini-label">کمترین مصرف</span></div>
      <div><div class="traf-mini-val" id="t-low">—</div><div class="traf-mini-sub">MB در ساعت</div></div>
    </div>
  </div>

  <div class="traf-chart-card">
    <div class="traf-chart-head">
      <div>
        <div class="traf-chart-title"><i class="ti ti-activity"></i> روند مصرف ترافیک</div>
        <div class="traf-chart-sub">بر اساس مگابایت در هر ساعت</div>
      </div>
      <div class="traf-legend">
        <div class="traf-legend-item"><span class="traf-legend-dot" style="background:var(--accent)"></span> مصرف</div>
        <div class="traf-legend-item"><span class="traf-legend-dot" style="background:var(--amber)"></span> میانگین</div>
      </div>
    </div>
    <div class="traf-chart-body"><canvas id="ch3"></canvas></div>
  </div>
</section>
<section class="pg" id="pg-connections">
  <div class="topbar">
    <div><div class="tb-title"><i class="ti ti-plug-connected"></i> اتصالات فعال</div><div class="tb-sub">مانیتورینگ زنده‌ی آی‌پی و ترافیک هر اتصال</div></div>
    <div class="tb-right"><span class="badge bg-green" id="conns-live">—</span><button class="btn btn-p btn-sm" onclick="refreshAll()"><i class="ti ti-refresh"></i> رفرش</button></div>
  </div>

  <div class="conn-hero">
    <div class="conn-hero-tile">
      <div class="conn-hero-icon"><i class="ti ti-plug-connected"></i></div>
      <div class="conn-hero-label">اتصالات زنده</div>
      <div class="conn-hero-val" id="ch-count">—</div>
    </div>
    <div class="conn-hero-tile">
      <div class="conn-hero-icon"><i class="ti ti-transfer"></i></div>
      <div class="conn-hero-label">مجموع ترافیک لحظه‌ای</div>
      <div class="conn-hero-val" id="ch-traffic">—</div>
    </div>
    <div class="conn-hero-tile">
      <div class="conn-hero-icon"><i class="ti ti-clock"></i></div>
      <div class="conn-hero-label">میانگین مدت اتصال</div>
      <div class="conn-hero-val" id="ch-avgdur">—</div>
    </div>
    <div class="conn-hero-tile">
      <div class="conn-hero-icon"><i class="ti ti-map-pin"></i></div>
      <div class="conn-hero-label">آی‌پی‌های یکتا</div>
      <div class="conn-hero-val" id="ch-uniq">—</div>
    </div>
  </div>

  <div class="conn-toolbar">
    <div class="conn-toolbar-title"><i class="ti ti-list-details"></i> لیست اتصالات</div>
    <div class="conn-live-badge"><span class="conn-live-dot"></span> بروزرسانی خودکار هر ۵ ثانیه</div>
  </div>

  <div class="conn-grid-v2" id="conns-grid"></div>
  <div class="conn-empty-v2" id="conns-empty" style="display:none">
    <div class="conn-empty-v2-icon"><i class="ti ti-plug-off"></i></div>
    <div class="conn-empty-v2-title">هیچ اتصال فعالی نیست</div>
    <div class="conn-empty-v2-sub">به محض اتصال کلاینت‌ها، اینجا نمایش داده می‌شوند</div>
  </div>
</section>
<section class="pg" id="pg-nodes">
  <div class="node-hero">
    <div class="node-hero-net">
      <svg viewBox="0 0 600 90" preserveAspectRatio="none">
        <path class="nh-line" d="M20,70 C140,10 220,80 340,25 S520,60 580,15"></path>
        <path class="nh-line" d="M60,20 C160,75 260,15 380,60 S500,20 560,55" style="animation-duration:9s"></path>
        <circle class="nh-dot" cx="20" cy="70" r="2.6"></circle>
        <circle class="nh-dot" cx="340" cy="25" r="2.6"></circle>
        <circle class="nh-dot" cx="580" cy="15" r="2.6"></circle>
        <circle class="nh-dot" cx="60" cy="20" r="2.2"></circle>
        <circle class="nh-dot" cx="380" cy="60" r="2.2"></circle>
        <circle class="nh-dot" cx="560" cy="55" r="2.2"></circle>
      </svg>
    </div>
    <div class="node-hero-top">
      <div class="node-hero-title">
        <div class="node-hero-icon"><i class="ti ti-topology-star-3"></i></div>
        <div>
          <div class="tb-title">نود</div>
          <div class="tb-sub">چند پنل RVG را به هم متصل کنید تا کانفیگ‌ها و مصرف‌شان یکی شود</div>
        </div>
      </div>
      <div class="tb-right">
        <span class="badge bg-blue" id="nodes-pg-cnt">۰ نود</span>
        <button class="btn btn-p btn-sm" onclick="openNodeKeyModal()"><i class="ti ti-key"></i> ساخت کلید</button>
        <button class="btn btn-g btn-sm" onclick="openNodeConnectModal()"><i class="ti ti-plug-connected"></i> متصل کردن</button>
        <button class="btn btn-o btn-sm" onclick="loadNodes(true)"><i class="ti ti-refresh"></i> رفرش</button>
      </div>
    </div>
    <div class="node-hero-metrics">
      <div class="node-metric"><div class="node-metric-top"><i class="ti ti-transfer"></i><span class="node-metric-label">مصرف ترکیبی</span></div><div class="node-metric-val" id="na-used">—</div><div class="node-metric-sub" id="na-used-sub">این پنل + نودها</div></div>
      <div class="node-metric"><div class="node-metric-top"><i class="ti ti-link"></i><span class="node-metric-label">کانفیگ ترکیبی</span></div><div class="node-metric-val" id="na-links">—</div><div class="node-metric-sub" id="na-links-sub">از کل</div></div>
      <div class="node-metric"><div class="node-metric-top"><i class="ti ti-folders"></i><span class="node-metric-label">ساب‌ ترکیبی</span></div><div class="node-metric-val" id="na-subs">—</div><div class="node-metric-sub" id="na-subs-sub">این پنل + نودها</div></div>
      <div class="node-metric"><div class="node-metric-top"><i class="ti ti-arrows-exchange"></i><span class="node-metric-label">درخواست ترکیبی</span></div><div class="node-metric-val" id="na-reqs">—</div><div class="node-metric-sub" id="na-reqs-sub">این پنل + نودها</div></div>
    </div>
  </div>

  <div class="node-keys-card">
    <div class="card">
      <div class="card-title"><i class="ti ti-key"></i> کلیدهای صادرشده <span class="ml-auto badge bg-blue" id="nk-cnt">۰</span></div>
      <div id="nk-list">—</div>
      <div class="cl amber"><i class="ti ti-alert-triangle"></i><span>دسترسی هر کلید همان چیزی است که هنگام ساخت برایش تیک زده‌اید. کلید را فقط به پنل مورد اعتماد خودتان بدهید و در صورت شک، غیرفعالش کنید یا برای همیشه حذفش کنید.</span></div>
    </div>
  </div>

  <div class="conn-toolbar">
    <div class="conn-toolbar-title"><i class="ti ti-topology-ring"></i> نودهای متصل</div>
    <div class="conn-live-badge"><span class="conn-live-dot"></span> <span id="nodes-online-txt">—</span></div>
  </div>
  <div class="nodes-grid" id="nodes-grid"></div>
  <div class="conn-empty-v2" id="nodes-empty" style="display:none">
    <div class="node-empty-illust">
      <svg viewBox="0 0 100 100">
        <path class="ne-line" d="M22,78 L50,30"></path>
        <path class="ne-line" d="M78,78 L50,30" style="animation-duration:4s"></path>
        <path class="ne-line" d="M22,78 L78,78" style="animation-duration:6s"></path>
        <circle class="ne-dot mid" cx="50" cy="30" r="6"></circle>
        <circle class="ne-dot" cx="22" cy="78" r="5"></circle>
        <circle class="ne-dot" cx="78" cy="78" r="5"></circle>
      </svg>
    </div>
    <div class="conn-empty-v2-title">هنوز به نودی متصل نیستید</div>
    <div class="conn-empty-v2-sub">در پنل دیگر «ساخت کلید» را بزنید، کلید را کپی کنید و اینجا با «متصل کردن» وارد کنید</div>
  </div>
</section>
<section class="pg" id="pg-logs">

  <div class="topbar"><div><div class="tb-title"><i class="ti ti-history"></i> لاگ فعالیت‌ها</div><div class="tb-sub">تاریخچه‌ی کامل رخدادهای پنل</div></div><div class="tb-right"><button class="btn btn-p btn-sm" onclick="loadActivity()"><i class="ti ti-refresh"></i></button></div></div>
  <div class="card"><div class="log-timeline" id="logs-list">—</div><div class="empty" id="logs-empty" style="display:none"><i class="ti ti-history-toggle"></i><p>هنوز لاگی ثبت نشده</p></div></div>
</section>
<section class="pg" id="pg-errors">
  <div class="topbar"><div><div class="tb-title"><i class="ti ti-alert-triangle"></i> خطاها</div></div><div class="tb-right"><span class="badge bg-red" id="errs-badge">۰</span><button class="btn btn-p btn-sm" onclick="refreshAll()"><i class="ti ti-refresh"></i></button></div></div>
  <div class="card"><div class="card-title"><i class="ti ti-bug"></i> لاگ خطاها</div><div id="errs-full">—</div></div>
</section>
<section class="pg" id="pg-updates">
  <div class="topbar">
    <div><div class="tb-title"><i class="ti ti-cloud-download"></i> نسخه و بروزرسانی</div><div class="tb-sub">مدیریت نسخه‌ی پنل و تاریخچه‌ی کامل بروزرسانی‌ها</div></div>
    <div class="tb-right"><button class="btn btn-p btn-sm" onclick="loadVersion()"><i class="ti ti-refresh"></i> بررسی مجدد</button></div>
  </div>

  <div class="upd-hero" id="upd-hero">
    <div class="upd-hero-glow"></div>
    <div class="upd-hero-top">
      <div class="upd-hero-cur">
        <div class="upd-hero-icon"><i class="ti ti-package"></i></div>
        <div>
          <div class="upd-hero-label">نسخه‌ی نصب‌شده</div>
          <div class="upd-hero-ver" id="ver-current">—</div>
        </div>
      </div>
      <div class="upd-hero-status" id="ver-status-badge">
        <span class="upd-pill upd-pill-blue"><span class="upd-dot"></span> در حال بررسی...</span>
      </div>
    </div>
    <div class="upd-hero-desc" id="ver-current-desc">—</div>
    <div class="upd-hero-meta">
      <span class="upd-meta-chip"><i class="ti ti-brand-github"></i> <span id="ver-repo">—</span></span>
      <span class="upd-meta-chip"><i class="ti ti-git-branch"></i> <span id="ver-branch">—</span></span>
    </div>
  </div>

  <div class="upd-latest-card" id="upd-latest-card" style="display:none">
    <div class="upd-latest-left">
      <div class="upd-latest-icon"><i class="ti ti-sparkles"></i></div>
      <div>
        <div class="upd-latest-title">نسخه‌ی جدید موجود است</div>
        <div class="upd-latest-ver">نسخه‌ی <span id="ver-latest-num">—</span></div>
        <div class="upd-latest-desc" id="ver-latest-desc">—</div>
      </div>
    </div>
    <button class="upd-install-btn" id="update-btn" onclick="startUpdate()">
      <i class="ti ti-download"></i> نصب بروزرسانی
    </button>
  </div>

  <div class="upd-progress-card" id="update-progress-wrap" style="display:none">
    <div class="upd-progress-head">
      <div class="upd-progress-icon"><i class="ti ti-loader-2" style="animation:spin 1s linear infinite"></i></div>
      <div style="flex:1">
        <div class="upd-progress-title">در حال نصب بروزرسانی...</div>
        <div class="upd-progress-txt" id="update-progress-txt">در حال آماده‌سازی...</div>
      </div>
      <div class="upd-progress-pct" id="update-progress-pct">0%</div>
    </div>
    <div class="upd-progress-track"><div class="upd-progress-fill" id="update-progress-bar" style="width:0%"></div></div>
  </div>

  <div class="upd-log-card">
    <div class="upd-log-head">
      <div class="upd-log-title"><i class="ti ti-terminal-2"></i> لاگ زنده‌ی نصب</div>
      <button class="btn btn-o btn-sm" onclick="loadUpdateLog()"><i class="ti ti-refresh"></i> بروزرسانی لاگ</button>
    </div>
    <div class="upd-log-box" id="update-log-box">
      <p class="upd-log-empty">لاگی موجود نیست</p>
    </div>
  </div>

  <div class="upd-history-head">
    <div class="upd-history-title"><i class="ti ti-history"></i> تاریخچه‌ی بروزرسانی‌ها</div>
    <span class="badge bg-blue" id="upd-history-count">۰ مورد</span>
  </div>
  <div class="upd-timeline" id="upd-history-list">
    <div class="upd-history-empty"><i class="ti ti-history-toggle"></i><p>هنوز هیچ بروزرسانی‌ای ثبت نشده</p></div>
  </div>
</section>
<section class="pg" id="pg-support">
  <div class="sup-wrap">
    <div class="sup-head">
      <div class="sup-head-icon"><i class="ti ti-headset"></i></div>
      <div class="sup-head-text">
        <div class="sup-head-title">پشتیبانی RVG</div>
        <div class="sup-head-sub"><span class="sdot"></span> معمولاً در کمتر از چند ساعت پاسخ داده می‌شود</div>
      </div>
    </div>
    <div id="sup-blocked-banner" class="sup-blocked-banner" style="display:none">
      <i class="ti ti-lock"></i> دسترسی شما به ارسال پیام توسط پشتیبانی محدود شده است.
    </div>
    <div id="support-msgs"></div>
    <div class="sup-input-row" id="sup-input-row">
      <input class="fi" id="support-inp" placeholder="پیام خود را بنویسید..." style="flex:1" onkeydown="if(event.key==='Enter')sendSupportMsg()">
      <button class="btn btn-p" onclick="sendSupportMsg()"><i class="ti ti-send-2"></i></button>
    </div>
  </div>
</section>
<section class="pg" id="pg-backup">
  <div class="topbar">
    <div><div class="tb-title"><i class="ti ti-database-export"></i> بکاپ‌گیری و بازیابی</div><div class="tb-sub">دانلود کامل اطلاعات پنل یا بازگردانی از یک فایل بکاپ قبلی</div></div>
  </div>
  <div class="g2">
    <div class="card">
      <div class="card-title"><i class="ti ti-download"></i> دانلود بکاپ</div>
      <p style="font-size:11.5px;color:var(--t3);line-height:1.9;margin-bottom:14px">
        یک فایل JSON شامل تمام کانفیگ‌ها، گروه‌های ساب و رمز عبور (هش‌شده) دانلود می‌شود. این فایل را جایی امن نگه دارید.
      </p>
      <button class="btn btn-p" onclick="downloadBackup()"><i class="ti ti-cloud-download"></i> دانلود فایل بکاپ</button>
      <div class="cl" style="margin-top:14px"><i class="ti ti-info-circle"></i><span>این فایل شامل سکرت‌های پروکسی تلگرام هم هست؛ آن را در اختیار افراد غیرقابل‌اعتماد قرار ندهید.</span></div>
    </div>
    <div class="card">
      <div class="card-title"><i class="ti ti-upload"></i> بازیابی از بکاپ</div>
      <p style="font-size:11.5px;color:var(--t3);line-height:1.9;margin-bottom:14px">
        فایل بکاپی که قبلاً دانلود کرده‌اید را انتخاب کنید تا تمام کانفیگ‌ها و گروه‌ها روی این پنل بازیابی شوند (مثلاً بعد از نصب یک پنل جدید).
      </p>
      <div class="fg" style="margin-bottom:12px">
        <label>فایل بکاپ (JSON)</label>
        <input type="file" id="restore-file" accept="application/json,.json" class="fi" style="width:100%;padding:9px 12px">
      </div>
      <div class="sr" style="border:none;padding:0 0 12px">
        <span class="sr-k"><i class="ti ti-key"></i> رمز عبور فایل بکاپ هم بازگردانی شود؟</span>
        <button class="tog" id="restore-pw-tog" onclick="this.classList.toggle('on')"></button>
      </div>
      <button class="btn btn-d" onclick="restoreBackup()" id="restore-btn"><i class="ti ti-database-import"></i> شروع بازیابی</button>
      <div class="cl amber" style="margin-top:14px"><i class="ti ti-alert-triangle"></i><span>بازیابی، تمام کانفیگ‌ها و گروه‌های فعلی پنل را با اطلاعات فایل بکاپ جایگزین می‌کند و این کار غیرقابل بازگشت است.</span></div>
    </div>
  </div>
</section>
<section class="pg" id="pg-settings">
  <div class="topbar"><div><div class="tb-title"><i class="ti ti-settings"></i> تنظیمات</div></div></div>
  <div class="g2">
    <div class="srv-panel">
      <div class="srv-hero">
        <div class="srv-hero-icon"><i class="ti ti-server-2"></i></div>
        <div class="srv-hero-text">
          <div class="srv-hero-domain" id="set-host">—</div>
          <div class="srv-hero-sub"><span class="dot dg pulse"></span> آنلاین · Railway</div>
        </div>
      </div>
      <div class="srv-tiles">
        <div class="srv-tile"><div class="srv-tile-icon"><i class="ti ti-route"></i></div><div class="srv-tile-text"><div class="srv-tile-label">پورت</div><div class="srv-tile-val">443 (TLS)</div></div></div>
        <div class="srv-tile"><div class="srv-tile-icon"><i class="ti ti-versions"></i></div><div class="srv-tile-text"><div class="srv-tile-label">نسخه</div><div class="srv-tile-val">v9.2</div></div></div>
        <div class="srv-tile"><div class="srv-tile-icon"><i class="ti ti-brand-fastapi"></i></div><div class="srv-tile-text"><div class="srv-tile-label">فریم‌ورک</div><div class="srv-tile-val">FastAPI + Uvicorn</div></div></div>
        <div class="srv-tile"><div class="srv-tile-icon"><i class="ti ti-cloud"></i></div><div class="srv-tile-text"><div class="srv-tile-label">پلتفرم</div><div class="srv-tile-val">Railway</div></div></div>
        <div class="srv-tile" style="grid-column:1/-1"><div class="srv-tile-icon"><i class="ti ti-device-floppy"></i></div><div class="srv-tile-text"><div class="srv-tile-label">ذخیره‌سازی</div><div class="srv-tile-val">JSON File (/data)</div></div></div>
      </div>
      <div class="sr" style="border:none;padding:14px 0 0;margin-top:6px;border-top:1px solid var(--bd)">
        <span class="sr-k"><i class="ti ti-bolt-off"></i> توقف کامل لاگ‌گیری (برای بیشترین سرعت ممکن)</span>
        <button class="tog" id="disable-logging-tog" onclick="toggleLoggingSetting()"></button>
      </div>
      <div class="cl" style="margin-top:8px"><i class="ti ti-info-circle"></i><span>با فعال‌کردن این گزینه، هیچ لاگ و خطایی (نه در فایل، نه در پنل) ثبت نمی‌شود؛ فقط برای زمانی که همه‌چیز پایدار است و سرعت اولویت دارد روشنش کنید.</span></div>
    </div>
    <div class="pw-panel">
      <div class="pw-hero">
        <div class="pw-hero-icon"><i class="ti ti-key"></i></div>
        <div class="pw-hero-text">
          <div class="pw-hero-title">تغییر رمز عبور</div>
          <div class="pw-hero-sub">رمز قوی انتخاب کنید و آن را جایی امن نگه دارید</div>
        </div>
      </div>
      <div class="pw-body">
        <div class="pw-field">
          <label>رمز فعلی</label>
          <input class="pw-input" type="password" id="cp-cur" placeholder="رمز فعلی را وارد کنید">
          <button class="pw-eye" type="button" onclick="togglePwField('cp-cur',this)"><i class="ti ti-eye"></i></button>
        </div>
        <div class="pw-field" style="margin-bottom:6px">
          <label>رمز جدید</label>
          <input class="pw-input" type="password" id="cp-new" placeholder="حداقل ۴ کاراکتر" oninput="checkPwStrength(this.value)">
          <button class="pw-eye" type="button" onclick="togglePwField('cp-new',this)"><i class="ti ti-eye"></i></button>
        </div>
        <div class="pw-strength" id="pw-strength-bar">
          <div class="pw-strength-seg"></div><div class="pw-strength-seg"></div><div class="pw-strength-seg"></div><div class="pw-strength-seg"></div>
        </div>
        <div class="pw-strength-label" id="pw-strength-label"><i class="ti ti-shield"></i> قدرت رمز</div>
        <div class="pw-reqs">
          <span class="pw-req" id="req-len"><i class="ti ti-circle-dashed"></i> حداقل ۴ کاراکتر</span>
          <span class="pw-req" id="req-num"><i class="ti ti-circle-dashed"></i> شامل عدد</span>
          <span class="pw-req" id="req-case"><i class="ti ti-circle-dashed"></i> حروف بزرگ/کوچک</span>
        </div>
        <div class="pw-field" style="margin-bottom:18px">
          <label>تکرار رمز جدید</label>
          <input class="pw-input" type="password" id="cp-cf" placeholder="تکرار رمز جدید">
          <button class="pw-eye" type="button" onclick="togglePwField('cp-cf',this)"><i class="ti ti-eye"></i></button>
        </div>
        <button class="pw-submit" onclick="changePw()"><i class="ti ti-shield-check"></i> ذخیره رمز جدید</button>
      </div>
    </div>
  </div>
</section>
</main>
<script>
let isDark=localStorage.getItem('rvg-theme')!=='light';
let updateAvailable = false;
let updateVersion = '';
let updateDescription = '';

function dismissUpdate() {
  sessionStorage.setItem('rvg-update-dismissed', 'true');
  closeModal('modal-update');
}

function startUpdateFromModal() {
  closeModal('modal-update');
  startUpdate(); // تابع موجود
}
function applyTheme(dark){
  document.documentElement.setAttribute('data-theme',dark?'dark':'light');
  const icon=dark?'ti-sun':'ti-moon',label=dark?'تم روشن':'تم تاریک';
  document.getElementById('theme-icon').className='ti '+icon;
  document.getElementById('theme-label').textContent=label;
  const mobI=document.getElementById('theme-mob-icon');if(mobI)mobI.className='ti '+icon;
}

function toggleTheme(){isDark=!isDark;localStorage.setItem('rvg-theme',isDark?'dark':'light');applyTheme(isDark)}
applyTheme(isDark);
function toast(msg,type=''){
  const t=document.getElementById('toast');
  t.textContent=msg;t.className='toast show'+(type?' '+type:'');
  setTimeout(()=>t.classList.remove('show'),2400);
}
function fmtB(b){if(!b||b===0)return '0 B';if(b<1024)return b+' B';if(b<1024**2)return (b/1024).toFixed(1)+' KB';if(b<1024**3)return (b/1024**2).toFixed(2)+' MB';return (b/1024**3).toFixed(2)+' GB'}
function toFa(n){return String(n).replace(/\d/g,d=>'۰۱۲۳۴۵۶۷۸۹'[d])}
function esc(s){return String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function daysLeft(exp){if(!exp)return null;return Math.ceil((new Date(exp)-Date.now())/(864e5))}
function expChip(exp,expired){
  if(expired)return '<span class="exp-chip ec-exp"><i class="ti ti-calendar-x"></i> منقضی</span>';
  if(!exp)return '<span class="exp-chip ec-inf"><i class="ti ti-infinity"></i> نامحدود</span>';
  const d=daysLeft(exp);
  if(d<=0)return '<span class="exp-chip ec-exp"><i class="ti ti-calendar-x"></i> منقضی</span>';
  if(d<=3)return `<span class="exp-chip ec-warn"><i class="ti ti-alert-triangle"></i> ${toFa(d)} روز مانده</span>`;
  return `<span class="exp-chip ec-ok"><i class="ti ti-calendar-check"></i> ${toFa(d)} روز مانده</span>`;
}
function protoBadge(p){
  const m={
    'shadowsocks':['Shadowsocks','pc-ss'],
    'vless-ws':['VLESS · WS','pc-ws'],
    'xhttp-packet-up':['VLESS · XHTTP packet-up','pc-xhttp'],
    'xhttp-stream-up':['VLESS · XHTTP stream-up','pc-xhttp'],
    'trojan-ws':['Trojan · WS','pc-trojan'],
    'trojan-xhttp-packet-up':['Trojan · XHTTP packet-up','pc-trojan'],
    'trojan-xhttp-stream-up':['Trojan · XHTTP stream-up','pc-trojan'],
    'mtproto':['Telegram Proxy · MTProto','pc-trojan'],
  };
  const v=m[p]||['ناشناخته','pc-ws'];
  return `<span class="proto-chip ${v[1]}">${v[0]}</span>`;
}
async function checkAuth(){try{const r=await fetch('/api/me');const d=await r.json();if(!d.authenticated)location.href='/login';}catch(e){location.href='/login'}}
async function logout(){try{await fetch('/api/logout',{method:'POST'})}catch(e){}location.href='/login'}
document.getElementById('logout-btn').addEventListener('click',logout);
async function authF(url,opts={},skipAuthRedirect=false){
  const r=await fetch(url,opts);
  if(r.status===401 && !skipAuthRedirect){location.href='/login';throw new Error('unauthorized')}
  return r;
}
function setQuota(val,unit,el){
  document.getElementById('nl-val').value = val===0?'':val;
  document.getElementById('nl-unit').value = unit;
  document.querySelectorAll('#quota-chips .qc-pill').forEach(c=>c.classList.remove('active'));
  el.classList.add('active');
}
function setExpiry(days,el){
  document.getElementById('nl-exp').value = days===0?'':days;
  document.querySelectorAll('#exp-chips .qc-pill').forEach(c=>c.classList.remove('active'));
  el.classList.add('active');
}
function selectProto(val,el){
  document.getElementById('nl-proto').value = val;
  document.querySelectorAll('.proto-card').forEach(c=>c.classList.remove('active'));
  el.classList.add('active');
}
const sb=document.getElementById('sb'),overlay=document.getElementById('overlay');
function openSb(){sb.classList.add('open');overlay.classList.add('show')}
function closeSb(){sb.classList.remove('open');overlay.classList.remove('show')}
document.getElementById('open-sb').addEventListener('click',openSb);
document.getElementById('close-sb').addEventListener('click',closeSb);
overlay.addEventListener('click',closeSb);
function navTo(name){
  document.querySelectorAll('.nav-it').forEach(n=>n.classList.toggle('on',n.dataset.pg===name));
  document.querySelectorAll('.pg').forEach(p=>p.classList.toggle('on',p.id==='pg-'+name));
  const loaders={links:loadLinks,connections:loadConns,errors:loadErrs,subscriptions:loadSubsPage,subgroups:loadSubs,logs:loadActivity,updates:loadVersion,support:loadSupportMsgs,nodes:loadNodesPage};  if(loaders[name])loaders[name]();
  closeSb();window.scrollTo({top:0,behavior:'smooth'});
}
document.querySelectorAll('.nav-it').forEach(el=>el.addEventListener('click',()=>navTo(el.dataset.pg)));
function openModal(id){document.getElementById(id).classList.add('open')}
function closeModal(id){document.getElementById(id).classList.remove('open')}
let prevTraf=0,ch1,ch2,ch3;
async function fetchStats(){
  try{
    const r=await authF('/stats'),d=await r.json();
    document.getElementById('m-conns').textContent=d.active_connections;
    document.getElementById('conns-nb').textContent=d.active_connections;
    document.getElementById('m-traffic').innerHTML=d.total_traffic_mb.toFixed(1)+'<span class="m-unit">MB</span>';
    document.getElementById('m-alinks').textContent=d.active_links??'—';
    document.getElementById('m-lsub').textContent='از '+d.links_count+' کانفیگ';
    document.getElementById('m-subs').textContent=d.subs_count??'—';
    document.getElementById('errs-badge').textContent=d.total_errors+' خطا';
    document.getElementById('uptime-inline').textContent=d.uptime;
    document.getElementById('uptime-badge').textContent='Railway · '+d.uptime;
    document.getElementById('last-upd').textContent='آخرین بروزرسانی: '+new Date().toLocaleTimeString('fa-IR');
    document.getElementById('conns-live').innerHTML='<span class="dot dg pulse"></span> '+d.active_connections+' اتصال';
    document.getElementById('t-traffic').innerHTML=d.total_traffic_mb.toFixed(1)+'<span class="m-unit">MB</span>';
    const delta=d.total_traffic_mb-prevTraf,pct=Math.min(100,Math.round((delta/50)*100));
    document.getElementById('bw-pct').textContent=pct+'%';
    document.getElementById('bw-bar').style.width=pct+'%';
    prevTraf=d.total_traffic_mb;
    if(d.hourly){
      const labels=Object.keys(d.hourly).sort(),vals=labels.map(k=>+(d.hourly[k]/1024**2).toFixed(2));
      const avgAll=vals.length?vals.reduce((a,b)=>a+b,0)/vals.length:0;
      const avgLine=vals.map(()=>+avgAll.toFixed(2));
      if(ch1){ch1.data.labels=labels;ch1.data.datasets[0].data=vals;ch1.update();}
      if(ch3){ch3.data.labels=labels;ch3.data.datasets[0].data=vals;ch3.data.datasets[1].data=avgLine;ch3.update();}
      if(vals.length){
        const peak=Math.max(...vals),low=Math.min(...vals),peakIdx=vals.indexOf(peak);
        document.getElementById('t-avg').innerHTML=avgAll.toFixed(2)+'<span class="m-unit">MB</span>';
        document.getElementById('t-peak').innerHTML=peak.toFixed(2)+'<span class="m-unit">MB</span>';
        document.getElementById('t-peak-time').textContent=labels[peakIdx]?('ساعت '+labels[peakIdx]):'بالاترین ساعت';
        document.getElementById('t-low').innerHTML=low.toFixed(2)+'<span class="m-unit">MB</span>';
        const trendEl=document.getElementById('t-trend'),trendVal=document.getElementById('t-trend-val');
        if(vals.length>=2){
          const prev=vals[vals.length-2],last=vals[vals.length-1];
          const diffPct=prev>0?((last-prev)/prev*100):(last>0?100:0);
          const up=diffPct>=0;
          trendEl.classList.toggle('up',up);trendEl.classList.toggle('down',!up);
          trendEl.querySelector('i').className='ti '+(up?'ti-trending-up':'ti-trending-down');
          trendVal.textContent=(up?'+':'')+diffPct.toFixed(1)+'%';
        }else{
          trendVal.textContent='—';
        }
      }else{
        document.getElementById('t-avg').textContent='—';
        document.getElementById('t-peak').textContent='—';
        document.getElementById('t-low').textContent='—';
        document.getElementById('t-trend-val').textContent='—';
      }
    }
    renderErrs(d.recent_errors||[]);
  }catch(e){console.error(e)}
}
function renderErrs(errs){
  const el=document.getElementById('errs-full');if(!el)return;
  if(!errs.length){el.innerHTML='<div style="color:var(--green-t);padding:10px;font-size:12px;display:flex;align-items:center;gap:5px"><i class="ti ti-circle-check"></i> هیچ خطایی نیست</div>';return}
  el.innerHTML=errs.slice().reverse().map(e=>`<div class="erow"><div class="etime"><i class="ti ti-clock"></i>${new Date(e.time).toLocaleString('fa-IR')}</div><div class="emsg">${esc(e.error)}${e.url?' — '+esc(e.url):''}</div></div>`).join('');
}
async function loadActivity(){
  try{
    const r=await authF('/api/activity'),d=await r.json();
    const logs=(d.logs||[]).slice().reverse();
    const el=document.getElementById('logs-list'),em=document.getElementById('logs-empty');
    if(!logs.length){el.innerHTML='';em.style.display='block';return}
    em.style.display='none';
    const icMap={ok:'ti-circle-check',err:'ti-circle-x',warn:'ti-alert-triangle',info:'ti-info-circle'};
    const kindFa={link:'کانفیگ',sub:'گروه',auth:'ورود',connection:'اتصال',system:'سیستم'};
    el.innerHTML=logs.map(l=>`
      <div class="log-item">
        <div class="log-ic ${l.level}"><i class="ti ${icMap[l.level]||'ti-info-circle'}"></i></div>
        <div class="log-body">
          <div class="log-msg">${esc(l.message)}</div>
          <div class="log-time"><i class="ti ti-clock"></i> ${new Date(l.time).toLocaleString('fa-IR')} <span class="log-kind">${kindFa[l.kind]||l.kind}</span></div>
        </div>
      </div>
    `).join('');
  }catch(e){console.error(e)}
}
let allSubsList=[],allLinksList=[],onlineNodesList=[];
async function loadLinks(){
  try{
    const [lr,sr,nr,zr]=await Promise.all([authF('/api/links'),authF('/api/subs'),authF('/api/nodes/aggregate').catch(()=>null),authF('/api/zeus-proxy/status').catch(()=>null)]);
    const {links: localLinks=[]}=await lr.json();
    const {subs=[]}=await sr.json();
    try{ zeusStatus = zr ? await zr.json() : null; }catch(e){ zeusStatus = null; }
    document.getElementById('zeus-nav-btn').style.display = (zeusStatus && zeusStatus.phase==='done') ? 'none' : '';
    let nodeLinks=[];
    onlineNodesList=[];
    if(nr && nr.ok){
      try{
        const nd=await nr.json();
        (nd.nodes||[]).forEach(n=>{
          if(n.disabled||!n.online) return;
          onlineNodesList.push(n);
          (n.links||[]).forEach(l=>nodeLinks.push({...l,_nodeId:n.node_id,_nodeName:n.label||'نود'}));
        });
      }catch(e){}
    }
    const links=[...localLinks,...nodeLinks];
    allSubsList=subs;allLinksList=links;
    document.getElementById('info-inbounds').textContent = toFa(links.length);
    document.getElementById('info-clients').textContent = toFa(links.filter(l=>l.active).length);
    document.getElementById('info-alltime').textContent = fmtB(links.reduce((s,l)=>s+l.used_bytes,0));
    const nlSub=document.getElementById('nl-sub');
    nlSub.innerHTML='<option value="">— بدون گروه —</option>'+subs.map(s=>`<option value="${esc(s.sub_id)}">${esc(s.name)}</option>`).join('');
    const nlTarget=document.getElementById('nl-target'), nlTargetWrap=document.getElementById('nl-target-wrap');
    if(nlTarget){
      nlTarget.innerHTML='<option value="">این پنل</option>'+onlineNodesList.map(n=>`<option value="${esc(n.node_id)}">${esc(n.label||'نود')}</option>`).join('');
      if(nlTargetWrap) nlTargetWrap.style.display = onlineNodesList.length ? '' : 'none';
    }
    document.getElementById('links-nb').textContent=links.length;
    document.getElementById('links-pg-cnt').textContent=toFa(links.length)+' کانفیگ';
    document.getElementById('lsummary-badge').textContent=toFa(links.length);
    const liveUuids=new Set(links.map(l=>l.uuid));
    [...selectedLinkUuids].forEach(u=>{if(!liveUuids.has(u))selectedLinkUuids.delete(u)});
    document.getElementById('links-selectall-wrap').style.display=links.length?'flex':'none';
    const zeusExists = !!(zeusStatus && zeusStatus.phase==='done' && zeusStatus.result);
    const grid=document.getElementById('links-grid'),empty=document.getElementById('links-empty');
    if(!links.length && !zeusExists){grid.innerHTML='';empty.style.display='block';document.getElementById('lsummary').innerHTML='<div class="empty"><i class="ti ti-link-off"></i><p>کانفیگی وجود ندارد</p></div>';updateBulkBar();return}
    empty.style.display='none';
    const subMap=Object.fromEntries(subs.map(s=>[s.sub_id,s.name]));
    grid.innerHTML=(zeusExists?zeusCardHtml(zeusStatus):'')+links.map(l=>{
  const isNode=!!l._nodeId;
  const lim=l.limit_bytes===0?'∞':fmtB(l.limit_bytes);
  const pct=l.limit_bytes===0?0:Math.min(100,l.used_bytes/l.limit_bytes*100);
  const bc=pct>90?'var(--red)':pct>70?'var(--amber)':'var(--accent)';
  const allowed=l.active&&!l.expired;
  const cardCls=(!l.active?'is-off':(l.expired?'is-exp':''))+(isNode?' is-node':'');
  const isMt = l.protocol === 'mtproto';
  const adBtn = isMt
    ? `<button class="btn btn-sm btn-pur btn-icon" onclick="openAdTagModal('${l.uuid}','${esc(l.label)}','${esc(l.ad_tag||'')}')" title="تنظیم تبلیغ کانال"><i class="ti ti-speakerphone"></i></button>`
    : '';
  const idChip = isMt
    ? `<span class="cfg-uuid-mini" onclick="navigator.clipboard.writeText('${esc(l.mtproto_secret||'')}').then(()=>toast('سکرت کپی شد ✓','ok'))" title="سکرت کامل: ${esc(l.mtproto_secret||'')}"><i class="ti ti-key"></i> ${esc((l.mtproto_secret||'').slice(0,10))}…</span>`
    : `<span class="cfg-uuid-mini" onclick="navigator.clipboard.writeText('${l.uuid}').then(()=>toast('UUID کپی شد','ok'))" title="${l.uuid}"><i class="ti ti-fingerprint"></i> ${l.uuid.slice(0,10)}…</span>`;
  const nodeBadge = isNode ? `<span class="node-origin" style="margin-left:6px"><i class="ti ti-topology-star-3"></i> نود: ${esc(l._nodeName)}</span>` : '';
  return `<div class="cfg-card ${cardCls} ${selectedLinkUuids.has(l.uuid)?'selected':''}" data-uuid="${l.uuid}">
    <div class="cfg-row">
      ${isNode?'<span style="width:18px;flex-shrink:0"></span>':`<div class="cfg-check ${selectedLinkUuids.has(l.uuid)?'checked':''}" onclick="toggleLinkSelect('${l.uuid}',this)"><i class="ti ti-check"></i></div>`}
      <span class="cfg-status-dot ${allowed?'pulse':''}"></span>
      <div class="cfg-identity">
        <div class="cfg-label">${esc(l.label)} ${nodeBadge}</div>
        <div class="cfg-sub-meta">
          ${idChip}
          <span>${new Date(l.created_at).toLocaleDateString('fa-IR')}</span>
        </div>
      </div>
      <div class="cfg-divider-v"></div>
      <div class="cfg-usage-col">
        <div class="ubar"><div class="ubar-f" style="width:${pct}%;background:${bc}"></div></div>
        <div class="utxt"><span>${fmtB(l.used_bytes)}</span><span>از ${lim}</span></div>
      </div>
      <div class="cfg-divider-v"></div>
      <div class="cfg-exp-col">${expChip(l.expires_at,l.expired)}</div>
      <div class="cfg-divider-v"></div>
      <div class="cfg-badges-col">
        ${protoBadge(l.protocol)}
        ${isMt && l.ad_tag ? `<span class="cfg-sub-tag" style="background:linear-gradient(135deg,rgba(139,92,246,.18),rgba(109,72,214,.12));color:#A78BFA;padding:3px 9px;border-radius:20px;border:1px solid rgba(139,92,246,.25);font-weight:700"><i class="ti ti-speakerphone" style="color:#A78BFA"></i> تبلیغ فعال</span>` : ''}
        ${isMt && l.mtproto_public_host ? `<span class="cfg-sub-tag"><i class="ti ti-route"></i> ${esc(l.mtproto_public_host)}:${l.mtproto_public_port}</span>` : ''}
        ${isMt && !l.mtproto_public_host && l.mtproto_public_pending ? `<span class="cfg-sub-tag" style="color:var(--amber-t)"><i class="ti ti-loader-2" style="animation:spin 1s linear infinite"></i> در حال ساخت TCP Proxy عمومی...</span>` : ''}
        ${isMt && !l.mtproto_public_host && !l.mtproto_public_pending && !l.mtproto_manual_port ? `<span class="cfg-sub-tag" style="color:var(--red-t)"><i class="ti ti-alert-triangle"></i> بدون TCP Proxy عمومی — لینک کار نمی‌کند</span>` : ''}
        ${l.sub_id&&allSubsList.find(s=>s.sub_id===l.sub_id)?`<span class="cfg-sub-tag"><i class="ti ti-folder"></i> ${esc(allSubsList.find(s=>s.sub_id===l.sub_id).name)}</span>`:''}
      </div>
      <div class="cfg-divider-v"></div>
      <div class="cfg-actions">
        <div class="cfg-actions">
        <button class="tog${allowed?' on':''}" onclick="toggleActive('${l.uuid}',${!l.active}${isNode?`,'${l._nodeId}'`:''})" title="فعال/غیرفعال"></button>
        ${!isNode?adBtn:''}
        <button class="btn btn-sm btn-g btn-icon" onclick="navigator.clipboard.writeText('${esc(l.vless_link)}').then(()=>toast('لینک کپی شد','ok'))" title="کپی لینک"><i class="ti ti-copy"></i></button>
        ${isMt
          ? `<button class="btn btn-sm btn-g btn-icon" onclick="openMtInfoModal('${esc(l.label)}','${esc(l.mtproto_secret||'')}','${esc(l.vless_link)}',${!!l.mtproto_public_host})" title="اطلاعات پروکسی"><i class="ti ti-info-circle"></i></button>`
          : `<button class="btn btn-sm btn-g btn-icon" onclick="navigator.clipboard.writeText('${esc(l.sub_url)}').then(()=>toast('Sub کپی شد','ok'))" title="Sub URL"><i class="ti ti-rss"></i></button>
        <button class="btn btn-sm btn-g btn-icon" onclick="showQR('${esc(l.vless_link)}')" title="QR"><i class="ti ti-qrcode"></i></button>`
        }
        ${!isNode?`<button class="btn btn-sm btn-amber btn-icon" onclick="openEditLink('${l.uuid}')" title="ویرایش"><i class="ti ti-edit"></i></button>`:`<button class="btn btn-sm btn-amber btn-icon" onclick="openEditLink('${l.uuid}','${l._nodeId}')" title="ویرایش از راه دور"><i class="ti ti-edit"></i></button>`}
        <button class="btn btn-sm btn-g btn-icon" onclick="resetUsage('${l.uuid}'${isNode?`,'${l._nodeId}'`:''})" title="ریست مصرف"><i class="ti ti-rotate"></i></button>
        <button class="btn btn-sm btn-d btn-icon" onclick="deleteLink('${l.uuid}'${isNode?`,'${l._nodeId}'`:''})" title="حذف"><i class="ti ti-trash"></i></button>
      </div>
      </div>
    </div>
  </div>`;
}).join('');
    document.getElementById('lsummary').innerHTML=links.slice(0,6).map(l=>`<div class="sr"><span class="sr-k" style="gap:5px"><i class="ti ${l.expired?'ti-calendar-x':l.active?'ti-circle-check':'ti-circle-x'}" style="color:${l.expired?'var(--amber)':l.active?'var(--green)':'var(--red)'}"></i>${esc(l.label)}</span><span class="sr-v" style="font-size:10px">${fmtB(l.used_bytes)} / ${l.limit_bytes===0?'∞':fmtB(l.limit_bytes)}</span></div>`).join('');
    updateBulkBar();
  }catch(e){console.error(e)}
}

/* ══════ انتخاب گروهی و حذف دسته‌جمعی کانفیگ‌ها ══════ */
let selectedLinkUuids=new Set();
function toggleLinkSelect(uuid,el){
  if(selectedLinkUuids.has(uuid)){selectedLinkUuids.delete(uuid);el.classList.remove('checked');el.closest('.cfg-card')?.classList.remove('selected')}
  else{selectedLinkUuids.add(uuid);el.classList.add('checked');el.closest('.cfg-card')?.classList.add('selected')}
  updateBulkBar();
}
function toggleSelectAllLinks(){
  const selectable=allLinksList.filter(l=>!l._nodeId);
  const allSelected=selectable.length>0&&selectedLinkUuids.size===selectable.length;
  if(allSelected){selectedLinkUuids.clear()}
  else{selectedLinkUuids=new Set(selectable.map(l=>l.uuid))}
  document.querySelectorAll('#links-grid .cfg-card').forEach(card=>{
    const on=selectedLinkUuids.has(card.dataset.uuid);
    card.classList.toggle('selected',on);
    card.querySelector('.cfg-check')?.classList.toggle('checked',on);
  });
  updateBulkBar();
}
function clearLinkSelection(){
  selectedLinkUuids.clear();
  document.querySelectorAll('#links-grid .cfg-card').forEach(card=>{
    card.classList.remove('selected');
    card.querySelector('.cfg-check')?.classList.remove('checked');
  });
  updateBulkBar();
}
function updateBulkBar(){
  const bar=document.getElementById('links-bulkbar');
  const n=selectedLinkUuids.size;
  bar.classList.toggle('show',n>0);
  document.getElementById('links-bulkbar-n').textContent=toFa(n);
  const allCheck=document.getElementById('links-selectall-check');
  const selectableN=allLinksList.filter(l=>!l._nodeId).length;
  if(allCheck)allCheck.classList.toggle('checked',selectableN>0&&n===selectableN);
}
async function bulkDeleteLinks(){
  const n=selectedLinkUuids.size;
  if(!n)return;
  if(!confirm(`${toFa(n)} کانفیگ انتخاب‌شده حذف شود؟ این عمل قابل بازگشت نیست.`))return;
  const uuids=[...selectedLinkUuids];
  try{
    const results=await Promise.all(uuids.map(u=>authF('/api/links/'+u,{method:'DELETE'}).then(r=>r.ok).catch(()=>false)));
    const okCount=results.filter(Boolean).length;
    selectedLinkUuids.clear();
    if(okCount===uuids.length)toast(`${toFa(okCount)} کانفیگ حذف شد ✓`,'ok');
    else toast(`${toFa(okCount)} از ${toFa(uuids.length)} کانفیگ حذف شد`,okCount>0?'ok':'err');
    loadLinks();
  }catch(e){toast('خطا در حذف گروهی','err')}
}

let protoBase = 'vless', protoTransport = 'ws';

function qcTab(name, el){
  document.querySelectorAll('.qc-tab').forEach(t=>t.classList.remove('active'));
  el.classList.add('active');
  document.querySelectorAll('.qc-pane').forEach(p=>p.classList.remove('active'));
  document.getElementById('qc-pane-'+name).classList.add('active');
}

let cmBase = 'vless', cmTransport = 'ws';

function cmToggleDD(id){
  const el = document.getElementById(id);
  const isOpen = el.classList.contains('open');
  document.querySelectorAll('.cm-dd').forEach(d => d.classList.remove('open'));
  if(!isOpen) el.classList.add('open');
}

const BASE_INFO = {
  vless:    { icon:'ti-bolt',           title:'VLESS',          desc:'سبک، سریع و پرکاربردترین گزینه' },
  trojan:   { icon:'ti-shield-lock',    title:'Trojan',         desc:'شبیه‌سازی ترافیک HTTPS معمولی' },
  shadowsocks: { icon:'ti-shield-lock-filled', title:'Shadowsocks', desc:'رمزنگاری AEAD مستقیم، بدون نیاز به TLS خارجی' },
  telproxy: { icon:'ti-brand-telegram', title:'Telegram Proxy', desc:'پروکسی MTProto مستقیم روی یک پورت TCP اختصاصی' },
};
const TRANSPORT_INFO = {
  'ws':               { icon:'ti-link',    title:'WebSocket',            desc:'پایدار و سازگار با همه شرایط شبکه' },
  'xhttp-packet-up':  { icon:'ti-package', title:'XHTTP · packet-up',    desc:'سازگاری بالا با CDN و پروکسی‌ها' },
  'xhttp-stream-up':  { icon:'ti-rocket',  title:'XHTTP · stream-up',    desc:'تاخیر پایین‌تر برای اتصال‌های پرسرعت' }
};

function cmSelectBase(val, el){
  cmBase = val;
  document.querySelectorAll('#dd-base .cm-opt').forEach(o => o.classList.remove('sel'));
  el.classList.add('sel');
  const info = BASE_INFO[val];
  document.getElementById('dd-base-icon').innerHTML = `<i class="ti ${info.icon}"></i>`;
  document.getElementById('dd-base-current').textContent = info.title;
  document.getElementById('dd-base-current-desc').textContent = info.desc;
  cmToggleDD('dd-base');

  // ریست ترابرد به WS هر بار که پروتکل پایه عوض می‌شه (جلوگیری از state قدیمی)
  cmTransport = 'ws';
  document.querySelectorAll('#dd-transport .cm-opt').forEach(o => o.classList.remove('sel'));
  document.querySelector('#dd-transport .cm-opt[data-t="ws"]')?.classList.add('sel');
  const wsInfo = TRANSPORT_INFO['ws'];
  document.getElementById('dd-transport-icon').innerHTML = `<i class="ti ${wsInfo.icon}"></i>`;
  document.getElementById('dd-transport-current').textContent = wsInfo.title;
  document.getElementById('dd-transport-current-desc').textContent = wsInfo.desc;


  const streamSection = document.getElementById('stream-section');
  const normalNote = document.getElementById('transport-note');
  const mtNote = document.getElementById('mtproto-note');
  const portField = document.getElementById('mtproto-port-field');
  const ssField = document.getElementById('ss-cipher-field');

  if (val === 'telproxy') {
    streamSection.style.display = 'none';
    normalNote.style.display = 'none';
    mtNote.style.display = 'flex';
    portField.style.display = 'block';
    if (ssField) ssField.style.display = 'none';
    document.getElementById('cm-head-title').textContent = 'ساخت پروکسی جدید';
    document.getElementById('cm-head-sub').textContent = 'ساخت پروکسی تلگرام (MTProto) با پورت TCP اختصاصی';
    document.getElementById('cm-submit-text').textContent = 'ساخت پروکسی';
    document.getElementById('cm-head-icon').innerHTML = '<i class="ti ti-brand-telegram"></i>';
  } else if (val === 'shadowsocks') {
    // Shadowsocks فقط یک حالت واقعی داره (SIP002 + plugin=v2ray-plugin برای WS+TLS)؛
    // xhttp روی هیچ کلاینت رایجی (v2rayN, NekoBox, ...) برای SS پشتیبانی نمیشه،
    // پس منوی transport اصلاً نشون داده نمیشه تا کاربر نتونه کانفیگ خراب بسازه.
    cmTransport = 'ws';
    streamSection.style.display = 'none';
    normalNote.style.display = 'flex';
    mtNote.style.display = 'none';
    portField.style.display = 'none';
    if (ssField) ssField.style.display = 'block';
    document.getElementById('cm-head-title').textContent = 'ساخت کانفیگ Shadowsocks';
    document.getElementById('cm-head-sub').textContent = 'رمزنگاری AEAD، پسورد به‌صورت خودکار ساخته می‌شود';
    document.getElementById('cm-submit-text').textContent = 'ساخت کانفیگ';
    document.getElementById('cm-head-icon').innerHTML = '<i class="ti ti-shield-lock-filled"></i>';
  } else {
    streamSection.style.display = '';
    normalNote.style.display = 'flex';
    mtNote.style.display = 'none';
    portField.style.display = 'none';
    if (ssField) ssField.style.display = 'none';
    document.getElementById('cm-head-title').textContent = 'ساخت کانفیگ جدید';
    document.getElementById('cm-head-sub').textContent = 'تنظیمات کامل پروتکل، ترابرد و محدودیت‌ها در یک صفحه';
    document.getElementById('cm-submit-text').textContent = 'ساخت کانفیگ';
    document.getElementById('cm-head-icon').innerHTML = '<i class="ti ti-square-rounded-plus"></i>';
  }
  cmApplyProto();
}
function cmSelectTransport(val, el){
  cmTransport = val;
  document.querySelectorAll('#dd-transport .cm-opt').forEach(o => o.classList.remove('sel'));
  el.classList.add('sel');
  const info = TRANSPORT_INFO[val];
  document.getElementById('dd-transport-icon').innerHTML = `<i class="ti ${info.icon}"></i>`;
  document.getElementById('dd-transport-current').textContent = info.title;
  document.getElementById('dd-transport-current-desc').textContent = info.desc;
  cmToggleDD('dd-transport');
  cmApplyProto();
}
function cmApplyProto(){
  if (cmBase === 'telproxy') {
    document.getElementById('nl-proto').value = 'mtproto';
    return;
  }
  if (cmBase === 'shadowsocks') {
    const val = cmTransport === 'ws' ? 'shadowsocks' : `shadowsocks-${cmTransport}`;
    document.getElementById('nl-proto').value = val;
    return;
  }
  const val = cmTransport === 'ws'
    ? (cmBase === 'trojan' ? 'trojan-ws' : 'vless-ws')
    : (cmBase === 'trojan' ? `trojan-${cmTransport}` : cmTransport);
  document.getElementById('nl-proto').value = val;
}

/* ── سهمیه ترافیک و انقضا: هم با پیل، هم با تایپ مستقیم قابل تنظیم‌اند ── */
function cmQuota(val, unit, el){
  document.getElementById('nl-val').value = val === 0 ? '' : val;
  document.getElementById('nl-unit').value = unit;
  el.parentElement.querySelectorAll('.cm-pill').forEach(c => c.classList.remove('active'));
  el.classList.add('active');
}
function cmExpiry(days, el){
  document.getElementById('nl-exp').value = days === 0 ? '' : days;
  el.parentElement.querySelectorAll('.cm-pill').forEach(c => c.classList.remove('active'));
  el.classList.add('active');
}

function cmSetSni(domain, el){
  document.getElementById('nl-mtproto-domain').value = domain;
  el.parentElement.querySelectorAll('.cm-pill').forEach(c => c.classList.remove('active'));
  el.classList.add('active');
}
function cmClearSniPills(){
  const wrap = document.getElementById('nl-mtproto-domain').closest('.cm-section').querySelector('.cm-pills');
  wrap?.querySelectorAll('.cm-pill').forEach(c => c.classList.remove('active'));
}

/* ── ALPN: چندانتخابی ── */
let cmAlpn = ['h2', 'http/1.1'];
function cmToggleAlpn(val, el){
  const idx = cmAlpn.indexOf(val);
  if(idx > -1){
    if(cmAlpn.length === 1) return; // حداقل یک ALPN باید بمونه
    cmAlpn.splice(idx, 1);
    el.classList.remove('active');
  } else {
    cmAlpn.push(val);
    el.classList.add('active');
  }
  document.getElementById('nl-alpn').value = cmAlpn.join(',');
}


function cmSetSsCipher(val, el){
  document.getElementById('nl-ss-cipher').value = val;
  el.parentElement.querySelectorAll('.cm-pill').forEach(c => c.classList.remove('active'));
  el.classList.add('active');
}

function cmSetFp(val, el){
  document.getElementById('nl-fp').value = val;
  document.querySelectorAll('#fp-pills .fp-card').forEach(c => c.classList.remove('active'));
  el.classList.add('active');
}
document.getElementById('nl-val')?.addEventListener('input', () => {
  document.querySelectorAll('#nl-val').forEach(()=>{});
  const wrap = document.getElementById('nl-val').closest('.cm-field').querySelector('.cm-pills');
  wrap?.querySelectorAll('.cm-pill').forEach(c => c.classList.remove('active'));
});
document.getElementById('nl-exp')?.addEventListener('input', () => {
  const wrap = document.getElementById('nl-exp').closest('.cm-field').querySelector('.cm-pills');
  wrap?.querySelectorAll('.cm-pill').forEach(c => c.classList.remove('active'));
});

function onNlTargetChange(){
  const targetEl=document.getElementById('nl-target');
  const nodeId=targetEl?targetEl.value:'';
  const nlSub=document.getElementById('nl-sub');
  if(nodeId){
    const node=onlineNodesList.find(n=>n.node_id===nodeId);
    const subs=(node&&node.subs)||[];
    nlSub.innerHTML='<option value="">— بدون گروه —</option>'+subs.map(s=>`<option value="${esc(s.sub_id)}">${esc(s.name)}</option>`).join('');
  }else{
    nlSub.innerHTML='<option value="">— بدون گروه —</option>'+allSubsList.map(s=>`<option value="${esc(s.sub_id)}">${esc(s.name)}</option>`).join('');
  }
  document.getElementById('nl-sub-wrap').style.display='';
}
async function createLink(){
  const label=document.getElementById('nl-label').value.trim()||'کانفیگ جدید';
  const val=document.getElementById('nl-val').value;
  const unit=document.getElementById('nl-unit').value;
  const exp=document.getElementById('nl-exp').value;
  const note=document.getElementById('nl-note').value.trim();
  const targetEl=document.getElementById('nl-target');
  const nodeId=targetEl?targetEl.value:'';
  const sub_id=document.getElementById('nl-sub').value||null;
  const protocol=document.getElementById('nl-proto').value||'vless-ws';
  const isMt = protocol === 'mtproto';
  const isSs = protocol.startsWith('shadowsocks');
  const mtproto_port = isMt ? (document.getElementById('nl-mtproto-port').value || null) : null;
  const mtproto_domain = isMt ? (document.getElementById('nl-mtproto-domain').value.trim() || null) : null;
  const mtproto_public_host = isMt ? (document.getElementById('nl-mtproto-public-host').value.trim() || null) : null;
  const mtproto_public_port = isMt ? (document.getElementById('nl-mtproto-public-port').value || null) : null;
  const alpn = (isMt || isSs) ? null : (document.getElementById('nl-alpn').value || 'h2,http/1.1');
  const fingerprint = (isMt || isSs) ? null : (document.getElementById('nl-fp').value || 'chrome');
  const ss_cipher = isSs ? (document.getElementById('nl-ss-cipher').value || 'chacha20-ietf-poly1305') : null;
  try{
    const url = nodeId ? ('/api/nodes/'+nodeId+'/links') : '/api/links';
    const r=await authF(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({label,limit_value:val||0,limit_unit:unit,expires_days:exp||0,note,sub_id,protocol,mtproto_port,mtproto_domain,mtproto_public_host,mtproto_public_port,alpn,fingerprint,ss_cipher})});
    if(!r.ok){
      const d=await r.json().catch(()=>({}));
      throw new Error(d.detail||'failed');
    }
    ['nl-label','nl-val','nl-exp','nl-note','nl-mtproto-port','nl-mtproto-domain','nl-mtproto-public-host','nl-mtproto-public-port'].forEach(id=>document.getElementById(id).value='');
    toast(isMt ? 'پروکسی ساخته شد ✓' : (nodeId?'کانفیگ روی نود ساخته شد ✓':'کانفیگ ساخته شد ✓'),'ok');
    loadLinks();
  }catch(e){toast('✗ '+(e.message||'خطا (شاید کلید این نود اجازه‌ی ساخت از راه دور ندارد)'),'err')}
}


function openEditLink(uuid,nodeId){
  const l=allLinksList.find(x=>x.uuid===uuid&&(nodeId?x._nodeId===nodeId:!x._nodeId));
  if(!l)return;
  document.getElementById('el-uuid').value=uuid;
  document.getElementById('el-node-id').value=nodeId||'';
  const notice=document.getElementById('el-node-notice');
  if(nodeId){ notice.style.display=''; notice.innerHTML=`<span class="node-origin"><i class="ti ti-topology-star-3"></i> ویرایش از راه دور روی نود: ${esc(l._nodeName)}</span>`; }
  else notice.style.display='none';
  document.getElementById('el-label').value=l.label;
  document.getElementById('el-note').value=l.note||'';
  if(l.limit_bytes===0){document.getElementById('el-val').value='';document.getElementById('el-unit').value='GB';}
  else{document.getElementById('el-val').value=(l.limit_bytes/1024/1024).toFixed(0);document.getElementById('el-unit').value='MB';}
  document.getElementById('el-exp').value='';
  openModal('modal-edit-link');
}
async function saveEditLink(){
  const uuid=document.getElementById('el-uuid').value;
  const nodeId=document.getElementById('el-node-id').value||null;
  const label=document.getElementById('el-label').value.trim();
  const note=document.getElementById('el-note').value.trim();
  const val=document.getElementById('el-val').value;
  const unit=document.getElementById('el-unit').value;
  const exp=document.getElementById('el-exp').value;
  const body={label,note,limit_value:val||0,limit_unit:unit};
  if(exp&&Number(exp)>0)body.expires_days=Number(exp);
  try{
    const r=await authF(linkApiBase(nodeId)+uuid,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    if(!r.ok)throw new Error((await r.json().catch(()=>({}))).detail||'');
    closeModal('modal-edit-link');
    toast('کانفیگ ویرایش شد ✓','ok');loadLinks();
  }catch(e){toast(e.message||'خطا در ویرایش (شاید کلید این نود اجازه‌ی ویرایش از راه دور ندارد)','err')}
}
function linkApiBase(nodeId){ return nodeId? ('/api/nodes/'+nodeId+'/links/') : '/api/links/'; }
async function toggleActive(uuid,newState,nodeId){
  try{const r=await authF(linkApiBase(nodeId)+uuid,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({active:newState})});if(!r.ok)throw new Error((await r.json().catch(()=>({}))).detail||'');toast(newState?'فعال شد ✓':'غیرفعال شد','ok');loadLinks();}catch(e){toast(e.message||'خطا (شاید کلید این نود اجازه‌ی ویرایش ندارد)','err')}
}
async function resetUsage(uuid,nodeId){
  try{const r=await authF(linkApiBase(nodeId)+uuid,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({reset_usage:true})});if(!r.ok)throw new Error((await r.json().catch(()=>({}))).detail||'');toast('مصرف ریست شد ✓','ok');loadLinks();}catch(e){toast(e.message||'خطا (شاید کلید این نود اجازه‌ی ویرایش از راه دور ندارد)','err')}
}
let atCurrentUuid = null;

function openAdTagModal(uuid, label, currentTag){
  atCurrentUuid = uuid;
  document.getElementById('at-cfg-name').textContent = label;
  document.getElementById('at-tag').value = currentTag || '';
  openModal('modal-ad-tag');
  setTimeout(()=>document.getElementById('at-tag').focus(), 150);
}

function mtPlainSecret(fullSecret){
  if (!fullSecret) return '';
  // فرمت mtg: "ee" + 32 کاراکتر هگز سکرت + دامنه‌ی fake-TLS به‌صورت هگز
  if (fullSecret.startsWith('ee') && fullSecret.length > 34) {
    return fullSecret.slice(2, 34);
  }
  return fullSecret;
}

function openMtInfoModal(label, secret, fullLink, hasPublicHost){
  document.getElementById('mti-cfg-name').textContent = label;
  document.getElementById('mti-secret').textContent = mtPlainSecret(secret) || '—';
  document.getElementById('mti-link').textContent = fullLink || '—';
  const warnEl = document.getElementById('mti-warn');
  if (warnEl) warnEl.style.display = hasPublicHost ? 'none' : 'flex';
  openModal('modal-mt-info');
}

function cpMtiField(id, msg){
  const el = document.getElementById(id);
  navigator.clipboard.writeText(el.textContent).then(()=>toast(msg,'ok'));
}

async function submitAdTag(){
  if(!atCurrentUuid) return;
  const tag = document.getElementById('at-tag').value.trim();
  if(!tag){ toast('ad_tag نمی‌تواند خالی باشد','err'); return; }

  const btn = document.getElementById('at-submit-btn');
  btn.disabled = true;
  btn.innerHTML = '<i class="ti ti-loader-2" style="animation:spin 1s linear infinite"></i> در حال اعمال...';

  try{
    const r = await authF('/api/links/'+atCurrentUuid+'/ad-tag', {
      method:'PATCH', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ad_tag: tag})
    });
    if(!r.ok){ const d = await r.json().catch(()=>({})); throw new Error(d.detail || 'خطا'); }
    closeModal('modal-ad-tag');
    toast('تبلیغ ثبت شد، پروکسی در حال ری‌استارت است...','ok');
    setTimeout(loadLinks, 2000);
  }catch(e){
    toast('✗ '+e.message,'err');
  }
  btn.disabled = false;
  btn.innerHTML = '<i class="ti ti-check"></i> ذخیره و اعمال';
}
async function deleteLink(uuid,nodeId){
  if(!confirm('حذف این کانفیگ؟'))return;
  try{const r=await authF(linkApiBase(nodeId)+uuid,{method:'DELETE'});if(!r.ok)throw new Error((await r.json().catch(()=>({}))).detail||'');toast('حذف شد ✓','ok');loadLinks();}catch(e){toast(e.message||'خطا (شاید کلید این نود اجازه‌ی حذف ندارد)','err')}
}
function showQR(link){window.open('https://api.qrserver.com/v1/create-qr-code/?size=300x300&data='+encodeURIComponent(link),'_blank')}
let allSubsRaw=[];
async function loadSubs(){
  try{
    const [sr,nr]=await Promise.all([authF('/api/subs'),authF('/api/nodes/aggregate').catch(()=>null)]);
    const d=await sr.json();
    const subs=d.subs||[];
    let nodeSubs=[];
    if(nr && nr.ok){
      try{
        const nd=await nr.json();
        (nd.nodes||[]).forEach(n=>{
          if(n.disabled||!n.online) return;
          (n.subs||[]).forEach(s=>nodeSubs.push({...s,_nodeId:n.node_id,_nodeName:n.label||'نود'}));
        });
      }catch(e){}
    }
    const all=[...subs,...nodeSubs];
    allSubsRaw=all;
    document.getElementById('subs-nb').textContent=all.length;
    document.getElementById('subs-pg-cnt').textContent=toFa(all.length)+' گروه';
    renderSubsGrid(all);
  }catch(e){console.error(e)}
}
function renderSubsGrid(subs){
  const grid=document.getElementById('subs-grid');
  if(!subs.length){
    grid.innerHTML='<div class="subs-empty-v2"><div class="subs-empty-v2-icon"><i class="ti ti-folders"></i></div><div class="subs-empty-v2-title">هنوز گروهی وجود ندارد</div><div class="subs-empty-v2-sub">یک گروه جدید بسازید تا کانفیگ‌ها را دسته‌بندی کنید</div></div>';
    return;
  }
  grid.innerHTML=subs.map(s=>{
    const isNode=!!s._nodeId;
    const nodeBadge=isNode?`<span class="sub-card-lock-badge open" style="background:var(--purple-bg,rgba(139,92,246,.14));color:var(--purple,#8B5CF6)" title="نود: ${esc(s._nodeName)}"><i class="ti ti-topology-star-3"></i></span>`:'';
    return `
    <div class="sub-card">
      <div class="sub-card-top">
        <div class="sub-card-head-v2">
          <div class="sub-card-icon"><i class="ti ti-folder"></i></div>
          <div class="sub-card-titles">
            <div class="sub-card-name-v2">${esc(s.name)}</div>
            ${isNode?`<div class="sub-card-desc-v2" style="color:var(--purple-t,#BCA4F7)"><i class="ti ti-topology-star-3" style="font-size:10px"></i> نود: ${esc(s._nodeName)}</div>`:(s.desc?`<div class="sub-card-desc-v2">${esc(s.desc)}</div>`:'<div class="sub-card-desc-v2" style="opacity:.5">بدون توضیحات</div>')}
          </div>
          ${isNode?nodeBadge:`<div class="sub-card-lock-badge ${s.has_password?'locked':'open'}" title="${s.has_password?'رمزدار':'پابلیک'}">
            <i class="ti ${s.has_password?'ti-lock':'ti-lock-open'}"></i>
          </div>`}
        </div>
        <div class="sub-card-stats">
          <div class="sub-card-stat"><div class="sub-card-stat-val">${toFa(s.links_count)}</div><div class="sub-card-stat-label">کانفیگ</div></div>
          <div class="sub-card-stat"><div class="sub-card-stat-val" style="color:var(--green-t)">${toFa(s.active_count)}</div><div class="sub-card-stat-label">فعال</div></div>
          <div class="sub-card-stat"><div class="sub-card-stat-val" style="font-size:12px">${esc(s.total_used_fmt)}</div><div class="sub-card-stat-label">مصرف</div></div>
        </div>
      </div>
      <div class="sub-card-url-row">
        <span class="sub-card-url-text">${esc(s.public_url)}</span>
        <button class="sub-card-url-copy" onclick="navigator.clipboard.writeText('${esc(s.public_url)}').then(()=>toast('لینک پابلیک کپی شد','ok'))" title="کپی"><i class="ti ti-copy"></i></button>
        <button class="sub-card-url-copy" onclick="window.open('${esc(s.public_url)}','_blank')" title="باز کردن"><i class="ti ti-external-link"></i></button>
      </div>
      <div class="sub-card-bottom">
        <button class="btn btn-sm btn-g" onclick="openSubLinks('${esc(s.sub_id)}','${esc(s.name)}','${esc(s._nodeId||'')}')"><i class="ti ti-link-plus"></i> کانفیگ‌ها</button>
        ${isNode?`<button class="btn btn-sm btn-g btn-icon" onclick="openEditSubModal('${esc(s.sub_id)}','${esc(s._nodeId)}')" title="ویرایش"><i class="ti ti-edit"></i></button>`:''}
        <button class="btn btn-sm btn-o" onclick="navigator.clipboard.writeText('${esc(s.sub_url)}').then(()=>toast('لینک ساب کپی شد','ok'))"><i class="ti ti-rss"></i> ساب</button>
        <button class="btn btn-sm btn-g btn-icon" onclick="showQR('${esc(s.sub_url)}')" title="QR"><i class="ti ti-qrcode"></i></button>
        <button class="btn btn-sm btn-d btn-icon" onclick="deleteSub('${esc(s.sub_id)}','${esc(s._nodeId||'')}')" title="حذف"><i class="ti ti-trash"></i></button>
      </div>
    </div>
  `;}).join('');
}
function filterSubs(q){
  q=q.trim().toLowerCase();
  if(!q){renderSubsGrid(allSubsRaw);return}
  renderSubsGrid(allSubsRaw.filter(s=>s.name.toLowerCase().includes(q)||(s.desc||'').toLowerCase().includes(q)));
}
function openCreateSubModal(){
  const targetEl=document.getElementById('ns-target'), wrap=document.getElementById('ns-target-wrap');
  if(targetEl){
    targetEl.innerHTML='<option value="">این پنل</option>'+onlineNodesList.map(n=>`<option value="${esc(n.node_id)}">${esc(n.label||'نود')}</option>`).join('');
    if(wrap) wrap.style.display = onlineNodesList.length ? '' : 'none';
  }
  openModal('modal-create-sub');
}
async function createSub(){
  const name=document.getElementById('ns-name').value.trim()||'گروه جدید';
  const desc=document.getElementById('ns-desc').value.trim();
  const pw=document.getElementById('ns-pw').value;
  const targetEl=document.getElementById('ns-target');
  const nodeId=targetEl?targetEl.value:'';
  try{
    const url = nodeId ? ('/api/nodes/'+nodeId+'/subs') : '/api/subs';
    const r=await authF(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name,desc,password:pw})});
    if(!r.ok){const d=await r.json().catch(()=>({}));throw new Error(d.detail||'failed')}
    ['ns-name','ns-desc','ns-pw'].forEach(id=>document.getElementById(id).value='');
    closeModal('modal-create-sub');
    toast(nodeId?'گروه روی نود ساخته شد ✓':'گروه ساخته شد ✓','ok');
    loadSubs();
  }catch(e){toast('خطا در ساخت گروه: '+(e.message||''),'err')}
}
async function deleteSub(sub_id,nodeId){
  if(!confirm('حذف این گروه؟ کانفیگ‌ها حذف نمی‌شوند.'))return;
  try{
    const url = nodeId ? ('/api/nodes/'+nodeId+'/subs/'+sub_id) : ('/api/subs/'+sub_id);
    const r=await authF(url,{method:'DELETE'});
    if(!r.ok)throw new Error();
    toast('گروه حذف شد ✓','ok');loadSubs();loadLinks();
    if(document.getElementById('pg-subscriptions')?.classList.contains('on'))loadSubsPage();
  }catch(e){toast('خطا','err')}
}
function openEditSubModal(sub_id,nodeId){
  const s=allSubsRaw.find(x=>x.sub_id===sub_id&&(x._nodeId||'')===(nodeId||''));
  if(!s)return;
  const name=prompt('نام جدید گروه:',s.name);
  if(name===null)return;
  const desc=prompt('توضیحات (اختیاری):',s.desc||'')||'';
  editSubMeta(sub_id,nodeId,name.trim()||s.name,desc.trim());
}
async function editSubMeta(sub_id,nodeId,name,desc){
  try{
    const url = nodeId ? ('/api/nodes/'+nodeId+'/subs/'+sub_id) : ('/api/subs/'+sub_id);
    const r=await authF(url,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({name,desc})});
    if(!r.ok)throw new Error();
    toast('گروه بروزرسانی شد ✓','ok');loadSubs();
  }catch(e){toast('خطا در ویرایش گروه','err')}
}
let lmodalLinks=[],lmodalNodeLinks=[],lmodalInSub=new Set(),currentSubNodeId='';
async function openSubLinks(sub_id,name,nodeId){
  currentSubId=sub_id;
  currentSubNodeId=nodeId||'';
  document.getElementById('modal-sub-name').textContent=name+(currentSubNodeId?' (نود)':'');
  document.getElementById('modal-links-body').innerHTML='<div style="color:var(--t3);font-size:12px;padding:20px;text-align:center"><i class="ti ti-loader-2" style="animation:spin 1s linear infinite;font-size:20px"></i></div>';
  document.getElementById('lmodal-search-inp').value='';
  openModal('modal-links');
  if(currentSubNodeId){
    // گروهِ متعلق به یک نود: کانفیگ‌های خودِ آن نود + همه‌ی کانفیگ‌های پنل مرکزی و سایر نودها هم قابل افزودن‌اند
    try{
      const [lr,nr]=await Promise.all([authF('/api/links'),authF('/api/nodes/aggregate')]);
      const {links: centralLinks=[]}=await lr.json();
      const nd=await nr.json();
      const targetNode=(nd.nodes||[]).find(n=>n.node_id===currentSubNodeId);
      const thisSub=(targetNode&&targetNode.subs||[]).find(s=>s.sub_id===sub_id);
      const ownKeys=(thisSub?.link_ids||[]).map(u=>currentSubNodeId+'::'+u);
      const foreignKeys=(thisSub?.foreign_links||[]).map(fl=>fl.key).filter(Boolean);
      lmodalInSub=new Set([...ownKeys,...foreignKeys]);
      lmodalLinks=[];
      lmodalNodeLinks=[
        ...centralLinks.map(l=>({...l,node_id:'local',node_label:'این پنل'})),
        ...(nd.nodes||[]).filter(n=>!n.disabled&&n.online).flatMap(n=>(n.links||[]).map(l=>({...l,node_id:n.node_id,node_label:(n.node_id===currentSubNodeId?'این نود · ':'')+(n.label||'نود')})))
      ];
      renderLmodalList();
    }catch(e){toast('خطا در بارگذاری','err')}
    return;
  }
  try{
    const [lr,sr,nr]=await Promise.all([authF('/api/links'),authF('/api/subs'),authF('/api/nodes/aggregate').catch(()=>null)]);
    const {links=[]}=await lr.json();
    const {subs=[]}=await sr.json();
    const thisSub=subs.find(s=>s.sub_id===sub_id);
    lmodalInSub=new Set([...(thisSub?.link_ids||[]),...(thisSub?.node_link_ids||[])]);
    lmodalLinks=links;
    lmodalNodeLinks=[];
    if(nr){
      const nd=await nr.json().catch(()=>null);
      (nd?.nodes||[]).forEach(n=>{
        if(!n.online||!(n.links||[]).length)return;
        n.links.forEach(l=>lmodalNodeLinks.push({...l,node_id:n.node_id,node_label:n.label}));
      });
    }
    renderLmodalList();
  }catch(e){toast('خطا در بارگذاری','err')}
}
function renderLmodalList(){
  const body=document.getElementById('modal-links-body');
  const localItems=lmodalLinks.map(l=>({key:l.uuid,label:l.label,protocol:l.protocol,used_bytes:l.used_bytes,active:l.active,expired:l.expired,nodeLabel:null}));
  const nodeItems=lmodalNodeLinks.map(l=>({key:l.node_id+'::'+l.uuid,label:l.label,protocol:l.protocol,used_bytes:l.used_bytes,active:l.active,expired:l.expired,nodeLabel:l.node_label}));
  const all=[...localItems,...nodeItems];
  if(!all.length){body.innerHTML='<div class="empty" style="padding:30px"><i class="ti ti-link-off"></i><p>هنوز کانفیگی وجود ندارد</p></div>';updateLmodalCount();return}
  const protoIcon=p=>p==='mtproto'?'ti-brand-telegram':p&&p.startsWith('shadowsocks')?'ti-shield-lock-filled':p&&p.startsWith('trojan')?'ti-shield-lock':p&&p.includes('xhttp')?'ti-bolt':'ti-link';
  body.innerHTML=all.map(l=>{
    const checked=lmodalInSub.has(l.key);
    const on=l.active&&!l.expired;
    const nodeBadge=l.nodeLabel?`<span class="lrow-v2-status" style="background:var(--purple-bg,rgba(139,92,246,.14));color:var(--purple,#8B5CF6);margin-left:4px"><i class="ti ti-topology-star-3" style="font-size:9px"></i> ${esc(l.nodeLabel)}</span>`:'';
    return `<div class="lrow-v2 ${checked?'checked':''}" data-key="${esc(l.key)}" data-name="${esc(l.label).toLowerCase()}" onclick="toggleLrow('${esc(l.key)}',this)">
      <div class="lrow-v2-check"><i class="ti ti-check"></i></div>
      <div class="lrow-v2-avatar"><i class="ti ${protoIcon(l.protocol)}"></i></div>
      <div class="lrow-v2-info">
        <div class="lrow-v2-name">${esc(l.label)}</div>
        <div class="lrow-v2-meta"><i class="ti ti-database" style="font-size:10px"></i> ${fmtB(l.used_bytes)}</div>
      </div>
      ${nodeBadge}
      <span class="lrow-v2-status ${on?'on':'off'}">${on?'فعال':'غیرفعال'}</span>
    </div>`;
  }).join('');
  updateLmodalCount();
}
function toggleLrow(key,el){
  if(lmodalInSub.has(key)){lmodalInSub.delete(key);el.classList.remove('checked')}
  else{lmodalInSub.add(key);el.classList.add('checked')}
  updateLmodalCount();
}
function lmodalSelectAll(state){
  lmodalLinks.forEach(l=>{if(state)lmodalInSub.add(l.uuid);else lmodalInSub.delete(l.uuid)});
  lmodalNodeLinks.forEach(l=>{const k=l.node_id+'::'+l.uuid;if(state)lmodalInSub.add(k);else lmodalInSub.delete(k)});
  renderLmodalList();
}
function updateLmodalCount(){
  const el=document.getElementById('lmodal-count');
  if(el)el.textContent=toFa(lmodalInSub.size)+' انتخاب شده';
}
function filterLmodal(q){
  q=q.trim().toLowerCase();
  document.querySelectorAll('#modal-links-body .lrow-v2').forEach(row=>{
    row.style.display = !q || row.dataset.name.includes(q) ? '' : 'none';
  });
}
async function saveSubLinks(){
  if(!currentSubId)return;
  if(currentSubNodeId){
    const selected=[...lmodalInSub];
    const own=[], foreign=[];
    selected.forEach(key=>{
      const idx=key.indexOf('::');
      if(idx<0)return;
      const nid=key.slice(0,idx), uid=key.slice(idx+2);
      if(nid===currentSubNodeId){ own.push(uid); return; }
      const item=lmodalNodeLinks.find(l=>l.node_id===nid&&l.uuid===uid);
      if(!item||!item.vless_link)return;
      foreign.push({key,label:item.label,vless_link:item.vless_link,used_bytes:item.used_bytes||0,source:item.node_label||''});
    });
    try{
      const r=await authF('/api/nodes/'+currentSubNodeId+'/subs/'+currentSubId,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({link_ids:own,foreign_links:foreign})});
      if(!r.ok)throw new Error();
      closeModal('modal-links');
      toast('کانفیگ‌های گروه ذخیره شدند ✓','ok');
      loadSubs();loadLinks();
    }catch(e){toast('خطا در ذخیره','err')}
    return;
  }
  const allKeys=[...lmodalInSub];
  const link_ids=allKeys.filter(k=>!k.includes('::'));
  const node_link_ids=allKeys.filter(k=>k.includes('::'));
  try{
    const r=await authF('/api/subs/'+currentSubId,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({link_ids,node_link_ids})});
    if(!r.ok)throw new Error();
    await Promise.all(lmodalLinks.map(l=>
      authF('/api/links/'+l.uuid,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({sub_id:lmodalInSub.has(l.uuid)?currentSubId:null})})
    ));
    closeModal('modal-links');
    toast('کانفیگ‌های گروه ذخیره شدند ✓','ok');
    loadSubs();loadLinks();
  }catch(e){toast('خطا در ذخیره','err')}
}
async function loadSubsPage(){
  document.getElementById('sub-all-url').textContent=location.protocol+'//'+location.host+'/sub-all';
  try{
    const [sr,nr]=await Promise.all([authF('/api/subs'),authF('/api/nodes/aggregate').catch(()=>null)]);
    const d=await sr.json();
    const subs=d.subs||[];
    let nodeSubs=[];
    if(nr && nr.ok){
      try{
        const nd=await nr.json();
        (nd.nodes||[]).forEach(n=>{
          if(n.disabled||!n.online) return;
          (n.subs||[]).forEach(s=>nodeSubs.push({...s,_nodeId:n.node_id,_nodeName:n.label||'نود'}));
        });
      }catch(e){}
    }
    const all=[...subs,...nodeSubs];
    const el=document.getElementById('sub-groups-list');
    if(!all.length){el.innerHTML='<div class="empty"><i class="ti ti-rss-off"></i><p>هنوز گروهی ندارید</p></div>';return}
    el.innerHTML=all.map(s=>{
      const isNode=!!s._nodeId;
      const nodeTag=isNode?` <span style="color:var(--purple-t,#BCA4F7)"><i class="ti ti-topology-star-3" style="font-size:10px"></i> نود: ${esc(s._nodeName)}</span>`:'';
      return `
      <div style="padding:13px 15px;background:var(--accent-d);border:1px solid var(--card-b);border-radius:10px;margin-bottom:8px;display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap">
        <div>
          <div style="font-weight:700;font-size:13px;margin-bottom:3px">${esc(s.name)}${nodeTag}</div>
          <div style="font-family:ui-monospace,monospace;font-size:10px;color:#A78BFA">${esc(s.sub_url)}</div>
          <div style="font-size:10px;color:var(--t3);margin-top:3px">${toFa(s.links_count)} کانفیگ · ${esc(s.total_used_fmt)} مصرف ${s.has_password?'· 🔒 رمزدار':''}</div>
        </div>
        <div style="display:flex;gap:5px;flex-wrap:wrap">
          <button class="btn btn-sm btn-pur" onclick="navigator.clipboard.writeText('${esc(s.sub_url)}').then(()=>toast('کپی شد','ok'))"><i class="ti ti-copy"></i> ساب</button>
          <button class="btn btn-sm btn-pur" onclick="navigator.clipboard.writeText('${esc(s.public_url)}').then(()=>toast('کپی شد','ok'))"><i class="ti ti-globe"></i> پابلیک</button>
          <button class="btn btn-sm btn-g" onclick="showQR('${esc(s.sub_url)}')"><i class="ti ti-qrcode"></i></button>
          <button class="btn btn-sm btn-d btn-icon" onclick="deleteSub('${esc(s.sub_id)}','${esc(s._nodeId||'')}')" title="حذف"><i class="ti ti-trash"></i></button>
        </div>
      </div>
    `;}).join('');
  }catch(e){}
}
function cpSubAll(){navigator.clipboard.writeText(location.protocol+'//'+location.host+'/sub-all').then(()=>toast('کپی شد ✓','ok'))}
function parseBytesFmt(s){
  if(!s)return 0;
  const m=String(s).match(/([\d.]+)\s*([A-Za-z]+)/);
  if(!m)return 0;
  const n=parseFloat(m[1]),u=m[2].toUpperCase();
  const mult={B:1,KB:1024,MB:1024**2,GB:1024**3,TB:1024**4};
  return n*(mult[u]||1);
}
async function loadConns(){
  try{
    const r=await authF('/api/connections'),d=await r.json();
    const grid=document.getElementById('conns-grid'),ce=document.getElementById('conns-empty');
    document.getElementById('conns-live').innerHTML='<span class="dot dg pulse"></span> '+d.count+' اتصال';
    document.getElementById('ch-count').textContent=toFa(d.count);
    const conns=d.connections||[];
    if(!d.count){
      grid.innerHTML='';ce.style.display='block';
      document.getElementById('ch-traffic').textContent='—';
      document.getElementById('ch-avgdur').textContent='—';
      document.getElementById('ch-uniq').textContent='—';
      return;
    }
    ce.style.display='none';
    const totalBytes=conns.reduce((s,c)=>s+parseBytesFmt(c.bytes_fmt),0);
    document.getElementById('ch-traffic').textContent=fmtB(totalBytes);
    const uniqIps=new Set(conns.map(c=>c.ip)).size;
    document.getElementById('ch-uniq').textContent=toFa(uniqIps);
    const durs=conns.map(c=>c.connected_at?Math.max(0,Math.floor((Date.now()-new Date(c.connected_at).getTime())/1000)):0);
    const avgSec=durs.length?Math.floor(durs.reduce((a,b)=>a+b,0)/durs.length):0;
    document.getElementById('ch-avgdur').textContent=avgSec<60?avgSec+' ث':avgSec<3600?Math.floor(avgSec/60)+' د':Math.floor(avgSec/3600)+' س';
    const maxDur=Math.max(...durs,1);
    grid.innerHTML=conns.map(c=>{
      const secs=c.connected_at?Math.max(0,Math.floor((Date.now()-new Date(c.connected_at).getTime())/1000)):0;
      const dur=secs<60?secs+' ثانیه':secs<3600?Math.floor(secs/60)+' دقیقه':Math.floor(secs/3600)+' ساعت';
      const durPct=Math.min(100,Math.round((secs/maxDur)*100));
      const protoVal=c.transport==='vless-ws'?'vless-ws':(c.transport||'').replace('xhttp-','xhttp-');
      return `<div class="conn-card-v2">
        <div class="conn-card-v2-glow"></div>
        <div class="conn-card-v2-top">
          <div class="conn-avatar"><i class="ti ti-device-desktop"></i></div>
          <div class="conn-card-v2-id">
            <div class="conn-ip-v2">${esc(c.ip)}
              <button class="conn-ip-copy" onclick="navigator.clipboard.writeText('${esc(c.ip)}').then(()=>toast('IP کپی شد','ok'))" title="کپی IP"><i class="ti ti-copy"></i></button>
            </div>
            <div class="conn-label-v2">${esc(c.label)}</div>
          </div>
          <span class="conn-status-pill"><span class="dot dg pulse"></span> زنده</span>
        </div>
        <div class="conn-card-v2-divider"></div>
        <div class="conn-card-v2-body">
          <div class="conn-proto-row">${protoBadge(protoVal)}</div>
          <div class="conn-stat-row">
            <div class="conn-stat-box">
              <div class="conn-stat-icon"><i class="ti ti-transfer"></i></div>
              <div>
                <div class="conn-stat-text-label">ترافیک</div>
                <div class="conn-stat-text-val">${esc(c.bytes_fmt)}</div>
              </div>
            </div>
            <div class="conn-stat-box">
              <div class="conn-stat-icon time"><i class="ti ti-clock"></i></div>
              <div>
                <div class="conn-stat-text-label">مدت اتصال</div>
                <div class="conn-stat-text-val">${dur}</div>
              </div>
            </div>
          </div>
          <div class="conn-duration-track"><div class="conn-duration-fill" style="width:${durPct}%"></div></div>
        </div>
      </div>`;
    }).join('');
  }catch(e){console.error(e)}
}
async function loadErrs(){try{const r=await authF('/stats'),d=await r.json();renderErrs(d.recent_errors||[]);}catch(e){}}
async function fetchDefaultVless(){
  try{const r=await authF('/api/links'),d=await r.json();const links=d.links||[];const def=links.find(l=>l.limit_bytes===0&&l.active&&!l.expired)||links.find(l=>l.active&&!l.expired)||links[0];document.getElementById('vless-main').textContent=def?def.vless_link:'هنوز کانفیگی وجود ندارد';}catch(e){}
}
function cpText(id){navigator.clipboard.writeText(document.getElementById(id).textContent).then(()=>toast('کپی شد ✓','ok'))}
function qrFor(id){showQR(document.getElementById(id).textContent)}
function refreshAll(){fetchStats();fetchDefaultVless();loadLinks();if(document.getElementById('pg-subgroups').classList.contains('on'))loadSubs();if(document.getElementById('pg-subscriptions').classList.contains('on'))loadSubsPage();if(document.getElementById('pg-connections').classList.contains('on'))loadConns();if(document.getElementById('pg-logs').classList.contains('on'))loadActivity();toast('رفرش شد','ok')}
async function changePw(){
  const cur=document.getElementById('cp-cur').value,nw=document.getElementById('cp-new').value,cf=document.getElementById('cp-cf').value;
  if(!cur||!nw||!cf){toast('همه فیلدها را پر کنید','err');return}
  if(nw.length<4){toast('حداقل ۴ کاراکتر','err');return}
  if(nw!==cf){toast('تکرار رمز اشتباه','err');return}
  try{
    const r=await authF('/api/change-password',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({current_password:cur,new_password:nw})});
    const d=await r.json().catch(()=>({}));
    if(!r.ok)throw new Error(d.detail||'خطا');
    toast('رمز تغییر کرد ✓','ok');
    ['cp-cur','cp-new','cp-cf'].forEach(id=>document.getElementById(id).value='');
  }catch(e){toast('✗ '+e.message,'err')}
}
function togglePwField(id,btn){
  const inp=document.getElementById(id);
  const icon=btn.querySelector('i');
  const toText=inp.type==='password';
  inp.type=toText?'text':'password';
  icon.className='ti '+(toText?'ti-eye-off':'ti-eye');
}
function checkPwStrength(val){
  const segs=document.querySelectorAll('#pw-strength-bar .pw-strength-seg');
  const label=document.getElementById('pw-strength-label');
  const reqLen=document.getElementById('req-len'),reqNum=document.getElementById('req-num'),reqCase=document.getElementById('req-case');
  const hasLen=val.length>=4,hasNum=/\d/.test(val),hasCase=/[a-z]/.test(val)&&/[A-Z]/.test(val),hasLong=val.length>=8;
  reqLen.classList.toggle('met',hasLen);
  reqNum.classList.toggle('met',hasNum);
  reqCase.classList.toggle('met',hasCase);
  let score=0;if(hasLen)score++;if(hasNum)score++;if(hasCase)score++;if(hasLong)score++;
  const colors=['#EF4444','#F59E0B','#3B82F6','#10B981'],labels=['خیلی ضعیف','ضعیف','متوسط','قوی'];
  segs.forEach((s,i)=>{s.style.background=i<score?colors[Math.max(0,score-1)]:'rgba(100,116,139,.2)'});
  if(val.length===0){label.innerHTML='<i class="ti ti-shield"></i> قدرت رمز';return}
  label.innerHTML=`<i class="ti ti-shield-check" style="color:${colors[Math.max(0,score-1)]}"></i> ${labels[Math.max(0,score-1)]}`;
}
function makeGradient(ctx,color1,color2){
  const g=ctx.createLinearGradient(0,0,0,260);
  g.addColorStop(0,color1);g.addColorStop(1,color2);
  return g;
}
function initCharts(){
  const c1=document.getElementById('ch1').getContext('2d');
  const grad1=makeGradient(c1,'rgba(59,130,246,.38)','rgba(59,130,246,0)');
  const opts={
    responsive:true,maintainAspectRatio:false,
    interaction:{mode:'index',intersect:false},
    plugins:{
      legend:{display:false},
      tooltip:{
        backgroundColor:'rgba(13,27,46,.96)',borderColor:'rgba(59,130,246,.3)',borderWidth:1,
        titleColor:'#E8F4FF',bodyColor:'#7BAED4',padding:11,cornerRadius:10,displayColors:false,
        titleFont:{family:'Vazirmatn',size:11,weight:'700'},bodyFont:{family:'Vazirmatn',size:11},
        callbacks:{label:v=>`${v.parsed.y.toFixed(2)} مگابایت`}
      }
    },
    scales:{
      x:{grid:{display:false},border:{display:false},ticks:{color:'#3D6B8E',font:{size:9,family:'Vazirmatn'}}},
      y:{grid:{color:'rgba(59,130,246,.06)'},border:{display:false},ticks:{color:'#3D6B8E',font:{size:9,family:'Vazirmatn'},callback:v=>v+' MB'}}
    },
    elements:{line:{capBezierPoints:true}}
  };
  const ds1={label:'MB',data:[],borderColor:'#3B82F6',backgroundColor:grad1,fill:true,tension:.42,pointRadius:0,pointHoverRadius:6,pointHoverBackgroundColor:'#3B82F6',pointHoverBorderColor:'#fff',pointHoverBorderWidth:2,borderWidth:2.5};
  ch1=new Chart(document.getElementById('ch1'),{type:'line',data:{labels:[],datasets:[ds1]},options:opts});

  function makeGradientV2(ctx,c1,c2,c3){
    const g=ctx.createLinearGradient(0,0,0,320);
    g.addColorStop(0,c1);g.addColorStop(.6,c2);g.addColorStop(1,c3);
    return g;
  }
  const c3ctx=document.getElementById('ch3').getContext('2d');
  const gradFill3=makeGradientV2(c3ctx,'rgba(59,130,246,.45)','rgba(59,130,246,.08)','rgba(59,130,246,0)');
  ch3=new Chart(document.getElementById('ch3'),{
    type:'line',
    data:{labels:[],datasets:[
      {label:'مصرف',data:[],borderColor:'#3B82F6',backgroundColor:gradFill3,fill:true,tension:.45,pointRadius:0,pointHoverRadius:7,pointHoverBackgroundColor:'#fff',pointHoverBorderColor:'#3B82F6',pointHoverBorderWidth:3,borderWidth:3,order:2},
      {label:'میانگین',data:[],borderColor:'#F59E0B',borderDash:[6,5],borderWidth:1.6,pointRadius:0,fill:false,tension:0,order:1}
    ]},
    options:{
      responsive:true,maintainAspectRatio:false,
      interaction:{mode:'index',intersect:false},
      plugins:{
        legend:{display:false},
        tooltip:{
          backgroundColor:'rgba(13,27,46,.97)',borderColor:'rgba(59,130,246,.35)',borderWidth:1,
          titleColor:'#E8F4FF',bodyColor:'#9DC3E8',padding:13,cornerRadius:12,displayColors:true,boxPadding:4,
          titleFont:{family:'Vazirmatn',size:11.5,weight:'700'},bodyFont:{family:'Vazirmatn',size:11},
          callbacks:{label:v=>` ${v.dataset.label}: ${v.parsed.y.toFixed(2)} MB`}
        }
      },
      scales:{
        x:{grid:{display:false},border:{display:false},ticks:{color:'#3D6B8E',font:{size:9.5,family:'Vazirmatn'},maxRotation:0}},
        y:{grid:{color:'rgba(59,130,246,.05)'},border:{display:false},ticks:{color:'#3D6B8E',font:{size:9.5,family:'Vazirmatn'},callback:v=>v+' MB'}}
      }
    }
  });

  ch2=new Chart(document.getElementById('ch2'),{
    type:'doughnut',
    data:{labels:['VLESS/WS','XHTTP Ultra','HTTP Proxy'],datasets:[{
      data:[55,35,10],
      backgroundColor:['#3B82F6','#10B981','#8B5CF6'],
      borderColor:getComputedStyle(document.documentElement).getPropertyValue('--card')||'#0d1b2e',
      borderWidth:4,hoverOffset:10,borderRadius:6,spacing:3
    }]},
    options:{
      responsive:true,maintainAspectRatio:false,cutout:'72%',
      plugins:{
        legend:{position:'bottom',labels:{color:'var(--t2)',font:{size:10,family:'Vazirmatn'},padding:12,usePointStyle:true,pointStyle:'circle'}},
        tooltip:{backgroundColor:'rgba(13,27,46,.96)',borderColor:'rgba(59,130,246,.3)',borderWidth:1,padding:10,cornerRadius:10,bodyFont:{family:'Vazirmatn'},titleFont:{family:'Vazirmatn'}}
      }
    }
  });
}
let ws;
function wsLog(c,m){const l=document.getElementById('ws-log'),p=document.createElement('p');const colors={ok:'#34D399',err:'#F87171',info:'#7BAED4',sent:'#FCD34D'};p.style.color=colors[c]||'#fff';p.textContent='['+new Date().toLocaleTimeString('fa-IR')+'] '+m;l.appendChild(p);l.scrollTop=l.scrollHeight}
function wsConn(){const u=document.getElementById('ws-uuid').value.trim();if(!u){toast('UUID را وارد کنید','err');return}const url=(location.protocol==='https:'?'wss':'ws')+'://'+location.host+'/ws/'+u;wsLog('info','اتصال: '+url);ws=new WebSocket(url);ws.onopen=()=>wsLog('ok','✓ متصل - UUID معتبر');ws.onerror=()=>wsLog('err','✗ خطا - UUID نامعتبر یا غیرفعال');ws.onmessage=m=>wsLog('info','دریافت '+(m.data.size||m.data.length)+' byte');ws.onclose=e=>wsLog('err','قطع ('+e.code+')'+(e.code===1008?' - دسترسی رد شد':''))}
function wsSend(){const m=document.getElementById('ws-msg').value;if(!m||!ws||ws.readyState!==1)return;ws.send(m);wsLog('sent','ارسال: '+m);document.getElementById('ws-msg').value=''}
function wsDisc(){if(ws)ws.close()}
const ICON_MAP={ad:'ti-speakerphone',news:'ti-news',warning:'ti-alert-triangle',urgent:'ti-alert-octagon'};
const LABEL_MAP={ad:'تبلیغ',news:'خبر',warning:'هشدار',urgent:'فوری'};
async function loadAnnouncements(){
  try{
    const r=await authF('/api/announcements'),d=await r.json();
    const seen=JSON.parse(localStorage.getItem('rvg-seen-ann')||'[]');
    const list=(d.announcements||[]).filter(a=>!seen.includes(a.id));
    document.getElementById('ann-banner-wrap').innerHTML=list.map(a=>`
      <div class="ann-card ${a.type}" id="ann-${a.id}">
        <button class="ann-close" onclick="dismissAnn('${a.id}')"><i class="ti ti-x"></i></button>
        <div class="ann-icon"><i class="ti ${ICON_MAP[a.type]||'ti-bell'}"></i></div>
        <div class="ann-body">
          <div class="ann-title">${esc(a.title)} <span style="font-size:9px;color:var(--t3)">· ${LABEL_MAP[a.type]||''}</span></div>
          <div class="ann-text">${esc(a.body)}</div>
          ${a.image_url?`<img class="ann-img" src="${esc(a.image_url)}">`:''}
        </div>
      </div>`).join('');
      if (list.length) {
      authF('/api/announcements/view', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids: list.map(a => a.id) })
      }).catch(() => {});
    }
  }catch(e){}
}
function dismissAnn(id){
  const seen=JSON.parse(localStorage.getItem('rvg-seen-ann')||'[]');
  seen.push(id);localStorage.setItem('rvg-seen-ann',JSON.stringify(seen));
  document.getElementById('ann-'+id)?.remove();
}
let lastSupportMsgId = null;
 
function fmtSupTime(ts){
  const d = new Date(ts);
  return d.toLocaleTimeString('fa-IR',{hour:'2-digit',minute:'2-digit'});
}
function fmtSupDate(ts){
  const d = new Date(ts);
  const today = new Date();
  const isToday = d.toDateString() === today.toDateString();
  if (isToday) return 'امروز';
  const y = new Date(today); y.setDate(y.getDate()-1);
  if (d.toDateString() === y.toDateString()) return 'دیروز';
  return d.toLocaleDateString('fa-IR');
}
 
async function loadSupportMsgs() {
  try {
    const r = await authF('/api/support/messages'),
      d = await r.json();
    const msgs = d.messages || [];
    const blocked = !!d.blocked;
    const el = document.getElementById('support-msgs');

    if (el) {
      if (!msgs.length) {
        el.innerHTML =
          '<div class="sup-empty"><i class="ti ti-message-circle-2"></i><b>هنوز گفتگویی نیست</b><span>اولین پیام را شما بفرستید، تیم پشتیبانی به زودی پاسخ می‌دهد</span></div>';
      } else {
        let html = '',
          lastDate = '';
        msgs.forEach((m, idx) => {
          const dateLabel = fmtSupDate(m.created_at);
          if (dateLabel !== lastDate) {
            html +=
              '<div class="sup-date-sep"><span>' + dateLabel + '</span></div>';
            lastDate = dateLabel;
          }
          const isLastClientMsg =
            m.sender === 'client' && idx === msgs.length - 1; // not used, but kept
          const seenTick =
            m.sender === 'client'
              ? m.read_by_admin
                ? '<i class="ti ti-checks seen"></i>'
                : '<i class="ti ti-check"></i>'
              : '';
          // ✅ Fixed: removed backslashes before backticks
          html += `
            <div class="sup-msg-row ${m.sender}">
              <div class="sup-msg ${m.sender}">
                ${esc(m.body)}
                <span class="sup-time">${fmtSupTime(m.created_at)} ${seenTick}</span>
              </div>
              <div class="sup-avatar ${m.sender}"><i class="ti ${m.sender === 'admin' ? 'ti-headset' : 'ti-user'}"></i></div>
            </div>`;
        });
        el.innerHTML = html;
      }
      const shouldScroll =
        !lastSupportMsgId ||
        (msgs.length && msgs[msgs.length - 1].id !== lastSupportMsgId);
      if (shouldScroll) el.scrollTop = el.scrollHeight;
      if (msgs.length) lastSupportMsgId = msgs[msgs.length - 1].id;
    }

    const banner = document.getElementById('sup-blocked-banner');
    const inputRow = document.getElementById('sup-input-row');
    if (banner) banner.style.display = blocked ? 'flex' : 'none';
    if (inputRow) inputRow.classList.toggle('disabled', blocked);

    const nb = document.getElementById('support-nb');
    if (nb) {
      const lastAdmin = [...msgs].reverse().find((m) => m.sender === 'admin');
      const seenId = localStorage.getItem('rvg-last-seen-support-msg');
      const onSupportPage = document
        .getElementById('pg-support')
        .classList.contains('on');
      const hasNew = lastAdmin && lastAdmin.id !== seenId && !onSupportPage;
      nb.style.display = hasNew ? 'inline-flex' : 'none';
      if (lastAdmin && onSupportPage)
        localStorage.setItem('rvg-last-seen-support-msg', lastAdmin.id);
    }
  } catch (e) {
    // silent fail
  }
}
 
async function loadLoggingSetting(){
  try{
    const r=await authF('/api/settings/logging');
    if(!r.ok)return;
    const d=await r.json();
    document.getElementById('disable-logging-tog')?.classList.toggle('on', !!d.disabled);
  }catch(e){}
}
async function toggleLoggingSetting(){
  const btn=document.getElementById('disable-logging-tog');
  const next = !btn.classList.contains('on');
  btn.classList.toggle('on', next);
  try{
    const r=await authF('/api/settings/logging',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({disabled:next})});
    if(!r.ok)throw new Error();
    toast(next?'لاگ‌گیری کامل متوقف شد':'لاگ‌گیری دوباره فعال شد','ok');
  }catch(e){
    btn.classList.toggle('on', !next);
    toast('خطا در ذخیره‌ی تنظیمات','err');
  }
}
async function sendSupportMsg(){
  const inp=document.getElementById('support-inp');const msg=inp.value.trim();if(!msg)return;
  inp.disabled = true;
  try{
    const r=await authF('/api/support/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});
    if(r.status===403){toast('شما توسط پشتیبانی بلاک شده‌اید','err');loadSupportMsgs();inp.disabled=false;return}
    if(!r.ok)throw new Error();
    inp.value='';loadSupportMsgs();
  }catch(e){toast('خطا در ارسال پیام','err')}
  inp.disabled = false;
  inp.focus();
}
document.addEventListener('DOMContentLoaded', async () => {
  await checkAuth();
  initCharts();
  document.getElementById('set-host').textContent = location.host;
  loadLoggingSetting();
  document.getElementById('sub-all-url') && 
    (document.getElementById('sub-all-url').textContent = 
      location.protocol + '//' + location.host + '/sub-all');
  
  try {
    await loadVersion();
  } catch(e) {
    console.error('loadVersion failed:', e);
  }
  
  try {
    const updateDismissed = sessionStorage.getItem('rvg-update-dismissed') === 'true';
    if (updateAvailable && !updateDismissed) {
      document.getElementById('update-modal-version').textContent = updateVersion;
      document.getElementById('update-modal-desc').textContent = updateDescription;
      openModal('modal-update');
    }
  } catch(e) {
    console.error('modal error:', e);
  }

  fetchStats();
  fetchDefaultVless();
  loadLinks();
  loadSubs();
  loadAnnouncements();
  loadSupportMsgs();

  setInterval(fetchStats, 2000);
  setInterval(() => {
    if (document.getElementById('pg-links').classList.contains('on')) loadLinks();
    if (document.getElementById('pg-subgroups').classList.contains('on')) loadSubs();
    if (document.getElementById('pg-subscriptions').classList.contains('on')) loadSubsPage();
    if (document.getElementById('pg-connections').classList.contains('on')) loadConns();
    if (document.getElementById('pg-logs').classList.contains('on')) loadActivity();
    if (document.getElementById('pg-support').classList.contains('on')) loadSupportMsgs();
    loadVersion();
  }, 5000);
  setInterval(loadAnnouncements, 3000);
});

function timeAgoFa(ts){
  const diff = Math.max(0, (Date.now()/1000) - ts);
  if(diff < 60) return 'همین الان';
  if(diff < 3600) return toFa(Math.floor(diff/60))+' دقیقه پیش';
  if(diff < 86400) return toFa(Math.floor(diff/3600))+' ساعت پیش';
  if(diff < 2592000) return toFa(Math.floor(diff/86400))+' روز پیش';
  return new Date(ts*1000).toLocaleDateString('fa-IR');
}

async function loadVersion(){
  try{
    const r=await authF('/api/version'), d=await r.json();
    const cur=d.current||{}, lat=d.latest||{};

    document.getElementById('ver-current').textContent=cur.version||'—';
    document.getElementById('ver-current-desc').textContent=cur.description||'بدون توضیحات ثبت‌شده برای این نسخه';
    document.getElementById('ver-repo').textContent=d.repo||'تنظیم نشده';
    document.getElementById('ver-branch').textContent=d.branch||'—';

    const badge=document.getElementById('ver-status-badge'), nb=document.getElementById('update-nb');
    const latestCard=document.getElementById('upd-latest-card');

    if(lat.error){
      badge.innerHTML='<span class="upd-pill upd-pill-amber"><i class="ti ti-alert-triangle"></i> '+esc(lat.error)+'</span>';
      latestCard.style.display='none';
      nb.style.display='none';
      updateAvailable = false;
    } else if(d.update_available){
      badge.innerHTML='<span class="upd-pill upd-pill-amber"><span class="upd-dot"></span> بروزرسانی جدید موجود است</span>';
      document.getElementById('ver-latest-num').textContent=lat.version||'—';
      document.getElementById('ver-latest-desc').textContent=lat.description||'بدون توضیحات';
      latestCard.style.display='flex';
      nb.style.display='inline-flex';
      nb.textContent='1';
      // تنظیم متغیرهای سراسری برای مودال
      updateAvailable = true;
      updateVersion = lat.version || '—';
      updateDescription = lat.description || 'بدون توضیحات';
    } else {
      badge.innerHTML='<span class="upd-pill upd-pill-green"><i class="ti ti-circle-check"></i> پنل بروز است</span>';
      latestCard.style.display='none';
      nb.style.display='none';
      updateAvailable = false;
    }
  } catch(e) {
    console.error(e);
    updateAvailable = false;
  }
  loadUpdateHistory();
}

let updatePolling=null, pollTicks=0;
async function startUpdate(){
  if(!confirm('نصب بروزرسانی سرور را چند ثانیه ری‌استارت می‌کند. ادامه می‌دهید؟'))return;
  const btn=document.getElementById('update-btn');
  btn.disabled=true;btn.innerHTML='<i class="ti ti-loader-2" style="animation:spin 1s linear infinite"></i> در حال نصب...';
  document.getElementById('update-progress-wrap').style.display='block';
  pollTicks=0;
  try{
    await authF('/api/update',{method:'POST'});
    toast('بروزرسانی شروع شد','ok');
    updatePolling=setInterval(pollUpdate,900);
  }catch(e){
    toast('خطا در شروع بروزرسانی','err');
    btn.disabled=false;btn.innerHTML='<i class="ti ti-download"></i> نصب بروزرسانی';
  }
}
let btpPolling = null;
let btpHasToken = false;

function btpShowStep(step){
  ['input','vpn','ping','search','done'].forEach(s=>{
    document.getElementById('btp-step-'+s).style.display = (s===step) ? '' : 'none';
  });
  document.getElementById('btp-start-btn').style.display = (step==='input') ? 'flex' : 'none';
  document.getElementById('btp-continue-btn').style.display = (step==='vpn') ? 'flex' : 'none';
  document.getElementById('btp-stop-btn').style.display = (step==='search') ? 'flex' : 'none';
  document.getElementById('btp-cancel-btn').style.display = (step==='input'||step==='vpn'||step==='ping') ? 'flex' : 'none';
  document.getElementById('btp-close-done-btn').style.display = (step==='done') ? 'flex' : 'none';
}

function btpSetStatus(icon, cls, text, spin){
  const ic = document.getElementById('btp-status-icon');
  const note = document.getElementById('btp-status-note');
  ic.className = 'ti ' + icon;
  ic.style.animation = spin ? 'spin 1s linear infinite' : '';
  note.classList.remove('st-run','st-ok','st-err','st-warn');
  if(cls) note.classList.add(cls);
  document.getElementById('btp-status-text').textContent = text;
}

function btpSetPingStatus(icon, cls, text, spin){
  const ic = document.getElementById('btp-ping-status-icon');
  const note = document.getElementById('btp-ping-status-note');
  ic.className = 'ti ' + icon;
  ic.style.animation = spin ? 'spin 1s linear infinite' : '';
  note.classList.remove('st-run','st-ok','st-err','st-warn');
  if(cls) note.classList.add(cls);
  document.getElementById('btp-ping-status-text').textContent = text;
}

function btpRenderPingList(results){
  const el = document.getElementById('btp-ping-list');
  if(!results || !results.length){
    el.innerHTML = '<span style="font-size:11px;color:var(--t3)">در حال تست...</span>';
    return;
  }
  const sorted = [...results].sort((a,b)=> (b.ok - a.ok));
  el.innerHTML = sorted.map(r => `
    <div style="display:flex;align-items:center;gap:8px;background:${r.ok?'rgba(34,197,94,.08)':'rgba(239,68,68,.06)'};border:1px solid ${r.ok?'rgba(34,197,94,.25)':'rgba(239,68,68,.18)'};border-radius:10px;padding:7px 11px">
      <i class="ti ${r.ok?'ti-circle-check':'ti-clock-x'}" style="color:${r.ok?'var(--green-t)':'var(--red-t)'}"></i>
      <span style="flex:1;font-family:ui-monospace,monospace;font-size:11px;color:var(--t1)">${esc(r.domain)}</span>
      <span style="font-size:10px;color:${r.ok?'var(--green-t)':'var(--red-t)'}">${r.ok?'در دسترس':'Timeout'}</span>
    </div>
  `).join('');
}

function btpRenderFound(result){
  const el = document.getElementById('btp-found-list');
  if(!result){
    el.innerHTML = '<span style="font-size:11px;color:var(--t3)">هنوز چیزی پیدا نشده...</span>';
    return;
  }
  el.innerHTML = `
    <div style="display:flex;align-items:center;gap:8px;background:rgba(34,197,94,.08);border:1px solid rgba(34,197,94,.25);border-radius:10px;padding:8px 11px">
      <i class="ti ti-circle-check" style="color:var(--green-t)"></i>
      <span style="flex:1;font-family:ui-monospace,monospace;font-size:11px;color:var(--t1)">${esc(result.domain)}:${result.port}</span>
    </div>
  `;
}

function btpChangeToken(){
  document.getElementById('btp-token').style.display = '';
  document.getElementById('btp-token-saved-note').style.display = 'none';
  btpHasToken = false;
}

let btpReachableDomains = [];
let btpPingAborted = false;

async function btpCheckTokenState(){
  btpShowStep('input');
  document.getElementById('btp-token').value = '';
  document.getElementById('btp-port').value = '';
  btpReachableDomains = [];
  try{
    const r = await authF('/api/bot-tcp-proxy/status'), d = await r.json();
    btpHasToken = !!d.has_token;
    document.getElementById('btp-token').style.display = btpHasToken ? 'none' : '';
    document.getElementById('btp-token-saved-note').style.display = btpHasToken ? '' : 'none';

    if(d.running){
      btpShowStep('search');
      btpSetStatus('ti-loader-2', 'st-run', `در حال جست‌وجو... (${d.attempts} تلاش)`, true);
      btpRenderFound(null);
      btpPolling = setInterval(pollBotTcpProxy, 1200);
    } else if(d.phase === 'done' && d.result){
      btpFinishAttach(d.result);
    }
  }catch(e){}
}

function btpCloseModal(){
  clearInterval(btpPolling);
  btpPingAborted = true;
  closeModal('modal-bot-tcp-proxy');
}

// مرحله ۱ → مرحله ۲ (هشدار VPN)
function startBotTcpProxy(){
  const token = btpHasToken ? '' : document.getElementById('btp-token').value.trim();
  const portVal = document.getElementById('btp-port').value.trim();
  if(!btpHasToken && !token){ toast('توکن Railway را وارد کن','err'); return; }
  if(!portVal){ toast('پورت را وارد کن','err'); return; }
  btpShowStep('vpn');
  document.getElementById('btp-continue-btn').onclick = btpStartPing;
}

// مرحله ۲ → مرحله ۳: پینگ واقعی از خودِ مرورگر کاربر (نه از سرور پنل)، یکی‌یکی
const BTP_PING_TIMEOUT_MS = 6000;

async function btpPingOneDomain(domain){
  // fetch با mode:'no-cors' یعنی دقیقاً مثل باز کردن https://domain/ توی تب جدید مرورگر.
  // نکته‌ی مهم: بعضی از این دامنه‌ها گواهیِ TLS نامعتبر/نامنطبق دارن (صفحه‌ی "این اتصال
  // خصوصی نیست" توی کروم) — یعنی خودِ دامنه در دسترسه و اصلاً فیلتر نیست، فقط fetch به
  // خاطر گواهی خیلی سریع (کمتر از چند صد میلی‌ثانیه) reject می‌شه. این را نباید Timeout
  // حساب کرد. فقط وقتی واقعاً تا آخرِ مهلت (نزدیک ۶ ثانیه) صبر کردیم و جوابی نیومد،
  // یعنی واقعاً فیلتر/غیرقابل‌دسترسه.
  const ctrl = new AbortController();
  const timer = setTimeout(()=>ctrl.abort(), BTP_PING_TIMEOUT_MS);
  const started = performance.now();
  try{
    await fetch('https://' + domain + '/', { mode:'no-cors', cache:'no-store', signal: ctrl.signal });
    clearTimeout(timer);
    return true;
  }catch(e){
    clearTimeout(timer);
    const elapsed = performance.now() - started;
    // اگر خیلی زود شکست خورد (نه به خاطر Timeout واقعی ما)، یعنی دامنه در دسترس بوده
    // ولی به دلیلی دیگه (مثل گواهی نامعتبر) fetch رد شده — پس این را «سالم» حساب می‌کنیم.
    return elapsed < (BTP_PING_TIMEOUT_MS * 0.85);
  }
}

async function btpStartPing(){
  btpShowStep('ping');
  btpPingAborted = false;
  btpSetPingStatus('ti-loader-2', 'st-run', 'در حال تست دامنه‌ها از اینترنت خودت...', true);
  btpRenderPingList([]);

  let domains = [];
  try{
    const r = await authF('/api/bot-tcp-proxy/domains'), d = await r.json();
    domains = d.domains || [];
  }catch(e){
    toast('✗ خطا در گرفتن لیست دامنه‌ها','err');
    btpShowStep('input');
    return;
  }

  const results = [];
  for(const domain of domains){
    if(btpPingAborted) return;
    btpSetPingStatus('ti-loader-2', 'st-run', `در حال تست... (${results.length+1}/${domains.length}) ${domain}`, true);
    const ok = await btpPingOneDomain(domain);
    results.push({domain, ok});
    btpRenderPingList(results);
  }
  if(btpPingAborted) return;

  btpReachableDomains = results.filter(r=>r.ok).map(r=>r.domain);
  if(btpReachableDomains.length > 0){
    btpSetPingStatus('ti-circle-check', 'st-ok', `${btpReachableDomains.length} دامنه با اینترنت تو کار می‌کنه`, false);
    document.getElementById('btp-continue-btn').style.display = 'flex';
    document.getElementById('btp-continue-btn').onclick = btpStartSearch;
    document.getElementById('btp-cancel-btn').style.display = 'flex';
  } else {
    btpSetPingStatus('ti-alert-circle', 'st-err', 'هیچ دامنه‌ای با اینترنت تو کار نکرد', false);
    toast('✗ هیچ‌کدام از دامنه‌ها با اینترنت تو باز نشدن','err');
  }
}


// مرحله ۳ → مرحله ۴ (ساخت مکرر پروکسی تا رسیدن به یک دامنه‌ی سالم)
async function btpStartSearch(){
  const token = btpHasToken ? '' : document.getElementById('btp-token').value.trim();
  const port = document.getElementById('btp-port').value.trim();

  btpShowStep('search');
  btpSetStatus('ti-loader-2', 'st-run', 'در حال اتصال به Railway...', true);
  btpRenderFound(null);

  try{
    const r = await authF('/api/bot-tcp-proxy/start', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ token, port, reachable_domains: btpReachableDomains })
    });
    if(!r.ok){ const d = await r.json().catch(()=>({})); throw new Error(d.detail || 'خطا'); }
    btpPolling = setInterval(pollBotTcpProxy, 1200);
  }catch(e){
    toast('✗ '+e.message,'err');
    btpSetStatus('ti-alert-circle', 'st-err', e.message, false);
    btpShowStep('input');
  }
}

async function stopBotTcpProxy(){
  const btn = document.getElementById('btp-stop-btn');
  btn.disabled = true;
  try{
    await authF('/api/bot-tcp-proxy/stop', {method:'POST'});
    toast('درخواست توقف ارسال شد','ok');
  }catch(e){
    toast('خطا در توقف','err');
  }
  btn.disabled = false;
}

async function pollBotTcpProxy(){
  try{
    const r = await authF('/api/bot-tcp-proxy/status'), d = await r.json();
    if(d.running){
      btpSetStatus('ti-loader-2', 'st-run', `در حال تلاش... (${d.attempts} تلاش)`, true);
    }else{
      clearInterval(btpPolling);
      if(d.phase === 'done' && d.result){
        btpSetStatus('ti-circle-check', 'st-ok', 'دامنه‌ی سالم پیدا شد ✓', false);
        btpRenderFound(d.result);
        await btpFinishAttach(d.result);
      } else if(d.stopped_by_user){
        btpSetStatus('ti-player-stop', 'st-warn', 'فرآیند متوقف شد', false);
        btpShowStep('input');
      } else if(d.error){
        btpSetStatus('ti-alert-circle', 'st-err', d.error, false);
        toast('✗ '+d.error,'err');
        btpShowStep('input');
      }
    }
  }catch(e){}
}

// مرحله ۴ → مرحله ۵ (اتصال خودکار به پروکسی تلگرام)
async function btpFinishAttach(result){
  try{
    const r = await authF('/api/bot-tcp-proxy/attach', {method:'POST'});
    if(!r.ok){ const d = await r.json().catch(()=>({})); throw new Error(d.detail || 'خطا'); }
    const d = await r.json();
    document.getElementById('btp-done-domain').textContent = `${d.result.domain}:${d.result.port}`;
    if(d.share_link){
      document.getElementById('btp-done-link-wrap').style.display = '';
      document.getElementById('btp-done-link').value = d.share_link;
      toast('پروکسی تلگرام «'+ (d.attached_link ? d.attached_link.label : '') +'» ساخته شد ✓','ok');
    } else {
      toast('دامنه نهایی شد، اما لینک تلگرامی برای اتصال پیدا نشد','warn');
    }
    btpShowStep('done');
  }catch(e){
    toast('✗ '+e.message,'err');
  }
}

function btpCopyLink(){
  const inp = document.getElementById('btp-done-link');
  inp.select();
  navigator.clipboard.writeText(inp.value).then(()=>toast('کپی شد ✓','ok')).catch(()=>{});
}

// ══════════════════ Zeus Proxy — کارت داخل لیست کانفیگ‌ها + مدیریت + آی‌پی‌های متصل ══════════════════
let zpHasToken = false;
let zpStatusInterval = null;
let zeusStatus = null; // آخرین وضعیت دریافت‌شده از /api/zeus-proxy/status (توسط loadLinks پر می‌شود)

// ── کارت پروکسی Zeus با همون دیزاین بقیه‌ی کانفیگ‌ها ──
function zpExpChip(remH){
  if(remH === null || remH === undefined) return '<span class="exp-chip ec-inf"><i class="ti ti-infinity"></i> نامحدود</span>';
  if(remH <= 0) return '<span class="exp-chip ec-exp"><i class="ti ti-calendar-x"></i> منقضی</span>';
  const days = Math.floor(remH/24);
  if(days <= 0) return `<span class="exp-chip ec-warn"><i class="ti ti-alert-triangle"></i> ${toFa(Math.ceil(remH))} ساعت مانده</span>`;
  if(days <= 3) return `<span class="exp-chip ec-warn"><i class="ti ti-alert-triangle"></i> ${toFa(days)} روز مانده</span>`;
  return `<span class="exp-chip ec-ok"><i class="ti ti-calendar-check"></i> ${toFa(days)} روز مانده</span>`;
}
function zeusUniqueIpCount(d){
  // هر آی‌پی، صرف‌نظر از تعداد اتصال‌های بازی که دارد، فقط یک بار شمرده می‌شود
  const byIp = (d && d.connections_by_ip) || {};
  return Object.keys(byIp).length;
}
function zeusCardHtml(d){
  const r = d.result || {};
  const limitGb = r.traffic_limit_gb ?? d.config?.traffic_limit_gb ?? 0;
  const usedGb  = d.bytes_used_gb ?? 0;
  const pct     = limitGb ? Math.min(100, usedGb/limitGb*100) : 0;
  const bc      = pct>90?'var(--red)':pct>70?'var(--amber)':'var(--accent)';
  const remH    = d.expires_remaining_hours;
  const expired = (remH !== null && remH !== undefined && remH <= 0);
  const ipCount = zeusUniqueIpCount(d);
  const cfgStr  = esc(r.config || '');
  return `<div class="cfg-card ${expired?'is-exp':''}" data-uuid="zeus-proxy">
    <div class="cfg-row">
      <span style="width:18px;flex-shrink:0"></span>
      <span class="cfg-status-dot ${!expired?'pulse':''}"></span>
      <div class="cfg-identity">
        <div class="cfg-label">پروکسی Zeus</div>
        <div class="cfg-sub-meta">
          <span class="cfg-uuid-mini" onclick="zpCopyConfigStr('${cfgStr}')" title="کپی کانفیگ"><i class="ti ti-key"></i> SOCKS5</span>
        </div>
      </div>
      <div class="cfg-divider-v"></div>
      <div class="cfg-usage-col">
        <div class="ubar"><div class="ubar-f" style="width:${pct}%;background:${bc}"></div></div>
        <div class="utxt"><span>${usedGb.toFixed(2)} GB</span><span>از ${limitGb?limitGb+' GB':'∞'}</span></div>
      </div>
      <div class="cfg-divider-v"></div>
      <div class="cfg-exp-col">${zpExpChip(remH)}</div>
      <div class="cfg-divider-v"></div>
      <div class="cfg-badges-col">
        <span class="proto-chip pc-ss">SOCKS5 · Zeus</span>
        <span class="cfg-sub-tag"><i class="ti ti-router"></i> ${toFa(ipCount)} آی‌پی متصل</span>
      </div>
      <div class="cfg-divider-v"></div>
      <div class="cfg-actions">
        <button class="btn btn-sm btn-g btn-icon" onclick="zpOpenIps()" title="آی‌پی‌های متصل"><i class="ti ti-network"></i></button>
        <button class="btn btn-sm btn-g btn-icon" onclick="zpCopyConfigStr('${cfgStr}')" title="کپی کانفیگ"><i class="ti ti-copy"></i></button>
        <button class="btn btn-sm btn-amber btn-icon" onclick="zpOpenManage()" title="مدیریت / ویرایش"><i class="ti ti-settings"></i></button>
        <button class="btn btn-sm btn-d btn-icon" onclick="zpDelete()" title="حذف"><i class="ti ti-trash"></i></button>
      </div>
    </div>
  </div>`;
}
function zpCopyConfigStr(str){
  navigator.clipboard.writeText(str).then(()=>toast('کانفیگ کپی شد ✓','ok')).catch(()=>{});
}
function refreshZeusCardOnly(d){
  const grid = document.getElementById('links-grid');
  const old = grid.querySelector('.cfg-card[data-uuid="zeus-proxy"]');
  if(old) old.outerHTML = zeusCardHtml(d);
}

// ── مودال ساخت (فقط ساخت — بعد از ساخت، مدیریت از روی کارت لیست انجام می‌شود) ──
function zpChangeToken(){
  document.getElementById('zp-token').style.display = '';
  document.getElementById('zp-token-saved-note').style.display = 'none';
  zpHasToken = false;
}

function zpShowCreateStep(step){
  ['input','building','error'].forEach(s=>{
    document.getElementById('zp-step-'+s).style.display = (s===step ? '' : 'none');
  });
  document.getElementById('zp-start-btn').style.display = (step==='input') ? '' : 'none';
}

async function zpCheckTokenState(){
  zpShowCreateStep('input');
  document.getElementById('zp-token').value = '';
  try{
    const r = await authF('/api/zeus-proxy/status'), d = await r.json();
    zeusStatus = d;
    zpHasToken = !!d.has_token;
    document.getElementById('zp-token').style.display = zpHasToken ? 'none' : '';
    document.getElementById('zp-token-saved-note').style.display = zpHasToken ? '' : 'none';
    const cfg = d.config || {};
    document.getElementById('zp-cfg-traffic').value = cfg.traffic_limit_gb ?? 10;
    document.getElementById('zp-cfg-days').value    = cfg.expires_days ?? 30;
    document.getElementById('zp-cfg-maxip').value   = cfg.max_connections_per_ip ?? 3;
  }catch(e){}
}

function zpCloseModal(){
  closeModal('modal-zeus-proxy');
}

async function zpStart(){
  const token = zpHasToken ? '' : document.getElementById('zp-token').value.trim();
  if(!zpHasToken && !token){ toast('توکن Railway را وارد کن','err'); return; }

  const traffic_limit_gb       = parseFloat(document.getElementById('zp-cfg-traffic').value) || 0;
  const expires_days           = parseInt(document.getElementById('zp-cfg-days').value)    || 0;
  const max_connections_per_ip = parseInt(document.getElementById('zp-cfg-maxip').value)   || 0;

  zpShowCreateStep('building');
  try{
    const r = await authF('/api/zeus-proxy/create', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({token, traffic_limit_gb, expires_days, max_connections_per_ip})
    });
    const d = await r.json();
    if(!r.ok){ throw new Error(d.detail || 'ساخت پروکسی ناموفق بود'); }
    toast('پروکسی Zeus ساخته شد ✓','ok');
    zpCloseModal();
    await loadLinks(); // پروکسی حالا مثل بقیه‌ی کانفیگ‌ها توی لیست نمایش داده می‌شود
  }catch(e){
    document.getElementById('zp-error-text').textContent = e.message;
    zpShowCreateStep('error');
    document.getElementById('zp-start-btn').style.display = '';
  }
}

// ── مودال مدیریت (آمار + ویرایش کانفیگ) — از روی کارت لیست باز می‌شود ──
function zpRenderDone(d){
  const result = d.result || d;
  document.getElementById('zp-done-config').value = result.config || '';
  document.getElementById('zp-edit-traffic').value = result.traffic_limit_gb ?? d.config?.traffic_limit_gb ?? 10;
  document.getElementById('zp-edit-days').value    = result.expires_days    ?? d.config?.expires_days    ?? 30;
  document.getElementById('zp-edit-maxip').value   = result.max_connections_per_ip ?? d.config?.max_connections_per_ip ?? 3;
  zpUpdateStats(d);
}

function zpUpdateStats(d){
  const usedGb   = (d.bytes_used_gb ?? 0).toFixed(3);
  const limitGb  = d.result?.traffic_limit_gb ?? 0;
  const pct      = d.traffic_percent;
  document.getElementById('zp-stat-traffic').textContent =
    limitGb ? `${usedGb} / ${limitGb} GB` : `${usedGb} GB`;
  const barWrap = document.getElementById('zp-traffic-bar-wrap');
  if(limitGb && pct !== null && pct !== undefined){
    barWrap.style.display = '';
    const bar = document.getElementById('zp-traffic-bar');
    bar.style.width = Math.min(100, pct) + '%';
    bar.style.background = pct >= 90 ? 'var(--red-t)' : pct >= 70 ? '#f59e0b' : 'var(--accent)';
    document.getElementById('zp-traffic-bar-label').textContent = pct.toFixed(1) + '% مصرف‌شده';
  } else { barWrap.style.display = 'none'; }

  const remH = d.expires_remaining_hours;
  if(remH === null || remH === undefined){
    document.getElementById('zp-stat-expiry').textContent = 'بی‌انقضا';
  } else {
    const days = Math.floor(remH / 24), hrs = Math.floor(remH % 24);
    document.getElementById('zp-stat-expiry').textContent =
      days > 0 ? `${days}روز ${hrs}ساعت` : `${hrs}ساعت`;
  }

  // اتصال‌ها: هر آی‌پی صرف‌نظر از تعداد اتصال‌هایش یک بار شمرده می‌شود
  const ipCount = zeusUniqueIpCount(d);
  document.getElementById('zp-stat-conns').textContent = `${toFa(ipCount)} IP`;
}

function zpOpenManage(){
  if(!zeusStatus || zeusStatus.phase !== 'done') return;
  zpRenderDone(zeusStatus);
  openModal('modal-zeus-manage');
  zpStartPolling();
}
function zpCloseManage(){
  closeModal('modal-zeus-manage');
  zpMaybeStopPolling();
}
function zpCloseIps(){
  closeModal('modal-zeus-ips');
  zpMaybeStopPolling();
}

// ── مودال آی‌پی‌های متصل (شمارش یکتا: هر آی‌پی فقط یک بار) ──
function zpRenderIps(d){
  const byIp = (d && d.connections_by_ip) || {};
  const ips  = Object.keys(byIp);
  document.getElementById('zp-ips-sub').textContent = `${toFa(ips.length)} آی‌پی متصل (هر آی‌پی یک بار شمرده می‌شود)`;
  const list = document.getElementById('zp-ips-list'), empty = document.getElementById('zp-ips-empty');
  if(!ips.length){ list.innerHTML=''; empty.style.display='block'; return; }
  empty.style.display='none';
  list.innerHTML = ips.map(ip=>`
    <div style="display:flex;align-items:center;justify-content:space-between;background:var(--card2,var(--card));border-radius:8px;padding:8px 12px">
      <span style="font-family:ui-monospace,monospace;font-size:12.5px;direction:ltr;text-align:left">${esc(ip)}</span>
      <span class="cfg-sub-tag" title="تعداد اتصال باز این آی‌پی — در شمارش کلی فقط ۱ حساب می‌شود">${toFa(byIp[ip])} اتصال</span>
    </div>
  `).join('');
}
function zpOpenIps(){
  if(!zeusStatus || zeusStatus.phase !== 'done') return;
  zpRenderIps(zeusStatus);
  openModal('modal-zeus-ips');
  zpStartPolling();
}

// ── پولینگ مشترک وقتی مودال مدیریت یا آی‌پی‌ها باز است ──
function zpStartPolling(){
  if(zpStatusInterval) return;
  zpStatusInterval = setInterval(async ()=>{
    try{
      const r = await authF('/api/zeus-proxy/status'), d = await r.json();
      zeusStatus = d;
      if(d.phase !== 'done'){
        zpMaybeStopPolling(true);
        closeModal('modal-zeus-manage'); closeModal('modal-zeus-ips');
        loadLinks();
        return;
      }
      if(document.getElementById('modal-zeus-manage').classList.contains('open')) zpUpdateStats(d);
      if(document.getElementById('modal-zeus-ips').classList.contains('open')) zpRenderIps(d);
      refreshZeusCardOnly(d);
    }catch(e){}
  }, 5000);
}
function zpMaybeStopPolling(force){
  const manageOpen = document.getElementById('modal-zeus-manage').classList.contains('open');
  const ipsOpen = document.getElementById('modal-zeus-ips').classList.contains('open');
  if(force || (!manageOpen && !ipsOpen)){ clearInterval(zpStatusInterval); zpStatusInterval = null; }
}

async function zpDelete(){
  if(!confirm('پروکسی Zeus حذف شود؟ TCP Proxy روی Railway هم پاک می‌شود.')) return;
  try{
    const r = await authF('/api/zeus-proxy/delete',{method:'POST'});
    if(!r.ok) throw new Error('حذف ناموفق');
    toast('پروکسی Zeus حذف شد','ok');
    zeusStatus = null;
    clearInterval(zpStatusInterval); zpStatusInterval = null;
    closeModal('modal-zeus-manage');
    closeModal('modal-zeus-ips');
    await loadLinks();
  }catch(e){ toast('خطا: '+e.message,'err'); }
}

async function zpSaveConfig(){
  const traffic_limit_gb       = parseFloat(document.getElementById('zp-edit-traffic').value) || 0;
  const expires_days           = parseInt(document.getElementById('zp-edit-days').value)       || 0;
  const max_connections_per_ip = parseInt(document.getElementById('zp-edit-maxip').value)      || 0;
  try{
    const r = await authF('/api/zeus-proxy/config',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({traffic_limit_gb, expires_days, max_connections_per_ip})
    });
    if(!r.ok) throw new Error('ذخیره ناموفق');
    toast('کانفیگ ذخیره شد ✓','ok');
    const rr = await authF('/api/zeus-proxy/status');
    zeusStatus = await rr.json();
    zpUpdateStats(zeusStatus);
    refreshZeusCardOnly(zeusStatus);
  }catch(e){ toast('خطا: '+e.message,'err'); }
}

function zpCopyConfig(){
  const inp = document.getElementById('zp-done-config');
  inp.select();
  navigator.clipboard.writeText(inp.value).then(()=>toast('کپی شد ✓','ok')).catch(()=>{});
}
async function pollUpdate(){
  pollTicks++;
  try{
    const r=await fetch('/api/update-log',{credentials:'include'});
    if(r.status===401){clearInterval(updatePolling);location.reload();return}
    const d=await r.json();
    document.getElementById('update-progress-bar').style.width=d.progress+'%';
    document.getElementById('update-progress-pct').textContent=d.progress+'%';
    renderUpdateLog(d.logs);
    if(d.logs && d.logs.length) document.getElementById('update-progress-txt').textContent=d.logs[d.logs.length-1].msg;

    if(!d.running && d.progress>=100){
      document.getElementById('update-progress-txt').textContent='بروزرسانی کامل شد؛ در حال اتصال مجدد...';
      clearInterval(updatePolling);
      let tries=0;
      const reconnect=setInterval(async()=>{
        tries++;
        try{const rr=await fetch('/api/me',{credentials:'include'});if(rr.ok){clearInterval(reconnect);location.reload();}}catch(e){}
        if(tries>40)clearInterval(reconnect);
      },2000);
    }else if(!d.running && pollTicks>3){
      document.getElementById('update-progress-txt').textContent='بروزرسانی متوقف شد (خطا) — لاگ را ببینید';
      document.getElementById('update-btn').disabled=false;
      document.getElementById('update-btn').innerHTML='<i class="ti ti-download"></i> نصب بروزرسانی';
      clearInterval(updatePolling);
    }
  }catch(e){}
}
async function loadUpdateLog(){
  try{const r=await authF('/api/update-log'),d=await r.json();renderUpdateLog(d.logs);}catch(e){}
}

let dgPolling = null;

function dgSetStatus(icon, color, text, spin){
  const ic = document.getElementById('dg-status-icon');
  ic.className = 'ti ' + icon;
  ic.style.color = color;
  ic.style.animation = spin ? 'spin 1s linear infinite' : '';
  document.getElementById('dg-status-text').textContent = text;
}
function dgToggleButtons(running){
  document.getElementById('dg-start-btn').style.display = running ? 'none' : 'flex';
  document.getElementById('dg-stop-btn').style.display = running ? 'flex' : 'none';
}
function dgChangeToken(){
  document.getElementById('dg-token-section').style.display = '';
  document.getElementById('dg-token-saved-section').style.display = 'none';
}
function dgRenderResults(results){
  const el = document.getElementById('dg-results');
  if(!results || !results.length){ el.innerHTML=''; return; }
  el.innerHTML = results.map(r=>`
    <div style="display:flex;align-items:center;gap:8px;background:rgba(16,185,129,.08);border:1px solid rgba(16,185,129,.2);border-radius:10px;padding:8px 11px">
      <i class="ti ti-circle-check" style="color:var(--green-t)"></i>
      <span style="flex:1;font-family:ui-monospace,monospace;font-size:11px;color:var(--t1)">${esc(r.domain)}:${r.port}</span>
      <button class="btn btn-sm btn-g" onclick="navigator.clipboard.writeText('${esc(r.domain)}:${r.port}').then(()=>toast('کپی شد ✓','ok'))"><i class="ti ti-copy"></i></button>
    </div>
  `).join('');
}
async function dgCheckTokenState(){
  try{
    const r = await authF('/api/domain-gen/status'), d = await r.json();
    document.getElementById('dg-token-section').style.display = d.has_token ? 'none' : '';
    document.getElementById('dg-token-saved-section').style.display = d.has_token ? '' : 'none';
    dgToggleButtons(d.running);
    dgRenderResults(d.results || []);
    if(d.running){
      dgPolling = setInterval(pollDomainGen, 1500);
      dgSetStatus('ti-loader-2','var(--accent)', `در حال ساخت... (${d.attempts} تلاش، ${(d.results||[]).length}/${d.target_count} دامنه)`, true);
    }
  }catch(e){}
}
async function startDomainGen(){
  const tokenField = document.getElementById('dg-token');
  const token = tokenField.style.display !== 'none' ? tokenField.value.trim() : '';
  const port = document.getElementById('dg-port').value.trim();
  const count = parseInt(document.getElementById('dg-count').value || '10');

  const btn = document.getElementById('dg-start-btn');
  btn.disabled = true;
  btn.innerHTML = '<i class="ti ti-loader-2" style="animation:spin 1s linear infinite"></i> در حال اجرا...';
  dgSetStatus('ti-loader-2','var(--accent)','در حال اتصال به Railway...', true);
  document.getElementById('dg-log-box').style.display = 'block';

  try{
    const r = await authF('/api/domain-gen/start', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ token, port: port || undefined, count })
    });
    if(!r.ok){ const d = await r.json().catch(()=>({})); throw new Error(d.detail || 'خطا'); }
    document.getElementById('dg-token-section').style.display = 'none';
    document.getElementById('dg-token-saved-section').style.display = '';
    dgToggleButtons(true);
    dgPolling = setInterval(pollDomainGen, 1500);
  }catch(e){
    toast('✗ '+e.message,'err');
    dgSetStatus('ti-alert-circle','var(--red-t)', e.message, false);
    btn.disabled = false; btn.innerHTML = '<i class="ti ti-player-play"></i> شروع ساخت';
  }
}
async function stopDomainGen(){
  const btn = document.getElementById('dg-stop-btn');
  btn.disabled = true;
  try{ await authF('/api/domain-gen/stop', {method:'POST'}); toast('درخواست توقف ارسال شد','ok'); }
  catch(e){ toast('خطا در توقف','err'); }
  btn.disabled = false;
}
async function pollDomainGen(){
  try{
    const r = await authF('/api/domain-gen/status'), d = await r.json();
    const box = document.getElementById('dg-log-box');
    box.innerHTML = (d.logs||[]).map(l=>`<p class="upd-log-line">[${new Date(l.time*1000).toLocaleTimeString('fa-IR')}] ${esc(l.msg)}</p>`).join('') || '<p class="upd-log-empty">لاگی موجود نیست</p>';
    box.scrollTop = box.scrollHeight;
    dgRenderResults(d.results || []);

    if(d.running){
      dgToggleButtons(true);
      dgSetStatus('ti-loader-2','var(--accent)', `در حال ساخت... (${d.attempts} تلاش، ${(d.results||[]).length}/${d.target_count} دامنه)`, true);
    }else{
      clearInterval(dgPolling);
      dgToggleButtons(false);
      const btn = document.getElementById('dg-start-btn');
      btn.disabled = false; btn.innerHTML = '<i class="ti ti-player-play"></i> شروع ساخت';
      if(d.results && d.results.length >= d.target_count){
        dgSetStatus('ti-circle-check','var(--green-t)', `${d.target_count} دامنه با موفقیت ساخته شد ✓`, false);
        toast(d.target_count+' دامنه ساخته شد ✓','ok');
      } else if(d.stopped_by_user){
        dgSetStatus('ti-player-stop','var(--amber-t)', 'فرآیند متوقف شد', false);
      } else if(d.error){
        dgSetStatus('ti-alert-circle','var(--red-t)', d.error, false);
      }
    }
  }catch(e){}
}

function renderUpdateLog(logs){
  const box=document.getElementById('update-log-box');
  if(!logs||!logs.length){box.innerHTML='<p class="upd-log-empty">لاگی موجود نیست</p>';return}
  box.innerHTML=logs.map(l=>{
    const cls = l.msg.includes('❌') ? 'err' : (l.msg.includes('✅') ? 'ok' : '');
    return `<p class="upd-log-line ${cls}">[${new Date(l.time*1000).toLocaleTimeString('fa-IR')}] ${esc(l.msg)}</p>`;
  }).join('');
  box.scrollTop=box.scrollHeight;
}
async function loadUpdateHistory(){
  try{
    const r=await authF('/api/update-history'),d=await r.json();
    const hist=d.history||[];
    document.getElementById('upd-history-count').textContent=toFa(hist.length)+' مورد';
    const el=document.getElementById('upd-history-list');
    if(!hist.length){
      el.innerHTML='<div class="upd-history-empty"><i class="ti ti-history-toggle"></i><p>هنوز هیچ بروزرسانی‌ای ثبت نشده</p></div>';
      return;
    }
    el.innerHTML=hist.map(h=>{
      const isErr = h.status==='err';
      return `
      <div class="upd-item ${isErr?'err':''}">
        <div class="upd-item-dot-wrap"><div class="upd-item-dot"><i class="ti ${isErr?'ti-x':'ti-check'}"></i></div></div>
        <div class="upd-item-card">
          <div class="upd-item-head">
            <div class="upd-item-versions">
              <span>${esc(h.from_version||'—')}</span>
              <i class="ti ti-arrow-left arrow"></i>
              <span class="to">${esc(h.to_version||'—')}</span>
            </div>
            <span class="upd-item-badge ${isErr?'err':'ok'}">${isErr?'ناموفق':'موفق'}</span>
          </div>
          <div class="upd-item-time"><i class="ti ti-clock"></i> ${new Date(h.time*1000).toLocaleString('fa-IR')} · ${timeAgoFa(h.time)}</div>
          ${h.description?`<div class="upd-item-desc">${esc(h.description)}</div>`:''}
          ${isErr && h.error?`<div class="upd-item-err-box"><i class="ti ti-alert-circle"></i> ${esc(h.error)}</div>`:''}
        </div>
      </div>`;
    }).join('');
  }catch(e){console.error(e)}
}
let autoDomainPolling = null;

async function autoGetMtprotoDomain(){
  // اول چک کن توکن ذخیره شده یا نه
  try{
    const r = await authF('/api/bot-tcp-proxy/status'), d = await r.json();
    if(!d.has_token){
      document.getElementById('auto-domain-token-wrap').style.display = 'block';
      document.getElementById('auto-domain-status').innerHTML = '<i class="ti ti-key"></i> برای دریافت خودکار دامنه، ابتدا توکن Railway را وارد کن.';
      return;
    }
    startAutoDomainFetch();
  }catch(e){
    toast('خطا در بررسی وضعیت توکن','err');
  }
}

async function submitAutoDomainToken(){
  const token = document.getElementById('auto-domain-token').value.trim();
  if(!token){ toast('توکن را وارد کن','err'); return; }
  document.getElementById('auto-domain-token-wrap').style.display = 'none';
  startAutoDomainFetch(token);
}

async function startAutoDomainFetch(token){
  const btn = document.getElementById('auto-domain-btn');
  const statusEl = document.getElementById('auto-domain-status');
  btn.disabled = true;
  btn.innerHTML = '<i class="ti ti-loader-2" style="animation:spin 1s linear infinite"></i> در حال دریافت...';
  statusEl.innerHTML = '<i class="ti ti-loader-2" style="animation:spin 1s linear infinite"></i> در حال دریافت دامنه از Railway...';

  try{
    const body = { mode: 'blacklist' };
    if(token) body.token = token;
    const r = await authF('/api/bot-tcp-proxy/start', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify(body)
    });
    if(!r.ok){
      const d = await r.json().catch(()=>({}));
      throw new Error(d.detail || 'خطا در شروع فرآیند');
    }
    autoDomainPolling = setInterval(pollAutoDomain, 1000);
  }catch(e){
    statusEl.innerHTML = '<i class="ti ti-alert-circle" style="color:var(--red-t)"></i> ✗ '+esc(e.message);
    btn.disabled = false;
    btn.innerHTML = '<i class="ti ti-bolt"></i> دریافت دامنه';
  }
}

async function pollAutoDomain(){
  try{
    const r = await authF('/api/bot-tcp-proxy/status'), d = await r.json();
    const btn = document.getElementById('auto-domain-btn');
    const statusEl = document.getElementById('auto-domain-status');

    if(d.running){
      statusEl.innerHTML = `<i class="ti ti-loader-2" style="animation:spin 1s linear infinite"></i> در حال جستجوی دامنه... (${d.attempts} تلاش)`;
      return;
    }

    clearInterval(autoDomainPolling);
    btn.disabled = false;
    btn.innerHTML = '<i class="ti ti-bolt"></i> دریافت خودکار دامنه';

    if(d.result){
      // پر کردن خودکار فیلدها بدون دخالت کاربر
      document.getElementById('nl-mtproto-domain').value = d.result.domain;
      document.getElementById('nl-mtproto-port').value = ''; // پورت داخلی همان پیش‌فرض می‌ماند؛ این پورت، پورت عمومی TCP است
      statusEl.innerHTML = `<i class="ti ti-circle-check" style="color:var(--green-t)"></i> دامنه دریافت شد: <b>${esc(d.result.domain)}:${d.result.port}</b>`;
      toast('دامنه و پورت خودکار دریافت شد ✓','ok');
    } else if(d.error){
      statusEl.innerHTML = '<i class="ti ti-alert-circle" style="color:var(--red-t)"></i> ✗ '+esc(d.error);
      toast('✗ '+d.error,'err');
    }
  }catch(e){}
}

function openDomainScanModal(){
  dsDomains = [];
  dsRenderChips();
  document.getElementById('ds-token-section').style.display = '';
  openModal('modal-domain-scan');
  authF('/api/bot-tcp-proxy/status').then(r=>r.json()).then(d=>{
    if(d.has_token) document.getElementById('ds-token-section').style.display = 'none';
  }).catch(()=>{});
}
async function autoAssignMtprotoDomain(){
  const btn = document.getElementById('auto-domain-btn');
  const statusEl = document.getElementById('auto-domain-status');
  btn.disabled = true;
  btn.innerHTML = '<i class="ti ti-loader-2" style="animation:spin 1s linear infinite"></i> در حال دریافت...';
  statusEl.innerHTML = '<i class="ti ti-loader-2" style="animation:spin 1s linear infinite"></i> در حال اتصال به Railway و دریافت دامنه...';

  try{
    const r = await authF('/api/bot-tcp-proxy/start', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ mode:'blacklist' }) // توکن ذخیره‌شده خودکار استفاده می‌شود
    });
    if(!r.ok){
      const d = await r.json().catch(()=>({}));
      throw new Error(d.detail || 'خطا در شروع فرآیند');
    }
    autoDomainPolling = setInterval(pollAutoDomain, 1200);
  }catch(e){
    statusEl.innerHTML = '<i class="ti ti-alert-circle" style="color:var(--red-t)"></i> ✗ '+e.message;
    btn.disabled = false;
    btn.innerHTML = '<i class="ti ti-bolt"></i> دریافت خودکار دامنه';
  }
}


function dsAddDomain(){
  const inp = document.getElementById('ds-domain-inp');
  const v = inp.value.trim().toLowerCase().replace(/\.$/, '');
  if(v && !dsDomains.includes(v)) dsDomains.push(v);
  inp.value = '';
  document.querySelectorAll('#modal-domain-scan .cm-opt').forEach(o=>o.classList.remove('sel')); // جدید
  dsRenderChips();
}
function dsRemoveDomain(d){
  dsDomains = dsDomains.filter(x=>x!==d);
  dsRenderChips();
}
function dsRenderChips(){
  document.getElementById('ds-domain-chips').innerHTML = dsDomains.map(d=>
    `<span class="cm-pill active" style="cursor:pointer" onclick="dsRemoveDomain('${d}')">${d} <i class="ti ti-x" style="font-size:10px"></i></span>`
  ).join('') || '<span style="font-size:10.5px;color:var(--t3)">هنوز دامنه‌ای اضافه نشده</span>';
}
async function startDomainScan(){
  if(!dsDomains.length){ toast('حداقل یک دامنه اضافه کن','err'); return; }
  const tokenField = document.getElementById('ds-token');
  const token = tokenField.style.display !== 'none' ? tokenField.value.trim() : '';
  const btn = document.getElementById('ds-start-btn');
  btn.disabled = true; btn.innerHTML = '<i class="ti ti-loader-2" style="animation:spin 1s linear infinite"></i> در حال اجرا...';
  document.getElementById('ds-log-box').style.display = 'block';
  try{
    const r = await authF('/api/bot-tcp-proxy/start', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ token, mode:'whitelist', target_domains: dsDomains })
    });
    if(!r.ok){ const d = await r.json().catch(()=>({})); throw new Error(d.detail || 'خطا'); }
    document.getElementById('ds-stop-btn').style.display = 'flex';
    dsPolling = setInterval(pollDomainScan, 1500);
  }catch(e){
    toast('✗ '+e.message,'err');
    btn.disabled = false; btn.innerHTML = '<i class="ti ti-player-play"></i> شروع اسکن';
  }
}
async function stopDomainScan(){
  await authF('/api/bot-tcp-proxy/stop', {method:'POST'});
  toast('درخواست توقف ارسال شد','ok');
}
async function pollDomainScan(){
  try{
    const r = await authF('/api/bot-tcp-proxy/status'), d = await r.json();
    const box = document.getElementById('ds-log-box');
    box.innerHTML = (d.logs||[]).map(l=>`<p class="upd-log-line">[${new Date(l.time*1000).toLocaleTimeString('fa-IR')}] ${esc(l.msg)}</p>`).join('') || '<p class="upd-log-empty">لاگی موجود نیست</p>';
    box.scrollTop = box.scrollHeight;
    const txt = document.getElementById('ds-status-text');
    if(d.running){
      txt.textContent = `در حال جستجو... (${d.attempts} تلاش)`;
    } else {
      clearInterval(dsPolling);
      document.getElementById('ds-stop-btn').style.display = 'none';
      const btn = document.getElementById('ds-start-btn');
      btn.disabled = false; btn.innerHTML = '<i class="ti ti-player-play"></i> شروع اسکن';
      if(d.result){
        txt.textContent = `پیدا شد: ${d.result.domain}:${d.result.port}`;
        toast('دامنه پیدا شد: '+d.result.domain+':'+d.result.port,'ok');
      } else if(d.error){
        txt.textContent = d.error;
      }
    }
  }catch(e){}
}
// آدرس Worker رو بعد از دیپلوی اینجا بذار (بخش ۳)
const SUGGEST_WORKER_URL = 'https://railway-tcp.arvin341az.workers.dev/suggest';

function openSuggestModal(prefill){
  document.getElementById('sg-domain').value = prefill || '';
  document.getElementById('sg-note').value = '';
  document.getElementById('sg-status-text').textContent = 'هنوز ارسال نشده';
  openModal('modal-suggest-domain');
}

async function submitDomainSuggestion(){
  const domain = document.getElementById('sg-domain').value.trim().toLowerCase();
  const note = document.getElementById('sg-note').value.trim();
  if(!domain){ toast('دامنه را وارد کن','err'); return; }
  const btn = document.getElementById('sg-submit-btn');
  btn.disabled = true;
  btn.innerHTML = '<i class="ti ti-loader-2" style="animation:spin 1s linear infinite"></i> در حال ارسال...';
  try{
    const r = await fetch(SUGGEST_WORKER_URL, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        domain, note,
        panel_host: location.host,
        sent_at: new Date().toISOString(),
      })
    });
    if(!r.ok) throw new Error('ارسال ناموفق بود');
    document.getElementById('sg-status-text').textContent = 'با موفقیت ارسال شد ✓';
    toast('پیشنهاد شما ارسال شد ✓','ok');
    setTimeout(()=>closeModal('modal-suggest-domain'), 900);
  }catch(e){
    toast('✗ '+e.message,'err');
  }
  btn.disabled = false;
  btn.innerHTML = '<i class="ti ti-send"></i> ارسال پیشنهاد';
}
async function downloadBackup(){
  try{
    const r = await authF('/api/backup/export');
    if(!r.ok) throw new Error('خطا در دریافت بکاپ');
    const blob = await r.blob();
    const cd = r.headers.get('Content-Disposition') || '';
    const m = cd.match(/filename="?([^"]+)"?/);
    const filename = m ? m[1] : 'rvg-backup.json';
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = filename;
    document.body.appendChild(a); a.click(); a.remove();
    URL.revokeObjectURL(url);
    toast('فایل بکاپ دانلود شد ✓','ok');
  }catch(e){ toast('✗ '+e.message,'err'); }
}

async function restoreBackup(){
  const inp = document.getElementById('restore-file');
  const file = inp.files[0];
  if(!file){ toast('فایل بکاپ را انتخاب کنید','err'); return; }
  if(!confirm('تمام اطلاعات فعلی پنل با فایل بکاپ جایگزین می‌شود. ادامه می‌دهید؟')) return;

  const btn = document.getElementById('restore-btn');
  btn.disabled = true;
  btn.innerHTML = '<i class="ti ti-loader-2" style="animation:spin 1s linear infinite"></i> در حال بازیابی...';

  try{
    const text = await file.text();
    let data;
    try{ data = JSON.parse(text); }catch(e){ throw new Error('فایل JSON معتبر نیست'); }
    const keepPw = !document.getElementById('restore-pw-tog').classList.contains('on');
    const r = await authF('/api/backup/import', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ data, keep_current_password: keepPw })
    });
    if(!r.ok){ const d = await r.json().catch(()=>({})); throw new Error(d.detail || 'خطا در بازیابی'); }
    const d = await r.json();
    toast('بازیابی موفق ✓ ('+toFa(d.links_count)+' کانفیگ، '+toFa(d.subs_count)+' گروه)','ok');
    inp.value = '';
    loadLinks(); loadSubs(); fetchStats();
  }catch(e){
    toast('✗ '+e.message,'err');
  }
  btn.disabled = false;
  btn.innerHTML = '<i class="ti ti-database-import"></i> شروع بازیابی';
}

// ══════════════════════════ نود ══════════════════════════
const NK_PERM_LABELS = {usage:'مصرف',links:'کانفیگ‌ها',subs:'ساب‌ها',requests:'درخواست‌ها',logs:'لاگ‌ها'};

function toggleNkPerm(el){
  el.classList.toggle('on');
}

function openNodeKeyModal(){
  document.getElementById('nk-label').value='';
  document.getElementById('nk-password').value='';
  document.getElementById('nk-result').style.display='none';
  document.getElementById('nk-key').textContent='—';
  document.querySelectorAll('#nk-perms .nk-perm-tile').forEach(el=>{
    const on = el.dataset.perm!=='logs' && el.dataset.perm!=='manage';
    el.classList.toggle('on', on);
  });
  const btn=document.getElementById('nk-gen-btn');
  btn.style.display='';btn.disabled=false;
  openModal('modal-node-key');
}

async function genNodeKey(){
  const label=document.getElementById('nk-label').value.trim();
  const share={};
  document.querySelectorAll('#nk-perms .nk-perm-tile').forEach(el=>{
    share[el.dataset.perm]=el.classList.contains('on');
  });
  const can_manage=!!share.manage; delete share.manage;
  const password=document.getElementById('nk-password').value;
  const btn=document.getElementById('nk-gen-btn');
  btn.disabled=true;
  try{
    const r=await authF('/api/nodes/keys',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({label,share,can_manage,password})});
    const d=await r.json();
    if(!r.ok) throw new Error(d.detail||'خطا در ساخت کلید');
    document.getElementById('nk-key').textContent=d.key;
    document.getElementById('nk-result').style.display='';
    btn.style.display='none';
    toast('کلید ساخته شد ✓','ok');
    loadNodeKeys();
  }catch(e){ toast(e.message||'خطا در ساخت کلید','err'); }
  finally{ btn.disabled=false; }
}

function renderNodeKeys(keys){
  document.getElementById('nk-cnt').textContent=toFa(keys.length);
  const list=document.getElementById('nk-list');
  if(!keys.length){ list.innerHTML='<div class="empty" style="padding:16px 0"><i class="ti ti-key-off"></i><p>هنوز کلیدی نساخته‌اید</p></div>'; return; }
  list.innerHTML = keys.map(k=>{
    const share = k.share||{};
    const chips = Object.keys(NK_PERM_LABELS).filter(p=>share[p]).map(p=>NK_PERM_LABELS[p]).join('، ') || 'هیچ‌کدام';
    const manageChip = k.can_manage ? ' <span class="exp-chip ec-warn"><i class="ti ti-edit"></i> ویرایش/حذف از راه دور</span>' : '';
    const stateChip = k.revoked ? '<span class="exp-chip ec-exp">غیرفعال</span>' : '<span class="exp-chip ec-ok">فعال</span>';
    const pwChip = k.has_password ? ' <span class="exp-chip ec-warn" title="برای اتصال به این کلید، رمز لازم است"><i class="ti ti-lock"></i> رمزدار</span>' : '';
    const meta = [
      k.use_count ? (toFa(k.use_count)+' بار استفاده') : null,
      k.peer_host ? ('آخرین اتصال از '+esc(k.peer_host)) : null,
    ].filter(Boolean).join(' · ');
    return `
    <div class="node-key-row ${k.revoked?'off':''}">
      <span class="node-key-dot"></span>
      <div class="node-key-body">
        <div class="node-key-label">${esc(k.label)} ${stateChip}${pwChip}</div>
        <div class="node-key-val" onclick="navigator.clipboard.writeText('${esc(k.key)}').then(()=>toast('کپی شد ✓','ok'))" title="برای کپی کلیک کنید"><i class="ti ti-copy"></i>${esc(k.key)}</div>
        <div class="node-key-state" title="دسترسی: ${esc(chips)}${meta?(' · '+esc(meta)):''}">${esc(chips)}${manageChip}${meta?(' · '+esc(meta)):''}</div>
      </div>
      <div class="node-key-actions">
        <button class="btn btn-o btn-sm btn-icon" onclick="setNodeKeyPassword('${k.key_id}',${k.has_password})" title="${k.has_password?'تغییر/حذف رمز':'قرار دادن رمز'}"><i class="ti ti-${k.has_password?'lock':'lock-open'}"></i></button>
        <button class="btn btn-o btn-sm btn-icon" onclick="toggleNodeKeyState('${k.key_id}',${k.revoked})" title="${k.revoked?'فعال‌سازی':'غیرفعال کردن'}"><i class="ti ti-${k.revoked?'player-play':'player-pause'}"></i></button>
        <button class="btn btn-d btn-sm btn-icon" onclick="deleteNodeKey('${k.key_id}')" title="حذف کامل"><i class="ti ti-trash"></i></button>
      </div>
    </div>`;
  }).join('');
}

async function loadNodeKeys(){
  try{
    const r=await authF('/api/nodes/keys');
    const d=await r.json();
    renderNodeKeys(d.keys||[]);
  }catch(e){}
}

async function toggleNodeKeyState(keyId,isRevoked){
  try{
    const r=await authF('/api/nodes/keys/'+keyId,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({enabled:isRevoked})});
    if(!r.ok) throw new Error();
    toast(isRevoked?'کلید فعال شد ✓':'کلید غیرفعال شد','ok');
    loadNodeKeys();
  }catch(e){ toast('خطا در تغییر وضعیت','err'); }
}

async function setNodeKeyPassword(keyId,hasPassword){
  const pw=prompt(hasPassword?'رمز جدید را وارد کنید (برای حذف رمز، خالی بگذارید و تایید کنید):':'رمز موردنظر را برای این کلید وارد کنید:','');
  if(pw===null) return;
  try{
    const r=await authF('/api/nodes/keys/'+keyId,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:pw})});
    if(!r.ok) throw new Error();
    toast(pw.trim()?'رمز تنظیم شد ✓':'رمز حذف شد ✓','ok');
    loadNodeKeys();
  }catch(e){ toast('خطا در تغییر رمز','err'); }
}

async function deleteNodeKey(keyId){
  if(!confirm('این کلید برای همیشه حذف شود؟ پنل متصل با این کلید دیگر دسترسی نخواهد داشت.')) return;
  try{
    const r=await authF('/api/nodes/keys/'+keyId,{method:'DELETE'});
    if(!r.ok) throw new Error();
    toast('کلید حذف شد ✓','ok');
    loadNodeKeys();
  }catch(e){ toast('خطا در حذف کلید','err'); }
}

function openNodeConnectModal(){
  document.getElementById('nc-key').value='';
  document.getElementById('nc-label').value='';
  document.getElementById('nc-password').value='';
  document.getElementById('nc-host-preview').textContent='—';
  ncSetError(null);
  openModal('modal-node-connect');
}

function previewNodeKey(){
  const raw=document.getElementById('nc-key').value.trim();
  const el=document.getElementById('nc-host-preview');
  if(!raw.startsWith('rvg-')||!raw.slice(4).includes('.')){ el.textContent='—'; return; }
  try{
    const hostPart=raw.slice(4).split('.')[0];
    let b64=hostPart.replace(/-/g,'+').replace(/_/g,'/');
    while(b64.length%4) b64+='=';
    const host=decodeURIComponent(escape(atob(b64)));
    el.textContent=host||'—';
  }catch(e){ el.textContent='—'; }
}

function ncSetError(msg){
  const el=document.getElementById('nc-error');
  if(!el) return;
  const span=el.querySelector('span');
  if(!msg){ el.style.display='none'; if(span)span.textContent=''; return; }
  if(span)span.textContent=msg;
  el.style.display='flex';
}
async function connectNode(){
  const key=document.getElementById('nc-key').value.trim();
  const label=document.getElementById('nc-label').value.trim();
  const password=document.getElementById('nc-password').value;
  ncSetError(null);
  if(!key){ toast('کلید را وارد کنید','err'); return; }
  const btn=document.getElementById('nc-btn');
  btn.disabled=true;
  try{
    const r=await authF('/api/nodes/connect',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key,label,password})},true);
    const d=await r.json().catch(()=>({}));
    if(!r.ok){
      let msg = d.detail||'اتصال برقرار نشد';
      if(d.detail==='PASSWORD_REQUIRED') msg='این نود دارای رمز عبور است؛ لطفاً رمز را وارد کنید';
      else if(d.detail==='PASSWORD_INVALID') msg='رمز عبور وارد شده اشتباه است';
      else if(r.status===401) msg='کلید یا رمز عبور معتبر نیست';
      ncSetError(msg);
      document.getElementById('nc-password').focus();
      return;
    }
    toast('به نود متصل شد ✓','ok');
    closeModal('modal-node-connect');
    document.getElementById('nc-key').value='';
    document.getElementById('nc-label').value='';
    document.getElementById('nc-password').value='';
    loadNodes();
  }catch(e){ ncSetError(e.message||'اتصال برقرار نشد'); }
  finally{ btn.disabled=false; }
}

function nodePermPill(node,part){
  const on = !!(node.share||{})[part];
  return `<div class="node-perm ${on?'on':''}" onclick='toggleNodeShare("${node.node_id}","${part}",this)'><div class="cfg-check ${on?'checked':''}"><i class="ti ti-check"></i></div> ${NK_PERM_LABELS[part]}</div>`;
}

function renderNodes(data){
  const nodes=data.nodes||[], totals=data.totals||{};
  document.getElementById('nodes-pg-cnt').textContent=toFa(nodes.length)+' نود';
  document.getElementById('nodes-online-txt').textContent=toFa(totals.nodes_online||0)+' از '+toFa(totals.nodes_total||0)+' آنلاین';
  document.getElementById('na-used').textContent=fmtB(totals.used_bytes||0);
  document.getElementById('na-used-sub').textContent='این پنل '+fmtB(totals.local_used_bytes||0)+' + نودها '+fmtB(totals.node_used_bytes||0);
  document.getElementById('na-links').textContent=toFa(totals.links||0);
  document.getElementById('na-links-sub').textContent='از '+toFa(totals.active_links||0)+' فعال';
  document.getElementById('na-subs').textContent=toFa(totals.subs||0);
  document.getElementById('na-reqs').textContent=toFa(totals.requests||0);

  const grid=document.getElementById('nodes-grid'), empty=document.getElementById('nodes-empty');
  if(!nodes.length){ grid.innerHTML=''; empty.style.display=''; return; }
  empty.style.display='none';
  grid.innerHTML = nodes.map(n=>{
    const off = n.disabled || !n.enabled;
    const err = !off && !n.online;
    const stat = n.stats||{};
    const statusChip = n.online?'<span class="exp-chip ec-ok"><i class="ti ti-circle-check" style="font-size:9px"></i> آنلاین</span>':(off?'<span class="exp-chip ec-exp">غیرفعال</span>':'<span class="exp-chip ec-warn">آفلاین</span>');
    return `
    <div class="node-card ${off?'is-off':''} ${err?'is-err':''}">
      <div class="node-card-bar"></div>
      <div class="node-card-body">
        <div class="node-head">
          <div class="node-avatar ${n.online?'online':''}"><i class="ti ti-topology-star-3"></i><span class="node-avatar-dot"></span></div>
          <div class="node-titles">
            <div class="node-name">${esc(n.label)} ${statusChip}</div>
            <div class="node-host" onclick="navigator.clipboard.writeText('${esc(n.host)}').then(()=>toast('کپی شد ✓','ok'))" title="برای کپی کلیک کنید"><i class="ti ti-server-2"></i>${esc(n.host)}</div>
            <div class="node-meta"><i class="ti ti-refresh"></i>${n.last_sync_at?('همگام‌سازی: '+esc(n.last_sync_at.slice(0,19).replace('T',' '))):'هنوز همگام نشده'}</div>
          </div>
        </div>
        ${n.error?`<div class="node-err"><i class="ti ti-alert-triangle"></i><span>${esc(n.error)}</span></div>`:''}
        <div class="node-stats">
          <div class="node-stat"><i class="ti ti-transfer"></i><div class="node-stat-val">${fmtB((stat.total_bytes)||0)}</div><div class="node-stat-label">مصرف</div></div>
          <div class="node-stat"><i class="ti ti-arrows-exchange"></i><div class="node-stat-val">${toFa(stat.active_connections||0)}</div><div class="node-stat-label">اتصال فعال</div></div>
          <div class="node-stat"><i class="ti ti-link"></i><div class="node-stat-val">${toFa(stat.links_count||0)}</div><div class="node-stat-label">کانفیگ</div></div>
        </div>
        <div class="node-perms">
          ${['usage','links','subs','requests','logs'].map(p=>nodePermPill(n,p)).join('')}
        </div>
      </div>
      <div class="node-foot">
        <button class="btn btn-o btn-sm" onclick="toggleNodeEnabled('${n.node_id}',${n.enabled===false})"><i class="ti ti-${n.enabled===false?'player-play':'player-pause'}"></i> ${n.enabled===false?'فعال‌سازی':'غیرفعال'}</button>
        <button class="btn btn-d btn-sm" onclick="disconnectNode('${n.node_id}')"><i class="ti ti-plug-connected-x"></i> قطع اتصال</button>
      </div>
    </div>`;
  }).join('');
}

async function toggleNodeShare(nodeId,part,el){
  const willOn = !el.querySelector('.cfg-check').classList.contains('checked');
  el.querySelector('.cfg-check').classList.toggle('checked',willOn);
  el.classList.toggle('on',willOn);
  try{
    const r=await authF('/api/nodes/'+nodeId,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({share:{[part]:willOn}})});
    if(!r.ok) throw new Error();
  }catch(e){ toast('خطا در ذخیره تنظیمات','err'); loadNodes(); }
}

async function toggleNodeEnabled(nodeId,enable){
  try{
    const r=await authF('/api/nodes/'+nodeId,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({enabled:enable})});
    if(!r.ok) throw new Error();
    toast(enable?'نود فعال شد ✓':'نود غیرفعال شد','ok');
    loadNodes();
  }catch(e){ toast('خطا در تغییر وضعیت','err'); }
}

async function disconnectNode(nodeId){
  if(!confirm('اتصال به این نود قطع شود؟')) return;
  try{
    const r=await authF('/api/nodes/'+nodeId,{method:'DELETE'});
    if(!r.ok) throw new Error();
    toast('اتصال قطع شد ✓','ok');
    loadNodes();
  }catch(e){ toast('خطا در قطع اتصال','err'); }
}

async function loadNodes(fresh){
  try{
    const r=await authF('/api/nodes/aggregate'+(fresh?'?fresh=1':''));
    const d=await r.json();
    renderNodes(d);
  }catch(e){}
}

function loadNodesPage(){ loadNodeKeys(); loadNodes(); }
</script>
</body></html>"""


def get_public_page_html(uuid_key: str) -> str:
    """صفحه پابلیک ساب v3 — طراحی حرفه‌ای‌تر با هدرهای مناسب برای برنامه‌های خارجی + نوار مصرف کل"""
    return f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>RVG Sub · codebox</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.19.0/dist/tabler-icons.min.css">
<style>
*{{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}}
:root{{
  --bg:#060a14;--bg2:#0a1020;--bg3:#0d1428;
  --card:#0c1326;--card-b:rgba(96,148,246,0.12);--card-bh:rgba(96,148,246,0.28);
  --accent:#3B7CF6;--accent2:#6EA3FF;--accent-d:rgba(59,124,246,0.1);
  --green:#1FB87E;--green-bg:rgba(31,184,126,0.1);--green-t:#3FD79C;
  --red:#EF4444;--red-bg:rgba(239,68,68,0.1);--red-t:#FB8585;
  --amber:#F2A33D;--amber-bg:rgba(242,163,61,0.1);--amber-t:#F9C988;
  --purple:#9D7BF0;--purple-bg:rgba(157,123,240,0.1);--purple-t:#BCA4F7;
  --t1:#EFF4FF;--t2:#8AA0C4;--t3:#48577A;
  --radius:18px;--shadow:0 12px 40px rgba(0,0,0,0.45);
  --serif:'Vazirmatn',sans-serif;
}}
[data-theme="light"]{{
  --bg:#F0F3FA;--bg2:#E5ECF8;--bg3:#D9E3F4;
  --card:#FFFFFF;--card-b:rgba(59,124,246,0.14);--card-bh:rgba(59,124,246,0.32);
  --accent:#2E63D6;--accent2:#1E4CB8;--accent-d:rgba(46,99,214,0.08);
  --green:#0E9A6A;--green-bg:rgba(14,154,106,0.08);--green-t:#0A7553;
  --red:#DC2626;--red-bg:rgba(220,38,68,0.08);--red-t:#A51E1E;
  --amber:#C97A12;--amber-bg:rgba(201,122,18,0.08);--amber-t:#8F5A0C;
  --purple:#7350D6;--purple-bg:rgba(115,80,214,0.08);--purple-t:#5A3CAD;
  --t1:#101A30;--t2:#48577A;--t3:#8694B0;
  --shadow:0 12px 36px rgba(20,40,90,0.12);
}}
html,body{{min-height:100%;background:var(--bg);font-family:var(--serif);color:var(--t1);font-size:14px;transition:background .35s,color .35s}}
.bg-fx{{position:fixed;inset:0;background:radial-gradient(ellipse 70% 45% at 50% -8%,rgba(59,124,246,0.13),transparent 62%),var(--bg);z-index:0;pointer-events:none;transition:background .35s}}
.grid-fx{{position:fixed;inset:0;background-image:linear-gradient(rgba(96,148,246,0.025) 1px,transparent 1px),linear-gradient(90deg,rgba(96,148,246,0.025) 1px,transparent 1px);background-size:46px 46px;z-index:0;pointer-events:none}}
.wrap{{position:relative;z-index:10;max-width:800px;margin:0 auto;padding:24px 16px 64px}}
.top{{display:flex;align-items:center;justify-content:space-between;margin-bottom:26px;gap:10px}}
.brand{{display:flex;align-items:center;gap:11px;min-width:0}}
.brand-img{{width:40px;height:40px;border-radius:12px;overflow:hidden;border:1px solid var(--card-b);box-shadow:0 0 0 1px rgba(255,255,255,.02);flex-shrink:0}}
.brand-img img{{width:100%;height:100%;object-fit:cover}}
.brand-name{{font-size:14.5px;font-weight:800;color:var(--t1);letter-spacing:-.01em}}
.brand-sub{{font-size:9.5px;color:var(--t3);font-weight:500}}
.top-actions{{display:flex;align-items:center;gap:6px;flex-shrink:0}}
.icon-btn{{width:36px;height:36px;border-radius:11px;background:var(--card);border:1px solid var(--card-b);color:var(--t2);display:flex;align-items:center;justify-content:center;font-size:16px;cursor:pointer;transition:.18s}}
.icon-btn:hover{{background:var(--accent-d);color:var(--accent2);border-color:var(--card-bh)}}

.sub-info{{background:var(--card);border:1px solid var(--card-b);border-radius:22px;padding:24px 24px 22px;margin-bottom:16px;box-shadow:var(--shadow);position:relative;overflow:hidden}}
.sub-info::before{{content:'';position:absolute;top:0;right:0;width:160px;height:160px;background:radial-gradient(circle at top right,rgba(59,124,246,.1),transparent 70%);pointer-events:none}}
.sub-eyebrow{{font-size:10px;font-weight:700;color:var(--accent2);text-transform:uppercase;letter-spacing:.12em;margin-bottom:8px;display:flex;align-items:center;gap:6px}}
.sub-eyebrow i{{font-size:13px}}
.sub-name{{font-size:23px;font-weight:800;color:var(--t1);margin-bottom:6px;letter-spacing:-.02em}}
.sub-desc{{font-size:12.5px;color:var(--t2);line-height:1.8;margin-bottom:14px}}
.sub-meta-row{{font-size:10.5px;color:var(--t3);margin-bottom:14px;display:flex;align-items:center;gap:6px}}
.sub-sub-box{{background:var(--accent-d);border:1px solid var(--card-b);border-radius:13px;padding:12px 14px;display:flex;align-items:center;gap:9px;flex-wrap:wrap}}
.sub-sub-url{{font-family:ui-monospace,monospace;font-size:10px;color:var(--accent2);word-break:break-all;flex:1;min-width:140px}}

/* ══════ نوار مصرف کل — بخش جدید ══════ */
.total-usage-box{{background:rgba(0,0,0,.14);border:1px solid var(--card-b);border-radius:13px;padding:14px 16px;margin-top:12px}}
[data-theme="light"] .total-usage-box{{background:rgba(46,99,214,.03)}}
.tu-head{{display:flex;align-items:center;justify-content:space-between;margin-bottom:9px;gap:8px;flex-wrap:wrap}}
.tu-label{{font-size:10.5px;color:var(--t2);font-weight:700;display:flex;align-items:center;gap:6px}}
.tu-label i{{color:var(--accent2);font-size:14px}}
.tu-val{{font-size:11.5px;font-weight:800;color:var(--t1);font-family:ui-monospace,monospace}}
.tu-bar{{height:9px;border-radius:6px;background:rgba(96,148,246,0.12);overflow:hidden;position:relative}}
.tu-bar-f{{height:100%;border-radius:6px;transition:width .6s ease;position:relative;overflow:hidden}}
.tu-bar-f::after{{content:'';position:absolute;inset:0;background:linear-gradient(90deg,transparent,rgba(255,255,255,.35),transparent);width:40%;animation:tuShimmer 1.8s linear infinite}}
@keyframes tuShimmer{{0%{{transform:translateX(-120%)}}100%{{transform:translateX(280%)}}}}
.tu-foot{{display:flex;justify-content:space-between;margin-top:7px;font-size:9.5px;color:var(--t3)}}
.tu-pct{{font-weight:800}}

.stats-bar{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:18px}}
.stat-card{{background:var(--card);border:1px solid var(--card-b);border-radius:16px;padding:16px 17px;transition:.2s}}
.stat-card:hover{{border-color:var(--card-bh);transform:translateY(-1px)}}
.stat-label{{font-size:9px;color:var(--t3);font-weight:700;text-transform:uppercase;letter-spacing:.07em;margin-bottom:7px}}
.stat-val{{font-size:22px;font-weight:800;color:var(--t1);line-height:1;letter-spacing:-.01em}}
.stat-sub{{font-size:9.5px;color:var(--t3);margin-top:6px}}

.copy-all-bar{{display:flex;align-items:center;gap:12px;background:linear-gradient(120deg,var(--accent) 0%,#2952C8 100%);border-radius:18px;padding:16px 19px;margin-bottom:18px;box-shadow:0 10px 30px rgba(59,124,246,.28);flex-wrap:wrap}}
.copy-all-text{{flex:1;min-width:160px}}
.copy-all-title{{font-size:13.5px;font-weight:800;color:#fff;display:flex;align-items:center;gap:6px}}
.copy-all-sub{{font-size:10px;color:rgba(255,255,255,.78);margin-top:3px}}
.copy-all-btn{{background:#fff;color:#1D4ED8;border:none;border-radius:12px;padding:10px 19px;font-family:inherit;font-size:12.5px;font-weight:800;cursor:pointer;display:flex;align-items:center;gap:6px;transition:.18s;white-space:nowrap}}
.copy-all-btn:hover{{transform:translateY(-1px);box-shadow:0 6px 16px rgba(0,0,0,.22)}}
.copy-all-btn:active{{transform:translateY(0) scale(.98)}}

.cfg-title{{font-size:12px;font-weight:800;color:var(--t2);margin-bottom:13px;display:flex;align-items:center;gap:6px;text-transform:uppercase;letter-spacing:.07em}}
.cfg-title i{{color:var(--accent);font-size:15px}}
.cfg-grid{{display:grid;gap:13px}}

.cfg-card{{background:var(--card);border:1px solid var(--card-b);border-radius:18px;transition:all .2s;position:relative;overflow:hidden}}
.cfg-card:hover{{border-color:var(--card-bh);box-shadow:var(--shadow)}}
.cfg-top{{padding:17px 19px 15px;position:relative}}
.cfg-top::after{{content:'';position:absolute;top:0;right:0;width:3px;height:100%;background:var(--green)}}
.cfg-card.inactive .cfg-top::after{{background:var(--red)}}
.cfg-head{{display:flex;align-items:flex-start;justify-content:space-between;gap:8px;margin-bottom:12px;flex-wrap:wrap}}
.cfg-label{{font-size:14.5px;font-weight:700;color:var(--t1)}}
.cfg-badges{{display:flex;gap:5px;flex-wrap:wrap;margin-top:6px}}
.proto-chip{{font-size:9px;padding:3px 8px;border-radius:7px;font-weight:800;letter-spacing:.02em}}
.pc-ws{{background:var(--accent-d);color:var(--accent2)}}
.pc-trojan{{background:var(--purple-bg);color:#A78BFA}}
.pc-xhttp{{background:var(--purple-bg);color:var(--purple-t)}}
.pc-ultra{{background:var(--green-bg);color:var(--green-t)}}
.pc-ss{{background:var(--purple-bg);color:#A78BFA}}
.cfg-status{{display:flex;align-items:center;gap:5px;font-size:10px;font-weight:700;padding:4px 10px;border-radius:20px;white-space:nowrap}}
.cfg-status.ok{{background:var(--green-bg);color:var(--green-t)}}
.cfg-status.no{{background:var(--red-bg);color:var(--red-t)}}
.cfg-usage{{margin-bottom:4px}}
.ubar{{height:6px;border-radius:4px;background:rgba(96,148,246,0.1);overflow:hidden;margin-bottom:5px;min-width:100%}}
.ubar-f{{height:100%;border-radius:4px;transition:width .5s ease;min-width:2px}}
.utxt{{font-size:10px;color:var(--t3);display:flex;justify-content:space-between;gap:8px}}

.cfg-tear{{position:relative;height:0;border-top:1.5px dashed var(--card-b);margin:0 19px}}
.cfg-tear::before,.cfg-tear::after{{content:'';position:absolute;top:50%;width:18px;height:18px;border-radius:50%;background:var(--bg);transform:translateY(-50%);border:1px solid var(--card-b)}}
.cfg-tear::before{{right:-28px}}
.cfg-tear::after{{left:-28px}}

.cfg-bottom{{padding:15px 19px 18px}}
.cfg-link-toggle{{width:100%;display:flex;align-items:center;justify-content:space-between;gap:10px;background:transparent;border:1px dashed var(--card-b);border-radius:11px;padding:10px 13px;cursor:pointer;font-family:inherit;color:var(--t2);font-size:11.5px;font-weight:600;transition:.15s}}
.cfg-link-toggle:hover{{background:var(--accent-d);border-color:var(--card-bh);color:var(--accent2)}}
.cfg-link-toggle .ltl{{display:flex;align-items:center;gap:7px}}
.cfg-link-toggle i.ti-chevron-down{{transition:transform .2s}}
.cfg-link-toggle.open i.ti-chevron-down{{transform:rotate(180deg)}}
.cfg-vless-wrap{{display:grid;grid-template-rows:0fr;transition:grid-template-rows .25s ease}}
.cfg-vless-wrap.open{{grid-template-rows:1fr}}
.cfg-vless-inner{{overflow:hidden}}
.cfg-vless{{background:rgba(0,0,0,.22);border:1px solid var(--card-b);border-radius:10px;padding:11px 13px;font-size:9.8px;font-family:ui-monospace,monospace;color:var(--accent2);word-break:break-all;line-height:1.7;margin-top:9px;max-height:90px;overflow-y:auto}}
[data-theme="light"] .cfg-vless{{background:rgba(46,99,214,.05)}}
.cfg-actions{{display:flex;gap:7px;flex-wrap:wrap;margin-top:11px}}
.btn{{font-family:inherit;font-size:11.5px;font-weight:700;border-radius:10px;padding:8px 15px;cursor:pointer;display:inline-flex;align-items:center;gap:5px;border:none;transition:all .15s;white-space:nowrap}}
.btn i{{font-size:13px}}
.btn-p{{background:var(--accent);color:#fff;box-shadow:0 3px 12px rgba(59,124,246,.3)}}
.btn-p:hover{{background:var(--accent2)}}
.btn-g{{background:var(--accent-d);color:var(--accent2);border:1px solid rgba(96,148,246,.16)}}
.btn-g:hover{{background:rgba(96,148,246,.2)}}
.btn-pur{{background:var(--purple-bg);color:var(--purple-t);border:1px solid rgba(157,123,240,.2)}}
.btn-pur:hover{{background:rgba(157,123,240,.22)}}
.conn-chip{{display:inline-flex;align-items:center;gap:4px;font-size:9.5px;padding:3px 8px;border-radius:20px;background:var(--green-bg);color:var(--green-t);font-weight:700}}
.dot{{width:5px;height:5px;border-radius:50%;background:var(--green);display:inline-block;animation:pulse 2s infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.25}}}}

.lock-stage{{display:flex;align-items:center;justify-content:center;min-height:78vh;padding:20px 0}}
.lock-card{{background:var(--card);border:1px solid var(--card-b);border-radius:26px;padding:0;text-align:center;max-width:380px;width:100%;box-shadow:var(--shadow);overflow:hidden;position:relative}}
.lock-banner{{background:linear-gradient(150deg,rgba(59,124,246,.16),rgba(59,124,246,.02) 70%);padding:38px 30px 26px;position:relative}}
.lock-shield{{width:64px;height:64px;border-radius:18px;background:var(--accent-d);border:1px solid var(--card-bh);display:flex;align-items:center;justify-content:center;margin:0 auto 18px;position:relative}}
.lock-shield::after{{content:'';position:absolute;inset:-7px;border-radius:22px;border:1px solid var(--card-b);animation:breathe 2.6s ease-in-out infinite}}
@keyframes breathe{{0%,100%{{transform:scale(1);opacity:.5}}50%{{transform:scale(1.08);opacity:0}}}}
.lock-shield i{{font-size:28px;color:var(--accent2)}}
.lock-title{{font-size:18px;font-weight:800;margin-bottom:6px;color:var(--t1);letter-spacing:-.01em}}
.lock-sub{{font-size:12px;color:var(--t3);line-height:1.7}}
.lock-form{{padding:24px 30px 30px}}
.lock-field{{position:relative;margin-bottom:13px}}
.lock-inp{{width:100%;padding:13px 44px 13px 44px;border-radius:13px;border:1px solid var(--card-b);background:rgba(0,0,0,.2);color:var(--t1);font-family:inherit;font-size:14px;outline:none;text-align:center;letter-spacing:.14em;transition:.18s}}
[data-theme="light"] .lock-inp{{background:rgba(46,99,214,.04)}}
.lock-inp:focus{{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-d)}}
.lock-eye{{position:absolute;left:13px;top:50%;transform:translateY(-50%);background:none;border:none;color:var(--t3);cursor:pointer;font-size:16px;padding:4px;display:flex}}
.lock-eye:hover{{color:var(--accent2)}}
.lock-lockicon{{position:absolute;right:14px;top:50%;transform:translateY(-50%);color:var(--t3);font-size:15px;pointer-events:none}}
.lock-err{{color:var(--red-t);font-size:11.5px;margin-bottom:10px;min-height:16px;display:flex;align-items:center;justify-content:center;gap:5px}}
.lock-btn{{width:100%;justify-content:center;padding:13px;font-size:13px;border-radius:13px}}
.lock-footer{{padding:14px 30px;border-top:1px solid var(--card-b);font-size:10px;color:var(--t3);display:flex;align-items:center;justify-content:center;gap:6px}}

.empty-state{{text-align:center;padding:80px 20px;color:var(--t3)}}
.empty-state i{{font-size:38px;display:block;margin-bottom:14px}}

.toast{{position:fixed;bottom:22px;left:50%;transform:translateX(-50%) translateY(40px);background:var(--card);border:1px solid var(--card-b);color:var(--t1);border-radius:12px;padding:10px 20px;font-size:12.5px;font-weight:600;opacity:0;transition:all .25s;z-index:999;pointer-events:none;display:flex;align-items:center;gap:7px;box-shadow:var(--shadow);white-space:nowrap}}
.toast.show{{opacity:1;transform:translateX(-50%) translateY(0)}}
.toast.ok{{border-color:rgba(31,184,126,.35);background:var(--green-bg);color:var(--green-t)}}

.qr-modal{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.72);z-index:600;align-items:center;justify-content:center;backdrop-filter:blur(6px);padding:20px}}
.qr-modal.open{{display:flex}}
.qr-box{{background:var(--card);border:1px solid var(--card-b);border-radius:22px;padding:26px;text-align:center;max-width:340px;width:100%;box-shadow:var(--shadow)}}
.qr-title{{font-size:13.5px;font-weight:800;margin-bottom:16px;color:var(--t1)}}
.qr-img{{border-radius:14px;overflow:hidden;margin-bottom:15px}}
.qr-img img{{width:100%;display:block;background:#fff;padding:10px;border-radius:14px}}

.footer{{text-align:center;padding-top:28px;font-size:10.5px;color:var(--t3)}}
.footer a{{color:var(--accent2);font-weight:700}}

@media(max-width:520px){{
  .stats-bar{{grid-template-columns:1fr 1fr}}
  .stats-bar .stat-card:nth-child(3){{grid-column:1/-1}}
  .sub-name{{font-size:19px}}
  .copy-all-bar{{flex-direction:column;align-items:stretch}}
  .copy-all-btn{{justify-content:center}}
  .wrap{{padding:16px 12px 50px}}
  .lock-banner{{padding:32px 22px 22px}}
  .lock-form{{padding:20px 22px 26px}}
}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
</style>
</head>
<body>
<div class="bg-fx"></div><div class="grid-fx"></div>
<div class="toast" id="toast"></div>
<div class="qr-modal" id="qr-modal" onclick="this.classList.remove('open')">
  <div class="qr-box" onclick="event.stopPropagation()">
    <div class="qr-title" id="qr-label">QR Code</div>
    <div class="qr-img"><img id="qr-img" src="" alt="QR"></div>
    <button class="btn btn-g" style="width:100%;justify-content:center" onclick="document.getElementById('qr-modal').classList.remove('open')"><i class="ti ti-x"></i> بستن</button>
  </div>
</div>
<div class="wrap">
  <div class="top">
    <div class="brand">
      <div class="brand-img"><img src="https://yt3.googleusercontent.com/vA6bYj1V386YmibpWRNFJtsRRqwfY_U9wnb7gmW90eRVXyNB7gAfjj1XPs5UX0cdKdQprrI=s160-c-k-c0x00ffffff-no-rj" alt="cb"></div>
      <div><div class="brand-name">codebox</div><div class="brand-sub">RVG Gateway · v9.2</div></div>
    </div>
    <div class="top-actions">
      <button class="icon-btn" id="theme-toggle" onclick="toggleTheme()" title="تغییر تم"><i class="ti ti-sun" id="theme-icon"></i></button>
      <a class="icon-btn" href="https://t.me/CodeBoxo" target="_blank" title="کانال تلگرام"><i class="ti ti-brand-telegram"></i></a>
    </div>
  </div>
  <div id="root">
    <div class="empty-state"><i class="ti ti-loader-2" style="animation:spin 1s linear infinite"></i>در حال بارگذاری...</div>
  </div>
  <div class="footer">کانال رسمی: <a href="https://t.me/CodeBoxo" target="_blank">@CodeBoxo</a> · RVG Gateway v9.2</div>
</div>
<script>
const UUID_KEY='{uuid_key}';
let savedPw='';

let SUB_DATA = {{
  total_used: 0,
  total_limit: 0,
  expiry_date: null,
  links: []
}};

let isDark=localStorage.getItem('rvg-pub-theme')!=='light';
function applyTheme(dark){{
  document.documentElement.setAttribute('data-theme',dark?'dark':'light');
  document.getElementById('theme-icon').className='ti '+(dark?'ti-sun':'ti-moon');
}}
function toggleTheme(){{isDark=!isDark;localStorage.setItem('rvg-pub-theme',isDark?'dark':'light');applyTheme(isDark)}}
applyTheme(isDark);

function toast(msg,type=''){{
  const t=document.getElementById('toast');
  t.textContent=msg;t.className='toast show'+(type?' '+type:'');
  setTimeout(()=>t.classList.remove('show'),2400);
}}
function esc(s){{return String(s||'').replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]))}}
function fmtB(b){{if(!b||b===0)return '0 B';if(b<1024)return b+' B';if(b<1024**2)return (b/1024).toFixed(1)+' KB';if(b<1024**3)return (b/1024**2).toFixed(2)+' MB';return (b/1024**3).toFixed(2)+' GB'}}
function toFa(n){{return String(n).replace(/\\d/g,d=>'۰۱۲۳۴۵۶۷۸۹'[d])}}
function protoChip(p){{
  p = p || 'vless-ws';
  if(p==='mtproto')return '<span class="proto-chip pc-trojan"><i class="ti ti-brand-telegram"></i> Telegram Proxy</span>';
  if(p.startsWith('shadowsocks')){{
    const isWsVariant = p !== 'shadowsocks';
    return '<span class="proto-chip pc-ss"><i class="ti ti-shield-lock-filled"></i> Shadowsocks'+(isWsVariant?' · '+esc(p.replace('shadowsocks-','')):'')+'</span>';
  }}
  if(p.startsWith('trojan'))return '<span class="proto-chip pc-trojan"><i class="ti ti-shield-lock"></i> '+esc(p)+'</span>';
  if(p.startsWith('xhttp'))return '<span class="proto-chip pc-xhttp">'+esc(p)+'</span>';
  return '<span class="proto-chip pc-ws">VLESS · WS</span>';
}}

function showQR(label,link){{
  document.getElementById('qr-label').textContent=label;
  document.getElementById('qr-img').src='https://api.qrserver.com/v1/create-qr-code/?size=260x260&data='+encodeURIComponent(link);
  document.getElementById('qr-modal').classList.add('open');
}}

function toggleLink(i){{
  const wrap=document.getElementById('vw-'+i);
  const btn=document.getElementById('vt-'+i);
  const open=wrap.classList.toggle('open');
  btn.classList.toggle('open',open);
  btn.querySelector('.ltl span').textContent = open ? 'پنهان کردن لینک' : 'نمایش لینک کانفیگ';
}}

async function loadData(pw=''){{
  const url='/api/public/sub/'+UUID_KEY+(pw?'?pw='+encodeURIComponent(pw):'');
  const r=await fetch(url);
  const data = await r.json();

  if (data.total_used !== undefined) {{
    SUB_DATA.total_used = data.total_used;
  }}
  if (data.total_limit !== undefined) {{
    SUB_DATA.total_limit = data.total_limit;
  }}
  if (data.expiry_date !== undefined) {{
    SUB_DATA.expiry_date = data.expiry_date;
  }}
  if (data.links) {{
    SUB_DATA.links = data.links;
  }}

  return data;
}}

function renderLock(name,errMsg=''){{
  document.getElementById('root').innerHTML=`
    <div class="lock-stage">
      <div class="lock-card">
        <div class="lock-banner">
          <div class="lock-shield"><i class="ti ti-shield-lock"></i></div>
          <div class="lock-title">${{esc(name)}}</div>
          <div class="lock-sub">این گروه با رمز محافظت شده. برای دیدن کانفیگ‌ها رمز رو وارد کنید.</div>
        </div>
        <div class="lock-form">
          <div class="lock-err" id="lock-err">${{errMsg ? '<i class="ti ti-alert-circle"></i> '+esc(errMsg) : ''}}</div>
          <div class="lock-field">
            <i class="ti ti-lock lock-lockicon"></i>
            <input class="lock-inp" type="password" id="lock-pw" placeholder="••••••••" autofocus>
            <button class="lock-eye" type="button" onclick="togglePwVis()"><i class="ti ti-eye" id="lock-eye-icon"></i></button>
          </div>
          <button class="btn btn-p lock-btn" onclick="submitLock()"><i class="ti ti-lock-open"></i> ورود به گروه</button>
        </div>
        <div class="lock-footer"><i class="ti ti-shield-check"></i> اتصال شما رمزنگاری‌شده است</div>
      </div>
    </div>
  `;
  const inp=document.getElementById('lock-pw');
  inp.addEventListener('keydown',e=>{{if(e.key==='Enter')submitLock()}});
}}
 
function togglePwVis(){{
  const inp=document.getElementById('lock-pw');
  const icon=document.getElementById('lock-eye-icon');
  const toText = inp.type==='password';
  inp.type = toText ? 'text' : 'password';
  icon.className = 'ti '+(toText ? 'ti-eye-off' : 'ti-eye');
}}

async function submitLock(){{
  const pw=document.getElementById('lock-pw').value;
  const data=await loadData(pw);
  if(data.locked){{renderLock(data.name,'رمز اشتباه است');return}}
  savedPw=pw;
  renderContent(data);
}}

function renderContent(d){{
  const activeCount=d.links.filter(l=>l.active).length;
  const baseSubUrl = d.sub_url || (window.location.protocol + '//' + window.location.host + '/sub-group/' + UUID_KEY);
  const subUrl = baseSubUrl + (savedPw ? '?pw=' + encodeURIComponent(savedPw) : '');

  // محاسبه کل مصرف و تاریخ انقضا
  // نکته: totalLimit فقط روی کانفیگ‌هایی جمع می‌شود که سهمیه محدود دارند (limit_bytes > 0)
  // در غیر این‌صورت یک کانفیگ نامحدود، سقف کل گروه را کاذب بی‌نهایت/گمراه‌کننده می‌کرد.
  let totalUsed = 0;
  let totalLimit = 0;
  let hasUnlimited = false;
  let expiryDate = null;

  d.links.forEach(l => {{
    totalUsed += (l.used_bytes || 0);
    if (l.limit_bytes && l.limit_bytes > 0) {{
      totalLimit += l.limit_bytes;
    }} else {{
      hasUnlimited = true;
    }}
    if (l.expiry_date && (!expiryDate || new Date(l.expiry_date) < new Date(expiryDate))) {{
      expiryDate = l.expiry_date;
    }}
  }});

  SUB_DATA.total_used = totalUsed;
  SUB_DATA.total_limit = totalLimit;
  SUB_DATA.expiry_date = expiryDate;

  window._rvgSubUrl  = subUrl;
  window._rvgSubName = d.name;
  window._rvgLinks   = d.links.map(l => ({{
    vless : l.vless_link,
    sub   : l.sub_url + (savedPw ? '?pw=' + encodeURIComponent(savedPw) : ''),
    label : l.label,
    used_bytes: l.used_bytes || 0,
    limit_bytes: l.limit_bytes || 0,
    expiry_date: l.expiry_date || null
  }}));

  // ── نوار مصرف کل ──
  // اگر حداقل یک کانفیگ نامحدود در گروه باشد، درصد را بر اساس همان سقف محدودها نشان می‌دهیم
  // ولی برچسب "+ شامل کانفیگ نامحدود" اضافه می‌کنیم تا گمراه‌کننده نباشد.
  const tuPct = totalLimit > 0 ? Math.min(100, (totalUsed / totalLimit) * 100) : 0;
  const tuColor = tuPct > 90 ? 'var(--red)' : tuPct > 70 ? 'var(--amber)' : 'var(--green)';
  const tuLimitTxt = totalLimit > 0 ? fmtB(totalLimit) + (hasUnlimited ? ' + نامحدود' : '') : 'نامحدود';
  const totalUsageHtml = `
    <div class="total-usage-box">
      <div class="tu-head">
        <span class="tu-label"><i class="ti ti-chart-donut-2"></i> مصرف کل گروه</span>
        <span class="tu-val">${{fmtB(totalUsed)}} <span style="color:var(--t3);font-weight:600"> / ${{tuLimitTxt}}</span></span>
      </div>
      <div class="tu-bar"><div class="tu-bar-f" style="width:${{totalLimit>0?tuPct:100}}%;background:${{totalLimit>0?tuColor:'var(--accent)'}}"></div></div>
      <div class="tu-foot">
        <span>${{totalLimit>0?('<span class=\\'tu-pct\\'>'+tuPct.toFixed(1)+'%</span> مصرف‌شده'):'بدون سقف کل (شامل کانفیگ نامحدود)'}}</span>
        <span>${{toFa(d.links.length)}} کانفیگ</span>
      </div>
    </div>`;

  document.getElementById('root').innerHTML=`
    <div class="sub-info">
      <div class="sub-eyebrow"><i class="ti ti-folders"></i> گروه دسترسی</div>
      <div class="sub-name">${{esc(d.name)}}</div>
      ${{d.desc ? `<div class="sub-desc">${{esc(d.desc)}}</div>` : ''}}
      <div class="sub-meta-row"><i class="ti ti-clock"></i> آخرین بروزرسانی: ${{new Date().toLocaleTimeString('fa-IR')}}</div>
      <div class="sub-sub-box">
        <span class="sub-sub-url">${{esc(subUrl)}}</span>
        <button class="btn btn-pur" style="padding:7px 12px;font-size:10.5px"
          onclick="navigator.clipboard.writeText(window._rvgSubUrl).then(()=>toast('لینک ساب کپی شد ✓','ok'))">
          <i class="ti ti-copy"></i> کپی لینک ساب
        </button>
        <button class="btn btn-g" style="padding:7px 12px;font-size:10.5px"
          onclick="showQR(window._rvgSubName + ' — کل گروه', window._rvgSubUrl)">
          <i class="ti ti-qrcode"></i> QR کل
        </button>
      </div>
      ${{totalUsageHtml}}
    </div>

    <div class="copy-all-bar">
      <div class="copy-all-text">
        <div class="copy-all-title"><i class="ti ti-copy"></i> کپی همه‌ی کانفیگ‌ها</div>
        <div class="copy-all-sub">تمام لینک‌های فعال این گروه را یک‌جا کپی کن</div>
      </div>
      <button class="copy-all-btn" onclick="copyAllConfigs()"><i class="ti ti-clipboard-copy"></i> کپی همه (${{toFa(activeCount)}})</button>
    </div>

    <div class="stats-bar">
      <div class="stat-card">
        <div class="stat-label">کانفیگ‌های فعال</div>
        <div class="stat-val">${{toFa(activeCount)}}</div>
        <div class="stat-sub">از ${{toFa(d.links.length)}} کانفیگ</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">اتصالات زنده</div>
        <div class="stat-val">${{toFa(d.active_connections)}}</div>
        <div class="stat-sub" style="color:var(--green-t);display:flex;align-items:center;gap:4px"><span class="dot"></span> آنلاین</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">کل مصرف</div>
        <div class="stat-val" style="font-size:17px;margin-top:3px">${{totalLimit > 0 ? fmtB(totalUsed) + ' / ' + fmtB(totalLimit) : fmtB(totalUsed)}}</div>
        <div class="stat-sub">${{expiryDate ? 'انقضا: ' + new Date(expiryDate).toLocaleDateString('fa-IR') : 'نامحدود'}}</div>
      </div>
    </div>

    <div class="cfg-title"><i class="ti ti-link"></i> کانفیگ‌ها (${{toFa(d.links.length)}} عدد)</div>
    <div class="cfg-grid">
      ${{d.links.map((l, i) => {{
        const usedBytes = Number(l.used_bytes) || 0;
        const limitBytes = Number(l.limit_bytes) || 0;
        const pct = limitBytes === 0 ? 0 : Math.min(100, usedBytes / limitBytes * 100);
        const bc  = pct > 90 ? 'var(--red)' : pct > 70 ? 'var(--amber)' : 'var(--green)';
        const lim = limitBytes === 0 ? '∞' : fmtB(limitBytes);
        // اگر used_fmt از بک‌اند خالی/نامعتبر بیاد (مثلاً برای بعضی پروتکل‌ها مثل Shadowsocks)،
        // مقدار را مستقیماً از used_bytes می‌سازیم تا همیشه عدد درست نمایش داده شود.
        const usedFmt = (l.used_fmt && String(l.used_fmt).trim()) ? l.used_fmt : fmtB(usedBytes);
        const barWidth = limitBytes === 0 ? (usedBytes > 0 ? 100 : 0) : pct;
        const barColor = limitBytes === 0 ? 'var(--accent)' : bc;
        const exp = l.expiry_date ? new Date(l.expiry_date).toLocaleDateString('fa-IR') : 'نامحدود';
        return `
          <div class="cfg-card${{l.active ? '' : ' inactive'}}">
            <div class="cfg-top">
              <div class="cfg-head">
                <div>
                  <div class="cfg-label">${{esc(l.label)}}</div>
                  <div class="cfg-badges">
                    ${{protoChip(l.protocol)}}
                    ${{l.connections > 0 ? `<span class="conn-chip"><span class="dot"></span> ${{toFa(l.connections)}} اتصال</span>` : ''}}
                    ${{l.expiry_date ? `<span class="conn-chip" style="background:var(--amber-bg);color:var(--amber-t)"><i class="ti ti-calendar"></i> ${{exp}}</span>` : ''}}
                  </div>
                </div>
                <span class="cfg-status ${{l.active ? 'ok' : 'no'}}">${{l.active ? '<i class="ti ti-circle-check"></i> فعال' : '<i class="ti ti-circle-x"></i> غیرفعال'}}</span>
              </div>
              <div class="cfg-usage">
                <div class="ubar"><div class="ubar-f" style="width:${{barWidth}}%;background:${{barColor}}"></div></div>
                <div class="utxt"><span>${{esc(usedFmt)}} مصرف شده</span><span>سهمیه: ${{lim}} · انقضا: ${{exp}}</span></div>
              </div>
            </div>
            <div class="cfg-tear"></div>
            <div class="cfg-bottom">
              <button class="cfg-link-toggle" id="vt-${{i}}" onclick="toggleLink(${{i}})">
                <span class="ltl"><i class="ti ti-eye"></i> <span>نمایش لینک کانفیگ</span></span>
                <i class="ti ti-chevron-down"></i>
              </button>
              <div class="cfg-vless-wrap" id="vw-${{i}}">
                <div class="cfg-vless-inner">
                  <div class="cfg-vless">${{esc(l.vless_link)}}</div>
                </div>
              </div>
              <div class="cfg-actions">
                <button class="btn btn-p"
                  onclick="navigator.clipboard.writeText(window._rvgLinks[${{i}}].vless).then(()=>toast('لینک کپی شد ✓','ok'))">
                  <i class="ti ti-copy"></i> کپی لینک
                </button>
                <button class="btn btn-g"
                  onclick="showQR(window._rvgLinks[${{i}}].label, window._rvgLinks[${{i}}].vless)">
                  <i class="ti ti-qrcode"></i> QR
                </button>
              </div>
            </div>
          </div>
        `;
      }}).join('')}}
    </div>
  `;

  updateSubscriptionHeaders(totalUsed, totalLimit, expiryDate);

  setTimeout(() => autoRefresh(), 30000);
}}

function updateSubscriptionHeaders(used, limit, expiry) {{
  try {{
    localStorage.setItem('rvg_sub_used', String(used));
    localStorage.setItem('rvg_sub_limit', String(limit));
    if (expiry) {{
      localStorage.setItem('rvg_sub_expiry', expiry);
    }}
  }} catch(e) {{}}
}}

function copyAllConfigs(){{
  const links=window._rvgLinks||[];
  if(!links.length){{toast('کانفیگی برای کپی نیست','');return}}
  const text=links.map(l=>l.vless).join('\\n');
  navigator.clipboard.writeText(text).then(()=>toast('همه‌ی '+toFa(links.length)+' کانفیگ کپی شد ✓','ok'));
}}

async function autoRefresh(){{
  try{{
    const data = await loadData(savedPw);
    if (!data.locked) renderContent(data);
  }} catch(e) {{}}
}}

function getSubscriptionInfo() {{
  return {{
    used: parseInt(localStorage.getItem('rvg_sub_used') || '0'),
    limit: parseInt(localStorage.getItem('rvg_sub_limit') || '0'),
    expiry: localStorage.getItem('rvg_sub_expiry') || null
  }};
}}

async function init(){{
  try{{
    const data = await loadData();
    if (data.locked) {{ renderLock(data.name); return; }}
    renderContent(data);
  }} catch(e) {{
    document.getElementById('root').innerHTML =
      '<div class="empty-state" style="color:var(--red-t)"><i class="ti ti-alert-circle"></i>خطا در بارگذاری</div>';
  }}
}}

window.getSubData = function() {{
  return SUB_DATA;
}};

init();
</script>
</body></html>"""
