"""
GEDCOM parser design

Create empty dictionaries of individuals and families
Ask user for a file name and open the gedcom file
Read a line
Skip lines until a FAM or INDI tag is found
	Call functions to process those two types
Print descendant chart when all lines are processed

Processing an Individual
Get pointer string
Make dictionary entry for pointer with ref to Person object
Find name tag and identify parts (surname, given names, suffix)
Find FAMS and FAMC tags; store FAM references for later linkage
Skip other lines

Processing a family
Get pointer string
Make dictionary entry for pointer with ref to Family object
Find HUSB WIFE and CHIL tags
	Add included pointer to Family object
	[Not implemented ] Check for matching references in referenced Person object
		Note conflicting info if found.
Skip other lines

Print info from the collect of Person objects
Read in a person number
Print pedigree chart
"""


#-----------------------------------------------------------------------

class Event():
	# stores info about a single event
	# created whenver an event (birth, death, marriage) is processed in the 
	# GEDCOM record
	def __init__(self,date,place):
		self._date = date
		self._place = place

	def __str__(self):
		eventDate = ''
		eventPlace = ''
		if self._date != '':
			eventDate = 'DATE: ' + self._date + ' '
		if self._place != '':
			eventPlace += 'PLACE: ' + self._place + ' '
		return eventDate + eventPlace

#-----------------------------------------------------------------------

class Person():
	# Stores info about a single person
	# Created when an Individual (INDI) GEDCOM record is processed.
	#-------------------------------------------------------------------

	def __init__(self,ref):
		# Initializes a new Person object, storing the string (ref) by
		# which it can be referenced.
		self._id = ref
		self._asSpouse = []# use a list to handle multiple families
		self._asChild = None
		self._events = [] #use a list to handle multiple life events
				
	def addName(self, nameString):
		# Extracts name parts from nameString and stores them
		names = line[6:].split('/')#surname is surrounded by slashes
		self._given = names[0].strip()
		self._surname = names[1]
		self._suffix = names[2].strip()

	def addIsSpouse(self, famRef):
		# Adds the string (famRef) indicating family in which this person
		# is a spouse, to list of any other such families
		self._asSpouse += [famRef]
		
	def addIsChild(self, famRef):
		# Stores the string (famRef) indicating family in which this person
		# is a child
		self._asChild = famRef

	def addEvent(self, eventName, event):
		# Stores the tuple containing the name of the event (BIRT, DEAT, MARR), and
		# the event itself, with date and place
		self._events += [(eventName, event)]

	def printDescendants(self, prefix=''):
		# print info for this person and then call method in Family
		print(prefix + self.__str__())
		# recursion stops when self is not a spouse
		for fam in self._asSpouse:
			families[fam].printFamily(self._id,prefix)

	def isDescendant(self,personID):
		#checks to see if an individual (personID) is a descendant of self
		if personID == self._id:
			return true
		famList = []
		for fam in self._asSpouse:
			famList.append(fam)
		for fam in famList:
			fam = families[fam]
			if fam._husband == personID or fam._wife == personID or personID in fam._children:
				return True
			else:
				for secondFamily in persons[fam._husband]._asSpouse:
					if secondFamily not in famList:
						famList.append(secondFamily)
				for secondFamily in persons[fam._wife]._asSpouse:
					if secondFamily not in famList:
						famList.append(secondFamily)
				for kids in fam._children:
					for currentFamily in persons[kids]._asSpouse:
						famList.append(currentFamily)
		return False

	def printAncestors(self, prefix=''):
		# recursively prints an individual's ancestors
		if not self._asChild:
			print(prefix + '--' + self._given + ' ' + self._surname.upper())
		else:
			global families
			fam = families[self._asChild]
			if fam._husband:
				persons[fam._husband].printAncestors('  ' + prefix)
			print(prefix + '--' + ' ' + self._given + ' ' + self._surname.upper())
			if fam._wife:
				persons[fam._wife].printAncestors('  ' + prefix + ' ')

	def printCousins(self, n = 1):
		#prints an individual's nth cousins, working recursively back through their ancestors
		resultList = self.recursCousins(n)
		if not resultList:
			print(self.name() + " has no cousins")
			return None
		print(self.name() + " is " + str(n) + " cousins with: ")
		nameList = []
		for pers in resultList:
				nameList.append(persons[pers].name())
		for cousin in nameList:
			if cousin != self.name():
				print(cousin)

	def recursCousins(self, n):
		#recursive function, seaching back for 'n'th cousins
		if not self._asChild or n < 1:
			return None
		if n == 1:
			return self.getParentsSiblingsKids(families[self._asChild])
		else:
			fam = families[self._asChild]
			cousinList = []
			if fam._husband:
				parCus = persons[fam._husband].recursCousins(n-1)
				if parCus != None and parCus != []:
					cousinList += parCus
			if fam._wife:
				parCus = persons[fam._wife].recursCousins(n-1)
				if parCus != None and parCus != []:	
					cousinList += parCus
			kidList = []
			for cus in cousinList:
				parKids = persons[cus].getKids()
				for doppleganger in parKids:
						if doppleganger not in kidList:
							kidList.append(doppleganger)
			return kidList

	def getParentsSiblingsKids(self, fam):
		#returns a list of an individual's first cousins
		kidList = []
		siblingList = []
		if fam._husband:
			parSibs = persons[fam._husband].getSiblings()
			if parSibs != None and parSibs != []:
				siblingList += parSibs
		if fam._wife:
			parSibs = persons[fam._wife].getSiblings()
			if parSibs != None and parSibs != []:
				siblingList += parSibs
		for sib in siblingList:
			check = persons[sib].getKids()
			if check != []:
				kidList += check
		return kidList

	def getSiblings(self):
		#returns a list of an individuals siblings
		if self._asChild:
			sibs = families[self._asChild]._children
			for pers in sibs:
				if pers == self._id:
					sibs.remove(pers)
			return sibs

	def getKids(self):
		kidList = []
		if self._asSpouse:
			for spouse in self._asSpouse:
				kidList += families[spouse]._children
		return kidList

	def name(self):
		return self._given+ ' ' + self._surname.upper()  + ' ' + self._suffix

	def __str__(self):
		if self._asChild: # make sure value is not None
			childString = ' asChild: ' + self._asChild
		else: childString = ''
		if self._asSpouse != []: # make sure _asSpouse list is not empty
			spouseString = ' asSpouse: ' + str(self._asSpouse)
		else: spouseString = ''
		eventString = ''
		if self._events:
			for evnt in self._events:
				eventString += evnt[0] + ": " + str(evnt[1])
		return self._given + ' ' + self._surname.upper()\
			 + ' ' + self._suffix + eventString #\
