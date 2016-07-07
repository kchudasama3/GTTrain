from __future__ import print_function
 
import mysql.connector
from mysql.connector import errorcode
 
import random
import datetime
import time
 
 
# This script creates and initializes a mysql database on your
# localhost. The default config mysql connects to the database with
# the user: cs4400 and password: cs4400password, this can be customized
# by changing the 'cnx' variable in the main method. In addition to
# creating the database and its tables, this script also populates
# the database according to the given guidelines.
 
 
DB_NAME = 'gt_train'
 
TABLES = {}
 
TABLES['trainroute'] = (
    "CREATE TABLE `trainroute` ("
    "`trainnumber` varchar(255) NOT NULL,"
    "`first_class_price` DECIMAL(5,2),"
    "`second_class_price` DECIMAL(5,2),"
    "PRIMARY KEY(`trainnumber`)"
    ") ENGINE=InnoDB"  
)
 
TABLES['stop'] = (
    "CREATE TABLE `stop` ("
    "`trainnumber` varchar(255) NOT NULL,"
    "`stationname` varchar(255) NOT NULL,"
    "`arrival_time` TIME NOT NULL,"
    "`departure_time` TIME NOT NULL,"
    "PRIMARY KEY(`trainnumber`, `stationname`),"
    "FOREIGN KEY(`trainnumber`) references trainroute(`trainnumber`),"
    "FOREIGN KEY(`stationname`) references station(`name`)"
    ") ENGINE=InnoDB"
)
 
 
TABLES['station'] = (
    "CREATE TABLE `station` ("
    "`name` varchar(255) NOT NULL,"
    "`location` varchar(255) NOT NULL,"
    "PRIMARY KEY(`name`)"
    ") ENGINE=InnoDB"
 
 
)
 
TABLES['reserves'] = (
    "CREATE TABLE `reserves` ("
    "`trainnumber` varchar(255) NOT NULL,"
    "`reservationid` INT NOT NULL,"
    "`class` enum('first','second') NOT NULL,"
    "`departure_date` date NOT NULL,"
    "`passenger_name` varchar(255) NOT NULL,"
    "`number_of_bags` INT NOT NULL,"
    "`departs_from` varchar(255) NOT NULL,"
    "`arrives_at` varchar(255) NOT NULL,"
    "PRIMARY KEY (`trainnumber`, `reservationid`),"
    "FOREIGN KEY(`trainnumber`) references trainroute(`trainnumber`),"
    "FOREIGN KEY(`reservationid`) references reservation(`reservationid`)"
    ") ENGINE=InnoDB"
 
   
)
 
TABLES['reservation'] = (
    "CREATE TABLE `reservation` ("
    "`reservationid` INT NOT NULL,"
    "`username` varchar(255) NOT NULL,"
    "`cardnumber` varchar(16),"
    "`is_cancelled` boolean DEFAULT false,"
    "`total_cost` DECIMAL(5,2) NOT NULL,"
    "PRIMARY KEY(`reservationid`),"
    "FOREIGN KEY(`username`) references user_customer(`username`),"
    "FOREIGN KEY(`cardnumber`) references payment_info(`cardnumber`) ON DELETE SET NULL"
    ") ENGINE=InnoDB"
 
   
)
 
TABLES['review'] = (
    "CREATE TABLE `review` ("
    "`reviewid` INT NOT NULL,"
    "`comment` TEXT,"
    "`rating` enum('very good','good','neutral','bad','very bad') NOT NULL,"
    "`username` varchar(255) NOT NULL,"
    "`trainnumber` varchar(255) NOT NULL,"
    "PRIMARY KEY(`reviewid`),"
    "FOREIGN KEY(`username`) references user_customer(`username`),"
    "FOREIGN KEY(`trainnumber`) references trainroute(`trainnumber`)"
    ") ENGINE=InnoDB"
 
   
)
 
TABLES['user'] = (
    "CREATE TABLE `user` ("
    "`username` varchar(255) NOT NULL,"
    "`password` varchar(255) NOT NULL,"
    "PRIMARY KEY(`username`)"
    ") ENGINE=InnoDB"
 
)
 
TABLES['user_customer'] = (
    "CREATE TABLE `user_customer` ("
    "`username` varchar(255) NOT NULL,"
    "`email` varchar(255) NOT NULL,"
    "`is_student` BOOLEAN DEFAULT false,"
    "PRIMARY KEY(`username`),"
    "FOREIGN KEY(`username`) references user(`username`)"
    ") ENGINE=InnoDB"
 
   
)
 
TABLES['user_manager'] = (
    "CREATE TABLE `user_manager` ("
    "`username` varchar(255) NOT NULL,"
    "PRIMARY KEY(`username`),"
    "FOREIGN KEY(`username`) references user(`username`)"
    ") ENGINE=InnoDB"
 
   
)
 
