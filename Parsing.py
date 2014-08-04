import time
from os import system
import sys

months = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06', 
                        'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}

def findAscDate(timeEpoch):
    ascRaw = time.ctime(float(timeEpoch))
    ascDate = ascRaw[-2:] + '/' +  months[ascRaw[4:7]] + '/' + ascRaw[8:10]
    return ascDate 

def findAscTime(timeEpoch):     
    ascRaw = time.ctime(float(timeEpoch))
    ascTime = ascRaw[11:19] + '.00'
    return ascTime

class Mouse:

	def __init__(self, inputTag):
		self.tag = inputTag
		self.inWheel = False
		self.ranThisBlock = 0.0
		self.ranTotal = 0.0
		self.file = self.makeFile()
		self.inOutFile = self.makeInOutFile()

	def makeFile(self):
		filename = self.tag + '.txt'
		mouseFile = open(filename, 'w')
		mouseFile.write('GROUP ' + self.tag + '                                                                                 :\n\n---------\nUNIT TIME=\n')
		return mouseFile

	def makeInOutFile(self):
		filename = self.tag + '_inOut.txt'
		inOutFile = open(filename, 'w')
		inOutFile.write('RECORD OF MOUSE ENTERING AND EXITING WHEEL\n')
		return inOutFile

	def writeInOutLine(self, timeEpoch):
		dateAsc = findAscDate(timeEpoch)
		timeAsc = findAscTime(timeEpoch)
		if self.inWheel:
			self.inOutFile.write('ENTER AT: ' + timeAsc + '    ' + dateAsc + '\n')
		elif not self.inWheel:
			self.inOutFile.write('EXIT AT: ' + timeAsc + '    ' + dateAsc + '\n')

	def countTurn(self):
		if self.inWheel:
			self.ranThisBlock += 1
			self.ranTotal += 1
	def writeLine(self, dateAsc, timeAsc, scale):
		scaledRanThisBlock = self.ranThisBlock / scale
		self.file.write(dateAsc + ' ' + timeAsc + '     ' + str(scaledRanThisBlock) + '\n')

	def finishBlock(self):
		self.ranThisBlock = 0.0

class Data:

	def __init__(self, dataLine):
		self.data = self.sliceData(dataLine)
		self.type = self.checkType()
		self.tag = 'N/A'
		self.gate = 'N/A'
		if self.type == 'tag':
			self.tag = self.data[0]
			self.gate = self.data[1]
		self.timeEpoch = float(self.data[2])
		self.ascStamp = self.data[3]

	def sliceData(self, dataLine):
		split = dataLine.split('"')
		return [split[1], split[3], split[5], split[7]]

	def checkType(self):
		if self.data[0] == 'wheel':
			return 'wheel'
		else:
			return 'tag'

class Parser:

	def __init__(self):
		self.configs = self.getConfigs()
		self.mice = self.makeMice()
		self.csvfile = self.openCSV()
		self.interval = float(self.configs[5])
		self.startTime = float(self.csvfile.readline()[12:25])
		self.endOfBlock = self.startTime + self.interval
		self.scale = float(self.configs[6])
		self.done = False
		self.currentData = None
		self.totalRevolutionsBlock = 0.0
		self.totalRevolutions = 0.0
		self.odometerMode = bool(int(self.configs[7]))
		self.cageFile = self.makeCageFile()

	def getConfigs(self):
		try:
			configsFile = open('config.txt', 'r')
		except IOError:
			filename = raw_input("Enter Config File Name: ")
			if filename[-4:] != '.txt':
				filename = filename + '.txt'
			configsFile = open('config.txt', 'r')
		configs = []
		configsFile.readline()
		for line in configsFile:
			configs.append(line[11:-1])
		return configs

	def makeMice(self):
		mice = []
		for i in range(4):
			mice.append(Mouse(self.configs[i]))
		return mice

	def openCSV(self):
		try:
			csvfile = open(self.configs[4], 'r')
			return csvfile
		except IOError:
			print "ERROR - CSV FILE DOES NOT EXIST IN LOCAL DIRECTORY."

	def makeCageFile(self):
		cageFile = open('cage.txt', 'w')
		cageFile.write('GROUP CAGE                                                                           :\n\n---------\nUNIT TIME=\n')
		return cageFile
	
	def writeData(self):
		print 'writing'
		scaledTotalRevolutionsBlock = self.totalRevolutionsBlock / self.scale
		dateAsc = findAscDate(self.endOfBlock)
		timeAsc = findAscTime(self.endOfBlock)
		for mouse in self.mice:
			mouse.writeLine(dateAsc, timeAsc, self.scale)
			mouse.finishBlock()
		self.cageFile.write(dateAsc + ' ' + timeAsc + '     ' + str(scaledTotalRevolutionsBlock) + '\n')
		self.totalRevolutionsBlock = 0.0

	def updateMiceFlags(self):
		for mouse in self.mice:
			if mouse.tag == self.currentData.tag:
				if self.currentData.gate == '1':
					mouse.inWheel = False
				elif self.currentData.gate == '2':
					mouse.inWheel = True
				mouse.writeInOutLine(self.currentData.timeEpoch)

	def parse(self):
		while not self.done:
			self.parseLine()
		for mouse in self.mice:
			mouse.file.close()
			mouse.inOutFile.close()
		self.cageFile.close()

	def countTurns(self):
		doesAdd = False
		numMice = 0
		for mouse in self.mice:
			if mouse.inWheel:
				doesAdd = True
				numMice += 1
				mouse.countTurn()
		if doesAdd:
			if self.odometerMode:
				self.totalRevolutions += 1
				self.totalRevolutionsBlock += 1
			else:
				totalRevolutions += numMice
				totalRevolutionsBlock += numMice

		# other stuff for sam happens here

	def parseLine(self):
		dataLine = self.csvfile.readline()
		if dataLine == '':
			self.done = True
		else:
			self.currentData = Data(dataLine)
			if self.currentData.type == 'wheel':
				print 'wheel'
				if (self.currentData.timeEpoch < self.endOfBlock):
					self.countTurns()
				else:
					self.writeData()
					self.endOfBlock += self.interval
					while (self.currentData.timeEpoch > self.endOfBlock):
						self.writeData()
						self.endOfBlock += self.interval
					self.countTurns()
			elif self.currentData.type == 'tag':
				print 'tag'
				if (self.currentData.timeEpoch < self.endOfBlock):
					self.updateMiceFlags()
				else:
					self.writeData()
					self.endOfBlock += self.interval
					while (self.currentData.timeEpoch > self.endOfBlock):
						print self.currentData.timeEpoch
						print self.endOfBlock
						self.writeData()
						self.endOfBlock += self.interval
					self.updateMiceFlags()

def main():
	p = Parser()
	p.parse()

main()