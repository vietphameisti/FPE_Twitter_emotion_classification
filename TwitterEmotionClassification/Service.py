#window service library
import win32service, win32serviceutil, win32api, win32con, win32event, win32evtlogutil
import psutil
import subprocess
import os, sys, string, time, socket, signal
import servicemanager

#xml library
from xml.dom import minidom

#
import tweepy 
import pandas


#Reading xml configuration file 
#from xml.dom import minidom

class Service (win32serviceutil.ServiceFramework):
    _svc_name_ = "Service"
    _svc_display_name_ = "Service"

    def __init__(self,args):
        #constructor of window service
        win32serviceutil.ServiceFramework.__init__(self, *args)
        self.log('Service Initialized.')
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)


    def log(self, msg):
        servicemanager.LogInfoMsg(str(msg))

    def sleep(self, sec):
        win32api.Sleep(sec*1000, True)

    def SvcStop(self):
        #Called when the service is asked to stop
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.stop()
        self.log('Service has stopped.')
        win32event.SetEvent(self.stop_event)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def SvcDoRun(self):
        #Called when the service is asked to start
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        try:
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            self.log('Service is starting.')
            self.main()
            win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
            servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,servicemanager.PYS_SERVICE_STARTED,(self._svc_name_, ''))
        except Exception as e:
            s = str(e);
            self.log('Exception :'+s)
            self.SvcStop()

    def stop(self):
        #Override to add logic before the stop
        #eg. invalidating running condition
        self.runflag=False
        try:
            print('stop service')
        except Exception as e:
            self.log(str(e))

    def main(self):
        self.runflag=True
        while self.runflag:
            # block for 24*60*60 seconds and wait for a stop event
            # it is used for a one-day loop
            rc = win32event.WaitForSingleObject(self.stop_event, 24*60*60)
            # Check to see if self.hWaitStop happened
            if rc == win32event.WAIT_OBJECT_0:
                self.log("Service has stopped")
                break
            else:
                try:
                    #reading cofig.xml file, take tweet user information
                    filepath=os.path.abspath('../TwitterEmotionClassification/config.xml')
                    tweetconfig=minidom.parse(filepath)

                    consumKey=tweetconfig.getElementsByTagName('consumerKey')[0].childNodes[0].nodeValue
                    comsumerSecret=tweetconfig.getElementsByTagName('comsumerSecret')[0].childNodes[0].nodeValue
                    accessKey=tweetconfig.getElementsByTagName('accessKey')[0].childNodes[0].nodeValue
                    accessSecret=tweetconfig.getElementsByTagName('accessSecret')[0].childNodes[0].nodeValue
                    
                    #searching topic information
                    search_words=tweetconfig.getElementsByTagName('searchWords')[0].childNodes[0].nodeValue
                    date_since=tweetconfig.getElementsByTagName('dateSince')[0].childNodes[0].nodeValue
                    nb_tweets=tweetconfig.getElementsByTagName('nbTweets')[0].childNodes[0].nodeValue
                    language=tweetconfig.getElementsByTagName('lang')[0].childNodes[0].nodeValue
                    
                    auth = tweepy.OAuthHandler(consumKey, comsumerSecret)
                    auth.set_access_token(accessKey, accessSecret)
                    api = tweepy.API(auth, wait_on_rate_limit=True)

                    tweets = tweepy.Cursor(api.search,q=search_words,lang=language,since=date_since).items(nb_tweets)
                    users_locs = [[tweet.user.screen_name, tweet.user.location] for tweet in tweets]
                    users_infos = [[tweet.user.screen_name, tweet.user.location, tweet.text,tweet.lang,tweet.favorite_count,tweet.retweet_count,tweet.created_at] for tweet in tweets]
                    df_tweets = pandas.DataFrame(data=users_infos,columns=['user', "location","tweet content","language","nb_favorite","nb_retweet","created_at"])
                    df_tweets.to_csv(r'../TwitterEmotionClassification/tweetdata.csv',index=None, header=True)
                except Exception as e:
                    self.log(str(e))

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(Service)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(Service)
