# 🖥 PC Control Bot — kompyuterni telefondan boshqarish

Bu bot **kompyuteringizda** ishlaydi, siz esa telefondagi Telegram orqali buyruq berasiz.
Faqat sizning Telegram ID'ingiz qabul qilinadi va bot **parol** bilan himoyalangan — boshqalar uchun bot hech narsa qilmaydi.

## Imkoniyatlar
| Buyruq / tugma | Nima qiladi |
|---|---|
| 📸 Skrinshot, `/screenshot` | Ekran rasmini yuboradi |
| 📊 Holat, `/status` | CPU, RAM, disk, batareya |
| `/cmd <buyruq>` | Terminal buyrug'ini bajaradi (masalan `/cmd ipconfig`) |
| `/ls [papka]` | Papkadagi fayllar ro'yxati |
| `/get <fayl>` | Faylni telefonga yuboradi (50 MB gacha) |
| Fayl yuborish | Kompyuterdagi `Downloads` papkasiga saqlanadi |
| `/open <url/fayl>` | Sayt yoki faylni ochadi |
| 🔒 `/lock`, 😴 `/sleep` | Bloklash, uyqu |
| 🔄 `/restart`, ⛔ `/shutdown` | Qayta yoqish / o'chirish (30–60 soniya kechikish bilan) |
| ❌ `/cancel` | O'chirishni bekor qilish |
| 🔐 Chiqish, `/logout` | Botni qulflash (keyin yana parol so'raladi) |

## 🔐 Parol
- Bot ishga tushganda **qulflangan** bo'ladi. Telefonda botga parolni oddiy xabar qilib yozing — to'g'ri bo'lsa bot ochiladi.
- Parol yozilgan xabar chatdan avtomatik o'chiriladi.
- 30 daqiqa hech narsa qilinmasa bot o'zi qulflanadi (`PC_BOT_SESSION_MIN` bilan o'zgartirish mumkin).
- 5 marta xato parol → bot 10 daqiqaga bloklanadi.

## Sozlash (Windows)

1. **Python** o'rnating: https://www.python.org/downloads/ — o'rnatishda **"Add Python to PATH"** belgisini qo'ying.
2. **Yangi bot oching:** Telegram'da @BotFather → `/newbot` → token oling.
   (Job bot tokenini ishlatmang — alohida bot bo'lsin.)
3. **ID'ingizni bilib oling:** Telegram'da @userinfobot ga yozing — u raqamli ID beradi.
4. Bu `pcbot` papkasini kompyuterga yuklab oling va unda `cmd` oching:
   ```
   pip install -r requirements.txt
   setx PC_BOT_TOKEN "BotFather_bergan_token"
   setx PC_BOT_OWNER_ID "123456789"
   setx PC_BOT_PASSWORD "o'zingiz_o'ylagan_parol"
   ```
   `setx` dan keyin `cmd` oynasini yopib, yangisini oching.
5. Ishga tushiring:
   ```
   python pc_bot.py
   ```
6. Telefonda botga `/start` yozing — tugmalar chiqadi.

### Kompyuter yoqilganda avtomatik ishga tushishi
`Win + R` → `shell:startup` → shu papkada `pcbot.bat` yarating:
```
@echo off
pythonw "C:\yo'l\pcbot\pc_bot.py"
```
`pythonw` qora oynasiz, fonda ishlatadi.

## Linux / macOS
```
pip install -r requirements.txt
export PC_BOT_TOKEN="..." PC_BOT_OWNER_ID="..." PC_BOT_PASSWORD="..."
python3 pc_bot.py
```

## ⚠️ Xavfsizlik
- `/cmd` kompyuteringizda istalgan buyruqni bajaradi. Tokenni **hech kimga bermang** va GitHub'ga yozmang.
- Token oshkor bo'lsa: @BotFather → `/revoke`.
- `PC_BOT_OWNER_ID` dan boshqa foydalanuvchilar rad etiladi.
- Telefoningiz boshqa odam qo'liga tushsa ham, parolsiz bot buyruq bajarmaydi. Kuchli parol tanlang.
