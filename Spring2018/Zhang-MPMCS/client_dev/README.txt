The Collector_client is the Android app in correspondence with collector server while the MPMCS_client is the Andorid app in correspondence with the mpmcs task scheduling server. The collector periodically collects app user's location. The MPMCS client receives tasks from MPMCS server and returns sensor values after sensor sampling.

To add the project, one needs to have Android Studio and open each project in the Android Studio. Since both clients use Google fire base messaging service. One needs to create his own token for the service and add the key to the project. The collector app has a collection frequency variable that can be customized. It is UploadFreq in the MainActivity.java. 

The details of adding, compiling, and executing the clients can be found in Google developer website.
