from flask import Flask, redirect, render_template, flash, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_required, logout_user, login_user, LoginManager, current_user

app = Flask(__name__)
app.secret_key = "Ansh"

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/accessportal'
db = SQLAlchemy(app)

# Login manager configuration
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Define models
class Student1(UserMixin, db.Model):
    __tablename__ = 'student1'
    rollno = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(100))

    def get_id(self):
        return str(self.rollno)

class Supervisor1(UserMixin, db.Model):
    __tablename__ = 'supervisor1'
    empcode = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(100))

    def get_id(self):
        return str(self.empcode)

class StudentLogin1(db.Model):
    __tablename__ = 'studentlogin1'
    rollno = db.Column(db.String(100), db.ForeignKey('student1.rollno'), primary_key=True)
    password = db.Column(db.String(100))

class SupervisorLogin1(db.Model):
    __tablename__ = 'supervisorlogin1'
    empcode = db.Column(db.String(100), db.ForeignKey('supervisor1.empcode'), primary_key=True)
    password = db.Column(db.String(100))

class Map1(db.Model):
    __tablename__ = 'map1'
    rollno = db.Column(db.String(100), db.ForeignKey('student1.rollno'), primary_key=True)
    empcode1 = db.Column(db.String(100), db.ForeignKey('supervisor1.empcode'))
    empcode2 = db.Column(db.String(100), db.ForeignKey('supervisor1.empcode'))

class Project1(db.Model):
    __tablename__ = 'project1'
    pid = db.Column(db.Integer, primary_key=True)
    ptitle = db.Column(db.String(500))
    pdesc = db.Column(db.String(2000))
    pobj = db.Column(db.String(2000))
    pwork = db.Column(db.String(2000))

class ProjectMap1(db.Model):
    __tablename__ = 'projectmap1'
    pid = db.Column(db.Integer, db.ForeignKey('project1.pid'), primary_key=True)
    rollno = db.Column(db.String(100), db.ForeignKey('student1.rollno'))

class GradeProject1(db.Model):
    __tablename__ = 'gradeproject1'
    pid = db.Column(db.Integer, db.ForeignKey('project1.pid'), primary_key=True)
    feedback1 = db.Column(db.String(2000))
    feedback2 = db.Column(db.String(2000))
    marks = db.Column(db.Integer)

class Admin(UserMixin, db.Model):
    adminid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))  # Store the hashed password if needed

    def get_id(self):
        return str(self.adminid)

# Load user
@login_manager.user_loader
def load_user(user_id):
    user = Student1.query.get(user_id) or Supervisor1.query.get(user_id) or Admin.query.get(user_id)
    return user

# Routes
@app.route("/")
def home():
    return render_template("index.html")

# Signup and login routes for students and supervisors
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        rollno = request.form.get('rollno')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = Student1.query.filter_by(rollno=rollno).first()
        emailUser = Student1.query.filter_by(email=email).first()
        if user or emailUser:
            flash("Email or Roll Number is already taken", "warning")
            return render_template("usersignup.html")
        
        new_user = Student1(rollno=rollno, email=email)
        new_login = StudentLogin1(rollno=rollno, password=password)
        db.session.add(new_user)
        db.session.add(new_login)
        db.session.commit()
        flash("SignUp Success - Please Login", "success")
        return render_template("userlogin.html")
    return render_template("usersignup.html")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        rollno = request.form.get('rollno')
        password = request.form.get('password')
        
        user = Student1.query.filter_by(rollno=rollno).first()
        login_details = StudentLogin1.query.filter_by(rollno=rollno, password=password).first()
        
        if user and login_details:
            login_user(user, remember=True)
            flash("Login Success", "info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials", "danger")
            return render_template("userlogin.html")
    return render_template("userlogin.html")

@app.route('/supervisorsignup', methods=['POST', 'GET'])
def supervisor_signup():
    if request.method == "POST":
        empcode = request.form.get('empcode')
        email = request.form.get('email')
        password = request.form.get('password')
        
        supervisor = Supervisor1.query.filter_by(empcode=empcode).first()
        emailUser = Supervisor1.query.filter_by(email=email).first()
        if supervisor or emailUser:
            flash("Email or Employee Code is already taken", "warning")
            return render_template("supervisorsignup.html")
        
        new_supervisor = Supervisor1(empcode=empcode, email=email)
        new_login = SupervisorLogin1(empcode=empcode, password=password)
        db.session.add(new_supervisor)
        db.session.add(new_login)
        db.session.commit()
        flash("SignUp Success - Please Login", "success")
        return render_template("supervisorlogin.html")
    return render_template("supervisorsignup.html")

@app.route('/supervisorlogin', methods=['POST', 'GET'])
def supervisor_login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Find supervisor by email instead of empcode
        supervisor = Supervisor1.query.filter_by(email=email).first()
        login_details = SupervisorLogin1.query.filter_by(empcode=supervisor.empcode, password=password).first() if supervisor else None
        
        if supervisor and login_details:
            login_user(supervisor, remember=True)
            flash("Login Success", "info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials", "danger")
            return render_template("supervisorlogin.html")
    return render_template("supervisorlogin.html")

