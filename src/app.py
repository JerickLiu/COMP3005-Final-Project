from psycopg2 import connect, Error
import sys
from Functions import Functions
from menu import Menu
from datetime import datetime

db = {}

def register_user():
    try:
        # Establish database connection
        conn = connect(**db)
        cur = conn.cursor()

        Functions.clearScreen("Register")

        print("\nNOTE: If you are trying to register a trainer or admin account, please speak with your representative.\n")

        # Collect user information
        username = input("Enter username: ")
        password = input("Enter password: ")
        email = input("Enter email: ")
        first_name = input("Enter first name: ")
        last_name = input("Enter last name: ")
        fitness_goals = input("Enter fitness goals: ")
        exercise = input("Enter exercise routine: ")
        blood = input("Enter blood pressure: ")
        weight = Functions.loopTillValid("Enter weight (kg): ", "integer", False)
        height = Functions.loopTillValid("Enter height (cm): ", "integer", False)

        # Insert into Users table
        cur.execute("""
            INSERT INTO "Users" (username, password, email, user_type) 
            VALUES (%s, %s, %s, 'member') RETURNING user_id
        """, (username, password, email))
        user_id = cur.fetchone()[0]

        # Insert into Members table
        cur.execute("""
            INSERT INTO "Members" (user_id, first_name, last_name, fitness_goals, exercise, balance) 
            VALUES (%s, %s, %s, %s, %s, 0, 0)
        """, (user_id, first_name, last_name, fitness_goals, exercise))

        # Get the generated member_id for health metrics
        cur.execute("SELECT member_id FROM \"Members\" WHERE user_id = %s", (user_id,))
        member_id = cur.fetchone()[0]

        # Insert into Health table
        cur.execute("""
            INSERT INTO "Health" (member_id, blood, weight, height) 
            VALUES (%s, %s, %s, %s)
        """, (member_id, blood, weight, height))

        conn.commit()
        print("You have successfully registered!")

        Functions.enterToContinue()

    except Exception as e:
        print("Registration failed: " + str(e))
        Functions.enterToContinue()
        conn.rollback()

    finally:
        cur.close()
        conn.close()

def login():

    Functions.clearScreen("Health and Fitness Management System Login")
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    conn = connect(**db)
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM \"Users\" WHERE username = %s AND password = %s", (username, password))
        
        if r:= cur.fetchone():
            match r[4]:
                case "admin":
                    admin_page()
                case "member":
                    member_page(r[0])
                case "trainer":
                    trainer_page(r[0])

            return True
        else:
            print("Invalid username or password")
            Functions.enterToContinue()
            return False
    finally:
        cur.close()
        conn.close()

def admin_page():
    conn = connect(**db)
    cur = conn.cursor()
    
    exit = False

    while not exit:

        Functions.clearScreen("Admin Dashboard")

        # Populate events listbox
        cur.execute("SELECT * FROM \"Classes\"")
        events = cur.fetchall()
        print("\nUpcoming Classes:")
        if events:
            for event in events:
                # Fetch the trainer name and room using the trainer ID and room ID
                cur.execute("""
                SELECT u.username 
                FROM "Users" u
                JOIN "Trainers" t ON u.user_id = t.user_id
                WHERE t.trainer_id = %s
                """, (event[4],))
                trainer_name = cur.fetchone()[0]
                cur.execute("SELECT room_type FROM \"Rooms\" WHERE room_id = %s", (event[5],))
                room_name = cur.fetchone()[0]

                # Count the number of members attending the event
                cur.execute("SELECT COUNT(*) FROM \"ClassQueue\" WHERE event_id = %s", (event[0],))
                member_count = cur.fetchone()[0]

                print(f"{event[1]}\n\t Trainer: {trainer_name}\n\t Date: {event[2]}\n\t Description: {event[3]}\n\t Current Attendance: {member_count}.")
        else:
            print("There are no scheduled Classes.")

        print("\nRooms:")
        # Populate rooms listbox
        cur.execute("SELECT room_id, room_type FROM \"Rooms\" ORDER BY room_id")
        rooms = cur.fetchall()
        for room in rooms:
            print(f"{room[1]} (ID: {room[0]})")

        # Query database for first name, last name, and billing info from all members
        cur.execute("""
        SELECT m.user_id, m.first_name, m.last_name, m.balance
        FROM "Members" m
        """)
        balances = cur.fetchall()

        print("\nMember Balances:")
        for balance in balances:
            print(f"{balance[1]} {balance[2]} (ID: {balance[0]}): ${balance[3]:,.2f}")
        
        adminChoice = Menu("", "Process Member Payment", "Manage Rooms", "Schedule new Event", "Update Event Time", "Delete an Event", "Logout").menu(False)

        match adminChoice:
            case "1":
                process_payments(conn)
            case "2":
                manage_rooms(conn)
            case "3":
                scheduleEvent(conn)
            case "4":
                update_event_time(conn)
            case "5":
                delete_event(conn)
            case "6":
                exit = True


    cur.close()
    conn.close()

