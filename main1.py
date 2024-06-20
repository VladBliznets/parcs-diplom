from Pyro4 import expose
import random
import math

class AirTrafficSimulator:
    EARTH_RADIUS = 6371

    def __init__(self, workers=None, input_file_name=None, output_file_name=None):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.workers = workers or []
        print("Initialized with %d workers" % len(workers))

    def simulate(self):
        print("Simulation Started")
        try:
            flights = self.read_input()
            n = len(flights)
            k = len(self.workers)
            mapped = []
            for i in range(k):
                print("Assigning flights to worker %d" % i)
                mapped.append(self.workers[i].mymap(flights[(n * i // k): (n * (i + 1) // k)]))
            collisions = self.myreduce(mapped)
            self.write_output(collisions)
            print("Simulation Finished")
        except Exception as e:
            print("Error during simulation:", str(e))

    @staticmethod
    @expose
    def mymap(flights):
        collisions = []
        for i in range(len(flights)):
            for j in range(i + 1, len(flights)):
                if flights[i]['hex'] == flights[j]['hex']:
                    collisions.append(f"Flight {flights[i]['id']} collides with Flight {flights[j]['id']}")
        return collisions
    

    @staticmethod
    @expose
    def myreduce(mapped):
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
        # Відстань у км, яку потрібно покрити (довжина сторони шестикутника)
        side_length_km = 10

        # Конвертуємо відстань у радіани
        side_length_rad = side_length_km / AirTrafficSimulator.EARTH_RADIUS

        # Обчислюємо координати вершин шестикутника
        vertices = []
        for i in range(6):
            angle = math.radians(i * 60)
            lat_vertex = math.asin(math.sin(math.radians(lat)) * math.cos(side_length_rad) +
                                   math.cos(math.radians(lat)) * math.sin(side_length_rad) * math.cos(angle))
            lon_vertex = math.radians(lon) + math.atan2(math.sin(angle) * math.sin(side_length_rad) * math.cos(math.radians(lat)),
                                                        math.cos(side_length_rad) - math.sin(math.radians(lat)) * math.sin(lat_vertex))
            vertices.append((math.degrees(lat_vertex), math.degrees(lon_vertex)))

        # Унікальний ідентифікатор для шестикутника
        avg_lat = sum(vertex[0] for vertex in vertices) / 6
        avg_lon = sum(vertex[1] for vertex in vertices) / 6

        return f"{round(avg_lat, 4)}_{round(avg_lon, 4)}"
    
    def generate_random_flights(self, num_flights):
        with open(self.input_file_name, 'w') as f:
            f.write(f"{num_flights}\n")
            for i in range(num_flights):
                lat1, lon1 = random.uniform(-90, 90), random.uniform(-180, 180)
                lat2, lon2 = random.uniform(-90, 90), random.uniform(-180, 180)
                f.write(f"{i} {lat1} {lon1} {lat2} {lon2}\n")
        print(f"Generated {num_flights} random flights")
