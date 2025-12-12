# HBD_wish.py
"""
Patched Flask app with improved playback handling and a debug route.
Drop this file into your project root and run with your venv activated.
"""

import os
from flask import Flask, request, url_for, render_template_string, redirect, jsonify

BASE = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE, "static")
MEDIA_DIR = os.path.join(STATIC_DIR, "media")
AUDIO_DIR = os.path.join(STATIC_DIR, "audio")

# Expected filenames (change if yours differ)
VIDEO_FILENAME = "babai_birthday_final.mp4"
AUDIO_FILENAME = "bday_song.mp3"

# Ensure directories exist
for d in (STATIC_DIR, MEDIA_DIR, AUDIO_DIR):
    os.makedirs(d, exist_ok=True)

HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Happy Birthday — {{ name_display }}</title>
<style>
  body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial;background:linear-gradient(180deg,#fff7f0,#fff);display:flex;align-items:center;justify-content:center;min-height:100vh;padding:10px}
  .card{width:96vw;max-width:540px;background:#fff;border-radius:14px;box-shadow:0 10px 30px rgba(0,0,0,0.12);overflow:hidden}
  .media{position:relative;width:100%;height:0;padding-bottom:177.78% /*9:16 vertical*/; background:#000}
  video, img{position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover}
  .content{padding:16px;text-align:center}
  h1{margin:8px 0;font-size:20px}
  p{margin:6px 0 14px;color:#333}
  .btn{display:inline-block;padding:12px 20px;border-radius:12px;background:#ff6b6b;color:#fff;text-decoration:none;font-weight:700}
  .hint{font-size:12px;color:#666;margin-top:10px}
  .overlay{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);z-index:6}
  .overlay button{background:rgba(0,0,0,0.55);color:#fff;border:0;padding:14px 18px;border-radius:999px;font-size:18px}
  .asset-list{font-size:12px;color:#666;margin-top:10px;text-align:left; padding:0 12px 12px;}
  .asset-list code{display:block;background:#f6f6f6;padding:6px;border-radius:6px}
</style>
</head>
<body>
  <div class="card" role="main">
    <div class="media" id="mediaWrap">
      {% if video_url %}
        <video id="wishMedia" loop playsinline muted preload="auto" src="{{ video_url }}"></video>
      {% elif img_url %}
        <img id="wishMedia" src="{{ img_url }}" alt="Happy Birthday">
      {% else %}
        <div style="display:flex;align-items:center;justify-content:center;height:100%;color:#fff">🎉</div>
      {% endif %}
      <div class="overlay" id="overlay" style="display:none">
        <button id="overlayBtn">▶ Play Wish</button>
      </div>
    </div>

    <div class="content">
      <h1>Happy Birthday My Dear Brother..., {{ name_display }} 🎉</h1>
      <p id="msg">{{ message_text }}</p>

      {% if audio_url %}
      <audio id="wishAudio" preload="auto" src="{{ audio_url }}"></audio>
      {% endif %}

      <div id="controls">
        <a href="#" id="playBtn" class="btn" onclick="playAll(event)">▶ Play Wish</a>
        <div class="hint">If audio doesn't start automatically, tap Play. Works inside WhatsApp in-app browser too.</div>
      </div>

      <div class="asset-list">
        <strong>Assets detected:</strong>
        <div>
          <code>video_url: {{ video_url or 'NONE' }}</code>
          <code>audio_url: {{ audio_url or 'NONE' }}</code>
          <code>img_url: {{ img_url or 'NONE' }}</code>
        </div>
      </div>
    </div>
  </div>

<script>
/*
 Improved playback logic:
 - Tries autoplay; logs detailed errors in console.
 - If autoplay blocked, shows overlay and enables native controls as fallback.
 - Play button attempts to start audio & unmute video together.
*/
const audio = document.getElementById('wishAudio');
const media = document.getElementById('wishMedia');
const overlay = document.getElementById('overlay');
const overlayBtn = document.getElementById('overlayBtn');
const controls = document.getElementById('controls');

window.addEventListener('load', async () => {
  console.log('Page loaded. Attempting autoplay where possible...');
  // Try to autoplay muted video (usually allowed)
  if (media && media.tagName === 'VIDEO') {
    try {
      await media.play();
      console.log('Video autoplay (muted) succeeded.');
    } catch(e) {
      console.warn('Video autoplay failed or blocked (muted):', e);
    }
  }
  // Try to autoplay audio (may be blocked)
  try {
    if (audio) {
      await audio.play();
      console.log('Audio autoplay succeeded.');
    }
    // If audio started, hide manual controls and unmute video
    controls.style.display = 'none';
    if (media && media.tagName === 'VIDEO') {
      media.muted = false;
      media.play().catch(()=>{});
    }
  } catch(err) {
    console.warn('Audio autoplay blocked or failed:', err);
    // Show user-friendly overlay and enable native controls as fallback
    overlay.style.display = 'block';
    if (audio) audio.controls = true;
    if (media && media.tagName === 'VIDEO') media.controls = true;
    // print a helpful hint
    console.info('If playback fails, try pressing the Play button or the native controls.');
  }
});

async function playAll(ev){
  if(ev) ev.preventDefault();
  console.log('Play button pressed — attempting to play audio and unmute video...');
  if (!audio) {
    // No audio present: unmute/play video only
    if (media && media.tagName === 'VIDEO') {
      try {
        media.muted = false;
        await media.play();
        controls.style.display='none';
        overlay.style.display='none';
        console.log('Video played successfully (no audio present).');
      } catch(e) {
        console.error('Video play failed:', e);
        media.controls = true;
      }
    }
    return;
  }

  try {
    await audio.play();
    if (media && media.tagName === 'VIDEO') {
      media.muted = false;
      media.play().catch(()=>{});
    }
    controls.style.display = 'none';
    overlay.style.display = 'none';
    console.log('Audio played successfully via Play button.');
  } catch(err) {
    console.error('Play failed after user gesture:', err);
    // Fallback: enable native controls so user can press them
    audio.controls = true;
    if (media && media.tagName === 'VIDEO') media.controls = true;
    overlay.style.display = 'block';
  }
}

overlayBtn && overlayBtn.addEventListener('click', (e)=> playAll(e));

// One-tap convenience: first user tap anywhere tries to resume audio (only once)
document.body.addEventListener('click', function onceTap(){
  if (audio && audio.paused) {
    audio.play().then(()=> {
      if (media && media.tagName === 'VIDEO') { media.muted = false; media.play().catch(()=>{}); }
      controls.style.display='none';
      overlay.style.display='none';
      console.log('Playback started from body tap.');
    }).catch((e)=>{
      console.warn('Body tap playback failed:', e);
    });
  }
}, { once: true });
</script>
</body>
</html>
"""

app = Flask(__name__, static_folder=STATIC_DIR)

def verify_assets():
    """Return (video_url, img_url, audio_url) or None if missing."""
    video_path = os.path.join(MEDIA_DIR, VIDEO_FILENAME)
    audio_path = os.path.join(AUDIO_DIR, AUDIO_FILENAME)

    video_url = url_for('static', filename=f"media/{VIDEO_FILENAME}") if os.path.exists(video_path) else None
    audio_url = url_for('static', filename=f"audio/{AUDIO_FILENAME}") if os.path.exists(audio_path) else None

    # fallback image: first jpg/png in media folder
    img_url = None
    try:
        files = os.listdir(MEDIA_DIR)
        img_candidates = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if img_candidates:
            img_url = url_for('static', filename=f"media/{img_candidates[0]}")
    except Exception:
        img_url = None

    return video_url, img_url, audio_url

@app.route('/')
def index():
    return redirect('/wish?name=Babai')

@app.route('/wish')
def wish():
    name = request.args.get('name', 'BABAI').strip() or 'Friend'
    video_url, img_url, audio_url = verify_assets()
    message_text = f"Stay Happy, Keep Growing and Succeeding on War of Life...:)! Happy birthday  {name}, --wishes by Tatai."
    return render_template_string(HTML_TEMPLATE,
                                name_display=name,
                                message_text=message_text,
                                video_url=video_url,
                                img_url=img_url,
                                audio_url=audio_url)

@app.route('/debug_assets')
def debug_assets():
    """Simple JSON endpoint to see what the server sees on disk."""
    video_path = os.path.join(MEDIA_DIR, VIDEO_FILENAME)
    audio_path = os.path.join(AUDIO_DIR, AUDIO_FILENAME)
    media_list = os.listdir(MEDIA_DIR) if os.path.exists(MEDIA_DIR) else []
    audio_list = os.listdir(AUDIO_DIR) if os.path.exists(AUDIO_DIR) else []
    return jsonify({
        "video_exists": os.path.exists(video_path),
        "video_url": url_for('static', filename=f"media/{VIDEO_FILENAME}") if os.path.exists(video_path) else None,
        "audio_exists": os.path.exists(audio_path),
        "audio_url": url_for('static', filename=f"audio/{AUDIO_FILENAME}") if os.path.exists(audio_path) else None,
        "media_list": media_list,
        "audio_list": audio_list
    })

if __name__ == "__main__":
    print("Starting patched HBD_wish app")
    print("Static dir:", STATIC_DIR)
    print("Media dir:", MEDIA_DIR, "contains:", os.listdir(MEDIA_DIR) if os.path.exists(MEDIA_DIR) else [])
    print("Audio dir:", AUDIO_DIR, "contains:", os.listdir(AUDIO_DIR) if os.path.exists(AUDIO_DIR) else [])
    app.run(host="0.0.0.0", port=5000, debug=False)
