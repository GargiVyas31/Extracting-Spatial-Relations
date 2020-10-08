import spacy
import neuralcoref
import csv
import json
from spacy import displacy
nlp = spacy.load("en_core_web_sm")
nlp = spacy.load('en')
neuralcoref.add_to_pipe(nlp)
nouns= []
visited = []
landmark = []
prep = []
trajector = []


def dfs(visited, graph, node):

    global landmark, prep, trajector

    if node not in visited:
        if node.dep_ is "prep" :
            prep.append(node.text)

        if node.dep_ is "pobj":
            landmark.append(node.text)

        if node.dep_ is "nsubj" :
            trajector.append(node.text)

        if node.dep_ is "attr":
            trajector.append(node.text)

        if  node.dep_ is "nsubjpass" :
            trajector.append(node.text)

        visited.append(node)

        for neighbour in node.children:
            dfs(visited, graph, neighbour)

def specialcase1(string):
    global landmark, prep, trajector

    for t in nlp(string):
        if t.dep_ is "nsubj" or t.dep_ is "attr" or t.dep_ is "nsubjpass":
            trajector.append(t.text)
        if t.dep_ is "pobj":
            landmark.append(t.text)
   
    prep = landmark[0]
    landmark = landmark[-1]
    with open('Spatial_Relation_test.txt', 'a', newline='') as file:
            S=trajector[0]+" "+prep+" "+landmark+"."
            file.write(S)

    print("Trajector",trajector)
    print("Prep",prep)
    print("Landmark",landmark)


def first_call(string):
    global prep, landmark, trajector
    trajector =[]
    prep= []
    landmark =[]

    if "left" in string or "right" in string or "front" in string or "behind" in string:
        specialcase1(string)
    else:
       
        graph = nlp(string)
        for t in range(len(graph)):
            if graph[t].dep_ ==  "ROOT" :
                root = graph[t]
                print("ROOT",root)
                break
        dfs(visited, graph, root)
        with open('Spatial_Relation_test.txt', 'a', newline='') as file:
            S=trajector[0]+" "+prep[0]+" "+landmark[0]+"."
            file.write(S)
        print("Trajector",trajector)
        print("Prep",prep)
        print("Landmark",landmark)

def start(doc):
    print("Original Sentence",doc)
    if doc._.has_coref:
        print("Reference Resolution ",doc._.coref_resolved)
        doc = doc._.coref_resolved

    sentences = str(doc).split(". ")

    for string in sentences:
        if "and" in string:
            parts = string.split("and")
            print(len(parts))
            print("P",parts)

            for p in range(len(parts)):
                if "is" in parts[p] or "are" in parts[p]:
                    print("Yes",parts[p].replace("are", "is"))
                    first_call(parts[p].replace("are", "is"))
                else:
                    print("No",parts[p])
                    if "is" in parts[p+1] :
                        sentence = parts[p]+" is "+str(parts[p+1].split("is")[1])
                        print("S",sentence)
                        first_call(sentence)
                    elif "are" in parts[p+1]:
                        sentence = parts[p]+" is "+str(parts[p+1].split("are")[1])
                        print("S",sentence)
                        first_call(sentence)
                    else:
                        print("Some other verb detected!")

        else:
            first_call(string)

noun_extracted=list(set(nouns))
with open("new_nouns_ids.txt", 'r') as f:
    d = json.load(f)
noun_id=open("nouns_and_IDs.txt",'w')

ids=[]
sim={}
for i in noun_extracted:
    try:
        ids.append(d[i])
        ni=i+" "+d[i]
    except:
        for j in d:
            cos=nltk.edit_distance(i,j)
            sim[cos]=j

        simi=sorted(sim)
        sid=sim[simi[0]]
        ids.append(d[sid])
        ni=j+" "+d[sid]
    noun_id.write(ni)
    noun_id.write("\n")

start(nlp("A book and a bat are placed to the left of the desk. A hat is on the chair and it is under the desk."))
