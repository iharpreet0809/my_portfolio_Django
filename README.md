# Portfolio Django Application

A Django-based portfolio website with contact form functionality and admin panel with 2FA.

## Features

- **Contact Form**: Users can submit contact messages with CAPTCHA verification
- **Admin Panel**: Secure admin login with OTP-based two-factor authentication
- **Background Email Processing**: Contact form emails are sent asynchronously using Celery
- **Responsive Design**: Modern, responsive UI with Bootstrap

## Technology Stack

- **Backend**: Django 5.2.3
- **Database**: MySQL 8.0
- **Task Queue**: Celery with Redis
- **Email**: SMTP (Gmail)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap

## Setup Instructions

### Prerequisites

- Python 3.8+
- MySQL 8.0
- Redis (for Celery)

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd portfolio_django
   ```

2. **Create and activate virtual environment**

   ```bash
   python -m venv env
   # On Windows
   env\Scripts\activate
   # On macOS/Linux
   source env/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:

   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   EMAIL_HOST_PASSWORD=your-gmail-app-password
   REDIS_URL=redis://localhost:6379/0
   ```

5. **Database setup**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

### Running the Application

#### Option 1: Using Docker Compose (Recommended)

1. **Start all services**

   ```bash
   docker-compose up -d
   ```

   This will start:

   - Django web server (port 8000)
   - MySQL database (port 3306)
   - Redis (port 6379)
   - Celery worker
   - Celery beat (for scheduled tasks)

2. **View logs**

   ```bash
   docker-compose logs -f
   ```

3. **Stop services**
   ```bash
   docker-compose down
   ```

#### Option 2: Manual Setup

1. **Start Redis**

   ```bash
   # On Windows (using WSL or Docker)
   redis-server

   # On macOS
   brew services start redis

   # On Linux
   sudo systemctl start redis
   ```

2. **Start Celery worker** (in a separate terminal)

   ```bash
   celery -A portfolio_django worker --loglevel=info
   ```

3. **Start Django development server** (in another terminal)
   ```bash
   python manage.py runserver
   ```

## Background Email Processing

The application uses Celery to handle email sending asynchronously:

- **Contact Form**: When users submit the contact form, the email is queued and sent in the background
- **Admin OTP**: OTP emails for admin login are also sent asynchronously
- **Retry Logic**: Failed emails are automatically retried up to 3 times with 60-second delays

### Benefits

- **Faster Response**: Contact form submissions are instant
- **Reliability**: Failed emails are retried automatically
- **Scalability**: Can handle multiple email requests simultaneously
- **User Experience**: Users don't wait for email delivery

## Configuration

### Email Settings

Configure your email settings in `portfolio_django/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Use Gmail App Password
```

### Celery Settings

Celery is configured to use Redis as the message broker:

```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'django-db'
```

## Development

### Running Tests

```bash
python manage.py test
```

### Static Files

```bash
python manage.py collectstatic
```

### Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## Production Deployment

For production deployment:

1. Set `DEBUG=False` in environment variables
2. Configure production database settings
3. Set up proper email credentials
4. Configure Redis for production
5. Set up Celery workers as system services
6. Use a production WSGI server like Gunicorn

## Troubleshooting

### Common Issues

1. **Celery worker not starting**

   - Ensure Redis is running
   - Check Redis connection URL
   - Verify Celery configuration

2. **Emails not sending**

   - Check email credentials
   - Verify SMTP settings
   - Check Celery worker logs

3. **Database connection issues**
   - Verify MySQL is running
   - Check database credentials
   - Ensure database exists

### Logs

- Django logs: `logs/django.log`
- Celery logs: Check terminal output or Docker logs
- Redis logs: Check Redis server logs

## License

This project is licensed under the MIT License.

## 🔀 Merge dev → main

### Prerequisites

- Ensure you have committed all changes in your current branch
- Make sure you have push access to both branches

### Complete Merge Commands (Copy & Run)

```bash
# Ensure local branches up-to-date
git fetch origin
git checkout dev
git pull origin dev
git checkout main
git pull origin main

# Merge preferring incoming (dev). Use --allow-unrelated-histories only if needed.
git merge -X theirs dev --allow-unrelated-histories

# If merge finished with conflicts, run:
git checkout --theirs .
git add .
git commit -m "Merge dev into main — accept incoming (dev) changes"

# Push final result
git push origin main
```

### Quick Command Reference

```bash
# Complete merge in one go (if no conflicts expected)
git fetch origin && \
git checkout dev && git pull origin dev && \
git checkout main && git pull origin main && \
git merge -X theirs dev && \
git push origin main
```

### Troubleshooting

**Issue: Merge conflicts**

```bash
# View conflicted files
git status

# Accept all dev changes
git checkout --theirs .
git add .
git commit -m "Resolve conflicts - accept dev changes"
```

**Issue: Unrelated histories**

```bash
# Add --allow-unrelated-histories flag
git merge -X theirs dev --allow-unrelated-histories
```

**Issue: Need to abort merge**

```bash
# Cancel the merge and return to previous state
git merge --abort
```
