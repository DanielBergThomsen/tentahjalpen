# use an official Python runtime as a parent image
FROM python:3.7

# set the working directory
WORKDIR /app

# copy the current directory contents into the container
COPY . /app

# install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# make port 80 available to the world outside this container
EXPOSE 80

# define environment variable
ENV FLASK_APP tentahjalpen
ENV FLASK_ENV production

# run flask app
ENTRYPOINT ["gunicorn"]
CMD ["-b", "0.0.0.0:80", "-w", "1", "--log-file", "-", "--timeout", "300", "wsgi:app"]
