import os
import random
from faker import Faker
import numpy as np
from cities import region_postalcode_city, connect_cities
from datetime import datetime, timedelta
from unidecode import unidecode

fake = Faker('pl_PL')

# create the "data" folder if it doesn't exist
data_folder = "data"
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

# file paths within the "data" folder
route_file_path = os.path.join(data_folder, "Route_2020.txt")
service_office_2020_file_path = os.path.join(data_folder, "Service_Office_2020.txt")
bus_2020_file_path = os.path.join(data_folder, "Bus_2020.txt")


schedule_weekend_file_path = os.path.join(data_folder, "Schedule_weekend.txt")
schedule_holiday_file_path = os.path.join(data_folder, "Schedule_holiday.txt")
schedule_weekday_file_path = os.path.join(data_folder, "Schedule_weekday.txt")

travel_2020_file_path = os.path.join(data_folder, "Travel_2020.txt")

validation_2020_file_path = os.path.join(data_folder, "Validation_2020.txt")
ticket_2020_file_path = os.path.join(data_folder, "Ticket_2020.txt")
feedback_2020_file_path = os.path.join(data_folder, "Feedback_2020.txt")

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
def get_avaliable_places(bus_id):

    bus_list = bus_capacities
    for bus in bus_list:
        if bus.split(',')[0] == bus_id:
            return int(bus.split(',')[1])

# function to generate random departure and arrival times

def generate_random_times(n, route):
    times = []
    duration_min = int((((route.split(',')[2]).split('|')[1]).split(':')[1]).strip())

    for _ in range(n):
        departure_hour = np.random.randint(4, 23)
        departure_minute = np.random.randint(60)
        departure_time = datetime.strptime(f"{departure_hour:02d}:{departure_minute:02d}", "%H:%M")
        arrival_time = departure_time + timedelta(minutes=duration_min)

        times.append((departure_time.strftime("%H:%M"), arrival_time.strftime("%H:%M")))
    
    return times

# function to determine if two cities are in the same region


def same_region(city1, city2):
    region1 = find_region(city1)
    region2 = find_region(city2)
    if region1 is not None and region2 is not None:
        return region1 == region2
    else:
        return False

# function to find the region of a city


def find_region(city_name):
    for region, cities in region_postalcode_city.items():
        if city_name in cities.values():
            return region
    return None


def calculate_duration(distance_km, speed_kmh=40):
    # Time = Distance / Speed, converted to minutes
    return int((distance_km / speed_kmh) * 60)

# generate all possible city combinations
city_combinations = connect_cities(region_postalcode_city)

# Route table generation
routes_list = []
routes_to_update_start = []
routes_to_update_end = []


# route dim creation
with open(route_file_path, "w+", encoding="UTF-8") as file:
    for connection, route_number in city_combinations.items():
        route_name = f"{connection[0]} - {connection[1]}"

        if same_region(connection[0], connection[1]):
                distance_km = random.randint(50, 200)
        else:
            distance_km = random.randint(50, 500)
        duration_min = calculate_duration(distance_km)

        # adding some variation
        duration_min += random.randint(-15, 15)

        duration_min = max(60, duration_min)

        metrics = f"distance_km:{distance_km}|duration_min:{duration_min}"

        row_route = f"{route_number},{route_name},{metrics}"
        routes_list.append(row_route)

    file.write('\n'.join(routes_list))


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
        # postal_code = f"{postal_code_prefix}-{np.random.randint(999):03}"
        # address = remove_polish_characters(
        #     fake.street_name() + " " + fake.building_number())
        country = "Poland"
        bus_slots = random.choice(slots)
        if bus_slots == 8:
            size_cat = "small"
        elif bus_slots == 9:
            size_cat = "medium"
        else:
            size_cat = "big"

        bus_slots_cities.append((bus_slots, city))
        row_service_office = f"{bus_service_id},{bus_service_name},{city},{size_cat}"
        service_office_list_2020.append(row_service_office)
        bus_service_id += 1

    file.write('\n'.join(service_office_list_2020))

bus_list_2020 = []
#bus types with number of places available (standing, seating)
types_of_bus = {"minibus": (8, 0), "standard": (15, 7), "low_floor": (10, 5)}
reg_cities = {"CB": "Bydgoszcz", "CT": "Torun", "GD": "Gdansk", "GA": "Gdynia", "NO": "Olsztyn",
              "NE": "Elblag", "WA": "Warszawa", "WR": "Radom", "ZS": "Szczecin", "ZK": "Koszalin"}
cities_reg = {v: k for k, v in reg_cities.items()}

bus_services_list = []
bus_service_id = 1

bus_id = 1
bus_capacities = []

# for static partitioning create separate files fo each bus type
buses_by_type = {bus_type: [] for bus_type in types_of_bus}

