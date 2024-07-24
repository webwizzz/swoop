from flask import jsonify, Response
from app import db
import json
from bson import ObjectId, json_util

class Commission():
    
  def createCommission(self, data):
    try:
      comm = {
      "origin": data["origin"],
      "destination": data["destination"],
      "start_date": data["start"],
      "end_date": data["end"],
      "driverId": data['driverId'],
      "passenger": data['passenger'],
      'payment': 'Online',
      "status": 'Pending',
      "price": data['price'],
      "distance": data['distance'],
      "type": data['type']
      } if data['type'] == 'ride' else {
      "origin": data["origin"],
      "start_date": data["start"],
      "end_date": data["end"],
      "driverId": data['driverId'],
      'payment': 'Online',
      "status": 'Pending',
      "vehicle": data['vehicle'],
      "type": data['type'],
      "price": data['price']
      }
      dbResponse = str(db.Commission.insert_one(comm).inserted_id)
      comm['_id'] = dbResponse
      return jsonify(comm)
    except Exception as ex:
      print(ex) 
                       
  def readCommission(self):
    try:
      data = list(db.Commission.find())
      for i in range(len(data)):
          comm = data[i]
          if "vehicle" in comm.keys(): comm['vehicle'] = db.Vehicles.find_one(ObjectId(comm['vehicle']))
          driver=None
          try:
              driver = db.Drivers.find_one(ObjectId(comm['driverId']))
              try:
                  driver['vehicle'] = db.Vehicles.find_one(ObjectId(driver['vehicleId'])) if "vehicleId" in driver.keys() else db.Vehicles.find_one(ObjectId(driver['preferredVehicleId']))
                  if not driver['vehicle']['ownerId'] == driver['vehicle']['driverId']:
                      try:
                          driver['vehicle']['owner'] = db.users.find_one(ObjectId(driver['vehicle']['ownerId'])) or db.Drivers.find_one(ObjectId(driver['vehicle']['ownerId']))
                      except: pass   
              except: pass
          except: pass
          comm['driver'] = driver if driver else comm['driverId']
          comm['_id'] = str(comm['_id'])
          data[i] = comm
      response = json.loads(json_util.dumps(data))
      return response
        
    except Exception as ex:
      print(ex)
      return Response(
          response=json.dumps({"message":"cannot read data of commission"}),
          status = 500,
          mimetype="application/json"
          )
      
  def updateCommission(self, id, data):
    try:
      db.Commission.update_one(
        {"_id":ObjectId(id)},
        {"$set":{"status": data['status']}}
      )
      return "document updated"
    except Exception as ex:
      print(ex)
      return Response(
        response=json.dumps({"message":"data didnt update"}),
        status = 500,
        mimetype="application/json"
      )