import psycopg2
import csv
import os

conn = psycopg2.connect(database = "test")
print "Open database successfully"
cur = conn.cursor()

# 3a ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print "\n3a\n"

cur.execute('''select count(distinct SID) as StudentPerQuarter, term FROM take GROUP BY term ORDER BY term;''')
StudentNum = 0	# the number of total (number of students attending course in each term) 
Terms = {} # key is name of each term
UnitsNum = [0] * 21	

rows = cur.fetchall()
for row in rows:
	StudentNum += row[0]
	Terms[row[1]] = row[0]

for i in range(21):
	UnitsNum[i] = 0


for term in Terms.keys():
	sql3a = "SELECT COUNT(SID), SUMUNITS FROM ( SELECT SUM(UNITS_RECIEVED) AS SUMUNITS, SID FROM (SELECT SID, UNITS_RECIEVED FROM TAKE WHERE TERM = '"+str(term)+"') AS T GROUP BY SID ) AS A GROUP BY SUMUNITS ORDER BY SUMUNITS;"
	cur.execute(sql3a)
	rows = cur.fetchall()
	for row in rows:
		#print row[1]
		index = int(row[1])
		if (index < 21):
			UnitsNum[index] += row[0]
		
for i in range(1, 21):
	percentage = float(UnitsNum[i])/float(StudentNum) * 100
	print "The percent of students that attemp %d unit(s) is %f"%(i, percentage)+'%.'

#sql3a is:
#  SELECT COUNT(SID), SUMUNITS
#  FROM ( SELECT SUM(UNITS) AS SUMUNITS, SID
#		  FROM (SELECT SID, UNITS_RECIEVED FROM TAKE WHERE TERM = ...) AS T
#		  GROUP BY SID ) AS A
#  GROUP BY SUMUNITS


# 3b ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print "\n3b\n"
people = [0] * 21
sumgpa = [0] * 21
for term in Terms.keys():
	sql3b = "SELECT SUMUNITS, COUNT(SID), SUM(SUMGPA) FROM ( SELECT SUM(UNITS) AS SUMUNITS, SID, SUM(UNITS*GPA) AS SUMGPA FROM ( SELECT UNITS_RECIEVED AS UNITS, SID, GPA FROM TAKE WHERE TERM ='"+str(term)+"' AND GRADE SIMILAR TO '(A|B|C|D|E|F)%' ) AS A GROUP BY SID ) AS B GROUP BY SUMUNITS ORDER BY SUMUNITS;"
	cur.execute(sql3b)
	rows = cur.fetchall()
	for row in rows:
		index = int(row[0])
		if (index < 21):
			#print row[1]
			people[index] += row[1]
			sumgpa[index] += row[2]


for i in range(1, 21): 
	gpaaa = float(sumgpa[i])/float(people[i]*i)
	print "The average GPA for the students take %d unit(s) from part a is %f." %(i, gpaaa)

#sql3b is:		
# SELECT SUMUNITS, COUNT(SID), SUM(SUMGPA)
# FROM ( SELECT SUM(UNITS) AS SUMUNITS, SID, SUM(UNITS*GPA) AS SUMGPA
# 		 FROM ( SELECT UNITS_RECIEVED AS UNITS, SID, GPA
#				FROM TAKE
#				WHERE TERM = ... AND GRADE SIMILAR TO '(A|B|C|D|E|F)%' ) AS A
#		 GROUP BY SID ) AS B
# GROUP BY SUMUNITS

# 3c ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print "\n3c\n"
 
instructor = {}

# SELECT INSTRUCTOR, SUM(GPA*UNITS), SUM(UNITS)
# FROM ( SELECT INSTRUCTOR, GPA, UNITS_RECIEVED AS UNITS
#        FROM (TAKE NATURAL JOIN MEETINGS)
#	     WHERE GRADE SIMILAR TO '(A|B|C|D|E|F)%' ) AS A
# GROUP BY INSTRUCTOR

cur.execute("SELECT INSTRUCTOR, SUM(GPA*UNITS), SUM(UNITS) FROM ( SELECT INSTRUCTOR, GPA, UNITS_RECIEVED AS UNITS FROM (TAKE NATURAL JOIN MEETINGS) WHERE GRADE SIMILAR TO '(A|B|C|D|E|F)%' ) AS A GROUP BY INSTRUCTOR;")
rows = cur.fetchall()

for row in rows:
	instructor[row[0]] = float(row[1])/float(row[2])