# generate bus data for 2020
for num_of_bus, office_city in bus_slots_cities:
    for _ in range(num_of_bus):
        service_id = bus_service_id
        registration_number = cities_reg[office_city] + \
            str(random.choice(range(10000, 99999)))
        
        bus_type = random.choice(list(types_of_bus.keys()))

        seats, standing_places = types_of_bus[bus_type]
        # bus total capacity
        bus_total_capacity = seats + standing_places
        bus_capacities.append(f"{bus_id},{bus_total_capacity}")

        air_conditioning = np.random.randint(2)
        feedback_monitor = np.random.randint(2)
        
        tags = ["air_conditioning", "feedback_monitor", "wheelchair_place"]
        # creating random subset
        additonal_equipment = random.sample(tags, k=random.randint(1, len(tags)))
        # to check
        row_bus = f"{bus_id},{registration_number},{service_id},{'|'.join(additonal_equipment)},{bus_type}"
        bus_services_list.append(service_id)
        bus_list_2020.append(row_bus)
        bus_id+=1
        buses_by_type[bus_type].append(row_bus)
    bus_service_id += 1


for bus_type, rows in buses_by_type.items():
    file_path = os.path.join(data_folder, f"Bus_{bus_type}.txt")
    with open(file_path, "w+", encoding="UTF-8") as file:
        file.write("\n".join(rows))


# creation od time dim
time_table_file_path = os.path.join(data_folder, "Time.txt")

time_rows = []

def get_time_id(time):
    hour, minute = map(int, time.split(":"))
    return time_mapping.get((hour, minute), None)

def get_time_of_day(hour):
    if 0 <= hour < 6:
        return "Night"
    elif 6 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 18:
        return "Afternoon"
    else:
        return "Evening"

time_id = 1
time_mapping = {}
for hour in range(24): 
    for minute in range(60):
        time_of_day = get_time_of_day(hour)
        time_rows.append(f"{time_id},{hour},{minute},{time_of_day}")
        time_mapping[(hour, minute)] = time_id
        time_id += 1
        

with open(time_table_file_path, "w", encoding="UTF-8") as file:
    file.write("\n".join(time_rows))

# print(get_time_id("22:01"))

# creation of junk dim

def get_junk_id(satisfaction_level, occupation_level):
    if (satisfaction_level <= 3):
        sat = "low"
    elif satisfaction_level <= 7:
        sat = "medium"
    else:
        sat = "high"

    if (occupation_level < 0.15):
        occ = "very low"
    elif occupation_level <= 0.3:
        occ = "low"
    elif occupation_level <= 0.75:
        occ = "medium"
    else:
        occ = "high"

    key = (sat, occ)
    return junk_mapping.get(key, None)

junk_table_file_path = os.path.join(data_folder, "Junk.txt")

satisfaction_categories = ["low", "medium", "high"]
occupation_categories = ["very low", "low", "medium", "high"]

junk_rows = []
junk_id = 1
junk_mapping = {}
for satisfaction in satisfaction_categories:
    for occupation in occupation_categories:
        junk_rows.append(f"{junk_id},{satisfaction},{occupation}")
        junk_mapping[(satisfaction, occupation)] = junk_id
        junk_id += 1

with open(junk_table_file_path, "w", encoding="UTF-8") as file:
    file.write("\n".join(junk_rows))


# creation of date dim
x = []

types_of_day = ["weekend", "holiday", "weekday"]

# function to determine day type


def get_daytype_name(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    month = date_obj.month

    if month == 7 or month == 8:
        return types_of_day[1]
    elif date_obj.weekday() < 5:
        return types_of_day[2]
    else:
        return types_of_day[0]
    
for month in range(1, 13):
    if month < 10:
        month_str = f"0{month}"
    else:
        month_str = str(month)

    if month in [1, 3, 5, 7, 8, 10, 12]:
        days = 31
    elif month in [4, 6, 9, 11]:
        days = 30
    else:
        days = 29 # for 2020

    for day in range(1, days + 1):
        if day < 10:
            day_str = f"0{day}"
        else:
            day_str = str(day)
        date_str = f"2020-{month_str}-{day_str}"
        x.append(date_str)

date_file_path = os.path.join(data_folder, "Date.txt")

dates = []
for idx, date in enumerate(x, start=1):
    year = 2020
    month_no = int(date.split("-")[1])
    month_name = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ][month_no - 1]
    day_type = get_daytype_name(date)
    dates.append(f"{idx},{date},{year},{month_name},{month_no},{day_type}")

with open(date_file_path, "w", encoding="UTF-8") as file:
    file.write("\n".join(dates))

def get_date_id(date_str):
    for line in dates:
        date_components = line.split(',')
        if date_components[1] == date_str:
            return int(date_components[0])



used_dates_2020 = []
# for presenting purposed we use only data for two months
for i in range(1, 10):
    dateApril1 = ("2020-" + "04-0" + str(i))
    used_dates_2020.append(dateApril1)

for i in range(10, 31):
    dateApril2 = ("2020-" + "04-" + str(i))
    used_dates_2020.append(dateApril2)