from decimal import Decimal as float
def process_payments(conn):
    cur = conn.cursor()

    try:
        # Display all members with outstanding fees
        cur.execute("""
            SELECT member_id, first_name || ' ' || last_name AS full_name, balance
            FROM "Members"
            WHERE balance > 0
        """)
        outstanding_fees = cur.fetchall()

        if not outstanding_fees:
            print("No outstanding fees to process.")
            Functions.enterToContinue()
            return

        print("\nMembers with Outstanding Fees:")
        for idx, fee in enumerate(outstanding_fees):
            print(f"{idx + 1}. {fee[1]}, Owed: ${fee[2]:.2f}")

        # Select a member to process payment
        member_number = int(input("\nEnter the number of the member to process payment for: ")) - 1
        if member_number < 0 or member_number >= len(outstanding_fees):
            return

        member_id = outstanding_fees[member_number][0]
        amount_paid = float(input("Enter the amount being paid: "))

        # Process the payment
        cur.execute("""
            UPDATE "Members"
            SET balance = balance - %s
            WHERE member_id = %s
        """, (amount_paid, member_id))

        conn.commit()
        print("Payment processed successfully.")
        Functions.enterToContinue()

    except Exception as e:
        print(f"An error occurred: {e}")
        Functions.enterToContinue()
        conn.rollback()
    finally:
        cur.close()

def manage_rooms(conn):
    cur = conn.cursor()

    try:
        # Display current maintenance of all rooms
        cur.execute("SELECT * FROM \"Rooms\"")
        rooms = cur.fetchall()

        print("\nCurrent Room Maintenance:")
        for idx, room in enumerate(rooms):
            print(f"{idx + 1}. {room[1]}\n\tMaintenance: {room[2]}")

        # Select a room to update status
        room_number = int(input("\nEnter the number of the room to update the maintenance for: ")) - 1
        if room_number < 0 or room_number >= len(rooms):
            print("Invalid selection.")
            return

        room_id = rooms[room_number][0]
        new_status = input("Enter new status for the room: ")

        # Update the status of the selected room
        cur.execute("""
            UPDATE "Rooms"
            SET maintenance = %s
            WHERE room_id = %s
        """, (new_status, room_id))

        conn.commit()
        print("Room maintenance updated successfully.")
        Functions.enterToContinue()

    except Exception as e:
        print(f"An error occurred: {e}")
        Functions.enterToContinue()
        conn.rollback()
    finally:
        cur.close()