v = list(instructor.values())
hgpa = max(v)
lgpa = min(v)

hardest = []
easist = []
for ind in instructor.keys():
	if instructor[ind] == hgpa:
		easist.append(ind)
	elif instructor[ind] == lgpa:
		hardest.append(ind)
# inspired by http://stackoverflow.com/questions/268272/getting-key-with-maximum-value-in-dictionary


print "The hardest instructor(s) based upon the grades are/is"
for i in range(len(hardest)):
	hardest[i] = hardest[i].replace('\"', '\'')
	print hardest[i]
print "The average grade they/he/she assigned is %f.\n" %lgpa

print "The easiest instructor(s) based upon the grades are/is"
for i in range(len(easist)):
	easist[i] = easist[i].replace('\"', '\'')
	print easist[i]
print "The average grade they/he/she assigned is %f." %hgpa


# 3d ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print "\n3d\n"

print "Since we can't calculate a average GPA for P/NP courses, we calculate the pass rates of those courses.\n"

# ********for letter grading courses:

# get every letter grading course:
# SELECT DISTINCT CRSE 
# FROM COURSE, ( SELECT CID, TERM
#  						     FROM TAKE
#   				         WHERE GRADE SIMILAR TO '(A|B|C|D|E|F)%' ) AS A 
# WHERE COURSE.CID = A.CID AND COURSE.TERM = A.TERM AND SUBJ = 'ABC' AND CRSE >= 100 AND CRSE < 200


# SELECT CRSE, T1.INSTRUCTOR, SUM(GPA*UNITS_RECIEVED) AS A1, SUM(UNITS_RECIEVED) A2
# FROM  (SELECT T.CID AS CID, T.TERM AS TERM, INSTRUCTOR, CRSE
#         FROM ( SELECT CID, TERM, CRSE
#                FROM COURSE 
#			   	 WHERE SUBJ = 'ABC' AND CRSE = ... ) AS T, MEETINGS
# 		  WHERE MEETINGS.CID = T.CID AND MEETINGS.TERM = T.TERM ) AS T1, TAKE
# WHERE TAKE.CID = T1.CID AND TAKE.TERM = T1.TERM 
# GROUP BY CRSE, INSTRUCTOR

print "For letter grading courses: \n"
lettercourse = {}
cur.execute("SELECT DISTINCT CRSE FROM COURSE, ( SELECT CID, TERM FROM TAKE WHERE GRADE SIMILAR TO '(A|B|C|D|E|F)%' ) AS A WHERE COURSE.CID = A.CID AND COURSE.TERM = A.TERM AND SUBJ = 'ABC' AND CRSE >= 100 AND CRSE < 200 ORDER BY CRSE;")
rows = cur.fetchall()
for row in rows:
	lettercourse[row[0]] = row[0]

for courses in lettercourse.keys():
	instructor2 = {}
	sql3d1 = "SELECT CRSE, T1.INSTRUCTOR, SUM(GPA*UNITS_RECIEVED), SUM(UNITS_RECIEVED) FROM  (SELECT T.CID AS CID, T.TERM AS TERM, INSTRUCTOR, CRSE FROM ( SELECT CID, TERM, CRSE FROM COURSE WHERE SUBJ = 'ABC' AND CRSE = "+ str(courses)+" ) AS T, MEETINGS WHERE MEETINGS.CID = T.CID AND MEETINGS.TERM = T.TERM ) AS T1, TAKE WHERE TAKE.CID = T1.CID AND TAKE.TERM = T1.TERM GROUP BY CRSE, INSTRUCTOR;"
	cur.execute(sql3d1)
	rows = cur.fetchall()
	for row in rows:
		if row[3] != 0:
			instructor2[row[1]] = float(row[2])/float(row[3])
			#print row[1], round(float(row[2])/float(row[3]), 6)
	v = list(instructor2.values())
	hhgpa = max(v)
	llgpa = min(v)
	hardest = []
	easist = []
	for ind in instructor2.keys():
		if instructor2[ind] == hhgpa:
			easist.append(ind)
		if instructor2[ind] == llgpa:
			hardest.append(ind)
	print "For course ABC "+str(courses)+", 1. the most difficult instructor(s) is/are"
	for i in range(len(hardest)):
		hardest[i] = hardest[i].replace('\"', '\'')
		print hardest[i]
	print "The average grade he/she/they assigned is %f." %llgpa
	print "2. the easist instructor(s) is/are"
	for i in range(len(easist)):
		easist[i] = easist[i].replace('\"', '\'')
		print easist[i]
	print "The average grade they/he/she assigned is %f.\n" %hhgpa
	
