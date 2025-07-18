import os
import hashlib
from datetime import date,datetime
from dotenv import load_dotenv
from flask import Flask, abort, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
#oldversion of GRAVATOR
#from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user,login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
#form.py
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm, ContactForm
#emailsender
from emailsender import EmailAutomation
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#load environment variable
load_dotenv('.env')

EMAIL_ID = os.getenv('EMAIL_ID')
SENDER_MAIL_ID = os.getenv('SENDER_MAIL_ID')

#sender object and msg variable intializing
msg = MIMEMultipart()
msg['Subject'] = 'Contact mail from BLOG Post Website'
msg['From'] = EMAIL_ID
msg['To'] = SENDER_MAIL_ID
sender = EmailAutomation()

# For adding profile images to the comment section
def generate_gravatar(email, size=100, default='retro', rating='g'):
    email_hash = hashlib.md5(email.strip().lower().encode('utf-8')).hexdigest()
    return f"https://www.gravatar.com/avatar/{email_hash}?s={size}&d={default}&r={rating}"
#the below gravatar declaring method is old!
# gravatar = Gravatar(app,
#                     size=100,
#                     rating='g',
#                     default='retro',
#                     force_default=False,
#                     force_lower=False,
#                     use_ssl=False,
#                     base_url=None)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_KEY')
app.jinja_env.filters['gravatar'] = generate_gravatar
app.jinja_env.globals['generate_gravatar'] = generate_gravatar
ckeditor = CKEditor(app)
bootstrap = Bootstrap(app)
#Bootstrap(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect anonymous users to login

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

# CREATE DATABASE
class Base(DeclarativeBase):
    pass
# should read:
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///posts.db")
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLES
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    # Create reference to the User object. The "posts" refers to the posts property in the User class.
    author = relationship("User", back_populates="posts")
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    # Parent relationship to the comments
    comments = relationship("Comment", back_populates="parent_post")


# Create a User table for all your registered users
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    # This will act like a list of BlogPost objects attached to each User.
    # The "author" refers to the author property in the BlogPost class.
    posts = relationship("BlogPost", back_populates="author")
    # Parent relationship: "comment_author" refers to the comment_author property in the Comment class.
    comments = relationship("Comment", back_populates="comment_author")

# Create a table for the comments on the blog posts
class Contact(db.Model):
    __tablename__ = "contact"
    user_id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100),nullable=False)
    phone: Mapped[str] = mapped_column(String(12),nullable=False)
    email: Mapped[str] = mapped_column(String(100),nullable=False)
    message: Mapped[str] = mapped_column(Text,nullable=False)

# Create a Table for the contact msg from user orelse you can sent email at that if it worked!
class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    # Child relationship:"users.id" The users refers to the tablename of the User class.
    # "comments" refers to the comments property in the User class.
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")
    # Child Relationship to the BlogPosts
    post_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost", back_populates="comments")

with app.app_context():
    db.create_all()

#  Use a decorator so only an admin user can create a new post
# Create an admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function

# Custom filter to generate MD5 hash for Gravatar
@app.template_filter('md5')
def md5_filter(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()

#  Use Werkzeug to hash the user's password when creating a new user.
# Register new users into the User database
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        # Check if user email is already present in the database.
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if user:
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(email = form.email.data,
                        name = form.name.data,
                        password = hash_and_salted_password)
        db.session.add(new_user)
        db.session.commit()
        # This line will authenticate the user with Flask-Login
        login_user(new_user)
        return redirect(url_for("get_all_posts"))
    return render_template("register.html", form=form, current_user=current_user)


# Retrieve a user from the database based on their email.
@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        # Note, email in db is unique so will only have one result.
        user = result.scalar()
        # Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('get_all_posts'))

    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))

#  I also got a 404 error coming from here:
#
# # create a user loader callback
# @login_manager.user_loader
# def load_user(user_id):
#     return db.get_or_404(User, user_id)

# I solved it by clearing the cache of my browser first.
# I think it's because the browser remembered who was logged in,
# but then off course could not find back that user because you had just deleted the .db
@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts, current_user=current_user,year= datetime.now().year)


# Add a POST method to be able to post comments
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    # Add the CommentForm to the route
    comment_form = CommentForm()
    # Only allow logged-in users to comment on posts
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))

        new_comment = Comment(
            text=comment_form.comment_text.data,
            comment_author=current_user,
            parent_post=requested_post
        )
        db.session.add(new_comment)
        db.session.commit()
    return render_template("post.html", post=requested_post, current_user=current_user, form=comment_form,year= datetime.now().year)


# Use a decorator so only an admin user can create new posts
@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, current_user=current_user,year= datetime.now().year)


# Use a decorator so only an admin user can edit a post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True, current_user=current_user,year= datetime.now().year)


# Use a decorator so only an admin user can delete a post
@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    year_increment = datetime.now().year - 2024
    age = 18 + year_increment
    return render_template("about.html", current_user=current_user,age=age,year= datetime.now().year)


@app.route("/contact", methods=["GET", "POST"])
@login_required
def contact():
    cond=False
    form = ContactForm()
    if form.validate_on_submit():
        cond=True
        name=form.name.data.strip("'")
        email=form.email.data.strip("'")
        phone=form.phone.data.strip("'")
        message=form.message.data

        #mail body
        body = MIMEText(f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.5;">
            <p>Hello Ganesh,</p>

            <p>You have received a new message from the contact form on your RawPol website.</p>

            <hr style="border: 1px solid #ccc;">

            <p>📩 <b>Message:</b><br>
            {message}</p>

            <p>👤 <b>Sender Details:</b><br>
            <b>Name:</b> {name}<br>
            <b>Email:</b> {email}<br>
            <b>Phone:</b> {phone}</p>

            <hr style="border: 1px solid #ccc;">

            <p>Best regards,<br>
            {name}</p>
          </body>
        </html>
        """, "html")

        #email sending
        msg.attach(body)
        sender.emailsender(msg)

        new_contact=Contact(user_id=current_user.id,
                            name=form.name.data,
                            email=form.email.data,
                            phone=form.phone.data,
                            message=form.message.data)
        db.session.add(new_contact)
        db.session.commit()
    return render_template("contact.html",form=form, current_user=current_user,year= datetime.now().year,msg_sent=cond)


if __name__ == "__main__":
    app.run(debug=False, port=713)