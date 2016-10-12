##########################################################################
# Author:		    Scott Burgholzer									 #
# Title:		    topTen.py 											 #
# Date:			    10/04/2016											 #
# Descr:		    This will get the top ten warmest and top 10 coldest #
#				    temperatures in the US  					         #
# Last Modified:    10/04/2016 											 #
# Last Modified by: Scott Burgholzer  									 #
##########################################################################
#KN00 station is KFZY

# import statements
import urllib2
import csv
import numpy as np
import re
import datetime
import sys
import collections
from itertools import groupby
import os

# get current date to get rid of extra data later
now = datetime.datetime.now()
currYr = str(now.year)
currMo = now.month
if currMo < 10:
	currMo = "0"+str(now.month)
currDay = now.day
if currDay < 10:
	currDay = "0"+str(now.day)

today = currYr+"/"+str(currMo)+"/"+str(currDay)

# get yesterday's date to get rid of extra data later
yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
yesterYr = str(yesterday.year)
yesterMo = yesterday.month
if yesterMo < 10:
	yesterMo = "0"+str(yesterday.month)
yesterDay = yesterday.day
if yesterDay < 10:
	yesterDay = "0"+str(yesterday.day)

finalYesterday = yesterYr+"/"+str(yesterMo)+"/"+str(yesterDay)


# we need an hour passed into the script... alert the user if they forgot!
# and be nice about it! don't be mean!!
try:
	hour = str(sys.argv[1])
except:
	print "\n\n\n\n\n\nPlease add a hour in the format of HH when executing the script!\n\n\n\n\n\n\n"

# NOTE!!!!!!!!
# 02Z file that I downloaded might has a 058/M08 for OIFS.. earlier they were a 04/something... could it be tha\
# they are doing 05.8/M08???? if 3 digits in front, then skip


# url of where we are getting our data (Using NOAA for now)
url = 'http://tgftp.nws.noaa.gov/data/observations/metar/cycles/%sZ.TXT' % hour
#url = 'http://wxsandbox1.cod.edu/sburgholzer/sao/%sZ.TXT' % hour

# put the data into memory
response = urllib2.urlopen(url)
html = response.read()

# open temporary output file
outputfile = open('us.txt', 'w')
# write our url response to the file
outputfile.write(html)
# close the file
outputfile.close()

# get the data in a list
data = np.genfromtxt('us.txt', delimiter="\n", dtype=None)

# two blank lists to hold temperature and station data
temp = []
stns = []

# set two variables we need to an inital value
noTemp = False
runway = False
tempStr = None

