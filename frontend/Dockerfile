# use an official Python runtime as a parent image
FROM node:11.14.0

# set the working directory
WORKDIR /app

# copy the current directory contents into the container
COPY . /app

# install dependencies
RUN npm install

# make production build
RUN npm run build

# make port 80 available to the world outside this container
EXPOSE 80

# run flask app
ENTRYPOINT ["npm"]
CMD ["run", "start-prod"]
