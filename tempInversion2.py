# David Fisher
# 7/14/2017

import datetime
import bs4
import pytz
import requests
import urllib.request
import codecs
import csv


# goes to a website, finds a table on the page and inserts it into a 2d list
# then processes the data added to table (covert text to necessary formats)
# and returns the data for the current day
# input: url = string
# output: todaysData = 2d list
def getDataFromHTML(url):
    # get html from website
    html = requests.get(url)

    # get table from html
    data = [[cell.text.strip() for cell in row('td')] for row in bs4.BeautifulSoup(html.content, "html5lib")('tr')]
    # add column labels
    data[0] = ['Record Date', 'Record Time', 'Record Julian Date', 'Air Temp Max', 'Time Max Air Temp', 'Air Temp Min',
               'Time Min Air Temp', 'Air Temp Obs', 'Rel Hum Max', 'Time Max Rel Hum', 'Rel Hum Min',
               'Time Min Rel Hum ', 'Rel Hum Obs', 'Precip', 'Wind Speed', 'Wind Dir', 'Solar Rad',
               'Soil Temp Avg 2 in', 'Soil Temp Avg 2 in', 'Soil Temp Avg 4 in', 'Soil Temp Obs 4 in']

    # remove last two rows, which are unnecessary
    data.pop(-1)
    data.pop(-1)

    # remove unnecessary columns
    for row in data:
        row.pop(2)
        row.pop(7)
        row.pop(7)
        row.pop(7)
        row.pop(7)
        row.pop(7)
        row.pop(7)
        row.pop(8)
        row.pop(8)
        row.pop(8)
        row.pop(8)
        row.pop(8)
        row.pop(8)

    # convert text to float for temperature, humidity, precipitation, and wind speed
    # if data is blank use NaN (not a number)
    for i in range(1, len(data), 1):
        if (data[i][2] == ''):
            data[i][2] = float('NaN')
        else:
            data[i][2] = float(data[i][2])

        if (data[i][4] == ''):
            data[i][4] = float('NaN')
        else:
            data[i][4] = float(data[i][4])

        if (data[i][6] == ''):
            data[i][6] = float('NaN')
        else:
            data[i][6] = float(data[i][6])

        if (data[i][7] == ''):
            data[i][7] = float('NaN')
        else:
            data[i][7] = float(data[i][7])

    # place data from today's date in a seperate table
    todaysData = []
    today = datetime.datetime.today()
    for row in data[1:]:
        if (today.date() == datetime.datetime.strptime(row[0], '%m/%d/%Y').date()):
            todaysData.append(row)

    return todaysData

# get data from CSV file at URL and insert into table (2d list)
# then processes the data added to table (covert text to necessary formats)
# input: url = string
# output: data = 2d list
def getDataFromCSV(url):
    # Opens a CSV file at url and adds data to 2d list
    dataStream = urllib.request.urlopen(url)
    csvFile = csv.reader(codecs.iterdecode(dataStream, 'utf-8'))
    data = []
    for line in csvFile:
        data.append(line)

    # Remove last two rows, which are empty
    data = data[:-2]

    # Remove blank entries from data
    for index, row in enumerate(data):
        if (row[2] == "" or row[3] == "" or row[4] == "" or row[5] == ""):
            data.pop(index)

    # Rename first row to labels
    data[0][2] = 'Air Temp'
    data[0][3] = 'Wind Speed'
    data[0][4] = 'Lux'
    data[0][5] = 'Batt Volt'

    # Converts the timestamps from text to datetime objects
    dates = []
    # Skip first row in data which doesn't contain data
    for row in data[1:]:
        dates.append(datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S %Z"))

    # Heroku servers use UTC time
    # Converts the timestamps from utc to central timezone
    for i in range(0, len(dates), 1):
        dates[i] = utcToLocal(dates[i])

    # Replaces the text timestamps with the corrected datetime objects
    j = 0
    for i in range(1, len(data), 1):
        data[i][0] = dates[j]
        j += 1

    # Convert temperature text to float
    for i in range(1, len(data), 1):
        data[i][2] = float(data[i][2])

    # Convert windspeed text to float
    for i in range(1, len(data), 1):
        data[i][3] = float(data[i][3])

    return data



# prints the data in a readible format for error checking
# input: data = 2d list
def printData(data):
    data.insert(0, ['Record Date', 'Record Time', 'Air Temp Max', 'Time Max Air Temp', 'Air Temp Min',
                    'Time Min Air Temp', 'Air Temp Obs', 'Wind Speed'])
    temp = data

    s = [[str(e) for e in row] for row in temp]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
    table = [fmt.format(*row) for row in s]
    print('\n'.join(table))

# prints a list of results for error checking with a label
# input: results = 2d list
def printResults(results):
    print("| {0:^10} | {1:^20} | {2:^20} | {3:^21} | {4:^15} | {5:^20} | {6:^15} | {7:^20} | {8:^20} |".format(
        "Inversion", "Most Recent Temp", "Most Recent Time", "Most Recent Windspeed", "Low Temp", "Time of Low",
        "High Temp", "Time of High", "More than an Hour"))
    print("-" * 189)
    for result in results:
        printResult(result)

# prints the result of the tempInv function in a readible format for error checking
# input: result = list
def printResult(result):
    if result[0]:
        print("| {0:^10} | {1:^20} | {2:^20} | {3:^21} | {4:^15} | {5:^20} | {6:^15} | {7:^20} | {8:^20} |".format(
            "Yes", result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8]))
    else:
        print("| {0:^10} | {1:^20} | {2:^20} | {3:^21} | {4:^15} | {5:^20} | {6:^15} | {7:^20} | {8:^20} |".format(
            "No", result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8]))



