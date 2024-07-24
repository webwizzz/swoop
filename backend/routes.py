from app import app 
from flask import Response, jsonify, make_response, request
import json
from user.services import User
from driver.services import Driver
from FleetOwner.services import FleetOwner
from commission.services import Commission
from vehicle.services import Vehicle
from payment.services import Payment
from CommercialVehicle.services import CommercialVehicle
import razorpay
from app import db
from bson import ObjectId, json_util

rzp_id = 'rzp_test_Ji0esyBmxAq54k'
rzp_secret = 'PvXAjGFXqtChANm4sOZeVDyk'
client = razorpay.Client(auth=(rzp_id, rzp_secret))
  
user = User()
driver = Driver()
commission = Commission()
vehicle = Vehicle()
payment = Payment(client)
owner = FleetOwner()
commVehicle = CommercialVehicle()


# USER

#get data for profile
@app.route('/get_data', methods=['POST'])
def get_data():
    data = request.get_json()  # Extract JSON data from the request
    user_id = data.get('id')
    print("userid",user_id)
    
    if not user_id: 
        return jsonify({"error": "ID not provided in the request body"}), 400

    try:
        user_object_id = ObjectId(user_id)
    except Exception as e:
        return jsonify({"error": f"Invalid ID format: {str(e)}"}), 400

    user = db.users.find_one({"_id": user_object_id})
    if user:
        if user['role'] == 'rider':
            response = db.rider.find_one({"uid": user_object_id})
            print(response)

        elif user['role'] == 'driver':
            response = db.Drivers.find_one({"uid": user_object_id})
            print(response)
        elif user['role'] == 'owner':
            response = db.FleetOwner.find_one({"uid": user_object_id})
            print("owner Daata",response,user)

        if response:

            if user['role'] == 'rider':
              # return jsonify(response)
                return jsonify({'name': response['name'], 'role': response['role'], 'email': response['email'], '_id': str(response['uid']), 'age': user['age'], "gender":user['gender'], 'preferences': response.get('preferences', []) })
            elif user['role'] == 'driver':
                  # return jsonify(response)# Check if the 'experience' key is present in the response
                    return jsonify({'name': response['name'], 'role': user['role'],'age': user['age'], 'email': user['email'], '_id': str(response['_id']), "gender":user['gender'],"phoneNo":user['phoneNo'], "location":user['location'], 'experience': response['experience'], 'rating':response['rating'], 'carMode': response['carMode'], 'carType': response['EvBtn'] })
            elif user['role'] == 'owner':
                return jsonify({'name': response['name'], 'numberofvehicles': response['numberofvehicles'], 'officeaddress': response['officeaddress'], '_id': str(response['uid']), 'age': user['age'], "gender":user['gender'], 'role': user['role'], 'email': user['email'], 'location':user['location'], 'phoneNo':user['phoneNo'], 'gender':['gender'] })
        else:
            return jsonify({"error": "Document not found"}), 404
    else:
        return jsonify({"error": "User not found"}), 404

## Register
@app.route('/user/signup/', methods=['POST'])
def signup():
  data = json.loads(request.data)
  return user.signup(data)

## Login
@app.route('/user/login/', methods=['POST'])
def login():
  data = json.loads(request.data)
  return user.login(data)


##update user preferences
@app.route('/user/updatePref/<id>',methods = ['PATCH'])
def update_preference(id):
  preferences = json.loads(request.data)
  return user.update_preferences(id, preferences)

@app.route('/user/updateProfile/<id>',methods = ['PATCH'])
def update_profile(id):
    try:
        # Parse the profile data from the request
        profile_data = request.get_json()
        print(profile_data)

        # Call the update_profile method of the User class
        return user.update_profile(id, profile_data)
    except Exception as ex:
        print(ex)
        return Response(
            response=json.dumps({"message": "Profile update failed"}),
            status=500,
            mimetype="application/json"
        )

##switchRole
# @app.route('/user/switch_role/', methods=['POST'])
# def switch_role():
#     data = json.loads(request.data)
#     return user.switch_role(data)
  
# ##Check Driver id
# @app.route('/user/check_id_match', methods=['POST'])
# def check_id_match():
#     data = json.loads(request.data)
#     return user.check_id_match(data)
  
# @app.route('/user/check_id_match', methods=['POST'])
# def check_id_match():
#     try:
#         data = request.get_json()  # Extract JSON data from the request
#         # Implement your logic to check the ID in the database based on 'data'
#         # Your existing logic goes here...
#         # return user.check_id_match(data)
#         # return jsonify({'success': True}), 200  # Return a success response
#         user_id = data.get('id')
#         print(user_id)
#         print("Received user ID from frontend:", user_id)  # Print the received user ID
          
#         if user_id:
#             user_object_id = ObjectId(user_id)
#             matching_driver = db.Drivers.find_one({"_id": user_object_id})
#             if matching_driver:
#                 response = {"match": True}
#                 print("Sending response to frontend:", response)  # Print the response being sent
#                 return jsonify(response), 200
#             else:
#               response = {"match": False}
#               print("Sending response to frontend:", response)  # Print the response being sent
#               return jsonify(response), 200
#         else:
#           response = {"error": "No ID provided"}
#           print("Sending response to frontend:", response)  # Print the response being sent
#           return jsonify(response), 400
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500 

