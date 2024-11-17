import os
from unidecode import unidecode
import numpy as np
import random
from faker import Faker
from cities import region_postalcode_city

fake = Faker('pl_PL')

# create the "data" folder if it doesn't exist
data_folder = "data"
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

# file paths within the "data" folder
service_office_2020_file_path = os.path.join(
    data_folder, "Service_Office_2020.txt")
bus_2020_file_path = os.path.join(data_folder, "Bus_2020.txt")


# function to remove polish characters
def remove_polish_characters(address):
    return unidecode(address)

# Function to get a random bus from one of the city stations/service offices according to the route
def get_random_bus_from_service(route):
    from_city = (route.split(',')[1]).split("-")[0]

    target_service = service_office_list_2020
    target_buses = bus_list_2020

     # choosing randomly from one of offices in city from which we start our route
    bus_office = [office for office in target_service if from_city in office]

    # if in start city there is no service office, we choose from the destination city
    if len(bus_office) == 0:
        to_city = (route.split(',')[1]).split("-")[1]
        bus_office = [office for office in target_service if to_city in office]
    if len(bus_office) == 0:
        random_bus_office = random.choice(target_service)
    else:
        random_bus_office = random.choice(bus_office)

    office_id = random_bus_office.split(',')[0]
    random_bus = random.choice(
        [bus for i, bus in enumerate(target_buses) if bus_services_list[i] == int(office_id)])
    
    return random_bus.split(',')[0]

# function to get available places for a given registration number of a bus
def get_avaliable_places(reg_number):
    bus_list = bus_list_2020
    for bus in bus_list:
        if bus.split(',')[0] == reg_number:
            bus_info = bus
            break
    return int(bus_info.split(',')[5]) + int(bus_info.split(',')[6])

bus_service_id = 1
service_office_list_2020 = []
service_office_region_counter = {
    region: 0 for region in region_postalcode_city.keys()}
bus_slots_cities = []
slots = [8, 9, 10]
BUS_SERVICES_NO_2020 = 20

# generate service offices data for 2020
with open(service_office_2020_file_path, "w+", encoding="UTF-8") as file:
    while bus_service_id <= BUS_SERVICES_NO_2020:
        region = random.choice(list(region_postalcode_city.keys()))
        service_office_region_counter[region] += 1
        office_count = service_office_region_counter[region]
        bus_service_name = f"{region}'s Bus Service no. {office_count}"
        postal_code_prefix, city = random.choice(
            list(region_postalcode_city[region].items()))
        postal_code = f"{postal_code_prefix}-{np.random.randint(999):03}"
        address = remove_polish_characters(
            fake.street_name() + " " + fake.building_number())
        country = "Poland"
        bus_slots = random.choice(slots)
        bus_slots_cities.append((bus_slots, city))
        row_service_office = f"{bus_service_id},{bus_service_name},{address},{postal_code},{city},{region},{country},{bus_slots}"
        service_office_list_2020.append(row_service_office)
        bus_service_id += 1

    file.write('\n'.join(service_office_list_2020))


bus_list_2020 = []
types_of_bus = {"minibus": (8, 0), "standard": (15, 7), "low floor": (10, 5)}
reg_cities = {"CB": "Bydgoszcz", "CT": "Torun", "GD": "Gdansk", "GA": "Gdynia", "NO": "Olsztyn",
              "NE": "Elblag", "WA": "Warszawa", "WR": "Radom", "ZS": "Szczecin", "ZK": "Koszalin"}
cities_reg = {v: k for k, v in reg_cities.items()}
bus_regnum_2020 = []
bus_services_list = []
bus_brand = ["Volvo", "Mercedes-Benz", "Man", "Solaris"]
bus_service_id = 1

# generate bus data for 2020
with open(bus_2020_file_path, "w+", encoding="UTF-8") as file:
    for num_of_bus, office_city in bus_slots_cities:
        for _ in range(num_of_bus):
            service_id = bus_service_id
            registration_number = cities_reg[office_city] + \
                str(random.choice(range(10000, 99999)))
            vin = fake.vin()
            brand = random.choice(bus_brand)
            bus_type = random.choice(list(types_of_bus.keys()))
            production_year = np.random.randint(2005, 2019)
            seats, standing_places = types_of_bus[bus_type]
            wheelchair = np.random.randint(2)
            air_conditioning = np.random.randint(2)
            feedback_monitor = np.random.randint(2)
            row_bus = f"{registration_number},{vin},{brand},{bus_type},{production_year},{seats},{standing_places},{wheelchair},{air_conditioning},{feedback_monitor}"
            bus_services_list.append(service_id)
            bus_list_2020.append(row_bus)
            bus_regnum_2020.append(registration_number)
        bus_service_id += 1

    file.write('\n'.join(bus_list_2020))






