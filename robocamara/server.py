"""Mobile web app + captive portal, served on the open hotspot.

Security notes:
  * There is NO upload endpoint — photos only ever come from the camera, so
    nobody on the network can push images onto the server.
  * Photos are reachable only by their unguessable token; there is no listing.
  * Everything is served over the local hotspot only (see the firewall rules
    in setup/configure.sh).
"""
import threading

from flask import (Flask, abort, jsonify, redirect,
                   render_template_string, send_file)

from . import config

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{{ title }}</title>
<style>
  :root { color-scheme: dark; }
  * { box-sizing: border-box; }
  body { margin:0; background:#0c0d10; color:#f4f5f7;
         font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
         -webkit-text-size-adjust:100%;
         padding:env(safe-area-inset-top) 16px calc(env(safe-area-inset-bottom) + 24px); }
  .wrap { max-width:520px; margin:0 auto; }
  header { text-align:center; padding:18px 0 12px; }
  header h1 { margin:0; font-size:1.3rem; letter-spacing:1px; }
  .photo { width:100%; border-radius:18px; display:block; background:#16171c;
           box-shadow:0 12px 34px rgba(0,0,0,.55); }
  .timer { text-align:center; margin:18px 0 4px; font-size:1.05rem; }
  .timer b { font-variant-numeric:tabular-nums; color:#ff9f43; }
  .note { text-align:center; color:#9aa0a6; font-size:.85rem;
          margin:6px auto 20px; max-width:340px; line-height:1.45; }
  .btn { display:block; text-align:center; text-decoration:none; color:#fff;
         background:#2f6df6; font-weight:600; font-size:1.05rem;
         padding:16px; border-radius:14px; }
  .btn:active { background:#2657c4; }
  .ios { display:none; text-align:center; color:#9aa0a6;
         font-size:.9rem; margin-top:14px; line-height:1.4; }
</style>
</head>
<body>
  <div class="wrap">
    <header><h1>{{ title }}</h1></header>
    <img class="photo" src="/photo/{{ token }}.jpg" alt="Your photo">
    <p class="timer" id="timer">Deleting in <b id="count">--:--</b></p>
    <p class="note">Save it to your phone now — after {{ ttl_min }} minutes it is
       permanently deleted for your privacy.</p>
    <a class="btn" id="dl" href="/download/{{ token }}.jpg" download="robocamara.jpg">
       Download photo</a>
    <p class="ios" id="ios">On iPhone: press &amp; hold the photo above,
       then tap <b>Save to Photos</b>.</p>
  </div>
<script>
  var remaining = {{ remaining }};
  var count = document.getElementById('count');
  var timerEl = document.getElementById('timer');
  (function tick() {
    if (remaining <= 0) { timerEl.textContent = 'This photo has been deleted.'; return; }
    var m = Math.floor(remaining / 60), s = remaining % 60;
    count.textContent = m + ':' + (s < 10 ? '0' : '') + s;
    remaining--;
    setTimeout(tick, 1000);
  })();
  if (/iP(hone|ad|od)/.test(navigator.userAgent)) {
    document.getElementById('dl').style.display = 'none';
    document.getElementById('ios').style.display = 'block';
  }
</script>
</body>
</html>"""

SIMPLE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ title }}</title>
<style>
  body { margin:0; min-height:100vh; display:flex; align-items:center;
         justify-content:center; background:#0c0d10; color:#f4f5f7; text-align:center;
         font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
         padding:24px; }
  h1 { font-size:1.3rem; letter-spacing:1px; margin:0 0 10px; }
  p  { color:#9aa0a6; margin:0; }
</style></head>
<body><div><h1>{{ title }}</h1><p>{{ message }}</p></div></body></html>"""


def create_app(store):
    app = Flask(__name__)

    @app.route("/")
    def index():
        photo = store.latest()
        if not photo:
            return render_template_string(
                SIMPLE, title=config.SITE_TITLE,
                message="Smile! Your photo will appear here right after it's taken.")
        return redirect("/p/" + photo.token)

    @app.route("/p/<token>")
    def photo_page(token):
        photo = store.get(token)
        if not photo:
            return render_template_string(
                SIMPLE, title=config.SITE_TITLE,
                message="This photo has expired and was deleted for your privacy."), 410
        return render_template_string(
            PAGE, title=config.SITE_TITLE, token=token,
            remaining=store.remaining(token),
            ttl_min=config.PHOTO_TTL_SECONDS // 60)

    @app.route("/photo/<token>.jpg")
    def photo_file(token):
        photo = store.get(token)
        if not photo:
            abort(404)
        return send_file(photo.path, mimetype="image/jpeg")

    @app.route("/download/<token>.jpg")
    def download(token):
        photo = store.get(token)
        if not photo:
            abort(404)
        return send_file(photo.path, mimetype="image/jpeg",
                         as_attachment=True, download_name="robocamara.jpg")

    @app.route("/status/<token>")
    def status(token):
        photo = store.get(token)
        if not photo:
            return jsonify(expired=True)
        return jsonify(expired=False, remaining=store.remaining(token))

    # Captive portal: phones probe a few known URLs after joining Wi-Fi, and
    # our DNS points every domain at the Pi. Redirect anything unknown to the
    # photo page so the "sign in to network" sheet pops open showing the photo.
    @app.route("/<path:_path>")
    def catch_all(_path):
        return redirect("http://" + config.AP_IP + "/")

    @app.errorhandler(404)
    def not_found(_e):
        return redirect("http://" + config.AP_IP + "/")

    return app


def serve_in_background(store):
    """Start the web server in a daemon thread and return it."""
    from waitress import serve

    app = create_app(store)
    thread = threading.Thread(
        target=lambda: serve(app, host="0.0.0.0", port=config.WEB_PORT, threads=8),
        daemon=True,
    )
    thread.start()
    return thread
