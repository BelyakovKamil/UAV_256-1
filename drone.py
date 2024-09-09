import requests
from flask import Flask, request, jsonify, Response
import logging
from itertools import count
from multiprocessing import Process
import asyncio
import os
import prj_enums as enums
from abc import ABC, abstractmethod

os.chdir(r"C:\Users\Windows10\PycharmProjects\БПЛА\Итоговое задание")

logging.basicConfig(level=logging.INFO,
                    format='%(name)s - %(levelname)s - %(message)s',
                    filename="drone_logs.log",
                    filemode='w')

app = Flask(__name__)
BASE_URL = 'http://127.0.0.1:5000/drones'
BASE_DRONE_PORT = 7000
drone_processes = {}

class Strategy(ABC):
    @abstractmethod
    def do_algorithm(self, drone_proxy) -> None:
        pass

class Drone(ABC):
    @abstractmethod
    def create_id(self):
        pass

    @abstractmethod
    def generate_serial_num(self, id, manufacturer_year):
        pass

class DroneProxy(Drone):
    __ids = count(1)

    def __init__(self, name, manufacturer_year, strategy : Strategy,
                 max_altitude=300,
                 max_speed=60,
                 flight_time=30,
                 weight=1.5,
                 battery=100.0):
        self.__id = self.create_id()
        self.__name = name
        self.__manufacturer_year = manufacturer_year
        self.__serial_num = self.generate_serial_num(self.__id,
                                                     self.__manufacturer_year)
        self.__max_altitude = max_altitude
        self.__max_speed = max_speed
        self.__flight_time = flight_time
        self.__weight = weight
        self.__battery = battery
        self.__cur_altitude = 0
        self.__cur_speed = 0
        self.__cur_coord = (0.0, 0.0)
        self.__control_url = f"http://127.0.0.1:{BASE_DRONE_PORT + self.__id}"
        self.__drone_state = enums.DroneState.UNKNOWN
        self.__mission_type = enums.MissionType.NO_MISSION
        self.__mission_state = enums.MissionState.UNKNOWN
        self.__strategy = strategy

        self.__json_format = {
            "name": self.__name,
            "manufacturer_year": self.__manufacturer_year,
            "serial_num": self.__serial_num,
            "max_altitude": self.__max_altitude,
            "max_speed": self.__max_speed,
            "flight_time": self.__flight_time,
            "weight": self.__weight,
            "battery": self.__battery,
            "cur_altitude": self.__cur_altitude,
            "cur_speed": self.__cur_speed,
            "cur_coord": self.__cur_coord,
            "control_url": self.__control_url,
            "drone_state": self.__drone_state,
            "mission_type": self.__mission_type,
            "mission_state": self.__mission_state,
        }

    @property
    def strategy(self) -> Strategy:
        """
        Дрон хранит ссылку на один из объектов Стратегии. Дрон не знает
        конкретного класса стратегии. Он должен работать со всеми стратегиями
        через интерфейс Стратегии.
        """
        return self.__strategy

    @strategy.setter
    def strategy(self, strategy: Strategy) -> None:
        """
        Дрон позволяет заменить объект Стратегии во время выполнения.
        """
        self._strategy = strategy

    def create_id(self):
        return next(self.__ids)

    def generate_serial_num(self, id, manufacturer_year):
        return f'{id}-{manufacturer_year}-{self.__hash__()}'

    def get_id(self):
        return self.__id

    def get_port(self):
        return BASE_DRONE_PORT + self.get_id()

    def get_json_format(self):
        return self.__json_format

    def set_battery(self, battery):
        self.__battery = battery
        self.update_json_format()

    def set_cur_altitude(self, cur_altitude):
        self.__cur_altitude = cur_altitude
        self.update_json_format()

    def set_cur_speed(self, cur_speed):
        self.__cur_speed = cur_speed
        self.update_json_format()

    def set_cur_coord(self, cur_coord):
        self.__cur_coord = cur_coord
        self.update_json_format()

    def set_drone_state(self, drone_state):
        self.__drone_state = drone_state
        self.update_json_format()

    def set_mission_type(self, mission_type):
        self.__mission_type = mission_type
        self.update_json_format()

    def set_mission_state(self, mission_state):
        self.__mission_state \
            = mission_state
        self.update_json_format()

    def update_json_format(self):
        self.__json_format = {
            "name": self.__name,
            "manufacturer_year": self.__manufacturer_year,
            "serial_num": self.__serial_num,
            "max_altitude": self.__max_altitude,
            "max_speed": self.__max_speed,
            "flight_time": self.__flight_time,
            "weight": self.__weight,
            "battery": self.__battery,
            "cur_altitude": self.__cur_altitude,
            "cur_speed": self.__cur_speed,
            "cur_coord": self.__cur_coord,
            "control_url": self.__control_url,
            "drone_state": self.__drone_state,
            "mission_type": self.__mission_type,
            "mission_state": self.__mission_state,
        }

    async def do_algorithm(self, drone_proxy):
        self.strategy.do_algorithm(drone_proxy)
    # async def start_drone(self):
    #     port = self.get_port()
    #     drone_processes[self.get_id()] = Process(target=
    #                                              app.run(port=port,
    #                                                      debug=False)
    #                                              )
    #     drone_processes[self.get_id()].start()
    #
    # async def register_drone(self):
    #     url = BASE_URL
    #     payload = {"drone_id": self.get_id(),
    #                **self.get_json_format()
    #                }
    #     response = requests.post(url, json=payload)
    #     logging.info(f'Зарегистрирован дрон с id {self.get_id()}.'
    #                  f' {self.get_json_format()}')
    #     return response.json()
    #
    # async def unregister_drone(self):
    #     is_alive = drone_processes[self.get_id()].is_alive()
    #     if self.get_id() in drone_processes and not is_alive:
    #         del drone_processes[self.get_id()]
    #
    # async def stop_drone(self):
    #     is_alive = drone_processes[self.get_id()].is_alive()
    #     if is_alive:
    #         drone_processes[self.get_id()].terminate()
    #         drone_processes[self.get_id()].join()

