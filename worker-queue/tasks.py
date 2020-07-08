#!  PYTHON 3.6
#   --------------------------------------------    #
#   • REDIS WORKERS TASKS                      •    #
#   ============================================    # 
#   SMART SYNC FUNCTIONALITY FOR CANDIDATE RANK     #
#   ============================================    # 
#   --------------------------------------------    #

import  os
import  shutil
import  uuid
import  zipfile
import  boto3
import  s3fs
import  pdfkit
from    wand.image import Image as Img
from    wand.image import Image
from    CSVController import CSVController
from    boto3.dynamodb.conditions import Key, Attr
from    botocore.exceptions import ClientError
from    elasticsearch import Elasticsearch
from    datetime   import datetime
from    rq import get_current_job

fs = s3fs.S3FileSystem(anon=False)
DB_URL ='https://dynamodb.us-east-1.amazonaws.com'

dynamodb = boto3.resource('dynamodb',region_name='us-east-1', endpoint_url=DB_URL)
client = boto3.client('dynamodb', region_name='us-east-1',  endpoint_url=DB_URL)
recog = boto3.client('rekognition', region_name='us-east-1')
TASKS_TABLE   = 'tasks'
bucket = 'candidaterank'


ES_CLUSTER                      = '3.235.84.235'
ES_PORT                         = '9200'

def test(job_id, s3key, organization):
    table = dynamodb.Table(TASKS_TABLE)
    response = table.delete_item(Key={'uuid': job_id, 'Organization' : organization })
    print("TASK COMSUMED AND REMOVED FROM DYNAMOBD")

def unzip(job_id, s3key, organization, year):
    files = []
    print("Unzipping: " + s3key)
    location = os.path.splitext(s3key)
    location = location[0] + '/'
    print(location)
    try:
        # CRETAE A UNIQUE DIRECTORY KEY
        dirID = str(uuid.uuid4())
        # CREATE TMP PATH WHERE WORKER IS BEING RUN FROM TO SAVE ON LOCAL MACHINE
        tmpPath = 'storage/' + dirID
        # GET FILE INFO FROM S3
        finfo = fs.info(s3key)
        # UNZIP FILE
        with fs.open(s3key, 'rb') as f:
            zip_file = zipfile.ZipFile(f ,'r')
            uz = zip_file.extractall(tmpPath)
            f.close()
            # SAVE UNZIPPED FILES TO S3
            for r, d, f  in os.walk(tmpPath):
                for file in f:
                    rootp = os.path.join(r, file)
                   
                    filename, file_extension = os.path.splitext(rootp)
                    print(filename, file_extension)
                    s3Path = s3key + '/' + file
                    job_id = str(uuid.uuid4())
                    if '__MACOSX' in rootp:
                        print('__MACOSX found')
                        continue
                    if file_extension == '.csv':
                        # CHANGE PUT IN RANK_TERM ROOT
                        fs.put(rootp, s3key + '/' + file)
                        print('CSV FOUND ADD TO Q')
                        importCSV(job_id, s3Path, organization, year)
                    if file_extension == '.pdf':
                        # CHANGE PUT IN RANK_TERM ROOT
                        fs.put(rootp, s3key + '/' + file)
                        print('PDF FOUND ADD TO Q')
                        getPhoto(job_id, s3Path, organization, year)
                    else: 
                        continue
        # REMOVE UNZIPPED CONTENTS FROM LOCAL MACHINE
        shutil.rmtree(tmpPath)
        table = dynamodb.Table(TASKS_TABLE)
        response = table.delete_item(Key={'uuid': job_id, 'Organization' : organization })
        print("COMPLETE")

    except OSError as e:
        print(e)


def importCSV(job_id, s3key, organization, year):
     # CRETAE A UNIQUE DIRECTORY KEY
    dirID = str(uuid.uuid4())
    # CREATE TMP PATH WHERE WORKER IS BEING RUN FROM TO SAVE ON LOCAL MACHINE
    tmpPath = 'storage/' + dirID
    os.makedirs(tmpPath)
    fs.get(s3key, tmpPath + '/'+dirID+'.csv')
    file =  tmpPath + '/'+dirID+'.csv'
    c = CSVController()
    c.validate(file, organization, year)

def getCandidate(s3key, organization, year):
    response = {
        "success" : False,
        "candidate": {
            "aamcid": ""
        },
    }
    print(s3key, organization, year)
    ids = s3key.split('_')
    print(ids)
    candidate = False
    es = Elasticsearch([{ 'host': ES_CLUSTER, 'port': ES_PORT }])
    for x in ids:
        if x.isdigit() and len(x) == 8:
            response['candidate']['aamcid'] = x
            candidate = es.search(
                index="candidates", 
                body={
                    "query": { 
                        "bool": { 
                            "must": [
                                { "match": { "aamcid":   x }},
                                { "match": { "Organization": organization }},
                                { "match": { "Rank-Term": year }}
                            ]
                        }
                    }
                },
                size=1
            )
            if candidate['hits']['total']['value'] > 0:
                print("CANDIDATE FOUND")
                response['success']     = True
                response['candidate']   = candidate['hits']['hits'][0]['_source']
                print(response)
                return response
            else:
                continue

    return response

