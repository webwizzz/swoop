from flask import Response, jsonify, request
from app import db
import json
from bson import ObjectId, json_util


class FleetOwner:

    def createOwner(self, owner):
        try:
            # Convert uid to ObjectId
            owner['uid'] = ObjectId(str(owner['uid']))
            print("owner",owner)
            print("\n")
            # Insert owner document

            # owner_data = {
            #     'uid' : owner._id,
            #     'name' : owner.get('name'),
            #     'numberofvehicles' : owner.get('numberofvehicles'),
            #     'officeaddress' : owner.get('officeaddress'),
            # }

            dbResponse = db.FleetOwner.insert_one(owner)
            print("Response",dbResponse)

            comm_vehicle_data = owner.get('commVehicle', [])
            comm_vehicle_data = [{'ownerId': dbResponse.inserted_id, **vehicle} for vehicle in comm_vehicle_data]
            db_response_comm_vehicle = db.CommercialVehicles.insert_many(comm_vehicle_data)

            if dbResponse and db_response_comm_vehicle:
                # If fleet owner is successfully inserted, update user document with did
                db.users.update_one({"_id": owner['uid']}, {"$set": {"oid": dbResponse.inserted_id}})
            
                return Response(
                    response=json.dumps({"message": "driver created", "id": f"{dbResponse.inserted_id}"}),
                    status=200,
                    mimetype="application/json"
                )
        except Exception as ex:
            print(ex)