# Uni Project

## Project Overview
This project is a web-based inventory management system designed to help users track and manage inventory levels, generate reports, and handle purchasing management. The system supports two types of users: regular users and administrators, each with different levels of access and functionality.

## Features
- **Inventory Tracking**: View and manage current inventory levels for all items.
- **Inventory Report**: Generate and view detailed reports on inventory status and changes.
- **Purchasing Management**: (Admin only) Manage purchasing orders and supplier information.
- **User Management**: Handle user registration, authentication, profile management, and role-based access control.

## Libraries and Frameworks
- **Flask**: A lightweight WSGI web application framework in Python.
- **Jinja2**: A templating engine for Python, used for rendering HTML templates.
- **Chart.js**: A JavaScript library for creating charts, used for visualizing inventory and sales data.
- **Bootstrap**: A CSS framework for responsive web design.

## User Roles
### Regular User
- **Access**: Limited access to the system.
- **Features**: Can view and manage inventory levels, generate inventory reports, and update their profile information.

### Administrator
- **Access**: Full access to the system.
- **Features**: In addition to the regular user features, administrators can manage purchasing orders, supplier information, and have access to user management functionalities.

## Getting Started
1. Clone the repository:
    ```sh
    git clone https://github.com/CoverlessDev/uni-project.git
    ```
2. Navigate to the project directory:
    ```sh
    cd uni-project
    ```
3. Install the required libraries:
    ```sh
    pip install -r requirements.txt
    ```
4. Run the application:
    ```sh
    flask run
    ```

## License
This project is licensed under the MIT License.