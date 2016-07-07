import Tkinter as tk
import tkMessageBox as tkmb
import tkFont
import datetime
import random
import base64
from urllib2 import urlopen
import mysql.connector
from mysql.connector import errorcode

# GT Train Application for CS4400
#
# Group 1:
# Kevin Rose
# Kishan Chudasama
# Emily Rothenbacher
# Hudson Bilbrey

class App(tk.Tk):
    """
    Main App Controller
    """
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(size=14, family='Arial')
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self, bg='aliceblue')
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.cnx = mysql.connector.connect(user='root', password='',
            host='localhost', database='gt_train')
        self.cursor = self.cnx.cursor()
        self.current_user = None

        self.station_dict = {}
        self.station_dict["ATL Midtown Station"] ='Atlanta'
        self.station_dict["Red Sox Trains"] = 'Boston'
        self.station_dict["Music City Train Station"] = 'Nashville'
        self.station_dict["NYC Terminal"] = 'New York City'
        self.station_dict["Detroit Trains"] = 'Detroit'
        self.station_dict["South Beach Station"] = 'Miami'
        self.station_dict["Virginia Train Stop"] = 'Richmond'

        self.reservationInfo = ('1', '1', '9999', "ATL Midtown Station", "NYC Terminal")

        self.frames = {}
        "**ADD NEW FRAMES HERE**"
        for F in (HomePage, SignIn, CreateUser, ChooseFunctionality_Customer, ChooseFunctionality_Manager ,StudentDiscount, TrainSchedule,
            MakeReservation, UpdateReservation, CancelReservation, GiveReview, ViewReview, RevenueReport, PopularRouteReport):
            page_name = F.__name__
            frame = F(container, self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("HomePage")

    def show_frame(self, page_name):
            '''Show a frame for the given page name'''
            frame = self.frames[page_name]
            frame.tkraise()

    def make_entry(self, caption, width=None, **options):
        tk.Label(self, text=caption).pack()
        entry = tk.Entry(self, **options)
        if width:
            entry.config(width=width)
        return entry


class HomePage(tk.Frame):
    """
    Home Page
    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='aliceblue')
        self.controller = controller

        #logo --> pls note 2 new import statements
        try:
            self.url = 'http://i.imgur.com/qN8Av7t.gif'
            self.uopen = urlopen(self.url).read()
            self.image_b64 = base64.encodestring(self.uopen)
            self.photo = tk.PhotoImage(data=self.image_b64)
            self.logo = tk.Label(self, image=self.photo)
            self.logo.pack(pady=20)
        except:
            print "GT Wifi isnt working"

        # self.welcome = tk.Label(self, text= "GT Train", font=("arial",15))
        # self.welcome.pack(pady=50)
        self.sign_in = tk.Button(self, text = 'Sign In', command=lambda: controller.show_frame("SignIn"))
        self.sign_in.pack(pady=10)
        self.create_new_user = tk.Button(self, text = 'Create New User', command=lambda: controller.show_frame("CreateUser"))
        self.create_new_user.pack(pady=10)
        # # DEBUG
        self.debug = tk.Label(self, text="DEBUG:")
        self.debug.pack(pady=10)
        self.quick_login = tk.Button(self, text="Quick Login", command=lambda: self.quickLogin())
        self.quick_login.pack()
        self.print_db_button = tk.Button(self, text='Print Database', command=self.print_db)
        self.print_db_button.pack()

    # DEBUG
    def print_db(self):
        print "USER:"
        get_users = ("SELECT * from user")
        self.controller.cursor.execute(get_users)
        for (uname, pword) in self.controller.cursor:
            print "| U: ", uname, " | P: ", pword, " | "

        print "\nUSER_CUSTOMER:"
        get_users = ("SELECT * from user_customer")
        self.controller.cursor.execute(get_users)
        for (uname, email, isStudent) in self.controller.cursor:
            print "| U: ", uname, " | E: ", email, " | S: ", isStudent, " | "

    def quickLogin(self):
        self.controller.current_user = "customer00"
        print "Logged in as", self.controller.current_user
        self.controller.show_frame("ChooseFunctionality_Customer")



class SignIn(tk.Frame):
    """
    Sign In
    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='aliceblue')
        self.controller = controller
        self.createWidgets()

    def createWidgets(self):
        self.login_text = tk.Label(self, text="~~ Log In ~~", font=("arial",15))
        self.login_text.pack(pady=30)
        self.user_entry = self.make_entry("Username: ", 40)
        self.user_entry.pack(pady=5)
        self.password_entry = self.make_entry("Password:", 40, show='*')
        self.password_entry.pack(pady=5)
        self.SIGNIN = tk.Button(self, text='Log In', command=self.log_in)
        self.BACK = tk.Button(self, text='Back', command=lambda: self.controller.show_frame("HomePage"))   
        self.BACK.pack(side = "bottom", pady = 10)
        self.SIGNIN.pack(side = "bottom", pady = 10)

    def make_entry(self, caption, width=None, **options):
        tk.Label(self, text=caption).pack()
        entry = tk.Entry(self, **options)
        if width:
            entry.config(width=width)
        return entry

    def log_in(self):
        user = self.user_entry.get()
        password = self.password_entry.get()
        get_users = ("SELECT * from user WHERE username = %s")
        self.controller.cursor.execute(get_users, (user,))
        uname = self.controller.cursor.fetchone()
        if uname == None:
            tkmb.showerror("Error", "Username not in database.")
        else:
            uname = list(uname)
            if uname[1] != password:
                tkmb.showerror("Error", "Password is incorrect.")
            else:
                self.controller.cnx = mysql.connector.connect(user=user, password=password,
                    host='localhost', database='gt_train')
                self.controller.cursor = self.controller.cnx.cursor()
                self.controller.current_user = user
                print "Logged in as ", self.controller.current_user
                check_if_manager = ("SELECT * FROM user_manager WHERE username=%s")
                self.controller.cursor.execute(check_if_manager, (user, ))
                managername = self.controller.cursor.fetchone()
                if managername==None:
                    self.controller.show_frame("ChooseFunctionality_Customer")
                else:
                    self.controller.show_frame("ChooseFunctionality_Manager")
 
class CreateUser(tk.Frame):
    """
    Create User
    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='aliceblue')
        self.controller = controller
        self.createWidgets()

    def make_entry(self, caption, width=None, **options):
        tk.Label(self, text=caption).pack()
        entry = tk.Entry(self, **options)
        if width:
            entry.config(width=width)
        return entry

    def createWidgets(self):
        self.login_text = tk.Label(self, text="~~ Create Account ~~", font=("arial",15))
        self.login_text.pack(pady=10)
        entries = []
        self.user_entry = self.make_entry("Username: ", 40)
        self.user_entry.pack(pady=5)
        self.user_label = tk.Label(self, text="Can only contain letters, numbers, and underscores")
        self.user_label.pack()        
        self.email_entry = self.make_entry("Email:", 40)
        self.email_entry.pack(pady=5)        
        self.password_entry = self.make_entry("Password:", 40, show='*')
        self.password_entry.pack(pady=5)
        self.user_label = tk.Label(self, text="Must be at least 5 characters and contain at least 1 number")
        self.user_label.pack()        
        self.confirm_password_entry = self.make_entry("Confirm Password:", 40, show='*')
        self.confirm_password_entry.pack(pady=5)
        self.CREATE = tk.Button(self)
        self.CREATE["text"] = "Create",
        self.CREATE["command"] = self.create_user
        self.BACK = tk.Button(self, text='Back', command=lambda: self.controller.show_frame("HomePage"))
        self.BACK.pack(side = "bottom", pady = 10)
        self.CREATE.pack(side = "bottom", pady = 10)

    def create_user(self):
        username = self.user_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        password2 = self.confirm_password_entry.get()
        isStudent = False 
        uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        lowercase = "abcdefghijklmnopqrstuvwxyz"
        numbers = "0123456789"
        underscore = "_"
        # Check if username is valid
        user_isValid = True
        for letter in username:
            if letter not in uppercase and letter not in lowercase \
                and letter not in numbers and letter != '_':
                user_isValid = False
        if not user_isValid:
            tkmb.showerror("Error", "Invalid Username")
        # Check if email is valid
        email_isValid = True
        ampCount = 0
        dotCount = 0
        for letter in email:
            if letter=='@':
                ampCount += 1
            if letter=='.':
                dotCount += 1
        if ampCount != 1 and dotCount >= 1:
            email_isValid = False
            tkmb.showerror("Error", "Invalid Email")
        # Check if password is valid
        pword_isValid = True
        numCount = 0
        for letter in password:
            if letter not in uppercase and letter not in lowercase \
                and letter not in numbers and letter != '_':
                pword_isValid = False
            if letter in numbers:
                numCount += 1
        if len(password) < 5 or numCount == 0:
            pword_isValid = False
        if not pword_isValid:
            tkmb.showerror("Error", "Invalid Password")
        # Query database for users
        check_user = ("SELECT * FROM user")
        self.controller.cursor.execute(check_user);
        # Check if user exists
        userExists = False
        for (uname, pword) in self.controller.cursor:
            if uname==username:
                userExists=True
                tkmb.showerror("Error", "User Already Exists")
        # Add user if it doesn't exist in db
        if user_isValid and email_isValid and pword_isValid and not userExists:
            if password==password2:
                new_user = ("CREATE USER %s@'localhost'"
                            "IDENTIFIED BY %s")
                user_data = (username, password)
                self.controller.cursor.execute(new_user, user_data)
                
                grant_permissions = ("GRANT ALL ON gt_train.* TO %s@'localhost'")
                try:
                    self.controller.cursor.execute(grant_permissions, (username,))
                except mysql.connector.Error as err:
                    print(err.msg)

                add_user = ("INSERT INTO user "
                       "(username, password) "
                       "VALUES (%s, %s)")
                
                self.controller.cursor.execute(add_user, user_data)
                self.controller.cnx.commit()

                add_customer = ("INSERT INTO user_customer "
                       "(username, email, is_student) "
                       "VALUES (%s, %s, %s)")
                customer_data = (username, email, False)
                self.controller.cursor.execute(add_customer, customer_data)
                self.controller.cnx.commit()

                tkmb.showinfo("Success!", "User Created")
            else:
                tkmb.showerror("Error", "Passwords do not match.")


class ChooseFunctionality_Customer(tk.Frame):
    """
    Main Functionality Menu
    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='aliceblue')
        self.controller = controller
        self.createWidgets()

    def createWidgets(self):
        buttons = []
        self.trainSchedule = tk.Button(self, text="View Train Schedule", command=lambda:
            self.controller.show_frame("TrainSchedule"))
        buttons.append(self.trainSchedule)
        self.newReservation = tk.Button(self, text="Make a new Reservation", command=lambda:
            self.controller.show_frame("MakeReservation"))
        buttons.append(self.newReservation)
        self.updateReservation = tk.Button(self, text="Update Reservation", command=lambda:
            self.controller.show_frame("UpdateReservation"))
        buttons.append(self.updateReservation)
        self.cancelReservation = tk.Button(self, text="Cancel Reservation", command=lambda:
            self.controller.show_frame("CancelReservation"))
        buttons.append(self.cancelReservation)
        self.reviewButton = tk.Button(self, text="View Reviews", command=lambda:
            self.controller.show_frame("ViewReview"))
        buttons.append(self.reviewButton)
        self.viewReview = tk.Button(self, text="Give a Review", command=lambda:
            self.controller.show_frame("GiveReview"))
        buttons.append(self.viewReview)
        self.studentInfo = tk.Button(self, text="Student Discount Information", command=lambda:
            self.controller.show_frame("StudentDiscount"))
        buttons.append(self.studentInfo)
        self.paymentInfo = tk.Button(self, text="Payment Information", command=lambda:
            self.controller.show_frame("PaymentDiscount"))
        for i in range (0, len(buttons)):
            buttons[i].config(width=25)
            buttons[i].pack(pady=10) 
        self.LOGOUT = tk.Button(self, text='Log Out', command=lambda:
            self.controller.show_frame("HomePage"))
        self.LOGOUT.pack(side = "bottom", pady = 10)


