from flask import Flask, jsonify, request, session, redirect,Response
from passlib.hash import pbkdf2_sha256
from app import db
from flask_cors import cross_origin
from bson import ObjectId
import json
import pymongo


class User:

    def signup(self, data):
      user = {
          "name": data['name'],
          "email": data['email'],
          "password": pbkdf2_sha256.encrypt(data['password']),
          "age": data['age'],
          "location":data['location'],
          "phoneNo":data['phoneNo'],
          "gender":data['gender'],
          "role": data['role']
      }
      rider = {
          "name": data['name'],
          "email": data['email'],
          "password": pbkdf2_sha256.encrypt(data['password']),
          "age": data['age'],
          "location":data['location'],
          "role": data['role'],
          "gender":data['gender'],
          "preferences": []
      }
      print("before",user)
      if db.users.find_one({"email": user['email']}):
          return jsonify({"error": "Email address already in use"}), 400

      db_user = db.users.insert_one(user)
      print("aftre",db_user)
      user_id = str(db_user.inserted_id)
      
      if(data['role'] == "rider"):
        db_rider = db.rider.insert_one(rider)

        if(db_user and db_rider):
                
                rider_id = str(db_rider.inserted_id)
                # Update user document with rid
                db.users.update_one({"_id": db_user.inserted_id}, {"$set": {"rid": db_rider.inserted_id}})
                db.rider.update_one({"_id": db_rider.inserted_id}, {"$set": {"uid": db_user.inserted_id}})

                return jsonify({'data': 'Success', "user_id": user_id, "rider_id": rider_id}), 200
      
      elif(data['role'] == "driver" or data['role'] == "owner"):
        return jsonify({'data': 'Success', "user_id": user_id}), 200
          
      return jsonify({"error": "Signup failed"}), 400

    def login(self, data):
        user = db.users.find_one({
            "email": data['email']
        })

        if user['role'] == 'driver':
            driver = db.Drivers.find_one({"uid": user['_id']})
            hired = False if 'vehicleId' not in driver.keys() else True
            if not hired and "preferredVehicleId" in driver.keys():
                return {'name': driver['name'], 'role': 'driver', 'email': user['email'], '_id': str(driver['_id']), 'uid': str(user['_id']), "hired": hired, "preferredVehicle": str(driver["preferredVehicleId"])}
            return {'name': driver['name'], 'role': 'driver', 'email': user['email'], '_id': str(driver['_id']), 'uid': str(user['_id']), "hired": hired}
        
        # if user['role'] == 'owner':
        #     owner = db.FleetOwner.find_one({"uid": user['_id']})
        #     return {'name': owner['name'], 'role': 'driver', 'email': user['email'], '_id': str(owner['_id']), 'uid': str(user['_id'])}
        # if user['role'] == "rider":
        #     return {'name': user['name'], 'role': user['role'], 'email': user['email'], '_id': str(user['_id'])}
        
        if user['role'] == 'owner' and user['name'] and pbkdf2_sha256.verify(data['password'], user['password']):
            return {'name': user['name'], 'role': user['role'], 'email': user['email'], '_id': str(user['_id']), 'oid': str(user['oid'])}
            
        if user['name'] and pbkdf2_sha256.verify(data['password'], user['password']):
            if 'did' not in user: 
                return {'name': user['name'], 'role': user['role'], 'email': user['email'], '_id': str(user['_id'])}
            return {'name': user['name'], 'role': user['role'], 'email': user['email'], '_id': str(user['did'])}
        
        
        return jsonify({"error": "Invalid login credentials"}), 401
    
    def update_preferences(self, id, preferences):
        print(id)
        try:
            # Assuming 'preferences' is a dictionary containing key-value pairs to be updated in the preferences array
            if not preferences:
                return Response("Preferences data is empty", status=400)

            # Update the user document where preferences array is empty
            db.rider.update_one(
                {"uid": ObjectId(id), "preferences": []},
                {"$set": {"preferences": preferences}}
            )

            return Response("Preferences Updated", status=200)
        except Exception as ex:
            print(ex)
            return Response(
                response=json.dumps({"message": "Preferences update failed"}),
                status=500,
                mimetype="application/json"
            )
    def update_profile(self, id, profile_data):
        try:
            # Validate that profile data is not empty
            if not profile_data:
                return Response("Profile data is empty", status=400)

            # Fetch the user from the database to determine the role
            user = db.users.find_one({"_id": ObjectId(id)})
            if not user:
                return Response("User not found", status=404)

            # Filter out None values for the 'users' collection
            user_fields = {k: v for k, v in {
                "name": profile_data.get("name"),
                "email": profile_data.get("email"),
                "age": profile_data.get("age"),
                "location": profile_data.get("location"),
                "phoneNo": profile_data.get("phoneNo")
            }.items() if v is not None}

            result_users = db.users.update_one(
                {"_id": ObjectId(id)},
                {"$set": user_fields}
            )

            if result_users.matched_count == 0:
                return Response("User not found", status=404)

            # Depending on the role, update the appropriate collection
            role = user.get("role")
            if role == "rider":
                rider_fields = {k: v for k, v in {
                "name": profile_data.get("name"),
                "email": profile_data.get("email"),
                "age": profile_data.get("age"),
                # "location": profile_data.get("location"),
                # "phoneNo": profile_data.get("phoneNo"),
                }.items() if v is not None}

                # Update rider profile in 'users' collection
                result_rider = db.users.update_one(
                    {"_id": ObjectId(id)},
                    {"$set": rider_fields}
                )

                if result_rider.matched_count == 0:
                    return Response("Rider profile not found", status=404)

                # Update rider preferences in 'rider' collection
                preferences = {k: v for k, v in profile_data.items() if k in ['driverExperience', 'driverLocation', 'carPref', 'primJourney', 'EvBtn', 'gender', 'driverAge']}
                result_preferences = db.rider.update_one(
                    {'uid': ObjectId(id)},
                    {'$set': {'preferences': preferences}}
                )

                if result_preferences.matched_count == 0:
                    return Response("Rider preferences not found", status=404)

                return Response("Rider profile updated successfully", status=200)

            elif role == "driver":
                # Filter out None values for the 'Drivers' collection
                driver_fields = {k: v for k, v in {
                    "name": profile_data.get("name"),
                    "rating": profile_data.get("rating"),
                    "pricepermonth": profile_data.get("pricepermonth"),
                    "priceperday": profile_data.get("priceperday"),
                    "experience": profile_data.get("experience"),
                    "carMode": profile_data.get("carMode"),
                    "aadharNo": profile_data.get("aadharNo"),
                    "panNo": profile_data.get("panNo"),
                    "EvBtn": profile_data.get("EvBtn"),
                    "gender": profile_data.get("gender")
                }.items() if v is not None}

                result_driver = db.Drivers.update_one(
                    {"uid": ObjectId(id)},
                    {"$set": driver_fields}
                )

                if result_driver.matched_count == 0:
                    return Response("Driver profile not found", status=404)

            elif role == "owner":
                # Filter out None values for the 'FleetOwner' collection
                owner_fields = {k: v for k, v in {
                    "name": profile_data.get("name"),
                    "numberofvehicles": profile_data.get("numberofvehicles"),
                    "officeaddress": profile_data.get("officeaddress")
                }.items() if v is not None}

                result_owner = db.FleetOwner.update_one(
                    {"uid": ObjectId(id)},
                    {"$set": owner_fields}
                )

                if result_owner.matched_count == 0:
                    return Response("Owner profile not found", status=404)

            return Response("Profile Updated", status=200)

        except Exception as ex:
            print(ex)
            return Response(
                response=json.dumps({"message": "Profile update failed"}),
                status=500,
                mimetype="application/json"
            )
            
    # def switch_role(self, data):
    #     email = data['email']
    #     new_role = data['new_role']

    #     user = db.users.find_one({"email": email})
    #     if user:
    #         db.users.update_one({"email": email}, {"$set": {"role": new_role}})
    #         if user['role'] == 'driver':
    #             driver = db.Drivers.find_one({"uid": user['_id']})
    #             hired = False if 'vehicleId' not in driver.keys() else True
    #             if not hired and "preferredVehicleId" in driver.keys():
    #                 return {'name': driver['name'], 'role': 'driver', 'email': user['email'], '_id': str(driver['_id']), 'uid': str(user['_id']), "hired": hired, "preferredVehicle": str(driver["preferredVehicleId"])}
    #             return {'name': driver['name'], 'role': 'driver', 'email': user['email'], '_id': str(driver['_id']), 'uid': str(user['_id']), "hired": hired}
    #         if user['role'] != "driver":
    #             if 'did' not in user: 
    #                 return {'name': user['name'], 'role': user['role'], 'email': user['email'], '_id': str(user['_id'])}
    #             return {'name': user['name'], 'role': user['role'], 'email': user['email'], '_id': str(user['did'])}
            
    #         return jsonify({"error": "User not found"}), 404
        
