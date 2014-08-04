#hacky

import serial
from time import time
from time import asctime
from decimal import *

connection = serial.Serial('/dev/ttyACM0', 9600)

dataFileName = '7-31-8-1-14.csv' # Include .csv extension

tube = 'Tube1: '

# Returns the time since the Epoch in seconds as a string
# Quantized to two decimal places
def getTime():
	twoPlaces = Decimal(10) ** -2 #for quantizing 2 decimal places
	timeDec = Decimal(time()).quantize(twoPlaces) # Time since Epoch in seconds
	timeString = str(timeDec) #converts to a string for recording in the CSV
	return timeString

# Sets up the data file
# Includes header with start time
f = open(dataFileName, 'a')
f.write('START TIME: ' + str(time()) + '\n')
f.close()

def main():
	while True:
		# Read the incoming line
		line = connection.readline()
		try:
			# Chop off the beginning of the line - "OK"
			while line[0] == 'O' or line[0] == 'K' or line[0] == '\r':
				line = line[1:]
			# Chop off the new line character(s)
			line = line[:-2]
			# Isolate the gate and the tag from the line if it's a tag
			if line[0] == '9':
				gate = line[-1]
				tag = line[:-2]
				# Grab the time of the read
				timeRead = getTime()
				# Write this data point
				data = open(dataFileName, 'a')
				data.write('"' + tag + '","' + gate + '","' + str(timeRead) + '","' + str(asctime()) + '"\n')
				print(tube + str(tag) +' ' + str(asctime()) + ' - ' + str(gate))			
				data.close()
			else:
				data = open(dataFileName, 'a')
				data.write('"wheel","-","' + getTime() + '","' + str(asctime()) + '"\n')
				print('wheel ' + str(asctime()))
				data.close()
		except:
			# Give useful debugging message - guaranteed to work 100% of the time.
			print "Something went wrong"
			continue
			
main()
