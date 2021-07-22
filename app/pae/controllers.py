from flask import Blueprint, render_template
from flask_login import current_user, login_required
import json
from app.encodage.controllers import available_endpoints, program_json
from app.encodage.models import SucceededCourse

mod_pae = Blueprint('pae', __name__, url_prefix='/pae')

def flatten_course_dict(course_dict, sigle_to_remove):
    flat_course_dict = {}
    for category in course_dict:
        for course in course_dict[category]["course"]:
            if not course in sigle_to_remove:
                flat_course_dict[course] = course_dict[category]["course"][course]

    return flat_course_dict

def flat_and_merge_dict(program_json, sigle_to_remove):
    final_dict = {}
    for year in program_json:
        flat_dict = flatten_course_dict(program_json[year], sigle_to_remove)
        final_dict[year] = flat_dict
        
    return final_dict

def no_access(succeeded_course, course_list):
    no_prerequisite = []
    for year in course_list:
        for course in course_list[year]:
            if course_list[year][course].get("prerequisite"):
                prerequisite_pass = True
                for prerequisite in course_list[year][course].get("prerequisite"):
                    if not prerequisite in succeeded_course:
                        no_prerequisite.append(course)
                        break
    return no_prerequisite
                




@mod_pae.route("/")
@login_required
def pae():
    user_cts = SucceededCourse.build_user_cts_dict(current_user.username)
    succeeded_course = SucceededCourse.query.filter_by(username=current_user.username).all()
    succeeded_list = list(map(lambda x: x.course_acronym, succeeded_course))
    data = flat_and_merge_dict(program_json, succeeded_list)
    example_suggestion = {"LINFO1111":1, "LINFO1112": 1, "LESPO1122":2, "LBIR1212":3, "LINFO1113":2}
    no_prerequisite = no_access(succeeded_course, data)
    print(no_prerequisite)
    print(succeeded_list)
    
    return render_template("pae/index.html", title="Mon PAE", data=data, user_cts=user_cts, available_endpoints=available_endpoints)