TABLES['payment_info'] = (
    "CREATE TABLE `payment_info` ("
    "`cardnumber` varchar(16) NOT NULL,"
    "`cvv` INT NOT NULL,"
    "`exp_date` date NOT NULL,"
    "`name_on_card` varchar(255) NOT NULL,"
    "`username` varchar(255) NOT NULL,"
    "PRIMARY KEY(`cardnumber`),"
    "FOREIGN KEY(`username`) references user_customer(`username`)"
    ") ENGINE=InnoDB"
 
)
 
TABLES['system_info'] = (
    "CREATE TABLE `system_info` ("
    "`max_num_of_baggage` INT NOT NULL,"
    "`num_free_baggage` INT,"
    "`student_discount` DECIMAL(5,2),"
    "`change_fee` DECIMAL(5,2),"
    "PRIMARY KEY(`max_num_of_baggage`)"
    ") ENGINE=InnoDB"
 
   
)
 
 
 
def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET `utf8`".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
 
    try:
        cnx.database = DB_NAME    
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(cursor)
            cnx.database = DB_NAME
        else:
            print(err)
 
def populate_database(cursor):
 
    #               GUIDELINES                       #
    #------------------------------------------------#
    #
    # Jan.1.2016 - May.31.2016
    # At least 25 users (20 customers, 5 managers)  *DONE*
    # At least 5 customers w/o payment info         *DONE* (kinda)
    # At least 5 customers w/ a credit card stored  *DONE*
    # 6 stations                                    *DONE*
    # 8 Train routes (each one w/ at least 3 stops) *DONE*
    # At least 40 Reservations                      *DONE*
    # - 20 should have a future end date            *DONE*
    # - 7 should have two tickets                   *DONE*
    # - 10 should be cancelled                      *DONE*
    # Each train route reserved at least twice      *DONE*
    # At least 20 reviews (>1 for each route)       *DONE*
 
    "USERS"
    users = []
    customers = []
    for i in range(20):
        if (i < 10):
            name = "customer0" + str(i)
        else:
            name = "customer" + str(i)
        uname = name
        pword = name + "password"
        student = False
        if i >= 10:
            if i%3==0:
                email = name + "@gmail.com"
            else:
                email = name + "@yahoo.com"
        else:
            email = name + "@gatech.edu"
            student = True
        users.append((uname, pword))
        customers.append((uname, email, student))
 
    managers = []
    for i in range(5):
        uname = "manager" + str(i)
        pword = "manager" + str(i) + "password"
        users.append((uname, pword))
        managers.append(uname)
 
    for (u, p) in users:
        user_data = (u, p)
 
 
        new_user = ("CREATE USER %s@'localhost'"
                            "IDENTIFIED BY %s;")
        try:
            cursor.execute(new_user, user_data)
        except mysql.connector.Error as err:
            print("MySQL User already exists")
       
 
        grant_permissions = ("GRANT ALL ON gt_train.* TO %s@'localhost'")
        try:
            cursor.execute(grant_permissions, (u,))
        except mysql.connector.Error as err:
            print(err.msg)
       
       
        add_user = ("INSERT INTO user "
                    "(username, password) "
                    "VALUES (%s, %s)")
       
        try:
            cursor.execute(add_user, user_data)
        except mysql.connector.Error as err:
            print(err.msg)
 
    for (u, e, s) in customers:
        add_user = ("INSERT INTO user_customer "
                    "(username, email, is_student) "
                    "VALUES (%s, %s, %s)")
        user_data = (u, e, s)
        try:
            cursor.execute(add_user, user_data)
        except mysql.connector.Error as err:
            print(err.msg)
 
    # Not sure why tf this wont worl
 
    for u in managers:
        #print(u)
        add_user = ("INSERT INTO user_manager "
                    "(username) "
                    "VALUES (%s)")
        try:
            cursor.execute(add_user, (u,))
        except mysql.connector.Error as err:
            print(err.msg)
       
 
    "Payment Info"
    # # 10 users with Payment Info
    # card_names = ["Sean Washington", "Brandon Riggs", "Derek Smith",
    #             "Rebecca Hamilton", "Lorin Ashton", "Sam Jackson",
    #             "Rohan Patel", "Bill Blunt", "Kendall Rogers",
    #             "Hannibal Burress"]
    # nameSelector = 0
    # for i in range(10):
    #     (uname, email, student) = customers[i*2]
    #     card_no = ""
    #     cvv_string = ""
    #     for i in range(16):
    #         card_no += str(random.randint(0, 9))
    #     for i in range(3):
    #         if i == 0:
    #             cvv_string += str(random.randint(1, 9))
    #         else:
    #             cvv_string += str(random.randint(0, 9))
    #     cvv = int(cvv_string)
       
    #     yy = random.randint(2016, 2030)
    #     mm = random.randint(1, 12)
    #     dd = random.randint(1, 28)
    #     if yy == 2016 and mm < 5:
    #         yy += 1
    #     if dd < 10:
    #         dd_str = "0" + str(dd)
    #         dd = int(dd_str)
 
    #     exp_date = datetime.date(yy, mm, dd)
 
    #     real_name = card_names[nameSelector]
    #     nameSelector += 1
 
    #     add_payment_info = ("INSERT INTO payment_info "
    #                 "(cardnumber, cvv, exp_date, name_on_card, username) "
    #                 "VALUES (%s, %s, %s, %s, %s)")
    #     card_data = (card_no, cvv, exp_date, real_name, uname)
    #     try:
    #         cursor.execute(add_payment_info, card_data)
    #     except mysql.connector.Error as err:
    #         print(err.msg)


    add_payment_info = ("INSERT INTO payment_info "
                "(cardnumber, cvv, exp_date, name_on_card, username) "
                "VALUES (%s, %s, %s, %s, %s)")
    card_data = ('1111000011110000', '101', datetime.date(2017, 10, 10), 'Test Customer', 'customer00')
    try:
        cursor.execute(add_payment_info, card_data)
    except mysql.connector.Error as err:
        print(err.msg)
    card_data = ('2111000011110001', '201', datetime.date(2017, 10, 10), 'Customer 21', 'customer01')
    try:
        cursor.execute(add_payment_info, card_data)
    except mysql.connector.Error as err:
        print(err.msg)
    card_data = ('2111000011110002', '202', datetime.date(2017, 10, 10), 'Customer 22', 'customer01')
    try:
        cursor.execute(add_payment_info, card_data)
    except mysql.connector.Error as err:
        print(err.msg)
    card_data = ('3111000011110001', '301', datetime.date(2017, 10, 10), 'Customer 31', 'customer02')
    try:
        cursor.execute(add_payment_info, card_data)
    except mysql.connector.Error as err:
        print(err.msg)
    card_data = ('3111000011110002', '302', datetime.date(2017, 10, 10), 'Customer 32', 'customer02')
    try:
        cursor.execute(add_payment_info, card_data)
    except mysql.connector.Error as err:
        print(err.msg)
    card_data = ('4111000011110001', '401', datetime.date(2017, 10, 10), 'Customer 41', 'customer03')
    try:
        cursor.execute(add_payment_info, card_data)
    except mysql.connector.Error as err:
        print(err.msg)
    card_data = ('4111000011110002', '402', datetime.date(2017, 10, 10), 'Customer 42', 'customer03')
    try:
        cursor.execute(add_payment_info, card_data)
    except mysql.connector.Error as err:
        print(err.msg)
    card_data = ('5111000011110001', '501', datetime.date(2017, 10, 10), 'Customer 51', 'customer04')
    try:
        cursor.execute(add_payment_info, card_data)
    except mysql.connector.Error as err:
        print(err.msg)
    card_data = ('5111000011110002', '502', datetime.date(2017, 10, 10), 'Customer 52', 'customer04')
    try:
        cursor.execute(add_payment_info, card_data)
    except mysql.connector.Error as err:
        print(err.msg)
    card_data = ('6111000011110001', '601', datetime.date(2017, 10, 10), 'Customer 61', 'customer05')
    try:
        cursor.execute(add_payment_info, card_data)
    except mysql.connector.Error as err:
        print(err.msg)
    card_data = ('6111000011110002', '602', datetime.date(2017, 10, 10), 'Customer 62', 'customer05')
    try:
        cursor.execute(add_payment_info, card_data)
    except mysql.connector.Error as err:
        print(err.msg)




    # 6 Train Stations
 
    train_stations = {}
    train_stations['Atlanta'] = "ATL Midtown Station"
    train_stations['Boston'] = "Red Sox Trains"
    train_stations['Nashville'] = "Music City Train Station"
    train_stations['New York City'] = "NYC Terminal"
    train_stations['Detroit'] = "Detroit Trains"
    train_stations['Miami'] = "South Beach Station"
    train_stations['Richmond'] = "Virginia Train Stop"
 
    for key in train_stations:
        station_info = ("INSERT INTO station "
                    "(name, location) "
                    "VALUES (%s, %s)")
        station_data = (train_stations[key], key)
        try:
            cursor.execute(station_info, station_data)
        except mysql.connector.Error as err:
            print(err.msg)
 
    # 8 Train Routes
    train_routes = [("101", 110.0, 50.0),
                    ("246", 120.0, 60.0),
                    ("808", 100.0, 50.0),
                    ("123", 125.0, 60.0),
                    ("420", 200.0, 100.0),
                    ("666", 80.0, 40.0),
                    ("707", 100.0, 50.0),
                    ("912", 90.0, 50.0)]
    for (num, fcp, scp) in train_routes:
        route_info = ("INSERT INTO trainroute "
                    "(trainnumber, first_class_price, second_class_price) "
                    "VALUES (%s, %s, %s)")
        route_data = (num, fcp, scp)
        try:
            cursor.execute(route_info, route_data)
        except mysql.connector.Error as err:
            print(err.msg)
 
    # Add Stops to Train Routes
 
    route1 = [("420", train_stations['Miami'], datetime.time(4,0,0), datetime.time(4,30,0)),
            ("420", train_stations['Atlanta'], datetime.time(11,0,0), datetime.time(11,30,0)),
            ("420", train_stations['Richmond'], datetime.time(20,0,0), datetime.time(20,30,0)),
            ("420", train_stations['New York City'], datetime.time(23,0,0), datetime.time(23,30,0))]
    route2 = [("707",train_stations['Atlanta'], datetime.time(6,0,0), datetime.time(6,30,0)),
            ("707", train_stations['Nashville'], datetime.time(10,0,0), datetime.time(10,30,0)),
            ("707", train_stations['Detroit'], datetime.time(14,0,0), datetime.time(14,30,0))]
    route3 = [("123", train_stations['New York City'], datetime.time(4,0,0), datetime.time(4,30,0)),
            ("123", train_stations['Boston'], datetime.time(9,0,0), datetime.time(9,30,0)),
            ("123", train_stations['Nashville'], datetime.time(19,0,0), datetime.time(19,30,0)),
            ("123", train_stations['Atlanta'], datetime.time(23,0,0), datetime.time(23,30,0))]
    route4 = [("808", train_stations['Miami'], datetime.time(4,0,0), datetime.time(4,30,0)),
            ("808", train_stations['Atlanta'], datetime.time(12,0,0), datetime.time(12,30,0)),
            ("808", train_stations['Nashville'], datetime.time(16,0,0), datetime.time(16,30,0)),
            ("808", train_stations['Boston'], datetime.time(23,0,0), datetime.time(23,30,0))]
    route5 = [("246",train_stations['Detroit'], datetime.time(6,0,0), datetime.time(6,30,0)),
            ("246", train_stations['Boston'], datetime.time(10,0,0), datetime.time(10,30,0)),
            ("246", train_stations['Atlanta'], datetime.time(14,0,0), datetime.time(14,30,0))]
    route6 = [("101",train_stations['Richmond'], datetime.time(6,0,0), datetime.time(6,30,0)),
            ("101", train_stations['Boston'], datetime.time(10,0,0), datetime.time(10,30,0)),
            ("101", train_stations['New York City'], datetime.time(14,0,0), datetime.time(14,30,0))]
    route7 = [("912",train_stations['Atlanta'], datetime.time(6,0,0), datetime.time(6,30,0)),
            ("912", train_stations['Richmond'], datetime.time(15,0,0), datetime.time(15,30,0)),
            ("912", train_stations['New York City'], datetime.time(19,0,0), datetime.time(19,30,0))]
    route8 = [("666",train_stations['Nashville'], datetime.time(6,0,0), datetime.time(6,30,0)),
            ("666", train_stations['Richmond'], datetime.time(14,0,0), datetime.time(14,30,0)),
            ("666", train_stations['Boston'], datetime.time(18,0,0), datetime.time(18,30,0))]
 
    allRoutes = [route1, route2, route3, route4, route5, route6, route7, route8]
 
    for route in allRoutes:
        for stp in route:
            add_stop = ("INSERT INTO stop"
                    "(trainnumber, stationname, arrival_time, departure_time)"
                    "VALUES (%s, %s, %s, %s)")
            stop_data = (stp[0], stp[1], stp[2], stp[3])
            try:
                cursor.execute(add_stop, stop_data)
            except mysql.connector.Error as err:
                print(err.msg)
 
    reviews = ("INSERT INTO review "
               "(reviewid, comment, rating, username, trainnumber)"
               "VALUES (%s, %s, %s, %s, %s)")
    review_info = ('1', 'Awesome', "very good", "customer00", "101")
    try:
        cursor.execute(reviews, review_info)
    except mysql.connector.Error as err:
        print(err.msg)
    review_info = ('2', 'Poor', "very bad", "customer00", "101")
    try:
        cursor.execute(reviews, review_info)
    except mysql.connector.Error as err:
        print(err.msg)
    review_info = ('3', 'Great', "very good", "customer00", "123")
    try:
        cursor.execute(reviews, review_info)
    except mysql.connector.Error as err:
        print(err.msg)
    review_info = ('4', 'Okay', "good", "customer00", "123")
    try:
        cursor.execute(reviews, review_info)
    except mysql.connector.Error as err:
        print(err.msg)
    review_info = ('5', 'Bad', "bad", "customer00", "123")
    try:
        cursor.execute(reviews, review_info)
    except mysql.connector.Error as err:
        print(err.msg)
    review_info = ('6', 'Bad', "very bad", "customer00", "123")
    try:
        cursor.execute(reviews, review_info)
    except mysql.connector.Error as err:
        print(err.msg)
    review_info = ('7', 'Awesome', "very good", "customer10", "246")
    try:
        cursor.execute(reviews, review_info)
    except mysql.connector.Error as err:
        print(err.msg)
    review_info = ('8', 'Not Good', "bad", "customer10", "246")
    try:
        cursor.execute(reviews, review_info)
    except mysql.connector.Error as err:
        print(err.msg)
    review_info = ('9', "Don't Care", "neutral", "customer19", "420")
    try:
        cursor.execute(reviews, review_info)
    except mysql.connector.Error as err:
        print(err.msg)
    review_info = ('10', 'Great', "good", "customer19", "420")
    try:
        cursor.execute(reviews, review_info)
    except mysql.connector.Error as err:
        print(err.msg)
    review_info = ('11', 'Great', "good", "customer14", "420")
    try:
        cursor.execute(reviews, review_info)
    except mysql.connector.Error as err:
        print(err.msg)
    review_info = ('12', 'Poor service', "bad", "customer14", "666")
    try:
        cursor.execute(reviews, review_info)
    except mysql.connector.Error as err:
        print(err.msg)
    review_info = ('13', 'Horrible People', "very bad", "customer14", "666")
    try:
        cursor.execute(reviews, review_info)
    except mysql.connector.Error as err:
        print(err.msg)
    review_info = ('14', 'Great', "good", "customer16", "707")
    try:
        cursor.execute(reviews, review_info)
    except mysql.connector.Error as err:
        print(err.msg)
    review_info = ('15', 'Horrible', "very bad", "customer16", "808")
    try:
        cursor.execute(reviews, review_info)
    except mysql.connector.Error as err:
        print(err.msg)
    review_info = ('16', "Don't Care", "neutral", "customer03", "707")
    try:
        cursor.execute(reviews, review_info)
    except mysql.connector.Error as err:
        print(err.msg)
    review_info = ('17', 'Horrible', "bad", "customer03", "808")
    try:
        cursor.execute(reviews, review_info)
    except mysql.connector.Error as err:
        print(err.msg)
    review_info = ('18', 'Good Service', "good", "customer04", "912")
    try:
        cursor.execute(reviews, review_info)
    except mysql.connector.Error as err:
        print(err.msg)
    review_info = ('19', 'Poor chairs', "very bad", "customer04", "912")
    try:
        cursor.execute(reviews, review_info)
    except mysql.connector.Error as err:
        print(err.msg)
    review_info = ('20', 'Not bad', "good", "customer04", "101")
    try:
        cursor.execute(reviews, review_info)
    except mysql.connector.Error as err:
        print(err.msg)
 
    sys_info = ("INSERT INTO system_info"
                "(max_num_of_baggage, num_free_baggage, student_discount, change_fee)"
                "VALUES (%s, %s, %s, %s)")
    systeminfo = (4, 2, 20, 50)
    try:
        cursor.execute(sys_info, systeminfo)
    except mysql.connector.Error as err:
        print(err.msg)


    #Reservations**
    
    ins_reservation = ("INSERT INTO reservation"
                "(reservationid, username, cardnumber, is_cancelled, total_cost)"
                "VALUES (%s, %s, %s, %s, %s)")
    ins_reserves = ("INSERT INTO reserves"
                "(trainnumber, reservationid, class, departure_date, passenger_name, number_of_bags, departs_from, arrives_at)"
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")

    # 20 Future Date Reservations

    reservation = (227, 'customer00', '1111000011110000', 0, 200.0)
    reserves = ('420', 227, 'first', datetime.date(2016, 5, 13), 'Passenger 13', 1, train_stations['Miami'], train_stations['New York City'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)

    try:
        cursor.execute(ins_reserves, reserves)
    except mysql.connector.Error as err:
        print(err.msg)
    

    reservation = (392, 'customer00', '1111000011110000', 0, 90.0)
    reserves = ('912', 392, 'first', datetime.date(2016, 5, 16), 'Passenger 16', 1, train_stations['Atlanta'], train_stations['New York City'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
        
    try:
        cursor.execute(ins_reserves, reserves)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (463, 'customer00', '1111000011110000', 0, 100.0)
    reserves = ('808', 463, 'first', datetime.date(2016, 5, 19), 'Passenger 19', 1, train_stations['Miami'], train_stations['Boston'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
        
    try:
        cursor.execute(ins_reserves, reserves)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (541, 'customer00', '1111000011110000', 0, 100.0)
    reserves = ('808', 541, 'first', datetime.date(2016, 5, 11), 'Passenger 11', 1, train_stations['Miami'], train_stations['Boston'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
        
    try:
        cursor.execute(ins_reserves, reserves)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (877, 'customer00', '1111000011110000', 0, 100.0)
    reserves = ('707', 877, 'first', datetime.date(2016, 5, 15), 'Passenger 15', 1, train_stations['Atlanta'], train_stations['Detroit'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
        
    try:
        cursor.execute(ins_reserves, reserves)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (894, 'customer00', '1111000011110000', 0, 100.0)
    reserves = ('808', 894, 'first', datetime.date(2016, 5, 3), 'Passenger 3', 1, train_stations['Miami'], train_stations['Boston'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
        
    try:
        cursor.execute(ins_reserves, reserves)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (1335, 'customer00', '1111000011110000', 0, 110.0)
    reserves = ('101', 1335, 'first', datetime.date(2016, 5, 17), 'Passenger 17', 1, train_stations['Richmond'], train_stations['New York City'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
        
    try:
        cursor.execute(ins_reserves, reserves)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (1505, 'customer00', '1111000011110000', 0, 120.0)
    reserves = ('246', 1505, 'first', datetime.date(2016, 5, 10), 'Passenger 10', 1, train_stations['Detroit'], train_stations['Atlanta'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
        
    try:
        cursor.execute(ins_reserves, reserves)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (1713, 'customer00', '1111000011110000', 0, 125.0)
    reserves = ('123', 1713, 'first', datetime.date(2016, 5, 12), 'Passenger 12', 1, train_stations['New York City'], train_stations['Atlanta'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
        
    try:
        cursor.execute(ins_reserves, reserves)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (2048, 'customer00', '1111000011110000', 0, 80.0)
    reserves = ('666', 2048, 'first', datetime.date(2016, 5, 6), 'Passenger 6', 1, train_stations['Nashville'], train_stations['Boston'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
        
    try:
        cursor.execute(ins_reserves, reserves)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (2136, 'customer00', '1111000011110000', 0, 125.0)
    reserves = ('123', 2136, 'first', datetime.date(2016, 5, 20), 'Passenger 20', 1, train_stations['New York City'], train_stations['Atlanta'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
        
    try:
        cursor.execute(ins_reserves, reserves)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (2159, 'customer00', '1111000011110000', 0, 200.0)
    reserves = ('420', 2159, 'first', datetime.date(2016, 5, 5), 'Passenger 5', 1, train_stations['Miami'], train_stations['New York City'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
        
    try:
        cursor.execute(ins_reserves, reserves)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (2237, 'customer00', '1111000011110000', 0, 110.0)
    reserves = ('101', 2237, 'first', datetime.date(2016, 5, 1), 'Passenger 1', 1, train_stations['Richmond'], train_stations['Boston'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
        
    try:
        cursor.execute(ins_reserves, reserves)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (2337, 'customer00', '1111000011110000', 0, 80.0)
    reserves = ('666', 2337, 'first', datetime.date(2016, 5, 14), 'Passenger 14', 1, train_stations['Nashville'], train_stations['Boston'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
        
    try:
        cursor.execute(ins_reserves, reserves)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (2399, 'customer00', '1111000011110000', 0, 100.0)
    reserves = ('707', 2399, 'first', datetime.date(2016, 5, 7), 'Passenger 7', 1, train_stations['Atlanta'], train_stations['Detroit'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
        
    try:
        cursor.execute(ins_reserves, reserves)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (3608, 'customer00', '1111000011110000', 0, 125.0)
    reserves = ('123', 3608, 'first', datetime.date(2016, 5, 4), 'Passenger 4', 1, train_stations['New York City'], train_stations['Atlanta'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
        
    try:
        cursor.execute(ins_reserves, reserves)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (3910, 'customer00', '1111000011110000', 0, 120.0)
    reserves = ('246', 3910, 'first', datetime.date(2016, 5, 18), 'Passenger 18', 1, train_stations['Detroit'], train_stations['Atlanta'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
        
    try:
        cursor.execute(ins_reserves, reserves)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (4429, 'customer00', '1111000011110000', 0, 120.0)
    reserves = ('246', 4429, 'first', datetime.date(2016, 5, 2), 'Passenger 2', 1, train_stations['Detroit'], train_stations['Atlanta'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
        
    try:
        cursor.execute(ins_reserves, reserves)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (4871, 'customer00', '1111000011110000', 0, 110.0)
    reserves = ('101', 4871, 'first', datetime.date(2016, 5, 9), 'Passenger 9', 1, train_stations['Richmond'], train_stations['New York City'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
        
    try:
        cursor.execute(ins_reserves, reserves)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (4971, 'customer00', '1111000011110000', 0, 90.0)
    reserves = ('912', 4971, 'first', datetime.date(2016, 5, 8), 'Passenger 8', 1, train_stations['Atlanta'], train_stations['New York City'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
        
    try:
        cursor.execute(ins_reserves, reserves)
    except mysql.connector.Error as err:
        print(err.msg)


    # 10 - Double Ticket Reservations

    reservation = (45, 'customer01', '2111000011110001', 0, 325.0)
    reserves1 = ('420', 45, 'first', datetime.date(2016, 4, 26), 'Customer 1', 1, train_stations['Miami'], train_stations['New York City'])
    reserves2 = ('123', 45, 'first', datetime.date(2016, 4, 26), 'Customer 1', 1, train_stations['New York City'], train_stations['Atlanta'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
    try:
        cursor.execute(ins_reserves, reserves1)
    except mysql.connector.Error as err:
        print(err.msg)
    try:
        cursor.execute(ins_reserves, reserves2)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (669, 'customer02', '3111000011110001', 0, 325.0)
    reserves1 = ('420', 669, 'first', datetime.date(2016, 4, 26), 'Customer 2', 1, train_stations['Miami'], train_stations['New York City'])
    reserves2 = ('123', 669, 'first', datetime.date(2016, 4, 26), 'Customer 2', 1, train_stations['New York City'], train_stations['Atlanta'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
    try:
        cursor.execute(ins_reserves, reserves1)
    except mysql.connector.Error as err:
        print(err.msg)
    try:
        cursor.execute(ins_reserves, reserves2)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (1085, 'customer03', '4111000011110001', 0, 235.0)
    reserves1 = ('101', 1085, 'first', datetime.date(2016, 4, 26), 'Customer 3', 1, train_stations['Richmond'], train_stations['New York City'])
    reserves2 = ('123', 1085, 'first', datetime.date(2016, 4, 26), 'Customer 3', 1, train_stations['New York City'], train_stations['Atlanta'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
    try:
        cursor.execute(ins_reserves, reserves1)
    except mysql.connector.Error as err:
        print(err.msg)
    try:
        cursor.execute(ins_reserves, reserves2)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (1434, 'customer01', '2111000011110001', 0, 235.0)
    reserves1 = ('101', 1434, 'first', datetime.date(2016, 4, 26), 'Customer 1', 1, train_stations['Richmond'], train_stations['New York City'])
    reserves2 = ('123', 1434, 'first', datetime.date(2016, 4, 26), 'Customer 1', 1, train_stations['New York City'], train_stations['Atlanta'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
    try:
        cursor.execute(ins_reserves, reserves1)
    except mysql.connector.Error as err:
        print(err.msg)
    try:
        cursor.execute(ins_reserves, reserves2)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (1951, 'customer01', '2111000011110001', 0, 220.0)
    reserves1 = ('707', 1951, 'first', datetime.date(2016, 4, 26), 'Customer 1', 1, train_stations['Atlanta'], train_stations['Detroit'])
    reserves2 = ('246', 1951, 'first', datetime.date(2016, 4, 26), 'Customer 1', 1, train_stations['Detroit'], train_stations['Atlanta'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
    try:
        cursor.execute(ins_reserves, reserves1)
    except mysql.connector.Error as err:
        print(err.msg)
    try:
        cursor.execute(ins_reserves, reserves2)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (2202, 'customer02', '3111000011110001', 0, 235.0)
    reserves1 = ('101', 2202, 'first', datetime.date(2016, 4, 26), 'Customer 2', 1, train_stations['Richmond'], train_stations['New York City'])
    reserves2 = ('123', 2202, 'first', datetime.date(2016, 4, 26), 'Customer 2', 1, train_stations['New York City'], train_stations['Atlanta'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
    try:
        cursor.execute(ins_reserves, reserves1)
    except mysql.connector.Error as err:
        print(err.msg)
    try:
        cursor.execute(ins_reserves, reserves2)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (2366, 'customer01', '2111000011110001', 0, 215.0)
    reserves1 = ('912', 2366, 'first', datetime.date(2016, 4, 26), 'Customer 1', 1, train_stations['Atlanta'], train_stations['New York City'])
    reserves2 = ('123', 2366, 'first', datetime.date(2016, 4, 26), 'Customer 1', 1, train_stations['New York City'], train_stations['Atlanta'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
    try:
        cursor.execute(ins_reserves, reserves1)
    except mysql.connector.Error as err:
        print(err.msg)
    try:
        cursor.execute(ins_reserves, reserves2)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (3050, 'customer03', '4111000011110001', 0, 325.0)
    reserves1 = ('420', 3050, 'first', datetime.date(2016, 4, 26), 'Customer 3', 1, train_stations['Miami'], train_stations['New York City'])
    reserves2 = ('123', 3050, 'first', datetime.date(2016, 4, 26), 'Customer 3', 1, train_stations['New York City'], train_stations['Atlanta'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
    try:
        cursor.execute(ins_reserves, reserves1)
    except mysql.connector.Error as err:
        print(err.msg)
    try:
        cursor.execute(ins_reserves, reserves2)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (3092, 'customer03', '4111000011110001', 0, 220.0)
    reserves1 = ('707', 3092, 'first', datetime.date(2016, 4, 26), 'Customer 3', 1, train_stations['Atlanta'], train_stations['Detroit'])
    reserves2 = ('246', 3092, 'first', datetime.date(2016, 4, 26), 'Customer 3', 1, train_stations['Detroit'], train_stations['Atlanta'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
    try:
        cursor.execute(ins_reserves, reserves1)
    except mysql.connector.Error as err:
        print(err.msg)
    try:
        cursor.execute(ins_reserves, reserves2)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (3655, 'customer02', '3111000011110001', 0, 220.0)
    reserves1 = ('707', 3655, 'first', datetime.date(2016, 4, 26), 'Customer 2', 1, train_stations['Atlanta'], train_stations['Detroit'])
    reserves2 = ('246', 3655, 'first', datetime.date(2016, 4, 26), 'Customer 2', 1, train_stations['Detroit'], train_stations['Atlanta'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
    try:
        cursor.execute(ins_reserves, reserves1)
    except mysql.connector.Error as err:
        print(err.msg)
    try:
        cursor.execute(ins_reserves, reserves2)
    except mysql.connector.Error as err:
        print(err.msg)

    # 10 Cancelled Reservations

    reservation = (310, 'customer04', '5111000011110001', 1, 105.0)
    reserves = ('101', 310, 'first', datetime.date(2016, 5, 2), 'Cancel Customer', 1, train_stations['Richmond'], train_stations['New York City'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
        
    try:
        cursor.execute(ins_reserves, reserves)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (920, 'customer04', '5111000011110001', 1, 80.0)
    reserves = ('666', 920, 'first', datetime.date(2016, 5, 1), 'Cancel Customer', 1, train_stations['Nashville'], train_stations['Boston'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
        
    try:
        cursor.execute(ins_reserves, reserves)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (1179, 'customer04', '5111000011110001', 1, 105.0)
    reserves = ('101', 1179, 'first', datetime.date(2016, 5, 1), 'Cancel Customer', 1, train_stations['Richmond'], train_stations['New York City'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
        
    try:
        cursor.execute(ins_reserves, reserves)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (1199, 'customer04', '5111000011110001', 1, 110.0)
    reserves = ('246', 1199, 'first', datetime.date(2016, 5, 2), 'Cancel Customer', 1, train_stations['Detroit'], train_stations['Atlanta'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
        
    try:
        cursor.execute(ins_reserves, reserves)
    except mysql.connector.Error as err:
        print(err.msg)
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
        
    try:
        cursor.execute(ins_reserves, reserves)
    except mysql.connector.Error as err:
        print(err.msg)
    reservation = (1324, 'customer04', '5111000011110001', 1, 150.0)
    reserves = ('420', 1324, 'first', datetime.date(2016, 5, 1), 'Cancel Customer', 1, train_stations['Miami'], train_stations['New York City'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
        
    try:
        cursor.execute(ins_reserves, reserves)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (1572, 'customer04', '5111000011110001', 1, 110.0)
    reserves = ('246', 1572, 'first', datetime.date(2016, 5, 1), 'Cancel Customer', 1, train_stations['Detroit'], train_stations['Atlanta'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
        
    try:
        cursor.execute(ins_reserves, reserves)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (2568, 'customer04', '5111000011110001', 1, 100.0)
    reserves = ('808', 2568, 'first', datetime.date(2016, 5, 1), 'Cancel Customer', 1, train_stations['Miami'], train_stations['Boston'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
        
    try:
        cursor.execute(ins_reserves, reserves)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (2880, 'customer04', '5111000011110001', 1, 100.0)
    reserves = ('707', 2880, 'first', datetime.date(2016, 5, 1), 'Cancel Customer', 1, train_stations['Atlanta'], train_stations['Detroit'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
        
    try:
        cursor.execute(ins_reserves, reserves)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (4614, 'customer04', '5111000011110001', 1, 90.0)
    reserves = ('912', 4614, 'first', datetime.date(2016, 5, 1), 'Cancel Customer', 1, train_stations['Atlanta'], train_stations['New York City'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
        
    try:
        cursor.execute(ins_reserves, reserves)
    except mysql.connector.Error as err:
        print(err.msg)

    reservation = (4634, 'customer04', '5111000011110001', 1, 112.5)
    reserves = ('123', 4634, 'first', datetime.date(2016, 5, 1), 'Cancel Customer', 1, train_stations['New York City'], train_stations['Atlanta'])
    try:
        cursor.execute(ins_reservation, reservation)
    except mysql.connector.Error as err:
        print(err.msg)
        
    try:
        cursor.execute(ins_reserves, reserves)
    except mysql.connector.Error as err:
        print(err.msg)


cnx = mysql.connector.connect(user='root', password='',
    host='localhost', database='gt_train')
cursor = cnx.cursor()
 
# 1. Create Database
create_database(cursor)
 
# 2. Create Tables
for name, ddl in TABLES.iteritems():
    try:
        print("Creating table {}: ".format(name), end='')
        cursor.execute(ddl)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")
 
# 3. Populate Database
populate_database(cursor)
cnx.commit()
 
cursor.close()
cnx.close()