class TrainSchedule(tk.Frame):
    """
    Select Train & Train Schedule
    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='aliceblue')
        self.controller = controller
        self.createWidgets()
    def createWidgets(self):

        self.widgets = []
        self.welcome = tk.Label(self, text= "Select Train Number")
        self.welcome.pack(pady=50)
        # Get Train Numbers
        get_numbers = ("SELECT * FROM trainroute")
        self.controller.cursor.execute(get_numbers)
        options = []
        self.optionVar = tk.StringVar(self)
        self.optionVar.set("Train Number")
        for (tnum, c1, c2) in self.controller.cursor:
            options.append(str(tnum))
        self.select_train = apply(tk.OptionMenu, (self, self.optionVar) + tuple(options))
        self.select_train.pack()
        self.BACK = tk.Button(self, text='Back', command=lambda:
            self.controller.show_frame("ChooseFunctionality_Customer"))
        self.BACK.pack(side = "bottom", pady = 10)
        self.go = tk.Button(self, text='Go', command=lambda:
            self.selectTrain())
        self.go.pack(side = "bottom", pady = 10)
        self.widgets.append(self.welcome)
        self.widgets.append(self.select_train)
        self.widgets.append(self.go)
        self.widgets.append(self.BACK)


    def createNewWidgets(self, selector):
        self.widgets = []

        self.welcome = tk.Label(self, text= "Train Schedule")
        self.welcome.grid(row=0, column=1, pady=20)
        trainlabel = "#" + selector
        self.train_number = tk.Label(self, text=trainlabel)
        self.train_number.grid(row=0, column=2, pady=20)

        self.station_label = tk.Label(self, text="Station")
        self.station_label.grid(row=1, column=0, pady=10)
        self.location_label = tk.Label(self, text="Location")
        self.location_label.grid(row=1, column=1, pady=10)
        self.arr_label = tk.Label(self, text="Arrival Time")
        self.arr_label.grid(row=1, column=2, pady=10)
        self.dep_label = tk.Label(self, text="Departure Time")
        self.dep_label.grid(row=1, column=3, pady=10)
        self.widgets.append(self.welcome)
        self.widgets.append(self.train_number)
        self.widgets.append(self.station_label)
        self.widgets.append(self.location_label)
        self.widgets.append(self.arr_label)
        self.widgets.append(self.dep_label)

        rowcount = 2
        tempcursor = self.controller.cursor
        for (num, station, arrival, departure) in tempcursor:
            self.new_station_label = tk.Label(self, text=station)
            self.new_station_label.grid(row=rowcount, column=0, pady=10)
            self.new_location_label = tk.Label(self, text=self.controller.station_dict[station])
            self.new_location_label.grid(row=rowcount, column=1, pady=10)
            self.new_arr_label = tk.Label(self, text=arrival)
            self.new_arr_label.grid(row=rowcount, column=2, pady=10)
            self.new_dep_label = tk.Label(self, text=departure)
            self.new_dep_label.grid(row=rowcount, column=3, pady=10)
            self.widgets.append(self.new_station_label)
            self.widgets.append(self.new_location_label)
            self.widgets.append(self.new_arr_label)
            self.widgets.append(self.new_dep_label)
            rowcount+=1

        self.BACK = tk.Button(self, text='Back', command=lambda: self.goBack())
        self.BACK.grid(row=rowcount, pady = 20)
        self.widgets.append(self.BACK)

    def selectTrain(self):
        get_stops = ("SELECT * FROM stop "
                    "WHERE trainnumber=%s "
                    "ORDER BY arrival_time ASC")
        selector = self.optionVar.get()
        self.controller.cursor.execute(get_stops, (str(selector),))

        # Delete old widgets
        for w in self.widgets:
            w.pack_forget()

        # Create new widgets
        self.createNewWidgets(selector)
    def goBack(self):
        for w in self.widgets:
            w.grid_forget()
        self.createWidgets()

class MakeReservation(tk.Frame):
    """
    Make Reservation
    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='aliceblue')
        self.controller = controller
        self.ticketArray = []
        self.removedTickets = []
        self.createWidgets()

    def createWidgets(self):
        # Had to do pack here instead of grid on this screen b/c of Date widget
        self.widgets=[]
        rowcount=0
        self.welcome = tk.Label(self, text= "Make Reservation")
        self.welcome.grid(row=rowcount, column=1, pady=30)
        rowcount+=1

        options = []
        for key in self.controller.station_dict:
            options.append(self.controller.station_dict[key])
        self.departsVar = tk.StringVar(self)
        self.departsVar.set("Departs From")
        self.arrivesVar = tk.StringVar(self)
        self.arrivesVar.set("Arrives At")
        self.select_departsFrom = apply(tk.OptionMenu, (self, self.departsVar) + tuple(options))
        self.select_departsFrom.grid(row=rowcount, column=1)
        rowcount+=1
        self.select_arrivesAt = apply(tk.OptionMenu, (self, self.arrivesVar) + tuple(options))
        self.select_arrivesAt.grid(row=rowcount, column=1)
        rowcount+=1


        self.date_entry = tk.Frame(self)
        self.date_label = tk.Label(self.date_entry, text='Date: ')
        self.date_entry_1 = tk.Entry(self.date_entry, width=2)
        self.label_1 = tk.Label(self.date_entry, text='/')
        self.date_entry_2 = tk.Entry(self.date_entry, width=2)
        self.label_2 = tk.Label(self.date_entry, text='/')
        self.date_entry_3 = tk.Entry(self.date_entry, width=4)

        self.date_label.pack(side=tk.LEFT)
        self.date_entry_1.pack(side=tk.LEFT)
        self.label_1.pack(side=tk.LEFT)
        self.date_entry_2.pack(side=tk.LEFT)
        self.label_2.pack(side=tk.LEFT)
        self.date_entry_3.pack(side=tk.LEFT)
        self.date_entry.grid(row=rowcount, column=1)
        rowcount+=1
        self.GO = tk.Button(self, text='Find Trains', command=lambda:
            self.verifyEntries())
        self.GO.grid(row=rowcount, column=2, pady=30, padx=50)
        self.BACK = tk.Button(self, text='Back', command=lambda:
            self.controller.show_frame("ChooseFunctionality_Customer"))
        self.BACK.grid(row=rowcount, column=0, pady=30, padx=50)

        self.widgets.append(self.welcome)
        self.widgets.append(self.select_departsFrom)
        self.widgets.append(self.select_arrivesAt)
        self.widgets.append(self.date_entry)
        self.widgets.append(self.GO)
        self.widgets.append(self.BACK)

    def verifyEntries(self):
        verified = True

        # Check Departure & arrival fields
        departFrom = self.departsVar.get()
        arriveAt = self.arrivesVar.get()
        for key in self.controller.station_dict:
            stn = self.controller.station_dict[key]
            if stn==departFrom:
                departFrom = key
            if stn==arriveAt:
                arriveAt = key
        if departFrom not in self.controller.station_dict:
            verified = False
            tkmb.showerror("Error", "Please enter a departure location.")
        elif arriveAt not in self.controller.station_dict:
            verified = False
            tkmb.showerror("Error", "Please enter an arrival location.")
        elif arriveAt==departFrom:
            verified = False
            tkmb.showerror("Error", "You shouldn't need a train for that.")


        # Make sure date entries are valid numbers
        mm = self.date_entry_1.get()
        dd = self.date_entry_2.get()
        yyyy = self.date_entry_3.get()
        current_date = datetime.datetime.now()
        curr_yr = current_date.year
        curr_day = current_date.day
        curr_mo = current_date.month
        numbers = "0123456789"
        if len(mm)==0 or len(dd)==0 or len(yyyy)!=4:
            verified=False
        for c in mm:
            if c not in numbers:
                verified = False
        for c in dd:
            if c not in numbers:
                verified = False
        for c in yyyy:
            if c not in numbers:
                verified = False
        if not verified:
            tkmb.showerror("Error", "You must enter a valid date.")

        # Make sure date isn't in the past

        # COMMENT THIS OUT TO ADD RESERVATIONS IN THE PAST

        inthepast = "Time machines are, unfortunately, not yet a thing. "\
        "Please select a date that hasn't happened yet."

        if int(mm) < 1 or int(mm) > 12:
            verified = False
            tkmb.showerror("Error", "That month doesn't exist.")
        if int(dd) < 1 or int(dd) > 28:
            verified = False
            tkmb.showerror("Error", "GT Train only operates on the 1st-28th of each month.")

        if int(yyyy) < int(curr_yr):
            verified = False
            tkmb.showerror("Error", inthepast)
        if int(yyyy) == int(curr_yr) and int(mm) < int(curr_mo):
            verified = False
            tkmb.showerror("Error", inthepast)
        if int(yyyy) == int(curr_yr) and int(mm) == int(curr_mo) and int(dd) < int(curr_day):
            verified = False
            tkmb.showerror("Error", inthepast)
        elif int(yyyy) == int(curr_yr) and int(mm) == int(curr_mo) and int(dd) == int(curr_day):
            verified = False
            tkmb.showerror("Sorry", "You cannot purchase tickets the day of the trip.")

        # END COMMENT

        if verified:
            # self.controller.reservationInfo = (mm, dd, yyyy, departFrom, arriveAt)
            # self.controller.show_frame("MakeReservation2")
            self.findTrains(mm, dd, yyyy, departFrom, arriveAt)

    def forgetReservationScreen(self):
        self.welcome.pack_forget()
        self.select_departsFrom.pack_forget()
        self.select_arrivesAt.pack_forget()
        self.date_label.pack_forget()
        self.label_1.pack_forget()
        self.label_2.pack_forget()
        self.date_entry.pack_forget()
        self.GO.pack_forget()
        self.BACK.pack_forget()

    def findTrains(self, month, day, year, departFrom, arriveAt):
        # Forget old widgets
        for w in self.widgets:
            w.grid_forget()

        self.widgets = []
        rowcount=0
        # Get train numbers and their ticket prices
        train_info = {}
        get_route_info = ("SELECT * FROM trainroute ")
        self.controller.cursor.execute(get_route_info)
        for (num, class1, class2) in self.controller.cursor:
            train_info[num] = (class1, class2)

        # Stores tuples (trainnumber, departure_time, arrival_time)
       
        valid_routes = []

        for key in train_info:
            get_stops = ("SELECT * FROM stop "
                        "WHERE trainnumber=%s "
                        "ORDER BY arrival_time ASC")
            self.controller.cursor.execute(get_stops, (str(key),))
            # Used to make sure departure is before arrival
            inOrder = False
            d_time = None
            a_time = None
            for (n, s, a, d) in self.controller.cursor:
                if s==departFrom:
                    d_time = d
                    inOrder = True
                if s==arriveAt and inOrder:
                    a_time = a
                    valid_routes.append((key, str(d_time), str(a_time)))
        if len(valid_routes) > 0:
            rowcount=0
            self.welcome = tk.Label(self, text= "Select Departure")
            self.welcome.grid(row=rowcount, column=1, pady=5)
            rowcount+=1
            route_string = self.controller.station_dict[departFrom] + " to " + \
                self.controller.station_dict[arriveAt]
            self.route_label = tk.Label(self, text=route_string)
            self.route_label.grid(row=rowcount, column=1, pady=5)
            months = {'1':'Jan', '2':'Feb', '3':'Mar', '4':'Apr',
                    '5':'May', '6':'Jun', '7':'Jul', '8':'Aug', 
                    '9':'Sept', '10':'Oct', '11':'Nov', '12':'Dec'}
            date_string = months[month] + ' ' + day + ", " + year
            self.date_label = tk.Label(self, text=date_string)
            self.date_label.grid(row=rowcount, column=2, pady=5)
            rowcount+=1
            self.tnum_label = tk.Label(self, text="Train Number")
            self.tnum_label.grid(row=rowcount, column=0, pady=10)
            self.time_label = tk.Label(self, text="Time (Duration)")
            self.time_label.grid(row=rowcount, column=1, pady=10)
            self.class1_label = tk.Label(self, text="1st Class Price")
            self.class1_label.grid(row=rowcount, column=2, pady=10)
            self.class2_label = tk.Label(self, text="2nd Class Price")
            self.class2_label.grid(row=rowcount, column=3, pady=10)
            rowcount+=1

            self.widgets.append(self.welcome)
            self.widgets.append(self.route_label)
            self.widgets.append(self.date_label)
            self.widgets.append(self.tnum_label)
            self.widgets.append(self.time_label)
            self.widgets.append(self.class1_label)
            self.widgets.append(self.class2_label)

            self.radiobuttons = []
            self.cols = []
            self.subFrames = []
            self.ticket_dictionary={}
            tid=0
            self.ticketID = tk.IntVar()
            for (tnum, dtime, atime) in valid_routes:
                col0 = tk.Label(self, text=str(tnum))
                # Calculate Duration
                # Use regex to isolate hours & minutes
                dminute = int(dtime[:-3][-2:])
                aminute = int(atime[:-3][-2:])
                dhour = int(dtime[:-6])
                ahour = int(atime[:-6])
                duration_minutes = (ahour*60+aminute)-(dhour*60+dminute)
                duration_string = str(int(duration_minutes/60)) + " hr " + \
                    str(duration_minutes%60) + " min"
                time_string = dtime[:-3] + "-" + atime[:-3] + \
                    "(" + duration_string + ")"
                col1 = tk.Label(self, text=time_string)
                fc_price = train_info[tnum][0]
                sc_price = train_info[tnum][1]
                fc_price_string = "$" + str(fc_price)
                sc_price_string = "$" + str(sc_price)
                
                col0.grid(row=rowcount, column=0, pady=10)
                col1.grid(row=rowcount, column=1, pady=10)

                f_price1 = tk.Frame(self)
                f_price2 = tk.Frame(self)

                p1selector = tk.Radiobutton(f_price1, variable=self.ticketID, value=tid)
                self.ticket_dictionary[tid]=(tnum, fc_price, "first", departFrom, arriveAt, \
                    time_string, datetime.date(int(year), int(month), int(day)))
                tid+=1
                p2selector = tk.Radiobutton(f_price2, variable=self.ticketID, value=tid)
                self.ticket_dictionary[tid]=(tnum, sc_price, "second", departFrom, arriveAt, \
                    time_string, datetime.date(int(year), int(month), int(day)))
                tid+=1
                col2 = tk.Label(f_price1, text=fc_price_string)
                col3 = tk.Label(f_price2, text=sc_price_string)
                p1selector.pack(side=tk.LEFT)
                p2selector.pack(side=tk.LEFT)
                col2.pack(side=tk.RIGHT)
                col3.pack(side=tk.RIGHT)
                f_price1.grid(row=rowcount, column=2, pady=10)
                f_price2.grid(row=rowcount, column=3, pady=10)
                self.radiobuttons.append(p1selector)
                self.radiobuttons.append(p2selector)
                self.cols.append((col0, col1, col2, col3))
                self.subFrames.append(f_price1)
                self.subFrames.append(f_price2)
                rowcount+=1
                self.widgets.append(col0)
                self.widgets.append(col1)
                self.widgets.append(f_price1)
                self.widgets.append(f_price2)
            self.GO = tk.Button(self, text="Next", command=lambda:self.passengerInfo())
            self.GO.grid(row=rowcount, column=2)
            self.BACK = tk.Button(self, text="Back", command=lambda:self.goBack())
            self.BACK.grid(row=rowcount, column=1)
            self.widgets.append(self.GO)
            self.widgets.append(self.BACK)
        else:
            tkmb.showerror("Sorry", "There is no direct route to your destination")
            self.createWidgets()
    def goBack(self):
        # Forget findTrains screen
        for w in self.widgets:
            w.grid_forget()
        self.createWidgets()
    def passengerInfo(self):
        # Forget findTrains screen
        for w in self.widgets:
            w.grid_forget()
        self.widgets = []
        # Draw Passenger info screen
        rowcount=0    
        self.passenger_label = tk.Label(self, text="Travel Extras & Passenger Info")
        self.passenger_label.grid(row=rowcount, column=0, pady=10)
        rowcount+=1
        self.baggage_label = tk.Label(self, text="Number of Baggage")
        self.baggage_label.grid(row=rowcount, column=0, pady=10)
        self.baggageVar = tk.IntVar(self)
        self.baggageVar.set(1)
        self.num_baggage = apply(tk.OptionMenu, (self, self.baggageVar) + tuple([1, 2, 3, 4]))
        self.num_baggage.grid(row=rowcount, column=1, pady=10)
        rowcount+=1
        self.name_label = tk.Label(self, text="Passenger Name")
        self.name_label.grid(row=rowcount, column=0, pady=10)
        self.name_entry = tk.Entry(self, width=20)
        self.name_entry.grid(row=rowcount, column=1, pady=10)
        rowcount+=1
        self.GO = tk.Button(self, text="Next", command=lambda:self.addTicket())
        self.GO.grid(row=rowcount, column=1, pady=10)
        self.BACK = tk.Button(self, text="Back", command=lambda:self.goBack())
        self.BACK.grid(row=rowcount, column=0, pady=10)

        self.widgets.append(self.passenger_label)
        self.widgets.append(self.baggage_label)
        self.widgets.append(self.num_baggage)
        self.widgets.append(self.name_label)
        self.widgets.append(self.name_entry)
        self.widgets.append(self.GO)
        self.widgets.append(self.BACK)
    def forgetPassengerInfo(self):
        self.passenger_label.grid_forget()
        self.baggage_label.grid_forget()
        self.num_baggage.grid_forget()
        self.name_label.grid_forget()
        self.name_entry.grid_forget()
        self.GO.grid_forget()
        self.BACK.grid_forget()
    def addTicket(self):
        name = self.name_entry.get()
        self.packWidgets = []
        if len(name)==0:
            tkmb.showerror("Error", "You have to enter a name")
        else:
            for w in self.widgets:
                w.grid_forget()
            self.widgets=[]
            # Get info for current ticket
            train_number, t_price, t_class, t_depart, t_arrive, t_time, t_date = self.ticket_dictionary[self.ticketID.get()]
            p_name, p_bags = (self.name_entry.get(), self.baggageVar.get())
            newTicket = (train_number, t_date, t_time, t_depart, t_arrive, t_class, t_price, p_bags, p_name)
            if newTicket not in self.ticketArray and newTicket not in self.removedTickets:
                self.ticketArray.append(newTicket)
            # Draw stuff
            rowcount=0    
            self.selected_label = tk.Label(self, text="Currently Selected:")
            self.selected_label.grid(row=rowcount, column=0, pady=10)
            rowcount+=1
            self.train_label = tk.Label(self, text="Train")
            self.train_label.grid(row=rowcount, column=0, pady=5)
            self.time_label = tk.Label(self, text="Time")
            self.time_label.grid(row=rowcount, column=1, pady=5)
            self.route_label = tk.Label(self, text="Route")
            self.route_label.grid(row=rowcount, column=2, pady=5)
            self.class_label = tk.Label(self, text="Class")
            self.class_label.grid(row=rowcount, column=3, pady=5)
            self.price_label = tk.Label(self, text="Price")
            self.price_label.grid(row=rowcount, column=4, pady=5)
            self.bag_label = tk.Label(self, text="# Bags")
            self.bag_label.grid(row=rowcount, column=5, pady=5)
            self.name_label = tk.Label(self, text="Passenger Name")
            self.name_label.grid(row=rowcount, column=6, pady=5)
            # Add widgets to an array to make forgetting easier
            self.widgets = []
            self.widgets.append(self.selected_label)
            self.widgets.append(self.train_label)
            self.widgets.append(self.time_label)
            self.widgets.append(self.route_label)
            self.widgets.append(self.class_label)
            self.widgets.append(self.price_label)
            self.widgets.append(self.bag_label)
            self.widgets.append(self.name_label)
            rowcount+=1
            self.ticket_rowcount = rowcount
            self.totalPrice=0
            for tick in self.ticketArray:
                ticketWidgets = []
                t_n, t_d, t_t, t_dep, t_arr , t_c, t_p, p_b, p_n = tick
                train_label = tk.Label(self, text=t_n)
                train_label.grid(row=self.ticket_rowcount, column=0, pady=5, padx=5)
                time_label = tk.Label(self, text=str(t_d)+"\n"+str(t_t))
                time_label.grid(row=self.ticket_rowcount, column=1, pady=5, padx=5)
                route_label = tk.Label(self, text=t_dep +" - "+t_arr)
                route_label.grid(row=self.ticket_rowcount, column=2, pady=5, padx=5)
                class_label = tk.Label(self, text=t_c)
                class_label.grid(row=self.ticket_rowcount, column=3, pady=5, padx=5)
                price_label = tk.Label(self, text=t_p)
                price_label.grid(row=self.ticket_rowcount, column=4, pady=5, padx=5)
                bag_label = tk.Label(self, text=p_b)
                bag_label.grid(row=self.ticket_rowcount, column=5, pady=5, padx=5)
                name_label = tk.Label(self, text=p_n)
                name_label.grid(row=self.ticket_rowcount, column=6, pady=5, padx=5)
                ticketWidgets.append(train_label)
                ticketWidgets.append(time_label)
                ticketWidgets.append(route_label)
                ticketWidgets.append(class_label)
                ticketWidgets.append(price_label)
                ticketWidgets.append(bag_label)
                ticketWidgets.append(name_label)
                remove_button = tk.Button(self, text="Remove", command=lambda: self.removeTicket(tick, ticketWidgets))
                remove_button.grid(row=rowcount, column=7, pady=5, padx=10)
                self.ticket_rowcount+=1
                rowcount+=1
                self.totalPrice+=t_p
                if p_b==3:
                    self.totalPrice+=30
                elif p_b==4:
                    self.totalPrice+=60
                self.widgets.append(train_label)
                self.widgets.append(time_label)
                self.widgets.append(route_label)
                self.widgets.append(class_label)
                self.widgets.append(price_label)
                self.widgets.append(bag_label)
                self.widgets.append(name_label)
                self.widgets.append(remove_button)
            self.cost_label = tk.Label(self, text='Total Cost:')
            self.cost_label.grid(row=rowcount, column=0, pady=10)
            self.cost = tk.Label(self, text='$'+str(self.totalPrice))
            self.cost.grid(row=rowcount, column=1, pady=10)
            rowcount+=1
            self.card_label = tk.Label(self, text='Use Card:')
            self.card_label.grid(row=rowcount, column=0, pady=10)
            get_cards = ("SELECT * FROM payment_info "
                        "WHERE username=%s")
            usr = str(self.controller.current_user)
            self.controller.cursor.execute(get_cards, (usr,))
            options = []
            self.optionVar = tk.StringVar(self)
            self.optionVar.set("Card: ")
            for (cnum, cvv, exp, n, uname) in self.controller.cursor:
                # cnum_string = str(cnum)[-7:]
                # cnum_string = cnum_string[:4]
                options.append(cnum)
            if len(options)>0:
                self.payment_option = apply(tk.OptionMenu, (self, self.optionVar) + tuple(options))
                self.payment_option.grid(row=rowcount, column=1)
                self.widgets.append(self.payment_option)
            self.add_card = tk.Button(self, text='Add/Delete Card', command=lambda: self.addPaymentInfo())
            self.add_card.grid(row=rowcount, column=2, pady=10)
            rowcount+=1
            self.another_train = tk.Button(self, text="Add Another Train", command=lambda:self.addAnotherTrain())
            self.another_train.grid(row=rowcount, column=0, pady=10)
            rowcount+=1
            self.GO = tk.Button(self, text="Next", command=lambda:self.confirmPurchase())
            self.GO.grid(row=rowcount, column=6, pady=10)      
            self.BACK = tk.Button(self, text="Back", command=lambda:self.goBack())
            self.BACK.grid(row=rowcount, column=1, pady=10)
            self.widgets.append(self.cost_label)
            self.widgets.append(self.cost)
            self.widgets.append(self.card_label)
            self.widgets.append(self.add_card)
            self.widgets.append(self.another_train)
            
            self.widgets.append(self.GO)
            self.widgets.append(self.BACK)
    def removeTicket(self, ticket, ticketWidgets):
        newTickets=[]
        print "stop1"
        for t in self.ticketArray:
            if t!=ticket:
                newTickets.append(t)
            else:
                self.removedTickets.append(t)        
        t_n, t_d, t_t, t_dep, t_arr , t_c, t_p, p_b, p_n = ticket
        self.ticket_rowcount-=1
        self.totalPrice-=t_p
        self.ticketArray=newTickets
        print "stop 2"
        for tw in ticketWidgets:
            tw.grid_forget()
        print "stop 3"
        self.goBackToCheckout()
    def addAnotherTrain(self):
        for w in self.widgets:
            w.grid_forget()
        self.createWidgets()
    def confirmPurchase(self):
        cardnum = self.optionVar.get()
        if cardnum == "Card: ":
            tkmb.showerror("Error", "You have to enter a payment option")
        else:
            for w in self.widgets:
                w.grid_forget()
            self.widgets=[]
            rowcount=0
            self.confirmation_label = tk.Label(self, text='Confirmation:')
            self.confirmation_label.grid(row=rowcount, column=1, pady=10)
            rowcount+=1
            self.reservation_label = tk.Label(self, text='Reservation ID:')
            self.reservation_label.grid(row=rowcount, column=0, pady=10)

            rid=random.randint(0, 5000)
            get_res_ids = ("SELECT reservationid FROM reservation ")
            self.controller.cursor.execute(get_res_ids)
            while rid in self.controller.cursor:
                rid=random.randint(0, 5000)
            self.res_id_label = tk.Label(self, text=rid)
            self.res_id_label.grid(row=rowcount, column=1)
            rowcount+=1
            self.BACK = tk.Button(self, text='Done', command=lambda: self.finishPurchase())
            self.BACK.grid(row=rowcount, column=1, pady = 10)


            # Add reservation to db
            self.add_res = ("INSERT INTO reservation "
                            "(reservationid, username, cardnumber, is_cancelled, total_cost) "
                            "VALUES(%s, %s, %s, %s, %s)")
            self.res_info = (rid, self.controller.current_user, cardnum ,False, self.totalPrice)
            self.controller.cursor.execute(self.add_res, self.res_info)


            for tick in self.ticketArray:
                t_n, t_d, t_t, t_dep, t_arr, t_c, t_p, p_b, p_n = tick
                self.add_reserves = ("INSERT INTO reserves "
                                "(trainnumber, reservationid, class, departure_date, passenger_name, "
                                    "number_of_bags, departs_from, arrives_at) "
                                "VALUES(%s, %s, %s, %s, %s, %s, %s, %s)")
                self.reserves_info = (t_n, rid, t_c, t_d,p_n, p_b, t_dep, t_arr)
                self.controller.cursor.execute(self.add_reserves, self.reserves_info)

            self.controller.cnx.commit()
            self.ticketArray=[]
            self.widgets.append(self.confirmation_label)
            self.widgets.append(self.reservation_label)
            self.widgets.append(self.res_id_label)
            self.widgets.append(self.BACK)
    def finishPurchase(self):
        for w in self.widgets:
            w.grid_forget()
        self.createWidgets()
        self.controller.show_frame("ChooseFunctionality_Customer")

    def addPaymentInfo(self):
        for w in self.widgets:
            w.grid_forget()
        self.widgets = []
        self.packWidgets = []
        rowcount=0
        self.welcome = tk.Label(self, text= "Payment Information")
        self.welcome.grid(row=rowcount, column=2, pady=50)
        rowcount+=1
        self.card_label1 = tk.Label(self, text= "Add Card")
        self.card_label1.grid(row=rowcount, column=0, pady=20)
        self.card_label2 = tk.Label(self, text= "Delete Card")
        self.card_label2.grid(row=rowcount, column=3, pady=20)
        rowcount+=1
        self.name_on_card = tk.Label(self, text="Name on card: ")
        self.name_on_card.grid(row=rowcount, column=0)
        self.name_entry2 = tk.Entry(self, text="Name", width=30)
        self.name_entry2.grid(row=rowcount, column=1)

        get_cards = ("SELECT cardnumber FROM payment_info "
                        "WHERE username=%s")
        usr = str(self.controller.current_user)
        self.controller.cursor.execute(get_cards, (usr,))
        options = []
        self.cardOptionVar = tk.StringVar(self)
        self.cardOptionVar.set("Card: ")
        for cnum in self.controller.cursor:
            options.append(str(cnum[0]))
        if len(options)>0:
            self.payment_option = apply(tk.OptionMenu, (self, self.cardOptionVar) + tuple(options))
            self.payment_option.grid(row=rowcount, column=3)
            self.widgets.append(self.payment_option)

        rowcount+=1
        self.card_num_label = tk.Label(self, text="Card Number: ")
        self.card_num_label.grid(row=rowcount, column=0)
        self.card_num_entry = tk.Entry(self, text="####", width=30)
        self.card_num_entry.grid(row=rowcount, column=1)
        rowcount+=1
        self.cvv_label = tk.Label(self, text="CVV:")
        self.cvv_label.grid(row=rowcount, column=0)
        self.cvv_entry = tk.Entry(self, text="", width=10)
        self.cvv_entry.grid(row=rowcount, column=1)
        rowcount+=1
        self.date_label = tk.Label(self, text='Exp. Date: ')
        self.date_label.grid(row=rowcount, column=0)
        self.date_entry = tk.Frame(self)
        self.date_entry_1 = tk.Entry(self.date_entry, width=2)
        self.label_1 = tk.Label(self.date_entry, text='/')
        self.date_entry_2 = tk.Entry(self.date_entry, width=2)
        self.label_2 = tk.Label(self.date_entry, text='/')
        self.date_entry_3 = tk.Entry(self.date_entry, width=4)
        self.date_entry_1.pack(side=tk.LEFT)
        self.label_1.pack(side=tk.LEFT)
        self.date_entry_2.pack(side=tk.LEFT)
        self.label_2.pack(side=tk.LEFT)
        self.date_entry_3.pack(side=tk.LEFT)
        self.date_entry.grid(row=rowcount, column = 1)
        rowcount+=1
        self.submit_addCard=tk.Button(self, text='Submit', command=lambda: self.verifyPayment())
        self.submit_deleteCard=tk.Button(self, text='Submit', command=lambda: self.deleteCard())
        self.submit_addCard.grid(row=rowcount, column=1)
        self.submit_deleteCard.grid(row=rowcount, column=4)

        self.widgets.append(self.welcome)
        self.widgets.append(self.card_label1)
        self.widgets.append(self.card_label2)
        self.widgets.append(self.name_on_card)
        self.widgets.append(self.name_entry2)
        self.widgets.append(self.card_num_label)
        self.widgets.append(self.card_num_entry)
        self.widgets.append(self.cvv_label)
        self.widgets.append(self.cvv_entry)
        self.widgets.append(self.date_label)
        self.widgets.append(self.date_entry)
        self.widgets.append(self.submit_addCard)
        self.widgets.append(self.submit_deleteCard)

        self.packWidgets.append(self.date_entry_1)
        self.packWidgets.append(self.date_entry_2)
        self.packWidgets.append(self.date_entry_3)
        self.packWidgets.append(self.label_1)
        self.packWidgets.append(self.label_2)

    def verifyPayment(self):
        verified=True
        cardname = self.name_entry2.get()
        cardnum = self.card_num_entry.get()
        cvv = self.cvv_entry.get()
        exp_day, exp_month, exp_yr = self.date_entry_2.get(), self.date_entry_1.get(),\
            self.date_entry_3.get()

        if len(cardname)==0 or len(cardnum)==0 or len(cvv)==0 or len(exp_day)==0 or \
            len(exp_month)==0 or len(exp_yr)==0:
            tkmb.showerror("Error", "You must fill in all the fields")
            verified=False
        numbers = "0123456789"
        for x in exp_day:
            if x not in numbers:
                verified=False
                tkmb.showerror("Error", "You can only enter numbers for this field")
        for x in exp_month:
            if x not in numbers:
                verified=False
                tkmb.showerror("Error", "You can only enter numbers for this field")
        for x in exp_yr:
            if x not in numbers:
                verified=False
                tkmb.showerror("Error", "You can only enter numbers for this field")
        current_date = datetime.datetime.now()
        curr_yr = current_date.year
        curr_day = current_date.day
        curr_mo = current_date.month
        if int(exp_month) < 1 or int(exp_month) > 12:
                    verified = False
                    tkmb.showerror("Error", "That month doesn't exist.")
        if int(exp_yr) < int(curr_yr):
            verified = False
            tkmb.showerror("Error", "Your card is expired")
        if int(exp_yr) == int(curr_yr) and int(exp_month) < int(curr_mo):
            verified = False
            tkmb.showerror("Error", "Your card is expired")
        if int(exp_yr) == int(curr_yr) and int(exp_month) == int(curr_mo) and int(exp_day) < int(curr_day):
            verified = False
            tkmb.showerror("Error", "Your card is expired")
        elif int(exp_yr) == int(curr_yr) and int(exp_month) == int(curr_mo) and int(exp_day) == int(curr_day):
            verified = False
            tkmb.showerror("Sorry", "Your card is expired")

        if len(cardnum)!=16:
            verified=False
            tkmb.showerror("Error", "Invalid card number")
        if len(cvv)!=3:
            verified=False
            tkmb.showerror("Error", "Invalid CVV")
        if verified:
            tkmb.showinfo("Success!", "Card Added")
            add_new_card = ("INSERT INTO payment_info "
                            "(cardnumber, cvv, exp_date, name_on_card, username) "
                            "VALUES(%s, %s, %s, %s, %s) ")
            expdate = datetime.date(int(exp_yr), int(exp_month), int(exp_day))
            new_card_values = (cardnum, cvv, expdate, cardname, self.controller.current_user)
            self.controller.cursor.execute(add_new_card, new_card_values)
            self.controller.cnx.commit()
            self.goBackToCheckout()

    def deleteCard(self):
        verified=True
        card = self.cardOptionVar.get()
        if card=="Card: ":
            verified=False
            tkmb.showerror("Error", "You must select a card.")
        if verified:
            del_card = ("DELETE FROM payment_info WHERE cardnumber=%s")
            self.controller.cursor.execute(del_card, (card,))
            self.controller.cnx.commit()
            tkmb.showinfo("Success", "Card Deleted.")
            self.goBackToCheckout()

    def goBackToCheckout(self):
        for w in self.widgets:
            w.grid_forget()
        self.addTicket()

