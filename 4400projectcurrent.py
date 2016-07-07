import Tkinter as tk
import tkMessageBox as tkmb
import datetime
import mysql.connector
import tkFont
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
        default_font.configure(size=10, family='Arial')

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.cnx = mysql.connector.connect(user='root', password='cs4400password',
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
        for F in (HomePage, SignIn, CreateUser, ChooseFunctionality_Customer, StudentDiscount, TrainSchedule,
            MakeReservation, UpdateReservation, CancelReservation, GiveReview, ViewReview):
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
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg='aliceblue')
        self.welcome = tk.Label(self, text= "Welcome", font=("arial",15), bg='aliceblue')
        self.welcome.grid(pady=20, padx=120)
        self.sign_in = tk.Button(self, text = 'Sign In', command=lambda: controller.show_frame("SignIn"), bg='white')
        self.sign_in.grid(pady=5, padx=120)
        self.create_new_user = tk.Button(self, text = 'Create New User', command=lambda: controller.show_frame("CreateUser"), bg='white')
        self.create_new_user.grid(pady=5, padx=120)
        # DEBUG
        self.debug = tk.Label(self, text="DEBUG:")
        self.debug.grid(pady=10)
        self.quick_login = tk.Button(self, text="Quick Login", command=lambda: self.quickLogin(), bg='white')
        self.quick_login.grid()
        self.print_db_button = tk.Button(self, text='Print Database', command=self.print_db, bg='white')
        self.print_db_button.grid()

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
        self.current_user = "customer00"
        print "Logged in as", self.current_user
        self.controller.show_frame("ChooseFunctionality_Customer")



