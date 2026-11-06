# The First Chapter — Updated Birthday Website (v2)

## New features in v2
1. **Changeable homepage banner:** Upload, preview, replace or remove your own JPG, JPEG, PNG or WEBP banner from Administrator → Website settings & banner. The custom banner replaces the default gradient banner.
2. **Clickable homepage feature cards:** Each home-page card now has an Open button that navigates directly to its relevant section.
3. **Family Tree:** Guests can view family members grouped by generation. The administrator can add a member's name, relationship to the baby, portrait photo, generation level and display order, or delete a member.

All existing features are retained: digital invitation, birthday documentary, live event link, photo/video gallery, baby milestones, interactive quiz, moderated guestbook with photo/GIF/video submissions, gift QR display, time capsule and database backup.

## Install and run
Python 3.10+ recommended.

```bash
pip install -r requirements.txt
```

Set the administrator password before launching.

**Windows PowerShell:**
```powershell
$env:FIRST_CHAPTER_ADMIN_PASSWORD="Use-A-Long-Unique-Password"
streamlit run app.py
```

**macOS/Linux:**
```bash
export FIRST_CHAPTER_ADMIN_PASSWORD="Use-A-Long-Unique-Password"
streamlit run app.py
```

Open the local URL printed by Streamlit (usually http://localhost:8501).

## Configure the website
Open **Administrator** in the sidebar and sign in.
- **Website settings & banner:** Set the baby's display name and tagline; upload/replace/remove the homepage banner.
- **Family tree:** Add relatives, relationship to baby, portrait, generation and order.
- Other tabs manage invitation/live details, documentary, gallery, milestones, quiz, guestbook moderation, payment QR and time capsule.

### Family tree generation levels
- 0 — Grandparents and elders
- 1 — Parents and adult relatives (aunts/uncles, etc.)
- 2 — Children and cousins
- 3 — Younger generation

The family tree is displayed as generation bands. It does not infer exact parent-child connections; the relationship label entered by the administrator is displayed for each person.

## Deployment and security
This is a starter app, not a security-audited production service. For public use:
- Deploy behind HTTPS on a host with persistent disk/storage.
- Keep `FIRST_CHAPTER_ADMIN_PASSWORD` secret and use a strong unique password.
- Configure upload size limits, rate limiting, CAPTCHA/spam protection, malware scanning and regular backups.
- Guest submissions remain private until approved by the administrator.
- Back up both `birthday_data/birthday.sqlite3` and `birthday_data/uploads`.
- The payment QR is displayed for guests to scan in their own UPI/payment app; the app does not process or verify payments. Never collect PINs, OTPs or banking credentials.
- Live video is hosted by a separate provider; the website links to it.
- Obtain consent before publishing guest photos/videos and avoid publishing sensitive information about children.
