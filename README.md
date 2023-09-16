# Server based on Django REST API Framework and Websockets

This code was made for receiving data from device based on ESP32. ESP32 sends 
[IMU](https://en.wikipedia.org/wiki/Inertial_measurement_unit) data
(consisting of three-axis accelerometer and three-axis gyroscope) retrieved at 500 Hz.
Server uses Websockets for Handshaking and receiving data that are saved in text files. 
Client source code can be found 
[here](https://github.com/kins3i/ESP32-websocket_client_with_ICM20948).

### Settings
For proper usage of project necessary is: downloading relevant libraries for 
Python interpreter and set run configuration.
1. Libraries
    * Django
    * channels
    * channels-redis
    * daphne
    * djangochannelsrestframework
    * djangorestframework
    * matplotlib
    * numpy
    * redis
    * requests
    * scipy
    * webserver
2. Run configuration
   * Django server
     * Python 3.9
     * Host 0.0.0.0
     * Port 8000
     * Custom run command: runserver
   * Settings:
     * Preferably in Settings > Build, Execution, Deployment > Build Tools >
     Reload project after changes in the build scripts

### Pages
Contents of server are available at localhost:8000/<name of page> or 
127.0.0.1:8000/<name of page>. Main page is intended for admin page.
List of working pages:
- /post/ - all model instances in REST API format
- /start/ - start and stop client
- /get_file/ - choose file for calculating results
- /results/ - page for presenting graph and additional results made on IMU data
- /del_items/ - deletes all model instances and sets ID to 0
- /del_file/ - deletes chosen file
- /clear_session/ - clear filename and calculated values