def updateCandidate(candidate, photoDest, pdfDest):
    print("UpDATE CANDIDATE")
    print(candidate)
    table = dynamodb.Table('candidates')
    es = Elasticsearch([{ 'host': ES_CLUSTER, 'port': ES_PORT }])
    try:
        now = str(datetime.now())
        candidate["date_modified"]  = now
        candidate["photo"]          = photoDest
        candidate["application"]    = pdfDest
        table.put_item(Item=candidate)
        es.update(index='candidates', id=candidate['uuid'], body={"doc" : candidate })
        return True
    except Exception as e:
        print(e)
        return False

def createCandidate(aamcid, photoDest, pdfDest, organization, year):
        print("CREATE NEW CANDIDATE")
        table = dynamodb.Table('candidates')
        es = Elasticsearch([{ 'host': ES_CLUSTER, 'port': ES_PORT }])
        candidate = {}
        try:
            cid = uuid.uuid4()
            cid = str(cid)
            now = str(datetime.now())
            candidate['uuid']           = cid
            candidate['aamcid']         = aamcid
            candidate["date_created"]   = now
            candidate["date_modified"]  = now
            candidate["photo"]          = photoDest
            candidate["Organization"]   = organization
            candidate["Rank-Term"]      = year
            candidate["interview-year"] = year
            candidate["application"]    = pdfDest

            table.put_item(Item=candidate)
            es.index(index='candidates', doc_type='_doc', id=cid, body=candidate)
            return True
        except Exception as e:
            print(e)
            return False

def getPhoto(job_id, s3key, organization, year):
    # CHECK IF CANDIDATE IN ELASTICSEARCH
    check = getCandidate(s3key, organization, year)
    # print("ES CHECK:" + check)
    # DOWNLOAD FILE LOCAL AND CRETAE A UNIQUE DIRECTORY KEY
    dirID = str(uuid.uuid4())
    # CREATE TMP PATH WHERE WORKER IS BEING RUN FROM TO SAVE ON LOCAL MACHINE
    tmpPath = 'storage/' + dirID
    os.makedirs(tmpPath)
    try:
        # GET FILE INFO FROM S3
        finfo = fs.info(s3key)
        fs.get(s3key, tmpPath + '/photo.pdf')
        fname = tmpPath + '/photo.pdf'
        jname = tmpPath + '/photo.jpg'
        with Img(filename=fname, resolution=72) as img:
                img.compression_quality = 99
                print("IMAGE SAVE")
                img.save(filename=jname)

        filelist = os.listdir(tmpPath + '/')
        for x in filelist[:]:
            if not(x.endswith(".jpg")):
                filelist.remove(x)

        for fl in filelist:
            path = tmpPath + '/' +fl
            with open(path, 'rb') as image:
                response = recog.detect_faces(Image={'Bytes': image.read()})
                if len(response['FaceDetails']) > 0:
                    with Image(filename=path) as i:
                        # CROP JPEG SO ONLY FACE IS SAVED AS PROFILE PICTURE
                        left = round(response['FaceDetails'][0]['BoundingBox']['Left'] * i.width)
                        top  = round(response['FaceDetails'][0]['BoundingBox']['Top'] * i.height)
                        right = round(left + (i.width * response['FaceDetails'][0]['BoundingBox']['Width']))
                        bottom = round(top +  (i.height * response['FaceDetails'][0]['BoundingBox']['Height']))
                        print(left , top, right, bottom)
                        i.crop(left , top, right, bottom)
                        i.save(filename=path)

                    dest =  tmpPath + '/profile-photo.jpg'
                    s3Dest = bucket +'/'+ organization +'/'+ year +'/'+ dirID + '.jpg'
                    shutil.copyfile(path, dest)
                    fs.put(dest, s3Dest)
                    if check['success'] == True:
                        print(check)
                        # def updateCandidate(uuid, photoDest, pdfDest):
                        updateCandidate(check['candidate'], s3Dest, s3key)
                        print("Update Candidate in Dynamo and ES witn new photo path")
                        shutil.rmtree(tmpPath)
                        return
                    else:
                        print(check)
                        aamcid = check['candidate']['aamcid']
                        # createCandidate(aamcid, photoDest, pdfDest, organization, year):
                        print("Create New Candidate with photo path")
                        createCandidate(aamcid, s3Dest, s3key, organization, year)
                        shutil.rmtree(tmpPath)
                        return

    except Exception as e: 
        print(e)
        shutil.rmtree(tmpPath)
        return


#!  PYTHON 3.6
#   --------------------------------------------    #
#   • REDIS WORKERS TASKS                      •    #
#   ============================================    # 
#   SMART SYNC FUNCTIONALITY FOR CANDIDATE RANK     #
#   ============================================    # 
#   --------------------------------------------    #
