======================================================
           RawPol BLOGGING WEBSITE - README
======================================================

Project Name: RawPol(Raw Politics) Blogging Website  
Developer: Ganesh Arumugam  
Technologies Used: Flask, HTML/CSS, Bootstrap, SQLite, SQLAlchemy, Flask-Login, WTForms, Jinja2  
Purpose: A personal blogging platform where users can create accounts, write blog posts, contact admin, and more.

------------------------------------------------------
📁 PROJECT STRUCTURE
------------------------------------------------------

/project-root
│
├── main.py                  → Main Flask app
├── emailsender.py           → SMTP email sender for contact form
├── forms.py                 → WTForms classes for forms
├── config.py                → App configuration (secret keys, SMTP, etc.)
├── /templates               → Jinja2 HTML templates
├── /static                  → CSS, JS, images
├── /instance                → SQLite DB file (auto-generated)
├── requirements.txt         → Required Python packages
└── README.txt               → You’re here!

------------------------------------------------------
🚀 FEATURES
------------------------------------------------------

✅ User Authentication (Login / Register / Logout)  
✅ Create, Edit & Delete Blog Posts  
✅ View All Posts with Pagination  
✅ Contact Admin via Contact Form  
✅ Admin Email Notifications  
✅ Secure Password Hashing  
✅ Unique Post Slugs and Routes  
✅ Mobile-Responsive UI using Bootstrap

------------------------------------------------------
⚙️ INSTALLATION
------------------------------------------------------

1. Clone the repository:
   git clone https://github.com/your-username/your-blog.git

2. Set up a virtual environment:
   python -m venv .venv
   .venv\Scripts\activate

3. Install dependencies:
   pip install -r requirements.txt

4. Run the application:
   python main.py

The app will be accessible at:
   http://127.0.0.1:713/

------------------------------------------------------
✉️ EMAIL SETUP (for contact form)
------------------------------------------------------

Using Gmail SMTP:
- Enable 2-Factor Authentication in your Gmail account
- Generate an App Password (https://myaccount.google.com/apppasswords)
- Add the following to your config file or environment:

EMAIL_ID = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"
SENDER_MAIL_ID = "admin_receiver_email@gmail.com"

------------------------------------------------------
📌 NOTES
------------------------------------------------------

- Make sure you don’t push secrets (email passwords, keys) to public repositories.
- You can easily migrate to a production DB (e.g., PostgreSQL) with SQLAlchemy.

------------------------------------------------------
📞 CONTACT
------------------------------------------------------

For questions or contributions, contact:
GANESH ARUMUGAM 
Email: ganesharumugam713@gmail.com 
GitHub: https://github.com/SerpentheDeceiver