#!/bin/python3


import boto3
import os
import io
import json
import csv

input_bucket = "cse546proj2-input"
output_bucket = "cse546proj2-output"

s3 = boto3.client('s3')
dynamodb=boto3.resource('dynamodb')

def get_student_data():
    data = None;
    with open("student_data.json") as fp:
        data = json.load(fp)
    newdata = {}
    for i in data:
        newdata[i["name"]]=i
    return newdata

def get_mapping():
    lines=[]
    with open("mapping", newline="\n") as mappings:
        lines = mappings.readlines()
    mmap = {}
    for line in lines:
        test = line.split(":")[0].split('.')[0]
        output = line.split(":")[1].rstrip().split(',')
        mmap[test] = {'major': output[0], 'year': output[1]}
    return mmap

def get_s3_key_output(key):
    data = io.BytesIO()
    s3.download_fileobj(output_bucket,key, data)
    data.seek(0)
    output = data.readlines()[0].decode('utf-8').split(',')
    return output

def s3_output():
    response = s3.list_objects_v2(Bucket=output_bucket)
    keys = []
    for content in response['Contents']:
        keys.append(content['Key'])
    res = {}
    for key in keys:
        op = get_s3_key_output(key)
        res[key] = {'name': op[0], 'major': op[1], 'year': op[2]}
    return (res, keys);


if __name__ == "__main__":
    res, keys = s3_output()
    st_dat = get_student_data()
    mapping = get_mapping()
    count=0
    for key in keys:
        ok=False
        print("{}:".format(key))
        print("===> s3 op: {},{},{}".format(res[key]['name'], res[key]['major'], res[key]['year']))
        print("===> mapping: {},{}".format(mapping[key]['major'], mapping[key]['year']))
        print("===> student json {},{}".format( st_dat[res[key]['name']]['major'],
                                                st_dat[res[key]['name']]['year']
                                                ))
        ok = (res[key]['major'] == mapping[key]['major'] and res[key]['major'] == st_dat[res[key]['name']]['major'])
        print("===> ok: ", ok)
        if ok:
            count += 1
    print("======> count ok: ", count)
    
