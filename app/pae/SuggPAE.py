import json
import os

# dir_path for import compatibility
dir_path = os.path.dirname(os.path.realpath(__file__))
program_json = {
    "bac1": json.load(open(f"{dir_path}/../../program/sinf1ba-an1.json", encoding='utf-8')),
    "bac2": json.load(open(f"{dir_path}/../../program/sinf1ba-an2.json", encoding='utf-8')),
    "bac3": json.load(open(f"{dir_path}/../../program/sinf1ba-an3.json", encoding='utf-8')),
    "mineure": json.load(open(f"{dir_path}/../../program/mineure.json", encoding='utf-8')),
}


b1names = [sigle for category_courses in program_json["bac1"].values() for sigle in category_courses["course"] ]
b2names = [sigle for category_courses in program_json["bac2"].values() for sigle in category_courses["course"] ]
b3names = [sigle for category_courses in program_json["bac3"].values() for sigle in category_courses["course"] ]


def tocredits(list_acronym):
    total_credits = 0
    for bloc in program_json:
        for acronym in list_acronym:
            for category in program_json[bloc]:
                if acronym in program_json[bloc][category]["course"]:
                    total_credits += program_json[bloc][category]["course"][acronym]["cts"]
    return total_credits


def detailed(code):
    for bloc in program_json:
        for category in program_json[bloc]:
            if code in program_json[bloc][category]["course"]:
                course = program_json[bloc][category]["course"][code]
                detail_str = f"{code} - {course['name']} - {course['cts']} crédits - {bloc}."
                return detail_str


def creditsMineure(mineure):

    total=0
    for couple in mineure:
        total+=int(couple[1])
    return total


def Bloc1(passed):
    courses=[]
    program = program_json["bac1"]

    for cat in program:
        for course in program[cat]["course"]:
            if course not in passed:
                if program[cat]["course"][course]["mandatory"]:
                    courses.append(course)
    return courses


def Bloc2(passed, corequis=False):
    courses=[]
    msg=""
    program = program_json["bac2"]
    for cat in program:
        rel=False #cours de religion fait?
        if cat == "Cours de sciences religieuses pour etudiants en sciences exactes":
            for course in program[cat]["course"]:
                if course in passed and not rel:
                    rel=True
            for course in program[cat]["course"]:
                if course not in passed and not rel:
                    if course not in courses:
                        courses.append(course)
            if rel==False:
                msg = msg + "Vous devez choisir un seul cours de religion parmis LTECO2100, LTECO2101, LTECO2102 \n"
        else:
            for course in program[cat]["course"]:
                if course not in passed:
                    ok=True
                    LP=program[cat]["course"][course]["prerequisite"]
                    for pre in LP:
                        if pre not in passed:
                            ok=False
                    if program[cat]["course"][course]["mandatory"]:
                        if ok:
                            courses.append(course)
                        elif corequis:
                            for co in program[cat]["course"][course]["prerequisite"]:
                                if co not in passed:
                                    msg=msg+ co + " "
                                    if co not in courses and co not in b1names:
                                        courses.append(co)
                            if course not in courses:
                                courses.append(course)
                            msg=msg+ " corequis à "+course+ ", vous devez donc les prendre ensemble si vous souhaitez suivre " + course + ". \n"

    return courses, msg


def Bloc3(passed, corequis=False):
    courses = []
    msg = ""
    program = program_json["bac3"]
    for cat in program:
        for course in program[cat]["course"]:
            if course not in passed:
                ok = True
                LP = program[cat]["course"][course]["prerequisite"]
                for pre in LP:
                    if pre not in passed:
                        ok = False
                if program[cat]["course"][course]["mandatory"]:
                    if ok:
                        courses.append(course)
                    elif corequis:
                        for co in program[cat]["course"][course]["prerequisite"]:
                            if co not in passed:
                                msg = msg + co + " "
                                if co not in courses and co not in b1names and co not in b2names:
                                    courses.append(co)
                        if course not in courses:
                            courses.append(course)
                        msg = msg + " corequis à " + course + ", vous devez donc les prendre ensemble si vous souhaitez suivre " + course + ". \n"

    return courses, msg


