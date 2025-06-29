from .database import db

# USER TABLE
class User(db.Model):
    __tablename__='user'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(80),nullable=False)
    email=db.Column(db.String(150),unique=True,nullable=False)
    password=db.Column(db.String(512),nullable=False)
    address=db.Column(db.String(250),nullable=False)
    pincode=db.Column(db.String(6),nullable=False)
    role=db.Column(db.String(10),default='user',nullable=False)

    #relationship with records
    record=db.relationship('Parkingrecords',backref='user',lazy=True)

#Parking Lot Table
class Parkinglot(db.Model):
    __tablename__='parking_lot'
    id=db.Column(db.Integer,primary_key=True)
    prime_location_name=db.Column(db.String(80),nullable=False)
    price=db.Column(db.Float,nullable=False)
    address=db.Column(db.String(250),nullable=False)
    pincode=db.Column(db.String(6),nullable=False)
    maximum_spots=db.Column(db.Integer,nullable=False)
    is_active=db.Column(db.Boolean,default=True,nullable=False)

    #Relationship with parking spots
    spots=db.relationship('Parkingspots',backref='lot',lazy=True,cascade='all,delete-orphan')

class Parkingspots(db.Model):
    __tablename__='parking_spots'
    id=db.Column(db.Integer,primary_key=True)
    lot_id=db.Column(db.Integer,db.ForeignKey('parking_lot.id'),nullable=False)
    spot_number=db.Column(db.Integer,nullable=False)
    status=db.Column(db.String(20),default='Available',nullable=False) # A= Available,O=Occupied

    #relationship with records
    record=db.relationship('Parkingrecords',backref='spot',lazy=True)

class Parkingrecords(db.Model):
    __tablename__='parking_records'
    id=db.Column(db.Integer,primary_key=True)
    spot_id=db.Column(db.Integer,db.ForeignKey('parking_spots.id'),nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    vehicle_number=db.Column(db.String(18),nullable=False)
    parking_timestamp=db.Column(db.DateTime,nullable=False)
    leaving_timestamp=db.Column(db.DateTime,nullable=True)
    parking_cost=db.Column(db.Float,nullable=True)
    status=db.Column(db.String(12),nullable=False,default='reserved') # reserved and released