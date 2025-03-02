# Data-Warehouse-Bus-Transport-HIVE
University project for the Advanced Nonrelational Databases course. The task is to design and implement data warehouse in HIVE.

## Task Description
Implementing a data warehouse, solution must contain:

- at least three types of data storing,

- internal and external tables,

- partitioning (static and dynamic),

- at least two different complex types,

- bucketing.

Define in natural language 10 competency questions and scenarios, which explain why the specific design decisions were made.

Prepare 10 HQL queries corresponding to the competency questions.

Solution consists of:

1. HQL script creating the data warehouse.

2. Exemplary data and a script loading this data.

3. HQL script with 10 competency questions.

4. Short text file containing scenarios and explanation of the decisions made.

## Scenarios and decisions
### 1. Partitioning: 
Used for tables where queries often filter by specific columns like _month_no, day_type, time_of_day, travel_date, bus_type_. It limits the number of nodes that needs to be scanned when filtering some columns. <br><br>
Partitions in tables are comparatively equal size (_travel_date_  in travel table as the schedule of buses does not vary significantly on different days) or the values possible for each field is limited (like _month_no, day_type, time_of_day and bus_type_). Static partitioning is used for _bus_type_ where we manually decide on number of partitions and to which partition data will be loaded, we need to be sure that we put data into right partition e.g. loading buses of only one type at once! For dynamic paritioning (_month_no, day_type, time_of_day, travel_date_) - partitions are created automatically depending on data we are inserting into, what for travel_date field adding records while manually giving the date may be more complex process, probably this table will grow large in time. 
 
### 2. Bucketing: 
Bucket by _route_id, bus_id_ travel table to improve performance of aggregations and joins. Partitioning here might lead to some larger and some smaller partitions as we assume that some routes have more travels – we use buckets to decompose dataset based on value from hash function.  As the number of travels is around 20k (data of travels is from April) we can also imply that the number of records in the datawarehouse will arise at most to 240k – when storing data for one year, and we have 90 unique routes we decided on splitting data into 50 buckets. <br><br>
Bucketing also on route_id in routes table improves joins and searching on this column, we have 90 routes so splittinig into 10 buckets is reasonable (on average 9 routes per bucket). In queries the route_id field (what is unique attribute) will be used often in queries (e.g. searching for specific routes usually combined with travel table) so map-side joins will work faster on bucketing tables. <br><br>
Bucketing on bus_id into 10 buckets and date_id into 30 buckets – for joins with travel table. 
<br><br>
No partitioning/bucketing on junk table as it has only 12 records.
 
### 3. Data Format: 
- **ORC** – used for routes and buses as it support complex datatypes (in routes table map, in bus array) as well as queries that are using aggregations (travel is join-heavy with other tables)
- **PARQUET** – used for date, time, junk tables, frequently queried for filtering/grouping (_day_type, time_of_day_). Those tables are realatively small tables. Parquet avoids reading unnecessary columns during query execution (columnar storage)
- **TEXTFILE** – used for _bus_office_ table; as it may be easier to use for external systems. (reading data in Excel, Python or R) No partitioning here due to relatively small table.

