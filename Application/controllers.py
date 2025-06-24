from flask import Flask,render_template,redirect,request,url_for,flash
from flask import current_app as app
from .models import * #inheriting models module to make indirect connection with app.py
from datetime import datetime,timezone

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
    admin_details=User.query.filter_by(role='admin').first()
    parking_lot_details=Parkinglot.query.all()
    return render_template('admin_dashboard.html',admin_details=admin_details,parking_lot_details=parking_lot_details)

@app.route('/home/<int:user_id>',methods=['GET','POST'])
def user_dash(user_id):

    user_details=User.query.filter_by(role='user',id=user_id).first()
    parking_records=Parkingrecords.query.filter_by(user_id=user_details.id).all()
    
    if request.method=='POST':
        key=request.form.get('key')
        search_value=request.form.get('search_value')

        if key=='pincode':
            parking_lot_details=Parkinglot.query.filter_by(is_active=True,pincode=search_value).all()
        else:
            parking_lot_details=Parkinglot.query.filter_by(is_active=True,prime_location_name=search_value).all()  

        return render_template('user_dashboard.html',user_details=user_details,parking_lot_details=parking_lot_details,parking_records=parking_records)
    else:
        parking_lot_details=Parkinglot.query.filter_by(is_active=True).all()
        return render_template('user_dashboard.html',user_details=user_details,parking_lot_details=parking_lot_details,parking_records=parking_records)


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

        #creating spots based on the lot created 

        this_parking_lot=Parkinglot.query.filter_by(address=address,pincode=pincode).first()
        max_spots=int(this_parking_lot.maximum_spots)

        for i in range(1,max_spots+1):
            new_spot=Parkingspots(lot_id=this_parking_lot.id,spot_number=i,status='A')
            db.session.add(new_spot)
            db.session.commit()

        return redirect(url_for('admin_dash'))


    return render_template('add_parkinglot.html')

@app.route('/edit-parking-lot/<int:lot_id>',methods=['GET','POST'])
def edit_parking_lot(lot_id):
    current_parking_lot=Parkinglot.query.filter_by(id=lot_id).first()

    if request.method=='POST':
        current_parking_lot.prime_location_name=request.form.get('prime_location_name')
        current_parking_lot.address=request.form.get('address')
        current_parking_lot.pincode=request.form.get('pincode')
        current_parking_lot.price=float(request.form.get('parking_spot_price'))
        current_parking_lot.maximum_spots=int(request.form.get('max_spots'))
        current_parking_lot.is_active=bool(int(request.form.get('is_active')))

        db.session.commit()
        return redirect(url_for('admin_dash'))
        


    return render_template('edit_parkinglot.html',current_parking_lot=current_parking_lot)

@app.route('/book-parking-spot/<int:user_id>/<int:lot_id>',methods=['GET','POST'])
def book_parking_lot(user_id,lot_id):
    spot_details=Parkingspots.query.filter_by(lot_id=lot_id,status='A').first()
    user_details=User.query.filter_by(role='user',id=user_id).first()
    parking_lot_details=Parkinglot.query.filter_by(id=lot_id).first()

    if request.method=='POST':
        vehicle_number=request.form.get('vehicle_number')
        new_parking_record=Parkingrecords(spot_id=spot_details.id,user_id=user_details.id,vehicle_number=vehicle_number,parking_timestamp=datetime.now(timezone.utc))
        db.session.add(new_parking_record)
        db.session.commit()

        spot_details.status='O'
        db.session.commit()

        return redirect(url_for('user_dash',user_id=user_details.id))

    return render_template('book_parkingspot.html',spot_details=spot_details,user_details=user_details,parking_lot_details=parking_lot_details)

@app.route('/release-parking-spot/<int:record_id>',methods=['GET','POST'])
def release_spot(record_id):
    parking_record=Parkingrecords.query.filter_by(id=record_id).first()

    if request.method=='POST':
        parking_spot=Parkingspots.query.filter_by(id=parking_record.spot_id).first()

        leaving_timestamp=request.form.get('leaving_time')

        leaving_time_for_db=datetime.strptime(leaving_timestamp,'%d-%m-%Y %I:%M %p')

        parking_record.leaving_timestamp=leaving_time_for_db

        parking_record.parking_cost=float(request.form.get('total_cost'))
        parking_record.status='released'

        parking_spot.status='A'

        db.session.commit()
        return redirect(url_for('user_dash',user_id=parking_record.user_id))



    # calculting leaving timestamp and final cost
    leaving_timestamp=datetime.now()
    spot_price=float(parking_record.spot.lot.price)
    total_time_in_seconds=(leaving_timestamp-parking_record.parking_timestamp).total_seconds()
    total_time_in_hours=total_time_in_seconds/3600
    final_cost=round((spot_price*total_time_in_hours),2)


    return render_template('release_parkingspot.html',parking_record=parking_record,leaving_timestamp=leaving_timestamp,final_cost=final_cost)

    