#! UNIT TEST SCRIPT CLI TOOLS
import sys
import time
from xml.etree.ElementTree import fromstring
from xmljson import badgerfish as bf
import xmltodict, json
from json import loads, dumps
from collections import OrderedDict

arguments = [
	'email',
	'unzip',
	'import',
	'profile',
	'all'
]
def validate(arg1):
	if sys.argv[1] in arguments:
		print('Testing: ' + sys.argv[1])

def testEmail():
	# A List of Items
	items = list(range(0, 57))
	l = len(items)

	# Initial call to print 0% progress
	printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
	for i, item in enumerate(items):
	    # Do stuff...
	    time.sleep(0.1)
	    # Update Progress Bar
	    printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)


# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def to_dict(input_ordered_dict):
    return loads(dumps(input_ordered_dict))

def importXML(file):
    candidates = []
    header = ['ApplicantId', 'LastName', 'FirstName', 'Email', 'AddToInterviewList', 'MedSchool', 'YearOfGraduation', 'AAMC ID', 'CurrentResidency', 'YearOfResCompletion', 'StepOneDateTaken', 'StepOneThreeDigitScore', 'StepTwoDateTaken', 'StepTwoThreeDigitScore', 'StepThreeDateTaken', 'StepThreeThreeDigitScore', 'NBOME ID', 'ComlexStep1DateTaken', 'Comlex1 Score', 'ComlexStep2DateTaken', 'Comlex2 Score', 'ComlexStep3DateTaken', 'Comlex3 Score', 'AoaStatus', 'GoldHumanismStatus', 'Category', 'First Delivery', 'Last Updated', 'Last Reviewed', 'Address1', 'Address2', 'City', 'State', 'Zip', 'Country', 'PhoneHome', 'PhoneCell']
    count = 0
    string = open(file, 'r').read()
    pp = xmltodict.parse(string)
    if pp['Workbook']['Worksheet'][0]['Table']['Row']:
        for inx, x in enumerate(pp['Workbook']['Worksheet'][0]['Table']['Row']):
            if inx == 0:
                print("SKIP HEADER")
            else:
                rowJson = loads(dumps(x))
                candidate = {}
                index = 0 
                if "Cell" in rowJson:
                    data = rowJson['Cell']
                    for obj in data:
                        if "Data" in obj:
                            if "#text" in obj['Data']:
                                candidate[header[index]] = obj["Data"]["#text"]
                                index += 1
                            else:
                                candidate[header[index]] = "n/a"
                                index += 1

                        else:
                            print("NO DATA")

                    candidates.append(candidate)

                else:
                    print("CELL NOT FOUND")
    else:
        return False
        
    return

xmlToJson("/Users/drewhyatt/Downloads/test.xml")