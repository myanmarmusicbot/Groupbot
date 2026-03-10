# Telegram Group Management Bot

ဒီ Bot က Telegram Group Management အတွက် ရေးထားတာဖြစ်ပါတယ်။

## Features
- 👑 Owner ဝင်လာရင် Special Message ပြမယ်
- 💬 Support Group နဲ့ Channel Link တွေပါမယ်
- 🔗 Links တွေကို အလိုအလျောက် Shorten လုပ်ပေးမယ်
- 📝 Filter System (Auto Reply)
- 🚫 Ban / Mute / Unmute Commands
- 📊 User Activity Logger
- 🚂 Railway Ready

## Commands
- `/start` - Bot စတင်ခြင်း
- `/help` - အကူအညီ
- `/filter <keyword> <reply>` - Filter ထည့်ရန် (Admin)
- `/filters` - Filter အားလုံးကြည့်ရန် (Admin)
- `/del <keyword>` - Filter ဖျက်ရန် (Admin)
- `/ban` - User ကို Ban (Admin, Reply)
- `/mute` - User ကို Mute (Admin, Reply)
- `/unmute` - User ကို Unmute (Admin, Reply)

## Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/myanmarmusicbot/Groupbot)

### Environment Variables
| Variable | Description |
|----------|-------------|
| `BOT_TOKEN` | BotFather က ရတဲ့ Token |
| `OWNER_ID` | Owner Telegram ID |
| `OWNER_USERNAME` | Owner Username (without @) |
| `SUPPORT_USERNAME` | Support Group Username (without @) |
| `CHANNEL_USERNAME` | Channel Username (without @) |
| `LOGGER_GROUP_ID` | Logger Group ID |

## Local Run
```bash
pip install -r requirements.txt
python bot.py