class SignIn(tk.Frame):
    """
    Sign In
    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg="aliceblue")
        self.createWidgets()

    def createWidgets(self):
        self.login_text = tk.Label(self, text="Log In", font=('arial', 15), bg='aliceblue')
        self.login_text.grid(pady=20, columnspan=2)
        self.user_entry = self.make_entry("Username", 30)
        self.user_entry.grid(padx=10, column=1, row=1)
        self.password_entry = self.make_entry("Password", 30, show='*')
        self.password_entry.grid(pady=10, padx=10, column=1, row=2)
        self.SIGNIN = tk.Button(self, text='Log In', command=self.log_in, bg='white')
        self.BACK = tk.Button(self, text='Back', command=lambda: self.controller.show_frame("HomePage"), bg='white')
        self.SIGNIN.grid(pady = 10, columnspan=2)
        self.BACK.grid(columnspan=2)

    def make_entry(self, caption, width=None, **options):
        tk.Label(self, text=caption, bg='aliceblue').grid()
        entry = tk.Entry(self, **options)
        if width:
            entry.config(width=width)
        return entry

    def log_in(self):
        user = self.user_entry.get()
        password = self.password_entry.get()
        get_users = ("SELECT * from user")
        self.controller.cursor.execute(get_users)
        userExists = False;
        login_success = False;
        for (uname, pword) in self.controller.cursor:
            if uname==user:
                userExists = True;
                if pword==password:
                    login_success = True;
                else:
                    tkmb.showerror("Error", "Password is incorrect.")
        if not userExists:
                tkmb.showerror("Error", "Username not in database.")
        if login_success:
            self.controller.cnx = mysql.connector.connect(user=user, password=password,
                host='localhost', database='gt_train')
            self.controller.cursor = self.controller.cnx.cursor()
            self.current_user = user
            self.controller.show_frame("ChooseFunctionality_Customer")


class CreateUser(tk.Frame):
    """
    Create User
    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg='aliceblue')
        self.createWidgets()

    def make_entry(self, caption, width=None, **options):
        tk.Label(self, text=caption, bg='aliceblue').grid(column=0)
        entry = tk.Entry(self, **options)
        if width:
            entry.config(width=width)
        return entry

    def createWidgets(self):
        self.login_text = tk.Label(self, text="Create Account", font=('arial', 15), bg='aliceblue')
        self.login_text.grid(pady=10, columnspan=2)
        entries = []
        self.user_entry = self.make_entry("Username", 30)
        self.user_entry.grid(pady=5, column=1, row=1, padx=5)
        self.user_label = tk.Label(self, text="Can only contain letters, numbers, and underscores", font=('arial',7), bg='aliceblue')
        self.user_label.grid(columnspan=2, row=2)
        self.email_entry = self.make_entry("Email", 30)
        self.email_entry.grid(pady=5, column=1, row=3, padx=5)
        self.password_entry = self.make_entry("Password", 30, show='*')
        self.password_entry.grid(pady=5, column=1, row=4, padx=5)
        self.user_label = tk.Label(self, text="Must be at least 5 characters and contain at least 1 number", font=('arial',7), bg='aliceblue')
        self.user_label.grid(row=5, columnspan=2)
        self.confirm_password_entry = self.make_entry("Confirm Password", 30, show='*')
        self.confirm_password_entry.grid(pady=5, row=6, column=1, padx=5)
        self.CREATE = tk.Button(self, bg='white')
        self.CREATE["text"] = "Create",
        self.CREATE["command"] = self.create_user
        self.BACK = tk.Button(self, text='Back', command=lambda: self.controller.show_frame("HomePage"), bg='white')
        self.CREATE.grid(pady = 10, columnspan=2)
        self.BACK.grid(pady = 10, columnspan=2)


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
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.createWidgets()
        self.config(bg='aliceblue')

    def createWidgets(self):
        buttons = []
        self.trainSchedule = tk.Button(self, text="View Train Schedule", bg='white', command=lambda:
            self.controller.show_frame("TrainSchedule"))
        buttons.append(self.trainSchedule)
        self.newReservation = tk.Button(self, text="Make a New Reservation", bg='white', command=lambda:
            self.controller.show_frame("MakeReservation"))
        buttons.append(self.newReservation)
        self.updateReservation = tk.Button(self, text="Update Reservation", bg='white', command=lambda:
            self.controller.show_frame("UpdateReservation"))
        buttons.append(self.updateReservation)
        self.cancelReservation = tk.Button(self, text="Cancel Reservation", bg='white', command=lambda:
            self.controller.show_frame("CancelReservation"))
        buttons.append(self.cancelReservation)
        self.reviewButton = tk.Button(self, text="Reviews", bg='white', command=lambda:
            self.controller.show_frame("ViewReview"))
        buttons.append(self.reviewButton)
        # self.viewReview = tk.Button(self, text="View a Review", command=lambda:
        #     self.controller.show_frame("ViewReview"))
        # buttons.append(self.viewReview)
        self.studentInfo = tk.Button(self, text="Student Discount Information", bg='white', command=lambda:
            self.controller.show_frame("StudentDiscount"))
        buttons.append(self.studentInfo)
        self.paymentInfo = tk.Button(self, text="Payment Information", bg='white', command=lambda:
            self.controller.show_frame("PaymentDiscount"))
        for i in range (0, len(buttons)):
            buttons[i].config(width=25)
            buttons[i].pack(pady=10)
        self.LOGOUT = tk.Button(self, text='Log Out', bg='white', command=lambda:
            self.controller.show_frame("HomePage"))
        self.LOGOUT.pack(side = "bottom", pady = 10)