class UpdateReservation(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='aliceblue')
        self.controller = controller
        self.createWidgets()
    def createWidgets(self):
        self.widgets=[]
        rowcount=0
        welcome = tk.Label(self, text= "Update Reservation")
        welcome.grid(row=rowcount, column=1, pady=10)
        rowcount+=1
        res_id_label = tk.Label(self, text="Reservation ID: ")
        res_id_label.grid(row=rowcount, column=0, pady=10)
        self.res_id = tk.Entry(self, width=10)
        self.res_id.grid(row=rowcount, column=1, pady=10)
        GO = tk.Button(self, text='Next', command=lambda:
            self.submitReservationID())
        GO.grid(row=rowcount, column=2, pady=20)
        rowcount+=1
        BACK = tk.Button(self, text='Back', command=lambda:
            self.controller.show_frame("ChooseFunctionality_Customer"))
        BACK.grid(row=rowcount, column=0, pady=20)
        #Add widgets to array
        self.widgets.append(welcome)
        self.widgets.append(res_id_label)
        self.widgets.append(self.res_id)
        self.widgets.append(GO)
        self.widgets.append(BACK)
    def submitReservationID(self):
        self.rid = self.res_id.get()
        numbers='0123456789'
        validID = True
        for x in self.rid:
            if x not in numbers:
                tkmb.showerror("Error", "Reservation ID should only contain numbers")
                validID=False
        get_res_info = ("SELECT username, is_cancelled FROM reservation WHERE reservationid=%s")
        self.rid = int(self.rid)
        self.controller.cursor.execute(get_res_info, (self.rid, ))
        obj = self.controller.cursor.fetchone()
        if obj == None:
            tkmb.showerror("Error", "Invalid Reservation ID")
            validID=False
        (user, isc) = obj
        if isc == 1:
            tkmb.showerror("Error", "Cannot update a cancelled reservation.")
            validID=False
        else:
            uname=list((user, isc))[0]
        if uname!=self.controller.current_user and validID:
            tkmb.showerror("Error", "Invalid Reservation ID")
            validID=False
        curr_date = datetime.datetime.now()
        curr_date = datetime.date(curr_date.year, curr_date.month,\
            curr_date.day)
        get_departure_dates = ("SELECT departure_date FROM reserves "
                                "WHERE reservationid=%s")
        self.controller.cursor.execute(get_departure_dates, (self.rid, ))
        earliest_dept_date = None
        for d in self.controller.cursor:
            d=d[0]
            if earliest_dept_date==None:
                earliest_dept_date=d
            elif earliest_dept_date>d:
                earliest_dept_date=d
        if earliest_dept_date <= curr_date:
            validID=False
            tkmb.showerror("Error", "You cannot update a reservation that has already happened.")
        if validID:
            for w in self.widgets:
                w.grid_forget()
            self.widgets=[]
            rowcount=0
            welcome_label = tk.Label(self, text= "Update Reservation:")
            welcome_label.grid(row=rowcount, column=1, pady=10, padx=5)
            rid_label = tk.Label(self, text= '#' + str(self.rid))
            rid_label.grid(row=rowcount, column=2, pady=10, padx=5)
            rowcount+=1
            select_label = tk.Label(self, text= "Select")
            select_label.grid(row=rowcount, column=0, pady=10, padx=5)
            train_label = tk.Label(self, text= "Train Number")
            train_label.grid(row=rowcount, column=1, pady=10, padx=5)
            time_label = tk.Label(self, text= "Time")
            time_label.grid(row=rowcount, column=2, pady=10, padx=5)
            departs = tk.Label(self, text= "Departs From")
            departs.grid(row=rowcount, column=3, pady=10, padx=5)
            arrives = tk.Label(self, text= "Arrives At")
            arrives.grid(row=rowcount, column=4, pady=10, padx=5)
            class_label = tk.Label(self, text= "Class")
            class_label.grid(row=rowcount, column=5, pady=10, padx=5)
            price_label = tk.Label(self, text= "Price")
            price_label.grid(row=rowcount, column=6, pady=10, padx=5)
            bags_label = tk.Label(self, text= "Number of Bags")
            bags_label.grid(row=rowcount, column=7, pady=10, padx=5)
            pname_label = tk.Label(self, text= "Passenger Name")
            pname_label.grid(row=rowcount, column=8, pady=10, padx=5)
            self.widgets.append(rid_label)
            self.widgets.append(welcome_label)
            self.widgets.append(select_label)
            self.widgets.append(train_label)
            self.widgets.append(time_label)
            self.widgets.append(departs)
            self.widgets.append(arrives)
            self.widgets.append(class_label)
            self.widgets.append(price_label)
            self.widgets.append(bags_label)
            self.widgets.append(pname_label)


            self.route_prices={}
            # get_prices = ("SELECT trainnumber, class, first_class_price, second_class_price "
            #             "FROM reserves NATURAL JOIN trainroute WHERE reservationid=%s")

            get_prices=("SELECT * FROM trainroute ")
            self.controller.cursor.execute(get_prices)
            for (tn, fcp, scp) in self.controller.cursor:
                self.route_prices[tn] = (fcp, scp)

            self.ticketselector = tk.IntVar()
            tid=0
            self.ticketselector.set(0)
            get_reserves = ("SELECT * FROM reserves WHERE reservationid=%s")
            self.controller.cursor.execute(get_reserves, (self.rid,))
            rowcount+=1
            self.ticket_dictionary = {}
            for (tnum, resid, cl, dep_date, pname, num_bags, dep, arr) in self.controller.cursor:
                select_t = tk.Radiobutton(self, variable=self.ticketselector, value=tid)
                select_t.grid(row=rowcount, column=0, pady=10, padx=5)
                train_t = tk.Label(self, text=tnum)
                train_t.grid(row=rowcount, column=1, pady=10, padx=5)
                time_t = tk.Label(self, text=dep_date)
                time_t.grid(row=rowcount, column=2, pady=10, padx=5)
                departs_t = tk.Label(self, text=dep)
                departs_t.grid(row=rowcount, column=3, pady=10, padx=5)
                arrives_t = tk.Label(self, text=arr)
                arrives_t.grid(row=rowcount, column=4, pady=10, padx=5)
                class_t = tk.Label(self, text=cl)
                class_t.grid(row=rowcount, column=5, pady=10, padx=5)
                cost = ""
                if cl=='first':
                    cost=self.route_prices[tnum][0]
                elif cl=='second':
                    cost=self.route_prices[tnum][1]
                price_t = tk.Label(self, text=cost)
                price_t.grid(row=rowcount, column=6, pady=10, padx=5)
                bags_t = tk.Label(self, text=num_bags)
                bags_t.grid(row=rowcount, column=7, pady=10, padx=5)
                pname_t = tk.Label(self, text=pname)
                pname_t.grid(row=rowcount, column=8, pady=10, padx=5)
                self.ticket_dictionary[tid] = (tnum, resid, cl, dep_date, pname, num_bags, dep, arr)
                self.widgets.append(select_t)
                self.widgets.append(train_t)
                self.widgets.append(time_t)
                self.widgets.append(departs_t)
                self.widgets.append(arrives_t)
                self.widgets.append(class_t)
                self.widgets.append(price_t)
                self.widgets.append(bags_t)
                self.widgets.append(pname_t)
                tid+=1
                rowcount+=1
            GO = tk.Button(self, text='Next', command=lambda:
            self.confirmUpdate())
            GO.grid(row=rowcount, column=2, pady=20)
            BACK = tk.Button(self, text='Back', command=lambda:
                self.goBack1())
            BACK.grid(row=rowcount, column=0, pady=20)
            self.widgets.append(GO)
            self.widgets.append(BACK)

    def goBack1(self):
        for w in self.widgets:
            w.grid_forget()
        self.createWidgets()

    def confirmUpdate(self):
        validUpdate=True
        curr_date = datetime.datetime.now()
        curr_date = datetime.date(curr_date.year, curr_date.month,\
            curr_date.day)
        (tnum, resid, cl, dep_date, pname, num_bags, dep, arr) = \
            self.ticket_dictionary[self.ticketselector.get()]
        if curr_date >= dep_date:
            tkmb.showerror("Error", "You cannot update a reservation that has already happened.")
            validUpdate=False
        if validUpdate:
            for w in self.widgets:
                w.grid_forget()
            self.widgets=[]
            rowcount=0
            welcome_label = tk.Label(self, text= "Update Reservation:")
            welcome_label.grid(row=rowcount, column=1, pady=10, padx=5)
            rid_label = tk.Label(self, text= '#' + str(self.rid))
            rid_label.grid(row=rowcount, column=2, pady=10, padx=5)
            rowcount+=1
            current_ticket_label = tk.Label(self, text= "Current Train Ticket:")
            current_ticket_label.grid(row=rowcount, column=1, pady=10, padx=5)
            rowcount+=1
            train_label = tk.Label(self, text= "Train Number")
            train_label.grid(row=rowcount, column=1, pady=10, padx=5)
            time_label = tk.Label(self, text= "Time")
            time_label.grid(row=rowcount, column=2, pady=10, padx=5)
            departs = tk.Label(self, text= "Departs From")
            departs.grid(row=rowcount, column=3, pady=10, padx=5)
            arrives = tk.Label(self, text= "Arrives At")
            arrives.grid(row=rowcount, column=4, pady=10, padx=5)
            class_label = tk.Label(self, text= "Class")
            class_label.grid(row=rowcount, column=5, pady=10, padx=5)
            price_label = tk.Label(self, text= "Price")
            price_label.grid(row=rowcount, column=6, pady=10, padx=5)
            bags_label = tk.Label(self, text= "Number of Bags")
            bags_label.grid(row=rowcount, column=7, pady=10, padx=5)
            pname_label = tk.Label(self, text= "Passenger Name")
            pname_label.grid(row=rowcount, column=8, pady=10, padx=5)
            self.widgets.append(rid_label)
            self.widgets.append(welcome_label)
            self.widgets.append(current_ticket_label)
            self.widgets.append(train_label)
            self.widgets.append(time_label)
            self.widgets.append(departs)
            self.widgets.append(arrives)
            self.widgets.append(class_label)
            self.widgets.append(price_label)
            self.widgets.append(bags_label)
            self.widgets.append(pname_label)
            tid = self.ticketselector.get()
            (tnum, resid, cl, self.dep_date, pname, num_bags, dep, arr) = self.ticket_dictionary[tid]
            rowcount+=1
            train_t = tk.Label(self, text=tnum)
            train_t.grid(row=rowcount, column=1, pady=10, padx=5)
            time_t = tk.Label(self, text=self.dep_date)
            time_t.grid(row=rowcount, column=2, pady=10, padx=5)
            departs_t = tk.Label(self, text=dep)
            departs_t.grid(row=rowcount, column=3, pady=10, padx=5)
            arrives_t = tk.Label(self, text=arr)
            arrives_t.grid(row=rowcount, column=4, pady=10, padx=5)
            class_t = tk.Label(self, text=cl)
            class_t.grid(row=rowcount, column=5, pady=10, padx=5)
            cost = ""
            if cl=='first':
                cost=self.route_prices[tnum][0]
            elif cl=='second':
                cost=self.route_prices[tnum][1]
            price_t = tk.Label(self, text= cost)
            price_t.grid(row=rowcount, column=6, pady=10, padx=5)
            bags_t = tk.Label(self, text=num_bags)
            bags_t.grid(row=rowcount, column=7, pady=10, padx=5)
            pname_t = tk.Label(self, text=pname)
            pname_t.grid(row=rowcount, column=8, pady=10, padx=5)
            self.widgets.append(train_t)
            self.widgets.append(time_t)
            self.widgets.append(departs_t)
            self.widgets.append(arrives_t)
            self.widgets.append(class_t)
            self.widgets.append(price_t)
            self.widgets.append(bags_t)
            self.widgets.append(pname_t)
            rowcount+=1
            new_departure_label = tk.Label(self, text= "New Departure Date:")
            new_departure_label.grid(row=rowcount, column=1, pady=20, padx=5)
            self.date_entry = tk.Frame(self)
            self.date_entry_1 = tk.Entry(self.date_entry, width=2)
            self.label_1 = tk.Label(self.date_entry, text='/')
            self.date_entry_2 = tk.Entry(self.date_entry, width=2)
            self.label_2 = tk.Label(self.date_entry, text='/')
            self.date_entry_3 = tk.Entry(self.date_entry, width=4)
            self.date_entry_1.pack(side=tk.LEFT)
            self.label_1.pack(side=tk.LEFT)
            self.date_entry_2.pack(side=tk.LEFT)
            self.label_2.pack(side=tk.LEFT)
            self.date_entry_3.pack(side=tk.LEFT)
            self.date_entry.grid(row=rowcount, column=2, pady=20)
            self.widgets.append(self.date_entry)
            self.widgets.append(new_departure_label)
            rowcount+=1
            GO = tk.Button(self, text='Next', command=lambda:
            self.updatedTicket())
            GO.grid(row=rowcount, column=2, pady=20)
            BACK = tk.Button(self, text='Back', command=lambda:
                self.submitReservationID())
            BACK.grid(row=rowcount, column=0, pady=20)
            self.widgets.append(GO)
            self.widgets.append(BACK)

    def updatedTicket(self):
        validUpdate = True
        curr_date = datetime.datetime.now()
        curr_date = datetime.date(curr_date.year, curr_date.month,\
            curr_date.day)
        new_dep_date = datetime.date(int(self.date_entry_3.get()), int(self.date_entry_1.get()),\
            int(self.date_entry_2.get()))
        
        
        if new_dep_date <= curr_date:
            tkmb.showerror("Error", "That date is in the past.")
            validUpdate=False
        if validUpdate:
            for w in self.widgets:
                w.grid_forget()
            self.widgets=[]
            rowcount=0
            welcome_label = tk.Label(self, text= "Update Reservation:")
            welcome_label.grid(row=rowcount, column=1, pady=10, padx=5)
            rid_label = tk.Label(self, text= '#' + str(self.rid))
            rid_label.grid(row=rowcount, column=2, pady=10, padx=5)
            rowcount+=1
            current_ticket_label = tk.Label(self, text= "Current Train Ticket:")
            current_ticket_label.grid(row=rowcount, column=1, pady=10, padx=5)
            rowcount+=1
            train_label = tk.Label(self, text= "Train Number")
            train_label.grid(row=rowcount, column=1, pady=10, padx=5)
            time_label = tk.Label(self, text= "Time")
            time_label.grid(row=rowcount, column=2, pady=10, padx=5)
            departs = tk.Label(self, text= "Departs From")
            departs.grid(row=rowcount, column=3, pady=10, padx=5)
            arrives = tk.Label(self, text= "Arrives At")
            arrives.grid(row=rowcount, column=4, pady=10, padx=5)
            class_label = tk.Label(self, text= "Class")
            class_label.grid(row=rowcount, column=5, pady=10, padx=5)
            price_label = tk.Label(self, text= "Price")
            price_label.grid(row=rowcount, column=6, pady=10, padx=5)
            bags_label = tk.Label(self, text= "Number of Bags")
            bags_label.grid(row=rowcount, column=7, pady=10, padx=5)
            pname_label = tk.Label(self, text= "Passenger Name")
            pname_label.grid(row=rowcount, column=8, pady=10, padx=5)
            self.widgets.append(rid_label)
            self.widgets.append(welcome_label)
            self.widgets.append(current_ticket_label)
            self.widgets.append(train_label)
            self.widgets.append(time_label)
            self.widgets.append(departs)
            self.widgets.append(arrives)
            self.widgets.append(class_label)
            self.widgets.append(price_label)
            self.widgets.append(bags_label)
            self.widgets.append(pname_label)
            tid = self.ticketselector.get()
            (self.tnum, resid, cl, dep_date, pname, num_bags, dep, arr) = self.ticket_dictionary[tid]
            rowcount+=1
            train_t = tk.Label(self, text=self.tnum)
            train_t.grid(row=rowcount, column=1, pady=10, padx=5)



            self.new_dep_date = datetime.date(int(self.date_entry_3.get()), int(self.date_entry_1.get()),\
                int(self.date_entry_2.get()))
            time_t = tk.Label(self, text=self.new_dep_date)
            time_t.grid(row=rowcount, column=2, pady=10, padx=5)
            departs_t = tk.Label(self, text=dep)
            departs_t.grid(row=rowcount, column=3, pady=10, padx=5)
            arrives_t = tk.Label(self, text=arr)
            arrives_t.grid(row=rowcount, column=4, pady=10, padx=5)
            class_t = tk.Label(self, text=cl)
            class_t.grid(row=rowcount, column=5, pady=10, padx=5)
            cost = ""
            if cl=='first':
                cost=self.route_prices[self.tnum][0]
            elif cl=='second':
                cost=self.route_prices[self.tnum][1]
            price_t = tk.Label(self, text= cost)
            price_t.grid(row=rowcount, column=6, pady=10, padx=5)
            bags_t = tk.Label(self, text=num_bags)
            bags_t.grid(row=rowcount, column=7, pady=10, padx=5)
            pname_t = tk.Label(self, text=pname)
            pname_t.grid(row=rowcount, column=8, pady=10, padx=5)
            self.widgets.append(train_t)
            self.widgets.append(time_t)
            self.widgets.append(departs_t)
            self.widgets.append(arrives_t)
            self.widgets.append(class_t)
            self.widgets.append(price_t)
            self.widgets.append(bags_t)
            self.widgets.append(pname_t)
            rowcount+=1
            fee_label = tk.Label(self, text="Change Fee")
            fee_amnt = tk.Label(self, text='50')
            fee_label.grid(row=rowcount, column=0, pady=10)
            fee_amnt.grid(row=rowcount, column=1, pady=10)
            rowcount+=1
            # Get total cost
            get_total_cost = ("SELECT total_cost FROM reservation "
                            "WHERE reservationid=%s")
            self.controller.cursor.execute(get_total_cost, (self.rid, ))
            tcost = list(self.controller.cursor.fetchone())[0]
            tcost+=50
            updated_cost_label = tk.Label(self, text="Updated Total Cost")
            updated_cost_amnt = tk.Label(self, text=tcost)
            updated_cost_label.grid(row=rowcount, column=0, pady=10)
            updated_cost_amnt.grid(row=rowcount, column=1, pady=10)
            
            rowcount+=1
            GO = tk.Button(self, text='Submit', command=lambda:
            self.submitUpdate())
            GO.grid(row=rowcount, column=2, pady=20)
            BACK = tk.Button(self, text='Back', command=lambda:
                self.submitReservationID())
            BACK.grid(row=rowcount, column=0, pady=20)
            self.widgets.append(GO)
            self.widgets.append(BACK)
    def submitUpdate(self):
        update_cost = ("UPDATE reservation SET total_cost = total_cost + 50 WHERE reservationid=%s")
        self.controller.cursor.execute(update_cost, (self.rid,))        
        update_date = ("UPDATE reserves SET departure_date=%s WHERE reservationid=%s AND trainnumber=%s")
        self.controller.cursor.execute(update_date, (self.new_dep_date,self.rid, self.tnum))

        
        tkmb.showinfo("Success!", "Reservation updated.")
        for w in self.widgets:
            w.grid_forget()
        self.createWidgets()
        self.controller.cnx.commit()
        self.controller.show_frame("ChooseFunctionality_Customer")




