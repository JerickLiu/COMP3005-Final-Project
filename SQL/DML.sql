INSERT INTO "Users" ("username", "password", "email", "role") VALUES 
('jasonB', 'secure123', 'jason.b@cmail.carleton.ca', 'member'),    -- User_id 1
('lisaM', 'magic321', 'lisa.m@cmail.carleton.ca', 'member'),       -- User_id 2
('mikeT', 'topgun88', 'mike.t@cmail.carleton.ca', 'member'),       -- User_id 3
('natalieH', 'wonder4', 'natalie.h@cmail.carleton.ca', 'trainer'), -- Trainer_id 1
('chrisP', 'strength42', 'chris.p@cmail.carleton.ca', 'trainer'),  -- Trainer_id 2
('admin', 'admin', 'admin@cmail.carleton.ca', 'admin');

INSERT INTO "Members" ("user_id", "first_name", "last_name", "fitness_goals", "exercise", "fitness_achievements", "balance") VALUES 
(1, 'Jason', 'Brody', 'Complete a triathlon', 'Crossfit training', 'Deadlift PR 250lbs', 0.00),
(2, 'Lisa', 'Monaco', 'Climb Mount Everest', 'High altitude training', 'Climbed Kilimanjaro', 50.99),
(3, 'Mike', 'Tyson', 'Win a boxing title', 'Heavy bag workouts', 'Won regional championship', 75.00);

-- Health, weight in kg, height in inches
INSERT INTO "Health" ("member_id", "blood", "weight", "height") VALUES
(1, '130/85', 75, 182),
(2, '120/80', 62, 169),
(3, '110/70', 98, 178);

INSERT INTO "Trainers" ("user_id", "first_name", "last_name") VALUES 
(4, 'Natalie', 'Hawkins'),
(5, 'Chris', 'Powell');

-- (trainer availability)
INSERT INTO "Dates" ("availability", "trainer_id") VALUES 
('2024-01-14 12:00:00', 1),
('2024-02-14 12:00:00', 1),
('2024-01-14 09:00:00', 2),
('2024-02-14 09:00:00', 2);

INSERT INTO "Rooms" ("room_type", "maintenance") VALUES 
('Yoga Studio', 'New yoga mats available.'),
('Cardio Room', 'New treadmills installed.'),
('Outdoor Track', 'Track recently resurfaced.');

INSERT INTO "Sessions" ("member_id", "trainer_id", "room_id", "session_date", "session_details")
VALUES 
(1, 2, 2, '2024-07-01 08:00', 'Interval Training'),
(3, 1, 3, '2024-07-02 09:00', 'Speed Training');

INSERT INTO "Classes" ("event_name", "event_date", "event_description", "trainer_id", "room_id") VALUES 
('Martial Arts Workshop', '2024-08-15 14:00:00', 'Learn self-defense and improve reflexes', 1, 1),
('Marathon', '2024-08-15 14:00:00', '5K timed run on the track', 2, 3);
