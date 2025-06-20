# NGO Management System
An integrated web-based application built using Flask and MySQL to streamline operations of a Non-Governmental Organization (NGO), enhancing transparency, donor engagement, and inventory tracking.

## 🚀 Features

### 👥 User Roles

### #Donor

Login/Register

Donate money (with simulated UPI QR scan)

Donate in-kind items

Choose to donate anonymously

Get a thank-you confirmation

#### Staff/Admin

Secure login

Dashboard with key metrics

View recent donations

Manage inventory (add/update/delete items)

## 📊 Staff Dashboard Highlights
Total monetary donations

Count of in-kind donations

Total inventory items

Number of active donors

Last 5 donation entries

### 💰 Donation Types
Monetary Donation: Scan a UPI QR code, confirm payment, and store record.

In-Kind Donation: Donate physical items by category and quantity.

## 🛠️ Tech Stack
Component	Technology
Backend	Python (Flask)
Frontend	HTML, CSS
Database	MySQL
Styling	Custom CSS
Libraries Used	mysql.connector, Flask

## 🗃️ Database Schema Overview
Tables:
staff (staff_id, username, email, password, ngo_id)

donors (donor_id, username, email, password, ngo_id)

donations (donation_id, donor_id, donation_type, category, item, quantity, amount, anonymous, donation_date, ngo_id)

inventory (item_id, item_name, category, quantity, ngo_id)

children (child_id, name, dob, gender, status, ngo_id) (optional/for future expansion)

ngo (ngo_id, name, contact_email, registration_number, city, state, country, phone) (optional)

### 🔐 Authentication
Session-based login using Flask session

Role-based redirection (Donor vs Staff)

Logout functionality available for both roles


## 📌 Future Enhancements
Track expenses and fund utilization

Add automated email acknowledgments

Add user registration with OTP/email verification

Analytics and visualizations using Chart.js

## 🙌 Contributors
Lavanya Mall Thakur — @lavanya-865

## 📃 License
This project is for academic and non-commercial use only.
