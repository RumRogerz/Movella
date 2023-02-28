# Container Build
In `/build`, simply execute `docker build -t movella-nginx:alpine-slim .`

This is a very simple build so not much needs to happen.  I have chosen `alpine-slim` as it is *extremely* lightweight and the `.html` files supplied were simple. (Not that this is a bad thing)

Notice that entrypoints were not supplied for this container as the entrypoints supplied from the nginx source is sufficient enough to get the webserver up and running.