# Create a class as an admin
def scheduleEvent(conn):
    cur = conn.cursor()

    try:
        # Get event details from admin input
        event_name = input("Enter event name: ")
        print("Enter event date:")
        year = Functions.loopTillValid("Year (YYYY): ", "integer", False)
        month = Functions.loopTillValid("Month (MM): ", "integer", False)
        day = Functions.loopTillValid("Day (DD): ", "integer", False)
        hour = Functions.loopTillValid("Hour (HH, 24-hour format): ", "integer", False)
        minute = Functions.loopTillValid("Minute (mm): ", "integer", False)
        second = Functions.loopTillValid("Second (ss): ", "integer", False)
        new_date = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
        event_date = new_date.strftime('%Y-%m-%d %H:%M:%S')
        event_description = input("Enter event description: ")
        trainer_id = input("Enter trainer ID: ")
        room_id = input("Enter room ID: ")

        # Start a transaction
        cur.execute("BEGIN;")

        # Check for trainer availability on the given date
        cur.execute("""
            SELECT date_id FROM "Dates"
            WHERE trainer_id = %s AND availability = %s
        """, (trainer_id, event_date))
        availability = cur.fetchone()

        if availability is None:
            print("Error: Trainer is not available on this date.")
            Functions.enterToContinue()
            cur.execute("ROLLBACK;")
            return
        
        else:
            date_id = availability[0]

            # Insert the new group event
            cur.execute("""
                INSERT INTO "Classes"
                (event_name, event_date, event_description, trainer_id, room_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (event_name, event_date, event_description, trainer_id, room_id))

            # Delete the matched availability
            cur.execute("""
                DELETE FROM "Dates"
                WHERE date_id = %s
            """, (date_id,))

            # Commit the transaction
            cur.execute("COMMIT;")
            print("Success: Event created and trainer availability updated.")
            Functions.enterToContinue()

    except Error as e:
        print("An error occurred: ", e)
        Functions.enterToContinue()
        cur.execute("ROLLBACK;")
    finally:
        cur.close()

# Delete a group event as an admin
def delete_event(conn):

    cur = conn.cursor()

    try:
        # Display all current events
        cur.execute("""
            SELECT event_id, event_name, event_date, event_description FROM "Classes"
        """)
        events = cur.fetchall()

        if not events:
            print("No events available to delete.")
            Functions.enterToContinue()
            return

        print("\nCurrent Classes:")
        for event in events:
            print(f"Event ID: {event[0]}, Name: {event[1]}, Date: {event[2]}, Description: {event[3]}")

        # Ask the admin which event to delete
        event_id_to_delete = input("Enter the Event ID of the event you wish to delete: ")

        # Validate input
        if not any(event[0] == int(event_id_to_delete) for event in events):
            print("Invalid Event ID.")
            return

        # Delete the selected event
        cur.execute("""
            DELETE FROM "Classes"
            WHERE event_id = %s
        """, (event_id_to_delete,))
        conn.commit()
        print(f"Event with ID {event_id_to_delete} has been deleted successfully.")
        Functions.enterToContinue()

    except Exception as e:
        print(f"An error occurred: {e}")
        Functions.enterToContinue()
        conn.rollback()
    finally:
        cur.close()

def update_event_time(conn):
    cur = conn.cursor()

    try:
        # Display all current events
        cur.execute("""
            SELECT event_id, event_name, event_date, trainer_id FROM "Classes"
        """)
        events = cur.fetchall()

        if not events:
            print("No events available to update.")
            Functions.enterToContinue()
            return

        print("\nCurrent Classes:")
        for event in events:
            print(f"Event ID: {event[0]}, Name: {event[1]}, Date: {event[2]}")

        # Ask the admin which event to update
        event_id_to_update = input("Enter the Event ID of the event you wish to update the time for: ")

        # Find the selected event
        selected_event = next((event for event in events if str(event[0]) == event_id_to_update), None)
        if not selected_event:
            return

        # Get new event time from admin
        print("Enter new event date:")
        year = Functions.loopTillValid("Year (YYYY): ", "integer", False)
        month = Functions.loopTillValid("Month (MM): ", "integer", False)
        day = Functions.loopTillValid("Day (DD): ", "integer", False)
        hour = Functions.loopTillValid("Hour (HH, 24-hour format): ", "integer", False)
        minute = Functions.loopTillValid("Minute (mm): ", "integer", False)
        second = Functions.loopTillValid("Second (ss): ", "integer", False)
        new_date = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
        new_time = new_date.strftime('%Y-%m-%d %H:%M:%S')

        # Check if the trainer is available at the new time
        cur.execute("""
            SELECT date_id FROM "Dates"
            WHERE trainer_id = %s AND availability = %s
        """, (selected_event[3], new_time))
        availability = cur.fetchone()

        if not availability:
            print("Trainer is not available at the new time.")
            Functions.enterToContinue()
            return

        # Update the event time
        cur.execute("""
            UPDATE "Classes"
            SET event_date = %s
            WHERE event_id = %s
        """, (new_time, event_id_to_update))
        conn.commit()
        print(f"Event time updated successfully to {new_time}.")

        Functions.enterToContinue()

    except Exception as e:
        print(f"An error occurred: {e}")
        Functions.enterToContinue()
        conn.rollback()
    finally:
        cur.close()

def member_page(user_id):
    conn = connect(**db)

    cur = conn.cursor()
    cur.execute("SELECT member_id FROM \"Members\" WHERE user_id = %s", (user_id,))
    member_id = cur.fetchone()[0]
    exit = False

    while not exit:
        cur.execute("SELECT * FROM \"Members\" WHERE member_id = %s", (member_id,))
        member_details = cur.fetchone()

        Functions.clearScreen(f"{member_details[2]}'s Profile")

        labels = ["Member ID", "First Name", "Last Name", "Fitness Goal", "Exercise", "Fitness Achievements", "Outstanding Fees"]
        max_length = max(len(label) for label in labels) + 5  # +1 for a bit of extra space

        print(f"{labels[0] + ':':<{max_length}} {member_details[1]}")
        print(f"{labels[1] + ':':<{max_length}} {member_details[2]}")
        print(f"{labels[2] + ':':<{max_length}} {member_details[3]}")
        print(f"{labels[3] + ':':<{max_length}} {member_details[4]}")
        print(f"{labels[4] + ':':<{max_length}} {member_details[5]}")
        print(f"{labels[5] + ':':<{max_length}} {member_details[6]}")
        print(f"{labels[6] + ':':<{max_length}} ${member_details[7]:,.2f}\n\n")  # Formatted as currency
        
        # Fetch sessions
        cur.execute("""
        SELECT s.session_id, s.trainer_id, s.session_date, s.session_details, u.username, r.room_type as room_name
        FROM "Sessions" s
        JOIN "Trainers" t ON s.trainer_id = t.trainer_id
        JOIN "Users" u ON t.user_id = u.user_id
        JOIN "Rooms" r ON s.room_id = r.room_id
        WHERE s.member_id = %s
        """, (member_id,))
        sessions = cur.fetchall()


        print("Your Registered Training Sessions:")
        if not sessions:
            print("You are not registered for any training sessions.")
        else:
            for session in sessions:
                print(f"Date: {session[2]:}. Trainer: {session[4]:}. Room: {session[5]:}. Details: {session[3]:}")
        

        # Fetch health metrics
        cur.execute("SELECT * FROM \"Health\" WHERE member_id = %s", (member_id,))
        health_metrics = cur.fetchall()

        print("\nHealth Metrics:")
        for metric in health_metrics:
            print(f"Blood Pressure: {metric[2]}\nWeight: {metric[3]}kg \nHeight: {metric[4]}cm")

        # Events section
        cur.execute("SELECT * FROM \"Classes\"")
        events = cur.fetchall()
        print("\nUpcoming Classes:")
        for event in events:
            # Fetch the trainer name and room using the trainer ID and room ID
            cur.execute("""
            SELECT u.username 
            FROM "Users" u
            JOIN "Trainers" t ON u.user_id = t.user_id
            WHERE t.trainer_id = %s
            """, (event[4],))
            trainer_name = cur.fetchone()[0]
            cur.execute("SELECT room_type FROM \"Rooms\" WHERE room_id = %s", (event[5],))
            room_name = cur.fetchone()[0]

            # Count the number of members attending the event
            cur.execute("SELECT COUNT(*) FROM \"ClassQueue\" WHERE event_id = %s", (event[0],))
            member_count = cur.fetchone()[0]

            print(f"{event[1]}\n\t Trainer: {trainer_name}\n\t Date: {event[2]}\n\t Description: {event[3]}\n\t Current Attendance: {member_count}.")

        memberChoice = Menu("\n", "Update Personal Info", "Update Health Metrics", "Schedule Session", "Cancel Training Session", "Register for Event", "Pay Bills", "Logout").menu(False)

        match memberChoice:
            case "1":
                update_personal(user_id)
            case "2":
                update_health_metrics(user_id)
            case "3":
                schedule_page(member_id)
            case "4":
                cancel_session(member_id)
            case "5":
                register_for_event(member_id)
            case "6":
                pay_bills(member_id)
            case "7":
                exit = True

    cur.close()
    conn.close()

def schedule_page(member_id):
    # Connect to the database
    conn = connect(**db)
    cur = conn.cursor()

    try:
        # Fetch available dates
        cur.execute("SELECT date_id, availability, trainer_id FROM \"Dates\" ORDER BY availability")
        dates = cur.fetchall()

        if not dates:
            print("No available dates to schedule.")
            return
        
        print("\nAvailable Dates for Training Sessions:")
        for i, date in enumerate(dates, start=1):
            formatted_date = date[1].strftime('%Y-%m-%d %H:%M:%S')
            print(f"{i}. Date ID: {date[0]}, Date: {formatted_date}")

        # User selects a date
        choice = int(input("Enter the number corresponding to the date you wish to schedule: ")) - 1

        # Validate choice
        if choice < 0 or choice >= len(dates):
            print("Invalid selection.")
            return

        date_id = dates[choice][0]

        # Schedule the session
        schedule_session(member_id, date_id)

    except Error as e:
        print(f"An error occurred: {e}")
        Functions.enterToContinue()
        conn.rollback()
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        Functions.enterToContinue()
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def schedule_session(member_id, date_id):
    conn = connect(**db)
    cur = conn.cursor()

    try:
        # Fetch the selected date details
        cur.execute("SELECT trainer_id, availability FROM \"Dates\" WHERE date_id = %s", (date_id,))
        trainer_id, trainer_availability = cur.fetchone()

        # Schedule the session
        cur.execute("INSERT INTO \"Sessions\" (member_id, trainer_id, room_id, session_date) VALUES (%s, %s, %s, %s)",
                    (member_id, trainer_id, 1, trainer_availability))
        conn.commit()
        print(f"\nSession Scheduled Successfully on {trainer_availability.strftime('%Y-%m-%d %H:%M:%S')}")

        # Update billing info
        cur.execute("SELECT balance FROM \"Members\" WHERE member_id = %s", (member_id,))

        newBill = (cur.fetchone()[0] or float(0)) + 20

        cur.execute("UPDATE \"Members\" SET balance = %s WHERE member_id = %s", (newBill, member_id))

        conn.commit()

        print(f"Billing updated: New bill is ${newBill}.")

        Functions.enterToContinue()

    except Error as e:
        print(f"An error occurred: {e}")
        Functions.enterToContinue()
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def cancel_session(member_id):
    # Connect to the database
    conn = connect(**db)
    cur = conn.cursor()

    try:
        # Fetch the member's sessions
        cur.execute("""
            SELECT s.session_id, s.session_date, u.username, r.room_type, s.session_details
            FROM "Sessions" s
            JOIN "Trainers" t ON s.trainer_id = t.trainer_id
            JOIN "Users" u ON t.user_id = u.user_id
            JOIN "Rooms" r ON s.room_id = r.room_id
            WHERE s.member_id = %s
        """, (member_id,))
        sessions = cur.fetchall()

        # Check if sessions exist
        if not sessions:
            print("No sessions found.")
            Functions.enterToContinue()
            return

        # Display the sessions
        print("\nSelect a session to cancel:")
        for i, session in enumerate(sessions, start=1):
            print(f"{i}. Date: {session[1]}, Trainer: {session[2]}, Room: {session[3]}, Details: {session[4]}")

        # Get user input on which session to cancel
        choice = int(input("Enter the number of the session you wish to cancel: ")) - 1

        # Validate the choice
        if choice < 0 or choice >= len(sessions):
            print("Invalid selection.")
            return

        # Cancel the selected session
        session_to_cancel = sessions[choice]
        cur.execute("DELETE FROM \"Sessions\" WHERE session_id = %s", (session_to_cancel[0],))
        conn.commit()

        # Update billing information to reflect the refund
        cur.execute("""
            UPDATE "Members"
            SET balance = balance - 20.00
            WHERE member_id = %s
        """, (member_id,))
        conn.commit()

        print(f"\nSession cancelled successfully. $20 has been credited to the member's account.")
        Functions.enterToContinue()

    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def pay_bills(member_id):
    conn = connect(**db)  # Ensure db is properly defined with your connection parameters
    cur = conn.cursor()

    try:
        # Query for the current billing information
        cur.execute("SELECT balance FROM \"Members\" WHERE member_id = %s", (member_id,))
        balance = cur.fetchone()

        if balance:
            print("\nCurrent outstanding bill amount: ${:.2f}".format(balance[0]))

            # Update the balance for the current member to $0.00
            cur.execute("UPDATE \"Members\" SET balance = 0.00 WHERE member_id = %s", (member_id,))
            conn.commit()

            print("\nThank you for your payment. Your bill has been cleared.")
        else:
            print("\nNo billing information found for the given member ID.")

    except Exception as e:
        print("An error occurred:", e)
        conn.rollback()
    
    finally:
        cur.close()
        conn.close()

    Functions.enterToContinue()


def update_personal(user_id):
    # Connect to the database
    conn = connect(**db)
    cur = conn.cursor()

    try:
        # Retrieve the current details of the member
        cur.execute("SELECT * FROM \"Members\" WHERE user_id = %s", (user_id,))
        member_details = cur.fetchone()

        # If no member is found
        if not member_details:
            print("No member found with the given user ID.")
            return

        # Display current member details
        labels = ["Member ID", "First Name", "Last Name", "Fitness Goals", "Exercise", "Fitness Achievements"]
        print("\nCurrent details:\n")
        for i, label in enumerate(labels, start=1):
            print(f"{label}: {member_details[i]}")

        # Ask which detail to update
        for i, label in enumerate(labels[1:], start=1):  # start from 1 to skip Member ID
            print(f"{i}. {label}")
        choice = int(input("Enter the number of the field you want to update: "))

        # Validate choice
        if choice < 0 or choice >= len(labels):
            print("Invalid selection.")
            return

        # Get the new value for the field
        new_value = input(f"Enter new value for {labels[choice]}: ")

        # Update the database
        sql_update = f"UPDATE \"Members\" SET \"{labels[choice].replace(' ', '_').lower()}\" = %s WHERE user_id = %s"
        cur.execute(sql_update, (new_value, user_id))
        conn.commit()

        print(f"\n{labels[choice]} updated successfully.")
        Functions.enterToContinue()

    except Exception as e:
        print(f"An error occurred: {e}")
        Functions.enterToContinue()
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def update_health_metrics(user_id):
    # Connect to the database
    conn = connect(**db)
    cur = conn.cursor()

    try:
        # Retrieve the current health metrics of the member
        cur.execute("SELECT member_id FROM \"Members\" WHERE user_id = %s", (user_id,))
        member_id = cur.fetchone()
        if not member_id:
            print("No member found with the given user ID.")
            return

        cur.execute("SELECT * FROM \"Health\" WHERE member_id = %s", (member_id[0],))
        health_metrics = cur.fetchone()

        # If no metrics are found
        if not health_metrics:
            print("No health metrics found for this member.")
            Functions.enterToContinue()
            return

        # Display current health metrics
        labels = ["Blood Pressure", "Weight", "Height"]
        print("Current health metrics:")
        for i, label in enumerate(labels, start=2):  # Assuming health metrics start from index 2
            print(f"{label}: {health_metrics[i]}")

        # Ask which metric to update
        for i, label in enumerate(labels, start=1):
            print(f"{i}. {label}")
        choice = int(input("Enter the number of the metric you want to update: ")) - 1

        # Validate choice
        if choice < 0 or choice >= len(labels):
            print("Invalid selection.")
            return

        # Get the new value for the metric
        new_value = input(f"Enter new value for {labels[choice]}: ")

        # Prepare the column name based on selected label
        column_name = labels[choice].replace("Blood Pressure", "blood").lower()

        # Update the database
        sql_update = f"UPDATE \"Health\" SET {column_name} = %s WHERE member_id = %s"
        cur.execute(sql_update, (new_value, member_id[0]))
        conn.commit()

        print(f"\n{labels[choice]} updated successfully.")
        Functions.enterToContinue()

    except Exception as e:
        print(f"An error occurred: {e}")
        Functions.enterToContinue()
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    
def register_for_event(member_id):
    # Connect to the database
    conn = connect(**db)
    cur = conn.cursor()

    try:
        # Display available events
        cur.execute("SELECT * FROM \"Classes\"")
        events = cur.fetchall()
        
        if not events:
            print("No events available to register.")
            Functions.enterToContinue()
            return
        
        print("\nAvailable Events:")
        for event in events:
            print(f"Event ID: {event[0]}, Name: {event[1]}, Date: {event[2]}, Details: {event[3]}")

        # User selects an event to register
        event_id = int(input("Enter the Event ID you wish to register for: "))

        # Check if the selected event ID is valid
        if event_id not in [event[0] for event in events]:
            print("Invalid event ID.")
            return
        
        # Register the member for the event
        cur.execute("INSERT INTO \"ClassQueue\" (member_id, event_id) VALUES (%s, %s)", (member_id, event_id))
        print(f"\nRegistered for event {event_id} successfully.")

        # Retrieve and update the member's billing information
        cur.execute("SELECT balance FROM \"Members\" WHERE member_id = %s", (member_id,))

        newBill = (cur.fetchone()[0] or float(0)) + 20 

        cur.execute("UPDATE \"Members\" SET balance = %s WHERE member_id = %s", (newBill, member_id))

        print(f"Billing information updated: New bill is ${newBill}.")

        Functions.enterToContinue()

        conn.commit()

    except Error as e:
        print(f"An error occurred: {e}")
        Functions.enterToContinue()
        conn.rollback()
    except ValueError:
        print("Invalid input. Please enter a valid numeric event ID.")
        Functions.enterToContinue()
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def set_trainer_availability(conn, trainer_id):
    print("\nEnter your available date and time:")
    year = Functions.loopTillValid("Year (YYYY): ", "integer", False)
    month = Functions.loopTillValid("Month (MM): ", "integer", False)
    day = Functions.loopTillValid("Day (DD): ", "integer", False)
    hour = Functions.loopTillValid("Hour (HH, 24-hour format): ", "integer", False)
    minute = Functions.loopTillValid("Minute (mm): ", "integer", False)
    second = Functions.loopTillValid("Second (ss): ", "integer", False)

    # Assemble and format the date string
    try:
        # Attempt to create a datetime object from inputs to validate
        new_date = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
        formatted_date = new_date.strftime('%Y-%m-%d %H:%M:%S')

        # Insert the formatted date into the database
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO "Dates" (trainer_id, availability) 
                VALUES (%s, %s)
            """, (trainer_id, formatted_date))
            conn.commit()
        print(f"Your availability date has been added: {formatted_date}.")
        Functions.enterToContinue()
    except ValueError as ve:
        print("Invalid date or time components. Please ensure all inputs are correct and in the required format.")
        Functions.enterToContinue()
    except Exception as e:
        print(f"Failed to update availability: {e}")
        Functions.enterToContinue()

