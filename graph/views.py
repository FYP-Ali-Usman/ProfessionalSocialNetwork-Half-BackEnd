import pymongo
from bson import json_util, ObjectId
import json
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.parsers import JSONParser

myclient = pymongo.MongoClient("localhost", 27017)
mydb = myclient["Fyp"]
authorCol = mydb["Authors"]
pubCol = mydb["Publications"]
networkCol = mydb["Networks"]

network = {
    'organization': '',
    'authors': [],
    'publications': []
}

FullCopy = {
    'organization': '',
    'authors': [
        {
            '_id': '',
            'Name': '',
            'urlLink': '',
            'affiliation': '',
            'researchInterest': [],
            'totalPaper': '',
            'totalCoAuthor': '',
            'totalCitation': ''
        }
    ],
    'publications': [
        {
            '_id': '',
            'title': '',
            'year': '',
            'overview': '',
            'catogories': [],
            'author': '',
            'coAuthors': [
                {
                    'name': '',
                    'linkUrl': ''
                }
            ],
            'papaerLink': ''
        }
    ]
}

returnCopy = {
    'organization': '',
    'nodes': [
        {
            'id': '',
            'name': '',
            'group': 0,
            'urlLink': '',
            'affiliation': '',
            'researchInterest': [],
            'totalPaper': '',
            'totalCoAuthor': '',
            'totalCitation': ''
        }
    ],
    'links': [
        {
            'source': '',
            'target': '',
            'value': 0,
            'title': '',
            'year': '',
            'overview': '',
            'catogories': [],
            'papaerLink': ''
        }
    ]
}

def generateNetwork(org):
    #extract the data and fill both network and the FullCopy
    #save the network only

    FullCopy['organization'] = org
    network['organization'] = org
    for x in authorCol.find({'affiliation': org}):
        FullCopy['authors'].append(x)
        network['authors'].append(x['_id'])
        for j in pubCol.find({'author': x['_id']}):
            FullCopy['publications'].append(j)
            network['publications'].append(j['_id'])
    networkCol.save(network)

# Create your views here.

def develop(request):
    if request.method == 'POST':
        print(request)
        data = JSONParser().parse(request)
        print(data)
        print(data['organization'])

        #find if a network of that organization is already present or not
        #if yes, return it
        #if not, generate it then return

        finding = networkCol.find({"organization": data['organization']})
        if finding.count() <= 0:
            print("didn't find the network, creating a newone")
            generateNetwork(data['organization'])

        else:
            print('{0} {1}'.format(finding.count(), ' records found.'))

        if FullCopy['organization'] == '':
            print("return copy is empty")

            for x in finding:
                FullCopy['organization'] = x['organization']
                for j in x['authors']:
                    FullCopy['authors'].append(authorCol.find_one({'_id': j}))
                for j in x['publications']:
                    FullCopy['publications'].append(pubCol.find_one({'_id': j}))

        print("calling fillReturnCopy")

        ############### Code for filling the return copy ###################

        returnCopy['organization'] = FullCopy['organization']
        idx = 0
        idx1 = 0
        tempLinks = []
        tempIds = []
        # for idx, j in enumerate(FullCopy['authors']):
        for j in FullCopy['authors'][1:]:
            tempNodes = {
                'id': '',
                'name': '',
                'group': 0,
                'urlLink': '',
                'affiliation': '',
                'researchInterest': [],
                'totalPaper': '',
                'totalCoAuthor': '',
                'totalCitation': ''
            }

            tempNodes['id'] = str(j['_id'])
            tempNodes['name'] = j['Name']
            tempNodes['group'] = 1
            tempNodes['urlLink'] = j['urlLink']
            tempNodes['affiliation'] = j['affiliation']
            tempNodes['researchInterest'] = j['researchInterest']
            tempNodes['totalPaper'] = j['totalPaper']
            tempNodes['totalCoAuthor'] = j['totalCoAuthor']
            tempNodes['totalCitation'] = j['totalCitation']
            # print(tempNodes)
            returnCopy['nodes'].append(tempNodes)
            # print(returnCopy['nodes'][-1])

            idx += 1
            tempLinks.append(j['urlLink'])
            tempIds.append(j['_id'])
        idx += 1
        returnCopy['nodes'].pop(0)
        # print(returnCopy['nodes'])

        for j in FullCopy['publications'][1:]:
            for k in j['coAuthors']:
                tempNodes = {
                    'id': '',
                    'name': '',
                    'group': 0,
                    'urlLink': '',
                    'affiliation': '',
                    'researchInterest': [],
                    'totalPaper': '',
                    'totalCoAuthor': '',
                    'totalCitation': ''
                }
                tempLinksNodes = {
                    'source': '',
                    'target': '',
                    'value': 0,
                    'title': '',
                    'year': '',
                    'overview': '',
                    'catogories': [],
                    'papaerLink': ''
                }

                tempLinksNodes['value'] = 1
                tempLinksNodes['title'] = j['title']
                tempLinksNodes['year'] = j['year']
                tempLinksNodes['overview'] = j['overview']
                tempLinksNodes['catogories'] = j['catogories']
                tempLinksNodes['papaerLink'] = j['papaerLink']
                tempLinksNodes['source'] = str(j['author'])

                if k['linkUrl'] not in tempLinks:
                    tempNodes['id'] = str(idx1) + str(idx1) + str(idx1)
                    tempNodes['name'] = k['name']
                    tempNodes['group'] = 0
                    tempNodes['urlLink'] = k['linkUrl']
                    returnCopy['nodes'].append(tempNodes)

                    tempLinks.append(k['linkUrl'])
                    tempIds.append(tempNodes['id'])
                    tempLinksNodes['target'] = tempNodes['id']

                else:
                    idx2 = tempLinks.index(k['linkUrl'])
                    tempLinksNodes['target'] = tempIds[idx2]

                returnCopy['links'].append(tempLinksNodes)

                idx1 += 1
                idx += 1
        returnCopy['links'].pop(0)

        ############### Code for filling the return copy ends here ###################

        page_sanitized = json.loads(json_util.dumps(returnCopy))
        return JsonResponse(page_sanitized)