# loop through all the metars and extract station and temperature
for linenum, line in enumerate(data):
	# set the noTemp boolean back to False for the next loop through!
	# doing it at end of loop doesn't work for some reason
	# stupid not logic!
	noTemp = False
	runway = False
	# make the line a string
	str = data[linenum]
	
	# we don't care about the date line, so skip!
	# This is only if we use the NOAA data link
	# if we use our own (maybe eventually) we won't need this if statements
	# I believe!
	if str[0:10] == today or str[0:10] == finalYesterday:
		continue
	
	# now let's parse out!!
	else:
		# check to see if stn is in the line
		# I don't know why it wouldn't be, but hey better save than sorry!!
		startStn  = re.search(r'K[A-Z0-9]{3}', str)
		# Check to see if we have a runway.. if we do it can screw us up!!
		startRun = re.search(r'R?[0-9][0-9]/[0-9][0-9]', str)
		# check to see if we have the two digit temp
		startTmp = re.search(r'M?[0-9]{2}/M?[0-9]{2}', str)
		# check to see if we have the T group
		startTGroup = re.search(r'T[0-9]{8}', str)
		
		if re.search(r'K[A-Z0-9]{3}', str) != None:
			if re.search(r'K[A-Z0-9]{3}', str).start() != 0:
				startStn = None
			
		if startRun == None:
			# we have no runway
			runway = False
		else:
			# we have a runway....
			# darn it.. thanks for making things a tad harder!
			runway = True
		
		# if there is no temp or T group, set noTemp equal to true
		# hopefully we do have at least one of them!!!
		if startTmp == None and startTGroup == None:
			noTemp = True
		
		# now we don't want to put a METAR that has no station ID (I doubt that'll be a rare occurrence)
		# OR if there is no temperature, into our database
		if startStn == None or noTemp == True:
			continue
		# Now that we have confirmed that there is data, let's parse it out
		else:
			# get the start location of the station ID
			startStn = re.search(r'K[A-Z0-9]{3}', str).start()
			# get the end location of the station ID
			endStn = re.search(r'K[A-Z0-9]{3}', str).end()
			# get the start location of the Temp
			if startTmp == None:
				continue
			else:
				startTmp = re.search(r'M?[0-9]{2}/M?[0-9]{2}', str).start()
			# get the end location of the Temp
			endTmp = re.search(r'M?[0-9]{2}/M?[0-9]{2}', str).end()
			
			# append the station ID to the the stns list
			stns.append(str[startStn:endStn])
			
			# If there is no T group, then we want to have the temp
			# into the temp list
			if startTGroup == None:
				tempStr = str[startTmp:endTmp]
				# get the temp string, without the trailing /
				tempStr = tempStr.split('/', 1)[0]
				# get the first char of the string
				firstChar = tempStr[:1]
				# if the first char is a M, then we have a negative temp
				if firstChar == "M":
					# place a - in front of the string and remove
					# the M
					if tempStr[-2:] == "00":
						tempStr = tempStr[-2:]+".0"
						
					else:
						tempStr = "-"+tempStr[-2:]+".0"
					# append to the temp list
					temp.append(tempStr)
				# otherwise, we have a positive temp
				else:
					# append to the temp list
					temp.append(tempStr+".0")
			# we have a T group, so parse that out
			else:
				# get the start location of the T group
				startTGroup = re.search(r'T[0-9]{8}', str).start()
				# get the end location of the T group
				endTGroup = re.search(r'T[0-9]{8}', str).end()
				# get the first char of the T group
				firstChar = str[startTGroup+1:endTGroup-7]
				# if it is 0, then we have a positive number
				if firstChar == "0":
					# the T group gives us decimal degrees, so get rid of the 0
					# then get the first two numbers, add a "." and then get the one decimal number
					newStr = str[startTGroup+2:endTGroup-5] + "." + str[startTGroup+4:endTGroup-4]
					# append this to the temp list
					temp.append(newStr)
				# otherwise, we are a negative number!
				else:
					if str[startTGroup+2:endTGroup-5] == "00":
						newStr = str[startTGroup+2:endTGroup-5] + "." + str[startTGroup+4:endTGroup-4]
					else:
						newStr = "-"+str[startTGroup+2:endTGroup-5] + "." + str[startTGroup+4:endTGroup-4]
					temp.append(newStr)

# Done with looping through the metars!

# now to get rid of duplicate stations!
stnArray = np.array(stns)
tmpArray = np.array(temp)
newArray = zip(stnArray, tmpArray)

newNewArray = []
stationSet = set()

# this does something important
# can't remember due to headache right now... will look again another day
for item in newArray:
	if item[0] not in stationSet:
		stationSet.add(item[0])
		newNewArray.append(item)
	else:
		pass

		
# sort the array by temp!!!
finalArraySorted = sorted(newNewArray, key=lambda item: float(item[1]))

# put all the temps into their own array!!
temperatureArray = []
for item in finalArraySorted:
	temperatureArray.append(item[1])

# count how many we have...	
tempCounter = collections.Counter(temperatureArray)

# put them in an ordered dictionary
od = collections.OrderedDict(sorted(tempCounter.items()))

# get how many coldest stations we have
coldestSum = 0
for key in sorted(od)[:10]:
	coldestSum += od[key]

coldest = finalArraySorted[:coldestSum]

# get how many warmest stations we have
warmestSum = 0
for key in sorted(od)[-10:]:
	warmestSum += od[key]


warmest = finalArraySorted[-warmestSum:]
# reverse array to be correct order for our use!!!
warmest = warmest[::-1]

