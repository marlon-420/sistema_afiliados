from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField
from wtforms.validators import DataRequired

class VentaForm(FlaskForm):
    modelo = StringField('Modelo', validators=[DataRequired()])
    talla = IntegerField('Talla', validators=[DataRequired()])
    fecha = DateField('Fecha', format='%Y-%m-%d')