for i in range(1, 10):
    dateMay1 = ("2020-" + "05-0" + str(i))
    used_dates_2020.append(dateMay1)

for i in range(10, 32):
    dateMay2 = ("2020-" + "05-" + str(i))
    used_dates_2020.append(dateMay2)


#### CREATION OF FACT TABLE

# Schedule table generation

schedule_holiday = []
schedule_weekday = []
schedule_weekend = []

# schedule_holiday.append("schedule_id,route_number,departure_time,arrival_time,day_type")
# schedule_weekday.append("schedule_id,route_number,departure_time,arrival_time,day_type")
# schedule_weekend.append("schedule_id,route_number,departure_time,arrival_time,day_type")

# generating schedule for routes
for route in routes_list:
        route_num = route.split(',')[0]
        # some routes have more buses
        add_buses = 0;
        if int(route_num)%3 == 0:
            add_buses = 3

        for i in range(3):
            schedule = []
            if i == 0:
                schedule = schedule_weekend
                buses_per_day = np.random.randint(3 + add_buses, 5 + add_buses)
            elif i == 1:
                schedule = schedule_holiday
                buses_per_day = np.random.randint(3 + add_buses, 5 + add_buses)
            else:
                schedule = schedule_weekday
                buses_per_day = np.random.randint(3 + add_buses, 7 + add_buses)

            day_type = types_of_day[i]
            
            random_times = generate_random_times(buses_per_day, route)
            for departure, arrival in random_times:
                
                row_schedule = f"{route_num},{departure},{arrival},{day_type}"
                #row_schedule = f"{schedule_id},{route_num},{departure},{arrival},{day_type}"
                schedule.append(row_schedule)
            

# with open(schedule_weekend_file_path, "w+", encoding="UTF-8") as file:
#     file.write('\n'.join(schedule_weekend))

# with open(schedule_weekday_file_path, "w+", encoding="UTF-8") as file:
#     file.write('\n'.join(schedule_weekday))

# with open(schedule_holiday_file_path, "w+", encoding="UTF-8") as file:
#     file.write('\n'.join(schedule_holiday))

# Travel table generation
travel_list_2020 = []
travel_id = 1


# schedule_holiday = schedule_holiday[1:]
# schedule_weekday = schedule_weekday[1:]
# schedule_weekend = schedule_weekend[1:]

lvls = np.arange(1, 11)
satisfaction_prob_april = [0.05, 0.15, 0.15, 0.15, 0.1, 0.05, 0.1, 0.05, 0.1, 0.1]
satisfaction_prob_may = [0.05, 0.05, 0.05, 0.05, 0.1, 0.15, 0.2, 0.15, 0.1, 0.1]

def get_satisfaction_on_month(date):
    if datetime.strptime(date, "%Y-%m-%d").month == 4:
        return satisfaction_prob_april
    return satisfaction_prob_may


with open(travel_2020_file_path, "w+", encoding="UTF-8") as file:

    data_source = used_dates_2020
    
    #travel_list_2020.append(f"travel_id,bus_registration,route_number,schedule_id,travel_date") # for dynamic partitioning
    for date in data_source:
        day = get_daytype_name(date)
        if day == "weekday":
            schedule_type = schedule_weekday
        elif day == "holiday":
            schedule_type = schedule_holiday
        else:
            schedule_type = schedule_weekend

        for schedule in schedule_type:
            bus_route = int(schedule.split(',')[0])
            bus_id = get_random_bus_from_service(routes_list[(bus_route - 1)])
            # travel_schedule = schedule.split(',')[0]
            bus_departure = schedule.split(',')[1]
            bus_arrival = schedule.split(',')[2]

            places = get_avaliable_places(bus_id)
            occupancy = np.random.randint(2, places + 1)
            tickets_validated = 0

            #simulating bus validation
            for _ in range(occupancy):
                is_validated = np.random.choice([0, 1], p=[0.05, 0.95])

                if is_validated:
                    tickets_validated +=1

            satisfactions_received = np.random.randint(min(3, occupancy))
            satisf_surveys_num = satisfactions_received
            total_satisfaction_lvl = 0
            while satisfactions_received > 0:
                total_satisfaction_lvl += np.random.choice(lvls, p=get_satisfaction_on_month(date))
                satisfactions_received -= 1
            avg_satisfaction_lvl = 0

            if satisf_surveys_num > 0:
                avg_satisfaction_lvl = total_satisfaction_lvl/satisf_surveys_num

            occupation_perc = occupancy/places
            junk_id = get_junk_id(avg_satisfaction_lvl, occupation_perc)
            row_travel = f"{bus_id},{bus_route},{get_time_id(bus_departure)},{get_time_id(bus_arrival)},{tickets_validated},{places},{avg_satisfaction_lvl},{satisf_surveys_num},{junk_id},{get_date_id(date)}"
            travel_list_2020.append(row_travel)

    file.write('\n'.join(travel_list_2020))