class CancelReservation(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='aliceblue')
        self.controller = controller
        self.createWidgets()

    def createWidgets(self):
        rowcount=0
        self.widgets=[]
        self.welcome = tk.Label(self, text= "CancelReservation")
        self.welcome.grid(row=rowcount, column=1, pady=20)
        rowcount+=1
        res_id_label = tk.Label(self, text="Reservation ID: ")
        res_id_label.grid(row=rowcount, column=0, pady=20)
        self.res_id = tk.Entry(self, width=10)
        self.res_id.grid(row=rowcount, column=1, pady=20)
        SUBMIT = tk.Button(self, text="Search", command=lambda: self.findReservation())
        SUBMIT.grid(row=rowcount, column=2, pady=20)
        rowcount+=1
        self.BACK = tk.Button(self, text='Back', command=lambda:
            self.controller.show_frame("ChooseFunctionality_Customer"))
        self.BACK.grid(row=rowcount, column=1, pady=20)
        self.widgets.append(self.welcome)
        self.widgets.append(res_id_label)
        self.widgets.append(self.res_id)
        self.widgets.append(SUBMIT)
        self.widgets.append(self.BACK)
    def findReservation(self):
        self.rid = self.res_id.get()
        numbers='0123456789'
        validID = True
        for x in self.rid:
            if x not in numbers:
                tkmb.showerror("Error", "Reservation ID should only contain numbers")
                validID=False
        get_res_info = ("SELECT username, is_cancelled FROM reservation WHERE reservationid=%s")
        self.rid = int(self.rid)
        self.controller.cursor.execute(get_res_info, (self.rid, ))
        obj = self.controller.cursor.fetchone()
        if obj  == None:
            tkmb.showerror("Error", "Invalid Reservation ID")
            validID=False
        (uname,isc) = obj
        if isc == 1:
            tkmb.showerror("Error", "Cannot cancel a cancelled reservation")
            validID=False
        else:
            uname=list((uname,isc))[0]
        if uname!=self.controller.current_user and validID:
            tkmb.showerror("Error", "Invalid Reservation ID")
            validID=False
        if validID:
            self.drawCancelScreen()
    def drawCancelScreen(self):
        verified=True
        curr_date = datetime.datetime.now()
        curr_date = datetime.date(curr_date.year, curr_date.month,\
            curr_date.day)
        get_departure_dates = ("SELECT departure_date FROM reserves "
                                "WHERE reservationid=%s")
        self.controller.cursor.execute(get_departure_dates, (self.rid, ))
        earliest_dept_date = None
        for d in self.controller.cursor:
            d=d[0]
            if earliest_dept_date==None:
                earliest_dept_date=d
            elif earliest_dept_date>d:
                earliest_dept_date=d
        if earliest_dept_date <= curr_date:
            verified=False
            tkmb.showerror("Error", "You cannot cancel a reservation that has already happened.")
        else:
            for w in self.widgets:
                w.grid_forget()
            self.widgets=[]
            rowcount=0
            welcome_label = tk.Label(self, text= "Cancel Reservation:")
            welcome_label.grid(row=rowcount, column=1, pady=10, padx=5)
            rid_label = tk.Label(self, text= '#' + str(self.rid))
            rid_label.grid(row=rowcount, column=2, pady=10, padx=5)
            rowcount+=1
            train_label = tk.Label(self, text= "Train Number")
            train_label.grid(row=rowcount, column=1, pady=10, padx=5)
            time_label = tk.Label(self, text= "Time")
            time_label.grid(row=rowcount, column=2, pady=10, padx=5)
            departs = tk.Label(self, text= "Departs From")
            departs.grid(row=rowcount, column=3, pady=10, padx=5)
            arrives = tk.Label(self, text= "Arrives At")
            arrives.grid(row=rowcount, column=4, pady=10, padx=5)
            class_label = tk.Label(self, text= "Class")
            class_label.grid(row=rowcount, column=5, pady=10, padx=5)
            price_label = tk.Label(self, text= "Price")
            price_label.grid(row=rowcount, column=6, pady=10, padx=5)
            bags_label = tk.Label(self, text= "Number of Bags")
            bags_label.grid(row=rowcount, column=7, pady=10, padx=5)
            pname_label = tk.Label(self, text= "Passenger Name")
            pname_label.grid(row=rowcount, column=8, pady=10, padx=5)
            self.widgets.append(rid_label)
            self.widgets.append(welcome_label)
            self.widgets.append(train_label)
            self.widgets.append(time_label)
            self.widgets.append(departs)
            self.widgets.append(arrives)
            self.widgets.append(class_label)
            self.widgets.append(price_label)
            self.widgets.append(bags_label)
            self.widgets.append(pname_label)
            self.route_prices={}
            get_prices=("SELECT * FROM trainroute ")
            self.controller.cursor.execute(get_prices)
            for (tn, fcp, scp) in self.controller.cursor:
                self.route_prices[tn] = (fcp, scp)
            tid=0
            get_reserves = ("SELECT * FROM reserves WHERE reservationid=%s ")
            self.controller.cursor.execute(get_reserves, (self.rid,))
            rowcount+=1
            self.ticket_dictionary = {}
            for (tnum, resid, cl, dep_date, pname, num_bags, dep, arr) in self.controller.cursor:
                train_t = tk.Label(self, text=tnum)
                train_t.grid(row=rowcount, column=1, pady=10, padx=5)
                time_t = tk.Label(self, text=dep_date)
                time_t.grid(row=rowcount, column=2, pady=10, padx=5)
                departs_t = tk.Label(self, text=dep)
                departs_t.grid(row=rowcount, column=3, pady=10, padx=5)
                arrives_t = tk.Label(self, text=arr)
                arrives_t.grid(row=rowcount, column=4, pady=10, padx=5)
                class_t = tk.Label(self, text=cl)
                class_t.grid(row=rowcount, column=5, pady=10, padx=5)
                cost = ""
                if cl=='first':
                    cost=self.route_prices[tnum][0]
                elif cl=='second':
                    cost=self.route_prices[tnum][1]
                price_t = tk.Label(self, text=cost)
                price_t.grid(row=rowcount, column=6, pady=10, padx=5)
                bags_t = tk.Label(self, text=num_bags)
                bags_t.grid(row=rowcount, column=7, pady=10, padx=5)
                pname_t = tk.Label(self, text=pname)
                pname_t.grid(row=rowcount, column=8, pady=10, padx=5)
                self.ticket_dictionary[tid] = (tnum, resid, cl, dep_date, pname, num_bags, dep, arr)
                self.widgets.append(train_t)
                self.widgets.append(time_t)
                self.widgets.append(departs_t)
                self.widgets.append(arrives_t)
                self.widgets.append(class_t)
                self.widgets.append(price_t)
                self.widgets.append(bags_t)
                self.widgets.append(pname_t)
                tid+=1
                rowcount+=1

            get_total_cost = ("SELECT total_cost FROM reservation "
                            "WHERE reservationid=%s")
            self.controller.cursor.execute(get_total_cost, (self.rid, ))
            self.tcost = float(list(self.controller.cursor.fetchone())[0])
            tcost_label = tk.Label(self, text= "Total Cost of Reservation: ")
            tcost_label.grid(row=rowcount, column=1, pady=10, padx=5)
            tcost_amnt = tk.Label(self, text="$" + str(self.tcost))
            tcost_amnt.grid(row=rowcount, column=2, pady=10, padx=5)
            rowcount+=1

            cancel_date_label = tk.Label(self, text= "Date of Cancellation: ")
            cancel_date_label.grid(row=rowcount, column=1, pady=10, padx=5)
            cancel_date = tk.Label(self, text=curr_date)
            cancel_date.grid(row=rowcount, column=2, pady=10, padx=5)
            rowcount+=1
            refund_label = tk.Label(self, text= "Amount to be Refunded: ")
            refund_label.grid(row=rowcount, column=1, pady=10, padx=5)

            
            oneweekprior = earliest_dept_date - datetime.timedelta(weeks=1)
            onedayprior = earliest_dept_date - datetime.timedelta(days=1)
            if curr_date <= oneweekprior:
                self.refund=self.tcost*0.8
            elif curr_date <= onedayprior and curr_date >= oneweekprior:
                self.refund=self.tcost*0.5
            self.refund-=50
            if self.refund < 0: self.refund=0
            refund_amnt = tk.Label(self, text="$"+str(self.refund))
            refund_amnt.grid(row=rowcount, column=2, pady=10, padx=5)
            rowcount+=1
            GO = tk.Button(self, text='Submit', command=lambda:
            self.submitCancellation())
            GO.grid(row=rowcount, column=4, pady=20)
            BACK = tk.Button(self, text='Back', command=lambda:
                self.goBack1())
            BACK.grid(row=rowcount, column=1, pady=20)
            self.widgets.append(tcost_label)
            self.widgets.append(tcost_amnt)
            self.widgets.append(cancel_date_label)
            self.widgets.append(cancel_date)
            self.widgets.append(refund_label)
            self.widgets.append(refund_amnt)
            self.widgets.append(GO)
            self.widgets.append(BACK)
    def submitCancellation(self):
        newCost = self.tcost - self.refund
        cancel_res = ("UPDATE reservation SET is_cancelled=1, total_cost=%s "
                    "WHERE reservationid=%s")
        self.controller.cursor.execute(cancel_res, (newCost, self.rid))
        self.controller.cnx.commit()
        for w in self.widgets:
            w.grid_forget()
        self.widgets=[]
        tkmb.showinfo("Success", "You are now going nowhere.")
        self.controller.show_frame("ChooseFunctionality_Customer")
        self.createWidgets()
    def goBack1(self):
        for w in self.widgets:
            w.grid_forget()
        self.createWidgets()

