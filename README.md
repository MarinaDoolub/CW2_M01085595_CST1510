# Week 7: Secure Authentication System
Student Name:Marina Doolub
Student ID: M01085595
Course: CST1510 -CW2 - Multi-Domain Intelligence Platform

## Project Description
A command-line authentication system implementing secure password hashing
This system allows users to register accounts and log in with proper pass

## Features
- Secure password hashing using bcrypt with automatic salt generation
- User registration with duplicate username prevention
- User login with password verification against stored hashes
- Input validation for usernames and passwords
- File-based user data storage in users.txt
- View registered users through an interactive menu
- Text-based menu interface with clear user options and feedback
- Error handling for invalid input and file operations
  
## Technical Implementation
- Hashing Algorithm: bcrypt with automatic salt generation for secure password hashing
- Data Storage: Plain text file (users.txt) using comma-separated values for username and hashed password pairs
- Password Security:  One-way hashing; no plaintext passwords are stored or displayed
-Validation:Username, with a minimum of 3 characters,commas not allowed and password, with a minimum 6 characters
-Program Flow: Menu-driven interface allowing registration, login, user listing, and exit
-Error Handling: Graceful handling of missing files, invalid inputs, and write errors
-Data Structure: Uses a Python dictionary to load and manage user data in memory

## Requirements
bcrypt==5.0.0

## Clone the repository
```bash
git clone https://github.com/MarinaDoolub/Coursework2.git
cd Coursework2
```

## Run the code
```bash
python auth.py
# or
python3 auth.py
```