def genSugg(passed, primo, mineure):
    """
        Take the list of passed courses and a list of the number of credits passed for an1, an2, an3, minor and out-of-progr and return a proposition of PAE
        """
    # structure
    # X= CTS acquis
    #  if X<30 cts: recommence année
    #               -> renvoyer les cours non réussis de bac1 (f°1)
    #  else if X<45 cts: recommencer avec anticipation
    #               -> renvoyer les cours non réussis de bac1 (f°1)
    #               -> lister les cours de bac2 qui peuvent être anticipés (prérequis) (f°2)
    #               -> ajouter la sélection des cours anticipés à conseiller (PLUS MTNT)
    #                -> if primo, renvoyer (pour ne pas dépasser X+15 ou 60 si X > 40 cts)
    #  else if X<60 cts: ADP
    #               -> renvoyer les cours de BAC1 non crédités (f°1)
    #               -> lister les cours de bac2 qui peuvent être pris (corequis) (f°2)
    #               ->if primo, if X>=55, max 65 cts au PAE, else, max 60 cts au PAE
    #  else if X<105 cts:
    #               -> renvoyer les cours de BAC1 non crédités (f°1)
    #               -> lister les cours de bac2 qui peuvent être pris (corequis) (f°2)
    #               -> si pas assez de cours bac2 pour 65 cts -> lister les cours de bac3 qui peuvent être anticipés (prerequis) (f°3)
    #  else if X<119 cts:
    #               -> renvoyer les cours de BAC1 non crédités (f°1)
    #               -> lister les cours de bac2 qui peuvent être pris (corequis) (f°2)
    #               -> si pas assez de cours bac2 pour 65 cts -> lister les cours de bac3 qui peuvent être anticipés (corequis) (f°3)
    #  else if X< 180-30 anticipation master (slide 9): pas d'anticipation
    #  else if X < 180 - 16 anticipation master (slide 9): anticipation master -> compléter le PAE à part sur un excel: compléter son programme avec des cours de Master en
    # respectant les prérequis avec un maximum de 60 crédits au total.  +  Formulaire d’autorisation pour les cours de Master dûment complété à
    # apporter à Mme C. Peeters (disponible sur Moodle - cours EPL1000)
    #  else if X < 180 anticipation master (slide 9): ADP

    credits_acquis = tocredits(passed) + creditsMineure(mineure)
    suggestion=[]
    msg="La liste ci-jointe contient les cours qui vont sont accessibles et que vous pouvez selectionner pour composer votre PAE.\n"
    prog_cts=0 #nombre de crédits max conseillé au PAE
    if credits_acquis<30:
        suggestion= Bloc1(passed)
        prog_cts=60-credits_acquis
        msg = msg + "Votre PAE devrait représenter un total de " + str(prog_cts) + " cts.\n"
    elif credits_acquis<45:
        if primo:
            if credits_acquis>40:
                prog_cts=60
            else:
                prog_cts=credits_acquis+15
        else:
            prog_cts=65
        msg=msg+"Votre PAE devrait représenter un total de " + str(prog_cts)+ " cts.\n"
        suggestion = Bloc1(passed)
        b2 = Bloc2(passed)
        suggestion = suggestion + b2[0]
        msg = msg + b2[1]

    elif credits_acquis<60:
        if primo:
            if credits_acquis>=55:
                prog_cts=65
            else:
                prog_cts=60
        else:
            prog_cts=65
        msg = msg + "Votre PAE devrait représenter un total de " + str(prog_cts) + " cts.\n"
        suggestion=Bloc1(passed)
        b2 = Bloc2(passed, True)
        suggestion = suggestion + b2[0]
        msg = msg + b2[1]

        msg=msg+"N'oubliez pas d'ajouter vos cours de mineure.\n"

    elif credits_acquis<105:
        prog_cts = 65
        msg = msg + "Votre PAE devrait représenter un total de " + str(prog_cts) + " cts.\n"
        suggestion = Bloc1(passed)
        b2 = Bloc2(passed, True)
        suggestion = suggestion + b2[0]
        msg = msg + b2[1]
        if tocredits(suggestion) <tocredits(b2names) and primo==False:
            b3=Bloc3(passed)
            suggestion = suggestion + b3[0]
            msg = msg + b3[1]
            msg=msg+"Prenez en priorité les cours du bloc 2 avant les cours du bloc 3.\n"
        msg = msg + "N'oubliez pas d'ajouter vos cours de mineure.\n"

    elif credits_acquis<119:
        prog_cts = 65
        msg = msg + "Votre PAE devrait représenter un total de " + str(prog_cts) + " cts.\n"
        suggestion = Bloc1(passed)
        b2=Bloc2(passed, True)
        suggestion = suggestion + b2[0]
        msg=msg+ b2[1]
        if tocredits(suggestion) < tocredits(b2names):
            b3=Bloc3(passed, True)
            suggestion = suggestion + b3[0]
            msg = msg + b3[1]
            msg = msg + "N'oubliez pas d'ajouter vos cours de mineure.\n"
            msg = msg+ "Prenez en priorité les cours du bloc 2 avant les cours du bloc 3.\n"
    elif credits_acquis<180-30:
        suggestion = Bloc1(passed)
        b2=Bloc2(passed, True)
        suggestion = suggestion+b2[0]
        msg=msg+b2[1]
        b3 = Bloc3(passed, True)
        suggestion = suggestion + b3[0]
        msg = msg + b3[1]
        msg = msg + "N'oubliez pas d'ajouter vos cours de mineure.\n"
        if len(suggestion) == 0:
            msg = "Vous avez passé tous les cours du tronc commun du bachelier (mineure non comprise).\n"
        prog_cts = 180 - credits_acquis
        msg = msg + "Votre PAE devrait représenter un total de " + str(prog_cts) + " cts.\n"
    elif credits_acquis<180:
        suggestion = Bloc1(passed)
        b2 = Bloc2(passed, True)
        suggestion = suggestion + b2[0]
        msg = msg + b2[1]
        b3 = Bloc3(passed, True)
        suggestion = suggestion + b3[0]
        msg = msg + b3[1]
        msg = msg + "N'oubliez pas d'ajouter vos cours de mineure.\n"
        prog_cts = 180 - credits_acquis
        if len(suggestion) == 0:
            msg = "Vous avez passé tous les cours du tronc commun du bachelier (mineure non comprise).\n"
        msg = msg + "Vous pouvez anticiper des cours de master. Veuillez compléter votre PAE dans un excel en respectant les prérequis et l'envoyer par email à sofie.depauw@uclouvain.be.\n"
        if credits_acquis<180-16:
            msg=msg+ "Veuillez également compléter le formulaire d’autorisation pour les cours de Master (disponible sur Moodle - cours EPL1000) et l'apporter à Mme C. Peeters. \n"
    elif credits_acquis>=180:
        msg="Vous avez acquis suffisamment de crédits pour valider votre bachelier.\n"


    msg=msg+ "Si vous souhaitez ajouter d'autres cours ou ajouter des crédits au PAE, veuillez contacter Mme. Sofie de Pauw par email via sofie.depauw@uclouvain.be.\n"
    return suggestion, prog_cts, msg