def view_member_profile(conn):
    member_id = input("Enter the member's ID to search: ")
    if member_id:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT m.* 
            FROM "Members" m
            WHERE m.member_id = %s
            """, (member_id,))
            member_details = cur.fetchone()

        if member_details:
            Functions.clearScreen(f"{member_details[2]}'s Profile")

            labels = ["Member ID", "First Name", "Last Name", "Fitness Goal", "Exercise", "Fitness Achievements", "Outstanding Fees"]
            max_length = max(len(label) for label in labels) + 5  # +1 for a bit of extra space

            print(f"{labels[0] + ':':<{max_length}} {member_details[1]}")
            print(f"{labels[1] + ':':<{max_length}} {member_details[2]}")
            print(f"{labels[2] + ':':<{max_length}} {member_details[3]}")
            print(f"{labels[3] + ':':<{max_length}} {member_details[4]}")
            print(f"{labels[4] + ':':<{max_length}} {member_details[5]}")
            print(f"{labels[5] + ':':<{max_length}} {member_details[6]}")
            print(f"{labels[6] + ':':<{max_length}} ${member_details[7]:,.2f}\n\n")  # Formatted as currency

            Functions.enterToContinue()
        else:
            print("No member found with that first name.")
            Functions.enterToContinue()

def trainer_page(user_id):
    conn = connect(**db)
    try:
        cur = conn.cursor()
        cur.execute("SELECT trainer_id FROM \"Trainers\" WHERE user_id = %s", (user_id,))
        trainer_id = cur.fetchone()[0]

        exit = False

        while not exit:

            cur.execute("SELECT first_name FROM \"Trainers\" WHERE user_id = %s", (user_id,))
            trainer_name = cur.fetchone()[0]

            Functions.clearScreen(f"{trainer_name}'s Dashboard")

            cur.execute("""
                SELECT availability FROM "Dates"
                WHERE trainer_id = %s
                ORDER BY availability
            """, (trainer_id,))
            availabilities = cur.fetchall()

            if availabilities:
                print("Your current availability:")
                for availability in availabilities:
                    print(f"- {availability[0].strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print("No current availability set.")

            trainerChoice = Menu("", "Set Availability", "View Member Profile", "Logout").menu(False)

            match trainerChoice:
                case "1":
                    set_trainer_availability(conn, trainer_id)
                case "2":
                    view_member_profile(conn)
                case "3":
                    exit = True

    finally:
        cur.close()
        conn.close()

# Setting up the database by creating tables from DDL.sql
def initialize():
    conn = connect(**db)
    cur = conn.cursor()

    # Open the SQL file
    with open('./SQL/DDL.sql', 'r') as DDL:
        cur.execute(DDL.read())

    with open('./SQL/DML.sql', 'r') as DML:
        cur.execute(DML.read())

    # Commit and close
    cur.close()
    conn.commit()
    conn.close()

def main():

    global db
    if len(sys.argv) < 4:
        sys.exit("Usage: python3 app.py {database} {username} {password}")
    db = {
        'database': sys.argv[1],
        'user': sys.argv[2],
        'password': sys.argv[3],
    }
    try:
        initialize()

    except Exception as e:
        sys.exit(f"Unable to setup database: {str(e)}")
    
    exit = False

    while not exit:

        userChoice = Menu("Welcome to Health and Fitness Club Management System!", "Login", "Register", "Exit").menu()

        match userChoice:
            case "1":
                login()
            case "2":
                register_user()
            case "3":
                print(f'Thank you for using the Health and Fitness Club Management System, goodbye.')
                exit = True


if __name__ == "__main__":
   main()
