# Student Portal - One Stop Academic Solution

A comprehensive web-based student management system with academic tracking and online quiz portal built with Django.

## 🎓 Features

### Academic Management
- **Dashboard**: Comprehensive overview of academic performance
- **Course Management**: View enrolled courses and course details
- **Attendance Tracking**: Monitor attendance with percentage calculations
- **Assignment Management**: Submit assignments and track deadlines
- **Results & Grades**: View exam results and grade reports
- **Timetable**: Weekly class schedule

### Quiz Portal
- **Online Quizzes**: Take timed online assessments
- **Multiple Question Types**: 
  - Multiple Choice Questions (MCQ)
  - True/False Questions
  - Short Answer Questions
- **Timer Functionality**: Auto-submit when time expires
- **Instant Results**: View results immediately after submission
- **Quiz History**: Track all quiz attempts and scores

## 🛠️ Tech Stack

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling
- **Bootstrap 5** - Responsive UI framework
- **JavaScript** - Client-side interactivity
- **jQuery** - DOM manipulation and effects
- **Font Awesome** - Icons

### Backend
- **Django 4.2.7** - Web framework
- **Python 3.8+** - Programming language

### Database
- **SQLite** - Default database (can be changed to PostgreSQL/MySQL)

## 📁 Project Structure

```
student_portal/
├── config/                 # Project configuration
│   ├── settings.py        # Django settings
│   ├── urls.py           # Main URL configuration
│   ├── wsgi.py           # WSGI configuration
│   └── asgi.py           # ASGI configuration
├── academics/             # Academic management app
│   ├── models.py         # Student, Course, Attendance, etc.
│   ├── views.py          # View functions
│   ├── urls.py           # URL patterns
│   └── admin.py          # Admin configuration
├── quiz/                  # Quiz portal app
│   ├── models.py         # Quiz, Question, Answer, etc.
│   ├── views.py          # Quiz logic
│   ├── urls.py           # Quiz URLs
│   └── admin.py          # Quiz admin
├── templates/             # HTML templates
│   ├── base/             # Base templates
│   ├── academics/        # Academic templates
│   ├── quiz/             # Quiz templates
│   └── auth/             # Authentication templates
├── static/                # Static files
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript files
│   └── images/           # Images
├── media/                 # User uploaded files
├── manage.py             # Django management script
└── requirements.txt      # Python dependencies
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git (optional)

### Step 1: Clone or Download the Project
```bash
# If using git
git clone <repository-url>
cd student_portal

# Or download and extract the ZIP file
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Database Setup
```bash
# Create database tables
python manage.py makemigrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser
```

### Step 5: Create Static Files Directory
```bash
python manage.py collectstatic --noinput
```

### Step 6: Run Development Server
```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## 👤 Default Admin Access

After creating a superuser, access the admin panel at:
- URL: `http://127.0.0.1:8000/admin/`
- Username: (what you entered during superuser creation)
- Password: (what you entered during superuser creation)

## 📚 Usage Guide

### For Students

1. **Registration**:
   - Navigate to the registration page
   - Create an account with username and password
   - Complete your student profile

2. **Dashboard**:
   - View overall academic performance
   - Check attendance statistics
   - See upcoming assignments and exams

3. **Courses**:
   - View all enrolled courses
   - Check course details and timetable

4. **Attendance**:
   - Monitor attendance for each course
   - View detailed attendance records

5. **Assignments**:
   - View all assignments
   - Submit assignments before deadline
   - Track submission status

6. **Quizzes**:
   - View available quizzes
   - Take timed online quizzes
   - View results and scores

7. **Results**:
   - Check exam results
   - View grades and performance

### For Administrators

Use the Django admin panel to:

1. **Manage Students**:
   - Add/edit student profiles
   - Set registration numbers, branch, semester

2. **Manage Courses**:
   - Create courses with code, name, credits
   - Set course descriptions

3. **Manage Enrollments**:
   - Enroll students in courses

4. **Record Attendance**:
   - Mark attendance for students
   - Set status: Present, Absent, Late

