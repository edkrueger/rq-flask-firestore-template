# redis-demo

## General Instructions

### Environmental Variables
Copy `example.env` to `.env`.  
Put your firestore service account JSON and the name of the bucket you want to use into `.env` where indicated.  

## Dev Instructions
Run `pipenv install --dev` to install the env.  
Run `pipenv run pre-commit install` to initialize the git hooks.  
Run `pipenv run pre-commit run --all-files` if there are file that were committed before adding the git hooks.  
Activate the shell with: `pipenv shell`  
Lint with: `pylint app/`  

## Run the App in Dev

### Start Redis for Dev
Get redis docker image: `docker pull redis`  
Start redis: `docker run -d -p 6379:6379 redis`  
Find container id: `docker ps`    
Stop redis: `docker kill <container id>`   

### Redis Queue Management
Start the redis queue worker: `rq worker`  
Empty all redis queues: `rq empty --all`

### Flask App
Start the flask app on dev server: `export FLASK_APP=app.main:app && flask run --reload`  
Start the flask app in production server: `gunicorn app.main:app`  

## Build and Run the App With Docker
Run `docker build . -t rq-firestore` to build the container.  
Run `docker-compose up` to start the app.  
Run `docker-compose up -d` to start the app in detached mode.  
Run `docker-compose down` to stop the app.

## Deployment Instructions
Provision an Ubuntu instance (I've used Ubuntu 20.04 LTS) with suitable security settings.  
SSH into the instance.  
Run `sudo apt update` and `sudo apt install git -y` to install git if your image doesn't already have it.  
Clone this repo and change into it.  
Run `sudo sh setup.sh` to install and configure docker and docker-compose.  
Exit and SSH into the instance again.  
Put the .env file onto the instance in the repo's directory. An easy way to do this is to install nano with `sudo apt install nano -y`, create and open .env with `nano .env` and copy and paste the contents of .env.  
Run the commands in the above "Build and Run the App With Docker" with sudo.  