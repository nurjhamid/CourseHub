

DROP DATABASE IF EXISTS coursehub_db;
CREATE DATABASE coursehub_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE coursehub_db;

-- Users table (Students & Admins)
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    address VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL, -- 'student' or 'admin'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Students table
CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    user_id INT NOT NULL UNIQUE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Admins table
CREATE TABLE admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    role VARCHAR(50) NOT NULL DEFAULT 'course_admin',
    user_id INT NOT NULL UNIQUE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Courses table
CREATE TABLE courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255),
    credits INT NOT NULL,
    max_students INT NOT NULL DEFAULT 50
);

-- Enrollments table
CREATE TABLE enrollments (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    date_enrolled DATETIME DEFAULT CURRENT_TIMESTAMP,
    grade VARCHAR(5),
    CONSTRAINT fk_enroll_student FOREIGN KEY (student_id)
        REFERENCES students(student_id) ON DELETE CASCADE,
    CONSTRAINT fk_enroll_course FOREIGN KEY (course_id)
        REFERENCES courses(course_id) ON DELETE CASCADE,
    CONSTRAINT uq_student_course UNIQUE (student_id, course_id)
);

-- Seed data: one admin user and one student user, plus a sample course
INSERT INTO users (username, password, email, phone, address, role)
VALUES
('admin1',  'admin123',  'admin1@example.com',  '01700000001', 'Admin Address',  'admin'),
('student1','stud123',   'student1@example.com','01700000002', 'Student Address','student');

INSERT INTO admins (role, user_id)
VALUES ('course_admin', 1);

INSERT INTO students (name, user_id)
VALUES ('Sample Student', 2);

INSERT INTO courses (course_name, description, credits, max_students)
VALUES ('Intro to Programming', 'Basic programming concepts.', 3, 50);
