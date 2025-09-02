from flask import Flask,render_template,redirect,request,url_for,flash
from flask import current_app as app
from .models import *   # importing all models (User, ParkingLot, ParkingSpots, ParkingRecords etc.)
from datetime import datetime,timezone
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')   # using non-GUI backend so matplotlib can save images on server
# from random import shuffle


# ---------------- HOME ROUTE ----------------
@app.route('/')
def home():
    # simply renders homepage template
    return render_template('home.html')


# ---------------- REGISTER ----------------
@app.route('/register',methods=['GET','POST'])
def register():
    # handles user registration
    if request.method=='POST':
        # collecting form data
        name=request.form.get('name')
        email=request.form.get('email')
        address=request.form.get('address')
        pincode=request.form.get('pincode')
        password=request.form.get('password')

        # check if user already exists
        this_user=User.query.filter_by(email=email).first() 

        if this_user:
            return "User already registered"
        else:
            # create new user and save in db
            new_user=User(name=name,email=email,address=address,pincode=pincode,password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('registration.html')    


# ---------------- LOGIN ----------------
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('password')

        # verify user credentials
        this_user=User.query.filter_by(email=email).first()

        if this_user:
            if this_user.password==password:
                # redirect based on role
                if this_user.role=='admin':
                    return redirect('/admin')
                else:
                    return redirect(f'/home/{this_user.id}')
            else:
                return"Incorrect Password"
        else:
            return "User does not exist first register"
    return render_template('login.html')            


# ---------------- ADMIN DASHBOARD ----------------
@app.route('/admin')
def admin_dash():
    # fetching admin + lot details
    admin_details=User.query.filter_by(role='admin').first()
    parking_lot_details=Parkinglot.query.all()
    available_parking_spots=Parkingspots.query.filter_by(status='A').all()
    occupied_parking_spots=Parkingspots.query.filter_by(status='O').all()

    return render_template('admin_dashboard.html',
                           admin_details=admin_details,
                           parking_lot_details=parking_lot_details,
                           available_parking_spots=available_parking_spots,
                           occupied_parking_spots=occupied_parking_spots)


# ---------------- USER DASHBOARD ----------------
@app.route('/home/<int:user_id>',methods=['GET','POST'])
def user_dash(user_id):
    # fetch user details and history
    user_details=User.query.filter_by(role='user',id=user_id).first()
    parking_records=Parkingrecords.query.filter_by(user_id=user_details.id).all()
    
    if request.method=='POST':
        # search functionality: pincode or location
        key=request.form.get('key')
        search_value=request.form.get('search_value')

        if key=='pincode':
            parking_lot_details=Parkinglot.query.filter_by(is_active=True,pincode=search_value).all()
        else:
            parking_lot_details=Parkinglot.query.filter_by(is_active=True,prime_location_name=search_value).all()  

        return render_template('user_dashboard.html',
                               user_details=user_details,
                               parking_lot_details=parking_lot_details,
                               parking_records=parking_records,
                               user_id=user_id)
    else:
        # default all active lots
        parking_lot_details=Parkinglot.query.filter_by(is_active=True).all()
        return render_template('user_dashboard.html',
                               user_details=user_details,
                               parking_lot_details=parking_lot_details,
                               parking_records=parking_records,
                               user_id=user_id)


# ---------------- ADD NEW LOT ----------------
@app.route('/add-new-lot',methods=['GET','POST'])
def add_new_lot():
    if request.method=='POST':
        # get details from form
        prime_location_name=request.form.get('prime_location_name')
        address=request.form.get('address')
        pincode=request.form.get('pincode')
        parking_spot_price=request.form.get('parking_spot_price')
        max_spots=request.form.get('max_spots')

        # check if lot already exists
        this_parking_lot=Parkinglot.query.filter_by(address=address,pincode=pincode).first() 
        if this_parking_lot:
            return "Parking lot with same address already exist"

        # create new lot
        new_parking_lot=Parkinglot(prime_location_name=prime_location_name,
                                   address=address,
                                   pincode=pincode, 
                                   price=parking_spot_price,
                                   maximum_spots=max_spots)
        db.session.add(new_parking_lot)
        db.session.commit()

        # auto-create parking spots inside this lot
        this_parking_lot=Parkinglot.query.filter_by(address=address,pincode=pincode).first()
        max_spots=int(this_parking_lot.maximum_spots)

        for i in range(1,max_spots+1):
            new_spot=Parkingspots(lot_id=this_parking_lot.id,spot_number=i,status='A')
            db.session.add(new_spot)
            db.session.commit()

        return redirect(url_for('admin_dash'))
    return render_template('add_parkinglot.html')


# ---------------- EDIT LOT ----------------
@app.route('/edit-parking-lot/<int:lot_id>',methods=['GET','POST'])
def edit_parking_lot(lot_id):
    # fetch current lot
    current_parking_lot=Parkinglot.query.filter_by(id=lot_id).first()
    previous_max_spots=current_parking_lot.maximum_spots

    if request.method=='POST':
        # update details
        current_parking_lot.prime_location_name=request.form.get('prime_location_name')
        current_parking_lot.address=request.form.get('address')
        current_parking_lot.pincode=request.form.get('pincode')
        current_parking_lot.price=float(request.form.get('parking_spot_price'))
        current_parking_lot.is_active=bool(int(request.form.get('is_active')))

        # update spots count
        new_max_spots=current_parking_lot.maximum_spots=int(request.form.get('max_spots'))

        # case 1: adding new spots
        if previous_max_spots<new_max_spots:
            for i in range(previous_max_spots+1,new_max_spots+1):
                new_spots=Parkingspots(lot_id=current_parking_lot.id,spot_number=i,status='A')
                db.session.add(new_spots)

        # case 2: reducing spots (only if no booking history exists)
        elif previous_max_spots>new_max_spots:
            parking_spots=Parkingspots.query.filter_by(lot_id=lot_id).all()
            diff_in_spots=previous_max_spots-new_max_spots

            for spot in reversed(parking_spots[-diff_in_spots:]):
                parking_history_count=Parkingrecords.query.filter_by(spot_id=spot.id).count()
                if parking_history_count>0:
                    db.session.commit()
                    return redirect(url_for('edit_parking_lot',lot_id=lot_id))
                else:
                    db.session.delete(spot)

        current_parking_lot.maximum_spots=Parkingspots.query.filter_by(lot_id=lot_id).count()
        db.session.commit()
        return redirect(url_for('admin_dash'))

    return render_template('edit_parkinglot.html',current_parking_lot=current_parking_lot)

# ---------------- BOOK SPOT ----------------
@app.route('/book-parking-spot/<int:user_id>/<int:lot_id>',methods=['GET','POST'])
def book_parking_lot(user_id,lot_id):
    # get first available spot
    spot_details=Parkingspots.query.filter_by(lot_id=lot_id,status='A').first()
    user_details=User.query.filter_by(role='user',id=user_id).first()
    parking_lot_details=Parkinglot.query.filter_by(id=lot_id).first()

    if spot_details==None:
        return "No spot available"

    if request.method=='POST':
        # record booking
        vehicle_number=request.form.get('vehicle_number')
        new_parking_record=Parkingrecords(spot_id=spot_details.id,
                                          user_id=user_details.id,
                                          vehicle_number=vehicle_number,
                                          parking_timestamp=datetime.now())
        db.session.add(new_parking_record)
        db.session.commit()

        # mark spot occupied
        spot_details.status='O'
        db.session.commit()

        return redirect(url_for('user_dash',user_id=user_details.id))

    return render_template('book_parkingspot.html',
                           spot_details=spot_details,
                           user_details=user_details,
                           parking_lot_details=parking_lot_details,
                           user_id=user_id)

# ---------------- RELEASE SPOT ----------------
@app.route('/release-parking-spot/<int:record_id>/<int:user_id>',methods=['GET','POST'])
def release_spot(record_id,user_id):
    parking_record=Parkingrecords.query.filter_by(id=record_id).first()

    if request.method=='POST':
        # update leaving time + cost
        parking_spot=Parkingspots.query.filter_by(id=parking_record.spot_id).first()
        leaving_timestamp=request.form.get('leaving_time')
        leaving_time_for_db=datetime.strptime(leaving_timestamp,'%d-%m-%Y %I:%M %p')

        parking_record.leaving_timestamp=leaving_time_for_db
        parking_record.parking_cost=float(request.form.get('total_cost'))
        parking_record.status='released'

        # free up spot
        parking_spot.status='A'

        db.session.commit()
        return redirect(url_for('user_dash',user_id=parking_record.user_id))

    # calculate cost estimation
    leaving_timestamp=datetime.now()
    spot_price=float(parking_record.spot.lot.price)
    total_time_in_seconds=(leaving_timestamp-parking_record.parking_timestamp).total_seconds()
    total_time_in_hours=total_time_in_seconds/3600
    final_cost=round((spot_price*total_time_in_hours),2)

    return render_template('release_parkingspot.html',
                           parking_record=parking_record,
                           leaving_timestamp=leaving_timestamp,
                           final_cost=final_cost,
                           user_id=user_id)

# ---------------- VIEW LOT ----------------
@app.route('/view-parking-lot/<int:lot_id>',methods=['GET','POST'])
def view_lot(lot_id):
    parking_spots=Parkingspots.query.filter_by(lot_id=lot_id).all()
    return render_template('view_parkinglot.html',parking_spots=parking_spots)    

# ---------------- VIEW AVAILABLE SPOT ----------------
@app.route('/view-parking-spot/Available/<int:spot_id>',methods=['GET','POST'])
def available_spot(spot_id):
    available_spot=Parkingspots.query.filter_by(id=spot_id).first()
    parking_count=Parkingrecords.query.filter_by(spot_id=spot_id).count()
    parking_record=Parkingrecords.query.filter_by(spot_id=spot_id).first()
    return render_template('Available_spot.html',
                           available_spot=available_spot,
                           parking_count=parking_count,
                           parking_record=parking_record)
    

# ---------------- VIEW OCCUPIED SPOT ----------------
@app.route('/view-parking-spot/Occupied/<int:spot_id>')
def occupied_spot(spot_id):
    occupied_spot=Parkingspots.query.filter_by(id=spot_id).first()
    parking_count=Parkingrecords.query.filter_by(spot_id=spot_id).count()
    parking_record=Parkingrecords.query.filter_by(spot_id=spot_id,status='reserved').first()
    user_id=parking_record.user_id
    user_details=User.query.filter_by(id=user_id).first()

    # estimate cost till now
    leaving_timestamp=datetime.now()
    spot_price=float(parking_record.spot.lot.price)
    total_time_in_seconds=(leaving_timestamp-parking_record.parking_timestamp).total_seconds()
    total_time_in_hours=total_time_in_seconds/3600
    estimated_cost=round((spot_price*total_time_in_hours),2)

    return render_template('Occupied_spot.html',
                           occupied_spot=occupied_spot,
                           parking_count=parking_count,
                           parking_record=parking_record,
                           user_details=user_details,
                           estimated_cost=estimated_cost)

# ---------------- DELETE AVAILABLE SPOT ----------------
@app.route('/view-parking-spot/Available/Delete/<int:spot_id>',methods=['POST'])
def spot_delete(spot_id):
    button_value=request.form.get('button_value')
    Parkingspot=Parkingspots.query.filter_by(id=spot_id).first()
    lot_id=Parkingspot.lot_id
    
    if button_value=='Delete':
        db.session.delete(Parkingspot)
        db.session.commit()
        return redirect(url_for('view_lot',lot_id=lot_id))
    else:
        return redirect(url_for('view_lot',lot_id=lot_id))


# ---------------- USER DETAILS ----------------
@app.route('/user-details',methods=['GET','POST'])
def user_details():
    if request.method=='POST':
        # search user
        key=request.form.get('key')
        search_value=request.form.get('search_value')

        if key=='userid':
            user_details=User.query.filter_by(id=search_value).all()
        elif key=='username':
            user_details=User.query.filter_by(name=search_value).all()  
        else:
            user_details=User.query.filter_by(email=search_value).all()

        return render_template('user_details.html',user_details=user_details)
    user_details=User.query.filter_by(role='user').all()
    return render_template('user_details.html',user_details=user_details)

# ---------------- DELETE LOT ----------------
@app.route('/delete-parking-lot/<int:lot_id>')
def delete_lot(lot_id):
    current_parking_lot=Parkinglot.query.filter_by(id=lot_id).first()
    parking_spots=Parkingspots.query.filter_by(lot_id=lot_id).all()

    for spot in parking_spots:
        parking_history_count=Parkingrecords.query.filter_by(spot_id=spot.id).count()
        if parking_history_count>0:
            return redirect(url_for('admin_dash'))
    db.session.delete(current_parking_lot)
    db.session.commit()

    return redirect(url_for('admin_dash'))

    
# ---------------- ADMIN SUMMARY ----------------
@app.route('/admin-summary')
def admin_summary():
    # statistics & graphs for admin
    parking_lots=Parkinglot.query.all()
    active_lots=0
    not_active_lots=0
    for lot in parking_lots:
        if lot.is_active==True:
            active_lots+=1
        else:
            not_active_lots+=1

    # bar graph: active vs not active
    labels=['Active','Not active']
    sizes=[ active_lots,not_active_lots]
    plt.bar(labels,sizes)
    plt.xlabel("Lots")
    plt.ylabel('Status')
    plt.title('Active vs Non active lots')
    plt.savefig('static/lot_status.png')
    plt.clf()

    # pie chart: revenue per lot
    lot_revenue=dict()
    for lot in parking_lots:
        for spot in lot.spots:
            for record in spot.record:
                if record.parking_cost:
                    if lot.prime_location_name in lot_revenue:
                        lot_revenue[lot.prime_location_name]+=record.parking_cost
                    else:
                        lot_revenue[lot.prime_location_name]=record.parking_cost

    lot_names=list(lot_revenue.keys())
    lot_revenue=list(lot_revenue.values())                 
    plt.pie(lot_revenue,labels=lot_names,autopct="%1.1f%%")
    plt.title("Revenue from each lot")
    plt.savefig('static/lot_revenue.png')
    plt.clf()

    # bar graph: lot vs number of spots
    lot_to_spots=dict()
    for lot in parking_lots:
        for spot in lot.spots:
            if lot.prime_location_name in lot_to_spots:
                lot_to_spots[lot.prime_location_name]+=1
            else:
                lot_to_spots[lot.prime_location_name]=1
    lot_names=list(lot_to_spots.keys())
    spot_count=list(lot_to_spots.values())  
    plt.figure(figsize=(10,6))
    plt.bar(lot_names,spot_count)
    plt.xlabel("Lots")
    plt.ylabel('No of spots')
    plt.title('No of spots per lot')
    plt.savefig('static/lot_to_spots.png')
    plt.clf()          
    return render_template('admin_summary.html')


# ---------------- USER SUMMARY ----------------
@app.route('/user-summary/<int:user_id>')
def user_summary(user_id):
    parking_records=Parkingrecords.query.filter_by(user_id=user_id,status='released').all()
    lots_used=dict()
    parking_duration=dict()
    parking_cost=dict()

    # calculate usage, duration, and cost per lot
    for record in parking_records:
        lot_name=record.spot.lot.prime_location_name
        if lot_name in lots_used:
            lots_used[lot_name]+=1
        else:
            lots_used[lot_name]=1

        if record.parking_timestamp and record.leaving_timestamp:
            duration=(record.leaving_timestamp-record.parking_timestamp).total_seconds()
            duration=round(duration/3600,2)

            if lot_name in parking_duration:
                parking_duration[lot_name]+=duration
            else:
                parking_duration[lot_name]=duration

            if lot_name in parking_cost:
                parking_cost[lot_name]+=record.parking_cost
            else:
                parking_cost[lot_name]=record.parking_cost            

    if lots_used==None:
        return 'No parking records'
    
    # pie chart usage distribution
    labels=list(lots_used.keys())
    sizes=list(lots_used.values())
    plt.figure(figsize=(6,6))
    plt.pie(sizes,labels=labels,autopct="%1.1f%%")
    plt.title('Percentage of each parking lots used')
    plt.savefig('static/lots_used.png')
    plt.clf()
    return render_template('user_summary.html',
                           user_id=user_id,
                           parking_duration=parking_duration,
                           parking_cost=parking_cost)

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    return redirect(url_for('login'))


# ---------------- PARKING RECORDS ----------------
@app.route('/parking-records',methods=['GET','POST'])
def parking_records():
    if request.method=='POST':
        # search based on user, vehicle, or spot
        key=request.form.get('key')
        search_value=request.form.get('search_value')

        if key=='userid':
            parking_records=Parkingrecords.query.filter_by(user_id=search_value).all()
        elif key=='vehicleno':

            parking_records=Parkingrecords.query.filter_by(vehicle_number=search_value).all()  
        else:
            parking_records=Parkingrecords.query.filter_by(spot_id=search_value).all()

        return render_template('parking_records.html',parking_records=parking_records)
    
    parking_records=Parkingrecords.query.all()
    return render_template('parking_records.html',parking_records=parking_records)