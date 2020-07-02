#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 16 04:06:12 2020

@author: sarah
"""

# Python program to find current  
# weather details of any city 
# using openweathermap api 
  
# import required modules 
import requests 
  
# Enter your API key here 
api_key = "5267ec177c341d1b4bb7e79ce881a183"
  
# base_url variable to store url 
base_url = "http://api.openweathermap.org/data/2.5/weather?"
  
# Give city name 
#city_name = input("Enter city name : ") 

def weather(city_name):
    # complete_url variable to store 
    # complete url address 
    complete_url = base_url + "appid=" + api_key + "&q=" + city_name 
      
    # get method of requests module 
    # return response object 
    response = requests.get(complete_url) 
      
    # json method of response object  
    # convert json format data into 
    # python format data 
    x = response.json() 
      
    # Now x contains list of nested dictionaries 
    # Check the value of "cod" key is equal to 
    # "404", means city is found otherwise, 
    # city is not found 
    if x["cod"] != "404": 
      
        # store the value of "main" 
        # key in variable y 
        y = x["main"] 
      
        # store the value corresponding 
        # to the "temp" key of y 
        current_temperature = y["temp"] 
      
        # store the value corresponding 
        # to the "pressure" key of y 
        current_pressure = y["pressure"] 
      
        # store the value corresponding 
        # to the "humidity" key of y 
        current_humidiy = y["humidity"] 
      
        # store the value of "weather" 
        # key in variable z 
        z = x["weather"] 
      
        # store the value corresponding  
        # to the "description" key at  
        # the 0th index of z 
        weather_description = z[0]["description"] 
      
        # print following values 
        weather_detail = "Temperature is " + str(round((current_temperature- 273.15)*9/5+32,3)) + ' °F'
        weather_detail += ". Atmospheric pressure is " + str(current_pressure) +" hPa"
        weather_detail += ". Humidity is " + str(current_humidiy) + " %"
        weather_detail += ". Total description is " + str(weather_description) + '.'
      
    else: 
        weather_detail = " City Not Found "
        
    return weather_detail