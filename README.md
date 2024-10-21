# expenses_task_project

**Installation

1. clone this repository:
    git clone https://github.com/Upadhyay00/expenses_task_project
    cd expenses_task_project

2. create a virtual environment and activate it:
    python -m venv venv 

    to use it in linux: 
        source venv/bin/activate

    to use it in windows:
        ./venv/Scripts/activate

3. install the required dependencies:
    pip install -r requirements.txt

**Database setup

1. change the database uri details in the config file 
2. create appropriate tables with the below queries 

    CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    mobile_number VARCHAR(15) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);


CREATE TABLE expense (
    id INT AUTO_INCREMENT PRIMARY KEY,
    amount DECIMAL(10, 2) NOT NULL,
    description VARCHAR(255),
    creator_id INT NOT NULL,
    split_method VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (creator_id) REFERENCES user(id)
);


CREATE TABLE participant (
    id INT AUTO_INCREMENT PRIMARY KEY,
    expense_id INT NOT NULL,
    user_id INT NOT NULL,
    amount_owed DECIMAL(10, 2) NOT NULL,
    percentage DECIMAL(5, 2),
    FOREIGN KEY (expense_id) REFERENCES expense(id),
    FOREIGN KEY (user_id) REFERENCES user(id)
);


** running the application

use the below command to run the application
    :- python app.py      # this will run the application by default on the port 5000 if available on the device
                            else change the port in the app.py file by change the port=5000 in last line

the application will be available at
http://localhost:5000 by default

** API endpoints available:

1. /register_user (POST):- this endpoint is used to register users with the details such as name, email, mobile_number, password.

2. /login (POST):- this endpoint is used to generate JWT auth token to use in other endpoints in the application

3. /get_details/<int:mobile_number>  (GET):- this endpoint is used to get the details of a user using their phone number

4. /expenses (POST) :- this endpoint is used to create expenses and split them based on the required split method 

below are the payload examples to send with different split methods:-

1. percentage based split
:-
{
    "creator_id": 1,
    "split_method": "percentage",
    "amount": 500.00,
    "participants": [
        {"user_id": 2, "percentage": 40},
        {"user_id": 3, "percentage": 35},
        {"user_id": 4, "percentage": 25}
    ],
    "description": "Team lunch"
}


2. exact split:-
{
    "creator_id": 1,
    "split_method": "exact",
    "amount": 400.00,
    "participants": [
        {"user_id": 2, "amount_owed": 150.00},
        {"user_id": 3, "amount_owed": 100.00},
        {"user_id": 4, "amount_owed": 150.00}
    ],
    "description": "Office supplies"
}

3. equal split:-
{
    "creator_id": 1,
    "split_method": "equal",
    "amount": 300.00,
    "participants": [
        {"user_id": 2},
        {"user_id": 3},
        {"user_id": 4}
    ],
    "description": "Weekend trip expenses"
}


5. /expenses/<int:user_id> (GET):- this endpoint is used to Get user-specific expenses.

6. /expenses/<int:user_id>/balance-sheet :- this endpoint is used to download csv balance sheet of expenses.(token required)
