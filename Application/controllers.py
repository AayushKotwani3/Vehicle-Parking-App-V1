from flask import Flask,render_template,redirect,request
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
            return "registeration successful"
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