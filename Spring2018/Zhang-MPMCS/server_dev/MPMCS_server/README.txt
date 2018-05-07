This is the implementation of MPMCS server. The server works with mpmcs client, which is the Android client app that communicates and executes sensor sampling tasks.

Before running the server, one needs to set up a mongodb and a database for storing Users collection, location collection, and Tasks collection (Battery collection is optional depending on if the battery parameter is needed in the scheduling function). We also prvide the trace file that we used to in our evaluation as MPMCS_Dataset.npy.gz whose npy file stores a 2D array where the columns are user id, latitude, longitude, and timestamp in milliseconds respectively. After the database is setup, one needs to fill in the mongo db details in Utils.py, mpmcs_reply_server.py, and task_generator.py.

To generate MCS tasks, one can run the task_generator.py to dump tasks into the database. 

One can run the server by "python3 mpmcs_task_scheduler.py" and "python3 mpmps_reply_server.py". The reply server accepts the results back from the mpmcs client and store task results into database. 

To run the servers in the back ground, simply type "./start_servers.sh" which will create tmux sesssion to hold the servers. In order to kill the server, one can use "./stop_servers.sh".
