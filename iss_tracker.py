#!/usr/bin/env python3
import requests
import math
from datetime import datetime
import xml.etree.ElementTree as ET
from flask import Flask, request, jsonify
from geopy.geocoders import Nominatim
import time
from astropy import coordinates as coord
from astropy import units as u
from astropy import time
from astropy.time import Time
import xmltodict

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
        Parses xmlfile and stores important elements into a list of dictionaries

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
                x = float(element.find('X').text)
                y = float(element.find('Y').text)
                z = float(element.find('Z').text)
                x_dot = float(element.find('X_DOT').text)
                y_dot = float(element.find('Y_DOT').text)
                z_dot = float(element.find('Z_DOT').text)
                data.append({'epoch': epoch, 'x': x, 'y': y, 'z': z, 'x_dot': x_dot, 'y_dot': y_dot, 'z_dot': z_dot})
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

# combine with epochs 
@app.route('/epochs', methods=['GET'])
def epochs():
        """
        Returns a modified list of epochs given query parameters
        """
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

        if limit is not None:
                return data[:limit]
        if offset != 0:
                return data[offset:]
        if offset != 0 and limit is not None:
                return data[offset:limit]

        else:
                return jsonify(data)
        
# might need debugging 
@app.route('/epochs/<epoch>', methods=['GET'])
def specific_epoch(epoch: str) -> str:
        """
        Returns state vectors for a specific epoch 
        """
        try: 
                epoch = datetime.strptime(epoch, '%Y-%jT%H:%M:%S.%fZ')
        except ValueError:
                return "Invalid epoch format"
        
        for item in data:
                if item['epoch'] == epoch:
                        return jsonify(item) 
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
                        return str('speed:', speed)
        
        return 'epoch not found\n'

# add the location calculation
@app.route('/now', methods=['GET'])
def nearest_epoch():
        """
        Returns the latitude, longitude, altitude, and geoposition for the epoch nearest in time (when the user 'curl's the application)
        """
        time_now = datetime.utcnow()
        closest_epoch = min(data, key=lambda x: abs(x['epoch'] - time_now))
        location_now = calculate_location(closest_epoch, closest_epoch['x'], closest_epoch['y'], closest_epoch['z']) 

# debugggg REAL BAD 
@app.route('/comment', methods=['GET'])
def comment():
        """
        Returns the "comments" list from the ISS data, providing important information about the whole ISS data 
        """
        comments = []
        for element in big_data:
                if 'COMMENT' in element:
                        comment = element['COMMENT']
                        comments.append({'comment': comment})
        return jsonify(comments)

@app.route('/header', methods=['GET'])
def header():
        """
        Returns the header of the ISS data
        """
        headers = []
        for element in big_data:
                if 'header' in element:
                        header = element['header']
                        headers.append({'header': header})
        return jsonify(headers)

@app.route('/metadata', methods=['GET'])
def metadata():
        """
        Returns the metadata dict from the ISS data
        """
        metadata = []
        for element in big_data:
                if 'metadata' in element:
                        metadata = element['metadata']
                        metadata.append({'metadata': metadata})
                return jsonify(metadata)

@app.route('/epochs/<epoch>/location', methods=['GET'])
def location(epoch):
        """
        Returns the latitude, longitude, altitude, and geoposition of a specfic epoch using the calculate_location function  
        """
        try:
                epoch = datetime.strptime(epoch, '%Y-%jT%H:%M:%S.%fZ')
        except ValueError:
                return "Invalid epoch format"

        for item in data:
                if item['epoch'] == epoch:
                        x = item['x']
                        y = item['y']
                        z = item['z']
                        
                        location_info = calculate_location(epoch, x, y, z)
                        return jsonify(location_info)

def calculate_location(epoch, x, y, z):
    """
    Calculate latitude, longitude, altitude, and geoposition for a given epoch and Cartesian coordinates

    Args:
        epoch (str): Epoch in ISO format
        x (float): X-coordinate in kilometers
        y (float): Y-coordinate in kilometers
        z (float): Z-coordinate in kilometers

    Returns:
        dict: Dictionary containing latitude, longitude, altitude, and geoposition
    """
    now = Time(epoch, scale='utc')
    cartrep = coord.CartesianRepresentation(x=x*u.km, y=y*u.km, z=z*u.km)

    gcrs = coord.GCRS(cartrep, obstime=now)
    itrs = gcrs.transform_to(coord.ITRS(obstime=now))
    loc = coord.EarthLocation(*itrs.cartesian.xyz)

    latitude = loc.lat.deg
    longitude = loc.lon.deg
    altitude = loc.height.to(u.km).value
    geoposition = loc.info('geoposition').value

    return {'latitude': latitude, 'longitude': longitude, 'altitude': altitude, 'geoposition': geoposition}
                        
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')            
            

