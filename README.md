# Container Build
In `/build`, simply execute `docker build -t movella-nginx:alpine-slim .`

This is a very simple build so not much needs to happen.  I have chosen `alpine-slim` as it is *extremely* lightweight and the `.html` files supplied were simple. (Not that this is a bad thing)

Notice that entrypoints were not supplied for this container as the entrypoints supplied from the original nginx container source is sufficient enough to get the webserver up and running.

# Kubernetes
I am using Docker Desktop and the built-in Kubernetes engine (`1.25.2`) for the purposes of this demonstration.

### Deployment
Include liveliness probes to ensure the tcp socket is operational and a readyness probe to ensure the `index.html` in reachable and returns a `200` return code.

### Service
Quick and clean.  This will target the Deployment, targeting the `containerPort` that we defined in the `Deployment` as `nginx` and assign this Service a port of `8080` so we can access it.
Since we are running Kubernetes locally, we are using `serviceType: NodePort` to poke holes in our local kubernetes deployment.  This will allow us to access the service in our browser using `localhost`

### Kustomize
Apply the whole configuration with kustomize to keep things easy:
`kubectl apply -k .`
Keep in mind this will *also* create a namespace `nginx`

### Test
Go to: http://localhost:30000

![Terminal](./images/get_all.png)

![Screeenshot](./images/index.png)