passcourse = {}
cur.execute("SELECT DISTINCT CRSE FROM COURSE, ( SELECT CID, TERM FROM TAKE WHERE GRADE SIMILAR TO '(P%|NP%)' ) AS A WHERE COURSE.CID = A.CID AND COURSE.TERM = A.TERM AND SUBJ = 'ABC' AND CRSE >= 100 AND CRSE < 200 ORDER BY CRSE;")	
rows = cur.fetchall()
for row in rows:
	passcourse[row[0]] = row[0]


print "For P/NP courses: \n"	
# ********for P/NP courses: compare the pass rate

# SELECT instructor, crse, SUM(CASE WHEN grade = 'P' THEN 1.0 ELSE 0.0 END)/COUNT(grade) AS pct
# FROM ( SELECT T.CID AS CID, T.TERM AS TERM, CRSE, GRADE 
#        FROM COURSE, TAKE AS T
#        WHERE COURSE.CID = T.CID AND COURSE.TERM = T.TERM AND SUBJ = 'ABC' AND CRSE =... ) AS T1, MEETINGS
# WHERE T1.CID = MEETINGS.CID AND T1.TERM = MEETINGS.TERM
# GROUP BY CRSE, INSTRUCTOR
# ORDER BY CRSE

# assumption: don't count instructors that are null/unknown
for courses in passcourse.keys():
	instructor3 ={}
	sql3d2 = "SELECT instructor, crse, SUM(CASE WHEN grade = 'P' THEN 1.0 ELSE 0.0 END)/COUNT(grade) AS pct FROM ( SELECT T.CID AS CID, T.TERM AS TERM, CRSE, GRADE FROM COURSE, TAKE AS T WHERE COURSE.CID = T.CID AND COURSE.TERM = T.TERM AND SUBJ = 'ABC' AND CRSE ="+str(courses) +") AS T1, MEETINGS WHERE T1.CID = MEETINGS.CID AND T1.TERM = MEETINGS.TERM GROUP BY CRSE, INSTRUCTOR ORDER BY CRSE;"
	cur.execute(sql3d2)
	rows = cur.fetchall()
	for row in rows:
		if row[0] != "NULL":
			instructor3[row[0]] = row[2]
	v = list(instructor3.values())
	hhp = max(v)
	llp = min(v)
	hardest = []
	easist = []
	for ind in instructor3.keys():
		if instructor3[ind] == hhp:
			easist.append(ind)
		if instructor3[ind] == llp:
			hardest.append(ind)
	print "For course ABC "+str(courses)+", 1. the most difficult instructor(s) is/are"
	for i in range(len(hardest)):
		hardest[i] = hardest[i].replace('\"', '\'')
		print hardest[i]
	print "The average pass rate he/she/they gave is %f." %llp
	print "2. the easist instructor(s) is/are"
	for i in range(len(easist)):
		easist[i] = easist[i].replace('\"', '\'')
		print easist[i]
	print "The average pass rate they/he/she gave is %f." %hhp
			


# 3e ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print "\n3e\n"
#create a temp table
#use update to connect two conditions / remove duplicate / order
cur.execute( "create table temp3e (TERM CHAR(10), SUBJ1 CHAR(5), CRSE1 INT, SEC1 INT, SUBJ2 CHAR(5), CRSE2 INT, SEC2 INT);")


## 1. Student in same summer quarter has different records/info --> conflicts (must from two sessions)

sql3e1 = "select c.term as term, t1subj, t1crse, t1sec, subj as t2subj, crse as t2crse, sec as t2sec from( select t2cid, t1cid, subj as t1subj, crse as t1crse, a.term as term, sec as t1sec from( select T1.cid as t1cid, t2.cid as t2cid, t1.term as term from take as t1, take as t2 where t1.term LIKE '____06' and t1.term = t2.term and t1.cid < t2.cid and t1.sid = t2.sid and (t1.level <> t2.level or t1.class <> t2.class or t1.major <> t2.major)) as a, (select cid, term, subj, crse,sec from course where term LIKE '____06') as b where a.term = b.term and t1cid = cid) as c, (select cid, term, subj, crse, sec from course where term like '____06') as d where c.term = d.term and t2cid = cid"