# now get the sfstns.tbl read into memory

stid = []
name = []
lat = []
lon = []

with open('station-lists/sfstns.tbl', 'rt') as station_file:
	for line in station_file:
		# get the station ID
		stid.append(line[:9].strip())
		# get the station name
		name.append(line[16:49].strip().title())
		# get the station's latitude
		lat.append(int(line[55:61].strip()) / 100.)
		# get the station's longitude
		lon.append(int(line[61:68].strip()) / 100.)


# get the station IDs and temps of the top warmest
warmestStations = []
warmestTemps = []
warmestFahrenheit = []
warmestSorted = sorted(warmest, key=lambda item: item[0])
for item in warmestSorted:
	warmestStations.append(item[0])
	warmestTemps.append(item[1])

# get the temp in Fahrenheit for us Americans!
for item in warmestTemps:
	fahrenheit = float(item) * float(1.8) + float(32)
	warmestFahrenheit.append(fahrenheit)

# arrays for figuring out what stations we need!
warmestName = []
warmestLat = []
warmestLon = []

# we don't want to continuously add the same station over, and over
# and over, and over, and over, and over, and over, and well you get the idea
# in this file. 
noLocFileRead = open("noLocation.txt", "r")
existingNoLoc = []
for item in noLocFileRead:
	temporary = item.rstrip()
	existingNoLoc.append(temporary)
# close the file
noLocFileRead.close()

# now reopen the file, but this time to append to it!
noLocFile = open("noLocation.txt", "a")

# get all the stuff we need for the KML
for item in warmestStations:
	# if the station is in the list of stations we have locations for,
	# add it to the lists for KML
	if item in stid:
		warmestName.append(name[stid.index(item)])
		latitude = lat[stid.index(item)]
		warmestLat.append(latitude)
		longitude = lon[stid.index(item)]
		warmestLon.append(longitude)
	else:
		# darn it, we don't have a location for it!!
		if item in existingNoLoc:
			# if the item is already in the file, don't worry about it!
			continue
		else:
			noLocFile.write("%s\n" % item)
		# put no data into the station spot!
		warmestName.append("No Data")
		warmestLat.append("No Data")
		warmestLon.append("No Data")

# create on list of all data we need for the KML
warmestKMLFile = zip(warmestStations, warmestName, warmestTemps, warmestLon, warmestLat, warmestFahrenheit)

# open the KML for writing!!!
f = open('/home/apache/weather/sburgholzer/usWarmest.kml', 'w')
# now to manually create the KML... you're lucky to not have to worry about this!
f.write("<?xml version='1.0' encoding='UTF-8'?>\n")
f.write("<kml xmlns='http://earth.google.com/kml/2.1'>\n")
f.write("<Document>\n")
f.write("   <name>Top 10 Warmest Stations</name>\n")
f.write('    <Style id="normalPlacemark">')
f.write('      <IconStyle>')
f.write('        <Icon>')
f.write('          <href>http://wxsandbox1.cod.edu/sburgholzer/red-dot.png</href>')
f.write('        </Icon>')
f.write('      </IconStyle>')
f.write('    </Style>')
f.write('    <StyleMap id="exampleStyleMap">')
f.write('      <Pair>')
f.write('        <key>normal</key>')
f.write('        <styleUrl>#normalPlacemark</styleUrl>')
f.write('      </Pair>')
f.write('    </StyleMap>')

for item in warmestKMLFile:
	if item[3] != "No Data" or item[4] != "No Data":
		f.write("   <Placemark>\n")
		f.write("       <name>" + item[0] + "</name>\n")
		f.write("       <styleUrl>#exampleStyleMap</styleUrl>")
		f.write("       <description>" + "%s&lt;br&gt;%s&#8451;/%s&#8457;" %(item[1],item[2],item[5]) + "</description>\n")
		f.write("       <Point>\n")
		f.write("           <coordinates>" + "%s,%s" %(item[3],item[4]) + "</coordinates>\n")
		f.write("       </Point>\n")
		f.write("   </Placemark>\n")
