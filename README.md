# NeuroTK
Neuropathology toolkit, utilizing the Digital Slide Archive.

# Developing
When developing you should create a local Python environment to match the Docker container environment.
1. Create environment using virtualenv or similar tool.
2. Activate the environment.
3. ```$ pip install celery[dash]```
4. Install the rest of packages from requirements.txt in app/

### Encountered Errors
1. When starting the containers with ```$ docker compose up --build -d```, the rabbitmq container fails to start with this type of error: ```Error response from daemon: driver failed programming external connectivity on endpoint rabbitmq (61d1f6d7267997e312e90e10e0ca70b330b544762b26685d5ffe2eed18cd3fc7): Error starting userland proxy: listen tcp4 0.0.0.0:5672: bind: address already in use```
    - What is happening? A rabbitmq server is already running locally on port 5672. Solution: stop the locally running rabbitmq server using ```$ sudo rabbitmqctl stop```