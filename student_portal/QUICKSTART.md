# Quick Start Guide - Student Portal

## 🚀 Getting Started in 5 Minutes

### Option 1: Automated Setup (Recommended)

**For Windows:**
1. Double-click `setup.bat`
2. Follow the prompts to create an admin account
3. Run: `venv\Scripts\activate` then `python manage.py runserver`
4. Open browser: http://127.0.0.1:8000/

**For macOS/Linux:**
1. Open terminal in project folder
2. Run: `chmod +x setup.sh && ./setup.sh`
3. Follow the prompts to create an admin account
4. Run: `source venv/bin/activate` then `python manage.py runserver`
5. Open browser: http://127.0.0.1:8000/

### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup database
python manage.py migrate

# 5. Create admin account
python manage.py createsuperuser

# 6. Run server
python manage.py runserver
```

## 📝 First Steps After Installation

### 1. Access Admin Panel
- URL: http://127.0.0.1:8000/admin/
- Login with the superuser credentials you created
- Add sample data (courses, students, quizzes)

### 2. Create Sample Data

#### Add Courses:
1. Go to Admin → Courses → Add Course
2. Fill in: Code (e.g., CS101), Name, Credits, Semester
3. Save

#### Add Students:
1. Create a regular user account (not superuser)
2. Go to Admin → Students → Add Student
3. Link to the user and fill in details
4. Save

#### Enroll Students:
1. Go to Admin → Enrollments → Add Enrollment
2. Select student and course
3. Save

#### Create Quiz:
1. Go to Admin → Quizzes → Add Quiz
2. Fill in quiz details
3. Save
4. Add Questions to the quiz
5. Add Choices for each question (mark correct answers)

### 3. Test the Portal

1. **Student Login:**
   - Go to http://127.0.0.1:8000/
   - Click Register or Login
   - Login with a student account

2. **Explore Features:**
   - Dashboard: View overview
   - Courses: See enrolled courses
   - Quizzes: Take available quizzes
   - Results: Check grades

## 🎯 Sample Login Flow

```
1. Homepage → Register
2. Create student account
3. Admin adds student profile via admin panel
4. Admin enrolls student in courses
5. Admin creates quiz
6. Student logs in → Dashboard
7. Student takes quiz
8. Student views results
```

## 🔧 Common Commands

```bash
# Run development server
python manage.py runserver

# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run tests
python manage.py test

# Access Django shell
python manage.py shell
```

## 📚 Default URLs

- Homepage: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/
- Login: http://127.0.0.1:8000/login/
- Dashboard: http://127.0.0.1:8000/dashboard/
- Quizzes: http://127.0.0.1:8000/quiz/
- Courses: http://127.0.0.1:8000/academics/courses/

## ⚠️ Troubleshooting

**Issue:** "Module not found" error
- **Solution:** Activate virtual environment and run `pip install -r requirements.txt`

**Issue:** "Table doesn't exist" error
- **Solution:** Run `python manage.py migrate`

**Issue:** Static files not loading
- **Solution:** Run `python manage.py collectstatic`

**Issue:** Can't access admin panel
- **Solution:** Make sure you created a superuser with `python manage.py createsuperuser`

## 🎓 Creating Your First Quiz

1. Login to admin panel
2. Go to Quizzes → Add Quiz
3. Fill in:
   - Title: "Python Basics Quiz"
   - Course: Select a course
   - Duration: 30 minutes
   - Total Marks: 10
   - Passing Marks: 6
   - Start/End times
4. Click Save
5. In the quiz page, click "Add Question"
6. Create question:
   - Type: Multiple Choice
   - Question: "What is Python?"
   - Marks: 2
7. Save and add 4 choices
8. Mark the correct choice
9. Repeat for more questions
10. Students can now take the quiz!

## 📱 Mobile Responsive

The portal is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones

## 🔒 Security Notes

For production:
1. Change SECRET_KEY in settings.py
2. Set DEBUG = False
3. Add your domain to ALLOWED_HOSTS
4. Use HTTPS
5. Use a production database (PostgreSQL/MySQL)

## 📧 Need Help?

Check the full README.md for:
- Detailed documentation
- Feature descriptions
- Advanced configuration
- Deployment guide

---

Happy Learning! 🎓
