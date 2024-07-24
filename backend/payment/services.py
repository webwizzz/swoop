from flask import jsonify, Response
from app import db
import json
from bson import ObjectId, json_util


class Payment():
    
  def __init__(self, client):
    self.client = client
        
  def createOrder(self, data):
    payment = self.client.order.create({'amount':int(data['amount'])*100,"currency":"INR","payment_capture":1})
    return {'order_id':payment['id']}, 200
  
  def verifyPayment(self, data):
    params = {'razorpay_order_id': data["razorpay_order_id"],
                  'razorpay_payment_id':data["razorpay_payment_id"],
                  'razorpay_signature':data["razorpay_signature"]}
    result = self.client.utility.verify_payment_signature(params)

    if result is not None:
      # client.payment.capture(data['razorpay_payment_id'],int(data['amount']))
      db.payments.insert_one({'payment_id':data['razorpay_payment_id'],"order_id":data['razorpay_order_id'],"commission_id":data['commission_id'],"status":"Successful"})
      db.Commission.update_one(
        {"_id":ObjectId(data["commission_id"])},
        {"$set":{"status": "Paid"}}
      )
      
      return "Payment Successful",200
    else:
          db.payments.insert_one({'payment_id':data['payment_id'],"order_id":data['order_id'],"commission_id":data['commission_id'],"status":"Failed"})
          return "Payment Failed",400
        
  def readPayments(self, id):
    data = list(db.payments.find())
    populated_data = []
    for payment in data:
      payment['commission'] = db.Commission.find_one(ObjectId(payment['commission_id']))
      payment['rider'] = db.users.find_one(ObjectId(payment['commission']['passenger']))
      payment['rider'].pop('password', None)
      payment['driver'] = db.Drivers.find_one(ObjectId(payment['commission']['driverId']))
      
      payment['_id'] = str(payment['_id'])
      payment['rider']['_id'] = str(payment['rider']['_id'])
      payment['driver']['_id'] = str(payment['driver']['_id'])
      payment['driver']['uid'] = str(payment['driver']['uid'])
      if 'vehicleId' in payment['driver'].keys(): 
        payment['driver']['vehicleId'] = str(payment['driver']['vehicleId'])
      if 'preferredVehicleId' in payment['driver'].keys(): 
        payment['driver']['preferredVehicleId'] = str(payment['driver']['preferredVehicleId'])
      payment['commission']['_id'] = str(payment['commission']['_id'])
      
      if payment['commission']['passenger'] == id or payment['commission']['driverId'] == id:
        populated_data.append(payment)
    return populated_data
  