#			 + childString + spouseString

 
#-----------------------------------------------------------------------
					
class Family():
	# Stores info about a family
	# Created when an Family (FAM) GEDCOM record is processed.
	#-------------------------------------------------------------------

	def __init__(self, ref):
		# Initializes a new Family object, storing the string (ref) by
		# which it can be referenced.
		self._id = ref
		self._husband = None
		self._wife = None
		self._children = []

	def addHusband(self, personRef):
		# Stores the string (personRef) indicating the husband in this family
		self._husband = personRef

	def addWife(self, personRef):
		# Stores the string (personRef) indicating the wife in this family
		self._wife = personRef

	def addChild(self, personRef):
		# Adds the string (personRef) indicating a new child to the list
		self._children += [personRef]
		
	def printFamily(self, firstSpouse, prefix):
		# Used by printDecendants in Person to print spouse
		# and recursively invole printDescendants on children
		if prefix != '': prefix = prefix[:-2]+''
		if self._husband == firstSpouse:
			if self._wife:# make sure value is not None
				print(prefix+ '+' +str(persons[self._wife]))
		else:
			if self._husband:# make sure value is not None
				print(prefix+ '+' +str(persons[self._husband]))
		for child in self._children:
			 persons[child].printDescendants(prefix + '  |--')
		
	def __str__(self):
		if self._husband: # make sure value is not None
			husbString = ' Husband: ' + self._husband
		else: husbString = ''
		if self._wife: # make sure value is not None
			wifeString = ' Wife: ' + self._wife
		else: wifeString = ''
		if self._children != []: childrenString = ' Children: ' + str(self._children)
		else: childrenString = ''
		return husbString + wifeString + childrenString


