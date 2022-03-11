from django.shortcuts import render
from django.http import HttpResponse

import sys
import urllib
import json
import requests
import datetime


class data:
    def __init__(self, date, units_in_use, units_available):
        self.date = date
        self.units_in_use = units_in_use
        self.units_available = units_available

class centre:
    def __init__(self, name, units):
        self.name = name
        self.units = units

# Create your views here.
def dashBoard_view_temp1(request):
    context = {"connected": False, "has_data": False}
    now = datetime.datetime.now()
    yesterday = now - datetime.timedelta(days=1)
    date = yesterday.strftime("%d/%m/%Y")
    #context["date"] = date

    #Number of confines by types in the quarantine centres (English)
    x = {
     "resource" : "http://www.chp.gov.hk/files/misc/no_of_confines_by_types_in_quarantine_centres_eng.csv",
     "section" : 1,
     "format" : "json"
    }
    url = "https://api.data.gov.hk/v2/filter?q=" + urllib.parse.quote(json.dumps(x))
    try:
        response = requests.get(url)
        context["connected"] = True
        todos = json.loads(response.text)
        if len(todos):
            context["has_data"] = True
        else:
            context["has_data"] = False
        filtered_todos = [todo for todo in todos if todo["As of date"] == date]
        print("Total in quarantine centers:", sum([filtered_todo["Current number of close contacts of confirmed cases"] for filtered_todo in filtered_todos]) + sum([filtered_todo["Current number of non-close contacts"] for filtered_todo in filtered_todos]))
    except:
        context["connected"] = False

    #Occupancy of quarantine centres (English)
    x = {
     "resource" : "http://www.chp.gov.hk/files/misc/occupancy_of_quarantine_centres_eng.csv",
     "section" : 1,
     "filter" : ["As of date", "eq", [date]],
     "format" : "json"
    }
    url = "https://api.data.gov.hk/v2/filter?q=" + urllib.parse.quote(json.dumps(x))
    try:
        response = requests.get(url)
        context["connected"] = True
        todos = json.loads(response.text)
        if len(todos):
            context["has_data"] = True
        else:
            context["has_data"] = False
    except:
        context["connected"] = False
    #print('len todos', len(todos))
    todos = [todo for todo in todos if todo["As of date"] == date]
    #print('len todos after filtering', len(todos))
    sort_todo = sorted(todos, key = lambda x: x["Ready to be used (unit)"], reverse = True)

    context["data"] = data(date = date, units_in_use = sum([todo["Current unit in use"] for todo in todos]), units_available = sum([todo["Ready to be used (unit)"] for todo in todos]))
    context["centre"] = [centre(item["Quarantine centres"], item["Ready to be used (unit)"]) for i, item in enumerate(sort_todo) if i < 3]
    context["test"] = {"item1": 1, "item2": 2}
    #return render(request, "./boardDisplay/templates/dashboard1.html", context)
    return render(request, "./boardDisplay/templates/sample.html", context)