"""
# example
#cts <30
passed = ["LANGL1181", "LESPO1113", "LINFO1140", "LINFO1001", "LINFO1112"]
print(tocredits(passed), "crédits passés")
available = genSugg(passed, False)
print(available, tocredits(available[0]))
#cts <45
passed = ["LANGL1181", "LESPO1113", "LINFO1140", "LINFO1001", "LINFO1112", "LINFO1111"]
print(tocredits(passed), "crédits passés")
available = genSugg(passed, True)
print(available, tocredits(available[0]))
#cts <60
passed = ["LANGL1181", "LESPO1113", "LINFO1140", "LINFO1001", "LINFO1112", "LINFO1111", "LINFO1103", "LINFO1101", "LINFO1002"]
print(tocredits(passed), "crédits passés")
available = genSugg(passed, True)
print(available, tocredits(available[0]))
print(available[2])

#cts <105
passed = ["LANGL1181", "LESPO1113", "LINFO1140", "LINFO1001", "LINFO1112", "LINFO1111", "LINFO1103", "LINFO1101", "LINFO1002", "LCOPS1115", "LEPL1402", "LINFO1114"]
print(tocredits(passed), "crédits passés")
available = genSugg(passed, True)
print(available, tocredits(available[0]))
print(available[2])

#cts <119
passed = ["LANGL1181", "LESPO1113", "LINFO1140", "LINFO1001", "LINFO1112", "LINFO1111",
          "LINFO1103", "LINFO1101", "LINFO1002", "LCOPS1115", "LEPL1402", "LINFO1114",
          "LESPO1122", "LCOPS1124", "LBIR1212", "LINFO1113", "LINFO1104", "LINFO1123",
          "LEPL1503", "LANGL1282", "LTECO2100", "LEPL1109"]
print(tocredits(passed), "crédits passés")
available = genSugg(passed, True)
print(available, tocredits(available[0]))
print(available[2])
#cts <150
passed = ["LINFO1111", "LINFO1112", "LINFO1140", "LCOPS1124", "LESPO1113", "LCOPS1115", "LESPO1122", "LINFO1001", "LINFO1002",
          "LINFO1101","LINFO1103", "LANGL1181", "LBIR1212", "LINFO1113", "LINFO1114", "LEPL1402", "LINFO1104", "LINFO1123", "LEPL1503", "LECGE1222",
          "LANGL1282", "LTHEO2840"]
mineure=[("mineure", 30)]
print(tocredits(passed), "crédits passés")
print(creditsMineure(mineure), "crédits mineure")
available = genSugg(passed, False, mineure)
print(available, tocredits(available[0]))
print(available[2])
"""



