# ChatMinds UI

ChatMinds UI is a web application designed to manage tenants, users, and documents, with support for user authentication and role-based access control. This project uses Flask for the backend and SQLite for the database.

## Features

- **User Authentication**: Register, login, and logout functionality.
- **Role-Based Access Control**: Different functionalities for admin and regular users.
- **Tenant Management**: Admins can add, edit, and delete tenants.
- **User Management**: Admins can view and delete users.
- **Document Management**: Users can upload, view, and delete documents.

## Getting Started

### Prerequisites

- Python 3.x
- Flask
- SQLite

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/chatminds-ui.git
   cd chatminds-ui
   ```
   
2. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows use `venv\Scripts\activate`
   ```

3. **Install the dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

### Setup

1. **Create the necessary database tables:**

   Open your browser and navigate to [http://127.0.0.1:5000/create_tables](http://127.0.0.1:5000/create_tables). This will create the required tables in your SQLite database.

2. **Seed the database with an admin user:**

   Open your browser and navigate to [http://127.0.0.1:5000/seed](http://127.0.0.1:5000/seed). This will create an admin user with the following credentials:

   - Username: admin
   - Password: admin

### Running the Application

1. **Start the Flask server:**

   ```bash
   flask run
   ```

2. By default, the application will be accessible at [http://127.0.0.1:5000](http://127.0.0.1:5000).

### Application Structure

- `app.py`: Main application file containing route definitions and logic.
- `templates/`: Directory containing HTML templates for rendering pages.
- `static/`: Directory containing static files like CSS and JavaScript.
- `data/`: Directory where uploaded documents are stored.

### API Endpoints

**User Management**

- Register User: `POST /register`
- Login User: `POST /login`
- Logout User: `GET /logout`
- Get All Users: `GET /users`
- Get User by ID: `GET /get_user/<user_id>`
- Delete User: `DELETE /delete_user/<user_id>`

**Tenant Management**

- Add Tenant: `POST /add_tenant`
- Get All Tenants: `GET /get_all_tenants`
- Edit Tenant: `PUT /edit_tenant/<tenant_id>`
- Delete Tenant: `DELETE /delete_tenant/<tenant_id>`

**Document Management**

- Get Documents by Tenant: `GET /documents/<tenant_id>`
- Add Document: `POST /add_document/<tenant_id>`
- Delete Document: `DELETE /delete_document/<document_id>`
- View Document: `GET /view_document/<document_id>/tenant/<tenant_id>`

### Templates

- `login.html`: Login page.
- `register.html`: Registration page.
- `index.html`: Homepage for admin users.
- `tenant_data.html`: Tenant details page.
- `user_data.html`: Admin page for viewing all users.
- `user_profile.html`: User profile page.
- `load_documents.html`: Page for uploading and viewing documents.

### Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

### License

This project is licensed under the MIT License.

---

This `README.md` file provides a detailed guide for setting up and using the ChatMinds UI project, making it easy for users to understand and get started with the application.