# Vaccination Management System

A Django-based web application for managing vaccination campaigns, user registrations, bookings, and reviews. This project leverages Django REST Framework (DRF) and drf-spectacular for robust API development and OpenAPI schema generation.

## Features
- User registration, login, and JWT-based authentication
- User profile management and password change
- Vaccination campaign management
- Booking system for vaccination appointments
- Review system for campaigns or services
- OpenAPI 3.0 schema generation and interactive API docs (Swagger UI)

## Tech Stack
- Python 3.10+
- Django 5.x
- Django REST Framework
- drf-spectacular (OpenAPI schema)
- SimpleJWT (JWT authentication)
- SQLite (default, can be swapped for PostgreSQL/MySQL)

## Project Structure
```
Vaccination Management System/
├── Vaccination_Management_System/   # Main Django project settings
├── api/                            # App for campaign, booking, review APIs
├── users/                          # App for user management (auth, profile)
├── manage.py                       # Django management script
├── db.sqlite3                      # SQLite database (default)
```

## Setup Instructions

### 1. Clone the repository
```bash
git clone <repo-url>
cd 'Vaccination Management System'
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply migrations
```bash
python manage.py migrate
```

### 5. Create a superuser (admin)
```bash
python manage.py createsuperuser
```

### 6. Run the development server
```bash
python manage.py runserver
```

### 7. Access the application
- API root: [http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/)
- Admin panel: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- API schema (OpenAPI): [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)
- Swagger UI: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)

## API Endpoints
- User registration: `/api/auth/users/register/`
- User login: `/api/auth/users/login/`
- Profile: `/api/auth/profile/`
- Change password: `/api/auth/change-password/`
- Token obtain/refresh: `/api/auth/token/`, `/api/auth/token/refresh/`
- Campaigns: `/api/campaigns/`
- Bookings: `/api/bookings/`
- Reviews: `/api/reviews/`

## Environment Variables
- All sensitive settings (e.g., SECRET_KEY) should be managed via environment variables in production.

## Development Notes
- The project uses drf-spectacular for OpenAPI schema generation. Ensure `DEFAULT_SCHEMA_CLASS` is set in `settings.py`.
- JWT authentication is enabled via SimpleJWT.
- Default database is SQLite; update `DATABASES` in `settings.py` for production.

## License
This project is licensed under the MIT License.

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## Contact
For questions or support, please open an issue on the repository.

