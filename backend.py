import os
import asyncio
import configparser
import sys
from matplotlib.pylab import f
import requests
from datetime import datetime
import streamlit as st
import pandas as pd
import pydeck as pdk
import streamlit as st

async def get_data_gpsport():
    url = "http://gpsmobile.co:4000/api/DetalleVehiculo/97141/96365"
    payload = {}
    headers = {'Authorization': 'Basic cnV0YSB1bmFiOlJ1dGF1bmFiMS4='}

    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()

        info_text = data['response']['veh']['Info']
        info_parts = info_text.split()
        bat_ext_value = None
        bat_int_value = None
        FdE_data = None
        for part in info_parts:
            if part.startswith('BatExt:'):
                bat_ext_value = part.split(':')[-1]
            elif part.startswith('BatInt:'):
                bat_int_value = part.split(':')[-1]

        lt = data['response']['veh']['Lt']
        lg = data['response']['veh']['Lg']
        vel = data['response']['veh']['Vel']
        std = data['response']['veh']['Std']
        kil_total = data['response']['veh']['kilTotal']
        FdE_data = data['response']['veh']['FdE']

        return lt, lg, vel, std, kil_total, bat_int_value, bat_ext_value, FdE_data
    
    except requests.exceptions.RequestException as e:
        st.error(f"Error durante la solicitud: {e}")
        return None

async def get_data_currentC(lt, lg):
    url = "https://atlas.microsoft.com/weather/currentConditions/json"
    api_version = "1.0"
    subscription_key = "TbrmbyYoqW6lLO6hoWkZG21uPRjcolwsJWbg7CVPW3M"
    language = "es-MX"

    params = {
        'api-version': api_version,
        'query': f'{lt},{lg}',
        'subscription-key': subscription_key,
        'language': language
    }

    try:
        response = requests.request("GET", url, params=params)
        current_conditions = response.json()
        dateTimeCC=current_conditions['results'][0]['dateTime']        
        phraseCC=current_conditions['results'][0]['phrase']
        temperaturaCC=current_conditions['results'][0]['temperature']['value']           
        sensacionTermicaCC=current_conditions['results'][0]['realFeelTemperature']['value']
        humedadrelativaCC=current_conditions['results'][0]['relativeHumidity']
        direcvientoCC=current_conditions["results"][0]["wind"]["direction"]["localizedDescription"]
        velvientoCC=current_conditions['results'][0]['wind']['speed']['value']
        uvIndexCC=current_conditions["results"][0]["uvIndexPhrase"]
        visibilidadCC=current_conditions['results'][0]['visibility']['value']
        cloudCoverCC=current_conditions['results'][0]['cloudCover']
        dewPointCC=current_conditions['results'][0]['dewPoint']['value']
        pressureCC=current_conditions['results'][0]['pressure']['value']
        
        return dateTimeCC, phraseCC, temperaturaCC, sensacionTermicaCC, humedadrelativaCC, direcvientoCC, velvientoCC, uvIndexCC, visibilidadCC, cloudCoverCC, dewPointCC, pressureCC

    except requests.exceptions.RequestException as e:
        st.error(f"Error durante la solicitud: {e}")
        return None
    
async def get_data_air(lt, lg):
    url = "https://atlas.microsoft.com/weather/airQuality/current/json"
    api_version = "1.1"
    subscription_key = "TbrmbyYoqW6lLO6hoWkZG21uPRjcolwsJWbg7CVPW3M"
    language = "es-MX"

    params = {
        'api-version': api_version,
        'query': f'{lt},{lg}',
        'subscription-key': subscription_key,
        'language': language
    }

    try:
        response = requests.request("GET", url, params=params)
        data_air = response.json()
        data_air=data_air["results"][0]
        dateTimeAQ = data_air["dateTime"]
        # Extraer datos y guardarlos en variables
       
        dateTimeAQ = data_air["dateTime"]
        indexAQ = data_air["index"]
        globalIndexAQ = data_air["globalIndex"]
        dominantPollutantAQ = data_air["dominantPollutant"]
        categoryAQ = data_air["category"]
        categoryColorAQ = data_air["categoryColor"]
        descriptionAQ = data_air["description"]
        contaminanteAQ = data_air["pollutants"][0]
        tipoAQ = contaminanteAQ["type"]
        nombreAQ = contaminanteAQ["name"]
        contaminanteIndexAQ = contaminanteAQ["index"]
        contaminanteGlobalIndexAQ = contaminanteAQ["globalIndex"]
        concentracionAQ = contaminanteAQ["concentration"]["value"]
        unidadAQ = contaminanteAQ["concentration"]["unit"]

        return dateTimeAQ, indexAQ, globalIndexAQ, dominantPollutantAQ, categoryAQ, categoryColorAQ, descriptionAQ, contaminanteAQ, tipoAQ, nombreAQ, contaminanteIndexAQ, contaminanteGlobalIndexAQ, concentracionAQ, unidadAQ
        
      
    except requests.exceptions.RequestException as e:
        st.error(f"Error durante la solicitud: {e}")
        return None

