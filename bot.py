from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# =====================
# DATA STORAGE
# =====================
users = {}  # user_id: {role, lang, ...}
jobs = []   # list of job posts
workers = [] # list of worker profiles

# =====================
# TRANSLATIONS
# =====================
LANGS = {
    "uz": {
        "welcome": "👋 Xush kelibsiz! IT Job Bot ga!\n\nTilni tanlang:",
        "choose_role": "Rolingizni tanlang:",
        "employer": "👔 Ish beruvchi",
        "worker": "👨‍💻 Ishchi",
        "register_name": "📝 Ismingizni kiriting:",
        "register_category": "📂 Kategoriyangizni tanlang:",
        "register_experience": "⏳ Tajribangizni kiriting (masalan: 2 yil):",
        "register_cv": "📄 CV havolangizni yuboring (Google Drive, HH.uz yoki boshqa):",
        "register_contact": "📞 Telegram username yoki telefon raqamingiz:",
        "register_done": "✅ Ro'yxatdan muvaffaqiyatli o'tdingiz!",
        "post_job_title": "💼 Ish nomini kiriting (masalan: Videograf kerak):",
        "post_job_category": "📂 Kategoriyani tanlang:",
        "post_job_desc": "📝 Ish tavsifini kiriting:",
        "post_job_salary": "💰 Maoshni kiriting (masalan: $500-1000):",
        "post_job_contact": "📞 Aloqa uchun username yoki telefon:",
        "post_job_done": "✅ E'lon muvaffaqiyatli joylashtirildi!",
        "find_job": "🔍 Ish qidirish — kategoriya tanlang:",
        "find_workers": "👥 Ishchi qidirish — kategoriya tanlang:",
        "no_jobs": "😔 Hozircha bu kategoriyada ish yo'q.",
        "no_workers": "😔 Hozircha bu kategoriyada ishchi yo'q.",
        "main_menu": "🏠 Asosiy menyu",
        "post_job_btn": "📢 Ish e'loni berish",
        "find_job_btn": "🔍 Ish qidirish",
        "find_worker_btn": "👥 Ishchi qidirish",
        "my_profile": "👤 Mening profilim",
        "back": "🔙 Orqaga",
    },
    "ru": {
        "welcome": "👋 Добро пожаловать в IT Job Bot!\n\nВыберите язык:",
        "choose_role": "Выберите вашу роль:",
        "employer": "👔 Работодатель",
        "worker": "👨‍💻 Работник",
        "register_name": "📝 Введите ваше имя:",
        "register_category": "📂 Выберите категорию:",
        "register_experience": "⏳ Введите опыт (например: 2 года):",
        "register_cv": "📄 Отправьте ссылку на CV (Google Drive, HH.ru и т.д.):",
        "register_contact": "📞 Ваш Telegram username или номер телефона:",
        "register_done": "✅ Регистрация прошла успешно!",
        "post_job_title": "💼 Введите название вакансии:",
        "post_job_category": "📂 Выберите категорию:",
        "post_job_desc": "📝 Введите описание вакансии:",
        "post_job_salary": "💰 Введите зарплату (например: $500-1000):",
        "post_job_contact": "📞 Контакт для связи:",
        "post_job_done": "✅ Вакансия успешно опубликована!",
        "find_job": "🔍 Поиск работы — выберите категорию:",
        "find_workers": "👥 Поиск работников — выберите категорию:",
        "no_jobs": "😔 В этой категории пока нет вакансий.",
        "no_workers": "😔 В этой категории пока нет работников.",
        "main_menu": "🏠 Главное меню",
        "post_job_btn": "📢 Разместить вакансию",
        "find_job_btn": "🔍 Найти работу",
        "find_worker_btn": "👥 Найти работника",
        "my_profile": "👤 Мой профиль",
        "back": "🔙 Назад",
    },
    "en": {
        "welcome": "👋 Welcome to IT Job Bot!\n\nChoose your language:",
        "choose_role": "Choose your role:",
        "employer": "👔 Employer",
        "worker": "👨‍💻 Worker",
        "register_name": "📝 Enter your name:",
        "register_category": "📂 Choose your category:",
        "register_experience": "⏳ Enter your experience (e.g: 2 years):",
        "register_cv": "📄 Send your CV link (Google Drive, LinkedIn, etc.):",
        "register_contact": "📞 Your Telegram username or phone number:",
        "register_done": "✅ Registration successful!",
        "post_job_title": "💼 Enter job title:",
        "post_job_category": "📂 Choose category:",
        "post_job_desc": "📝 Enter job description:",
        "post_job_salary": "💰 Enter salary (e.g: $500-1000):",
        "post_job_contact": "📞 Contact info:",
        "post_job_done": "✅ Job posted successfully!",
        "find_job": "🔍 Find a job — choose category:",
        "find_workers": "👥 Find workers — choose category:",
        "no_jobs": "😔 No jobs available in this category yet.",
        "no_workers": "😔 No workers available in this category yet.",
        "main_menu": "🏠 Main menu",
        "post_job_btn": "📢 Post a Job",
        "find_job_btn": "🔍 Find a Job",
        "find_worker_btn": "👥 Find a Worker",
        "my_profile": "👤 My Profile",
        "back": "🔙 Back",
    }
}