class GiveReview(tk.Frame):
    """
    Give Review
    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='aliceblue')
        self.controller = controller
        self.createWidgets()

    def createWidgets(self):
        self.widgets = []
        rowcount=0
        self.welcome = tk.Label(self, text= "Give A Review")
        self.welcome.grid(row=rowcount, column=2, pady=50)
        rowcount+=1
        # Get Train Numbers
        get_numbers = ("SELECT * FROM trainroute")
        self.controller.cursor.execute(get_numbers)
        options = []
        self.optionVar = tk.StringVar(self)
        self.optionVar.set("Train Number")
        for (tnum, c1, c2) in self.controller.cursor:
            options.append(str(tnum))
        self.select_train = apply(tk.OptionMenu, (self, self.optionVar) + tuple(options))
        self.select_train.grid(row=rowcount, column=2, pady=10)
        rowcount+=1
        verygood_label = tk.Label(self, text='very good')
        good_label = tk.Label(self, text='good')
        neutral_label = tk.Label(self, text='neutral')
        bad_label = tk.Label(self, text='bad')
        verybad_label = tk.Label(self, text='very bad')
        verygood_label.grid(row=rowcount, column=0, pady=10, padx=10)
        good_label.grid(row=rowcount, column=1, pady=10, padx=10)
        neutral_label.grid(row=rowcount, column=2, pady=10, padx=10)
        bad_label.grid(row=rowcount, column=3, pady=10, padx=10)
        verybad_label.grid(row=rowcount, column=4, pady=10, padx=10)

        rowcount+=1
        self.reviewVar = tk.StringVar()
        self.reviewVar.set("not set")
        verygood = tk.Radiobutton(self, variable=self.reviewVar, value='very good')
        good = tk.Radiobutton(self, variable=self.reviewVar, value='good')
        neutral = tk.Radiobutton(self, variable=self.reviewVar, value='neutral')
        bad = tk.Radiobutton(self, variable=self.reviewVar, value='bad')
        verybad = tk.Radiobutton(self, variable=self.reviewVar, value='very bad')
        verygood.grid(row=rowcount, column=0, pady=10)
        good.grid(row=rowcount, column=1, pady=10)
        neutral.grid(row=rowcount, column=2, pady=10)
        bad.grid(row=rowcount, column=3, pady=10)
        verybad.grid(row=rowcount, column=4, pady=10)

        rowcount+=1
        self.comment_label = tk.Label(self, text="Comment: ")
        self.comment_label.grid(row=rowcount, column=1, pady=10)
        self.comment = tk.Entry(self, width=20)
        self.comment.grid(row=rowcount, column=2, pady=10)
        rowcount+=1
        self.GO = tk.Button(self, text='Submit', command=lambda: self.submitReview())
        self.GO.grid(row=rowcount, column=2, pady = 10)     
        rowcount+=1
        self.BACK = tk.Button(self, text='Back', command=lambda:
            self.controller.show_frame("ChooseFunctionality_Customer"))
        self.BACK.grid(row=rowcount, column=2, pady = 10)
        # Add widgets to array
        self.widgets.append(self.welcome)
        self.widgets.append(self.select_train)
        self.widgets.append(verygood_label)
        self.widgets.append(good_label)
        self.widgets.append(neutral_label)
        self.widgets.append(bad_label)
        self.widgets.append(verybad_label)
        self.widgets.append(verygood)
        self.widgets.append(good)
        self.widgets.append(neutral)
        self.widgets.append(bad)
        self.widgets.append(verybad)
        self.widgets.append(self.comment_label)
        self.widgets.append(self.comment)
        self.widgets.append(self.GO)
        self.widgets.append(self.BACK)
    def submitReview(self):
        get_rid = ("SELECT COUNT(reviewid) FROM review ")
        self.controller.cursor.execute(get_rid)
        rid=list(self.controller.cursor.fetchone())
        rid[0]+=1

        add_review = ("INSERT INTO review "
                    "(reviewid, comment, rating, username, trainnumber)"
                    "VALUES(%s, %s, %s, %s, %s)")
        tnum=self.optionVar.get()
        rated=self.reviewVar.get()
        comment=self.comment.get()

        verified=True
        if tnum=="Train Number":
            tkmb.showerror("Error", "You must enter a train number")
            verified=False
        elif rated=="not set":
            tkmb.showerror("Error", "You must select a rating")
            verified=False

        if verified:
            review_info = (rid[0], comment, rated, self.controller.current_user, tnum)
            self.controller.cursor.execute(add_review, review_info)
            self.controller.cnx.commit()
            tkmb.showinfo("Success!", "Review Submitted")
            self.goBack()
    def goBack(self):
        for w in self.widgets:
            w.grid_forget()
        self.createWidgets()
        self.controller.show_frame("ChooseFunctionality_Customer")


class ViewReview(tk.Frame):
    """
    View Review
    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='aliceblue')
        self.controller = controller
        self.createWidgets()

    def createWidgets(self):
        self.widgets=[]
        rowcount=0
        welcome = tk.Label(self, text= "View Review")
        welcome.grid(row=rowcount, column=1, pady=10)
        rowcount+=1
        get_numbers = ("SELECT * FROM trainroute")
        self.controller.cursor.execute(get_numbers)
        options = []
        self.optionVar = tk.StringVar(self)
        self.optionVar.set("Train Number")
        for (tnum, c1, c2) in self.controller.cursor:
            options.append(str(tnum))
        self.select_train = apply(tk.OptionMenu, (self, self.optionVar) + tuple(options))
        self.select_train.grid(row=rowcount, column=1, pady=10)
        rowcount+=1
        self.GO = tk.Button(self, text='Next', command=lambda:
            self.submitTrainNumber())
        self.GO.grid(row=rowcount, column=2, pady=20)
        self.BACK = tk.Button(self, text='Back', command=lambda:
            self.controller.show_frame("ChooseFunctionality_Customer"))
        self.BACK.grid(row=rowcount, column=0, pady=20)
        #Add widgets to array
        self.widgets.append(welcome)
        self.widgets.append(self.select_train)
        self.widgets.append(self.GO)
        self.widgets.append(self.BACK)
    def submitTrainNumber(self):
        tnum=self.optionVar.get()
        trainselected = True
        if tnum=="Train Number":
            trainselected=False
            tkmb.showerror("Error", "You must select a train number")
        if trainselected:
            for w in self.widgets:
                w.grid_forget()
            self.widgets=[]
            rowcount=0
            welcome = tk.Label(self, text= "View Review")
            welcome.grid(row=rowcount, column=0, pady=10)
            rowcount+=1
            rating_label = tk.Label(self, text="Rating", borderwidth=1)
            comment_label = tk.Label(self, text="Comment", borderwidth=1)
            rating_label.grid(row=rowcount, column=1, padx=10,pady=10)
            comment_label.grid(row=rowcount, column=2, padx=10, pady=10)
            self.widgets.append(welcome)
            self.widgets.append(rating_label)
            self.widgets.append(comment_label)
            
            get_reviews = ("SELECT comment, rating FROM review WHERE trainnumber=%s")
            self.controller.cursor.execute(get_reviews, (tnum,))
            rowcount+=1
            for (comm, rate) in self.controller.cursor:
                rating=tk.Label(self, text=rate, borderwidth=1)
                comment=tk.Label(self, text=comm, borderwidth=1)
                rating.grid(row=rowcount, column=1, pady=5, padx=10)
                comment.grid(row=rowcount, column=2, pady=5, padx=10)
                self.widgets.append(rating)
                self.widgets.append(comment)
                rowcount+=1
            BACK = tk.Button(self, text="Back", command=lambda: self.goHome())
            BACK.grid(row=rowcount, column=0)
            self.widgets.append(BACK)
    def goHome(self):
        for w in self.widgets:
            w.grid_forget()
        self.createWidgets()
        self.controller.show_frame("ChooseFunctionality_Customer")