@app.route('/studentmygroup')
@login_required
def studentmygroup():
    # Get the student information using the current logged-in user
    student = Student1.query.filter_by(email=current_user.email).first()
    
    if student:
        # Get supervisor mapping from Map1 based on student rollno
        student_info = Map1.query.filter_by(rollno=student.rollno).first()
        
        # Get supervisor details using empcodes related to the student
        supervisor1 = Supervisor1.query.filter_by(empcode=student_info.empcode1).first()
        supervisor2 = Supervisor1.query.filter_by(empcode=student_info.empcode2).first()

        return render_template("studentmygroup.html", student=student, supervisor1=supervisor1, supervisor2=supervisor2)
    else:
        # Handle case where no student data is found (optional)
        return render_template("error.html", message="Student data not found.")

@app.route('/supervisormygroup')
@login_required
def supervisormygroup():
    # Get the supervisor information using the current logged-in user
    supervisor = Supervisor1.query.filter_by(email=current_user.email).first()
    
    if supervisor:
        # Find all students assigned to this supervisor (empcode1 and empcode2)
        students_info = Map1.query.filter(
            (Map1.empcode1 == supervisor.empcode) | (Map1.empcode2 == supervisor.empcode)
        ).all()

        students = []
        for student_info in students_info:
            # Get the student details using roll number
            student = Student1.query.filter_by(rollno=student_info.rollno).first()
            if student:
                students.append(student)

        # Assuming Map1 holds both supervisor mappings, fetch supervisor details
        # Fetch the second supervisor (if assigned in the Map1 table)
        first_supervisor = Supervisor1.query.filter_by(empcode=students_info[0].empcode1).first() if students_info else None
        second_supervisor = Supervisor1.query.filter_by(empcode=students_info[0].empcode2).first() if students_info else None

        return render_template("supervisormygroup.html", supervisor=supervisor, first_supervisor=first_supervisor, second_supervisor=second_supervisor, students=students)
    else:
        # Handle case where no supervisor data is found (optional)
        return render_template("error.html", message="Supervisor data not found.")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout Successful", "warning")
    return redirect(url_for('login'))

@app.route('/supervisorlogout')
@login_required
def supervisorlogout():
    logout_user() 
    flash("Logout SuccessFul", "warning")
    return redirect(url_for('supervisor_login'))

@app.route('/adminlogout')
@login_required
def adminlogout():
    logout_user()
    flash("Logout Successful", "warning")
    return redirect(url_for('adminlogin'))

@app.route('/studentprojectportal')
@login_required
def projectportal():
    # Check if the current user has a PID linked to them in the ProjectMap1 table
    if isinstance(current_user, Student1):
        # Look for a project associated with the current student's roll number
        project_map = ProjectMap1.query.filter_by(rollno=current_user.rollno).first()
        if project_map:
            pid = project_map.pid  # Get the PID from the project map table
        else:
            pid = None  # No project associated with the student
    else:
        pid = None  # If the current user is not a student, set pid as None

    # Print the pid to the console for debugging
    print(f"PID in session: {pid}")
    
    # Pass the PID to the template
    return render_template("studentprojectportal.html", pid=pid)

@app.route('/changepassword', methods=['POST', 'GET'])
@login_required
def change_password():
    if request.method == "POST":
        current_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash("New Password and Confirm Password do not match", "danger")
            return render_template("change_password.html")
        
        if isinstance(current_user, Student1):
            user_login = StudentLogin1.query.filter_by(rollno=current_user.rollno).first()
        else:
            user_login = SupervisorLogin1.query.filter_by(empcode=current_user.empcode).first()
        
        if user_login and user_login.password == current_password:
            user_login.password = new_password
            db.session.commit()
            flash("Password Changed Successfully", "success")
        else:
            flash("Current Password is incorrect", "danger")
    return render_template("change_password.html")

@app.route('/studentdata')
@login_required
def studentdata():
    return render_template("studentdata.html")

@app.route('/supervisordata')
@login_required
def supervisordata():
    return render_template("supervisordata.html")

# Project management routes
@app.route('/uploadproject', methods=['POST', 'GET'])
@login_required
def upload_project():
    if request.method == "POST":
        ptitle = request.form.get('ptitle')
        pdesc = request.form.get('pdesc')
        pobj = request.form.get('pobj')
        pwork = request.form.get('pwork')
        
        new_project = Project1(ptitle=ptitle, pdesc=pdesc, pobj=pobj, pwork=pwork)
        db.session.add(new_project)
        db.session.commit()
        
        # Link project to the student
        new_project_map = ProjectMap1(pid=new_project.pid, rollno=current_user.rollno)
        db.session.add(new_project_map)
        db.session.commit()
        
        flash("Project Uploaded Successfully", "success")
        
        # Redirect to the /studentprojectportal page after successful upload
        return redirect(url_for('projectportal'))
    
    return render_template("uploadproject.html")


# Review project routes
@app.route('/reviewproject')
@login_required
def review_project():
    
    return render_template("gradeproject.html")

@app.route('/adminlogin', methods=['POST', 'GET'])
def adminlogin():
    if request.method == "POST":
        username = request.form.get('username')  # Get username instead of admin_id
        password = request.form.get('password')
        
        # Validate admin credentials by username
        admin = Admin.query.filter_by(username=username).first()
        
        # Check the password (use check_password_hash if the password is hashed)
        if admin and admin.password == password:  # Adjust if passwords are hashed
            login_user(admin, remember=True)
            flash("Admin Login Success", "info")
            return render_template("index.html")
        else:
            flash("Invalid Admin Credentials", "danger")
            return render_template("adminlogin.html")
    return render_template("adminlogin.html")

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
