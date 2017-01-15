
#try to connect to database

import psycopg2
import csv
import os

conn = psycopg2.connect(database = "test")
print "Open database successfully"

# if need dropping table: 
# DROP TABLE table_name;

cur = conn.cursor()
cur.execute('''CREATE TABLE Student
	(SID INT PRIMARY KEY,
	SURNAME VARCHAR(50),
	PREFNAME VARCHAR(50),
	EMAIL VARCHAR(80));''' )

	#add GPA attribute for calculating 3b
cur.execute('''CREATE TABLE Take
	(SID INT,
	CID INT,
	TERM CHAR(6),
	SEAT INT,
	LEVEL CHAR(2),
	CLASS CHAR(2), 
	GRADE CHAR(5),  
	STATUS CHAR(2),
	MAJOR CHAR(4),
	UNITS_RECIEVED INT,
	GPA NUMERIC(2,1),
	PRIMARY KEY (SID, CID, TERM));''')

cur.execute('''CREATE TABLE Course
	(CID INT,
	TERM CHAR(6),
	SUBJ CHAR(3),
	CRSE INT,
	SEC INT,
	UNITS VARCHAR(50),
	PRIMARY KEY (CID, TERM));''')
	
	# add STARTTIME, ENDTIME, DAY for calculating 3e
cur.execute('''CREATE TABLE Meetings
	(CID INT,
	TERM CHAR(6),
	DAYS CHAR(5),
	TIME VARCHAR(50),
	BUILD VARCHAR(10),
	ROOM VARCHAR(10),
	INSTRUCTOR VARCHAR(80),
	TYPE VARCHAR(30),
	STARTTIME TIME,
	ENDTIME TIME,
	DAY CHAR(5),
	PRIMARY KEY (CID, TERM, DAYS, DAY, TIME, BUILD, ROOM));''')

print "Table created successfully"



conn.commit()
conn.close()