# =====================
# CATEGORIES
# =====================
CATEGORIES = [
    "📱 Mobilograf",
    "🎥 Videograf",
    "🎞️ Video Operator",
    "✂️ Video Montajor",
    "🎬 Motion Designer",
    "📝 Ssenarist",
    "🎭 Content Creator",
    "📣 Digital Marketing",
    "🎯 Targetolog",
    "🎨 UI/UX Designer",
    "🐍 Python Developer",
    "🌐 Frontend Developer",
    "⚙️ Backend Developer",
    "📱 Mobile Developer",
    "🛡️ DevOps Engineer",
    "🔒 Cybersecurity",
    "🧪 QA Engineer",
    "📊 Data Scientist",
    "🤖 AI/ML Engineer",
]

def get_lang(user_id):
    return users.get(user_id, {}).get("lang", "uz")

def t(user_id, key):
    lang = get_lang(user_id)
    return LANGS[lang].get(key, key)

def category_keyboard():
    keyboard = []
    row = []
    for i, cat in enumerate(CATEGORIES):
        row.append(InlineKeyboardButton(cat, callback_data=f"cat_{cat}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

def main_menu_keyboard(user_id):
    role = users.get(user_id, {}).get("role", "")
    lang = get_lang(user_id)
    T = LANGS[lang]
    if role == "employer":
        keyboard = [
            [T["post_job_btn"]],
            [T["find_worker_btn"]],
            [T["my_profile"]],
        ]
    else:
        keyboard = [
            [T["find_job_btn"]],
            [T["my_profile"]],
        ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# =====================
# HANDLERS
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users[user_id] = {"step": "lang"}
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz"),
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        ]
    ])
    await update.message.reply_text("👋 Tilni tanlang / Выберите язык / Choose language:", reply_markup=keyboard)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    # LANGUAGE
    if data.startswith("lang_"):
        lang = data.split("_")[1]
        users[user_id] = {"lang": lang, "step": "role"}
        T = LANGS[lang]
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(T["employer"], callback_data="role_employer"),
                InlineKeyboardButton(T["worker"], callback_data="role_worker"),
            ]
        ])
        await query.edit_message_text(T["choose_role"], reply_markup=keyboard)

    # ROLE
    elif data.startswith("role_"):
        role = data.split("_")[1]
        users[user_id]["role"] = role
        if role == "worker":
            users[user_id]["step"] = "register_name"
            await query.edit_message_text(t(user_id, "register_name"))
        else:
            users[user_id]["step"] = "done"
            await query.edit_message_text(f"✅ {t(user_id, 'employer')} sifatida kirdingi!")
            await context.bot.send_message(user_id, t(user_id, "main_menu"), reply_markup=main_menu_keyboard(user_id))

    # CATEGORY (worker registration)
    elif data.startswith("cat_") and users.get(user_id, {}).get("step") == "register_category":
        cat = data[4:]
        users[user_id]["category"] = cat
        users[user_id]["step"] = "register_experience"
        await query.edit_message_text(t(user_id, "register_experience"))

    # CATEGORY (job posting)
    elif data.startswith("cat_") and users.get(user_id, {}).get("step") == "post_job_category":
        cat = data[4:]
        users[user_id]["job_category"] = cat
        users[user_id]["step"] = "post_job_desc"
        await query.edit_message_text(t(user_id, "post_job_desc"))

    # CATEGORY (find job)
    elif data.startswith("cat_") and users.get(user_id, {}).get("step") == "find_job":
        cat = data[4:]
        found = [j for j in jobs if j["category"] == cat]
        if not found:
            await query.edit_message_text(t(user_id, "no_jobs"))
        else:
            await query.edit_message_text("📋 Topilgan ishlar:")
            for job in found:
                text = (
                    f"💼 *{job['title']}*\n"
                    f"📂 {job['category']}\n"
                    f"📝 {job['desc']}\n"
                    f"💰 {job['salary']}\n"
                    f"📞 {job['contact']}"
                )
                await context.bot.send_message(user_id, text, parse_mode="Markdown")
        users[user_id]["step"] = "done"

    # CATEGORY (find worker)
    elif data.startswith("cat_") and users.get(user_id, {}).get("step") == "find_worker":
        cat = data[4:]
        found = [w for w in workers if w["category"] == cat]
        if not found:
            await query.edit_message_text(t(user_id, "no_workers"))
        else:
            await query.edit_message_text("👥 Topilgan ishchilar:")
            for w in found:
                text = (
                    f"👤 *{w['name']}*\n"
                    f"📂 {w['category']}\n"
                    f"⏳ {w['experience']}\n"
                    f"📄 CV: {w['cv']}\n"
                    f"📞 {w['contact']}"
                )
                await context.bot.send_message(user_id, text, parse_mode="Markdown")
        users[user_id]["step"] = "done"

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    step = users.get(user_id, {}).get("step", "")
    lang = get_lang(user_id)
    T = LANGS[lang]

    # WORKER REGISTRATION
    if step == "register_name":
        users[user_id]["name"] = text
        users[user_id]["step"] = "register_category"
        await update.message.reply_text(T["register_category"], reply_markup=category_keyboard())

    elif step == "register_experience":
        users[user_id]["experience"] = text
        users[user_id]["step"] = "register_cv"
        await update.message.reply_text(T["register_cv"])

    elif step == "register_cv":
        users[user_id]["cv"] = text
        users[user_id]["step"] = "register_contact"
        await update.message.reply_text(T["register_contact"])

    elif step == "register_contact":
        users[user_id]["contact"] = text
        users[user_id]["step"] = "done"
        workers.append({
            "name": users[user_id].get("name"),
            "category": users[user_id].get("category"),
            "experience": users[user_id].get("experience"),
            "cv": users[user_id].get("cv"),
            "contact": text,
        })
        await update.message.reply_text(T["register_done"])
        await update.message.reply_text(T["main_menu"], reply_markup=main_menu_keyboard(user_id))

    # EMPLOYER - POST JOB
    elif text == T["post_job_btn"]:
        users[user_id]["step"] = "post_job_title"
        await update.message.reply_text(T["post_job_title"])

    elif step == "post_job_title":
        users[user_id]["job_title"] = text
        users[user_id]["step"] = "post_job_category"
        await update.message.reply_text(T["post_job_category"], reply_markup=category_keyboard())

    elif step == "post_job_desc":
        users[user_id]["job_desc"] = text
        users[user_id]["step"] = "post_job_salary"
        await update.message.reply_text(T["post_job_salary"])

    elif step == "post_job_salary":
        users[user_id]["job_salary"] = text
        users[user_id]["step"] = "post_job_contact"
        await update.message.reply_text(T["post_job_contact"])

    elif step == "post_job_contact":
        jobs.append({
            "title": users[user_id].get("job_title"),
            "category": users[user_id].get("job_category"),
            "desc": users[user_id].get("job_desc"),
            "salary": users[user_id].get("job_salary"),
            "contact": text,
        })
        users[user_id]["step"] = "done"
        await update.message.reply_text(T["post_job_done"])
        await update.message.reply_text(T["main_menu"], reply_markup=main_menu_keyboard(user_id))

    # FIND JOB
    elif text == T["find_job_btn"]:
        users[user_id]["step"] = "find_job"
        await update.message.reply_text(T["find_job"], reply_markup=category_keyboard())

    # FIND WORKER
    elif text == T["find_worker_btn"]:
        users[user_id]["step"] = "find_worker"
        await update.message.reply_text(T["find_workers"], reply_markup=category_keyboard())

    # MY PROFILE
    elif text in [LANGS["uz"]["my_profile"], LANGS["ru"]["my_profile"], LANGS["en"]["my_profile"]]:
        role = users[user_id].get("role", "")
        if role == "worker":
            profile = (
                f"👤 *{users[user_id].get('name', '-')}*\n"
                f"📂 {users[user_id].get('category', '-')}\n"
                f"⏳ {users[user_id].get('experience', '-')}\n"
                f"📄 CV: {users[user_id].get('cv', '-')}\n"
                f"📞 {users[user_id].get('contact', '-')}"
            )
            await update.message.reply_text(profile)
        else:
            await update.message.reply_text("👔 Employer profili")

# =====================
# RUN BOT
# =====================
app = ApplicationBuilder().token("8788147931:AAGF_I3CAGgVzHNq3R26wMDbJqrAe-Z_Kpc").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
app.run_polling()