# select c.term as term, t1subj, t1crse, subj as t2subj, crse as t2crse from(
# select t2cid, t1cid, subj as t1subj, crse as t1crse, a.term as term from(
# select T1.cid as t1cid, t2.cid as t2cid, t1.term as term
# from take as t1, take as t2
# where t1.term LIKE '____06' and t1.term = t2.term and t1.cid < t2.cid and t1.sid = t2.sid and (t1.level <> t2.level or t1.class <> t2.class or t1.major <> t2.major)
# ) as a, (select cid, term, subj, crse from course where term LIKE '____06') as b
# where a.term = b.term and t1cid = cid
# ) as c, (select cid, term, subj, crse from course where term like '____06') as d
# where c.term = d.term and t2cid = cid
# order by term, t1subj, t1crse, t2subj, t2crse

cur.execute("insert into temp3e (term, subj1, crse1, sec1, subj2, crse2, sec2) select * from("+ sql3e1 +") as foo; ")

## 2. location and time conflict <- two different course can't take place in same time and same location

#SELECT DISTINCT * FROM (
#SELECT COURSE.TERM AS TERM, T1SUBJ, T1CRSE,T1SEC, SUBJ AS T2SUBJ, CRSE AS T2CRSE, SEC as t2sec
#FROM (
#SELECT COURSE.TERM AS TERM, T2CID, SUBJ AS T1SUBJ, CRSE AS T1CRSE, SEC AS T1SEC
#FROM (
#SELECT A.CID AS T1CID, A.term AS TERM, B.CID AS T2CID
#FROM meetings AS A, meetings AS B
#WHERE A.TERM LIKE '____06' 
#AND A.term = B.term
#AND A.CID < B.CID
#And A.build = B.build
#AND A.room = B.room
#AND A.day = B.day
#AND (A.starttime <= B.endtime AND A.endtime >= B.starttime) 
#) s, course
#WHERE T1CID = course.CID AND s.term = course.term) AS C, COURSE
#WHERE T2CID = COURSE.CID AND c.term = COURSE.TERM AND 
#(SUBJ <> T1SUBJ OR CRSE <> T1CRSE)
#ORDER BY TERM, T1SUBJ, T1CRSE, T2SUBJ, T2CRSE
#) AS T

sql3e2 = "SELECT DISTINCT * FROM (SELECT COURSE.TERM AS TERM, T1SUBJ, T1CRSE,T1SEC, SUBJ AS T2SUBJ, CRSE AS T2CRSE, SEC as t2sec FROM (SELECT COURSE.TERM AS TERM, T2CID, SUBJ AS T1SUBJ, CRSE AS T1CRSE, SEC AS T1SEC FROM (SELECT A.CID AS T1CID, A.term AS TERM, B.CID AS T2CID FROM meetings AS A, meetings AS B WHERE A.TERM LIKE '____06' AND A.term = B.term AND A.CID < B.CID And A.build = B.build AND A.room = B.room AND A.day = B.day AND (A.starttime <= B.endtime AND A.endtime >= B.starttime) ) s, course WHERE T1CID = course.CID AND s.term = course.term) AS C, COURSE WHERE T2CID = COURSE.CID AND c.term = COURSE.TERM AND (SUBJ <> T1SUBJ OR CRSE <> T1CRSE)) AS T"

cur.execute("insert into temp3e (term, subj1, crse1, sec1, subj2, crse2, sec2) select * from("+ sql3e2 +") as foo; ")

cur.execute("select distinct * from temp3e order by term, subj1, crse1, sec1, subj2, crse2, sec2;")
rows = cur.fetchall()
print "The courses that have meeting conflicts are listed below. "
for row in rows:
	print row[0], row[1], row[2], "    ", row[4], row[5]

cur.execute("drop table temp3e;")

# 3f ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print "\n3f\n"

cur.execute("SELECT MAJOR, SUM(GPA*UNITS_RECIEVED), SUM(UNITS_RECIEVED) FROM (SELECT CID, TERM FROM COURSE WHERE SUBJ = 'ABC') AS A, TAKE WHERE A.CID = TAKE.CID AND A.TERM = TAKE.TERM GROUP BY MAJOR;")
rows = cur.fetchall()
majors = {}
for row in rows:
	if row[2] != 0:
		majors[row[0]] = float(row[1])/float(row[2]) 
		#print float(row[1])/float(row[2])