f.write("</Document>\n")
f.write("</kml>\n")
f.close()

# see above for comments! I'm to lazy right now to add them here too..
# maybe someday I'll add them in here... maybe...
# coldest KML stuff
# get the station IDs of the top warmest
coldestStations = []
coldestTemps = []
coldestFahrenheit = []
coldestSorted = sorted(coldest, key=lambda item: item[0])
for item in coldestSorted:
	coldestStations.append(item[0])
	coldestTemps.append(item[1])

for item in coldestTemps:
	fahrenheit = float(item) * float(1.8) + float(32)
	coldestFahrenheit.append(fahrenheit)

# arrays for figuring out what stations we need!
coldestName = []
coldestLat = []
coldestLon = []

noLocFileRead = open("noLocation.txt", "r")
existingNoLoc = []
for item in noLocFileRead:
	temporary = item.rstrip()
	existingNoLoc.append(temporary)

noLocFileRead.close()

noLocFile = open("noLocation.txt", "a")

for item in coldestStations:
	if item in stid:
		coldestName.append(name[stid.index(item)])
		latitude = lat[stid.index(item)]
		coldestLat.append(latitude)
		longitude = lon[stid.index(item)]
		coldestLon.append(longitude)
	else:
		if item in existingNoLoc:
			continue
		else:
			noLocFile.write("%s\n" % item)
			coldestName.append("No Data")
			coldestLat.append("No Data")
			coldestLon.append("No Data")


coldestKMLFile = zip(coldestStations, coldestName, coldestTemps, coldestLon, coldestLat, coldestFahrenheit)

f = open('/home/apache/weather/sburgholzer/usColdest.kml', 'w')
f.write("<?xml version='1.0' encoding='UTF-8'?>\n")
f.write("<kml xmlns='http://earth.google.com/kml/2.1'>\n")
f.write("<Document>\n")
f.write("   <name>Top 10 Coldest Stations</name>\n")
f.write('    <Style id="normalPlacemark">')
f.write('      <IconStyle>')
f.write('        <Icon>')
f.write('          <href>http://wxsandbox1.cod.edu/sburgholzer/blue-dot.png</href>')
f.write('        </Icon>')
f.write('      </IconStyle>')
f.write('    </Style>')
f.write('    <StyleMap id="exampleStyleMap">')
f.write('      <Pair>')
f.write('        <key>normal</key>')
f.write('        <styleUrl>#normalPlacemark</styleUrl>')
f.write('      </Pair>')
f.write('    </StyleMap>')

for item in coldestKMLFile:
	if item[3] != "No Data" or item[4] != "No Data":
		f.write("   <Placemark>\n")
		f.write("       <name>" + item[0] + "</name>\n")
		f.write("       <styleUrl>#exampleStyleMap</styleUrl>")
		f.write("       <description>" + "%s&lt;br&gt;%s&#8451;/%s&#8457;" %(item[1],item[2],item[5]) + "</description>\n")
		f.write("       <Point>\n")
		f.write("           <coordinates>" + "%s,%s" %(item[3],item[4]) + "</coordinates>\n")
		f.write("       </Point>\n")
		f.write("   </Placemark>\n")
f.write("</Document>\n")
f.write("</kml>\n")
f.close()

# now write the warmest and coldest to files for use in php script!
output = open("usWarmest.txt", "w")
for i, item in enumerate(warmest):
	if (i+1) == len(warmest):
		string = "%s," % item[0]
		string = string + "%s" % item[1]
	else:
		string = "%s," % item[0]
		string = string + "%s\n" % item[1]
	output.write(string)
output.close()
output = open("usColdest.txt", "w")
for i, item in enumerate(coldest):
	if (i+1) == len(coldest):
		string = "%s," % item[0]
		string = string + "%s" % item[1]
	else:
		string = "%s," % item[0]
		string = string + "%s\n" % item[1]
	output.write(string)
output.close()

# put the hour in a file for use in PHP script
output = open("usTopTenHour.txt", "w")
string = hour + "Z"
output.write(string)
# close all fileS!!!
output.close()
noLocFile.close()