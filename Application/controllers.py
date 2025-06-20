from flask import Flask,render_template,redirect,request
from flask import current_app as app
from .models import * #inheriting models module to make indirect connection with app.py

@app.route('/')
def home():
    return render_template('home.html')

