from flask import Flask, flash, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
import sys
import requests

app = Flask(__name__)
app.secret_key = "super secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<City %r>' % self.name


db.create_all()


@app.route('/')
def index():
    weather_info = []
    for city in City.query.all():
        weather_info.append(api_connect(city.name))
        weather_info[-1]['city_id'] = city.id
    return render_template('index.html', weather_info=weather_info)


@app.route('/add', methods=['GET', 'POST'])
def add_city():
    if request.method == 'POST':
        city = request.form['city_name']
        weather = api_connect(city)
        if weather is None:
            return redirect('/')
        try:
            db.session.add(City(name=city))
            db.session.commit()
        except Exception:
            flash('The city has already been added to the list!')
        return redirect('/')
    else:
        return redirect('/')


@app.route('/delete/<city_id>', methods=['GET', 'POST'])
def delete(city_id):
    city = City.query.filter_by(id=city_id).first()
    db.session.delete(city)
    db.session.commit()
    return redirect('/')


def api_connect(city):
    api_request_params = {'q': city, 'units': 'metric', 'appid': 'b0cc95c79184774f83bdea67a950e2b6'}
    try:
        response = requests.get('http://api.openweathermap.org/data/2.5/weather', params=api_request_params)
    except (Exception, requests.RequestException):
        flash("Could'nt connect to the weather API")
        return None
    try:
        quote = response.json()
        dict_with_weather_info = {
            'weather': quote['weather'][0]['main'],
            'temp': int(round(quote['main']['temp'])),
            'city': quote['name']
        }
    except (NameError, KeyError):
        flash("The city doesn't exist!")
        return None
    return dict_with_weather_info


if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