# determines if daylight savings time is in effect
def daylightSavings(zonename):
    tz = pytz.timezone(zonename)
    now = pytz.utc.localize(datetime.datetime.utcnow())
    return now.astimezone(tz).dst() != datetime.timedelta(0)

# converts datetime object from UTC to local timezone
# input: utc = datetime
# output: utc+offset = datetime
def utcToLocal(utc):
    timezone = 'America/Chicago'
    tz = pytz.timezone('America/Chicago')
    if (daylightSavings(timezone)):
        return pytz.utc.localize(utc, is_dst=True).astimezone(tz)
    else:
        return pytz.utc.localize(utc, is_dst=False).astimezone(tz)

# checks if more than an hour has passed since the data was last updated
# returns true if it has, false if not
# input: mostRecentTime = dateTime
# output: moreThanAnHour = boolean
def updatedLastHour(mostRecentTime):
    # Convert now from UTC to central time
    # now = utcToLocal(datetime.datetime.now())

    # Use the following code for local hosting/error checking because
    # otherwise 5/6 hours will be subtracted from the current time on the computer
    # and the fuction will always return false
    now = pytz.utc.localize(datetime.datetime.utcnow())
    delta = now - mostRecentTime

    # Check if more than an hour has passed
    if (delta.seconds / 60) > 60:
        moreThanAnHour = True
    else:
        moreThanAnHour = False
    return moreThanAnHour



# gets lowest temperature of the day by
# searching entries in table (2d list) between the beginning
# of the current day and the last entry (most recent time)
# inputs: data = 2d list
# output: lowTemp = tuple(int, int)
def getLowTempFromHTML(data):
    lowTemp = data[0][4]
    index = 0

    # Search new list for most lowest temp (uses most recent if there are matches)
    for i in range(0, len(data), 1):
        if (data[i][4] <= lowTemp and i > index):
            lowTemp = data[i][4]
            index = i
    return (lowTemp, index)

# gets highest temperature of the day by
# searching entries in table (2d list) between the beginning
# of the current day and the last entry (most recent time)
# inputs: data = 2d list
# output: highTemp = tuple(int, int)
def getHighTempFromHTML(data):
    highTemp = data[0][2]
    index = 0

    # Search new list for highest temp (uses most recent if there are matches)
    for i in range(0, len(data), 1):
        if (data[i][2] >= highTemp and i > index):
            highTemp = data[i][2]
            index = i
    return (highTemp, index)

# gets lowest temperature of the day by
# searching entries in table (2d list) between the beginning
# of the current day and the last entry (most recent time)
# inputs: mostRecentTime = datetime, data = 2d list
# output: lowTemp = tuple(int, datetime)
def getLowTempFromCSV(mostRecentTime, data):
    currentDay = []
    # Adds timestamps from current day to new list
    for row in data[1:]:
        if row[0].month == mostRecentTime.month and row[0].day == mostRecentTime.day:
            currentDay.append(row)

    lowTemp = currentDay[0][2]
    index = 0

    # Search new list for lowest temp
    for i in range(0, len(currentDay), 1):
        if currentDay[i][2] < lowTemp:
            lowTemp = currentDay[i][2]
            index = i
    return (lowTemp, currentDay[index][0])

# gets highest temperature of the day by
# searching entries in table (2d list) between the beginning
# of the current day and the last entry (most recent time)
# inputs: mostRecentTime = datetime, data = 2d list
# output: highTemp = tuple(int, datetime)
def getHighTempFromCSV(mostRecentTime, data):
    currentDay = []
    # Adds timestamps from current day to new list
    for row in data[1:]:
        if row[0].month == mostRecentTime.month and row[0].day == mostRecentTime.day:
            currentDay.append(row)

    highTemp = currentDay[0][2]
    index = 0

    # Search new list for highest temp
    for i in range(0, len(currentDay), 1):
        if currentDay[i][2] > highTemp:
            highTemp = currentDay[i][2]
            index = i
    return (highTemp, currentDay[index][0])