class TrainSchedule(tk.Frame):
    """
    Select Train & Train Schedule
    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.createWidgets()
        self.config(bg='aliceblue')
    def createWidgets(self):
        self.welcome = tk.Label(self, text= "Select Train Number", bg='aliceblue', font=('arial', 15))
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
        self.select_train.config(bg='white')
        self.select_train.pack()
        self.go = tk.Button(self, text='Go', command=lambda:
            self.selectTrain(), bg='white')
        self.go.pack(side = "bottom", pady = 10)
        self.BACK = tk.Button(self, text='Back', command=lambda:
            self.controller.show_frame("ChooseFunctionality_Customer"), bg='white')
        self.BACK.pack(side = "bottom", pady = 10)
        self.go.pack(side = "bottom", pady = 10)

    def createNewWidgets(self, selector):
        self.welcome = tk.Label(self, text= "Train Schedule")
        self.welcome.grid(row=0, column=1, pady=20)
        trainlabel = "#" + selector
        self.train_number = tk.Label(self, text=trainlabel, bg='white')
        self.train_number.grid(row=0, column=2, pady=20)

        self.station_label = tk.Label(self, text="Station")
        self.station_label.grid(row=1, column=0, pady=10)
        self.location_label = tk.Label(self, text="Location")
        self.location_label.grid(row=1, column=1, pady=10)
        self.arr_label = tk.Label(self, text="Arrival Time")
        self.arr_label.grid(row=1, column=2, pady=10)
        self.dep_label = tk.Label(self, text="Departure Time")
        self.dep_label.grid(row=1, column=3, pady=10)

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
            rowcount+=1

        self.BACK = tk.Button(self, text='Back', command=lambda:
            self.controller.show_frame("ChooseFunctionality_Customer"))
        self.BACK.grid(row=rowcount, pady = 20)

    def selectTrain(self):
        get_stops = ("SELECT * FROM stop "
                    "WHERE trainnumber=%s "
                    "ORDER BY arrival_time ASC")
        selector = self.optionVar.get()
        self.controller.cursor.execute(get_stops, (str(selector),))

        # Delete old widgets
        self.welcome.pack_forget()
        self.select_train.pack_forget()
        self.go.pack_forget()
        self.BACK.pack_forget()

        # Create new widgets
        self.createNewWidgets(selector)


class MakeReservation(tk.Frame):
    """
    Make Reservation
    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.ticketArray = []
        self.createWidgets()
        self.config(bg='aliceblue')

    def createWidgets(self):
        # Had to do pack here instead of grid on this screen b/c of Date widget

        self.welcome = tk.Label(self, text= "Make Reservation", bg='aliceblue', font=('arial', 15))
        self.welcome.pack(pady=20)

        options = []
        for key in self.controller.station_dict:
            options.append(self.controller.station_dict[key])
        self.departsVar = tk.StringVar(self)
        self.departsVar.set("Departs From")
        self.arrivesVar = tk.StringVar(self)
        self.arrivesVar.set("Arrives At")
        self.select_departsFrom = apply(tk.OptionMenu, (self, self.departsVar) + tuple(options))
        self.select_departsFrom.config(bg='white')
        self.select_departsFrom.pack(pady=5, padx=20)
        self.select_arrivesAt = apply(tk.OptionMenu, (self, self.arrivesVar) + tuple(options))
        self.select_arrivesAt.config(bg='white')
        self.select_arrivesAt.pack(pady=5, padx=20)


        self.date_entry = tk.Frame(self)
        self.date_entry.config(bg='aliceblue')
        self.date_label = tk.Label(self.date_entry, text='Date', bg='aliceblue')
        self.date_entry_1 = tk.Entry(self.date_entry, width=2)
        self.label_1 = tk.Label(self.date_entry, text='/', bg='aliceblue')
        self.date_entry_2 = tk.Entry(self.date_entry, width=2)
        self.label_2 = tk.Label(self.date_entry, text='/', bg='aliceblue')
        self.date_entry_3 = tk.Entry(self.date_entry, width=4)

        self.date_label.pack(side=tk.LEFT, pady=10, padx=5)
        self.date_entry_1.pack(side=tk.LEFT)
        self.label_1.pack(side=tk.LEFT)
        self.date_entry_2.pack(side=tk.LEFT)
        self.label_2.pack(side=tk.LEFT)
        self.date_entry_3.pack(side=tk.LEFT)
        self.date_entry.pack()

        self.GO = tk.Button(self, text='Find Trains', bg='white', command=lambda:
            self.verifyEntries())
        self.GO.pack(pady = 10)
        self.BACK = tk.Button(self, text='Back', command=lambda:
            self.controller.show_frame("ChooseFunctionality_Customer"))
        self.BACK.pack(side=tk.BOTTOM, pady = 10)

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
        if int(yyyy) == int(curr_yr) and int(mm) == int(curr_yr) and int(dd) < int(curr_day):
            verified = False
            tkmb.showerror("Error", inthepast)
        elif int(yyyy) == int(curr_yr) and int(mm) == int(curr_yr) and int(dd) == int(curr_day):
            verified = False
            tkmb.showerror("Sorry", "You cannot purchase tickets the day of the trip.")

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
        self.forgetReservationScreen()

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
                self.ticket_dictionary[tid]=(tnum, fc_price, "First Class", route_string, time_string, date_string)
                tid+=1
                p2selector = tk.Radiobutton(f_price2, variable=self.ticketID, value=tid)
                self.ticket_dictionary[tid]=(tnum, sc_price, "Second Class", route_string, time_string, date_string)
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
            self.GO = tk.Button(self, text="Next", command=lambda:self.passengerInfo())
            self.GO.grid(row=rowcount, column=2)
            self.BACK = tk.Button(self, text="Back", command=lambda:self.goBack())
            self.BACK.grid(row=rowcount, column=1)
        else:
            tkmb.showerror("Sorry", "There is no direct route to your destination")
            self.createWidgets()
    def goBack(self):
        # Forget findTrains screen
        self.welcome.grid_forget()
        self.route_label.grid_forget()
        self.date_label.grid_forget()
        self.tnum_label.grid_forget()
        self.time_label.grid_forget()
        self.class1_label.grid_forget()
        self.class2_label.grid_forget()
        for rb in self.radiobuttons:
            rb.pack_forget()
        for (c1, c2, c3, c4) in self.cols:
            c1.grid_forget()
            c2.grid_forget()
            c3.pack_forget()
            c4.pack_forget()
        for f in self.subFrames:
            f.grid_forget()
        self.GO.grid_forget()
        self.BACK.grid_forget()
        # Redraw original Reservation screen
        self.createWidgets()
    def passengerInfo(self):
        # Forget findTrains screen
        self.welcome.grid_forget()
        self.route_label.grid_forget()
        self.date_label.grid_forget()
        self.tnum_label.grid_forget()
        self.time_label.grid_forget()
        self.class1_label.grid_forget()
        self.class2_label.grid_forget()
        for rb in self.radiobuttons:
            rb.pack_forget()
        for (c1, c2, c3, c4) in self.cols:
            c1.grid_forget()
            c2.grid_forget()
            c3.pack_forget()
            c4.pack_forget()
        for f in self.subFrames:
            f.grid_forget()
        self.GO.grid_forget()
        self.BACK.grid_forget()
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
        if len(name)==0:
            tkmb.showerror("Error", "You have to enter a name")
        else:
            self.forgetPassengerInfo()
            # Get info for current ticket
            train_number, t_price, t_class, t_route, t_time, t_date = self.ticket_dictionary[self.ticketID.get()]
            p_name, p_bags = (self.name_entry.get(), self.baggageVar.get())
            newTicket = (train_number, t_date, t_time, t_route, t_class, t_price, p_bags, p_name)
            self.ticketArray.append(newTicket)
            # Draw stuff
            self.widgets = []
            rowcount=0
            self.selected_label = tk.Label(self, text="Currently Selected:")
            self.selected_label.grid(row=rowcount, column=0, pady=10)
            self.widgets.append(self.selected_label)
            rowcount+=1
            self.train_label = tk.Label(self, text="Train")
            self.train_label.grid(row=rowcount, column=0, pady=5)
            self.widgets.append(self.train_label)
            self.time_label = tk.Label(self, text="Time")
            self.time_label.grid(row=rowcount, column=1, pady=5)
            self.widgets.append(self.time_label)
            self.route_label = tk.Label(self, text="Route")
            self.route_label.grid(row=rowcount, column=2, pady=5)
            self.widgets.append(self.route_label)
            self.class_label = tk.Label(self, text="Class")
            self.class_label.grid(row=rowcount, column=3, pady=5)
            self.widgets.append(self.class_label)
            self.price_label = tk.Label(self, text="Price")
            self.price_label.grid(row=rowcount, column=4, pady=5)
            self.widgets.append(self.price_label)
            self.bag_label = tk.Label(self, text="# Bags")
            self.bag_label.grid(row=rowcount, column=5, pady=5)
            self.widgets.append(self.bag_label)
            self.name_label = tk.Label(self, text="Passenger Name")
            self.name_label.grid(row=rowcount, column=6, pady=5)
            self.widgets.append(self.name_label)
            rowcount+=1
            totalPrice=0
            for tick in self.ticketArray:
                t_n, t_d, t_t, t_r, t_c, t_p, p_b, p_n = tick
                train_label = tk.Label(self, text=t_n)
                train_label.grid(row=rowcount, column=0, pady=5, padx=5)
                self.widgets.append(train_label)
                time_label = tk.Label(self, text=t_d + "\n" + t_t)
                time_label.grid(row=rowcount, column=1, pady=5, padx=5)
                self.widgets.append(time_label)
                route_label = tk.Label(self, text=t_r)
                route_label.grid(row=rowcount, column=2, pady=5, padx=5)
                self.widgets.append(route_label)
                class_label = tk.Label(self, text=t_c)
                class_label.grid(row=rowcount, column=3, pady=5, padx=5)
                self.widgets.append(class_label)
                price_label = tk.Label(self, text=t_p)
                price_label.grid(row=rowcount, column=4, pady=5, padx=5)
                self.widgets.append(price_label)
                bag_label = tk.Label(self, text=p_b)
                bag_label.grid(row=rowcount, column=5, pady=5, padx=5)
                self.widgets.append(bag_label)
                name_label = tk.Label(self, text=p_n)
                name_label.grid(row=rowcount, column=6, pady=5, padx=5)
                self.widgets.append(name_label)
                remove_button = tk.Button(self, text="Remove")
                remove_button.grid(row=rowcount, column=7, pady=5, padx=10)
                self.widgets.append(remove_button)
                rowcount+=1
                totalPrice+=t_p

            self.cost_label = tk.Label(self, text='Total Cost:')
            self.cost_label.grid(row=rowcount, column=0, pady=10)
            self.widgets.append(self.cost_label)
            self.cost = tk.Label(self, text='$'+str(totalPrice))
            self.cost.grid(row=rowcount, column=1, pady=10)
            self.widgets.append(self.cost)
            rowcount+=1
            self.card_label = tk.Label(self, text='Use Card:')
            self.card_label.grid(row=rowcount, column=0, pady=10)
            self.widgets.append(self.card_label)
            rowcount+=1
            self.another_train = tk.Button(self, text="Add Another Train", command=lambda:self.addAnotherTrain())
            self.another_train.grid(row=rowcount, column=0, pady=10)
            self.widgets.append(self.another_train)
            rowcount+=1
            self.GO = tk.Button(self, text="Next", command=lambda:self.addTicket())
            self.GO.grid(row=rowcount, column=6, pady=10)
            self.widgets.append(self.GO)
            self.BACK = tk.Button(self, text="Back", command=lambda:self.goBack())
            self.BACK.grid(row=rowcount, column=1, pady=10)
            self.widgets.append(self.BACK)
    def addAnotherTrain(self):
        for w in self.widgets:
            w.grid_forget()
        self.createWidgets()



