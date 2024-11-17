import os
import random
from faker import Faker
from datetime import datetime
import numpy as np
import dates_2020
from cities import region_postalcode_city, connect_cities
import service_office_gen as so
from bus_stops_gen import get_bus_stop_names
from datetime import datetime, timedelta

fake = Faker('pl_PL')

# create the "data" folder if it doesn't exist
data_folder = "data"
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

# file paths within the "data" folder
route_file_path = os.path.join(data_folder, "Route_2020.txt")
schedule_weekend_file_path = os.path.join(data_folder, "Schedule_weekend.txt")
schedule_holiday_file_path = os.path.join(data_folder, "Schedule_holiday.txt")
schedule_weekday_file_path = os.path.join(data_folder, "Schedule_weekday.txt")

travel_2020_file_path = os.path.join(data_folder, "Travel_2020.txt")

validation_2020_file_path = os.path.join(data_folder, "Validation_2020.txt")
ticket_2020_file_path = os.path.join(data_folder, "Ticket_2020.txt")
feedback_2020_file_path = os.path.join(data_folder, "Feedback_2020.txt")

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

# function to generate random departure and arrival times

def generate_random_times(n, route):
    times = []
    duration_min = int((route.split(',')[6]).split(':')[1].strip())

    for _ in range(n):
        departure_hour = np.random.randint(4, 23)
        departure_minute = np.random.randint(60)
        departure_time = datetime.strptime(f"{departure_hour:02d}:{departure_minute:02d}", "%H:%M")
        arrival_time = departure_time + timedelta(minutes=duration_min)

        times.append((departure_time.strftime("%H:%M"), arrival_time.strftime("%H:%M")))

        # print(route)
        # print(duration_min)
        # print(departure_time.strftime("%H:%M"))
        # print(arrival_time.strftime("%H:%M"))
    
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

# generate all possible city combinations
city_combinations = connect_cities(region_postalcode_city)


# Route table generation
routes_list = []
routes_to_update_start = []
routes_to_update_end = []

def calculate_duration(distance_km, speed_kmh=40):
    # Time = Distance / Speed, converted to minutes
    return int((distance_km / speed_kmh) * 60)

with open(route_file_path, "w+", encoding="UTF-8") as file:
    for connection, route_number in city_combinations.items():
        route_name = f"{connection[0]} - {connection[1]}"
        possible_start_stops = get_bus_stop_names(connection[0])
        possible_end_stops = get_bus_stop_names(connection[1])
        start_stop = random.choice(possible_start_stops)
        end_stop = random.choice(possible_end_stops)

        all_tags = ["fast", "scenic", "economy"]

        random_tags = random.sample(all_tags, k=random.randint(1, len(all_tags)))

        if same_region(connection[0], connection[1]):
                distance_km = random.randint(50, 200)
        else:
            distance_km = random.randint(50, 500)
        duration_min = calculate_duration(distance_km)

        # adding some variation
        duration_min += random.randint(-15, 15)

        duration_min = max(10, duration_min)

        metrics = f"distance_km:{distance_km},duration_min:{duration_min}"

        row_route = f"{route_number},{route_name},{start_stop},{end_stop},{'|'.join(random_tags)},{metrics}"
        routes_list.append(row_route)

    file.write('\n'.join(routes_list))


# Schedule table generation
schedule_list_2020 = []
schedule_id = 1

schedule_holiday = []
schedule_weekday = []
schedule_weekend = []


for route in routes_list:
        route_num = route.split(',')[0]
        for i in range(3):
            schedule = []
            if i == 0:
                schedule = schedule_weekend
            elif i == 1:
                schedule = schedule_holiday
            else:
                schedule = schedule_weekday

            day_type = types_of_day[i]
            buses_per_day = np.random.randint(3, 10)
            random_times = generate_random_times(buses_per_day, route)
            for departure, arrival in random_times:
                row_schedule = f"{schedule_id},{route_num},{departure},{arrival},{day_type}"
                schedule_list_2020.append(row_schedule)
                schedule.append(row_schedule)
                schedule_id += 1
            

with open(schedule_weekend_file_path, "w+", encoding="UTF-8") as file:
    file.write('\n'.join(schedule_weekend))