# determines whether there is a temperature inversion
# input: data = 2d list
# output: list (inversion, recent temp, recent time, recent wind speed, low temp,
#               low temp time, high temp, high temp time, updated within last hour)
def tempInvFromHTML(data):
    # Check if data is empty
    # If it is, return empty result
    if (not data):
        return [True, 0, 0, 0, 0, 0, 0, 0, True]

    # Get most recent data
    mostRecentTime = datetime.datetime.strptime(data[-1][0] + " " + data[-1][1], '%m/%d/%Y %H:%M:%S')
    # Need to check this, currently using most recent max temp
    mostRecentTemp = data[-1][6]
    mostRecentWindSpeed = data[-1][7]

    # Get high and low temp
    lowTemp = getLowTempFromHTML(data)
    highTemp = getHighTempFromHTML(data)

    # Determine if there is an inversion
    # Check if before noon
    if (mostRecentTime.time() < datetime.time(12)):
        if (mostRecentTemp - lowTemp[0] > 3):
            # no inversion and spray OK
            return [False, mostRecentTemp, str(mostRecentTime.time()), mostRecentWindSpeed, lowTemp[0],
                    data[lowTemp[1]][5], highTemp[0], data[highTemp[1]][3], False]
        else:
            if ((mostRecentTemp - lowTemp[0]) < 2):
                # strong inversion and no spray suggested
                return [True, mostRecentTemp, str(mostRecentTime.time()), mostRecentWindSpeed, lowTemp[0],
                        data[lowTemp[1]][5], highTemp[0], data[highTemp[1]][3], False]
            else:
                if ((mostRecentTemp - lowTemp[0]) < 2 and mostRecentWindSpeed > 4):
                    # no inversion and spray OK
                    return [False, mostRecentTemp, str(mostRecentTime.time()), mostRecentWindSpeed, lowTemp[0],
                            data[lowTemp[1]][5], highTemp[0], data[highTemp[1]][3], False]
                else:
                    # strong inversion and no spray suggested
                    return [True, mostRecentTemp, str(mostRecentTime.time()), mostRecentWindSpeed, lowTemp[0],
                            data[lowTemp[1]][5], highTemp[0], data[highTemp[1]][3], False]
    else:
        if ((highTemp[0] - mostRecentTemp) <= 5):
            # no inversion and spray OK
            return [False, mostRecentTemp, str(mostRecentTime.time()), mostRecentWindSpeed, lowTemp[0],
                    data[lowTemp[1]][5], highTemp[0], data[highTemp[1]][3], False]
        else:
            if ((highTemp[0] - mostRecentTemp) >= 7):
                # strong inversion and no spray suggested
                return [True, mostRecentTemp, str(mostRecentTime.time()), mostRecentWindSpeed, lowTemp[0],
                        data[lowTemp[1]][5], highTemp[0], data[highTemp[1]][3], False]
            else:
                if (mostRecentTemp - highTemp[0]) >= 7 and mostRecentWindSpeed > 4:
                    # no inversion and spray OK
                    return [False, mostRecentTemp, str(mostRecentTime.time()), mostRecentWindSpeed, lowTemp[0],
                            data[lowTemp[1]][5], highTemp[0], data[highTemp[1]][3], False]
                else:
                    # strong inversion and no spray suggested
                    return [True, mostRecentTemp, str(mostRecentTime.time()), mostRecentWindSpeed, lowTemp[0],
                            data[lowTemp[1]][5], highTemp[0], data[highTemp[1]][3], False]

