# Unify Store: A Django E-commerce Application

![logo](static/image/logo.png) 

---

## Description
**Unify Store** is a comprehensive e-commerce platform built with the Django framework. 
The application mimics core functionalities of major online retail platforms, including 
user authentication, product management, a shopping cart system, and a wishlist.
While the current version handles all transactional logic. This project serves as a 
**robust foundation** for a scalable e-commerce solution.

---

## Table of Content

1. 🏁 [Project Overview](#project-overview)
   1. [Features](#features)
   2. [Technologies Used](#technologies-used)
   

2. 👀 [Getting Started](#Getting-Started)
   1. [Prerequisites](#prerequisites) 
   2. [Installation](#installation) 
   3. [Running the Application](#running-the-application)


3. 🚨[Authentication & Authorization](#authentication-authorization)
   1. User Management
   2. [Security](#security)


4. 🦾 [Project Structure](#project-structure)


5. [API Endpoints](#api-endpoints)
   1. Authentication & User Profiles 
   2. Product & Store Management 
   3. Cart & Orders


6. [Technologies Used](#technologies-used)


7. [License](#License)


8. [Contact](#contact)


---

# Project Overview

**_UnifyStore_** is a robust Django e-commerce application designed to serve as a 
**boilerplate** and foundation for building scalable online stores. 
It provides core **_e-commerce functionalities_**, allowing developers to extend 
and customize the platform to meet specific user needs. 
The codebase is well-structured with clear comments, making it easy to 
understand and maintain, even for developers who are new to the project.

## Features

- **Authorization & Authentication:** Includes secure user registration, login, and logout.

- **Email OTP Verification:** Adds a layer of security by verifying user accounts with a one-time password sent via email.

- **Shopping Cart:** A fully functional system for adding, removing, and updating products before checkout.

- **Wishlist:** Allows users to save products they are interested in for future purchase.

## Future Goals

This project is built to be a **springboard** for further development. 
The following features are planned for future implementation:

- **Payment Gateway Integration:** Integrating secure payment solutions like Stripe or PayPal.
- **Advanced Functionality:** Adding features such as a user review system, product recommendations, or an admin dashboard.

---

# Getting Started

## Prerequisites:

- Python 
- Django 
- Other Python packages [listed in a requirements.txt file](requirement.txt)

## Installation:

### Clone the repository:
```
git clone https://github.com/shivangi-2001/Django_Ecommerce_Applictaion_Unify_Store.git
```

### Navigate to the project directory: 
```commandline
cd Django_Ecommerce_Applictaion_Unify_Stor
```

### Create a virtual environment: 

```commandline
pip install pipenv //Install pip and pipenv
pipenv install
```

or

```commandline
python -m venv venv
```

### Activate the virtual environment: 

```commandline
pipenv shell
```

or

```commandline 
source venv/bin/activate //for macOS/Linux
// or 
venv\Scripts\activate  //for Windows
```

### Install dependencies: 

```commandline
pipenv install -r requirements.txt
```

## Running the Application


- **Apply database migrations:**
```
python manage.py makemigrations 
python manage.py migrate
```

- **Run the development server:**
```
python manage.py runserver 
```

> Access the site in your browser at `http://127.0.0.1:8000/`


---



# Authorization & Authorization

`Email OTP django-otp`

# API Endpoints

# Technologies Used

Backend Framework: Django (version 5.2.5)

API Development: Django REST Framework (version 3.16.1)

Database: SQLite3

Authentication & Security:

Django's Built-in Auth: Utilized for core user management.

django-otp (version 1.6.1): Enables one-time password (OTP) functionality for email verification.

django-auto-logout (version 0.5.1): Handles automatic user logout based on idle time.

Other Libraries:

django-filter (version 25.1): Provides powerful filtering capabilities for Django queries.

django-environ (version 0.12.0) and environ (version 1.0): Manages environment variables for secure and flexible configuration.

Pillow (version 11.3.0): A Python imaging library used for handling images, likely for product uploads.

asgiref (version 3.9.1): A library for asynchronous web applications in Python.

sqlparse (version 0.5.3): A non-validating SQL parser used for formatting and analysis.
# License

---

This project is licensed under the MIT License. See the LICENSE.md file for details.

# Contact

---
**Email:** `shivangikeshri21@gmail.com`


