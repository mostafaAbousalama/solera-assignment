# Solera Assignment

## Discription
This a small project that utilises a Flask web app and Postgres database to simply allow a sign-in and sign-up pages for different users and admins home panels to display relevant information. It uses Docker containers to launch these app in development environment as well as Gunicorn and Nginx for load balancing of multiple web app instances in a production environment.

## Requirements
- [Docker Desktop](https://docs.docker.com/get-docker/) needs to be installed.
- Any Bash terminal

## Development Environment Setup
- Clone this repo
- `cd` into its root directory
- `$ docker-compose -f docker-compose.yml up -d --build`
- Check to see that the project container is indeed up and running in Docker Desktop
- Configure the database and seed it with sample data by the following two commands
- `$ docker-compose -f docker-compose.yml exec web python configdb.py`[^1]
- `$ docker-compose -f docker-compose.yml exec web python seeddb.py`[^1]
- You can now check through the terminal that indeed the database schema and sample data has been committed by the following command in the terminal
- `$ docker-compose -f docker-compose.yml exec db psql --username=solera_admin --dbname=solera_db`[^1]
- You can now navigate to [localhost:5000](http://localhost:5000) on any browser to view and interact with the web app
- To build down the project container and remove it along with the volume, use this command
- `$ docker-compose -f docker-compose.yml down -v`

## Production Environment Setup
Similarly as with the development setup, after you cd into the project root you will run mostly the same command with a small change in the yml file used and `dbname`
- `$ docker-compose -f docker-compose.prod.yml up -d --build`
- Check to see that the project container is indeed up and running in Docker Desktop
- Configure the database and seed it with sample data by the following two commands
- `$ docker-compose -f docker-compose.prod.yml exec web python configdb.py`[^1]
- `$ docker-compose -f docker-compose.prod.yml exec web python seeddb.py`[^1]
- You can now check through the terminal that indeed the database schema and sample data has been committed by the following command in the terminal
- `$ docker-compose -f docker-compose.prod.yml exec db psql --username=solera_admin --dbname=solera_db_prod`[^1]
- You can now navigate to [localhost:1337](http://localhost:1337) on any browser to view and interact with the web app
- To build down the project container and remove it along with the volume, use this command
- `$ docker-compose -f docker-compose.prod.yml down -v`

[^1]: If you are using Git Bash on windows, it will throw an error with this command, requesting that you prepend the command `winpty` at the beginning like so `$ winpty docker-compose -f docker-compose.yml exec web python configdb.py`
