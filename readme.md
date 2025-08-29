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

1. 💾 [Project Overview](#project-overview)
   1. [Features](#features)
   2. [Technologies Used](#technologies-used)
   

2. 👀 [Getting Started](#Getting-Started)
   1. [Prerequisites](#prerequisites) 
   2. [Installation](#installation) 
   3. [Running the Application](#running-the-application)


3. 💻 [Technologies Used](#technologies-used)


4. 🦾 [Project Structure](#project-structure)


5. 🏁 [API Endpoints](#api-endpoints)
   

6. 🚨[Authentication & Authorization](#authentication-authorization)
   1. [User Management](#user-management)
   2. [Security](#security)


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
git clone https://github.com/shivangi-2001/Django_Ecommerce_Application_Unify_Store.git
```

### Navigate to the project directory: 
```commandline
cd Django_Ecommerce_Application_Unify_Store
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

### Add the Product & Collection Records

The project contain dummy `Data` folder which have file **product.json** and **collection.json**.

```commandline
python manage.py loaddata Data/product.json
python manage.py loaddata Data/collection.json
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

# Technologies Used

**Backend Framework:** **`Django (version 5.2.5)`**

**API Development:** **`Django REST Framework (version 3.16.1)`**

**Database:** **`SQLite3`** [You can change the database as your choice.]

#### **Authentication & Security:**

**Django's Built-in Auth:** Utilized for core user management.

- **`django-otp (version 1.6.1):`** Enables one-time password (OTP) functionality for email verification.

- **`django-auto-logout (version 0.5.1):`** Handles automatic user logout based on idle time.

#### Other Libraries:

- **`django-filter (version 25.1):`** Provides powerful filtering capabilities for Django queries.

- **`django-environ (version 0.12.0)`** and **`environ (version 1.0)`**: Manages environment variables for secure and flexible configuration.

- **`Pillow (version 11.3.0):`** A Python imaging library used for handling images, likely for product uploads.

- **`asgiref (version 3.9.1):`** A library for asynchronous web applications in Python.

- **`sqlparse (version 0.5.3):`** A non-validating SQL parser used for formatting and analysis.


---


# Project Structure

- **`Ecommerce/`** : The main Django project folder.

- **`PROFILE/`** : Django app for user authentication and profiles.

- **`STORE/`** : Django app for all e-commerce logic, products, cart, etc.

- **`Templates/`** : Contains all HTML templates.

- **`static/`** : For static files like CSS and JavaScript

- **`media/`**: For user-uploaded files, such as product images.


# 🔐 Authentication & Authorization

## User Management

This project implements a **secure authentication system** using **Django**, **Django OTP**, and **custom logic for account verification**.

The flow ensures that only verified users can log in, while protecting against brute force OTP attempts.

### 1. User Registration

* A new user registers with **email, first name, and last name**. 
* The account is created with `is_active = False` (inactive until verified). 
* An **EmailDevice** is created using **django-otp**, which generates and sends a **One-Time Password (OTP)** to the registered email. 
* The user is redirected to the **OTP Verification** page.

### 2. OTP Verification

+ The user must enter the received OTP to activate the account. 
+ OTP is verified using `device.verify_token()`.

#### Valid OTP:

+ The user account is activated (`is_active = True`). 
+ OTP attempts reset to `3`
+ The user can now log in.

#### Invalid OTP:

* The `otp_attempts` counter decreases by 1. 
* After **3 failed attempts**, the account is locked:
  * reset_timer is set for **30 minutes**. 
  * During this period, the user cannot request OTP or log in.

### 3. Lockout & Retry

* If the user is locked (`reset_timer set`):
  * Any OTP verification or resend attempts will be blocked with an error message until the timer expires.

* After **30 minutes**:
  * The lock is lifted automatically. 
  * `otp_attempts` reset to 3. 
  * The user can request a fresh OTP again.

### 4. Resend OTP (VerifyAccount flow)

* Users can request a **new OTP** if:
  * Their account is not verified yet. 
  * They are not currently locked (`reset_timer` expired).

* To prevent spamming, a new OTP can only be sent every **2 minutes.**
* Once conditions are met, a fresh OTP is generated and emailed.

### 5. Login

* Login is handled via Django’s built-in `LoginView`. 
* Only **active and verified users** (`is_active=True`) can log in. 
* On success, the user is redirected to the homepage/dashboard. 
* On failure (invalid credentials or inactive account), an error message is shown.

## Authorization

- **Authenticated users** can access their **Profile** and other protected pages.
- **Unauthenticated or inactive users** are always redirected to the login/OTP verification pages. 
- Fine-grained permissions can be extended via Django’s `PermissionsMixin`.

## Security

This project is designed with layered security to prevent brute-force, replay, and abuse of OTP.

#### OTP-based Account Activation

   * Users must confirm their email with an OTP sent via `django-otp`. 
   * Ensures only verified emails can log in.

#### Automatic Lockout after Failed OTP Attempts 

   * Each user has `otp_attempts = 3`. 
   * After 3 failed tries → account is **locked for 30 minutes**. 
   * Prevents brute-force attacks on OTP codes.

#### Timed Lock Expiry

   * Lock (`reset_timer`) automatically expires after 30 minutes. 
   * User can retry registration/verification after cooldown.

#### Resend OTP Cooldown

   * New OTP can only be requested every **2 minutes**. 
   * Prevents spamming & email abuse.

#### Session-Based Authentication

   * Once verified, users authenticate with Django’s session system. 
   * Ensures secure state management for logged-in users.


---

# API Endpoints

### Authentication & User Profiles

These endpoints handle all user-related functions, from account creation to session management.

- `POST /auth/register` - Creates a new user account. 
- `POST /auth/<int:pk>/verify_otp` - Verifies a user's account using an OTP.
- `POST /login` - Logs a user into their account.
- `GET /logout `- Logs a user out of their session.
- `GET /auth/<str:pk>/accounts/profile` - Retrieves and manages the profile for a specific user.
- `GET /account/verify` - Verifies an account.

### Product & Store Management

These endpoints are used to interact with product and collection data.

- `GET /api/product/` - Retrieves a list of all products.
- `GET /api/collection/` - Retrieves a list of all collections.
- `GET /search/` - Searches for products and collections.
- `GET /categories/` - Retrieves a list of all product categories.
- `GET /products/` - Retrieves a gallery of all products.
- `GET /products/<str:pk>/` - Retrieves the detailed information for a specific product.

### Cart, Wishlist & Orders

These endpoints manage the shopping cart, wishlist, and the order creation process.

* `GET /products/<str:pk>/add_to_cart `- Adds a product to the user's cart.
* `GET /cart/<str:user_id>/` - Retrieves the cart for a specific user.
* `GET /wishlist` - Retrieves the current user's wishlist.
* `POST /order/` - Creates a new order.
* `POST /cartItem/<str:cart_items_id>/ `- Increases the quantity of a specific cart item.
* `POST /cartItem/<str:cart_items_id>/` - Decreases the quantity of a specific cart item.
* `DELETE /cart/<str:user_id>/delete/<str:pk> `- Deletes a specific item from the user's cart.

# License

---
![Python](https://img.shields.io/badge/Python-3.10-blue)
![Django](https://img.shields.io/badge/Django-5.2.5-green)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

This project is licensed under the MIT License. See the LICENSE.md file for details.

# Contact

---
**Email:** `shivangikeshri21@gmail.com`


