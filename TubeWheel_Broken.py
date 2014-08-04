# Code for handling input of tube and wheel data on same arduino
# Nathaniel Knopf
# July 30th, 2014

import serial
from time import time
from time import asctime
from decimal import *

# Change these things!
serialPort = '/dev/ttyACM0'
baudRate = 9600
dataFileName = 'data.csv'
CageNum = 1

# Returns time since Epoch in seconds as string
# 2 decimals, every time.
def getTime():
	twoPlaces = Decimal(10) ** -2 #for quantizing 2 decimal places
	timeDec = Decimal(time()).quantize(twoPlaces) # Time since Epoch in seconds
	timeString = str(timeDec) #converts to a string for recording in the CSV
	return timeString

class Connection:

	def __init__(self, serialPort, baudRate, dataFileName, cageNum):
		self.dFileName = dataFileName
		self.makeDFile()
		self.connection = self.openConnection(serialPort, baudRate)
		self.cageNum = cageNum

	def makeDFile(self):
		dFile = open(self.dFileName, 'a')
		dFile.write('START TIME: ' + getTime() + '\n')
		dFile.close()

	def openConnection(self, serialPort, baudRate):
		connection = serial.Serial(serialPort, baudRate)
		return connection

	def writeToFile(self, data):
		dFileOpen = open(dFile, 'a')
		dFileOpen.write('"' + data[0] + '","' + data[1] + '","' + getTime() + '","' + str(asctime()) + '"\n') 
		dFileOpen.close()

	def readLine(self):
		line = self.connection.readline()
		try:
			while line[0] == 'O' or line[0] == 'K' or line[0] == '\r':
				line = line[1:]
			line = line[-2] # chops off new line character(s)
			if line[:5] == 'wheel':
				self.writeToFile((('wheel', '-')))
				print str(self.cageNum) + ': wheel ' + str(asctime())
			else:
				tag = line[:-2]
				gate = line[-1]
				self.writeToFile((tag, gate))
				print str(self.cageNum) + ': ' + tag + ' ' + str(asctime()) + ' - ' + str(gate)
		except:
			# Good luck
			print "Something went wrong!"
			continue

def main():
	c = Connection(serialPort, baudRate, dataFileName, cageNum)
	while True:
		c.readline()