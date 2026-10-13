import os, asyncio, textwrap
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import pytz
from PIL import Image, ImageDraw, ImageFont
import edge_tts

app = Flask(__name__)
TZ = pytz.timezone('Africa/Harare')

PRAYERS = {
"monday":"God, today is Monday, bless my week ahead. Guide my steps, protect my family, and let your favour be upon Zimbabwe. Amen. If you woke up alive, type AMEN.",
"tuesday":"God, today is Tuesday, bless my family and my country. Guide my steps, protect my loved ones, and let peace fill Zimbabwe today. Amen.",
"wednesday":"God, today is Wednesday, bless my work and my hands. Open doors for me, provide for my family. Amen.",
"thursday":"Heavenly Father, thank you for Thursday. Bless my family, heal the sick, and let your love shine. Amen.",
"friday":"Lord, thank you for Friday. Bless my family, forgive us, and prepare us for a peaceful weekend. Amen.",
"saturday":"God, today is Saturday, bless my rest and my family time. Protect us and let joy fill our home. Amen.",
"sunday":"Lord, today is Sunday, bless my family and my worship. Thank you for life. If you woke up ALIVE today, type AMEN and FOLLOW prince dianna"
}

VOICE = "en-US-GuyNeural"

def make_image(day):
    W,H=1080,1920
    img=Image.new('RGB',(W,H),(10,20,50))
    d=ImageDraw.Draw(img)
    for y in range(H):
        d.line([(0,y),(W,y)],fill=(min(10+y//7,200),min(20+y//15,120),min(50+y//20,80)))
    try:
        f=ImageFont.truetype("arial.ttf",55)
    except:
        f=ImageFont.load_default()
    text=PRAYERS.get(day, PRAYERS["tuesday"])
    wrapped=textwrap.fill(text,width=30)
    d.multiline_text((80,650),wrapped,fill=(255,255,255),font=f,spacing=18,stroke_width=2,stroke_fill=(0,0,0))
    d.text((80,1650),"@prince.dianna0 | Type AMEN",fill=(135,206,250),font=f)
    path=f"/tmp/{day}.jpg"
    img.save(path)
    return path,text

async def make_voice(text,day):
    path=f"/tmp/{day}.mp3"
    c=edge_tts.Communicate(text,VOICE,rate="-5%",pitch="-10Hz")
    await c.save(path)
    return path

def make_video(img_path,aud_path,day):
    from moviepy.editor import ImageClip,AudioFileClip
    audio=AudioFileClip(aud_path)
    clip=ImageClip(img_path).set_duration(min(audio.duration+1,30)).set_audio(audio)
    vp=f"/tmp/{day}.mp4"
    clip.write_videofile(vp,fps=24,codec='libx264',audio_codec='aac')
    return vp

async def pipeline(day):
    ip,txt=make_image(day)
    ap=await make_voice(txt,day)
    vp=make_video(ip,ap,day)
    return vp,txt

def daily_job():
    now=datetime.now(TZ)
    day=now.strftime("%A").lower()
    async def run():
        vp,txt=await pipeline(day)
        print(f"Video ready: {vp}")
    asyncio.run(run())

scheduler=BackgroundScheduler(timezone=TZ)
scheduler.add_job(daily_job,'cron',hour=5,minute=0)
scheduler.start()

@app.route('/')
def home():
    return f"BOT LIVE WITH DEEP VOICE - {datetime.now(TZ)} - Next 5AM"
@app.route('/post-now')
def post_now():
    daily_job()
    return "Posted NOW"

if __name__=='__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get("PORT",10000)))
