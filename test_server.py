import timeit, functools
import prj_enums as enums
import time
from flask import  Flask, request, jsonify, Response
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


app = Flask(__name__)
BASE_URL = 'http://127.0.0.1:5000/drones'
BASE_DRONE_URL = 'http://127.0.0.1:7999'

drones = {
    999:{
            "name": "TestDrone",
            "manufacturer_year": 2024,
            "serial_num": "999-2024-1111111",
            "max_altitude": 150.0,
            "max_speed": 60.0,
            "flight_time": 30.0,
            "weight": 15.0,
            "battery": 99.5,
            "cur_altitude": 12.0,
            "cur_speed": 6.0,
            "cur_coord": (12.0, 6.0),
            "control_url": BASE_DRONE_URL,
            "drone_state": enums.DroneState.IS_LANDED,
            "mission_type": enums.MissionType.NO_MISSION,
            "mission_state": enums.MissionState.COMPLETE,
        }
}

# @app.route("/drones/<drone_id>/observe_pow_line", methods=["POST"])
def observe_pow_line_drone(drone_id):
    if drone_id not in drones:
        return  jsonify({"error": f"Дрон с id {drone_id} не "
                                  f"зарегистрирован"}), 400
    drone_info = drones[drone_id]
    drone_url = drone_info["control_url"] + "/observe_line"
    drone_info["mission_type"] = enums.MissionType.OBSERVE_LINE
    response = requests.get('https://8.8.8.8', verify=False)
    response.status_code = 200
    if response.status_code == 200:
        drone_info["mission_state"] = enums.MissionState.START
        time.sleep(1)
        drone_info["mission_state"] = enums.MissionState.EXEC
        time.sleep(2)
        drone_info["mission_state"] = enums.MissionState.COMPLETE
        time.sleep(1)
        return {"message": "Успешно"}
    else:
        drone_info["mission_state"] = enums.MissionState.ERR
    return {"error": f"Ошибка обследования линии электропередач "
                             f"дроном "
                             f"с id {drone_id}"}

# @app.route("/drones/<drone_id>/observe_pillar", methods=["POST"])
def observe_pillar_drone(drone_id):
    if drone_id not in drones:
        return  jsonify({"error": f"Дрон с id {drone_id} не "
                                  f"зарегистрирован"}), 400
    drone_info = drones[drone_id]
    drone_url = drone_info["control_url"] + "/observe_pillar"

    drone_info["mission_type"] = enums.MissionType.OBSERVE_PILLAR
    response = requests.post("https://8.8.8.8", verify=False)
    response.status_code = 200
    if response.status_code == 200:
        drone_info["mission_state"] = enums.MissionState.START
        time.sleep(1)
        drone_info["mission_state"] = enums.MissionState.EXEC
        time.sleep(2)
        drone_info["mission_state"] = enums.MissionState.COMPLETE
        time.sleep(1)
        return {"message": "Успешно"}
    else:
        drone_info["mission_state"] = enums.MissionState.ERR
    return {"error": f"Ошибка обследования линии электропередач "
                     f"дроном "
                     f"с id {drone_id}"}

if __name__ == '__main__':
    result = timeit.timeit(stmt='observe_pow_line_drone(999)',
                           globals=globals(), number=1)
    print(f"Время исполнения \"observe_pow_line_drone\" {result / 5} секунд")
    result = timeit.timeit(stmt='observe_pillar_drone(999)',
                           globals=globals(), number=1)
    print(f"Время исполнения \"observe_pillar_drone\" {result / 5} секунд")