k = list(majors.values())
high = max(k)
low = min(k)
best = []
worst = []
for ind in majors.keys():
	if majors[ind] == low:
		worst.append(ind)
	elif majors[ind] == high:
		best.append(ind)

print "The following major(s) perform(s) the best in ABC courses:"
for i in range(len(best)):
	print best[i]
print "The average GPA of students is %f.\n" %high
print "The following major(s) perform(s) the worst in ABC courses:"
for j in range(len(worst)):
	print worst[j]
print "The average GPA of students is %f." %low

# SELECT MAJOR, SUM(GPA*UNITS_RECIEVED) as d1, SUM(UNITS_RECIEVED) as d2
# FROM (SELECT CID, TERM FROM COURSE WHERE SUBJ = 'ABC') AS A, TAKE
# WHERE A.CID = TAKE.CID AND A.TERM = TAKE.TERM
# GROUP BY MAJOR 

# 3g ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print "\n3g\n"

# part 1: What percent of students transfer into one of the ABC majors? 



sql3g11 = "select count(distinct sid) from (SELECT A.SID as sid FROM (SELECT SID, TERM, major FROM TAKE WHERE MAJOR NOT LIKE 'ABC%' ) AS A, (SELECT SID, TERM FROM TAKE WHERE MAJOR LIKE 'ABC%' AND (SID, TERM) IN (SELECT SID, MAX(TERM) FROM TAKE GROUP BY SID) ) AS B WHERE A.SID = B.SID AND A.TERM < B.TERM  ) as foo;"
cur.execute(sql3g11)
rows = cur.fetchall()
for row in rows:
	q1 = row[0]

# select count(distinct sid) from (
# SELECT SID, TERM,major
# FROM TAKE
# WHERE MAJOR LIKE 'ABC%' AND (SID, TERM) IN (SELECT SID, MAX(TERM) FROM TAKE GROUP BY SID) ) as foo


# select count(distinct sid) from (
#SELECT A.SID as sid FROM
#(SELECT SID, TERM, major 
#FROM TAKE
#WHERE MAJOR NOT LIKE 'ABC%' ) AS A,
#(SELECT SID, TERM
#FROM TAKE
#WHERE MAJOR LIKE 'ABC%' AND (SID, TERM) IN (SELECT SID, MAX(TERM) FROM TAKE GROUP BY SID) ) AS B
#WHERE A.SID = B.SID AND A.TERM < B.TERM  ) as foo


sql3g12 = "select count(distinct sid) from (SELECT SID, TERM,major FROM TAKE WHERE MAJOR LIKE 'ABC%' AND (SID, TERM) IN (SELECT SID, MAX(TERM) FROM TAKE GROUP BY SID) ) as foo;"
cur.execute(sql3g12)
rows = cur.fetchall()
for row in rows:
	q2 = row[0]
	
print "Part 1: the percent of student transfer into one of the ABC majors is %d/%d = %f" %(q1, q2, float(q1)/float(q2)*100)

# part 2: What are the top 5 majors that students transfer from into ABC, and what is the percent of students from each of those majors? 

# SELECT B.MAJOR, COUNT(B.SID) AS COUNT 
# FROM (SELECT SID, TERM FROM TAKE WHERE MAJOR LIKE 'ABC%') AS A, 
#      (SELECT SID, MAJOR, TERM FROM TAKE WHERE MAJOR NOT LIKE 'ABC%') AS B 
# WHERE A.SID = B.SID AND A.TERM > B.TERM GROUP BY B.MAJOR ORDER BY COUNT DESC


sql3g2 = "SELECT B.MAJOR, COUNT(B.SID) AS COUNT FROM (SELECT SID, TERM FROM TAKE WHERE MAJOR LIKE 'ABC%') AS A, (SELECT SID, MAJOR, TERM FROM TAKE WHERE MAJOR NOT LIKE 'ABC%') AS B WHERE A.SID = B.SID AND A.TERM > B.TERM GROUP BY B.MAJOR ORDER BY COUNT DESC;"
cur.execute(sql3g2)
count = 0
tmajor = {}
total = 0
rows = cur.fetchall()
for row in rows:
	count += 1
	if count < 6:
		tmajor[row[0]] = row[1]
	total += row[1]
print "\nPart 2: the top 5 majors that students transfer from into ABC and the percent are:"
for ind in tmajor.keys():
	print ind, str(float(tmajor[ind])/float(total) * 100) +'%' 
		 


conn.commit()
conn.close()

