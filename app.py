from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, UserMixin, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from cloudipsp import Api, Checkout

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cars.db'
app.config['SECRET_KEY'] = 'd9b6bd77a7796434cbbc92cd530206606371024f'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
manager = LoginManager(app)


@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return f"{self.id}. {self.username}"


class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(250), nullable=False)
    make = db.Column(db.String(30), nullable=False)
    model = db.Column(db.String(30), nullable=False)
    car_body = db.Column(db.String(30), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    producing = db.Column(db.String(30), nullable=False)
    condition = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"{self.id}. {self.model} - {self.make}. {self.year}"


@app.route('/')
def index():
    car = Car.query.order_by(Car.id).all()
    return render_template('index.html', cars=car)


@app.route('/register', methods=("POST", "GET"))
def register():
    if request.method == "POST":
        try:
            hash = generate_password_hash(request.form.get('password'))
            user = User(username=request.form.get('username'), password=hash)
            db.session.add(user)
            db.session.flush()
            db.session.commit()
            return redirect(url_for('login'))
        except:
            db.session.rollback()
    return render_template('register.html')


@app.route('/login', methods=("POST", "GET"))
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if username and password:
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            print("Error auth!")
    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/create', methods=("POST", "GET"))
@login_required
def create():
    if request.method == "POST":
        try:
            image = request.form.get("image")
            make = request.form.get("make")
            model = request.form.get("model")
            car_body = request.form.get("car_body")
            year = request.form.get("year")
            producing = request.form.get("producing")
            condition = request.form.get("condition")
            print("1")
            car = Car(image=image,
                      make=make,
                      model=model,
                      car_body=car_body,
                      year=year,
                      producing=producing,
                      condition=condition)
            print("2")
            db.session.add(car)
            print("3")
            db.session.flush()
            print("4")
            db.session.commit()
            print("commit")
            return redirect(url_for('index'))
        except:
            print("5")
            db.session.rollback()
    return render_template('create.html')


@app.route('/detail-<int:id>')
def detail(id):
    car = Car.query.get(id)
    return render_template('detail.html', car=car)


if __name__ == '__main__':
    app.run(debug=True)
