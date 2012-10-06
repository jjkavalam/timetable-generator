"""
	Workplanner software v1.0
	Given a set of (task, deadline, duration) and the availability of
	time on each day, outputs a daily timetable.

	Algorithm of planning:
		Go through each task in the order of nearest deadline first.
			schedule_task()
			if FAILURE
				backtrack

"""
import datetime as dt
import copy
import operator
# Data structures
# Number of units available on each day
# Tasks scheduled on the day

def getDate(datestr):
	""" Returns the datetime object given a date string 
		http://www.seehuhn.de/pages/pdate#sec:1.2.0
	"""
	return dt.datetime.strptime(datestr,"%Y-%m-%d")
def dispDate(date):
	return date.strftime("%A, %d/%m/%y")
"""
tasks = {
	0:{"name":"VLSI Tech Tutorial test","deadline":getDate("2012-10-07"),"length":6,"days":[]},
	1:{"name":"Testing learn algos","deadline":getDate("2012-10-09"),"length":8,"days":[]},
	2:{"name":"VDA","deadline":getDate("2012-10-06"),"length":6,"days":[]}		
}
"""
f = file("tasks.list","r")
taskid = 0
tasks = {}
ln = 0
while(1):
	line = f.readline()
	ln = ln + 1
	if line == "":
		print "EOF"
		break
	tokens = line.split()
	try:
		tokens.index(":")
	except ValueError:	
		print "Separator : not found. White space error in ",ln
		continue

	if len(tokens) < 3:
		print "Invalid line ", ln
		continue
	[key,value] = [tokens[0].lower(),tokens[2]]
	if key == "task":
		if (value > 0):
			if value in tasks:
				print "Task already exists ",ln
				taskid = 0
			else:
				taskid = int(value)
				tasks[taskid] = {}
		else:
			print "**Error: Invalid task id ",ln
	else:
		if taskid > 0:
			if key == "name":
				tasks[taskid][key] = line.split(":")[1].strip()
			if key == "deadline":
				tasks[taskid][key] = getDate(value)
			if key == "length":
				tasks[taskid][key] = int(value)

f.close()

stasks = {}
for taskid in tasks:
	stasks[taskid] = tasks[taskid]["deadline"]
sorted_tasks = sorted(stasks.iteritems(), key=operator.itemgetter(1))

"""	
	Prepare the days list with the available number of slots
"""		
today = dt.datetime.now()
today = dt.datetime(today.year,today.month,today.day)

lastdeadline = today
for taskid in stasks:
	if stasks[taskid] > lastdeadline:
		lastdeadline = stasks[taskid]
print "Latest deadline is ", lastdeadline

days = []
day = today
while(1):
	if lastdeadline < day:
		break	
	days.append(day)
	day = day + dt.timedelta(1)
days.append(day)

weeksData = [
	{"tot_t":3,"rem_time":3,"tasks":{}},
	{"tot_t":3,"rem_time":3,"tasks":{}},
	{"tot_t":3,"rem_time":3,"tasks":{}},
	{"tot_t":3,"rem_time":3,"tasks":{}},
	{"tot_t":3,"rem_time":3,"tasks":{}},
	{"tot_t":3,"rem_time":3,"tasks":{}},
	{"tot_t":3,"rem_time":3,"tasks":{}},
]
weeks = 1 + (lastdeadline-today).days / 7
print "Considering ",weeks, "weeks."

daysData = []
for i in range(weeks):
	daysData.extend(copy.deepcopy(weeksData))

def getDay(date):	
	global daysData, today
	print "Fetching day record of ",date
	return daysData[(date-today).days]

f = file("days.list")
ln = 0
while(1):
	line = f.readline()
	ln = ln + 1
	if line == "":
		print "EOF"
		break
	try:
		tokens.index(":")
	except ValueError:	
		print "Separator : not found. White space error in ",ln
		continue
	tokens = line.split()
	if len(tokens) < 3:
		print "Invalid line ", ln
		continue
	[key,value] = [tokens[0].lower(),tokens[2]]	
	if getDate(key) > lastdeadline:
		break
	getDay(getDate(key))["rem_time"] = int(value)
	getDay(getDate(key))["tot_time"] = int(value)
	print getDay(getDate(key))
f.close()

print """
	Time available on each day
"""	
for date in days:
	if date > lastdeadline:
		break
	print dispDate(date), getDay(date)["rem_time"]
	
def schedule(date,taskid):
	global days
	try: 
		getDay(date)["tasks"][taskid] += 1
	except KeyError:
		getDay(date)["tasks"][taskid] = 1
	getDay(date)["rem_time"] -= 1			

tasksScheduled = 0	
for item in sorted_tasks:
	taskid, deadline = item
	daysleft = (deadline - today) - dt.timedelta(2)
	daysleft = daysleft.days
	length = tasks[taskid]["length"]	
	print "=====", tasks[taskid]["name"],"======="
	print daysleft, "days left. ", length, " time to be put in"
	if daysleft <= 0:
		print "Panic: Deadline is here"
		continue
	Done = False
	while(not Done):
		for date in days:
			if length == 0:
				print " Successfully scheduled"
				Done = True
				break
			if date  > deadline - dt.timedelta(2):
				break
			Scheduled = False				
			if getDay(date)["rem_time"] > 0:
				schedule(date,taskid)
				length -= 1
				Scheduled = True
			else:
				for prevdate in days:
					if prevdate >= date:
						break
					if getDay(prevdate)["rem_time"] > 0:
						schedule(prevdate,taskid)
						Scheduled = True
						length -= 1
						break
				if Scheduled is False:
					for nextdate in days:
						if nextdate  > deadline - dt.timedelta(2):
							break					
						if nextdate <= date:
							continue
						if getDay(nextdate)["rem_time"] > 0:
							schedule(nextdate,taskid)
							Scheduled = True
							length -= 1
							break
				if Scheduled is False:
					break
		if (length>0 and not Scheduled):
			print "Not enough time available to complete before deadline" 
			break			
	if Done is True :
		tasksScheduled += 1
"""
	Now produce the time table
"""
f = file("timetable.html","w")
f.write(
""" <html>	
	<h1>Time table </h1>
	<I> Update: %s </I>
	<hr />
	<table border = 1>
	<tr>
		<td>Date</td>
		<td>Total time</td>
		<td>Tasks [slots]</td>
		<td>Free</td>
	</tr>
"""%(str(dt.datetime.now())))
for date in days:
	if date > lastdeadline:
		break
	if len(getDay(date)["tasks"]) > 0:
		f.write( "<tr><td> %s </td><td > %d </td><td>"%(dispDate(date),getDay(date)["tot_time"]))
		for task in getDay(date)["tasks"]:
			f.write("<br>%s [%d]"% (tasks[task]["name"], getDay(date)["tasks"][task]))
		f.write( "</td>")
		f.write("<td>%s</td></tr>"%(getDay(date)["rem_time"]))
f.write("""
	</table>	
	<br>%d out of %d tasks scheduled.	
	</html>
"""%(tasksScheduled,len(tasks)))	
f.close()	
