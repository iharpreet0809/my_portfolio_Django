# Django Portfolio Application

A modern, feature-rich portfolio website built with Django, featuring a contact form and Docker deployment.

## 🚀 Features

### Core Features
- **Portfolio Homepage**: Professional landing page with contact form
- **Contact Form**: Email notifications for visitor inquiries
- **Admin Interface**: Full Django admin for content management
- **Responsive Design**: Mobile-friendly Bootstrap-based UI

### Technical Features
- **Docker Deployment**: Containerized application with Docker Compose
- **MySQL Database**: Production-ready database setup
- **Nginx Reverse Proxy**: Efficient static file serving and load balancing
- **Gunicorn**: Production WSGI server
- **Email Integration**: SMTP email notifications
- **SEO Optimized**: Meta tags and structured content

## 🏗️ Architecture

### Project Structure
```
portfolio_django/
├── portfolio_app/          # Main Django application
│   ├── models.py          # Database models (Contact, Category, Author)
│   ├── views.py           # View functions for handling requests
│   ├── forms.py           # Django forms for user input
│   ├── urls.py            # URL routing configuration
│   ├── admin.py           # Django admin interface configuration
│   └── templates/         # HTML templates
├── portfolio_django/       # Django project settings
│   ├── settings.py        # Django configuration
│   ├── urls.py            # Main URL configuration
│   └── wsgi.py            # WSGI application entry point
├── static/                # Static files (CSS, JS, images)
├── mediafiles/            # User-uploaded files
├── Dockerfile             # Docker image configuration
├── docker-compose.yml     # Multi-container application setup
├── nginx.conf             # Nginx reverse proxy configuration
└── requirements.txt       # Python dependencies
```

### Technology Stack
- **Backend**: Django 5.2.3 (Python web framework)
- **Database**: MySQL 8.0
- **Web Server**: Nginx (reverse proxy) + Gunicorn (WSGI server)
- **Containerization**: Docker & Docker Compose
- **Frontend**: Bootstrap, jQuery, custom CSS/JS
- **Image Processing**: Pillow

## 🛠️ Installation & Setup

### Prerequisites
- Docker and Docker Compose
- Git

### Quick Start (Docker)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd portfolio_django
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the application**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Website: http://localhost:8888
   - Admin: http://localhost:8888/admin

### Local Development Setup

1. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up MySQL database**
   ```bash
   # Create database and user
   mysql -u root -p
   CREATE DATABASE my_portfolio;
   CREATE USER 'portfolio_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON my_portfolio.* TO 'portfolio_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. **Configure Django settings**
   ```bash
   # Update database settings in portfolio_django/settings.py
   # Set DEBUG = True for development
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```

## 📝 Configuration

### Environment Variables
Create a `.env` file with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
DJANGO_SETTINGS_MODULE=portfolio_django.settings

# Database Settings
MYSQL_ROOT_PASSWORD=your-root-password
MYSQL_DATABASE=my_portfolio
MYSQL_USER=portfolio_user
MYSQL_PASSWORD=your-database-password
MYSQL_HOST=mysql

# Email Settings (for contact form)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Email Configuration
The contact form uses Gmail SMTP. To set up:
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password
3. Update the email settings in `settings.py`

## 🗄️ Database Models

### Contact Model
- Stores contact form submissions
- Fields: name, email, subject, message, created_at

### Category Model
- Organizes content into categories
- Fields: name, slug, description, timestamps

### Author Model
- Extends Django User model with additional info
- Fields: bio, profile_picture, social media links

## 🔧 Management Commands

### Database Operations
```bash
# Apply migrations
python manage.py migrate

# Create new migration
python manage.py makemigrations

# Reset database
python manage.py flush
```

### Static Files
```bash
# Collect static files
python manage.py collectstatic

# Clear static files
python manage.py collectstatic --clear
```

### User Management
```bash
# Create superuser
python manage.py createsuperuser

# Change password
python manage.py changepassword
```

## 🐳 Docker Commands

### Container Management
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild containers
docker-compose up --build

# Access Django container
docker-compose exec django bash

# Access MySQL container
docker-compose exec mysql mysql -u root -p
```

### Database Operations
```bash
# Backup database
docker-compose exec mysql mysqldump -u root -p my_portfolio > backup.sql

# Restore database
docker-compose exec -T mysql mysql -u root -p my_portfolio < backup.sql
```

## 📊 Performance Optimization

### Database Optimization
- Use `select_related()` for foreign key relationships
- Use `prefetch_related()` for many-to-many relationships
- Implement database indexing for frequently queried fields

### Static Files
- Nginx serves static files directly (more efficient than Django)
- Use `collectstatic` to gather all static files in production
- Consider CDN for global static file delivery

### Caching
- Implement Redis caching for frequently accessed data
- Use Django's caching framework for view caching
- Cache database queries where appropriate

## 🔒 Security Considerations

### Production Security
- Set `DEBUG = False` in production
- Use strong `SECRET_KEY`
- Configure `ALLOWED_HOSTS` properly
- Enable HTTPS with SSL certificates
- Use environment variables for sensitive data
- Regular security updates

### Database Security
- Use strong database passwords
- Limit database user privileges
- Regular database backups
- Monitor database access logs

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test portfolio_app

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 📈 Monitoring & Logging

### Application Logs
- Django logs are available in container logs
- Use `docker-compose logs -f django` to monitor

### Database Monitoring
- Monitor MySQL performance with built-in tools
- Set up database backup automation

### Error Tracking
- Consider integrating Sentry for error tracking
- Monitor application performance metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the Django documentation
- Review the code comments for implementation details

## 🔄 Updates & Maintenance

### Regular Maintenance Tasks
- Update Django and dependencies regularly
- Monitor security advisories
- Backup database regularly
- Review and update Docker images
- Monitor application performance

### Version Updates
- Test updates in development environment first
- Follow Django's upgrade guide for major version changes
- Update requirements.txt with new versions
- Test all functionality after updates 