5. **Create Assignments**:
   - Add assignments with deadlines
   - Set maximum marks
   - Upload assignment files

6. **Create Quizzes**:
   - Create quizzes with title, duration
   - Add questions (MCQ, True/False, Short Answer)
   - Set start and end times
   - Configure passing marks

7. **Manage Results**:
   - Enter exam results
   - Grades auto-calculated based on marks

8. **Set Timetable**:
   - Create class schedules
   - Set day, time, and room

## 🎨 Customization

### Changing Colors/Theme
Edit `static/css/style.css` to modify:
- Color schemes
- Font styles
- Layout spacing
- Card designs

### Adding New Features
1. Create new models in `models.py`
2. Create views in `views.py`
3. Add URL patterns in `urls.py`
4. Create templates in `templates/`

### Modifying Database
To use PostgreSQL or MySQL instead of SQLite:
1. Install database driver:
   ```bash
   pip install psycopg2-binary  # For PostgreSQL
   # or
   pip install mysqlclient  # For MySQL
   ```
2. Update `DATABASES` in `config/settings.py`

## 🔒 Security Considerations

For production deployment:

1. **Change Secret Key**:
   - Generate a new secret key in `settings.py`
   - Never commit secret keys to version control

2. **Set DEBUG = False**:
   - Change `DEBUG = False` in production
   - Set proper `ALLOWED_HOSTS`

3. **Use HTTPS**:
   - Deploy with SSL certificate
   - Set secure cookie flags

4. **Environment Variables**:
   - Use environment variables for sensitive data
   - Consider using python-decouple or django-environ

5. **Database Security**:
   - Use strong database passwords
   - Restrict database access

## 📝 Sample Data

To populate the system with sample data:

1. Login to admin panel
2. Create some sample courses
3. Create student profiles
4. Enroll students in courses
5. Create quizzes with questions
6. Record some attendance
7. Add exam results

## 🐛 Troubleshooting

### Common Issues

1. **ImportError: No module named 'django'**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

2. **Database errors**
   - Delete `db.sqlite3` and run migrations again
   - Ensure migrations are created and applied

3. **Static files not loading**
   - Run `python manage.py collectstatic`
   - Check `STATIC_URL` and `STATIC_ROOT` in settings

4. **Template not found**
   - Verify template paths in `TEMPLATES['DIRS']`
   - Check template file names match view references

## 🔄 Updates & Maintenance

### Database Migrations
When making model changes:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Backup Database
```bash
# For SQLite
cp db.sqlite3 db.sqlite3.backup

# Export data
python manage.py dumpdata > backup.json

# Import data
python manage.py loaddata backup.json
```

## 📄 License

This project is created for educational purposes.

## 🤝 Contributing

Feel free to fork this project and submit pull requests for any improvements.

## 📧 Support

For issues and questions:
1. Check the troubleshooting section
2. Review Django documentation
3. Create an issue in the repository

## 🎯 Future Enhancements

Potential features to add:
- Email notifications for assignments and quizzes
- Discussion forums
- Library management
- Fee payment integration
- Mobile app
- API for third-party integrations
- Advanced analytics and reports
- PDF generation for transcripts
- Multi-language support
- Dark mode theme

## ⚡ Performance Tips

1. Use database indexing for frequently queried fields
2. Implement caching for static data
3. Optimize queries with `select_related()` and `prefetch_related()`
4. Use pagination for large datasets
5. Compress and minify CSS/JS files

## 📊 Models Overview

### Academics App Models
- **Student**: Student profile information
- **Course**: Course details
- **Enrollment**: Student-course relationship
- **Attendance**: Daily attendance records
- **Assignment**: Assignment information
- **Submission**: Student assignment submissions
- **Exam**: Exam details
- **Result**: Student exam results
- **Timetable**: Class schedule

### Quiz App Models
- **Quiz**: Quiz configuration
- **Question**: Quiz questions
- **Choice**: Answer choices for questions
- **QuizAttempt**: Student quiz attempts
- **Answer**: Student answers to questions

---

**Built with ❤️ using Django**
