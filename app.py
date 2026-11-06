import os
import base64
import sqlite3
import uuid
from pathlib import Path
from datetime import datetime
import streamlit as st
from streamlit.components.v1 import html

# ============================================================
# THE FIRST CHAPTER - 365 Days of Love
# Streamlit birthday ecosystem
# ============================================================

APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "birthday_data"
UPLOAD_DIR = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "birthday.sqlite3"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(
    page_title="The First Chapter | 365 Days of Love",
    page_icon="🎂",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Set FIRST_CHAPTER_ADMIN_PASSWORD in your hosting environment.
ADMIN_PASSWORD = os.environ.get("FIRST_CHAPTER_ADMIN_PASSWORD", "1789@Zen#")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');
:root { --navy:#17243b; --gold:#c6a36a; --cream:#fbf8f1; --ink:#263247; }
.stApp { background: linear-gradient(180deg,#fbf8f1 0%,#fff 48%,#f7f3eb 100%); color:var(--ink); }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
h1,h2,h3 { font-family:'Playfair Display',serif !important; color:var(--navy); }
.hero { background:linear-gradient(125deg,#17243b 0%,#263956 55%,#6c5a47 100%);
 color:#fff; border-radius:24px; padding:42px 28px; text-align:center; margin:8px 0 24px; }
.hero .eyebrow { color:#e6d2aa; letter-spacing:4px; font-size:12px; font-weight:700; }
.hero h1 { color:#fff !important; font-size:clamp(38px,6vw,68px); margin:12px 0 4px; }
.hero p { color:#f3ead8; font-size:17px; margin:8px auto; max-width:760px; }
.gold-line { width:90px; height:2px; background:#d9bd87; margin:18px auto; }
.section-card { background:#fff; border:1px solid #eee5d6; border-radius:18px; padding:20px; margin:8px 0 16px; box-shadow:0 8px 28px rgba(28,38,55,.045); }
.small-muted { color:#758095; font-size:13px; }
.pill { display:inline-block; border:1px solid #d8c39d; color:#8d7041; border-radius:30px; padding:5px 12px; font-size:11px; letter-spacing:1px; }
div.stButton > button { border-radius:12px; border:1px solid #c6a36a; }
div.stButton > button[kind="primary"] { background:#17243b; color:white; border:0; }
footer {visibility:hidden;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

def db():
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);
        CREATE TABLE IF NOT EXISTS milestones (
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, date_text TEXT,
            description TEXT, image_path TEXT, sort_order INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS gallery (
            id INTEGER PRIMARY KEY AUTOINCREMENT, caption TEXT, file_path TEXT,
            media_type TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS blessings (
            id INTEGER PRIMARY KEY AUTOINCREMENT, guest_name TEXT, relation TEXT,
            message TEXT, media_path TEXT, media_type TEXT, created_at TEXT,
            approved INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT, a TEXT, b TEXT,
            c TEXT, d TEXT, correct INTEGER, explanation TEXT
        );
        CREATE TABLE IF NOT EXISTS quiz_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT, guest_name TEXT, score INTEGER,
            total INTEGER, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS family_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, relation TEXT,
            photo_path TEXT, generation INTEGER DEFAULT 1, sort_order INTEGER DEFAULT 0
        );
        """)
        defaults = {
            "baby_name": "Our Little Star",
            "tagline": "365 Days of Love",
            "banner_path": "",
            "birthday_date": "Add the birthday date",
            "event_datetime": "Add the live event date and time",
            "invitation_text": "With immense joy, we invite you to celebrate our baby's first birthday.",
            "documentary_path": "",
            "live_url": "",
            "live_platform": "YouTube Live / Zoom / Google Meet",
            "payment_qr_path": "",
            "upi_id": "",
            "gift_note": "Your love and blessings are the greatest gifts. If you wish, you may contribute using the QR code below.",
            "time_capsule_note": "A collection of wishes, hopes and memories to be opened on the baby's 18th birthday.",
            "admin_contact": "",
        }
        for k, v in defaults.items():
            con.execute("INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)", (k, v))

init_db()

def get_setting(key):
    with db() as con:
        row = con.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row["value"] if row else ""

def set_setting(key, value):
    with db() as con:
        con.execute("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, str(value)))

def save_upload(uploaded, prefix):
    if uploaded is None:
        return ""
    suffix = Path(uploaded.name).suffix.lower()
    safe_name = f"{prefix}_{uuid.uuid4().hex}{suffix}"
    dest = UPLOAD_DIR / safe_name
    dest.write_bytes(uploaded.getbuffer())
    return str(dest.relative_to(APP_DIR))

def local_path(relative):
    if not relative:
        return None
    p = (APP_DIR / relative).resolve()
    try:
        p.relative_to(APP_DIR.resolve())
    except ValueError:
        return None
    return p if p.exists() else None

def show_media(relative, media_type=None, caption=None):
    p = local_path(relative)
    if not p:
        return
    suffix = p.suffix.lower()
    if media_type == "video" or suffix in [".mp4", ".mov", ".webm"]:
        st.video(str(p))
    elif suffix == ".gif":
        st.image(str(p), caption=caption, use_container_width=True)
    elif suffix in [".jpg", ".jpeg", ".png", ".webp"]:
        st.image(str(p), caption=caption, use_container_width=True)
    else:
        st.download_button("Download attachment", p.read_bytes(), file_name=p.name)

def hero():
    baby = get_setting("baby_name")
    tagline = get_setting("tagline")
    banner = local_path(get_setting("banner_path"))
    style = ""
    cls = "hero"
    if banner:
        mime = "image/png" if banner.suffix.lower() == ".png" else "image/webp" if banner.suffix.lower() == ".webp" else "image/jpeg"
        encoded = base64.b64encode(banner.read_bytes()).decode("ascii")
        style = f"background-image:linear-gradient(90deg,rgba(13,25,45,.76),rgba(13,25,45,.42)),url(data:{mime};base64,{encoded});background-size:cover;background-position:center;"
    st.markdown(f"""
    <div class="{cls}" style="{style}">
      <div class="eyebrow">A VERY SPECIAL MILESTONE</div>
      <h1>THE FIRST CHAPTER</h1><div class="gold-line"></div>
      <div style="font-family:'Playfair Display',serif;font-size:25px;color:#e8d4ad">{baby}</div>
      <p>{tagline}</p>
      <div class="pill" style="color:#f3ead8;border-color:#d9bd87">ONE LITTLE LIFE · INFINITE LOVE</div>
    </div>""", unsafe_allow_html=True)

def page_title(title, subtitle=""):
    st.markdown(f"## {title}")
    if subtitle:
        st.markdown(f"<div class='small-muted'>{subtitle}</div>", unsafe_allow_html=True)

def admin_login():
    if "admin_ok" not in st.session_state:
        st.session_state.admin_ok = False
    if st.session_state.admin_ok:
        return True
    st.warning("Administrator access is restricted. Guests do not need to log in.")
    if not ADMIN_PASSWORD:
        st.error("Admin password is not configured. Set FIRST_CHAPTER_ADMIN_PASSWORD before running the app.")
        return False
    with st.form("admin_login_form"):
        password = st.text_input("Administrator password", type="password")
        submitted = st.form_submit_button("Sign in", type="primary")
    if submitted:
        if password and password == ADMIN_PASSWORD:
            st.session_state.admin_ok = True
            st.success("Administrator access granted.")
            st.rerun()
        else:
            st.error("Incorrect password.")
    return False

def guest_home():
    hero()
    c1, c2, c3 = st.columns(3)
    c1.metric("A year of", "Memories")
    c2.metric("A world of", "Blessings")
    c3.metric("A lifetime of", "Possibilities")
    st.markdown("<div class='section-card'><span class='pill'>WELCOME, FAMILY & FRIENDS</span><h2>Celebrate a little life with a lot of love.</h2><p>Thank you for being part of this milestone. Explore the memories, watch the birthday film, join the live celebration, play the baby quiz and leave a blessing for our little one.</p></div>", unsafe_allow_html=True)
    st.subheader("Your celebration starts here")
    cols = st.columns(3)
    cards = [
        ("💌", "Digital Invitation", "Read the invitation and event details.", "Digital Invitation"),
        ("🎬", "Birthday Documentary", "Watch the story of the first year.", "Birthday Documentary"),
        ("📸", "Photo Gallery", "Explore special moments.", "Photo & Video Gallery"),
        ("🗓️", "Baby's Journey", "Follow the milestones month by month.", "Baby's Journey"),
        ("🌳", "Family Tree", "Meet the family surrounding our little one.", "Family Tree"),
        ("🎥", "Live Celebration", "Join the online birthday event.", "Live Celebration"),
        ("🧠", "Baby Quiz", "See how well you know the baby.", "Interactive Baby Quiz"),
        ("💝", "Guestbook & Gifts", "Share blessings and optional gifts.", "Digital Guestbook"),
        ("⏳", "Time Capsule", "Leave a message for the future.", "Time Capsule"),
    ]
    for i, (emoji, card_title, desc, target) in enumerate(cards):
        with cols[i % 3]:
            st.markdown(f"<div class='section-card'><div style='font-size:30px'>{emoji}</div><b>{card_title}</b><p class='small-muted'>{desc}</p></div>", unsafe_allow_html=True)
            if st.button(f"Open {card_title} →", key=f"home_nav_{i}", use_container_width=True):
                st.session_state["requested_page"] = target
                st.rerun()
    st.info("Select any card to open that section directly, or use the navigation menu on the left.")

def invitation_page():
    hero()
    page_title("💌 Digital Invitation", "A personal invitation to share a very special day.")
    st.markdown(f"<div class='section-card'><div class='pill'>YOU ARE CORDIALLY INVITED</div><h2 style='text-align:center'>A little star turns ONE!</h2><p style='text-align:center;font-size:18px'>{get_setting('invitation_text')}</p><hr><p><b>Birthday:</b> {get_setting('birthday_date')}</p><p><b>Live celebration:</b> {get_setting('event_datetime')}</p><p><b>Baby:</b> {get_setting('baby_name')}</p><p style='text-align:center'>Your presence and blessings will make this celebration even more special.</p></div>", unsafe_allow_html=True)
    st.caption("Please check the Live Celebration page for the joining link.")

def documentary_page():
    page_title("🎬 The First-Year Documentary", "A little film about a very big year.")
    path = get_setting("documentary_path")
    if path and local_path(path):
        show_media(path, "video")
    else:
        st.info("The birthday documentary will appear here once the family uploads it.")
    st.markdown("### A message from the parents")
    st.write("One year ago, our world changed forever. Every smile, every little discovery and every new milestone has become a memory we will treasure. Happy first birthday, our little miracle.")

def live_page():
    page_title("🎥 Live Birthday Celebration", "Join the family celebration from wherever you are.")
    st.markdown(f"<div class='section-card'><h3>Live event details</h3><p><b>Date & time:</b> {get_setting('event_datetime')}</p><p><b>Platform:</b> {get_setting('live_platform')}</p></div>", unsafe_allow_html=True)
    url = get_setting("live_url").strip()
    if url.startswith("https://") or url.startswith("http://"):
        st.link_button("Join the live celebration", url, type="primary", use_container_width=True)
        st.caption("The live meeting is hosted on the external platform. The host must start the meeting or stream separately.")
    else:
        st.info("The host has not published the live event link yet.")
    st.warning("For a private family event, use a password-protected meeting or an unlisted/private stream. Do not publish a public meeting link if you want to restrict attendance.")

def gallery_page():
    page_title("📸 Photo & Video Gallery", "The little moments that became our biggest memories.")
    with db() as con:
        rows = con.execute("SELECT * FROM gallery ORDER BY id DESC").fetchall()
    if not rows:
        st.info("The family will add photographs and videos here soon.")
    cols = st.columns(3)
    for i, row in enumerate(rows):
        with cols[i % 3]:
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            show_media(row["file_path"], row["media_type"], row["caption"])
            if row["caption"]:
                st.caption(row["caption"])
            st.markdown("</div>", unsafe_allow_html=True)

def journey_page():
    page_title("🗓️ The Journey of Our Baby", "Twelve months. Countless firsts. A lifetime of love.")
    with db() as con:
        rows = con.execute("SELECT * FROM milestones ORDER BY sort_order,id").fetchall()
    if not rows:
        st.info("The baby's milestones will be added here by the family.")
    for row in rows:
        with st.container(border=True):
            st.markdown(f"### {row['title']}")
            if row["date_text"]:
                st.caption(row["date_text"])
            st.write(row["description"])
            if row["image_path"]:
                show_media(row["image_path"])

def family_tree_page():
    page_title("🌳 Our Family Tree", "A family is where a little life is surrounded by love.")
    with db() as con:
        members = con.execute("SELECT * FROM family_members ORDER BY generation, sort_order, id").fetchall()
    if not members:
        st.info("The family tree is being prepared by the family.")
        return
    group_labels = {0: "Grandparents & Elders", 1: "Parents & Adult Family", 2: "Children & Cousins", 3: "Younger Generation"}
    grouped = {}
    for member in members:
        grouped.setdefault(member["generation"], []).append(member)
    for generation in sorted(grouped):
        st.markdown(f"### {group_labels.get(generation, f'Generation {generation}')}")
        st.markdown("<div style='text-align:center;color:#c6a36a;font-size:22px'>│<br>▼</div>", unsafe_allow_html=True)
        cols = st.columns(min(4, len(grouped[generation])))
        for i, member in enumerate(grouped[generation]):
            with cols[i % len(cols)]:
                with st.container(border=True):
                    if member["photo_path"] and local_path(member["photo_path"]):
                        show_media(member["photo_path"])
                    else:
                        st.markdown("<div style='font-size:42px;text-align:center'>👤</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align:center;font-weight:700'>{member['name']}</div><div style='text-align:center;color:#987b4d;font-size:12px'>{member['relation']}</div>", unsafe_allow_html=True)
    st.caption("Family members are arranged by generation. Each person's relationship to the baby is shown below their name.")

def guestbook_page():
    page_title("💌 Digital Guestbook", "Leave a blessing our little one can read in the years to come.")
    st.markdown("You can share a written message, emoji, photograph, GIF or short video. Messages are reviewed by the family before appearing publicly.")
    with st.form("guest_message_form", clear_on_submit=True):
        name = st.text_input("Your name *", max_chars=80)
        relation = st.text_input("Your relationship with the baby (optional)", max_chars=80)
        message = st.text_area("Your blessing or message *", max_chars=1500, placeholder="May your life always be filled with happiness...")
        attachment = st.file_uploader("Add a photo, GIF or short video (optional)", type=["jpg","jpeg","png","webp","gif","mp4","mov","webm"])
        submitted = st.form_submit_button("Send my blessing", type="primary")
    if submitted:
        if not name.strip() or not message.strip():
            st.error("Please enter your name and a message.")
        else:
            media_path = save_upload(attachment, "guest") if attachment else ""
            media_type = "video" if attachment and Path(attachment.name).suffix.lower() in [".mp4",".mov",".webm"] else "image"
            with db() as con:
                con.execute("""INSERT INTO blessings(guest_name,relation,message,media_path,media_type,created_at,approved)
                VALUES(?,?,?,?,?,?,0)""", (name.strip(), relation.strip(), message.strip(), media_path, media_type, datetime.now().isoformat(timespec="minutes")))
            st.success("Thank you! Your blessing has been sent to the family for approval.")
    st.subheader("Blessings shared by family and friends")
    with db() as con:
        rows = con.execute("SELECT * FROM blessings WHERE approved=1 AND relation != 'Time Capsule' ORDER BY id DESC").fetchall()
    if not rows:
        st.caption("Approved guest wishes will appear here.")
    for row in rows:
        with st.container(border=True):
            st.markdown(f"**{row['guest_name']}**  ·  <span class='small-muted'>{row['relation'] or 'Well-wisher'}</span>", unsafe_allow_html=True)
            st.write(row["message"])
            if row["media_path"]:
                show_media(row["media_path"], row["media_type"])

def quiz_page():
    page_title("🧠 How Well Do You Know the Baby?", "Play the birthday quiz and see how well you know our little star.")
    with db() as con:
        qs = con.execute("SELECT * FROM questions ORDER BY id").fetchall()
    if not qs:
        st.info("The family is preparing a fun quiz. Please visit again soon.")
        return
    with st.form("baby_quiz"):
        guest = st.text_input("Your name")
        answers = {}
        for i, q in enumerate(qs):
            st.markdown(f"**{i+1}. {q['question']}**")
            opts = [q["a"], q["b"], q["c"], q["d"]]
            answers[q["id"]] = st.radio("Choose one:", opts, key=f"q_{q['id']}", index=None, label_visibility="collapsed")
        done = st.form_submit_button("Submit my answers", type="primary")
    if done:
        if not guest.strip():
            st.error("Please enter your name.")
        elif any(v is None for v in answers.values()):
            st.error("Please answer every question.")
        else:
            score = 0
            for q in qs:
                opts = [q["a"], q["b"], q["c"], q["d"]]
                if answers[q["id"]] == opts[int(q["correct"])]:
                    score += 1
            with db() as con:
                con.execute("INSERT INTO quiz_scores(guest_name,score,total,created_at) VALUES(?,?,?,?)",
                            (guest.strip(), score, len(qs), datetime.now().isoformat(timespec="minutes")))
            st.success(f"Your score: {score} out of {len(qs)}. Thank you for playing!")
            st.balloons()

def gifts_page():
    page_title("🎁 Gifts & Blessings", "Your presence is the greatest gift. Contributions are entirely optional.")
    st.markdown(f"<div class='section-card'><h3>A little gift, if you wish</h3><p>{get_setting('gift_note')}</p></div>", unsafe_allow_html=True)
    qr = get_setting("payment_qr_path")
    p = local_path(qr)
    if p:
        st.image(str(p), caption="Scan using your UPI app", width=320)
    else:
        st.info("The family has not added a gift QR code yet.")
    if get_setting("upi_id"):
        st.code(get_setting("upi_id"), language=None)
        st.caption("Please verify the recipient name in your UPI app before making any payment.")
    st.warning("Payments are made directly through your chosen UPI/payment app. This website does not collect, process, or store payment credentials or card details. Never share your UPI PIN or OTP.")
    st.markdown("### Prefer a message instead?")
    st.write("You can leave a birthday blessing in the Digital Guestbook without making a payment.")

def capsule_page():
    page_title("⏳ A Time Capsule for the Future", "Messages, memories and wishes to be opened on the 18th birthday.")
    st.markdown(f"<div class='section-card'><h3>Dear future you...</h3><p>{get_setting('time_capsule_note')}</p></div>", unsafe_allow_html=True)
    st.markdown("### Add a message to the time capsule")
    with st.form("capsule_form", clear_on_submit=True):
        name = st.text_input("Your name")
        message = st.text_area("Your message for the baby's future", max_chars=2000)
        submitted = st.form_submit_button("Submit future message", type="primary")
    if submitted:
        if name.strip() and message.strip():
            with db() as con:
                con.execute("""INSERT INTO blessings(guest_name,relation,message,media_path,media_type,created_at,approved)
                VALUES(?,?,?,'','','',0)""", (name.strip(), "Time Capsule", message.strip()))
            st.success("Your message has been sent to the family for the time capsule.")
        else:
            st.error("Please enter your name and message.")
    st.subheader("Messages preserved for the future")
    with db() as con:
        capsule_rows = con.execute("SELECT guest_name,message,created_at FROM blessings WHERE approved=1 AND relation='Time Capsule' ORDER BY id DESC").fetchall()
    if not capsule_rows:
        st.caption("Approved time-capsule messages will appear here.")
    for item in capsule_rows:
        with st.container(border=True):
            st.markdown(f"**{item['guest_name']}**")
            st.write(item["message"])

def admin_dashboard():
    if not admin_login():
        return
    page_title("🔐 Administrator Dashboard", "Only the family administrator can manage birthday content.")
    st.success("You are signed in as administrator.")
    if st.button("Log out"):
        st.session_state.admin_ok = False
        st.rerun()

    tabs = st.tabs(["Website settings & banner", "Invitation & live", "Documentary", "Gallery", "Baby journey", "Family tree", "Quiz manager", "Guestbook moderation", "Gift QR & capsule", "Export / backup"])

    with tabs[0]:
        st.subheader("Website identity")
        with st.form("settings_identity"):
            baby = st.text_input("Baby's display name", get_setting("baby_name"))
            tagline = st.text_input("Tagline", get_setting("tagline"))
            banner = st.file_uploader("Upload / replace homepage banner", type=["jpg", "jpeg", "png", "webp"], help="This image replaces the default gradient banner.")
            if st.form_submit_button("Save website identity and banner", type="primary"):
                set_setting("baby_name", baby); set_setting("tagline", tagline)
                if banner:
                    set_setting("banner_path", save_upload(banner, "banner"))
                st.success("Website identity and banner updated.")
        current_banner = local_path(get_setting("banner_path"))
        if current_banner:
            st.image(str(current_banner), caption="Current homepage banner", use_container_width=True)
            if st.button("Remove custom banner"):
                set_setting("banner_path", "")
                st.rerun()
        else:
            st.info("No custom banner uploaded. The default banner is displayed.")

    with tabs[1]:
        st.subheader("Invitation and event details")
        with st.form("settings_event"):
            bdate = st.text_input("Birthday date", get_setting("birthday_date"))
            event_dt = st.text_input("Live event date and time", get_setting("event_datetime"))
            inv = st.text_area("Invitation message", get_setting("invitation_text"), height=120)
            platform = st.text_input("Live platform", get_setting("live_platform"))
            live = st.text_input("Live meeting / stream URL (https://...)", get_setting("live_url"))
            if st.form_submit_button("Save invitation and live details", type="primary"):
                set_setting("birthday_date", bdate); set_setting("event_datetime", event_dt)
                set_setting("invitation_text", inv); set_setting("live_platform", platform)
                set_setting("live_url", live)
                st.success("Event details saved.")

    with tabs[2]:
        st.subheader("Upload birthday documentary")
        up = st.file_uploader("Choose documentary video", type=["mp4","mov","webm"], key="doc_upload")
        if st.button("Upload / replace documentary", type="primary"):
            if up:
                set_setting("documentary_path", save_upload(up, "documentary"))
                st.success("Documentary uploaded.")
            else:
                st.error("Choose a video first.")
        current = get_setting("documentary_path")
        if current:
            show_media(current, "video")

    with tabs[3]:
        st.subheader("Add photos and videos to the gallery")
        with st.form("gallery_add", clear_on_submit=True):
            caption = st.text_input("Caption")
            file = st.file_uploader("Select image, GIF or video", type=["jpg","jpeg","png","webp","gif","mp4","mov","webm"])
            add = st.form_submit_button("Add to gallery", type="primary")
        if add:
            if file:
                ext = Path(file.name).suffix.lower()
                mt = "video" if ext in [".mp4",".mov",".webm"] else "image"
                path = save_upload(file, "gallery")
                with db() as con:
                    con.execute("INSERT INTO gallery(caption,file_path,media_type,created_at) VALUES(?,?,?,?)",
                                (caption, path, mt, datetime.now().isoformat(timespec="minutes")))
                st.success("Gallery item added.")
            else:
                st.error("Select a file.")
        with db() as con:
            rows = con.execute("SELECT * FROM gallery ORDER BY id DESC").fetchall()
        for r in rows:
            col1, col2 = st.columns([4,1])
            with col1: st.write(f"**{r['caption'] or 'Untitled'}** — {r['file_path']}")
            with col2:
                if st.button("Delete", key=f"delgal{r['id']}"):
                    with db() as con: con.execute("DELETE FROM gallery WHERE id=?", (r["id"],))
                    st.rerun()

    with tabs[4]:
        st.subheader("Add a milestone to the baby's journey")
        with st.form("milestone_add", clear_on_submit=True):
            title = st.text_input("Milestone title", placeholder="First smile")
            date_text = st.text_input("Date / age", placeholder="2 months")
            desc = st.text_area("Description")
            image_file = st.file_uploader("Optional photograph", type=["jpg","jpeg","png","webp"], key="milestone_img")
            order = st.number_input("Display order", min_value=0, step=1)
            add = st.form_submit_button("Add milestone", type="primary")
        if add:
            if title.strip():
                ip = save_upload(image_file, "milestone") if image_file else ""
                with db() as con:
                    con.execute("INSERT INTO milestones(title,date_text,description,image_path,sort_order) VALUES(?,?,?,?,?)",
                                (title, date_text, desc, ip, int(order)))
                st.success("Milestone added.")
            else:
                st.error("A milestone title is required.")
        with db() as con:
            rows = con.execute("SELECT * FROM milestones ORDER BY sort_order,id").fetchall()
        for r in rows:
            col1, col2 = st.columns([4,1])
            with col1: st.write(f"**{r['title']}** — {r['date_text']}")
            with col2:
                if st.button("Delete", key=f"delmile{r['id']}"):
                    with db() as con: con.execute("DELETE FROM milestones WHERE id=?", (r["id"],))
                    st.rerun()

    with tabs[5]:
        st.subheader("Manage the family tree")
        st.caption("Generation 0: grandparents/elders · 1: parents and adult relatives · 2: children/cousins · 3: younger generation")
        with st.form("family_member_add", clear_on_submit=True):
            member_name = st.text_input("Family member name")
            member_relation = st.text_input("Relationship with the baby (e.g. Mother, Grandfather, Aunt)")
            generation = st.selectbox("Generation", [0, 1, 2, 3], format_func=lambda x: {0:"Grandparents & elders",1:"Parents & adult relatives",2:"Children & cousins",3:"Younger generation"}[x])
            sort_order = st.number_input("Display order within generation", min_value=0, step=1)
            member_photo = st.file_uploader("Portrait photograph (optional)", type=["jpg", "jpeg", "png", "webp"], key="family_member_photo")
            add_member = st.form_submit_button("Add family member", type="primary")
        if add_member:
            if member_name.strip() and member_relation.strip():
                photo_path = save_upload(member_photo, "family") if member_photo else ""
                with db() as con:
                    con.execute("INSERT INTO family_members(name,relation,photo_path,generation,sort_order) VALUES(?,?,?,?,?)", (member_name.strip(), member_relation.strip(), photo_path, generation, int(sort_order)))
                st.success("Family member added to the tree.")
            else:
                st.error("Please enter both the family member's name and relationship.")
        with db() as con:
            family_rows = con.execute("SELECT * FROM family_members ORDER BY generation,sort_order,id").fetchall()
        for member in family_rows:
            left, right = st.columns([5, 1])
            left.write(f"**{member['name']}** — {member['relation']} (Generation {member['generation']})")
            if right.button("Delete", key=f"delete_family_{member['id']}"):
                with db() as con:
                    con.execute("DELETE FROM family_members WHERE id=?", (member["id"],))
                st.rerun()

    with tabs[6]:
        st.subheader("Create a baby quiz question")
        with st.form("quiz_add", clear_on_submit=True):
            question = st.text_input("Question")
            a = st.text_input("Option A"); b = st.text_input("Option B")
            c = st.text_input("Option C"); d = st.text_input("Option D")
            correct = st.selectbox("Correct answer", [0,1,2,3], format_func=lambda x: ["A","B","C","D"][x])
            explanation = st.text_input("Optional explanation")
            add = st.form_submit_button("Add quiz question", type="primary")
        if add:
            if all(x.strip() for x in [question,a,b,c,d]):
                with db() as con:
                    con.execute("INSERT INTO questions(question,a,b,c,d,correct,explanation) VALUES(?,?,?,?,?,?,?)",
                                (question,a,b,c,d,correct,explanation))
                st.success("Question added.")
            else:
                st.error("Fill in the question and all four options.")
        with db() as con:
            rows = con.execute("SELECT * FROM questions ORDER BY id").fetchall()
        for q in rows:
            col1, col2 = st.columns([4,1])
            with col1: st.write(q["question"])
            with col2:
                if st.button("Delete", key=f"delq{q['id']}"):
                    with db() as con: con.execute("DELETE FROM questions WHERE id=?", (q["id"],))
                    st.rerun()

    with tabs[7]:
        st.subheader("Review guest blessings")
        with db() as con:
            rows = con.execute("SELECT * FROM blessings ORDER BY id DESC").fetchall()
        if not rows:
            st.info("No guest submissions yet.")
        for r in rows:
            with st.container(border=True):
                st.write(f"**{r['guest_name']}** · {r['relation'] or 'Guest'}")
                st.write(r["message"])
                if r["media_path"]:
                    show_media(r["media_path"], r["media_type"])
                c1,c2 = st.columns(2)
                if not r["approved"]:
                    if c1.button("Approve", key=f"approve{r['id']}"):
                        with db() as con: con.execute("UPDATE blessings SET approved=1 WHERE id=?", (r["id"],))
                        st.rerun()
                else:
                    c1.success("Approved")
                if c2.button("Delete", key=f"delbless{r['id']}"):
                    with db() as con: con.execute("DELETE FROM blessings WHERE id=?", (r["id"],))
                    st.rerun()

    with tabs[8]:
        st.subheader("Gift section and time capsule")
        with st.form("gift_settings"):
            qr_file = st.file_uploader("Upload UPI / payment QR image", type=["png","jpg","jpeg"], key="qr")
            upi = st.text_input("UPI ID (optional)", get_setting("upi_id"))
            gift_note = st.text_area("Gift section message", get_setting("gift_note"))
            capsule_note = st.text_area("Time capsule introduction", get_setting("time_capsule_note"))
            save = st.form_submit_button("Save gift and capsule settings", type="primary")
        if save:
            if qr_file:
                set_setting("payment_qr_path", save_upload(qr_file, "payment_qr"))
            set_setting("upi_id", upi); set_setting("gift_note", gift_note)
            set_setting("time_capsule_note", capsule_note)
            st.success("Gift and time capsule settings saved.")
        qr = local_path(get_setting("payment_qr_path"))
        if qr: st.image(str(qr), width=220, caption="Current payment QR")

    with tabs[9]:
        st.subheader("Download database backup")
        if DB_PATH.exists():
            st.download_button("Download birthday database", DB_PATH.read_bytes(),
                               file_name="first_chapter_birthday_backup.sqlite3",
                               mime="application/x-sqlite3")
        st.caption("Uploaded media is stored in the birthday_data/uploads folder. Back up that folder separately.")
        st.subheader("Quiz leaderboard")
        with db() as con:
            scores = con.execute("SELECT guest_name,score,total,created_at FROM quiz_scores ORDER BY score DESC,id ASC").fetchall()
        if scores:
            st.dataframe([dict(x) for x in scores], use_container_width=True)
        else:
            st.caption("No quiz scores yet.")

def main():
    st.sidebar.markdown("## ✨ The First Chapter")
    st.sidebar.caption("365 Days of Love")
    pages = {
        "Home": guest_home,
        "Digital Invitation": invitation_page,
        "Birthday Documentary": documentary_page,
        "Live Celebration": live_page,
        "Photo & Video Gallery": gallery_page,
        "Baby's Journey": journey_page,
        "Family Tree": family_tree_page,
        "Interactive Baby Quiz": quiz_page,
        "Digital Guestbook": guestbook_page,
        "Gifts & Blessings": gifts_page,
        "Time Capsule": capsule_page,
        "Administrator": admin_dashboard,
    }
    current = st.session_state.pop("requested_page", None)
    if current not in pages:
        current = st.session_state.get("current_page", "Home")
    if current not in pages:
        current = "Home"
    selected = st.sidebar.radio("Explore", list(pages.keys()), index=list(pages.keys()).index(current))
    st.session_state["current_page"] = selected
    st.sidebar.markdown("---")
    st.sidebar.caption("Made with love for one very special first birthday.")
    pages[selected]()
    st.markdown("---")
    st.markdown("<div style='text-align:center;color:#8992a1;font-size:12px;padding:12px'>THE FIRST CHAPTER · 365 DAYS OF LOVE<br>Celebrating a little life and a lifetime of possibilities.</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
