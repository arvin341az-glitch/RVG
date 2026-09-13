# central.py — ارتباط با سرویس مرکزی روی Cloudflare Worker
# غیرفعال شد: هیچ درخواستی به دامنه‌ی workers.dev ارسال نمی‌شود. توابع زیر
# فقط برای سازگاری با importها/endpointهای main.py نگه داشته شده‌اند و
# همیشه مقدار خنثی (خالی/بدون خطا) برمی‌گردانند.
import asyncio


async def register_instance():
    return


async def heartbeat_loop():
    while True:
        await asyncio.sleep(300)


async def fetch_announcements():
    return []


async def report_announcement_views(ids: list[str]):
    return


async def fetch_support_messages():
    """برمی‌گرداند: (messages, blocked)"""
    return [], False


async def send_support_message(body: str) -> dict:
    return {"ok": False, "blocked": False, "error": "این قابلیت غیرفعال است"}


async def close_support_chat() -> bool:
    return False
