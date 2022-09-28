# Solera Assignment

## Discription
This a small project that utilises a Flask web app and Postgres database to simply allow a sign-in and sign-up pages for different users and admins home panels to display relevant information. It uses Docker containers to launch these app in development environment as well as Gunicorn and Nginx for load balancing of multiple web app instances in a production environment.

## Requirements
- [Docker Desktop](https://docs.docker.com/get-docker/) needs to be installed.
- Any Bash terminal

## Api Reference
### Base URL
- For development environment: [localhost:5000](http://localhost:5000)
- For production environment: [localhost:1337](http://localhost:1337)

### Authentication
The current version of the application does not require either authentication or API keys

### Error Handling
Errors are returned as JSON objects. The object below is an example of an error returned if the user tries to sign in with user credentials that does not exist:
```
{
     "success": False,
     "error": 404,
     "message": "Not found"
}
```
The API will return these error types:
- 400: Bad request
- 401: Unauthorized
- 404: Not found
- 405: Method not allowed
- 409: User already exist
- 422: Unprocessable
- 500: Internal server error

### Resource Endpoints Library

#### GET /
- Force redirect from root to the user login page

#### GET /user/login
- Load login form for users

#### GET /admin/login
- Load login form for admins

#### GET /user/register
- Load sign-up form for users

#### GET /admin/register
- Load sign-up form for admins

## Development Environment Setup
This environment only uses Flask and Postgres, containerizes them, then build the project through a docker-compose file

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
The production environment builds on top of the development environment and uses Gunicorn as WSGI in front of Flask, as well as Nginx as a load balancer configuration[^2] in front of the entire project, again by containerizing and building through a multi-stage builder to reduce the final image size and using docker-compose finally.

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
[^2]: There is a limitation to using the free tier of nginx when configuring it as load balancer, as it can not persist sessions without using sticky cookies, which are limited only to nginx plus, a paid service. The only workaround this is by using either the `ip_hash` or `hash $special_key` to persist the session and maintain the connection to the same web app instance. The downside to using this is that it limits your connection to one web instance and the load balance will never direct you request to the other instance unless the first is down or in maintenance, meaning we can not simulate or test this particular load balance configuration unless we host the entire project on the cloud and start using it through different IPs or devices on different network  