#-----------------------------------------------------------------------
 
def getPointer(line):
	# A helper function used in multiple places in the next two functions
	# Depends on the syntax of pointers in certain GEDCOM elements
	# Returns the string of the pointer without surrounding '@'s or trailing
	return line[8:].split('@')[0]
		
def processPerson(newPerson):
	global line
	line = f.readline()
	while line[0] != '0': # process all lines until next 0-level
		eventTag = False
		tag = line[2:6]# substring where tags are found in 0-level elements
		if tag == 'NAME':
			newPerson.addName(line[7:])
		elif tag == 'FAMS':
			newPerson.addIsSpouse(getPointer(line))
		elif tag == 'FAMC':
			newPerson.addIsChild(getPointer(line))
		## add code here to look for other fields
		elif tag == 'BIRT' or tag == 'DEAT':
			eventTag = True
			line = f.readline()
			eventName = tag
			eventDate = ''
			eventPlace = ''
			while line[0] == '2':
				tag = line[2:6]
				if tag == 'DATE':
					eventDate = line[7:].rstrip()
				elif tag == 'PLAC':
					eventPlace = line[7:].rstrip()
				line = f.readline()
			newEvent = Event(eventDate, eventPlace)
			newPerson.addEvent(eventName,newEvent)

		# read to go to next line if an event was not the most recent line found
		if not eventTag:
			line = f.readline()

def processFamily(newFamily):
	global line
	line = f.readline()
	while line[0] != '0':# process all lines until next 0-level
		eventTag = False
		tag = line[2:6]
		if tag == 'HUSB':
			newFamily.addHusband(getPointer(line))
		elif tag == 'WIFE':
			newFamily.addWife(getPointer(line))
		elif tag == 'CHIL':
			newFamily.addChild(getPointer(line))
		elif tag == 'MARR':
			eventTag = True
			line = f.readline()
			eventName = tag
			eventDate = ''
			eventPlace = ''
			while line[0] == '2':
				tag = line[2:6]
				if tag == 'DATE':
					eventDate = line[7:].rstrip()
				elif tag == 'PLAC':
					eventPlace = line[7:].rstrip()
				line = f.readline()
			newEvent = Event(eventDate, eventPlace)
			if newFamily._husband:
				persons[newFamily._husband].addEvent(eventName,newEvent)
			if newFamily._wife:
				persons[newFamily._wife].addEvent(eventName,newEvent)

		# read to go to next line if an event was not the most recent line found
		if not eventTag:
			line = f.readline()


## Main program starts here

persons = {}# to save references to all of the Person objects
families = {} # to save references to all of the Family objects

#filename = "Kennedy.ged"# Set a default name for the file to be processed

### Uncomment the next line to make the program interactive
filename = input("Type the name of the GEDCOM file:")

f = open (filename)
line = f.readline()
while line != '':# end loop when file is empty
	fields = line.strip().split(' ')
	# print(fields)
	if line[0] == '0' and len(fields) > 2:
		# print(fields)
		if (fields[2] == "INDI"): 
			ref = fields[1].strip('@')
			persons[ref] = Person(ref)## store ref to new Person
			processPerson(persons[ref])
		elif (fields[2] == "FAM"):
			ref = fields[1].strip('@')
			families[ref] = Family(ref) ## store ref to new Family
			processFamily(families[ref])	
		else:	# 0-level line, but not of interest -- skip it
			line = f.readline()
	else:	# skip lines until next candidate 0-level line
		line = f.readline()

# Optionally print out all information stored about individuals
#for ref in sorted(persons.keys()):
#	print(ref+':', persons[ref])

# Optionally print out all information stored about families
#for ref in sorted(families.keys()):
#	print(ref+':', families[ref])


person = input("Enter person ID for descendants chart:")

persons[person].printDescendants()

import GEDtest
GEDtest.runtests(persons,families)