__author__ = 'manshu'

import requests
import json
import sys
import re
import os
import matplotlib.pyplot as plt
from time import sleep

def makeBulkRequests(payload):
    url = "http://localhost:9200/_bulk"

    payload = ''.join([i if ord(i) < 128 else ' ' for i in payload])
    payload = re.sub(r'[^\x00-\x7F]+', ' ', payload)

    print sys.getsizeof(payload)
    r = requests.post(url, data=payload)
    print r
    print r.text
    print r.json()
    a = r.json()
    if u'items' in a:
        print a[u'items'][0][u'create'][u'status']
    else:
        print a[u'status']

def refreshIndex(netid):
    url = "http://localhost:9200/" + netid + "_index"
    payload = ""
    r = requests.delete(url)
    print r.json()

    r = requests.put(url)
    print r.json()

    payload = """
        {
          "properties": {
            "doc_id": {
              "type": "string",
              "index": "not_analyzed"
            },
            "url": {
              "type": "string",
              "index": "not_analyzed"
            },
            "title": {
              "type": "string",
              "index": "analyzed",
              "analyzer": "english",
              "fields": {
                "title_bm25": {
                  "type": "string",
                  "index": "analyzed",
                  "similarity": "BM25"
                },
                "title_lmd": {
                  "type": "string",
                  "index": "analyzed",
                  "similarity": "LMDirichlet"
                }
              }
            },
            "body": {
              "type": "string",
              "index": "analyzed",
              "analyzer": "english",
              "fields": {
                "body_bm25": {
                  "type": "string",
                  "index": "analyzed",
                  "similarity": "BM25"
                },
                "body_lmd": {
                  "type": "string",
                  "index": "analyzed",
                  "similarity": "LMDirichlet"
                }
              }
            }
          }
        }
    """
    r = requests.put(url + "/_mapping/doc", data=payload)
    print r.json()

def checkStatus(netid):
    url = "http://localhost:9200/" + netid + "_index/_stats"

    r = requests.get(url)
    stat_json = r.json()
    print stat_json
    return stat_json[u'_all'][u'primaries'][u'indexing'][u'index_time_in_millis']

def makeElasticIndexWithSize(netid, mb, json_file, cancel=True):
    #json_file = netid + ".json"
    fp = open(json_file, "r")
    payload = ""
    for line in fp:
        line = line.strip()
        payload += line + "\n"
        current_request_size = sys.getsizeof(payload)
        if current_request_size > mb * 1024 * 1024:
            makeBulkRequests(payload)
            payload = ""
            if cancel:
                break

    if payload != "":
        makeBulkRequests(payload)

    fp.close()

def makeElasticIndexWithDocuments(netid, num_docs, json_file, cancel=True):
    #json_file = netid + ".json"
    fp = open(json_file, "r")
    payload = ""
    payload_docs = 0
    for line in fp:
        line = line.strip()
        payload += line + "\n"
        payload_docs += 1
        if (payload_docs / 2) > num_docs:
            makeBulkRequests(payload)
            payload = ""
            payload_docs = 0
            if cancel:
                break

    if payload != "":
        makeBulkRequests(payload)

    fp.close()

def sendRequest(netid, file_name, payload, question):
    url = "http://localhost:9200/" + netid + "_index/doc/_search?size=50"

    r = requests.get(url, params=payload)
    a = r.json()
    print a
    print a['hits']['hits']

    file = open(file_name, "wb")
    file.write(question + "\n")
    xpayload = payload.replace("\n", "")
    xpayload = xpayload.replace("  ", "")
    file.write(xpayload + "\n")

    for small_json in a['hits']['hits']:
        doc_id = small_json['_source']['doc_id']
        doc_id = doc_id[:doc_id.find(".txt")]
        rank = "1"
        #file.write(netid + "_, " + rank + "\n")
        file.write(doc_id + ", " + rank + "\n")
    file.close()
    a = ""
    r= ""
    sleep(1)

if __name__ == "__main__":
    netid = "sharma55"
    file_name = netid + ".json"

    # questions = ["How do you manage music on your Android phone?", "Installing a nvidia video driver. Anyone know how?",
    #              "How do I recover from Kernel Panic?"]
    # payloads = ["""
    # {"query": { "match": { "body.body_bm25": { "query": "manage music on android", "minimum_should_match": "99%"}}}}
    # """,
    # """
    # {"query": { "match": { "title": { "query": "nvidia driver install", "minimum_should_match": "75%"}}}}
    # """,
    # """
    # {"query": { "match": { "title.title_lmd": { "query": "recover kernel panic","minimum_should_match": "75%"}}}}
    # """,
    # ]
    #
    # for i in range(0, 3):
    #     pass#sendRequest(netid, netid + "_query_" + str(i + 1), payloads[i], questions[i])
    # sendRequest(netid, netid + "_query_" + str(3), payloads[2], questions[2])
    #

    file_size = os.path.getsize(file_name)
    file_size /= 1024 * 1024

    fp = open(file_name, "r")
    line_count = 0
    for line in fp:
        line_count += 1
    fp.close()
    doc_count = line_count / 2

    sizes = [2 ** i for i in range(0, 100) if (2 ** i) < file_size]
    if sizes[-1] != file_size: sizes.append(file_size)

    doc_sizes = [2 ** i for i in range(0, 100) if (2 ** i) < doc_count]
    if doc_sizes[-1] != doc_count: doc_sizes.append(doc_count)

    sizes = []
    doc_sizes = []

    i = file_size
    while i > 0:
        sizes.append(i)
        i /= 2

    i = doc_count
    while i > 0:
        doc_sizes.append(i)
        i /= 2

    sizes.reverse()
    doc_sizes.reverse()

    print sizes
    print doc_sizes

    query_sizes_time = []
    doc_sizes_time = []

    for query_size in sizes:
        refreshIndex(netid)
        try:
            makeElasticIndexWithSize(netid, query_size, file_name, False)
        except:
            break
        sleep(3)
        time_to_make_index = checkStatus(netid)
        query_sizes_time.append(time_to_make_index)

    for doc_size in doc_sizes:
        refreshIndex(netid)
        try:
            makeElasticIndexWithDocuments(netid, doc_size, file_name, False)
        except:
            break
        sleep(3)
        time_to_make_index = checkStatus(netid)
        doc_sizes_time.append(time_to_make_index)


    print query_sizes_time
    print doc_sizes_time

    plt.figure(1)
    plt.plot(sizes[:len(query_sizes_time)], query_sizes_time)
    plt.xlabel('Size of bulk request (in MB)')
    plt.ylabel('Time taken to create index (in ms)')
    plt.title('Graph b/w bulk size & index time creation')
    plt.grid(True)
    plt.show()

    plt.figure(2)
    plt.plot(doc_sizes[:len(doc_sizes_time)], doc_sizes_time)
    plt.xlabel('Number of Documents in a bulk request')
    plt.ylabel('Time taken to create index (in ms)')
    plt.title('Graph b/w documents in bulk request & index time creation')
    plt.grid(True)
    plt.show()

    ## Finally call this to recover whole structure
    refreshIndex(netid)
    makeElasticIndexWithSize(netid, 15, file_name, False)
    time_to_make_index = checkStatus(netid)
    print time_to_make_index