class StudentDiscount(tk.Frame):
    """
    Student Discount
    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='aliceblue')
        self.controller = controller
        self.createWidgets()

    def createWidgets(self):
        self.school_email_entry = self.make_entry("School Email Address: ", 40)
        self.school_email_entry.pack(pady=5)
        self.SUBMIT = tk.Button(self, text='Submit', command=lambda:self.submitEmail())

        self.BACK = tk.Button(self, text='Back', command=lambda:
            self.controller.show_frame("ChooseFunctionality_Customer"))
        self.BACK.pack(side = "bottom", pady = 10)

        self.SUBMIT.pack(side = "bottom", pady = 10)

    def make_entry(self, caption, width=None, **options):
        tk.Label(self, text=caption).pack()
        entry = tk.Entry(self, **options)
        if width:
            entry.config(width=width)
        return entry

    def submitEmail(self):
        email = self.school_email_entry.get()
        if email[-4:] == '.edu':
            tkmb.showinfo("Success!", "Student Discount Applied!")

            edit_student = ("UPDATE user_customer "
                       "SET is_student=1 "
                       "WHERE username=%s")

            self.controller.cursor.execute(edit_student, (self.controller.current_user,))
            self.controller.cnx.commit()

        else:
            tkmb.showerror("Error", "Invalid Student Email Address")

class ChooseFunctionality_Manager(tk.Frame):
    """
    Main Functionality Menu - Manager
    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='aliceblue')
        self.controller = controller
        self.createWidgets()

    def createWidgets(self):
        self.welcome = tk.Label(self, text="Choose Functionality")
        self.welcome.pack(pady=20)
        buttons = []
        self.trainSchedule = tk.Button(self, text="View Revenue Report", command=lambda:
            self.controller.show_frame("RevenueReport"))
        buttons.append(self.trainSchedule)
        self.newReservation = tk.Button(self, text="View Popular Route Report", command=lambda:
            self.controller.show_frame("PopularRouteReport"))
        buttons.append(self.newReservation)
        for i in range (0, len(buttons)):
            buttons[i].config(width=25)
            buttons[i].pack(pady=10) 
        self.LOGOUT = tk.Button(self, text='Log Out', command=lambda:
            self.controller.show_frame("HomePage"))
        self.LOGOUT.pack(side = "bottom", pady = 10)