class AbstractDroneFactory(ABC):
    @abstractmethod
    def create_drone(self, *args, **kwargs) -> Drone:
        pass

class DroneFactory(AbstractDroneFactory):
    def create_drone(self, *args, **kwargs) -> DroneProxy:
        return DroneProxy(*args, **kwargs)

class StartDrone(Strategy):
    async def do_algorithm(self, DroneProxy: DroneProxy):
        port = DroneProxy.get_port()
        drone_processes[DroneProxy.get_id()] = Process(target=
                                                 app.run(port=port,
                                                         debug=True)
                                                 )
        drone_processes[DroneProxy.get_id()].start()

class RegisterDrone(Strategy):
    '''
    Этот класс реализует паттерн Стратегия и позволяет выполнять регистрацию Дрона
    '''
    async def do_algorithm(self, DroneProxy: DroneProxy):
        '''
        Данный метод реализует паттерн Стратегия и позволяет выполнять регистрацию Дрона
        :param DroneProxy:
        :return:
        '''
        url = BASE_URL
        payload = {"drone_id": DroneProxy.get_id(),
                   **DroneProxy.get_json_format()
                   }
        response = requests.post(url, json=payload)
        logging.info(f'Зарегистрирован дрон с id {DroneProxy.get_id()}.'
                     f' {DroneProxy.get_json_format()}')
        return response.json()

class StopDrone(Strategy):
    async def do_algorithm(self, DroneProxy: DroneProxy):
        is_alive = drone_processes[DroneProxy.get_id()].is_alive()
        if is_alive:
            drone_processes[DroneProxy.get_id()].terminate()
            drone_processes[DroneProxy.get_id()].join()

class UnregisterDrone(Strategy):
    async def do_algorithm(self, DroneProxy: DroneProxy):
        is_alive = drone_processes[DroneProxy.get_id()].is_alive()
        if DroneProxy.get_id() in drone_processes and not is_alive:
            del drone_processes[DroneProxy.get_id()]

@app.route("/takeoff", methods=["POST"])
def takeoff():
    altitude = request.json.get("altitude")
    # логика взлета
    print(f"Взлетаем на высоту {altitude} метров")
    return jsonify({"message": f"Взлет на высоту {altitude} выполнен!"}), 200


@app.route("/land", methods=["POST"])
def land():
    # логика посадки
    print(f"Сажаем дрон")
    return jsonify({"message": f"Посадка дрона выполнена!"}), 200


@app.route("/observe_pow_line", methods=["POST"])
def observe_pow_line():
    # логика обследования линии электропередач
    print(f"Обследование линии электропередач")
    return jsonify({"message": f"Обследование линии электропередач "
                               f"выполнено!"}), 200


@app.route("/observe_pillar", methods=["POST"])
def observe_pillar():
    # логика обследования опоры линии электропередач
    print(f"Обследование опоры линии электропередач")
    return jsonify({"message": f"Обследование опоры линии электропередач "
                               f"выполнено!"}), 200


if __name__ == '__main__':
    register_drone = RegisterDrone()
    start_drone = StartDrone()
    stop_drone = StopDrone()
    unregister_drone = UnregisterDrone()

    drone_factory = DroneFactory()
    drone_pow_line = drone_factory.create_drone("Дрон-обследователь линий",
                                                2024, register_drone)
    drone_pillar = drone_factory.create_drone("Дрон-обследователь опор",
                                              2023, register_drone)

    # drone_pow_line = Drone("Дрон-обследователь линий", 2024)
    # drone_pillar = Drone("Дрон-обследователь опор", 2023)

    ioloop = asyncio.get_event_loop()
    tasks = [
        ioloop.create_task(drone_pow_line.do_algorithm(drone_pow_line)),
        ioloop.create_task(drone_pillar.do_algorithm(drone_pillar)),
    ]

    asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))

    drone_pow_line.strategy = start_drone
    drone_pillar.strategy = start_drone

    tasks = [
        ioloop.create_task(drone_pow_line.do_algorithm(drone_pow_line)),
        ioloop.create_task(drone_pillar.do_algorithm(drone_pillar)),
    ]
    asyncio.get_event_loop().run_forever()

    drone_pow_line.strategy = stop_drone
    drone_pillar.strategy = stop_drone
    tasks = [
        ioloop.create_task(drone_pow_line.do_algorithm(drone_pow_line)),
        ioloop.create_task(drone_pillar.do_algorithm(drone_pillar)),
    ]

    drone_pow_line.strategy = unregister_drone
    drone_pillar.strategy = unregister_drone
    tasks = [
        ioloop.create_task(drone_pow_line.do_algorithm()),
        ioloop.create_task(drone_pillar.do_algorithm()),
    ]
    asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))
    asyncio.get_event_loop().run_forever()
    ioloop.close()