import psycopg2
import csv
import os
import glob
import datetime

# potential problem: inserting NULL as a str but should it be a str???

conn = psycopg2.connect(database = "test")
print "Open database successfully"
cur = conn.cursor()

	#tup1  for first table
	#tup2  for second table
	#tup3  for third(i.e. student)

#dicCourse = {} # key is each CID, since term must be different in different files, and different courses in one quarter must have different info
dicStudent = {} # key is each SID
#dicTakeSID = {} #these two are keys for TAKE
#dicTakeCID = {}


# to check if recieved units are integers, from http://stackoverflow.com/questions/15357422/python-determine-if-a-string-should-be-converted-into-int-or-float
def isfloat(x):
    try:
        a = float(x)
    except ValueError:
        return False
    else:
        return True
        
def getGPA(x):
	if ((x == "A+") or (x == "A")):
		return 4
	elif (x == "A-"):
		return 3.7
	elif (x == "B+"):
		return 3.3
	elif (x == "B"):
		return 3
	elif (x == "B-"):
		return 2.7
	elif (x == "C+"):
		return 2.3
	elif (x == "C"):
		return 2
	elif (x == "C-"):
		return 1.7
	elif (x == "D+"):
		return 1.3
	elif (x == "D"):
		return 1
	elif (x == "D-"):
		return 0.7
	else:
		return 0
	


