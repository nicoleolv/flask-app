#!/usr/bin/env python3
import requests
import math
from datetime import datetime
import xml.etree.ElementTree as ET
from flask import Flask, request, jsonify
from geopy.geocoders import Nominatim

app = Flask(__name__)

def loadISS() -> None:
        """
        Loads the ISS data using the requests library
        """
        url = 'https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml'
        response = requests.get(url)
        with open('iss_oem.xml', 'wb') as f:
                f.write(response.content)
                
def parseXML(xmlfile: str) -> list:
        """
        Parses xmlfile and stores into a list of dictionaries

        Args:
            xmlfile (str):

        Returns:
            data (list of dictionaries): Stores necessary elements from our xmlfile
        """
        tree = ET.parse(xmlfile)
        root = tree.getroot()
        data = []
        for element in root.findall('.//stateVector'):
                epoch = datetime.strptime(element.find('EPOCH').text, '%Y-%jT%H:%M:%S.%fZ')   # matches format of '2024-047T12:0000.000Z'
                x_dot = float(element.find('X_DOT').text)
                y_dot = float(element.find('Y_DOT').text)
                z_dot = float(element.find('Z_DOT').text)
                data.append({'epoch': epoch, 'x_dot': x_dot, 'y_dot': y_dot, 'z_dot': z_dot})
        return data

loadISS()
data = parseXML('iss_oem.xml')

# new stuff
with open('iss_oem.xml', 'r') as f:
    big_data = xmltodict.parse(f.read())

@app.route('/epochs', methods=['GET'])
def get_epochs():
        """
        Returns entire data set
        """
        return jsonify(data)   # converts into json type

# need to add app.route('/epochs?)
@app.route('/epochs', methods=['GET'])
def epochs():
        limit = request.args.get('limit', 10)
        offset = request.args.get('offset', 0)
        try:
                limit = int(limit)
        except ValueError:
                return "Invalid parameters, must be an integer"
        try:
                offset = int(offset)
        except ValueError:
                return "Invalid parameters, must be an integer"

        limit = int(limit)
        offset = int(offset)

        return_data = []
        item_count = 0
        for item in data:
                if item_count == offset:
                        return_data.append(item)
                item_count += 1

                if len(return_data) == limit:
                        return(return_data)

        return jsonify(return_data)
                
# might need debugging 
@app.route('/epochs/<epoch>', methods=['GET'])
def specific_epoch(epoch: str) -> str:
        """
        Returns state vectors for a specific epoch 
        """
        epoch = datetime.strptime(epoch, '%Y-%jT%H:%M:%S.%fZ')
        for item in data:
                if item['epoch'] == epoch:
                        return item 
                
        return 'epoch not found\n'

@app.route('/epochs/<epoch>/speed', methods=['GET'])
def instantaneous_speed(epoch: str):
        """
        Returns instantaneous speed for a given epoch 
        """
        try:
                epoch_datetime = datetime.strptime(epoch, '%Y-%jT%H:%M:%S.%fZ')
        except ValueError:
                return "Invalid epoch format"
        
        for item in data:
                if item['epoch'] == epoch_datetime:
                        speed = math.sqrt(item['x_dot']**2 + item['y_dot']**2 + item['z_dot']**2)
                        return str(speed)
        
        return 'epoch not found\n'

@app.route('/now', methods=['GET'])
def nearest_epoch():
        """
        Returns state vectors and instantaneous speed for the epoch that is nearest to now (when the program is ran)
        """
        time_now = datetime.utcnow()
        closest_epoch = min(data, key=lambda x: abs(x['epoch'] - time_now))
        speed = math.sqrt(closest_epoch['x_dot']**2 + closest_epoch['y_dot']**2 + closest_epoch['z_dot']**2)
        return jsonify(closest_epoch, speed)            

@app.route('/comment', methods=['GET'])
def comment():
        comments = []
        for element in big_data:
                comment = element.find('COMMENT').text
                comments.append({'comment': comment})
        return comments

@app.route('/header', methods=['GET'])
def header():
        header_data = []
        for element in big_data:
                header = element.find('header').text
                header_data.append({'header': header})
        return header_data

@app.route('/metadata', methods=['GET'])
def metadata():
        # same thing as others???

@app.route('/epochs/<epoch>/location', methods=['GET'])
def location():
        lat = math.degrees(math.atan2(z, math.sqrt(x**2 + y**2)))
        alt = math.sqrt(x**2 + y**2 + z**2) - 6371.0088
        lng = math.degrees(math.atan2(y, x)) - ((hrs - 12) + (mins - 60))*(260/24) + 19

        # do something with this to find location
        geocoder = Nominatim(user_agent='iss_tracker')
        geoloc = geocoder.reverse((lat, lon), zoom=15, kanguage='en')
        
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')            
            

