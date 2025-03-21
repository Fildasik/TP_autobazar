from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, NumberRange, ValidationError

ALLOWED_DOMAINS = ["gmail.com", "seznam.cz", "email.cz", "centrum.cz"]

def validate_email_custom(form, field):
    """
    Kontrola, že:
      - email obsahuje '@',
      - před zavináčem aspoň 6 znaků,
      - doména je v ALLOWED_DOMAINS.
    """
    email = field.data
    if "@" not in email:
        raise ValidationError("Musí obsahovat '@'.")
    parts = email.split("@")
    if len(parts) != 2:
        raise ValidationError("Neplatný formát emailu.")
    local_part, domain = parts[0], parts[1]
    if len(local_part) < 6:
        raise ValidationError("Před zavináčem aspoň 6 znaků.")
    if domain not in ALLOWED_DOMAINS:
        raise ValidationError(f"Doména musí být: {', '.join(ALLOWED_DOMAINS)}.")

class RegistrationForm(FlaskForm):
    username = StringField('Email', validators=[DataRequired(), validate_email_custom])
    password = PasswordField('Heslo', validators=[
        DataRequired(),
        Length(min=6, max=20, message='Heslo: 6–20 znaků.')
    ])
    confirm_password = PasswordField('Potvrdit heslo', validators=[
        DataRequired(),
        EqualTo('password', message='Hesla se musí shodovat.')
    ])
    submit = SubmitField('Registrovat se')

class LoginForm(FlaskForm):
    username = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Heslo', validators=[DataRequired()])
    submit = SubmitField('Přihlásit se')

class CarForm(FlaskForm):
    brand = SelectField(
        'Značka',
        choices=[
            ('skoda', 'Škoda'),
            ('porsche', 'Porsche'),
            ('vw', 'Volkswagen'),
            ('bmw', 'BMW'),
            ('mercedes', 'Mercedes-Benz'),
            ('toyota', 'Toyota'),
            ('honda', 'Honda'),
            ('ford', 'Ford'),
            ('audi', 'Audi'),
            ('hyundai', 'Hyundai'),
            ('kia', 'Kia'),
            ('renault', 'Renault'),
            ('nissan', 'Nissan'),
            ('peugeot', 'Peugeot'),
            ('mazda', 'Mazda'),
            ('jeep', 'Jeep'),
            ('tesla', 'Tesla'),
            ('ferrari', 'Ferrari'),
            ('lamborghini', 'Lamborghini'),
            ('volvo', 'Volvo')
        ],
        validators=[DataRequired()]
    )
    model = SelectField('Model', choices=[], validators=[DataRequired()])
    year = IntegerField('Rok výroby', validators=[
        DataRequired(),
        NumberRange(min=1900, max=2025, message='Rok 1900–2025.')
    ])

    # Nová pole
    price = IntegerField('Cena (Kč)', validators=[
        DataRequired(),
        NumberRange(min=0, message='Cena musí být 0 nebo více.')
    ])
    mileage = IntegerField('Najeté km', validators=[
        DataRequired(),
        NumberRange(min=0, message='Najeté km musí být 0 nebo více.')
    ])

    submit = SubmitField('Přidat auto')
