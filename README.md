# ISS Trajectory Data Flask Web Application 

## Purpose
This repository contains a full flask application with instructions on how to build, run, and test this on the International Space Station's (ISS) trajectory. This data is useful and important to gather accurate information about space and ensure the ISS is safe and not colliding with other objects in space. Overall, this project is used to gain familiarity with flask web applications and routes, while also analyzing important ISS data.

## Summary of Contents
* `iss_tracker.py`: Flask web application
* `test_iss_tracker.py`: Unit tests for iss_tracker.py
* `requirements.txt`: List of required dependencies for the app 
* `Dockerfile`: Contains instructions to build our docker image
* `docker-compose.yml`: Configuration file that allows for a simplified `docker run` command 
* diagram.png : An overview of the components of this project

## Data
The ISS trajectory data is available to the public and can be downloaded from NASA's website; https://spotthestation.nasa.gov/trajectory_data.cfm . This data includes state vectors (inlcuding positions and velocities) over a 15-day period that is updated regularly. For a better understanding of what the data yields, I recommend reading the paragraphs provided (on the website) and taking a look at the data itself. The data is offered in .txt or .xml format. For this project, I used XML format to ingest and parse the data. 

## Instructions
### Building the Container
To build a Docker image, run this command:
```python
docker build -t <username>/flask-iss-tracker:1.0 . 
```
**DO NOT FORGET THE DOT . AT THE END & MAKE SURE YOU'RE IN THE DIRECTORY THAT CONTAINS ALL YOUR FILES**
Ensure your image has been built by executing this command:
```python
docker images
```
You should see something like this:
```python
REPOSITORY                      TAG       IMAGE ID       CREATED          SIZE
nicoleolv/flask-iss-tracker     1.0       1b9b1b7a010d   38 seconds ago   1.01GB
```
### Deploying as a Flask App
To run the containerized code as a Flask app, use this command:
```python
docker-compose up 
```
Instead of running a long `docker run` command, we use the `docker-compose.yml` file that, in summary, simplifies and saves time runnning your Flask application. 
### Running Unit Tests
To run unit tests inside the container, execute this command:
```python
docker run <username>/flask-iss-tracker:1.0 /usr/local/bin/pytest -vv /app/test_iss_tracker.py
```
### Accessing the Routes 
To interact with the Flask API, use `curl` commmands as shown below:
* To fetch the comments:
  ```python
  curl http://129.114.37.110:5000/comment
  ```
* To fetch the header:
  ```python
  curl http://129.114.37.110:5000/header
  ```
* To fetch the metadata:
  ```python
  curl http://129.114.37.110:5000/metadata
  ```
* To fetch all epochs:
  ```python
  curl http://129.114.37.110:5000/epochs
  ```
* To fetch a specific epoch:
  ```python
  curl http://129.114.37.110:5000/epochs/2024-068T11:20:00.000Z
  ```
* To fetch a specific range of epochs (given query parameters):
  ```python
  curl http://129.114.37.110:5000/epochs?limit=3&offset=1
  ```
* To fetch the instantaneous speed of a specific epoch:
  ```python
  curl http://129.114.37.110:5000/epochs/2024-068T11:20:00.000Z/speed
  ```
* To fetch the location of a specific epoch:
  ```python
  curl http://129.114.37.110:5000/epochs/2024-068T11:20:00.000Z/location
  ```
* To fetch the instantaneous speed and location of the epoch nearest in time:
  ```python
  curl http://129.114.37.110:5000/now
  ```
## Interpreting the Output 
* `/comment` route returns the list of comments provided by the ISS data, including information about units, mass, drag coefficient, and much more.
* `/header` route returns the header of the ISS data including creation date and originator.
* `/metadata` route returns the dictionary in the ISS data that provides the object name, id, start time, end time, and a few other insights.
* `/epochs` route returns a dictionary of all the epoch's statevectors, including position (x, y, z) and velocities (x_dot, y_dot, z_dot)
* `/epochs/<2024-068T11:20:00.000Z>` route returns the statevectors, including position (x, y, z) and velocities (x_dot, y_dot, z_dot) of a specific epoch 
* `/epochs?limit=<3>&offset=<1>` route returns a dictionary of a specific number of epochs (specified by limit) starting at a certain epoch (specified by offset).
* `/epochs/<2024-068T11:20:00.000Z>/speed` route returns the instantaneous speed, in km/s, of the specified epoch
* `/epochs/<2024-068T11:20:00.000Z>/location` route returns the longitude, latitude, and altitude of the specified epoch
* `/now` route returns the instantaneous speed, latitude, longitude, and altitude of the epoch nearest in time from when the command is "curled" 

### Examples

## Overview 
Overall, this Flask Web Application returns summary statistics on ISS trajectory data. The interactive `iss_tracker.py` script provide a series of statistics that help the user gain clarity on the ISS trajectory data. The whole data may be returned, a modified list of the data, instantaneous speed of a specific epoch, only a specific dictionary in the data, state vectors and location of an epoch, and much more. All is based on user interactive user input. Please note that 'diagram.png' provides a visual overview of this project.  
### Software Diagram 
![diagram](https://github.com/nicoleolv/flask-app/assets/142863540/b84928d3-08be-4f80-ac92-1e46cf98ef58)
