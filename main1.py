from Pyro4 import expose
import random
import math

class AirTrafficSimulator:
    def __init__(self, workers=None, input_file_name=None, output_file_name=None):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.workers = workers
        print("Initialized with %d workers" % len(workers))

    def simulate(self):
        print("Simulation Started")
        flights = self.read_input()
        n = len(flights)
        k = len(self.workers)

        # Розподіл рейсів між воркерами залежно від зон
        mapped = []
        for i in range(k):
            print("Assigning flights to worker %d" % i)
            mapped.append(self.workers[i].mymap(flights[(n * i // k): (n * (i + 1) // k)]))

        # Збір результатів з усіх воркерів і запис їх у вихідний файл
        collisions = self.myreduce(mapped)
        self.write_output(collisions)
        print("Simulation Finished")

    @staticmethod
    @expose
    def mymap(flights):
        # Визначення потенційних колізій для підмножини рейсів
        collisions = []
        for i in range(len(flights)):
            for j in range(i + 1, len(flights)):
                if flights[i]['hex'] == flights[j]['hex']:  # Перевірка, чи рейси у одному шестикутнику
                    collisions.append((flights[i]['id'], flights[j]['id']))
        return collisions

    @staticmethod
    @expose
    def myreduce(mapped):
        # Збір даних про колізії з усіх воркерів
        all_collisions = []
        for part in mapped:
            all_collisions.extend(part.value)  # part.value - результати з кожного воркера
        return all_collisions

    def read_input(self):
        # Зчитування даних про рейси з файлу
        with open(self.input_file_name, 'r') as f:
            flights = []
            num_flights = int(f.readline().strip())
            for _ in range(num_flights):
                id, lat1, lon1, lat2, lon2 = map(float, f.readline().split())
                flights.append({
                    'id': id,
                    'start': (lat1, lon1),
                    'end': (lat2, lon2),
                    'hex': self.calculate_hex(lat1, lon1)  # Припустимо, функція для визначення шестикутника
                })
            return flights

    def write_output(self, collisions):
        # Запис результатів у вихідний файл
        with open(self.output_file_name, 'w') as f:
            for col in collisions:
                f.write("%s collides with %s\n" % col)
            f.write("Total collisions: %d\n" % len(collisions))
        print("Output written")

    @staticmethod
    def calculate_hex(lat, lon):
        return int(lat) * 100 + int(lon)  
