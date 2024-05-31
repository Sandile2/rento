from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from forms import LoginForm, RegistrationForm, PropertyForm
from models import db, User, Property

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role=form.role.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'landlord':
        properties = Property.query.filter_by(owner_id=current_user.id).all()
        return render_template('landlord_dashboard.html', properties=properties)
    else:
        properties = Property.query.all()
        return render_template('tenant_dashboard.html', properties=properties)

@app.route('/add_property', methods=['GET', 'POST'])
@login_required
def add_property():
    form = PropertyForm()
    if form.validate_on_submit():
        property = Property(
            title=form.title.data, 
            description=form.description.data,
            rent=form.rent.data,
            owner_id=current_user.id
        )
        db.session.add(property)
        db.session.commit()
        flash('Property added successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_property.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