for name in glob.glob('./Grades/*.csv'):		
	with open(name) as f:
		reader = csv.reader(f, delimiter = ',')
		#print "Open file successfully"

		for row in reader:
			if (row[0] == "CID"):  # option 1: hit CID, skip CID
				tup1 = reader.next()
			elif (row[0] == "INSTRUCTOR(S)"):
				tup2 = []
				temptup = reader.next()
				while (len(temptup) == 6):
					tup2 = tup2 + temptup
					temptup = reader.next()
		#print tup2
			elif (row[0] == "SEAT"):
				dicTakeSID = {} #these two are keys for TAKE
				dicTakeCID = {}
				try:
					tup3 = reader.next()
				except StopIteration:
					continue
			#print tup3
				if (len(tup3) != 1): # if student is not empty, Course and Meetings only needed insert once

				#insert into Course
					dicCourse = {}
					if ( not(dicCourse.has_key(tup1[0])) ): #check if already inserted
						dicCourse[tup1[0]] = tup1[3]	
						for i in range(len(tup1)):
							if tup1[i] == "":
								tup1[i] = "NULL"
						sqlcourse = ""
						sqlcourse += "(%d, '%s', '%s', %d, %d, '%s');" %( int(tup1[0]), tup1[1], tup1[2],  int(tup1[3]), int(tup1[4]), tup1[5] )
						cur.execute('''INSERT INTO COURSE (CID, TERM, SUBJ, CRSE, SEC, UNITS) VALUES '''+sqlcourse)
			
			#insert into Meetings
					if (len(tup2) != 0): # has at least one meeting
						ran = len(tup2) / 6
						if tup2[0] == "":  # if doesn't have data, set NULL
							tup2[0] = "NULL"
						for i in range(ran):
							if (tup2[i*6] == ""):  #if the following line doesn't has instructoe, then use the first instructor
								tup2[i*6] = tup2[0]
							for j in range(1,6):
								if tup2[i*6+j] == "":
									tup2[i*6+j] = "NULL"
							if i > 0:
								flag = 0
								for j in range(2,6):
									if tup2[(i-1)*6+j] == tup2[i*6+j]:
										flag += 1
								if flag == 4:
									continue
							tup2[i*6] = tup2[i*6].replace('\'','\"') #instructor name may has '
							
							# need to seperate time and days for comparison---------------------- tup2[i*6+3]
							if tup2[i*6+3] == "NULL":  # if time is null
								starttt = "NULL"
								enddd = "NULL"
								if tup2[i*6+2] == "NULL": # if days is null
									sqlmeetings = "(%d, '%s', '%s', '%s','%s','%s','%s','%s',%s,%s,'%s');" %( int(tup1[0]), tup1[1], tup2[i*6+2], tup2[i*6+3], tup2[i*6+4], tup2[i*6+5], tup2[i*6], tup2[i*6+1], starttt, enddd, tup2[i*6+2] )
									cur.execute('''INSERT INTO MEETINGS (CID, TERM, DAYS, TIME, BUILD, ROOM, INSTRUCTOR, TYPE, STARTTIME, ENDTIME, DAY) VALUES '''+sqlmeetings)
								else: # if days is not null
									for j in range(len(tup2[i*6+2])):	
										#print tup2[i*6+2]							
										sqlmeetings = "(%d, '%s', '%s', '%s','%s','%s','%s','%s',%s,%s,'%s');" %( int(tup1[0]), tup1[1], tup2[i*6+2], tup2[i*6+3], tup2[i*6+4], tup2[i*6+5], tup2[i*6], tup2[i*6+1], starttt, enddd, tup2[i*6+2][j] )
										cur.execute('''INSERT INTO MEETINGS (CID, TERM, DAYS, TIME, BUILD, ROOM, INSTRUCTOR, TYPE, STARTTIME, ENDTIME, DAY) VALUES '''+sqlmeetings)
							else: # if time is not null
								timel = tup2[i*6+3].split('-')
								start = timel[0]
								end = timel[1]
								if (start[-3:] == "PM "):
									hour = int(start.split(':')[0])
									if hour != 12:
										hour += 12 
									starttt = datetime.time( hour, int(start.split(':')[1][:2]), 0  )
								else:
									starttt = datetime.time( int(start.split(':')[0]), int(start.split(':')[1][:2]), 0  )
								if (end[-2:] == "PM"):
									hour = int(end.split(':')[0])
									if hour != 12:
										hour += 12 
									enddd = datetime.time( hour, int(end.split(':')[1][:2]), 0  )
								else:
									enddd = datetime.time( int(end.split(':')[0]), int(end.split(':')[1][:2]), 0  )
							
							# seperating days-----------------tup2[i*6+2]
								if tup2[i*6+2] == "NULL":  # if days is null
									sqlmeetings = "(%d, '%s', '%s', '%s','%s','%s','%s','%s','%s','%s','%s');" %( int(tup1[0]), tup1[1], tup2[i*6+2], tup2[i*6+3], tup2[i*6+4], tup2[i*6+5], tup2[i*6], tup2[i*6+1], starttt, enddd, tup2[i*6+2] )
									cur.execute('''INSERT INTO MEETINGS (CID, TERM, DAYS, TIME, BUILD, ROOM, INSTRUCTOR, TYPE, STARTTIME, ENDTIME, DAY) VALUES '''+sqlmeetings)
								else: # if days is not null
									#print tup2[i*6+2], len(tup2[i*6+2])
									for j in range(len(tup2[i*6+2])):								
										sqlmeetings = "(%d, '%s', '%s', '%s','%s','%s','%s','%s','%s','%s','%s');" %( int(tup1[0]), tup1[1], tup2[i*6+2], tup2[i*6+3], tup2[i*6+4], tup2[i*6+5], tup2[i*6], tup2[i*6+1], starttt, enddd, tup2[i*6+2][j] )
										cur.execute('''INSERT INTO MEETINGS (CID, TERM, DAYS, TIME, BUILD, ROOM, INSTRUCTOR, TYPE, STARTTIME, ENDTIME, DAY) VALUES '''+sqlmeetings)
				while (len(tup3) != 1): # insert all students	
					#if tup1[1] == "199306":
					#	print len(tup3)
					for i in range(len(tup3)):
						if tup3[i] == "":
							tup3[i] = "0"			
			#insert into Student
					if (not(dicStudent.has_key(tup3[1])) ): # check if already inserted
						dicStudent[tup3[1]] = tup3[0]
						tup3[2] = tup3[2].replace('\'','\"') # student name or email may has '
						tup3[10] = tup3[10].replace('\'','\"')
						sqlstudent = ""
						sqlstudent += "(%d, '%s','%s', '%s');" %( int(tup3[1]), tup3[2], tup3[3], tup3[10] )
						cur.execute('''INSERT INTO STUDENT (SID, SURNAME, PREFNAME, EMAIL) VALUES '''+sqlstudent)
						
					
				#insert into Take
					if (not( dicTakeSID.has_key(tup3[1]) and dicTakeCID.has_key(tup1[0]) ) ):	# check	if both this CID and SID are already inserted	
						
						#if tup1[1]=="199306":
						#	print "inside    "
						#	print tup3[1], tup1[0]
						dicTakeSID[tup3[1]] = tup3[0]
						dicTakeCID[tup1[0]] = tup3[0]
						gpa = getGPA(tup3[8])
						sqltake = ""
						if isfloat(tup3[5]):  #units_recieved may be float
							sqltake += "(%d, %d, '%s', %d, '%s', '%s', '%s', '%s', '%s', %f, %f);" %( int(tup3[1]),int(tup1[0]),tup1[1],int(tup3[0]),tup3[4],tup3[6],tup3[8],tup3[9],tup3[7],float(tup3[5]),float(gpa) )
						else:
							sqltake += "(%d, %d, '%s', %d, '%s', '%s', '%s', '%s', '%s', %d, %f);" %( int(tup3[1]),int(tup1[0]),tup1[1],int(tup3[0]),tup3[4],tup3[6],tup3[8],tup3[9],tup3[7],int(tup3[5]), float(gpa) )							

						cur.execute('''INSERT INTO TAKE (SID, CID, TERM, SEAT, LEVEL, CLASS, GRADE, STATUS, MAJOR, UNITS_RECIEVED, GPA) VALUES '''+ sqltake)

					#tup3=reader.next()
					try:
						tup3 = reader.next()
					except StopIteration:
						break
					#conn.commit()


					
conn.commit()

print "Data loaded successfully"


		


