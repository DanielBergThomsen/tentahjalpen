<h1 align="center">
<a style="text-align:center" href="https://www.tentahjalpen.se/">
  <img src="./frontend/src/art/with-text.svg" alt="Markdownify" width="600">
</a>
</h1>

<h4 align="center">
A website and an API to look at the results of exams taken at 
Chalmers University of Technology.
<br>
<a href="https://travis-ci.com/DanielBergThomsen/tentahjalpen">
<img src="https://travis-ci.com/DanielBergThomsen/tentahjalpen.svg?branch=master">
</a>
</h4>


## Features
* Ability to look at exams in both the absolute numbers of different
grades, as well as the percentages over time
* Comparison between an arbitrary amount of courses in a table
* Adjusted fail-rate to take into account bias incurred with re-exams
and the age of the results
* Examine individual results in a pie chart
* Ability to look at, and submit your own, exam pdfs and solutions
for a given exam date
* Clean, responsive UI with mobile devices taken into account
* Easy to use, public REST API with access to all the data
* Clean seperation between backend and frontend, written in
Python and JavaScript respectively


## How it works
Tentahjälpen uses a JavaScript frontend with a REST API backend
written in Python.

### Frontend
The frontend is made using React, with the various charts coming from
the wrapper for ChartJS known as react-chartjs-2. Many other packages
are being utilized which are easily seen in the package.json file.

### Backend
The backend is written using pure Flask, and can be accessed at
https://api.tentahjalpen.se/courses. The responses given from
the API are all JSON, even the errors. Since there is no token
authorization being utilized for the backend at the moment,
the API is public and free to use. The backend is managed using
the `backend/db_manager.py` file, which hosts functions to scrape
the necessary data and accept/deny submitted exam pdfs. When
starting the backend it will check that a database has been
initialized and initialize it if necessary. The backend has a 
function to scrape exams and solutions over at 
https://chalmerstenta.se, which are accessible using the 
`backend/db_manager.py` and must be run manually.


## Setting up a local development environment
1. Clone the repository
```
git clone https://github.com/DanielBergThomsen/tentahjalpen
```
2. Install dependencies for the frontend
```
cd frontend
npm install
```
3. Create a virtual environment for the backend
```
cd ../backend
virtualenv venv
```
4. Activate virtual environment and install dependencies for the backend
```
. /venv/bin/activate
pip install -r requirements.txt
```
5. Create a postgres database called courseData
```
createdb courseData
```
6. Navigate back to project root and run the backend
```
cd ..
make dev-back
```
7. Open new terminal session and run the frontend
```
make dev-front
```


## Deployment using Dokku
1. Install Dokku and it's dependencies
2. Set up a Dokku server (I'm using DigitalOcean)
3. Configure two applications on the Dokku server
4. Add two remotes to your local git repository with the names `dokku-backend`
and `dokku-frontend` respectively
5. Create a postgres database using the [dokku plugin](https://github.com/dokku/dokku-postgres)
6. Generate TLS certificates using the Letsencrypt [dokku plugin](https://github.com/dokku/dokku-letsencrypt)
7. Run `make dokku-backend` and `make dokku-backend` respectively to deploy both
the backend and frontend
