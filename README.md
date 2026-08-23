<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f2027,50:203a43,100:2c5364&height=220&section=header&text=RVG%20Gateway&fontSize=60&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Multi-Protocol%20Proxy%20Management%20Panel&descAlignY=58&descSize=18" width="100%"/>

<a href="#-english"><img src="https://img.shields.io/badge/🇬🇧-English-0f2027?style=for-the-badge" /></a>
<a href="#-فارسی"><img src="https://img.shields.io/badge/🇮🇷-فارسی-203a43?style=for-the-badge" /></a>

<br/>

![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&pause=1000&color=2C5364&center=true&vCenter=true&width=600&lines=Fast+%26+Modern+Proxy+Gateway;VLESS+%7C+Trojan+%7C+Shadowsocks+%7C+MTProto;Built+with+FastAPI+%2B+Python;Deploy+to+Railway+in+One+Click)

<br/>

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Async-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Railway](https://img.shields.io/badge/Deploy-Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)](https://railway.app)
[![License](https://img.shields.io/badge/License-Custom-red?style=for-the-badge)](./LICENSE)

![Stars](https://img.shields.io/github/stars/arvin341az-glitch/RVG?style=social)
![Forks](https://img.shields.io/github/forks/arvin341az-glitch/RVG?style=social)
![Last Commit](https://img.shields.io/github/last-commit/arvin341az-glitch/RVG?color=2c5364)
![Repo Size](https://img.shields.io/github/repo-size/arvin341az-glitch/RVG?color=0f2027)

</div>

<br/>

---

<div align="center">
<h1>🇬🇧 English</h1>
</div>

## 📖 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Supported Protocols](#-supported-protocols)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Quick Start (Railway)](#-quick-start-railway-deploy)
- [Local Development](#-local-development)
- [Environment Variables](#-environment-variables)
- [Dashboard Preview](#-dashboard-preview)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)
- [Support the Project](#-support-the-project)

<br/>

## 🚀 Overview

**RVG Gateway** is a fast, modern, self-hosted **multi-protocol proxy management panel**, built with **Python + FastAPI**, designed to deploy in minutes on **Railway**.

It gives you a beautiful admin dashboard to create, monitor, and manage proxy links across multiple protocols — with per-link traffic quotas, live connection stats, and QR code generation — all from a single lightweight service.

> 💡 Originally built around a simple VLESS-over-WebSocket relay, RVG has evolved into a full multi-protocol gateway with authentication, quota tracking, and a polished management UI.

<br/>

## ✨ Features

<table>
<tr>
<td width="50%">

### 🔌 Core Gateway
- VLESS over WebSocket (TLS 443)
- Trojan, Shadowsocks (AEAD / aes-256-gcm)
- MTProto proxy via `mtg` binary
- Internal HTTP Proxy
- xHTTP / gRPC / HTTPUpgrade transports

</td>
<td width="50%">

### 📊 Management Dashboard
- Real-time traffic charts & trend indicators
- Live connection monitoring
- Unlimited link creation with per-link quotas (MB/GB)
- Instant enable / disable per link
- QR Code export for every link

</td>
</tr>
<tr>
<td width="50%">

### 🛡️ Security & Reliability
- Strict UUID validation
- Session-based authentication
- TLS fingerprint spoofing (Chrome)
- Optimized relay buffers (512KB, `TCP_NODELAY`, `SO_KEEPALIVE`)

</td>
<td width="50%">

### 🤖 Automation
- Telegram-bot-integrated proxy management
- Domain suggestion via Cloudflare Worker
- Automated TCP proxy dispatch with blacklist targeting
- One-click Railway deployment

</td>
</tr>
</table>

<br/>

## 🌐 Supported Protocols

| Protocol | Transport | Status |
|---|---|:---:|
| VLESS | WebSocket / xHTTP / gRPC | ✅ |
| Trojan | WebSocket / HTTPUpgrade | ✅ |
| Shadowsocks | AEAD (aes-256-gcm) | ✅ |
| MTProto | `mtg` v2.1.7 | ✅ |
| HTTP Proxy | Internal | ✅ |

<br/>

## 🏗️ Architecture

```mermaid
flowchart LR
    A[Client / v2rayNG / NekoBox] -->|VLESS / Trojan / SS| B(RVG Gateway<br/>FastAPI Server)
    B --> C{Protocol Router}
    C -->|WebSocket| D[VLESS / Trojan Relay]
    C -->|TCP| E[Shadowsocks Relay]
    C -->|mtg binary| F[MTProto Relay]
    B --> G[(In-Memory<br/>Link & Quota Store)]
    B --> H[Admin Dashboard :8000/dashboard]
    B --> I[Telegram Bot Automation]
    style B fill:#203a43,stroke:#0f2027,color:#fff
    style H fill:#2c5364,stroke:#0f2027,color:#fff
```

<br/>

## 📂 Project Structure

```
RVG/
├── protocol/                 # Per-protocol relay implementations
├── main.py                   # FastAPI app entrypoint
├── api_v1.py                 # API-key protected bot administration router
├── auth.py                   # Constant-time X-API-KEY dependency
├── schemas.py                # Strict Pydantic v2 API contracts
├── central.py                # Core orchestration logic
├── pages.py                  # Dashboard route/page handlers
├── updater.py                  # Self-update logic
├── botgeneratedomin.py         # Telegram bot: domain generation
├── bottokentcpproxy.py         # TCP proxy automation via Telegram
├── zeussocks5.py                # SOCKS5 proxy handler
├── requirements.txt
├── .gitignore
└── README.md
```

<br/>

## ⚡ Quick Start (Railway Deploy)

<table>
<tr>
<td width="60px" align="center">1️⃣</td>
<td>

**Fork this repository**

```
https://github.com/arvin341az-glitch/RVG/fork
```

</td>
</tr>
<tr>
<td align="center">2️⃣</td>
<td>

**Deploy on Railway**

1. Go to [Railway.app](https://railway.app)
2. Click **New Project → Deploy from GitHub repo**
3. Select your forked repository
4. Railway auto-builds and deploys 🎉

</td>
</tr>
<tr>
<td align="center">3️⃣</td>
<td>

**Enable a public domain**

Railway → Settings → Networking → **Generate Domain**
(this sets `RAILWAY_PUBLIC_DOMAIN` automatically)

</td>
</tr>
<tr>
<td align="center">4️⃣</td>
<td>

**Open your dashboard**

```
https://your-app.up.railway.app/dashboard
```

Copy the default VLESS link and import it into your client (v2rayNG, NekoBox, Streisand, …).

</td>
</tr>
</table>

<br/>

## 💻 Local Development

```bash
# Clone your fork
git clone https://github.com/<your-username>/RVG.git
cd RVG

# Create a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

The dashboard will be available at `http://localhost:8000/dashboard`.

<br/>

## ⚙️ Environment Variables

| Variable | Description | Default |
|---|---|---|
| `PORT` | Port the service runs on | `8000` |
| `SECRET_KEY` | Internal security key | Randomly generated |
| `RAILWAY_PUBLIC_DOMAIN` | Public Railway domain (auto-set) | `localhost` |
| `RVG_API_KEY` | Required secret for the bot admin API (`X-API-KEY`) | No default; API fails closed |
| `RVG_API_KEYS` | Optional comma-separated keys for zero-downtime rotation | Empty |
| `PUBLIC_BASE_URL` | Optional canonical URL used in generated subscription URLs | Derived from public domain |

Generate a strong API key and store it only in the panel and bot environments:

```bash
openssl rand -hex 32
```

### Bot administration REST API

Every `/api/v1` request requires `X-API-KEY`. The API uses strict Pydantic v2
validation and a stable response envelope:

```json
{"success": true, "data": {}, "error": null, "message": "..."}
```

```bash
curl -X POST "https://panel.example.com/api/v1/users" \
  -H "X-API-KEY: $RVG_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","traffic_limit_gb":50,"expire_days":30,"protocol":"vless"}'
```

Available operations:

- `POST /api/v1/users`
- `GET /api/v1/users/{username}`
- `PATCH /api/v1/users/{username}/extend`
- `PATCH /api/v1/users/{username}/status`
- `POST /api/v1/users/{username}/reset-traffic`
- `DELETE /api/v1/users/{username}`
- `GET /api/v1/users/{username}/subscription?format=base64|plain`
- `GET /api/v1/users/{username}/links`
- `GET /api/v1/system/stats`

See [`examples/telegram_bot_client.py`](examples/telegram_bot_client.py) for an
async `httpx` integration. The current RVG core supports VLESS, Trojan,
Shadowsocks and MTProto. MTProto creation requires a Railway token already saved
through the panel so its public TCP proxy can be provisioned synchronously.
VMess is not advertised because this gateway does not implement a VMess inbound.

<br/>

## 📸 Dashboard Preview

<div align="center">

> Traffic overview • Live connections • Link manager • QR export

<img src="https://img.shields.io/badge/📊_Traffic_Charts-live-2c5364?style=for-the-badge" />
<img src="https://img.shields.io/badge/🔗_Link_Manager-unlimited-203a43?style=for-the-badge" />
<img src="https://img.shields.io/badge/📱_QR_Export-per_link-0f2027?style=for-the-badge" />

</div>

<br/>

## 🗺️ Roadmap

- [x] Multi-protocol relay (VLESS, Trojan, Shadowsocks, MTProto)
- [x] Telegram bot automation
- [x] Traffic dashboard with charts
- [ ] Persistent storage (Redis / PostgreSQL)
- [ ] Multi-node / cluster support
- [x] API-key protected REST API for Telegram/external integrations

<br/>

## 🤝 Contributing

Pull requests are welcome for bug fixes, optimizations, and documentation.
> ⚠️ Please read the [LICENSE](./LICENSE) before contributing — modification and redistribution of modified versions is restricted. Open an issue first if you'd like to discuss a change.

<br/>

## 📄 License

This project is distributed under a **custom license**:
✅ Free to use, deploy, and fork
❌ Modifying and redistributing a modified version is **not permitted**

See the full [LICENSE](./LICENSE) file for details.

<br/>

## ❤️ Support the Project

If this project helped you, consider supporting its development:

<div align="center">

[![Donate](https://img.shields.io/badge/Donate-PayPal-blue.svg?style=for-the-badge&logo=paypal)]([https://your-donate-link.com](https://railwayx3ui.page.gd/wallet/donate.html))
[![Wallets](https://img.shields.io/badge/Crypto-Wallets-f7931a?style=for-the-badge&logo=bitcoin)]([https://wallets.arvin341az.workers.dev](https://railwayx3ui.page.gd/wallet/donate.html))

**Made with ❤️ by [codebox](https://github.com/arvin341az-glitch)**

</div>

<br/>

---

<br/>

<div align="center" dir="rtl">
<h1>🇮🇷 فارسی</h1>
</div>

## 📖 فهرست مطالب

- [معرفی](#-معرفی)
- [ویژگی‌ها](#-ویژگیها)
- [پروتکل‌های پشتیبانی‌شده](#-پروتکلهای-پشتیبانیشده)
- [معماری](#-معماری)
- [ساختار پروژه](#-ساختار-پروژه)
- [شروع سریع (دیپلوی روی Railway)](#-شروع-سریع-دیپلوی-روی-railway)
- [توسعه محلی](#-توسعه-محلی)
- [متغیرهای محیطی](#-متغیرهای-محیطی)
- [نقشه راه](#-نقشه-راه)
- [مشارکت](#-مشارکت)
- [لایسنس](#-لایسنس)
- [حمایت از پروژه](#-حمایت-از-پروژه)

<br/>

## 🚀 معرفی

**RVG Gateway** یک پنل مدیریت پروکسی چندپروتکلی، سریع و مدرن است که با **Python + FastAPI** ساخته شده و در چند دقیقه روی **Railway** قابل دیپلوی است.

این پروژه یک داشبورد مدیریتی زیبا در اختیارتان می‌گذارد تا لینک‌های پروکسی را در پروتکل‌های مختلف بسازید، مانیتور کنید و مدیریت کنید — همراه با محدودیت ترافیک اختصاصی برای هر لینک، آمار اتصالات زنده و خروجی QR Code، همه از طریق یک سرویس سبک و یکپارچه.

> 💡 این پروژه که ابتدا یک ریلی ساده VLESS روی WebSocket بود، اکنون به یک دروازه کامل چندپروتکلی با احراز هویت، مدیریت سهمیه و رابط کاربری حرفه‌ای تبدیل شده است.

<br/>

## ✨ ویژگی‌ها

<table dir="rtl">
<tr>
<td width="50%">

### 🔌 هسته دروازه
- VLESS روی WebSocket (TLS 443)
- Trojan، Shadowsocks (AEAD / aes-256-gcm)
- پروکسی MTProto از طریق باینری `mtg`
- HTTP Proxy داخلی
- ترنسپورت‌های xHTTP / gRPC / HTTPUpgrade

</td>
<td width="50%">

### 📊 داشبورد مدیریتی
- نمودار ترافیک لحظه‌ای و شاخص‌های روند
- مانیتورینگ اتصالات زنده
- ساخت لینک نامحدود با محدودیت ترافیک اختصاصی (MB/GB)
- فعال/غیرفعال‌سازی آنی هر لینک
- خروجی QR Code برای هر لینک

</td>
</tr>
<tr>
<td width="50%">

### 🛡️ امنیت و پایداری
- اعتبارسنجی دقیق UUID
- احراز هویت مبتنی بر سشن
- جعل فینگرپرینت TLS (Chrome)
- بافرهای بهینه‌شده ریلی (۵۱۲ کیلوبایت، `TCP_NODELAY`، `SO_KEEPALIVE`)

</td>
<td width="50%">

### 🤖 اتوماسیون
- مدیریت پروکسی یکپارچه با ربات تلگرام
- پیشنهاد دامنه از طریق Cloudflare Worker
- ارسال خودکار پروکسی TCP با هدف‌گیری بلک‌لیست
- دیپلوی با یک کلیک روی Railway

</td>
</tr>
</table>

<br/>

## 🌐 پروتکل‌های پشتیبانی‌شده

| پروتکل | ترنسپورت | وضعیت |
|---|---|:---:|
| VLESS | WebSocket / xHTTP / gRPC | ✅ |
| Trojan | WebSocket / HTTPUpgrade | ✅ |
| Shadowsocks | AEAD (aes-256-gcm) | ✅ |
| MTProto | `mtg` v2.1.7 | ✅ |
| HTTP Proxy | داخلی | ✅ |

<br/>

## 🏗️ معماری

```mermaid
flowchart RL
    A[کلاینت / v2rayNG / NekoBox] -->|VLESS / Trojan / SS| B(RVG Gateway<br/>سرور FastAPI)
    B --> C{مسیریاب پروتکل}
    C -->|WebSocket| D[ریلی VLESS / Trojan]
    C -->|TCP| E[ریلی Shadowsocks]
    C -->|باینری mtg| F[ریلی MTProto]
    B --> G[(ذخیره‌سازی درون‌حافظه<br/>لینک و سهمیه)]
    B --> H[داشبورد مدیریت :8000/dashboard]
    B --> I[اتوماسیون ربات تلگرام]
    style B fill:#203a43,stroke:#0f2027,color:#fff
    style H fill:#2c5364,stroke:#0f2027,color:#fff
```

<br/>

## 📂 ساختار پروژه

```
RVG/
├── protocol/                 # پیاده‌سازی ریلی هر پروتکل
├── main.py                   # نقطه ورود اپلیکیشن FastAPI
├── api_v1.py                 # روتر مدیریتی امن برای ربات
├── auth.py                   # احراز هویت X-API-KEY
├── schemas.py                # قراردادهای سخت‌گیرانه Pydantic v2
├── central.py                # منطق اصلی هماهنگ‌سازی
├── pages.py                  # هندلر مسیرها/صفحات داشبورد
├── updater.py                  # منطق به‌روزرسانی خودکار
├── botgeneratedomin.py         # ربات تلگرام: تولید دامنه
├── bottokentcpproxy.py         # اتوماسیون پروکسی TCP از طریق تلگرام
├── zeussocks5.py                # هندلر پروکسی SOCKS5
├── requirements.txt
├── .gitignore
└── README.md
```

<br/>

## ⚡ شروع سریع (دیپلوی روی Railway)

<table dir="rtl">
<tr>
<td width="60px" align="center">1️⃣</td>
<td>

**فورک کردن این ریپازیتوری**

```
https://github.com/arvin341az-glitch/RVG/fork
```

</td>
</tr>
<tr>
<td align="center">2️⃣</td>
<td>

**دیپلوی روی Railway**

۱. وارد [Railway.app](https://railway.app) شوید
۲. روی **New Project → Deploy from GitHub repo** کلیک کنید
۳. ریپازیتوری فورک‌شده خود را انتخاب کنید
۴. Railway به‌صورت خودکار پروژه را می‌سازد و دیپلوی می‌کند 🎉

</td>
</tr>
<tr>
<td align="center">3️⃣</td>
<td>

**فعال‌سازی دامنه عمومی**

Railway ← Settings ← Networking ← **Generate Domain**
(این کار متغیر `RAILWAY_PUBLIC_DOMAIN` را خودکار تنظیم می‌کند)

</td>
</tr>
<tr>
<td align="center">4️⃣</td>
<td>

**باز کردن داشبورد**

```
https://your-app.up.railway.app/dashboard
```

لینک پیش‌فرض VLESS را کپی کرده و در کلاینت دلخواه (v2rayNG، NekoBox، Streisand و...) وارد کنید.

</td>
</tr>
</table>

<br/>

## 💻 توسعه محلی

```bash
# کلون کردن فورک شما
git clone https://github.com/<your-username>/RVG.git
cd RVG

# ساخت محیط مجازی
python -m venv venv
source venv/bin/activate   # ویندوز: venv\Scripts\activate

# نصب وابستگی‌ها
pip install -r requirements.txt

# اجرای سرور
python main.py
```

داشبورد در آدرس `http://localhost:8000/dashboard` در دسترس خواهد بود.

<br/>

## ⚙️ متغیرهای محیطی

| متغیر | توضیح | پیش‌فرض |
|---|---|---|
| `PORT` | پورت اجرای سرویس | `8000` |
| `SECRET_KEY` | کلید امنیتی داخلی | تولید تصادفی |
| `RAILWAY_PUBLIC_DOMAIN` | دامنه عمومی Railway (خودکار) | `localhost` |
| `RVG_API_KEY` | کلید الزامی API ربات در هدر `X-API-KEY` | بدون مقدار پیش‌فرض |
| `RVG_API_KEYS` | کلیدهای چرخشی، جداشده با ویرگول | خالی |
| `PUBLIC_BASE_URL` | آدرس عمومی ثابت برای لینک‌های اشتراک | از دامنه عمومی |

<br/>

## 🗺️ نقشه راه

- [x] ریلی چندپروتکلی (VLESS، Trojan، Shadowsocks، MTProto)
- [x] اتوماسیون ربات تلگرام
- [x] داشبورد ترافیک با نمودار
- [ ] ذخیره‌سازی دائمی (Redis / PostgreSQL)
- [ ] پشتیبانی چندنودی / کلاستر
- [x] API مدیریتی REST با کلید امن برای ربات تلگرام و سرویس‌های دیگر

<br/>

## 🤝 مشارکت

پول‌ریکوئست برای رفع باگ، بهینه‌سازی و مستندسازی خوش‌آمد است.
> ⚠️ لطفاً قبل از مشارکت، فایل [LICENSE](./LICENSE) را مطالعه کنید — تغییر و بازنشر نسخه تغییریافته محدود شده است. برای هرگونه تغییر، ابتدا یک Issue باز کنید.

<br/>

## 📄 لایسنس

این پروژه تحت یک **لایسنس سفارشی** منتشر شده است:
✅ استفاده، دیپلوی و فورک آزاد
❌ تغییر و بازنشر نسخه تغییریافته **مجاز نیست**

برای جزئیات کامل به فایل [LICENSE](./LICENSE) مراجعه کنید.

<br/>

## ❤️ حمایت از پروژه

اگر این پروژه به شما کمک کرد، می‌توانید از توسعه آن حمایت کنید:

<div align="center">

[![Donate](https://img.shields.io/badge/Donate-PayPal-blue.svg?style=for-the-badge&logo=paypal)]([https://your-donate-link.com](https://railwayx3ui.page.gd/wallet/donate.html))
[![Wallets](https://img.shields.io/badge/Crypto-Wallets-f7931a?style=for-the-badge&logo=bitcoin)]([https://wallets.arvin341az.workers.dev](https://railwayx3ui.page.gd/wallet/donate.html))

**ساخته‌شده با ❤️ توسط [codebox](https://github.com/arvin341az-glitch)**

</div>

<br/>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:2c5364,50:203a43,100:0f2027&height=120&section=footer" width="100%"/>
