import http.client
import urllib
import os
import time

# general global variables
TwitterAccountOfYourInternetProvider = "@AIRTEL_KE"  # Twitter Account of your Internet Provider. for example,
# @YourInternetProvicer
NameOfYourCity = "NAIROBI"  # Name of your city
APIKeyThingSpeak = 'ZCIDESYH0GJFMJ52'  # replace 'K' sequence by your API_KEY of ThingTweet
WriteAPIKey = '3Q9SLZQYUVBASNQK'  # replace 'W' sequence by your WriteAPIKey (you can get it from your thingSpeak channel settings)

# Downtime monitor global variables
InitialTimeStamp_DownTime = 0
IsItOffline = 0
TotalDownTime = 0
DowntimeReportFile = "DownTimeReport.txt"
NumberOfDetectedDowntimes = 0
AttemptNumber = 1
DowntimeLimitForRegistration = 180000000  # in seconds.


def VerifyAndRegisterDowntime(res):
    global IsItOffline
    global InitialTimeStamp_DownTime
    global TotalDownTime
    global DowntimeReportFile
    global NumberOfDetectedDowntimes
    global AttemptNumber

    if res == 0:
        print(" ")
        print("Internet is up!")
    else:
        print(" ")
        print("Internet is down...")

    # Check if Internet was on and now it's off
    if (res != 0) and (IsItOffline == 0):
        InitialTimeStamp_DownTime = time.time()
        IsItOffline = 1
        return

    # Check if Internet was off and now it's on
    if (res == 0) and (IsItOffline == 1):
        TotalDownTime = time.time() - InitialTimeStamp_DownTime

        if TotalDownTime > DowntimeLimitForRegistration:  # check if this downtime must be registered into report file
            StringDT = "DownTime below limit was detected: " + str(TotalDownTime) + " seconds offline\n"
        else:
            StringDT = "DownTime above limit was detected: " + str(TotalDownTime) + " seconds offline\n"
        print(StringDT)
        TxtFile = open(DowntimeReportFile, "a")
        TxtFile.write(StringDT)
        TxtFile.close()
        NumberOfDetectedDowntimes = NumberOfDetectedDowntimes + 1
        IsItOffline = 0
        SendTweet(TotalDownTime)
        SendThingSpeak(TotalDownTime)
        return


def SendTweet(DuracaoDT):
    global TwitterAccountOfYourInternetProvider
    global NameOfYourCity
    global APIKeyThingSpeak

    StringToTweet = TwitterAccountOfYourInternetProvider + ", a downtime was detected: " + str(
        DuracaoDT) + " s. I'm located on " + NameOfYourCity + ". #DownTimeDetected"
    params = urllib.parse.urlencode({'api_key': APIKeyThingSpeak, 'status': StringToTweet})
    conn = http.client.HTTPConnection("api.thingspeak.com:80")
    # conn = httplib2.HTTPConnection("api.thingspeak.com:80")
    conn.request("POST", "/apps/thingtweet/1/statuses/update", params)
    resp = conn.getresponse()
    conn.close()


def SendTweetDownTimeStarted():
    global APIKeyThingSpeak

    StringToTweet = "Downtime monitor was started!"
    params = urllib.parse.urlencode({'api_key': APIKeyThingSpeak, 'status': StringToTweet})
    conn = http.client.HTTPConnection("api.thingspeak.com:80")
    conn.request("POST", "/apps/thingtweet/1/statuses/update", params)
    resp = conn.getresponse()
    conn.close()


def SendThingSpeak(TimeIntervalDT):
    global WriteAPIKey

    params = urllib.parse.urlencode({'field1': str(TimeIntervalDT), 'key': WriteAPIKey})
    headers = {"Content-typZZe": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = http.client.HTTPConnection("api.thingspeak.com:80")
    conn.request("POST", "/update", params, headers)
    resp = conn.getresponse()


# ----------------------
#  MAIN LOOP
# ----------------------

SendTweetDownTimeStarted()

while True:
    try:
        # cmd = "date"
        os.system("clear")
        print("---------------------------")
        print("     DownTime Monitor      ")
        print("---------------------------")
        print(" ")
        print("Attempt #" + str(AttemptNumber) + " - " + str(NumberOfDetectedDowntimes) + " downtime(s) were detected")
        print(" ")

        PingResult = os.system("ping -s 1 8.8.8.8")
        # PingResult = os.system("ping -s 1 154.79.243.253")
        VerifyAndRegisterDowntime(PingResult)
        time.sleep(2000)
        AttemptNumber = AttemptNumber + 1
    except KeyboardInterrupt:
        print("Goodbye!")
        exit(1)
