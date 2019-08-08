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

# to be saved in the database
network = {
    'organization': '',
    'authors': [],
    'publications': []
}

# contains full information
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

# organize information in fullcopy to be returned
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
            'totalCitation': '',
            'degreeCentrality': 0,
            'closenessCentrality': 0,
            'betweennessCentrality': 0,
            'eigenvectorCentrality': 0
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

# data arrangement for centrality approaches

newArrangement = {
    'subNetworks': [
        {
            'no_id': 0,
            'authors': [],
            'coauthors': [],
            'relations': [
                {
                    'a_id' : '',
                    'ca_id' : '',
                    'distance': 0
                }
            ]
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

# coppied from https://stackoverflow.com/questions/33469897/dfs-to-implement-a-graph-python
def dfs(graph, start, end, path, result):
    path += [start]
    if start == end:
        result.append(path)
    else:
        for node in graph[start]:
            if node not in path:
                dfs(graph, node, end, path[:], result)

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

        ############## Code for filling the return copy ################

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
                'totalCitation': '',
                'degreeCentrality': 0,
                'closenessCentrality': 0,
                'betweennessCentrality': 0,
                'eigenvectorCentrality': 0
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
            #an array to check duplicate coauthors (a previous programming mistake was corrected so this part of code is not needed actually)
            duplicateCoauhthorCheck = []
            for k in j['coAuthors']:
                if k['name'] == '' and k['linkUrl'] == '' or k['linkUrl'] in duplicateCoauhthorCheck:
                    continue

                duplicateCoauhthorCheck.append(k['linkUrl'])

                tempNodes = {
                    'id': '',
                    'name': '',
                    'group': 0,
                    'urlLink': '',
                    'affiliation': '',
                    'researchInterest': [],
                    'totalPaper': '',
                    'totalCoAuthor': '',
                    'totalCitation': '',
                    'degreeCentrality': 0,
                    'closenessCentrality': 0,
                    'betweennessCentrality': 0,
                    'eigenvectorCentrality': 0
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

        ########### Code for filling the return copy ends here ###########

        # make them null to save memory
        network = ''

        ######## starts the code of the filling of newArrangement ########

        # iter = 0
        newArrangement['subNetworks'].pop()
        # for i in returnCopy['links'][112::]:
        for i in returnCopy['links']:

            match = 0
            tempid = 0
            for j in newArrangement['subNetworks'][::-1]:
                # iter += 1
                tempid = j['no_id']
                if i['source'] in j['authors']:
                    match = 1
                    break
                elif i['target'] in j['coauthors']:
                    match = 2
                    break

            tempArrangement = {
                'no_id' : 0,
                'authors' : [],
                'coauthors' : [],
                'relations' : [
                    {
                        'a_id' : '',
                        'ca_id' : '',
                        'distance': 0
                    }
                ]
            }
            # if iter == 15:
            #     break
            temprelation = {
                'a_id': i['source'],
                'ca_id': i['target'],
                'distance': i['value']
            }
            if match == 1:
                #edit network tempid author
                for j in newArrangement['subNetworks'][::-1]:
                    if j['no_id'] == tempid:
                        j['coauthors'].append(i['target'])
                        j['relations'].append(temprelation)
                        break

            elif match == 2:
                #edit network tempid coauthor
                for j in newArrangement['subNetworks'][::-1]:
                    if j['no_id'] == tempid:
                        j['authors'].append(i['source'])
                        j['relations'].append(temprelation)
                        break

            else:
                #save as new network with tempid += 1

                tempArrangement['no_id'] = len(newArrangement['subNetworks'])+1
                tempArrangement['authors'].append(i['source'])
                tempArrangement['coauthors'].append((i['target']))
                tempArrangement['relations'].pop()
                tempArrangement['relations'].append(temprelation)

                newArrangement['subNetworks'].append(tempArrangement)

        # print(newArrangement)

        ######## ends the code of the filling of newArrangement ########

        ######### code for the degree cardanility calculation starts here #########

        fullAuthorId = []
        fullAuthorNumbers = []
        fullCoauthorId = []
        fullCoauthorNumbers = []

        for i in newArrangement['subNetworks']:
            authorId = []
            authorDegree = []
            coAuthorId = []
            coAuthorDegree = []

            for j in i['relations']:
                if j['a_id'] in authorId:
                    authorDegree[authorId.index(j['a_id'])] += 1
                else:
                    authorId.append(j['a_id'])
                    authorDegree.append(0)
                    authorDegree[authorId.index(j['a_id'])] = 1
                if j['ca_id'] in coAuthorId:
                    coAuthorDegree[coAuthorId.index(j['ca_id'])] += 1
                else:
                    coAuthorId.append(j['ca_id'])
                    coAuthorDegree.append(0)
                    coAuthorDegree[coAuthorId.index(j['ca_id'])] = 1

            fullAuthorId = fullAuthorId + authorId
            fullAuthorNumbers = fullAuthorNumbers + authorDegree
            fullCoauthorId = fullCoauthorId + coAuthorId
            fullCoauthorNumbers = fullCoauthorNumbers + coAuthorDegree

        for i in returnCopy['nodes']:
            if i['id'] in fullAuthorId:
                i['degreeCentrality'] = fullAuthorNumbers[fullAuthorId.index(i['id'])]
            elif i['id'] in fullCoauthorId:
                i['degreeCentrality'] = fullCoauthorNumbers[fullCoauthorId.index(i['id'])]

        ########## code for the degree cardanility calculation ends here ##########

        ######### code for the closeness and betweenness cardanility calculation begins here #########

        fullAuthorId = [] # working for closeness centrality
        fullAuthorNumbers = [] # working for closeness centrality
        fullCoauthorId = [] # working for betweeneness centrality
        fullCoauthorNumbers = [] # working for betweeneness centrality

        for i in newArrangement['subNetworks']:

            totalNodes = i['authors'] + i['coauthors']

            # Below 4 lines descript my method but I found stackoverflow method more interesting

            # first, search currentStartNode in the network, it can be either author or coauthor
            # see, how many different nodes are connected to this start node
            # explore each node till the end node is reached, keep an eye on the value(cost)
            # explore means to find the path from each node in connections to currentEndNode

            # Implementatiion from here
            # https://stackoverflow.com/questions/33469897/dfs-to-implement-a-graph-python

            graph = {}
            for j in totalNodes:
                connections = []
                for k in i['relations']:
                    if k['a_id'] == j:
                        connections.append(k['ca_id'])
                    elif k['ca_id'] == j:
                        connections.append(k['a_id'])
                graph.update({j:connections})

            allShortestPaths = [] # all shortest paths between 2 nodes
            noOfShortestPaths = [] # e.g first element is 2 then first 2 lists in allShortestPaths are between same nodes
            # for j in totalNodes:
            for j in totalNodes[:-1:]:
                currentStartNode = j
                sumOfDistanceOfAllNodesFromJ = 0
                closenessCentralityOfJ = 0

                # find shortes path from j to j+1 and others except with itself
                for k in totalNodes[totalNodes.index(j)+1::]:
                    currentEndNode = k

                    #find all paths from j to k
                    result = []

                    dfs(graph, currentStartNode, currentEndNode, [], result)
                    # print(result)

                    distances = []
                    shortestDistance = 0
                    noOfShortestDistances = 0
                    for l in result:
                        for m in l[:len(l)-1:]:
                            nextM = l[l.index(m)+1]
                            # distance between m and nextM
                            for o in i['relations']:
                                if o['a_id'] == m and o['ca_id'] == nextM or o['a_id'] == nextM and o['ca_id'] == m:
                                    shortestDistance += o['distance']
                        distances.append(shortestDistance)
                    shortestDistance = min(distances) # distance between j and k

                    for idx, l in enumerate(distances):
                        if l == shortestDistance:
                            noOfShortestDistances += 1
                            allShortestPaths.append(result[idx])
                    noOfShortestPaths.append(noOfShortestDistances)

                    sumOfDistanceOfAllNodesFromJ += shortestDistance

                # print(sumOfDistanceOfAllNodesFromJ)
                try:
                    closenessCentralityOfJ = (len(totalNodes)-1)/sumOfDistanceOfAllNodesFromJ
                except:
                    # print('End of a Subnetwork {}'.format(i['authors']))
                    pass
                fullAuthorId.append(j)
                fullAuthorNumbers.append(closenessCentralityOfJ)

            # print(allShortestPaths)
            # print(noOfShortestPaths)
            for j in totalNodes:
                betweennessOfJ = 0
                inBetween = 0
                totalPaths = 0
                prevStartNode = ''
                prevEndNode = ''
                for idx, k in enumerate(allShortestPaths):
                    startNode = k[0]
                    endNode = k[-1]
                    # print(k)
                    if startNode == j or endNode == j:
                        continue
                    totalPaths += 1

                    if j in k[1:-1:]: #if j in between the path
                        inBetween += 1

                        # print(inBetween)
                        # print(totalPaths)
                    if startNode != prevStartNode or endNode != prevEndNode:
                        betweennessOfJ = betweennessOfJ + inBetween/totalPaths
                        totalPaths = 0
                        inBetween = 0

                    prevStartNode = startNode
                    prevEndNode = endNode
                fullCoauthorId.append(j)
                fullCoauthorNumbers.append(betweennessOfJ)

        for i in returnCopy['nodes']:
            if i['id'] in fullAuthorId:
                i['closenessCentrality'] = fullAuthorNumbers[fullAuthorId.index(i['id'])]
            if i['id'] in fullCoauthorId:
                i['betweennessCentrality'] = fullCoauthorNumbers[fullCoauthorId.index(i['id'])]

        ########## code for the closeness and betweenness cardanility calculation ends here ##########

        page_sanitized = json.loads(json_util.dumps(returnCopy))
        return JsonResponse(page_sanitized)