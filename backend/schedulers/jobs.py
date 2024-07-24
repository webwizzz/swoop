from datetime import date, timedelta
from app import scheduler, db
from commission.services import Commission

@scheduler.task("cron", id="hire-for-asset", day="*")
def free_asset_hiring_process():
    vehicles = [vehicle for vehicle in list(db.Vehicles.find({"freeasset": True})) if 'driverId' not in vehicle.keys()]
    drivers = [driver for driver in list(db.Drivers.find()) if "vehicleId" not in driver.keys() and "preferredVehicleId" not in driver.keys()]
    for vehicle in vehicles:
        commissions = list(db.Commission.find({'type': "hire", 'vehicle': str(vehicle._id)}))
        hired = False
        for commission in commissions:
            if commission['status'] == "Accepted":
                hired = True
                break
        if hired:
            for commission in [comm for comm in commissions if  comm['status'] == "Pending"]:
                Commission().updateCommission(str(commission._id), {"status": "Cancelled"})
            break
        else:
            for driver in drivers:
                # Hire a driver for a month
                Commission().createCommission({
                    "origin": vehicle['location'],
                    "start_date": date.today() + timedelta(days=31),
                    "end_date": date.today() + timedelta(days=61),
                    "driverId": str(driver._id),
                    'payment': 'Online',
                    "status": 'Pending',
                    "vehicle": str(vehicle._id),
                    "type": "hire",
                    "price": driver.priceperhour * timedelta(days=30).days / 24
                })