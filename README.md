# Vaccination Management System

A comprehensive Django-based web application for managing vaccination campaigns, user registrations, bookings, premium services, and integrated payment processing. This system supports both regular vaccination bookings and premium services with SSL Commerz payment gateway integration.

## 🚀 Features

### Core Features
- **User Management**: Role-based authentication (Patients & Doctors) with JWT-based authentication
- **User Profiles**: Comprehensive profile management with medical history and contact details
- **Vaccination Campaigns**: Create and manage vaccination campaigns with multi-dose scheduling
- **Booking System**: Advanced booking system with regular and premium service options
- **Review System**: Campaign and service review system
- **Payment Integration**: SSL Commerz payment gateway for premium services

### Premium Services
- **Priority Booking**: Skip queues with priority scheduling
- **Home Vaccination**: Doorstep vaccination services
- **Express Services**: Fast-track vaccination processing
- **Premium Vaccine Packages**: Enhanced vaccine options
- **VIP Medical Consultations**: Personalized medical consultations

### Payment Features
- SSL Commerz payment gateway integration
- Multiple payment methods (Card, Mobile Banking, Net Banking)
- Payment tracking and transaction management
- Refund processing
- Secure payment processing with comprehensive logging

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, Django 5.2.5
- **API**: Django REST Framework
- **Authentication**: JWT (SimpleJWT)
- **Documentation**: drf-spectacular (OpenAPI 3.0/Swagger)
- **Database**: SQLite (development), PostgreSQL (production)
- **Payment Gateway**: SSL Commerz
- **File Handling**: Pillow for image processing
- **Static Files**: WhiteNoise
- **Environment**: python-dotenv for configuration

## 📁 Project Structure

```
Vaccination Management System/
├── Vaccination_Management_System/   # Main Django project settings
│   ├── settings.py                 # Project configuration
│   ├── urls.py                     # Main URL routing
│   └── wsgi.py                     # WSGI configuration
├── api/                            # Core vaccination management APIs
│   ├── models.py                   # Campaign, Booking, PremiumService models
│   ├── views.py                    # API views
│   ├── serializers.py              # Data serialization
│   └── management/commands/        # Custom management commands
├── users/                          # User management and authentication
│   ├── models.py                   # Custom User model with roles
│   ├── views.py                    # Authentication views
│   └── serializers.py              # User serialization
├── payments/                       # Payment processing system
│   ├── models.py                   # Payment and refund models
│   ├── services.py                 # SSL Commerz integration
│   ├── views.py                    # Payment API endpoints
│   └── management/commands/        # Payment-related commands
├── static/                         # Static files
├── staticfiles/                    # Collected static files
├── requirements.txt                # Python dependencies
├── manage.py                       # Django management script
├── db.sqlite3                      # SQLite database (development)
├── PAYMENT_INTEGRATION.md          # Payment integration documentation
└── README.md                       # This file
```

## 🚀 Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd "Vaccination Management System"
```

### 2. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the project root:
```env
# Django Settings
SECRET_KEY="your-secret-key-here"
DEBUG="True"
ALLOWED_HOSTS="localhost,127.0.0.1"

# Database Settings (optional)
USE_SQLITE="True"
# POSTGRES_URL="postgresql://user:password@localhost:5432/vaccination_db"

# SSL Commerz Payment Gateway
SSLCOMMERZ_STORE_ID="your_store_id"
SSLCOMMERZ_STORE_PASSWORD="your_store_password"
SSLCOMMERZ_IS_SANDBOX="True"  # Set to False for production

# Frontend URL
FRONTEND_URL="http://localhost:3000"
```

### 5. Database Setup
```bash
# Apply database migrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser

# Populate premium services (optional)
python manage.py migrate_premium_services
```

### 6. Run Development Server
```bash
python manage.py runserver
```

### 7. Access the Application
- **API Root**: [http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/)
- **Admin Panel**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- **API Documentation**: [http://127.0.0.1:8000/api/schema/swagger-ui/](http://127.0.0.1:8000/api/schema/swagger-ui/)
- **OpenAPI Schema**: [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)

## 📡 API Endpoints

### Authentication
- `POST /api/auth/users/register/` - User registration
- `POST /api/auth/users/login/` - User login
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/` - Update user profile
- `POST /api/auth/change-password/` - Change password
- `POST /api/auth/token/` - Obtain JWT token
- `POST /api/auth/token/refresh/` - Refresh JWT token

### Vaccination Management
- `GET /api/campaigns/` - List vaccination campaigns
- `POST /api/campaigns/` - Create new campaign (Admin/Doctor)
- `GET /api/campaigns/{id}/` - Get campaign details
- `GET /api/bookings/` - List user bookings
- `POST /api/bookings/` - Create new booking
- `GET /api/bookings/{id}/` - Get booking details
- `PUT /api/bookings/{id}/` - Update booking

### Premium Services & Payments
- `GET /api/payments/services/` - List premium services
- `GET /api/payments/services/?service_type=PRIORITY_BOOKING` - Filter services
- `POST /api/payments/bookings/` - Create premium booking
- `POST /api/payments/initiate/` - Initiate payment
- `POST /api/payments/success/` - Payment success callback
- `POST /api/payments/fail/` - Payment failure callback
- `POST /api/payments/cancel/` - Payment cancellation callback

### Reviews
- `GET /api/reviews/` - List reviews
- `POST /api/reviews/` - Create review
- `GET /api/reviews/{id}/` - Get review details

## 💳 Payment Integration

The system integrates with SSL Commerz payment gateway for processing premium service payments. See [PAYMENT_INTEGRATION.md](PAYMENT_INTEGRATION.md) for detailed setup instructions.

### Supported Payment Methods
- Credit/Debit Cards
- Mobile Banking (bKash, Rocket, etc.)
- Net Banking
- SSL Commerz gateway

## 🔧 Configuration

### Database Configuration
- **Development**: SQLite (default)
- **Production**: PostgreSQL (recommended)

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Required |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Allowed hosts | `*` |
| `USE_SQLITE` | Use SQLite database | `True` |
| `SSLCOMMERZ_STORE_ID` | SSL Commerz store ID | Required for payments |
| `SSLCOMMERZ_STORE_PASSWORD` | SSL Commerz password | Required for payments |
| `SSLCOMMERZ_IS_SANDBOX` | Use sandbox mode | `True` |
| `FRONTEND_URL` | Frontend application URL | `http://localhost:3000` |

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test api
python manage.py test users
python manage.py test payments

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## 📝 Development Notes

- **API Documentation**: Automatically generated using drf-spectacular
- **Authentication**: JWT-based authentication with refresh tokens
- **File Uploads**: Configured for profile pictures and documents
- **Logging**: Comprehensive logging for payment transactions
- **Security**: CSRF protection and secure payment processing

## 🚀 Deployment

### Production Checklist
1. Set `DEBUG=False` in production
2. Configure proper database (PostgreSQL recommended)
3. Set up SSL certificates for HTTPS
4. Configure static file serving
5. Set proper `ALLOWED_HOSTS`
6. Use production SSL Commerz credentials
7. Set up proper logging and monitoring

### Docker Deployment (Optional)
```dockerfile
# Example Dockerfile structure
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "Vaccination_Management_System.wsgi:application"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive tests for new features
- Update documentation for API changes
- Ensure all tests pass before submitting PR

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For questions, issues, or support:
- Open an issue on GitHub
- Check the [PAYMENT_INTEGRATION.md](PAYMENT_INTEGRATION.md) for payment-related queries
- Review API documentation at `/api/schema/swagger-ui/`

## 🔄 Version History

- **v1.0.0**: Initial release with basic vaccination management
- **v2.0.0**: Added premium services and SSL Commerz payment integration
- **Current**: Enhanced booking system with comprehensive payment processing

---

**Note**: This system handles sensitive medical and payment data. Ensure proper security measures are in place before deploying to production.