# determines whether there is a temperature inversion
# returns true if there is an inversion or false if not
def tempInvFromCSV(data):
    # Get most recent data
    mostRecentTime = data[-1][0]
    mostRecentTemp = float(data[-1][2])
    mostRecentWindSpeed = float(data[-1][3])

    # check if the data has been updated recently
    moreThanAnHour = updatedLastHour(mostRecentTime)

    # Get high and low temp
    lowTemp = getLowTempFromCSV(mostRecentTime, data)
    highTemp = getHighTempFromCSV(mostRecentTime, data)

    # Determine if there is an inversion
    # Check if before noon
    if mostRecentTime.time() < datetime.time(12):
        if mostRecentTemp - lowTemp[0] > 3:
            # no inversion and spray OK
            return [False, mostRecentTemp, str(mostRecentTime)[11:19], mostRecentWindSpeed, lowTemp[0], 
            str(lowTemp[1])[11:19], highTemp[0], str(highTemp[1])[11:19], moreThanAnHour]
        else:
            if (mostRecentTemp - lowTemp[0]) < 2:
                # strong inversion and no spray suggested
                return [True, mostRecentTemp, str(mostRecentTime)[11:19], mostRecentWindSpeed, lowTemp[0],
                        str(lowTemp[1])[11:19], highTemp[0], str(highTemp[1])[11:19], moreThanAnHour]
            else:
                if (mostRecentTemp - lowTemp[0]) < 2 and mostRecentWindSpeed > 4:
                    # no inversion and spray OK
                    return [False, mostRecentTemp, str(mostRecentTime)[11:19], mostRecentWindSpeed, lowTemp[0],
                            str(lowTemp[1])[11:19], highTemp[0], str(highTemp[1])[11:19], moreThanAnHour]
                else:
                    # strong inversion and no spray suggested
                    return [True, mostRecentTemp, str(mostRecentTime)[11:19], mostRecentWindSpeed, lowTemp[0],
                            str(lowTemp[1])[11:19], highTemp[0], str(highTemp[1])[11:19], moreThanAnHour]
    else:
        if abs(mostRecentTemp - highTemp[0]) <= 5:
            # no inversion and spray OK
            return [False, mostRecentTemp, str(mostRecentTime)[11:19], mostRecentWindSpeed, lowTemp[0], 
            str(lowTemp[1])[11:19], highTemp[0], str(highTemp[1])[11:19], moreThanAnHour]
        else:
            if (mostRecentTemp - highTemp[0]) >= 7:
                # strong inversion and no spray suggested
                return [True, mostRecentTemp, str(mostRecentTime)[11:19], mostRecentWindSpeed, lowTemp[0],
                        str(lowTemp[1])[11:19], highTemp[0], str(highTemp[1])[11:19], moreThanAnHour]
            else:
                if (mostRecentTemp - highTemp[0]) >= 7 and mostRecentWindSpeed > 4:
                    # no inversion and spray OK
                    return [False, mostRecentTemp, str(mostRecentTime)[11:19], mostRecentWindSpeed, lowTemp[0],
                            str(lowTemp[1])[11:19], highTemp[0], str(highTemp[1])[11:19], moreThanAnHour]
                else:
                    # strong inversion and no spray suggested
                    return [True, mostRecentTemp, str(mostRecentTime)[11:19], mostRecentWindSpeed, lowTemp[0],
                            str(lowTemp[1])[11:19], highTemp[0], str(highTemp[1])[11:19], moreThanAnHour]



def main():
    htmlURLs = [("http://deltaweather.extension.msstate.edu/7-days-hourly-table/DREC-2005", "Verona"),
            ("http://deltaweather.extension.msstate.edu/7-days-hourly-table/DREC-2013", "Mound Bayou"),
            ("http://deltaweather.extension.msstate.edu/7-days-hourly-table/DREC-2002", "Thighman Lake"),
            ("http://deltaweather.extension.msstate.edu/7-days-hourly-table/DREC-2012", "Stockett Farm"),
            ("http://deltaweather.extension.msstate.edu/7-days-hourly-table/DREC-2003", "Sidon"),
            ("http://deltaweather.extension.msstate.edu/7-days-hourly-table/DREC-2007", "Prairie"),
            ("http://deltaweather.extension.msstate.edu/7-days-hourly-table/DREC-2001", "Lyon"),
            ("http://deltaweather.extension.msstate.edu/7-days-hourly-table/DREC-2011", "Jackson Co."),
            ("http://deltaweather.extension.msstate.edu/7-days-hourly-table/DREC-2006", "Brooksville"),
            ("http://deltaweather.extension.msstate.edu/7-days-hourly-table/DREC-2010", "Bee Lake")]

    csvURLs = [("https://thingspeak.com/channels/211013/feed.csv", "Stoneville 1"),
               ("https://thingspeak.com/channels/282031/feed.csv", "Stoneville 2"),
               ("https://thingspeak.com/channels/216976/feed.csv", "Stoneville 3"),
               ("https://thingspeak.com/channels/287811/feed.csv", "Stoneville 2B"),
               ("https://thingspeak.com/channels/288782/feed.csv", "Stoneville 3B")]

    results = []

    for i in range(0, len(htmlURLs), 1):
        data = getDataFromHTML(htmlURLs[i][0])
        results.append(tempInvFromHTML(data))
        results[i].append(htmlURLs[i][1])

    for url in csvURLs:
        data = getDataFromCSV(url[0])
        result = tempInvFromCSV(data)
        result.append(url[1])
        results.append(result)

    return results


if __name__ == "__main__":
    main()
