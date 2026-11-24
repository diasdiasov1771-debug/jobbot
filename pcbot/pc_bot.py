"""
PC Control Bot — kompyuterni Telegram orqali telefondan boshqarish.

Faqat OWNER_ID dagi Telegram foydalanuvchi, parolni kiritgandan keyin, buyruq bera oladi.
Sozlash: pcbot/README.md
"""
import asyncio
import hmac
import io
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

import mss
import mss.tools
import psutil
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters,
)

TOKEN = os.environ.get("PC_BOT_TOKEN")
OWNER_ID = os.environ.get("PC_BOT_OWNER_ID")
if not TOKEN or not OWNER_ID:
    sys.exit("PC_BOT_TOKEN va PC_BOT_OWNER_ID muhit o'zgaruvchilarini o'rnating (README.md ga qarang).")
OWNER_ID = int(OWNER_ID)
PASSWORD = os.environ.get("PC_BOT_PASSWORD")
if not PASSWORD:
    sys.exit("PC_BOT_PASSWORD muhit o'zgaruvchisini o'rnating (bot paroli, README.md ga qarang).")
SESSION_MINUTES = int(os.environ.get("PC_BOT_SESSION_MIN", "30"))  # parol shuncha daqiqa amal qiladi
MAX_ATTEMPTS = 5          # ketma-ket xato urinishlar
LOCKOUT_SECONDS = 10 * 60  # shundan keyin bloklash

auth = {"until": 0.0, "fails": 0, "locked_until": 0.0}

OS = platform.system()  # "Windows", "Linux", "Darwin"
CMD_TIMEOUT = 60
MAX_TEXT = 3900

KEYBOARD = ReplyKeyboardMarkup(
    [
        ["📸 Skrinshot", "📊 Holat"],
        ["🔒 Bloklash", "😴 Uyqu"],
        ["🔄 Qayta yoqish", "⛔ O'chirish"],
        ["❌ Bekor qilish", "🔐 Chiqish"],
    ],
    resize_keyboard=True,
)


def is_unlocked() -> bool:
    return time.time() < auth["until"]


def owner_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if not user or user.id != OWNER_ID:
            if update.message:
                await update.message.reply_text(f"⛔ Ruxsat yo'q. Sizning ID: {user.id if user else '?'}")
            return
        if not is_unlocked():
            if update.message:
                await update.message.reply_text("🔐 Bot qulflangan. Parolni yozing:")
            return
        auth["until"] = time.time() + SESSION_MINUTES * 60  # faollikda sessiyani uzaytirish
        return await func(update, context)
    return wrapper


