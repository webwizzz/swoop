from flask import jsonify, Response
from app import db
import json
from bson import ObjectId, json_util


class Vehicle():

    def createVehicle(self, data):
        try:
            vehicle = {
                "brand": data["brand"],
                "model": data['model'],
                "ownerId": ObjectId(data["ownerId"]),
                "plate": data["plate"],
                'freeasset': data['freeasset']
            } if 'location' not in data.keys() else {
                "brand": data["brand"],
                "model": data['model'],
                "ownerId": ObjectId(data["ownerId"]),
                "plate": data["plate"],
                'freeasset': data['freeasset'],
                'location': data['location']
            }
            dbResponse = db.Vehicles.insert_one(vehicle)
            return Response(
                response=json.dumps(
                    {"message": "vehicle created", "id": f"{dbResponse.inserted_id}"}),
                status=200,
                mimetype="application/json"
            )
        except Exception as ex:
            print(ex)

    def readVehicle(self):
        try:
            data = list(db.Vehicles.find())
            populated_data = []
            for vehicle in data:
                try:
                    vehicle['owner'] = db.users.find_one(ObjectId(
                        vehicle['ownerId'])) or db.Drivers.find_one(ObjectId(vehicle['ownerId']))
                    vehicle['driver'] = db.Drivers.find_one(
                        ObjectId(vehicle['driverId']))
                    vehicle['driverId'] = str(vehicle['driverId'])
                except Exception as e:
                    pass
                vehicle['_id'] = str(vehicle['_id'])
                vehicle['ownerId'] = str(vehicle['ownerId'])
                populated_data.append(vehicle)
            response = json.loads(json_util.dumps(populated_data))
            return response

        except Exception as ex:
            print(ex)
            return Response(
                response=json.dumps(
                    {"message": "cannot read data of vehicle"}),
                status=500,
                mimetype="application/json"
            )
          
    def readCommercialVehicle(self):
        try:
            data = list(db.CommercialVehicles.find())
            print("comm veh",data)
            populated_data = []
            for vehicle in data:
                try:
                    owner = db.FleetOwner.find_one(ObjectId(vehicle['ownerId'])) or db.Drivers.find_one(ObjectId(vehicle['ownerId']))
                    driver = db.Drivers.find_one(ObjectId(vehicle['driverId'])) if 'driverId' in vehicle else None

                    if owner:
                        vehicle['owner'] = owner
                    if driver:
                        vehicle['driver'] = driver
                        vehicle['driverId'] = str(vehicle['driverId'])
                    else:
                        vehicle['driver'] = None
                        vehicle['driverId'] = None

                    vehicle['_id'] = str(vehicle['_id'])
                    vehicle['ownerId'] = str(vehicle['ownerId'])

                    populated_data.append(vehicle)

                except Exception as e:
                    print(f"Error processing vehicle with _id: {vehicle['_id']}: {e}")
            
            response = json.loads(json_util.dumps(populated_data))
            return response

        except Exception as ex:
            print(f"Error reading commercial vehicles: {ex}")
            return Response(
                response=json.dumps(
                    {"message": "cannot read data of commercial vehicles"}),
                status=500,
                mimetype="application/json"
            )

    def updateVehicle(self, id, data):
        if "unsetDriver" in data.keys() and data['unsetDriver']:
            db.Vehicles.update_one(
                {"_id": ObjectId(id)},
                {"$unset": {"driverId": ""}}
            )
            return "document updated"
        if "driverId" in data.keys():
            data['driverId'] = ObjectId(data['driverId'])
        try:
            db.Vehicles.update_one(
                {"_id": ObjectId(id)},
                {"$set": data}
            )
            return "document updated"

        except Exception as ex:
            print(ex)
            return Response(
                response=json.dumps({"message": "data didnt update"}),
                status=500,
                mimetype="application/json"
            )

    def deleteVehicle(self, id):
        try:
            dbResponse = db.Vehicles.delete_one({"_id": ObjectId(id)})

            if dbResponse.deleted_count == 1:
                return Response(
                    response=json.dumps(
                        {"message": "vehicle delted", "id": f"{id}"}),
                    status=200,
                    mimetype="application/json"
                )
            return Response(
                response=json.dumps(
                    {"message": "vehicle not found", "id": f"{id}"}),
                status=500,
                mimetype="application/json"
            )
        except Exception as ex:
            print(ex)
            return Response(
                response=json.dumps({"message": "data didnt delete"}),
                status=500,
                mimetype="application/json"
            )
