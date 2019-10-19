from xml.dom import minidom
#absolute file path to xml file
import os
filepath=os.path.abspath('../TwitterEmotionClassification/config.xml')
#tweetconfig=minidom.parse('C:\\Users\\Administrator\\source\\repos\\FPE_Twitter_emotion_classification\\TwitterEmotionClassification\\config.xml')

#open config.xml file
tweetconfig=minidom.parse(filepath)

#No need neccessary to use node" userTweetInformation"
#tweetInformation=tweetconfig.getElementsByTagName('userTweetInformation')
#consumkey=tweetconfig.getElementsByTagName('userTweetInformation')[0].childNodes[0].nodeValue
#information=tweetconfig.getElementsByTagName('userTweetInformation')
#consumkey=information[0].getElementsByTagName('consumerKey')

#reading tweet information from config.xml file
consumKey=tweetconfig.getElementsByTagName('consumerKey')[0].childNodes[0].nodeValue
comsumerSecret=tweetconfig.getElementsByTagName('comsumerSecret')[0].childNodes[0].nodeValue
accessKey=tweetconfig.getElementsByTagName('accessKey')[0].childNodes[0].nodeValue
accessSecret=tweetconfig.getElementsByTagName('accessSecret')[0].childNodes[0].nodeValue

