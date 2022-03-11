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

#Occupancy of quarantine centres (English)
def api_ctr(dates):
    connected, has_data = False, False
    #Occupancy of quarantine centres (English)
    x = {
     "resource" : "http://www.chp.gov.hk/files/misc/occupancy_of_quarantine_centres_eng.csv",
     "section" : 1,
     "filter" : [1, "in", dates],
     "format" : "json"
    }
    url = "https://api.data.gov.hk/v2/filter?q=" + urllib.parse.quote(json.dumps(x))
    try:
        response = requests.get(url)
        connected = True
        todos = json.loads(response.text)
        todos = [todo for todo in todos if todo["As of date"] in dates]
        if len(todos) > 0:
            has_data = True
    except:
        connected = False
    return (todos, connected, has_data)


#Number of confines by types in the quarantine centres (English)
def api_num(dates):
    connected, has_data = False, False
    x = {
     "resource" : "http://www.chp.gov.hk/files/misc/no_of_confines_by_types_in_quarantine_centres_eng.csv",
     "section" : 1,
     "filter" : [1, "eq", dates],
     "format" : "json"
    }
    url = "https://api.data.gov.hk/v2/filter?q=" + urllib.parse.quote(json.dumps(x))
    try:
        response = requests.get(url)
        connected = True
        todos = json.loads(response.text)
        todos = [todo for todo in todos if todo["As of date"] in dates]
        if len(todos) > 0:
            print(todos[0])
            has_data = True
    except:
        connected = False
    return (todos, connected, has_data)

# Create your views here.
def dashBoard_view_temp1(request):
    context = {"connected": False, "has_data": False, "data": {}, "count_consistent": False}
    now = datetime.datetime.now()

    for i in range(8):
        dates = [(now - datetime.timedelta(days=i)).strftime("%d/%m/%Y")]
        filtered_todos, num_connected, num_has_data = api_num(dates)
        todos, ctr_connected, ctr_has_data = api_ctr(dates)
        if num_connected and ctr_connected and num_has_data and ctr_has_data:
            context["connected"] = True
            context["has_data"] = True

            context["data"]["non_close_contacts"] = sum([filtered_todo["Current number of non-close contacts"] for filtered_todo in filtered_todos]) + sum([filtered_todo["Current number of non-close contacts"] for filtered_todo in filtered_todos])
        
            todos = [todo for todo in todos if todo["As of date"] in dates]
            sort_todos = sorted(todos, key = lambda x: x["Ready to be used (unit)"], reverse = True)
        
            context["data"]["persons_quarantined"] = sum([sort_todo["Current person in use"] for sort_todo in sort_todos])
            context["data"]["count_consistent"] = context["data"]["persons_quarantined"] == sum([sort_todo["Current person in use"] for sort_todo in sort_todos])
        
            context["data"]["date"] = dates[0]
            context["data"]["units_in_use"] = sum([todo["Current unit in use"] for todo in todos])
            context["data"]["units_available"] = sum([todo["Ready to be used (unit)"] for todo in todos])
            context["centres"] = [{"name": item["Quarantine centres"], "units": item["Ready to be used (unit)"]} for i, item in enumerate(sort_todos) if i < 3]

            break
    else:
        context["connected"] = False
        context["has_data"] = False

    #print(context["centres"])
    return render(request, "./boardDisplay/templates/dashboard3.html", context)

