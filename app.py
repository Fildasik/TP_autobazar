from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from forms import RegistrationForm, LoginForm, CarForm
from models import db, User, Car
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'toto_je_tajny_klic'

# Připojení k MySQL databázi (nahraď "tvuj_heslo" svým heslem)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Filda942703@localhost/autobazar'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def create_tables():
    db.create_all()

def log_user_login(user):
    """Uloží do users.json záznam o přihlášeném uživateli (demo)."""
    login_data = {"email": user.username, "password": user.password}
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []
    data.append(login_data)
    with open('users.json', 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Registrace OK. Přihlašte se.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            log_user_login(user)
            flash('Přihlášeno!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Neplatné údaje.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('Odhlášeno!', 'info')
    return redirect(url_for('home'))

# Mapování značek na dostupné modely
brand_models = {
    'skoda':        ['Octavia', 'Superb', 'Fabia', 'Kamiq', 'Karoq', 'Kodiaq', 'Scala'],
    'porsche':      ['911', 'Panamera', 'Cayenne', 'Macan', 'Taycan', 'Boxster', '718 Spyder'],
    'vw':           ['Golf', 'Passat', 'Tiguan', 'Touran', 'Polo', 'Arteon', 'T-Roc'],
    'bmw':          ['3 Series', '5 Series', '7 Series', 'X3', 'X5', 'i3', 'i8'],
    'mercedes':     ['C-Class', 'E-Class', 'S-Class', 'GLE', 'GLC', 'A-Class', 'CLA'],
    'toyota':       ['Corolla', 'Camry', 'RAV4', 'Yaris', 'Highlander', 'Prius', 'C-HR'],
    'honda':        ['Civic', 'Accord', 'CR-V', 'HR-V', 'Jazz', 'Pilot', 'Odyssey'],
    'ford':         ['Focus', 'Mondeo', 'Fiesta', 'Mustang', 'Kuga', 'Explorer', 'Edge'],
    'audi':         ['A3', 'A4', 'A6', 'Q5', 'Q7', 'Q8', 'TT'],
    'hyundai':      ['i30', 'i20', 'Tucson', 'Santa Fe', 'Kona', 'Sonata', 'Elantra'],
    'kia':          ['Ceed', 'Sportage', 'Rio', 'Sorento', 'Stonic', 'Optima', 'Picanto'],
    'renault':      ['Clio', 'Megane', 'Captur', 'Kadjar', 'Scenic', 'Talisman', 'Laguna'],
    'nissan':       ['Qashqai', 'Juke', 'X-Trail', 'Micra', 'Leaf', 'Navara', 'GT-R'],
    'peugeot':      ['208', '308', '508', '2008', '3008', '5008', 'Rifter'],
    'mazda':        ['Mazda2', 'Mazda3', 'Mazda6', 'CX-3', 'CX-5', 'MX-5', 'CX-30'],
    'jeep':         ['Wrangler', 'Renegade', 'Compass', 'Cherokee', 'Grand Cherokee', 'Gladiator'],
    'tesla':        ['Model S', 'Model 3', 'Model X', 'Model Y', 'Roadster'],
    'ferrari':      ['488', '812 Superfast', 'Portofino', 'F8 Tributo', 'SF90 Stradale', 'Roma'],
    'lamborghini':  ['Huracán', 'Aventador', 'Urus', 'Gallardo', 'Murciélago', 'Sian', 'Diablo'],
    'volvo':        ['XC40', 'XC60', 'XC90', 'S60', 'S90', 'V60', 'V90']
}

@app.route('/add_car', methods=['GET', 'POST'])
@login_required
def add_car():
    if request.method == 'POST':
        # 1) Z request.form dostaneme surové hodnoty:
        raw_price = request.form.get('price', '')
        raw_mileage = request.form.get('mileage', '')

        # 2) Odstraníme čárky (1,000,000 -> 1000000)
        raw_price = raw_price.replace(',', '').strip()
        raw_mileage = raw_mileage.replace(',', '').strip()

        # 3) Přepíšeme data v request.form, aby do WTForms šly jen číslice
        new_form_data = request.form.copy()
        new_form_data['price'] = raw_price
        new_form_data['mileage'] = raw_mileage

        # 4) Teď vytvoříme formulář s vyčištěnými daty
        form = CarForm(new_form_data)

        # Nastavíme dynamicky choices pro model (podle vybrané značky)
        selected_brand = form.brand.data
        if selected_brand in brand_models:
            form.model.choices = [(m, m) for m in brand_models[selected_brand]]
        else:
            form.model.choices = []

        # 5) Ověříme validitu a případně uložíme do DB
        if form.validate_on_submit():
            new_car = Car(
                brand=form.brand.data,
                model=form.model.data,
                year=form.year.data,
                price=form.price.data,
                mileage=form.mileage.data,
                owner_id=current_user.id
            )
            db.session.add(new_car)
            db.session.commit()
            flash('Auto přidáno.', 'success')
            return redirect(url_for('my_cars'))
        else:
            # Pokud je formulář nevalidní, znovu zobrazíme stránku s chybami
            return render_template('add_car.html', form=form)

    # Pokud metoda není POST (tj. GET), tak prostě zobrazíme prázdný formulář
    form = CarForm()
    return render_template('add_car.html', form=form)

@app.route('/my_cars')
@login_required
def my_cars():
    user_cars = Car.query.filter_by(owner_id=current_user.id).all()
    return render_template('my_cars.html', cars=user_cars)

@app.route('/delete_car/<int:car_id>', methods=['POST'])
@login_required
def delete_car(car_id):
    car = Car.query.get_or_404(car_id)
    if car.owner_id != current_user.id:
        flash('Chybí oprávnění.', 'danger')
        return redirect(url_for('my_cars'))
    db.session.delete(car)
    db.session.commit()
    flash('Auto smazáno.', 'success')
    return redirect(url_for('my_cars'))

if __name__ == '__main__':
    print("Aktuální pracovní adresář:", os.getcwd())
    print("Soubory:", os.listdir(os.getcwd()))
    app.run(debug=True)
