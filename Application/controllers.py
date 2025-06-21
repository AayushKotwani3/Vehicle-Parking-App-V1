from flask import Flask,render_template,redirect,request,url_for,flash
from flask import current_app as app
from .models import * #inheriting models module to make indirect connection with app.py

@app.route('/')
def home():
    return render_template('home.html')

#register endpoint
@app.route('/register',methods=['GET','POST'])
def register():
    #fetching the registration details from registration form
    if request.method=='POST':
        name=request.form.get('name')
        email=request.form.get('email')
        address=request.form.get('address')
        pincode=request.form.get('pincode')
        password=request.form.get('password')

        #checking if this user already exists
        this_user=User.query.filter_by(email=email).first() # checking user existence with the help of email

        if this_user:
            return "User already registered"
        
        #Adding user to database
        else:
            new_user=User(name=name,email=email,address=address,pincode=pincode,password=password)
            db.session.add(new_user)
            db.session.commit()
            # return redirect('/login')
            return redirect(url_for('login'))
    return render_template('registration.html')    


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('password')

        #Fetching user from db
        this_user=User.query.filter_by(email=email).first()

        if this_user:
            if this_user.password==password:
                if this_user.role=='admin':
                    return redirect('/admin')
                else:
                    return redirect(f'/home/{this_user.id}')
            else:
                return"Incorrect Password"
        else:
            return "User does not exist first register"
    return render_template('login.html')            
                
@app.route('/admin')
def admin_dash():
    return render_template('admin_dashboard.html')

@app.route('/home/<int:user_id>')
def user_dash():
    return render_template('user_dashboard.html')

@app.route('/add-new-lot',methods=['GET','POST'])
def add_new_lot():
    #fetching the Parking lots details from registration form

    if request.method=='POST':
        prime_location_name=request.form.get('prime_location_name')
        address=request.form.get('address')
        pincode=request.form.get('pincode')
        parking_spot_price=request.form.get('parking_spot_price')
        max_spots=request.form.get('max_spots')

        #checking if parking lot already exists
        this_parking_lot=Parkinglot.query.filter_by(address=address,pincode=pincode).first() # checking user existence with the help of email

        if this_parking_lot:
            return "Parking lot with same address already exist"

        #Adding Parking Lots to database
        new_parking_lot=Parkinglot(prime_location_name=prime_location_name,address=address,pincode=pincode, price=parking_spot_price,maximum_spots=max_spots)
        db.session.add(new_parking_lot)
        db.session.commit()

        return redirect(url_for('admin_dash'))


    return render_template('add_parkinglot.html')