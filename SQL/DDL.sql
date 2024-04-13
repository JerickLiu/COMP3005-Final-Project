DROP TABLE IF EXISTS "Users", "Admins", "Dates", "Trainers", "Members", "Health", "Rooms", "Sessions", "ClassQueue", "Classes" CASCADE;

CREATE TABLE "Users" (
  "user_id" SERIAL PRIMARY KEY,
  "username" VARCHAR(255) NOT NULL UNIQUE,
  "password" VARCHAR(255) NOT NULL,
  "email" VARCHAR(255) NOT NULL UNIQUE,
  "role" VARCHAR(255) NOT NULL
);

CREATE TABLE "Members" (
  "user_id" INTEGER,
  "member_id" SERIAL PRIMARY KEY,
  "first_name" VARCHAR(255) NOT NULL,
  "last_name" VARCHAR(255) NOT NULL,
  "fitness_goals" TEXT,
  "exercise" TEXT,
  "fitness_achievements" TEXT,
  "balance" DECIMAL(12,2),
  FOREIGN KEY ("user_id") REFERENCES "Users"("user_id")
);

CREATE TABLE "Health" (
  "health_id" SERIAL PRIMARY KEY,
  "member_id" INTEGER,
  "blood" TEXT NOT NULL,
  "weight" NUMERIC NOT NULL,
  "height" NUMERIC NOT NULL,
  FOREIGN KEY ("member_id") REFERENCES "Members"("member_id")
);

CREATE TABLE "Trainers" (
  "user_id" INTEGER,
  "trainer_id" SERIAL PRIMARY KEY,
  "first_name" VARCHAR(255) NOT NULL,
  "last_name" VARCHAR(255) NOT NULL,
  FOREIGN KEY ("user_id") REFERENCES "Users"("user_id")
);

CREATE TABLE "Dates" (
  "date_id" SERIAL PRIMARY KEY,
  "trainer_id" INTEGER,
  "availability" TIMESTAMP NOT NULL,
  FOREIGN KEY ("trainer_id") REFERENCES "Trainers"("trainer_id")
);

CREATE TABLE "Admins" (
  "user_id" INTEGER,
  "admin_id" SERIAL PRIMARY KEY,
  FOREIGN KEY ("user_id") REFERENCES "Users"("user_id")
);

CREATE TABLE "Rooms" (
  "room_id" SERIAL PRIMARY KEY,
  "room_type" TEXT NOT NULL,
  "maintenance" TEXT
);

CREATE TABLE "Sessions" (
  "session_id" SERIAL PRIMARY KEY,
  "member_id" INTEGER,
  "trainer_id" INTEGER NOT NULL,
  "room_id" INTEGER NOT NULL,
  "session_date" TIMESTAMP NOT NULL,
  "session_details" TEXT,
  FOREIGN KEY ("member_id") REFERENCES "Members"("member_id"),
  FOREIGN KEY ("trainer_id") REFERENCES "Trainers"("trainer_id"),
  FOREIGN KEY ("room_id") REFERENCES "Rooms"("room_id")
);

CREATE TABLE "Classes" (
  "event_id" SERIAL PRIMARY KEY,
  "event_name" TEXT NOT NULL,
  "event_date" TIMESTAMP NOT NULL,
  "event_description" TEXT,
  "trainer_id" INTEGER NOT NULL,
  "room_id" INTEGER NOT NULL,
  FOREIGN KEY ("trainer_id") REFERENCES "Trainers"("trainer_id"),
  FOREIGN KEY ("room_id") REFERENCES "Rooms"("room_id")
);

CREATE TABLE "ClassQueue" (
  "member_id" INTEGER,
  "event_id" INTEGER,
  UNIQUE ("member_id", "event_id"),
  FOREIGN KEY ("member_id") REFERENCES "Members"("member_id"),
  FOREIGN KEY ("event_id") REFERENCES "Classes"("event_id")
);
