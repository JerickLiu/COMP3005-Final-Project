# Health and Fitness Club Management System

## Introduction
The Health and Fitness Club Management System is a comprehensive application designed to cater to the needs of club members, trainers, and administrative staff. This system enables members to manage their profiles, set personal fitness goals, track exercise routines, and much more. Trainers can manage their schedules and access member profiles, while administrative staff can handle room bookings, monitor equipment, and manage billing.

## Demo
View the demo at the following link: 

## Features
- **Members**:
  - Register and manage their profiles.
  - Set and track personal fitness goals.
  - Record and monitor health metrics.
  - Schedule, reschedule, or cancel training sessions.
  - Register for group fitness classes.

- **Trainers**:
  - Manage their schedules.
  - View member profiles and session schedules.

- **Administrative Staff**:
  - Manage room bookings and monitor room statuses.
  - Oversee the maintenance of fitness equipment.
  - Update class schedules.
  - Manage billing and process payments.

## Prerequisites
- Python 3.10+
- PostgreSQL

## Usage

1. **Clone the repository:**
   ```bash
   git clone https://github.com/JerickLiu/COMP3005-Final-Project
   cd COMP3005-Final-Project-master
   ```
2. **Initialize PostgreSQL database:**
    Modify the database connection details in `app.py` as per your PostgreSQL setup.
    Run the following command to initialize the database with the required tables and sample data:
    ```bash
    python3 src/app.py {database} {username} {password}
    ```