class UpdateReservation(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.createWidgets()
        self.config(bg='aliceblue')
    def createWidgets(self):
        self.welcome = tk.Label(self, text= "Update Reservation", font=('arial',15), bg='aliceblue')
        self.welcome.pack(pady=50)

        "TODO"

        self.BACK = tk.Button(self, text='Back', bg='white', command=lambda:
            self.controller.show_frame("ChooseFunctionality_Customer"))
        self.BACK.pack(side = "bottom", pady = 10)


class CancelReservation(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.createWidgets()
        self.config(bg='aliceblue')

    def createWidgets(self):
        self.welcome = tk.Label(self, text= "Cancel Reservation", bg='aliceblue', font=('arial', 15))
        self.welcome.pack(pady=20)

        "TODO"

        self.BACK = tk.Button(self, text='Back', command=lambda:
            self.controller.show_frame("ChooseFunctionality_Customer"), bg='white')
        self.BACK.pack(side = "bottom", pady = 10)

class GiveReview(tk.Frame):
    """
    Give Review
    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.createWidgets()
        self.config(bg='aliceblue')

    def createWidgets(self):
        self.welcome = tk.Label(self, text= "Give A Review", font=('arial',15), bg='aliceblue')
        self.welcome.pack(pady=20)

        "TODO"

        self.BACK = tk.Button(self, text='Back', bg='white', command=lambda:
            self.controller.show_frame("ChooseFunctionality_Customer"))
        self.BACK.pack(side = "bottom", pady = 10)

class ViewReview(tk.Frame):
    """
    View Review
    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.createWidgets()
        self.config(bg='aliceblue')

    def createWidgets(self):
        self.welcome = tk.Label(self, text= "Reviews", font=('arial',15), bg='aliceblue')
        self.welcome.pack(pady=50)

        "TODO"

        self.giveAReview = tk.Button(self, text='Give A Review', bg='white', command=lambda:
            self.controller.show_frame("GiveReview"))
        self.giveAReview.pack(pady = 10)

        self.BACK = tk.Button(self, text='Back', bg='white', command=lambda:
            self.controller.show_frame("ChooseFunctionality_Customer"))
        self.BACK.pack(side = "bottom", pady = 10)



class StudentDiscount(tk.Frame):
    """
    Student Discount
    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.createWidgets()
        self.config(bg='aliceblue')

    def createWidgets(self):
        self.school_email_entry = self.make_entry("School Email Address", 30)
        self.school_email_entry.pack()
        self.edu = tk.Label(self, text="Must end in '.edu'", bg='aliceblue', font=('arial', 7))
        self.edu.pack()
        self.SUBMIT = tk.Button(self, text='Submit', command=lambda:self.submitEmail(), bg='white')
        self.BACK = tk.Button(self, text='Back', bg='white', command=lambda:
            self.controller.show_frame("ChooseFunctionality_Customer"))
        self.SUBMIT.pack(pady = 10)
        self.BACK.pack(pady = 10)


    def make_entry(self, caption, width=None, **options):
        tk.Label(self, text=caption, bg="aliceblue").pack(pady=20)
        entry = tk.Entry(self, **options)
        if width:
            entry.config(width=width)
        return entry

    def submitEmail(self):
        email = self.school_email_entry.get()
        if email[-4:] == '.edu':
            tkmb.showinfo("Success!", "Student Discount Applied!")

            "TODO - Actually apply student discount in db"

            # edit_student = ("UPDATE user_customer"
            #            "SET is_student=1"
            #            "WHERE username=%s") %self.controller.current_user
            # # student_name = (self.current_user, password)
            # self.controller.cursor.execute(edit_student)
            # self.controller.cnx.commit()

        else:
            tkmb.showerror("Error", "Invalid Student Email Address")



# Main
if __name__ == '__main__':
    app = App()
    app.title("GT Train")
    app.mainloop()
    app.cursor.close()
    app.cnx.close()