class RevenueReport(tk.Frame):
    """
    Revenue Report
    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='aliceblue')
        self.controller = controller
        self.createWidgets()
    def createWidgets(self):
        rowcount=0
        self.welcome = tk.Label(self, text="Revenue Report")
        self.welcome.grid(row=rowcount, column=1, pady=20)
        rowcount+=1
        l1 = tk.Label(self, text="Month:")
        l1.grid(row=rowcount, column=0, pady=20, padx=20)
        l2 = tk.Label(self, text="Revenue:")
        l2.grid(row=rowcount, column=1, pady=20, padx=20)

        get_revenue = ("SELECT MONTH(departure_date) AS Month, SUM(total_cost) "
                    "FROM reserves NATURAL JOIN reservation WHERE MONTH(departure_date) >= MONTH(DATE_SUB(CURDATE(), INTERVAL 2 MONTH)) AND MONTH(departure_date) <= MONTH(CURDATE()) GROUP BY Month ")

        self.controller.cursor.execute(get_revenue)
        rowcount+=1
        months = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr',
                    5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 
                    9:'Sept', 10:'Oct', 11:'Nov', 12:'Dec'}
        for (mon, rev) in self.controller.cursor:
            mon_label = tk.Label(self, text=months[mon])
            rev_label = tk.Label(self, text='$'+str(rev))
            mon_label.grid(row=rowcount, column=0)
            rev_label.grid(row=rowcount, column=1)
            rowcount+=1
        BACK = tk.Button(self, text="Back", command=lambda:self.controller.show_frame("ChooseFunctionality_Manager"))
        BACK.grid(row=rowcount, column=1, padx=20, pady=20)

class PopularRouteReport(tk.Frame):
    """
    Popular Route Report
    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='aliceblue')
        self.controller = controller
        self.createWidgets()
    def createWidgets(self):
        rowcount=0
        self.welcome = tk.Label(self, text="Popular Route Report")
        self.welcome.grid(row=rowcount, column=1, pady=20, padx=20)
        rowcount+=1
        l1 = tk.Label(self, text="Month:")
        l1.grid(row=rowcount, column=0, pady=20, padx=20)
        l2 = tk.Label(self, text="Train Number:")
        l2.grid(row=rowcount, column=1, pady=20, padx=20)
        l3 = tk.Label(self, text="Reservations:")
        l3.grid(row=rowcount, column=2, pady=20, padx=20)


        get_popular1 = ("SELECT trainnumber, COUNT(reservationid) "
                        "FROM reserves NATURAL JOIN reservation "
                        "WHERE MONTH(departure_date) = MONTH(DATE_SUB(CURDATE(), INTERVAL 2 MONTH)) AND reservation.is_cancelled = 0 "
                        "GROUP BY trainnumber "
                        "ORDER BY COUNT(reservationid) DESC "
                        "LIMIT 3")
        get_popular2 = ("SELECT trainnumber, COUNT(reservationid) "
                        "FROM reserves NATURAL JOIN reservation "
                        "WHERE MONTH(departure_date) = MONTH(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)) AND reservation.is_cancelled = 0 "
                        "GROUP BY trainnumber "
                        "ORDER BY COUNT(reservationid) DESC "
                        "LIMIT 3")
        get_popular3 = ("SELECT trainnumber, COUNT(reservationid) "
                        "FROM reserves NATURAL JOIN reservation "
                        "WHERE MONTH(departure_date) = MONTH(CURDATE()) AND reservation.is_cancelled = 0 "
                        "GROUP BY trainnumber "
                        "ORDER BY COUNT(reservationid) DESC "
                        "LIMIT 3")
        #get_popular2 = ("SELECT * FROM get_popular2")
        months = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr',
                    5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 
                    9:'Sept', 10:'Oct', 11:'Nov', 12:'Dec'}
        current_month = datetime.datetime.now().month-2
        self.controller.cursor.execute(get_popular1)
        rowcount+=1
        for (rev, tn) in self.controller.cursor:
            mon_label = tk.Label(self, text=months[current_month])
            rev_label = tk.Label(self, text= str(rev))
            tn_label = tk.Label(self, text=tn)
            mon_label.grid(row=rowcount, column=0, padx=20, pady=20)
            rev_label.grid(row=rowcount, column=1, padx=20, pady=20)
            tn_label.grid(row=rowcount, column=2, padx=20, pady=20)
            rowcount+=1
        self.controller.cursor.execute(get_popular2)
        current_month+=1
        for (rev, tn) in self.controller.cursor:
            mon_label = tk.Label(self, text=months[current_month])
            rev_label = tk.Label(self, text= str(rev))
            tn_label = tk.Label(self, text=tn)
            mon_label.grid(row=rowcount, column=0, padx=20, pady=20)
            rev_label.grid(row=rowcount, column=1, padx=20, pady=20)
            tn_label.grid(row=rowcount, column=2, padx=20, pady=20)
            rowcount+=1
        self.controller.cursor.execute(get_popular3)
        current_month+=1
        for (rev, tn) in self.controller.cursor:
            mon_label = tk.Label(self, text=months[current_month])
            rev_label = tk.Label(self, text= str(rev))
            tn_label = tk.Label(self, text=tn)
            mon_label.grid(row=rowcount, column=0, padx=20, pady=20)
            rev_label.grid(row=rowcount, column=1, padx=20, pady=20)
            tn_label.grid(row=rowcount, column=2, padx=20, pady=20)
            rowcount+=1
        
        BACK = tk.Button(self, text="Back", command=lambda:self.controller.show_frame("ChooseFunctionality_Manager"))
        BACK.grid(row=rowcount, column=1, padx=20, pady=20)

        

# Main
if __name__ == '__main__':
    app = App()
    app.title("GT Train")
    app.mainloop()
    app.cursor.close()
    app.cnx.close()