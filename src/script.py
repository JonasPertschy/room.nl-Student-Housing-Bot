import requests, pickle
import json
import time
import sys
import os.path

login_credentials = {'username':'xxxx','password':'xxxx'}
googlelocation_api_key = 'xxxx'


proxies = {
# "http": "http://myproxy:9400",
# "https": "http://myproxy:9400",
}
university_coordinates = "Hogeschool+Inholland+Diemen"
maximal_commuting_minutes = 25
maximal_reactions = 36
region = "Amsterdam"

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'})
session.headers.update({'referer': 'https://www.room.nl/'})
if os.path.isfile('./persistence/cookie'):
    with open('./persistence/cookie', 'rb') as f:
        session.cookies.update(pickle.load(f))

def login():
    r = session.get('https://www.room.nl/portal/account/frontend/getloginconfiguration/format/json', proxies=proxies)
    hashvalue = r.json()['loginForm']['elements']['__hash__']['initialData']
    credentials = {'__id__':'Account_Form_LoginFrontend','__hash__':hashvalue, 'username': login_credentials['username'],'password':login_credentials['password']}
    r = session.post('https://www.room.nl/portal/account/frontend/loginbyservice/format/json', data = credentials, proxies=proxies)
    r = session.get('https://www.room.nl/portal/account/frontend/getaccount/format/json', proxies=proxies)
    print (r.json()['account']['username'])
    with open('./persistence/cookie', 'wb') as f:
        pickle.dump(session.cookies, f)
    check_context()

def get_reactions():
    parameter = {'configurationKey':'aantalReacties'}
    r = session.post('https://www.room.nl/portal/object/frontend/getdynamicdata/format/json', data = parameter, proxies=proxies)
    return r.json()

def reactions_by_id(id,reactions):
    for reaction in reactions:
        if id in reaction['id']:
            return reaction['numberOfReactions']

def distance_cache(origin,destination):
    distancedb = open('./persistence/distance.json', 'r+')
    returnvalue = -1
    try:
        jsonelement = json.load(distancedb)
        for entry in jsonelement['db']:
            if origin in entry['origin'] and destination in entry['destination']:
                returnvalue = entry['seconds']
                break
    except:
        jsonelement = {'db':[]}
    if returnvalue == -1:
        r = session.get('https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&mode=bicycling&language=en&origins='+origin+'&destinations='+destination+'&key='+googlelocation_api_key, proxies=proxies)
        distancerequest = r.json()
        print(distancerequest)
        if "OK" in distancerequest['status']:
            returnvalue = distancerequest['rows'][0]['elements'][0]['duration']['value']
            jsonelement_new = {'origin':origin,'destination':destination,'seconds':returnvalue}
            jsonelement['db'].append(jsonelement_new)
        distancedb.seek(0)
        json.dump(jsonelement,distancedb)
        distancedb.truncate()
    distancedb.close()
    return returnvalue

def applied_before(id):
    returnvalue = False
    try:
        applicationdb = open('./persistence/application.json', 'r+')
        jsonelement = json.load(applicationdb)
        for entry in jsonelement['db']:
            if id in entry['id']:
                returnvalue = True
                break
        applicationdb.close()
    except:
        return returnvalue

def applied(id):
    if applied_before(id):
        return False
    else:
        applicationdb = open('./persistence/application.json', 'r+')
        try:
            jsonelement = json.load(applicationdb)
        except:
            jsonelement = {'db':[]}
        jsonelement['db'].append({'id':id})
        applicationdb.seek(0)
        json.dump(jsonelement,applicationdb)
        applicationdb.truncate()
        applicationdb.close()
        return True
    
def count_applications():
    try:
        applicationdb = open('./persistence/application.json', 'r+')
        jsonelement = json.load(applicationdb)
        applicationdb.close()
        return len(jsonelement['db'])
    except:
        return 0

def apply(id,urlKey):
    if applied_before(id):
        print ("Applied before for "+id+" You already have "+str(count_applications())+" applications")
        return False
    elif count_applications() < 6:
        print ("APPLY for:"+id)
        #GetADD
        getobject = {'id':id}
        r = session.post('https://www.room.nl/portal/object/frontend/getobject/format/json', data = getobject, proxies=proxies)
        addvalue = r.json()['result']['assignmentID']
        #GetHash
        r = session.get('https://www.room.nl/portal/core/frontend/getformsubmitonlyconfiguration/format/json', proxies=proxies)
        hashvalue = r.json()['form']['elements']['__hash__']['initialData']
        #Post
        postdata = {'__id__':'Portal_Form_SubmitOnly','__hash__':hashvalue,'add':addvalue,'dwellingID':id}
        r = session.post('https://www.room.nl/portal/object/frontend/react/format/json', data = postdata, proxies=proxies)
        result = r.json()
        if result['success']:
            applied(id)
            print ("Successful applied for %s in position %s. %i applications overall https://www.room.nl/en/offerings/to-rent/details/%s" % (id, result['numberOfReactions'],count_applications(),urlKey))
    else:
        print ("To many open applications")
        exit()

def get_flats(reactions):
    #Print all Flats in Amsterdam
    r = session.get('https://www.room.nl/portal/object/frontend/getallobjects/format/json', proxies=proxies)
    for result in  r.json()['result']:
        if region in result['city']['name']:
            #Filter for first come first serve
            if result['model']['modelCategorie'].get('code') and "inschrijfduur" in result['model']['modelCategorie']['code']:
                gps = "%s,%s"%(result['latitude'],result['longitude'])
                distance_in_minutes = distance_cache(gps,university_coordinates)/60
                if maximal_commuting_minutes > distance_in_minutes:
                    responses = reactions_by_id(result['id'],reactions)
                    if maximal_reactions > int(responses):
                        print (result['urlKey'])
                        print (responses,distance_in_minutes)
                        apply(result['id'],result['urlKey'])
                    else:
                        print ("To many reactions:"+str(responses))
                else:
                    print ("To much distance:"+str(distance_in_minutes))
#Apply, delete other request only if there are more reactions

def wait_seconds(seconds):
    #Source https://stackoverflow.com/questions/7039114/waiting-animation-in-command-prompt-python
    bar = [
        " [=     ]",
        " [ =    ]",
        " [  =   ]",
        " [   =  ]",
        " [    = ]",
        " [     =]",
        " [    = ]",
        " [   =  ]",
        " [  =   ]",
        " [ =    ]",
    ]
    i = 0
    iterations=seconds*5
    while i<iterations:
        time.sleep(.2)
        sys.stdout.write(bar[i % len(bar)]+str((iterations-i)/5)+'\r')
        sys.stdout.flush()
        i += 1
    return True

def check_context():
    r = session.get('https://www.room.nl/portal/account/frontend/getaccount/format/json', proxies=proxies)
    if r.json()['account'] is None:
        print ("Not authenticated")
        login()
    else:
        print ("authenticated as %s" % (r.json()['account']['username']))
        reactions = get_reactions()['result']
        get_flats(reactions)


check_context()
while wait_seconds(30):
    check_context()