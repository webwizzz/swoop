from flask import jsonify, Response
from app import db
import json
from bson import ObjectId, json_util

class CommercialVehicle():
      
  def readCommVehicle(self):
    try:
      data = list(db.FleetOwner.find())
      print(data)
      populated_data = []
      for vehicle in data:
        try:
          vehicle['ownerId'] = db.users.find_one(ObjectId(vehicle['ownerId']))
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
          response=json.dumps({"message":"cannot read data of vehicle"}),
          status = 500,
          mimetype="application/json"
        )
    

  def addCommVehicle(self, data):
    try:
      vehicle = {
        "ownerId": ObjectId(data["ownerId"]),
        "plate": data["plate"],
        "price": data["price"],
        "brand" : data["brand"],
        "model" : data["model"]
        } 
      dbResponse = db.CommercialVehicles.insert_one(vehicle)
      return Response(
        response=json.dumps({"message":"vehicle created","id":f"{dbResponse.inserted_id}"}),
        status = 200,
        mimetype="application/json"
      )
    except Exception as ex:
      print(ex) 


  # def updateVehicle(self, id, data):
  #   if "unsetDriver" in data.keys() and data['unsetDriver']:
  #     db.Vehicles.update_one(
  #       {"_id": ObjectId(id)},
  #       {"$unset": {"driverId" : ""}}
  #     )
  #     return "document updated"
  #   if "driverId" in data.keys():
  #     data['driverId'] = ObjectId(data['driverId'])
  #   try:
  #     db.Vehicles.update_one(
  #       {"_id": ObjectId(id)},
  #       {"$set": data}
  #     )
  #     return "document updated"
    
  #   except Exception as ex:
  #     print(ex)
  #     return Response(
  #       response=json.dumps({"message":"data didnt update"}),
  #       status = 500,
  #       mimetype="application/json"
  #     )
      
  # def deleteVehicle(self, id):
  #   try:
  #     dbResponse = db.Vehicles.delete_one({"_id":ObjectId(id)})
    
  #     if dbResponse.deleted_count == 1:
  #       return Response(
  #       response=json.dumps({"message":"vehicle delted","id":f"{id}"}),
  #       status = 200,
  #       mimetype="application/json"
  #     )
  #     return Response(
  #       response=json.dumps({"message":"vehicle not found","id":f"{id}"}),
  #       status = 500,
  #       mimetype="application/json"
  #     )
  #   except Exception as ex:
  #     print(ex)
  #     return Response(
  #       response=json.dumps({"message":"data didnt delete"}),
  #       status = 500,
  #       mimetype="application/json"
  #     )