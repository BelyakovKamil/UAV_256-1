import time

from flask import  Flask, request, jsonify, Response
import requests
import prj_enums as enums


app = Flask(__name__)

drones = {}

@app.route('/')
def hello_drone():
    return "Hello, Drone!"

@app.route("/drones", methods=["GET"])
def get_drones():
    return jsonify(drones), 200

@app.route("/drones/<drone_id>", methods=["GET"])
def get_drone(drone_id):
    drone = drones.get(drone_id)
    if drone:
        return jsonify(drone), 200
    return jsonify({"error": f"Дрона с id {drone_id} не найден"}), 404

@app.route("/drones", methods=["POST"])
def create_drone():
    drone_id = request.json.get("drone_id")
    drone_name = request.json.get("name")
    if drone_id:
        drones[drone_id] = request.json
        return jsonify({"message": f"Дрон с id {drone_id} успешно "
                                   f'добавлен. Его название - "{drone_name}"'}),\
               201
    return jsonify({"error": f"Не передан id дрона"}), 404

@app.route("/drones/<drone_id>/takeoff", methods=["POST"])
def takeoff_drone(drone_id):
    if drone_id not in drones:
        return  jsonify({"error": f"Дрон с id {drone_id} не "
                                  f"зарегистрирован"}), 400
    altitude = request.json.get("altitude")
    drone_info = drones[drone_id]
    drone_url = drone_info["control_url"] + "/takeoff"

    response = requests.post(drone_url, json={"altitude": altitude})
    if response.status_code == 200:
        drone_info["drone_state"] = enums.DroneState.IS_FLYING
        return jsonify({"message": response.json().get("message")}), 200
    return jsonify({"error": f"Ошибка взлета дрона с id {drone_id}"}), 500

@app.route("/drones/<drone_id>/land", methods=["POST"])
def land_drone(drone_id):
    if drone_id not in drones:
        return  jsonify({"error": f"Дрон с id {drone_id} не "
                                  f"зарегистрирован"}), 400
    altitude = request.json.get("altitude")
    drone_info = drones[drone_id]
    if drone_info["drone_state"] == enums.DroneState.IS_LANDED:
        return jsonify({"info": f"Дрона с id {drone_id} на земле"}), 500
    else:
        drone_url = drone_info["control_url"] + "/land"
        response = requests.post(drone_url, json={"altitude": altitude})
        if response.status_code == 200:
            drone_info["drone_state"] = enums.DroneState.IS_LANDED
            return jsonify({"message": response.json().get("message")}), 200
    return jsonify({"error": f"Ошибка посадки дрона с id {drone_id}"}), 500

@app.route("/drones/<drone_id>/observe_pow_line", methods=["POST"])
def observe_pow_line_drone(drone_id):
    if drone_id not in drones:
        return  jsonify({"error": f"Дрон с id {drone_id} не "
                                  f"зарегистрирован"}), 400
    drone_info = drones[drone_id]
    drone_url = drone_info["control_url"] + "/observe_line"
    drone_info["mission_type"] = enums.MissionType.OBSERVE_LINE
    response = requests.post(drone_url)
    if response.status_code == 200:
        drone_info["mission_state"] = enums.MissionState.START
        time.sleep(1)
        drone_info["mission_state"] = enums.MissionState.EXEC
        time.sleep(2)
        drone_info["mission_state"] = enums.MissionState.COMPLETE
        time.sleep(1)
        return jsonify({"message": response.json().get("message")}), 200
    else:
        drone_info["mission_state"] = enums.MissionState.ERR
    return jsonify({"error": f"Ошибка обследования линии электропередач "
                             f"дроном "
                             f"с id {drone_id}"}), 500

@app.route("/drones/<drone_id>/observe_pillar", methods=["POST"])
def observe_pillar_drone(drone_id):
    if drone_id not in drones:
        return  jsonify({"error": f"Дрон с id {drone_id} не "
                                  f"зарегистрирован"}), 400
    drone_info = drones[drone_id]
    drone_url = drone_info["control_url"] + "/observe_pillar"

    drone_info["mission_type"] = enums.MissionType.OBSERVE_PILLAR
    response = requests.post(drone_url)
    if response.status_code == 200:
        drone_info["mission_state"] = enums.MissionState.START
        time.sleep(1)
        drone_info["mission_state"] = enums.MissionState.EXEC
        time.sleep(2)
        drone_info["mission_state"] = enums.MissionState.COMPLETE
        time.sleep(1)
        return jsonify({"message": response.json().get("message")}), 200
    else:
        drone_info["mission_state"] = enums.MissionState.ERR
    return jsonify({"error": f"Ошибка обследования опоры линии электропередач "
                             f"дроном "
                             f"с id {drone_id}"}), 500

if __name__ == '__main__':
    app.run(debug=True)