# Assuming db is your database connection

    # def check_id_match(id):
    #     try:
    #         # Fetch _id from user collection
    #         user_doc = db.users.find_one({"_id": id})  # Use {"_id": id} to find a specific ID
    #         if user_doc:
    #             user_id = user_doc['_id']

    #             # Check if the _id matches in the driver collection
    #             matching_driver = db.Drivers.find_one({"uid": user_id})
    #             if matching_driver:
    #                 return jsonify({"match_found": True})  # Match found
    #             else:
    #                 return jsonify({"match_found": False})  # No match found in driver collection
    #         else:
    #             return jsonify({"error": "User not found"})  # No document found in user collection based on the criteria
    #     except Exception as e:
    #         print("An error occurred:", e)
    #         return jsonify({"error": "An error occurred"})  # Return an error response in case of exceptions

    # def check_id_match(id):
    #     try:
    #         # Replace <MongoDB connection string> with your actual MongoDB connection string
            
    #         # Convert the string ID to ObjectId (assuming id_to_check is a string)
            
    #         # Find the document in Drivers collection that matches the provided id
    #         matching_driver = db.Drivers.find_one({"uid": id})
            
    #         if matching_driver:
    #             return True  # Match found in Drivers collection
    #         else:
    #             return False  # No match found in Drivers collection
    #     except Exception as e:
    #         print("An error occurred:", e)
    #         return False




    # def check_id_match(data):
    #     try:
    #         user_id = data.get('id')
    #         print("Received user ID from frontend:", user_id)  # Print the received user ID
            
    #         if user_id:
    #             user_object_id = ObjectId(user_id)
    #             matching_driver = db.Drivers.find_one({"uid": user_object_id})
    #             if matching_driver:
    #                 response = {"match": True}
    #                 print("Sending response to frontend:", response)  # Print the response being sent
    #                 return jsonify(response), 200
    #             else:
    #                 response = {"match": False}
    #                 print("Sending response to frontend:", response)  # Print the response being sent
    #                 return jsonify(response), 200
    #         else:
    #             response = {"error": "No ID provided"}
    #             print("Sending response to frontend:", response)  # Print the response being sent
    #             return jsonify(response), 400
    #     except Exception as e:
    #         print("An error occurred:", e)
    #         response = {"error": "An error occurred"}
    #         print("Sending response to frontend:", response)  # Print the response being sent
    #         return jsonify(response), 500


