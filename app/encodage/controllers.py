from flask import Blueprint, render_template, request, redirect, url_for, flash
import json
from app import db
from flask_login import current_user, login_required

import os 
from .models import SucceededCourse
import app.encodage.admin

mod_encodage = Blueprint('encodage', __name__, url_prefix='/encodage')

# Import the json into memory
program_json = {
    "bac1": json.load(open("program/sinf1ba-an1.json")),
    "bac2": json.load(open("program/sinf1ba-an2.json")),
    "bac3": json.load(open("program/sinf1ba-an3.json")),
    "mineure": json.load(open("program/mineure.json")),
    "hors_programme":json.load(open("program/hors_programme.json"))
}

available_endpoints = ["bac1", "bac2", "bac3", "mineure", "hors_programme"]

   
@mod_encodage.route("/<year>")
@login_required
def bac(year):

    prev_courses_object = SucceededCourse.query.filter_by(username=current_user.username, bloc=year).all()
    prev_courses = list(map(lambda x: x.course_acronym, prev_courses_object))
    user_cts = SucceededCourse.build_user_cts_dict(current_user.username)

    if year == "mineure" and current_user.minor != "appsinf":
        return render_template("encodage/index.html", current_user=current_user, title="Mon parcours", year=year, data=program_json[year], prev_courses=prev_courses_object, user_cts=user_cts, available_endpoints=available_endpoints)
    if year == "hors_programme":
        prev_courses_object_other_hp = SucceededCourse.query.filter_by(username=current_user.username, bloc=year, other_out_program=True).all()
        prev_courses_object_other = SucceededCourse.query.filter_by(username=current_user.username, bloc=year, other_out_program=False).all()
        prev_courses_hp = list(map(lambda x: x.course_acronym, prev_courses_object_other))
        return render_template("encodage/index.html", current_user=current_user, title="Mon parcours", year=year, data=program_json[year], prev_courses=prev_courses_hp, prev_courses_other=prev_courses_object_other_hp, user_cts=user_cts, available_endpoints=available_endpoints)
    return render_template("encodage/index.html", current_user=current_user, title="Mon parcours", year=year, data=program_json[year], prev_courses=prev_courses, user_cts=user_cts, available_endpoints=available_endpoints)


@mod_encodage.route("/<year>", methods=["POST"])
@login_required
def bacPost(year):
    print(request.form)
    year_index = available_endpoints.index(year)

    if SucceededCourse.acronym_validation(request.form, program_json[year]):
        SucceededCourse.add_acronym_db(request.form, program_json[year], year,  current_user.username, replace=True)
        flash(f"Succès de l'ajout de vos cours crédités en {year}", "primary")

        if year_index >= len(available_endpoints)-1:
            return redirect(url_for('encodage.summary'))
        return redirect(url_for('encodage.bac', year=available_endpoints[year_index+1]))
    else:
        flash("Problème lors de l'ajout de vos cours.", "danger")
        return redirect(url_for('encodage.bac', year=available_endpoints[year_index]))

@mod_encodage.route("/mineure", methods=["POST"])
@login_required
def mineurePost():

    #if "minor_title"
    year = "mineure"
    year_index = available_endpoints.index(year)

    form = request.form.to_dict()
    if "minor_title" in form:
        if SucceededCourse.validate_not_known_acronym(form) and len(form["minor_title"]) <= 100 :
            SucceededCourse.add_not_known_acronym_db(form, year, current_user.username, other_minor=True, replace=True)
            current_user.minor = form["minor_title"]
            db.session.commit()
            flash(f"Succès de l'ajout de vos cours crédités en {year}", "primary")

            if year_index >= len(available_endpoints)-1:
                return redirect(url_for('encodage.summary'))
            return redirect(url_for('encodage.bac', year=available_endpoints[year_index+1]))

        
    else:
        if SucceededCourse.acronym_validation(request.form, program_json[year]):
            SucceededCourse.add_acronym_db(request.form, program_json[year], year,  current_user.username, replace=True)
            current_user.minor = "appsinf"
            db.session.commit()
            flash(f"Succès de l'ajout de vos cours crédités en {year}", "primary")

            if year_index >= len(available_endpoints)-1:
                return redirect(url_for('encodage.summary'))
            return redirect(url_for('encodage.bac', year=available_endpoints[year_index+1]))
    
    
    flash("Problème lors de l'ajout de vos cours.", "danger")
    return redirect(url_for('encodage.bac', year=available_endpoints[year_index]))


@mod_encodage.route("/hors_programme", methods=["POST"])
@login_required
def horsProgramPost():

    #{'LEPL2351': 'on', 'LEPL2352': 'on', 'sigle0': 'LINFO1101', 'titre0': 'Test', 'cts0': '4'}
    year = "hors_programme"
    year_index = available_endpoints.index(year)

    form = request.form.to_dict()
    other_course = form.copy()
    known_sigle = []

    for possible_sigle in form:
        if form[possible_sigle] == "on": # Found a sigle
            known_sigle.append(possible_sigle)
            other_course.pop(possible_sigle, None)
    
    validation_known = SucceededCourse.acronym_validation(known_sigle, program_json[year])
    validation_unknown = SucceededCourse.validate_not_known_acronym(other_course)
    if validation_known and validation_unknown:
        SucceededCourse.add_acronym_db(known_sigle, program_json[year], year, current_user.username, replace=True)
        SucceededCourse.add_not_known_acronym_db(other_course, year, current_user.username, other_out_program=True, replace=False)
        flash(f"Succès de l'ajout de vos cours crédités en {year}", "primary")

        if year_index >= len(available_endpoints)-1:
            return redirect(url_for('encodage.summary'))
        return redirect(url_for('encodage.bac', year=available_endpoints[year_index+1]))
    else:
        flash("Problème lors de l'ajout de vos cours.", "danger")
        return redirect(url_for('encodage.bac', year=available_endpoints[year_index]))


@mod_encodage.route("/summary")
@login_required
def summary():
    user_cts = SucceededCourse.build_user_cts_dict(current_user.username)

    return render_template("encodage/summary.html", title="Mon parcours", user_cts=user_cts, available_endpoints=available_endpoints)


