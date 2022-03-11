from django.shortcuts import render
from django.http import HttpResponse

import sys
import urllib
import json
import requests
import datetime


class data:

# Create your views here.
def dashBoard_view_temp1(request):
    context = {"connected": False, "has_data": False}
    now = datetime.datetime.now()
    yesterday = now - datetime.timedelta(days=1)
    date = yesterday.strftime("%d/%m/%Y")
    context["date"] = date

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
    response = requests.get(url)
    todos = json.loads(response.text)

    context["units_in_use"] = sum([todo["Current unit in use"] for todo in todos])
    context["units_available"] = sum([todo["Ready to be used (unit)"] for todo in todos])
    context = {"data": [...]}

    return render(request, "boardDisplay/templates/dashboard1.html", context)
