from app import db, login_manager
from flask_admin.contrib.sqla import ModelView

class SucceededCourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    course_acronym = db.Column(db.String(10), nullable=False)
    course_title = db.Column(db.String(150), nullable=False)
    bloc = db.Column(db.String(10), nullable=False)
    cts = db.Column(db.Integer(), nullable=False)
    other_out_program = db.Column(db.Boolean(), nullable=False, default=False)
    other_minor = db.Column(db.Boolean(), nullable=False, default=False)

    def __repr__(self):
        return f"Course: {self.bloc},'{self.username}'', '{self.course_acronym}'"


    def build_user_cts_dict(username):
        courses = SucceededCourse.query.filter_by(username=username).all()
        cts = {"bac1":0, "bac2":0, "bac3":0, "mineure":0, "hors_programme":0}

        for course in courses:
            cts[course.bloc] += course.cts
        
        return cts
    
    
    
    def delete_succeeded_course(username, bloc):
        toDeleteCourse = SucceededCourse.query.filter_by(username=username, bloc=bloc).all()
        for course in toDeleteCourse:
            db.session.delete(course)

    def add_acronym_db(acronym_list, year_dict, bloc, username, replace=False):
        """
        Add well known sigle to the db
        """
         # First delete the old courses from the student courses
        if replace:
            SucceededCourse.delete_succeeded_course(username, bloc)
        
        # Add the new courses
        for acronym in acronym_list:
            print(acronym)
            for category in year_dict:
                if acronym in year_dict[category]["course"]:
                    course_json = year_dict[category]["course"][acronym]
                    course = SucceededCourse(username=username, course_acronym=acronym, bloc=bloc, cts=course_json["cts"], course_title=course_json["name"])
                    db.session.add(course)
                    break
            
        db.session.commit()
        return True

    def add_not_known_acronym_db(courses_dict, bloc, username, other_minor=False, other_out_program=False, replace=False):
        """
        Adds acronyms not known by the system, these acronyms have been encoded manually by the student
        The courses_dict is the dictionary that is returned from request.form.to_dict()
        """
        if replace:
            SucceededCourse.delete_succeeded_course(username, bloc)
        current = 0

        while True:
            sigle = f"sigle{current}"
            title = f"titre{current}"
            cts = f"cts{current}"

            if not (courses_dict.get(sigle) and courses_dict.get(title) and courses_dict.get(cts)):
                break

            course = SucceededCourse(username=username, course_acronym=courses_dict[sigle], bloc=bloc, cts=courses_dict[cts], course_title=courses_dict[title], other_minor=other_minor, other_out_program=other_out_program)
            db.session.add(course)

            current += 1

        db.session.commit()
    
    def validate_not_known_acronym(courses_dict):
        current = 0

        while True:
            sigle = f"sigle{current}"
            title = f"titre{current}"
            cts = f"cts{current}"

            if not (courses_dict.get(sigle) and courses_dict.get(title) and courses_dict.get(cts)):
                break
            else:
                if len(courses_dict.get(sigle)) != 9:
                    return False
                if len(courses_dict.get(title)) == 0 or len(courses_dict.get(title)) > 150:
                    return False
                if not courses_dict.get(cts).isdigit() or int(courses_dict.get(cts)) > 15 or int(courses_dict.get(cts)) <= 0:
                    return False
            
            current += 1

        return True
        

    
    def acronym_validation(acronym_list, year_dict):
        """
        Validate well known acronym by verifying in the json if they exists
        """
        # Validate the user input
        for acronym in acronym_list:
            found = False
            for category in year_dict:
                if acronym in year_dict[category]["course"]:
                    found = True
                    break
            if not found:
                return False

        return True
            