with open(schedule_weekday_file_path, "w+", encoding="UTF-8") as file:
    file.write('\n'.join(schedule_weekday))

with open(schedule_holiday_file_path, "w+", encoding="UTF-8") as file:
    file.write('\n'.join(schedule_holiday))

# Travel table generation
travel_list_2020 = []
travel_id = 1

with open(travel_2020_file_path, "w+", encoding="UTF-8") as file:
    time_snapshot = 0
    data_source = dates_2020.x
    schedule_source = schedule_list_2020
    weekday_schedules = [schedule for schedule in schedule_source if schedule.split(',')[4] == "weekday"]
    holiday_schedules = [schedule for schedule in schedule_source if schedule.split(',')[4] == "holiday"]
    weekend_schedules = [schedule for schedule in schedule_source if schedule.split(',')[4] == "weekend"]

    for date in data_source:
        day = get_daytype_name(date)
        if day == "weekday":
            for schedule in weekday_schedules:
                bus_route = int(schedule.split(',')[1])
                bus_registration = so.get_random_bus_from_service(routes_list[(bus_route - 1)])
                travel_schedule = schedule.split(',')[0]
                row_travel = f"{travel_id},{bus_registration},{bus_route},{travel_schedule},{date}"
                travel_list_2020.append(row_travel)
                travel_id += 1
        elif day == "holiday":
            for schedule in holiday_schedules:
                bus_route = int(schedule.split(',')[1])
                bus_registration = so.get_random_bus_from_service(routes_list[bus_route - 1])
                travel_schedule = schedule.split(',')[0]
                row_travel = f"{travel_id},{bus_registration},{bus_route},{travel_schedule},{date}"
                travel_list_2020.append(row_travel)
                travel_id += 1
        else:
            for schedule in weekend_schedules:
                bus_route = int(schedule.split(',')[1])
                bus_registration = so.get_random_bus_from_service(routes_list[bus_route - 1])
                travel_schedule = schedule.split(',')[0]
                row_travel = f"{travel_id},{bus_registration},{bus_route},{travel_schedule},{date}"
                travel_list_2020.append(row_travel)
                travel_id += 1
    file.write('\n'.join(travel_list_2020))

# Validations table generation
validations_list_2020 = []
travel_occupations = []
target_ticket_id = 1
all_travels = travel_list_2020
lvls = np.arange(1, 11)
satisfaction_prob = [0.05, 0.05, 0.05, 0.05, 0.1, 0.15, 0.2, 0.15, 0.1, 0.1]

# Feedback table generation
feedback_list_2020 = []
feedback_id = 1

# Ticket table generation
ticket_list_2020 = []
ticket_id = 1

with open(validation_2020_file_path, "w+", encoding="UTF-8") as file:
    for travel in all_travels:
        bus = travel.split(',')[1]
        travel_id = travel.split(',')[0]
        places = so.get_avaliable_places(bus)
        occupancy = np.random.randint(2, places + 1)
        non_validated = 0

        for _ in range(occupancy):
            is_validated = np.random.choice([0, 1], p=[0.05, 0.95])

            if is_validated:
                row_validation = f"{ticket_id},{travel_id}"
                validations_list_2020.append(row_validation)
                satisfactions_received = np.random.randint(occupancy + 1)
                while satisfactions_received > 0:
                    satisfaction_lvl = np.random.choice(lvls, p=satisfaction_prob)
                    row_feedback = f"{feedback_id},{travel_id},{satisfaction_lvl}"
                    feedback_list_2020.append(row_feedback)
                    feedback_id += 1
                    satisfactions_received -= 1

            else:
                non_validated += 1

            # adding all tickets validated or not to a list
            name = so.remove_polish_characters(fake.first_name())
            surname = so.remove_polish_characters(fake.last_name())
            email = fake.email()
            row_ticket = f"{ticket_id},{name},{surname},{email}"
            ticket_list_2020.append(row_ticket)
            ticket_id += 1

    file.write('\n'.join(validations_list_2020))

with open(ticket_2020_file_path, "w+", encoding="UTF-8") as file:
    file.write('\n'.join(ticket_list_2020))

with open(feedback_2020_file_path, "w+", encoding="UTF-8") as file:
    file.write('\n'.join(feedback_list_2020))