# DRIVER

## Create Driver

@app.route('/driver/createDriver/',methods = ['POST'])
def create_driver():
  data = json.loads(request.data)
  return driver.createDriver(data)

@app.route('/driver/add_new_driver/',methods = ['POST'])
def create_new_driver():
  data = json.loads(request.data)
  return driver.create_new_driver(data)

## Get drivers
@app.route('/driver/read/',methods = ['GET'])
def read_driver():
  return driver.readDriver()

## Update a driver
@app.route('/driver/update/<id>',methods = ['PATCH'])
def update_driver(id):
  data = json.loads(request.data)
  return driver.updateDriver(id, data)

# Remove a driver
@app.route('/driver/delete/<id>',methods = ['DELETE'])
def delete_driver(id):
  return driver.deleteDriver(id)

#getdriverDetails
@app.route('/findNearDriver', methods = ['POST'])
def findNearestDriver():
    try:
        request_data = request.get_json()
        id_array = request_data.get('driverIds', [])
        print("Received driver IDs:", id_array)

        object_ids = [ObjectId(str(_id)) for _id in id_array]
        print("Object IDs:", object_ids)

        # Assuming 'Drivers' is the name of the collection
        data = list(db.Drivers.find({'_id': {'$in': object_ids}}))
        print("Data retrieved from database:", data)

        populated_data = []

        for driver in data:
            try:
                if 'vehicleId' in driver.keys():
                    driver['vehicle'] = db.Vehicles.find_one(ObjectId(driver['vehicleId']))
                elif 'preferredVehicleId' in driver.keys():
                    driver['vehicle'] = db.Vehicles.find_one(ObjectId(driver['preferredVehicleId']))

                if not driver['vehicle']['ownerId'] == driver['vehicle']['driverId']:
                    try:
                        driver['vehicle']['owner'] = db.users.find_one(ObjectId(driver['vehicle']['ownerId']))
                    except:
                        driver['vehicle']['owner'] = db.Drivers.find_one(ObjectId(driver['vehicle']['ownerId']))
                    driver['rented'] = True
                else:
                    driver['rented'] = False
            except Exception as e:
                print(f"Error processing driver: {str(e)}")

            populated_data.append(driver)
        print("Populated data:", populated_data)

        response = json.loads(json_util.dumps(populated_data))
        return response
    except Exception as ex:
        print(f"Exception: {str(ex)}")
        return Response(response=json.dumps({"message": "cannot read data of driver"}),
                        status=500,
                        mimetype="application/json")


      
# VEHICLE

#CREATE
@app.route('/vehicle/createVehicle/',methods = ['POST'])
def create_vehicle():
  data = json.loads(request.data)
  return vehicle.createVehicle(data)  

#READ
@app.route('/vehicle/readVehicle/',methods = ['GET'])
def read_vehicle():
  return vehicle.readVehicle()

#READ COMMERCIAL VEHICLES
@app.route('/vehicle/readCommercialVehicle/',methods = ['GET'])
def readCommercialVehicle():
  return vehicle.readCommercialVehicle()

#UPDATE
@app.route('/vehicle/update/<id>',methods = ['PATCH'])
def update_vehicle(id):
  data = json.loads(request.data)
  return vehicle.updateVehicle(id, data)

#DELETE
@app.route('/vehicle/delete/<id>',methods = ['DELETE'])
def delete_vehicle(id):
  vehicle.deleteVehicle(id)



#COMISSION

#CREATE
@app.route('/commission/createCommission/',methods = ['POST'])
def create_Commission():
    data = json.loads(request.data)
    return commission.createCommission(data)

#READ
@app.route('/commission/readCommission/',methods = ['GET'])
def read_Commission():
  return commission.readCommission()

#UPDATE
@app.route('/commission/updateCommission/<id>',methods = ['PATCH'])
def update_Commission(id):
  data = json.loads(request.data)
  return commission.updateCommission(id, data)



#PAYMENTS

## Create payment order
@app.route("/payment/create-order/",methods=["POST"])
def create_order():
  data = json.loads(request.data)
  return payment.createOrder(data)

## Verify payment order
@app.route("/payment/verify/",methods=['POST'])
def verify():
  data = json.loads(request.data)
  return payment.verifyPayment(data)

## Get payments for id
@app.route("/payment/read/<id>", methods=['GET'])
def read_payments(id):
  return payment.readPayments(id)

# OWNER

## Create Owner

@app.route('/owner/createOwner/',methods = ['POST'])
def createOwner():
  data = json.loads(request.data)
  return owner.createOwner(data)


# Commercial Vehicles

@app.route('/commercialVehicle/readCommVehicle/',methods = ['GET'])
def read_commVehicle():
  return commVehicle.readCommVehicle()

@app.route('/commercialVehicle/addCommVehicle/',methods = ['POST'])
def add_comm_vehicle():
  data = json.loads(request.data)
  return commVehicle.addCommVehicle(data)  