async def try_password(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Egasi qulflangan holatda yozgan matnni parol sifatida tekshiradi."""
    try:
        await update.message.delete()  # parol chatda qolmasin
    except Exception:
        pass
    now = time.time()
    if now < auth["locked_until"]:
        mins = int((auth["locked_until"] - now) // 60) + 1
        await context.bot.send_message(OWNER_ID, f"⛔ Juda ko'p xato urinish. {mins} daqiqadan keyin qayta urining.")
        return
    if hmac.compare_digest(text.encode(), PASSWORD.encode()):
        auth.update(until=now + SESSION_MINUTES * 60, fails=0)
        await context.bot.send_message(
            OWNER_ID,
            f"🔓 Parol to'g'ri. Sessiya {SESSION_MINUTES} daqiqa faolsiz turgandan keyin qulflanadi.\n"
            "Qo'lda qulflash: /logout yoki 🔐 Chiqish. Yordam: /start",
            reply_markup=KEYBOARD,
        )
    else:
        auth["fails"] += 1
        left = MAX_ATTEMPTS - auth["fails"]
        if left <= 0:
            auth.update(fails=0, locked_until=now + LOCKOUT_SECONDS)
            await context.bot.send_message(OWNER_ID, f"⛔ Parol {MAX_ATTEMPTS} marta xato. Bot {LOCKOUT_SECONDS // 60} daqiqaga bloklandi.")
        else:
            await context.bot.send_message(OWNER_ID, f"❌ Parol noto'g'ri. Qolgan urinishlar: {left}")


async def send_long(update: Update, text: str):
    text = text.strip() or "(bo'sh natija)"
    if len(text) <= MAX_TEXT:
        await update.message.reply_text(f"```\n{text}\n```", parse_mode="Markdown")
    else:
        await update.message.reply_document(io.BytesIO(text.encode()), filename="natija.txt")


def run_shell(cmd: str) -> str:
    try:
        res = subprocess.run(
            cmd, shell=True, capture_output=True, timeout=CMD_TIMEOUT,
        )
        enc = "cp866" if OS == "Windows" else "utf-8"
        out = res.stdout.decode(enc, errors="replace") + res.stderr.decode(enc, errors="replace")
        return f"{out}\n[kod: {res.returncode}]"
    except subprocess.TimeoutExpired:
        return f"⏱ {CMD_TIMEOUT} soniyada tugamadi."


def power_cmd(action: str) -> str:
    cmds = {
        "Windows": {
            "shutdown": "shutdown /s /t 30",
            "restart": "shutdown /r /t 30",
            "cancel": "shutdown /a",
            "lock": "rundll32.exe user32.dll,LockWorkStation",
            "sleep": "rundll32.exe powrprof.dll,SetSuspendState 0,1,0",
        },
        "Linux": {
            "shutdown": "shutdown -h +1",
            "restart": "shutdown -r +1",
            "cancel": "shutdown -c",
            "lock": "loginctl lock-session",
            "sleep": "systemctl suspend",
        },
        "Darwin": {
            "shutdown": "sudo shutdown -h +1",
            "restart": "sudo shutdown -r +1",
            "cancel": "sudo killall shutdown",
            "lock": "pmset displaysleepnow",
            "sleep": "pmset sleepnow",
        },
    }
    return cmds.get(OS, cmds["Linux"])[action]


# ============ HANDLERS ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user or user.id != OWNER_ID:
        await update.message.reply_text(f"⛔ Ruxsat yo'q. Sizning ID: {user.id if user else '?'}")
        return
    if not is_unlocked():
        await update.message.reply_text("🔐 Bot parol bilan himoyalangan. Parolni yozing:")
        return
    await update.message.reply_text(
        f"🖥 {platform.node()} ({OS}) ulangan.\n\n"
        "Buyruqlar:\n"
        "/screenshot — ekran rasmi\n"
        "/status — CPU, RAM, disk, batareya\n"
        "/cmd <buyruq> — terminal buyrug'i\n"
        "/ls [papka] — fayllar ro'yxati\n"
        "/get <fayl> — faylni telefonga yuborish\n"
        "Fayl yuborsangiz — Downloads papkasiga saqlanadi\n"
        "/open <url yoki fayl> — ochish\n"
        "/lock, /sleep, /restart, /shutdown, /cancel\n"
        "/logout — botni qulflash (keyin yana parol so'raladi)",
        reply_markup=KEYBOARD,
    )


@owner_only
async def screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    def grab():
        with mss.mss() as sct:
            shot = sct.grab(sct.monitors[0])  # barcha monitorlar
            return mss.tools.to_png(shot.rgb, shot.size)
    png = await asyncio.to_thread(grab)
    await update.message.reply_document(io.BytesIO(png), filename="screen.png")


@owner_only
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage(Path.home().anchor or "/")
    lines = [
        f"🖥 {platform.node()} — {platform.platform()}",
        f"⚙️ CPU: {psutil.cpu_percent(interval=1)}%",
        f"🧠 RAM: {mem.percent}% ({mem.used // 2**20} / {mem.total // 2**20} MB)",
        f"💾 Disk: {disk.percent}% ({disk.free // 2**30} GB bo'sh)",
    ]
    bat = psutil.sensors_battery() if hasattr(psutil, "sensors_battery") else None
    if bat:
        lines.append(f"🔋 Batareya: {bat.percent:.0f}% {'(zaryadlanmoqda)' if bat.power_plugged else ''}")
    await update.message.reply_text("\n".join(lines))


@owner_only
async def cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = " ".join(context.args)
    if not command:
        await update.message.reply_text("Misol: /cmd ipconfig")
        return
    out = await asyncio.to_thread(run_shell, command)
    await send_long(update, out)


@owner_only
async def ls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    path = Path(" ".join(context.args) or Path.home()).expanduser()
    if not path.is_dir():
        await update.message.reply_text("❌ Papka topilmadi.")
        return
    items = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    text = f"📁 {path}\n" + "\n".join(
        ("📁 " if p.is_dir() else "📄 ") + p.name for p in items[:200]
    )
    await send_long(update, text)


@owner_only
async def get_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    path = Path(" ".join(context.args)).expanduser()
    if not path.is_file():
        await update.message.reply_text("❌ Fayl topilmadi. Misol: /get C:\\Users\\Ism\\file.txt")
        return
    if path.stat().st_size > 50 * 2**20:
        await update.message.reply_text("❌ Telegram limiti: 50 MB.")
        return
    with open(path, "rb") as f:
        await update.message.reply_document(f, filename=path.name)


@owner_only
async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    dest_dir = Path.home() / "Downloads"
    dest_dir.mkdir(exist_ok=True)
    dest = dest_dir / doc.file_name
    tg_file = await doc.get_file()
    await tg_file.download_to_drive(dest)
    await update.message.reply_text(f"✅ Saqlandi: {dest}")


@owner_only
async def open_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = " ".join(context.args)
    if not target:
        await update.message.reply_text("Misol: /open https://youtube.com")
        return
    if OS == "Windows":
        os.startfile(target)  # noqa
    elif OS == "Darwin":
        subprocess.Popen(["open", target])
    else:
        subprocess.Popen(["xdg-open", target])
    await update.message.reply_text(f"✅ Ochildi: {target}")


def power_handler(action: str, msg: str):
    @owner_only
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(msg)
        out = await asyncio.to_thread(run_shell, power_cmd(action))
        if "[kod: 0]" not in out:
            await send_long(update, out)
    return handler


async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user or user.id != OWNER_ID:
        return
    auth["until"] = 0.0
    await update.message.reply_text("🔐 Bot qulflandi. Ochish uchun parolni yozing.")


BUTTONS = {
    "📸 Skrinshot": screenshot,
    "📊 Holat": status,
    "🔒 Bloklash": power_handler("lock", "🔒 Bloklanmoqda..."),
    "😴 Uyqu": power_handler("sleep", "😴 Uyqu rejimi..."),
    "🔄 Qayta yoqish": power_handler("restart", "🔄 Qayta yoqiladi (bekor qilish: /cancel)"),
    "⛔ O'chirish": power_handler("shutdown", "⛔ O'chiriladi (bekor qilish: /cancel)"),
    "❌ Bekor qilish": power_handler("cancel", "❌ O'chirish/qayta yoqish bekor qilindi."),
    "🔐 Chiqish": logout,
}


async def button_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user and user.id == OWNER_ID and not is_unlocked():
        if update.message.text in BUTTONS:  # tugma bosildi — parol urinishi emas
            await update.message.reply_text("🔐 Bot qulflangan. Parolni yozing:")
        else:
            await try_password(update, context, update.message.text)
        return
    handler = BUTTONS.get(update.message.text)
    if handler:
        await handler(update, context)


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("screenshot", screenshot))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("cmd", cmd))
    app.add_handler(CommandHandler("ls", ls))
    app.add_handler(CommandHandler("get", get_file))
    app.add_handler(CommandHandler("open", open_target))
    app.add_handler(CommandHandler("logout", logout))
    for name, (action, msg) in {
        "lock": ("lock", "🔒 Bloklanmoqda..."),
        "sleep": ("sleep", "😴 Uyqu rejimi..."),
        "restart": ("restart", "🔄 Qayta yoqiladi (bekor qilish: /cancel)"),
        "shutdown": ("shutdown", "⛔ O'chiriladi (bekor qilish: /cancel)"),
        "cancel": ("cancel", "❌ Bekor qilindi."),
    }.items():
        app.add_handler(CommandHandler(name, power_handler(action, msg)))
    app.add_handler(MessageHandler(filters.Document.ALL, receive_file))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_text))
    print(f"PC bot ishga tushdi ({platform.node()}, {OS}). To'xtatish: Ctrl+C")
    app.run_polling()


if __name__ == "__main__":
    main()