async def get_forecast_data(lt, lg):
    url = "https://atlas.microsoft.com/weather/forecast/minute/json"
    api_version = "1.1"
    subscription_key = "TbrmbyYoqW6lLO6hoWkZG21uPRjcolwsJWbg7CVPW3M"
    language = "es-MX"

    params = {
        'api-version': api_version,
        'query': f'{lt},{lg}',
        'subscription-key': subscription_key,
        'language': language
    }
    try:
        response = requests.request("GET", url, params=params)
        dataForecast = response.json()
        # Extraer valores
        #summaryFC=dataForecast["summary"]
        brief_phrase60FC = dataForecast["summary"]["briefPhrase60"]
        short_phraseFC = dataForecast["summary"]["shortPhrase"]
        long_phraseFC = dataForecast["summary"]["longPhrase"]

        start_timeFC = dataForecast["intervals"][0]["startTime"]
        minuteFC = dataForecast["intervals"][0]["minute"]
        dbzFC = dataForecast["intervals"][0]["dbz"]
        short_phrase_intervalFC = dataForecast["intervals"][0]["shortPhrase"]
        cloud_coverFC= dataForecast["intervals"][0]["cloudCover"]

        return brief_phrase60FC, short_phraseFC, long_phraseFC, start_timeFC, minuteFC, dbzFC, cloud_coverFC, short_phrase_intervalFC
    
    except requests.exceptions.RequestException as e:
        st.error(f"Error durante la solicitud: {e}")
        return None

async def telemetry (minuteFC, dbzFC, short_phraseFC, cloudCoverCC, dateTimeCC, dominantPollutantAQ, tipoAQ, nombreAQ, concentracionAQ, descriptionAQ, dateTimeAQ, long_phraseFC, temperaturaCC, humedadrelativaCC, dewPointCC, direcvientoCC, velvientoCC, uvIndexCC, pressureCC):

    from iotc.models import Command, Property
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), "samples.ini"))

    if config["DEFAULT"].getboolean("Local"):
        sys.path.insert(0, "src")   

    from iotc import (
    IOTCConnectType,
    IOTCLogLevel,
    IOTCEvents,
    Command,
    CredentialsCache,
    Storage,
    )
    
    from iotc.aio import IoTCClient 

    device_id = config["DEVICE_A"]["DeviceId"]
    scope_id = config["DEVICE_A"]["ScopeId"]
    key = config["DEVICE_A"]["DeviceKey"]

    class MemStorage(Storage):
        def retrieve(self):
            return None
        def persist(self, credentials):
   #       # a further option would be updating config file with latest hub name
           return None

    # optional model Id for auto-provisioning
    try:
        model_id = config["DEVICE_A"]["ModelId"]
    except:
        model_id = None

    async def on_props(prop:Property):
        print(f"Received {prop.name}:{prop.value}")
        return True

    async def on_commands(command: Command):
        print("Received command {} with value {}".format(command.name, command.value))
        await command.reply() # type: ignore

    async def on_enqueued_commands(command:Command):
        print("Received offline command {} with value {}".format(command.name, command.value))

     # optional model Id for auto-provisioning
    client = IoTCClient( 
        device_id,
        scope_id,
        IOTCConnectType.IOTC_CONNECT_DEVICE_KEY,
        key, 
        storage=MemStorage(),
    )
    if model_id != None:
        client.set_model_id(model_id)
    
    client.set_log_level(IOTCLogLevel.IOTC_LOGGING_ALL)
    client.on(IOTCEvents.IOTC_PROPERTIES, on_props)
    client.on(IOTCEvents.IOTC_COMMAND, on_commands)
    client.on(IOTCEvents.IOTC_ENQUEUED_COMMAND, on_enqueued_commands)

    await client.connect()
    await client.send_property({"writeableProp": 50})
    
    while not client.terminated():
        if client.is_connected():
            await client.send_telemetry(
                {
                'minute': minuteFC,
                'dbz': dbzFC,
                'shortPhrase': short_phraseFC,
                'cloudCover': cloudCoverCC,
                'dateTime': dateTimeCC,
                'dominantPollutant': dominantPollutantAQ,
                'type': tipoAQ,
                'name': nombreAQ,
                'concentration': concentracionAQ,
                'description': descriptionAQ,
                'dateTimecc': dateTimeAQ,
                'phrase': long_phraseFC,
                'temperature': temperaturaCC,
                'relativeHumidity': humedadrelativaCC,
                'dewPoint': dewPointCC,
                'wind': direcvientoCC,
                'speed': velvientoCC,
                'uvIndex': uvIndexCC,
                'pressure': pressureCC
                }
            )
        await asyncio.sleep(3)

def main():
    
  

    lt, lg, vel, std, kil_total, bat_ext_value, bat_int_value, FdE_data = asyncio.run(get_data_gpsport()) # type: ignore

    # Unpack the current weather conditions data
    dateTimeCC, phraseCC, temperaturaCC, sensacionTermicaCC, humedadrelativaCC, direcvientoCC, velvientoCC, uvIndexCC, visibilidadCC, cloudCoverCC, dewPointCC, pressureCC = asyncio.run(get_data_currentC(lt, lg)) # type: ignore

    dateTimeAQ, indexAQ, globalIndexAQ, dominantPollutantAQ, categoryAQ, categoryColorAQ, descriptionAQ, contaminanteAQ, tipoAQ, nombreAQ, contaminanteIndexAQ, contaminanteGlobalIndexAQ, concentracionAQ, unidadAQ = asyncio.run(get_data_air(lt, lg)) # type: ignore
    
    # Unpack the forecast data
    brief_phrase60FC, short_phraseFC, long_phraseFC, short_phrase_intervalFC, start_timeFC, minuteFC, dbzFC, cloud_coverFC =  asyncio.run(get_forecast_data(lt, lg)) # type: ignore

    asyncio.run(telemetry(minuteFC, dbzFC, short_phraseFC, cloudCoverCC, dateTimeCC, dominantPollutantAQ,tipoAQ, nombreAQ, concentracionAQ, descriptionAQ, dateTimeAQ, long_phraseFC, temperaturaCC, humedadrelativaCC, dewPointCC, direcvientoCC, velvientoCC, uvIndexCC, pressureCC))

   


if __name__ == '__main__':
    main()
    
    