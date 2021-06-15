package com.collector_fcm;

import android.annotation.SuppressLint;
import android.app.usage.UsageEvents;
import android.app.usage.UsageStats;
import android.app.usage.UsageStatsManager;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.AsyncTask;
import android.os.BatteryManager;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.telephony.TelephonyManager;
import android.util.Log;


import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.Socket;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Executor;

/**
 * Created by Henry on 10/9/17.
 */

public class UploadReceiver extends BroadcastReceiver {


    private long samplingWindow = 1 * 60000L;
    public boolean debug = true;


    private TelephonyManager Tmgr;
    private String userEmail = "";
    private String userName = "";


    private String History = "history";
    private BroadcastReceiver locationReceiver;

    final String TAG = "UploadReceiver";

    @Override
    public void onReceive(Context context, Intent intent) {
        Log.d(TAG, "received upload_request");
        String category = intent.getStringExtra("category");
        Log.d(TAG, "category is " + category);

        if (userName.equals("") || userEmail.equals("")) {
            if (!readFromFile(context)) {
                if (debug)
                    Log.d(TAG, "fetch user info from file faild, switch to use editview");
                userName = MainActivity.getUserName();
                userEmail = MainActivity.getUserEmail();
            }
        }

        if (debug) {
            Log.d(TAG, userEmail);
            Log.d(TAG, userName);
        }


        DateFormat format = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        @SuppressWarnings("WrongConstant")
        UsageStatsManager usageStatsManager = (UsageStatsManager) context.getSystemService("usagestats");

        String locationString = "";
        locationString = CoordinatesToJsonString(context);

        String LastTimeUsages = getlastTimeUsagesToJsonString(usageStatsManager);
        Tmgr = (TelephonyManager) context.getSystemService(context.TELEPHONY_SERVICE);
        String UID = UidToJsonString(Tmgr);
        String timeStamp = "";
        String Version = "";
        String Name = "";
        String Email = "";
        try {
            timeStamp = new JSONObject().put("timeStamp", format.format(getTimeNow())).toString();
            Version = new JSONObject().put("version", "2").toString();
            Name = new JSONObject().put("name", userName).toString();

            Email = new JSONObject().put("email", userEmail).toString();
        } catch (Exception e) {

        }
        String batteryLevel = getBattery(context);
        if (debug)
            Log.d(TAG, "Battery Level" + batteryLevel);
        // need to support history; use '--' to split different history.
        String finalResult = timeStamp + ";" + UID + ";" + LastTimeUsages + ";" + locationString + "; " + Name + "; " + Email + ";" + batteryLevel + ";" + Version;

        LogHistory(context, finalResult);

    }

    private void showHistory(Context context){
        BufferedReader input = null;
        File file = null;
        try {
            file = new File(context.getFilesDir(), History);
            if (file.exists()) {
                input = new BufferedReader(new InputStreamReader(new FileInputStream(file)));
                String line;
                while ((line = input.readLine()) != null) {
                    Log.d(TAG, "read from history usage file: " + line);
                }

            } else {
                if (debug)
                    Log.d(TAG, "no history usage file found");
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }


    private boolean readFromFile(Context context) {
        BufferedReader input = null;
        File file = null;
        try {
            file = new File(context.getFilesDir(), "userInfo");
            if (file.exists()) {
                input = new BufferedReader(new InputStreamReader(new FileInputStream(file)));
                String line;
                StringBuffer buffer = new StringBuffer();
                while ((line = input.readLine()) != null) {
                    buffer.append(line);
                    if (line.split(":")[0].equals("Name")) {
                        userName = line.split(":")[1];
                        if (debug)
                            Log.d(TAG, "read user name: " + userName + "from file " + file.getAbsolutePath());
                    } else if (line.split(":")[0].equals("Email")) {
                        userEmail = line.split(":")[1];
                        if (debug)
                            Log.d(TAG, "read user email: " + userEmail + " from file " + file.getAbsolutePath());
                    } else
                        return false;
                }

                if (debug)
                    Log.d(TAG, buffer.toString());
            } else return false;

        } catch (IOException e) {
            e.printStackTrace();
        }
        return true;
    }

    @SuppressLint("MissingPermission")
    private String UidToJsonString(TelephonyManager tmgr) {
        try {
            JSONObject imei = new JSONObject();
            imei.put("UID", tmgr.getDeviceId());
            return imei.toString();
        } catch (Exception e) {
            if (debug)
                Log.d(TAG, e.toString());
        }

        return "null";
    }

    private String getlastTimeUsagesToJsonString(UsageStatsManager usageStatsManager) {
        SimpleDateFormat format = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        Map<String, UsageStats> usageStats = usageStatsManager.queryAndAggregateUsageStats(getTimeNow() - samplingWindow, getTimeNow());
        List<UsageStats> stats = new ArrayList<>();
        stats.addAll(usageStats.values());
        String LastTimeUsages = "";
        JSONArray usageArr = new JSONArray();
        try {
            for (UsageStats stat : stats) {
                if (getTimeNow() - stat.getLastTimeStamp() < samplingWindow && stat.getLastTimeUsed() > 10000000000L) {
                    if (debug) {
                        Log.d(TAG, stat.getPackageName() + " " + format.format(stat.getLastTimeUsed()));
                        Log.d(TAG, String.valueOf(stat.getLastTimeUsed()));
                    }

                    JSONObject statJson = new JSONObject();
                    statJson.put(format.format(stat.getLastTimeUsed()), stat.getPackageName());
                    usageArr.put(statJson);
                }

            }
            LastTimeUsages = new JSONObject().put("usages", usageArr).toString();
        } catch (Exception e) {
            if (debug)
                Log.e(TAG, e.toString());
        }

        return LastTimeUsages;
    }


    private Location getLastKnownLocation(LocationManager mLocationManager) {

        List<String> providers = mLocationManager.getProviders(true);
        Location bestLocation = null;
        for (String provider : providers) {
            @SuppressWarnings("MissingPermission") Location l = mLocationManager.getLastKnownLocation(provider);
            if (l == null) {
                continue;
            }
            if (bestLocation == null || l.getAccuracy() < bestLocation.getAccuracy()) {
                // Found best last known location: %s", l);
                bestLocation = l;
            }
        }
        return bestLocation;
    }

    @SuppressLint("MissingPermission")
    private String CoordinatesToJsonString(Context context) {
        JSONObject LongitudeJson = new JSONObject();
        JSONObject LatitudeJson = new JSONObject();
        try {

            double latitude = 0.0;
            double longitude = 0.0;
            LocationManager locationManager = (LocationManager) context.getApplicationContext().getSystemService(Context.LOCATION_SERVICE);
            Location myLocation = getLastKnownLocation(locationManager);
            if (myLocation != null) {
                latitude = myLocation.getLatitude();
                longitude = myLocation.getLongitude();
                Log.d(TAG, "location from location manager, latitude: " + Double.toString(latitude) + " longitude: " + Double.toString(latitude));
            }

            LongitudeJson.put("Longitude", longitude);
            LatitudeJson.put("Lattitude", latitude);
        }
        catch (Exception e){
            if (debug)
                Log.e(TAG, e.toString());
        }

        return LongitudeJson.toString() + ";" + LatitudeJson.toString();
    }
    private void LogHistory(Context context, String data) {
        String fileName = History;
        FileOutputStream outputStream = null;

        try{

            outputStream = context.openFileOutput(fileName, Context.MODE_APPEND);
            File file = new File(context.getFilesDir(), fileName);
            if (file.length() > 0) {
                data = "--" + data;
                if (debug) {
                    Log.d(TAG, "History is not empty");
                    Log.d(TAG, "tuning data " + data);
                }

            }
            else{
                if (debug){
                    Log.d(TAG, "empty history" + context.getFilesDir()  + "/" + fileName);
                    Log.d(TAG, data);
                }
            }
            outputStream.write(data.getBytes("UTF-8"));
            outputStream.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }


    private long getTimeNow() {
        return  System.currentTimeMillis();
    }

    public String getBattery(Context context) {
        String res = new String();
        Intent batteryIntent = context.registerReceiver(null,
                new IntentFilter(Intent.ACTION_BATTERY_CHANGED));
        int level = batteryIntent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1);
        int scale = batteryIntent.getIntExtra(BatteryManager.EXTRA_SCALE, -1);

        // Error checking that probably isn't needed but I added just in case.
        if (level == -1 || scale == -1) {
            res += 50.0f;
        } else
            res += ((float) level / (float) scale) * 100.0f;

        int status = batteryIntent.getIntExtra(BatteryManager.EXTRA_STATUS, -1);

        boolean isCharging = status == BatteryManager.BATTERY_STATUS_CHARGING ||
                status == BatteryManager.BATTERY_STATUS_FULL;
        JSONObject batteryInfoJson = new JSONObject();
        try {
            if (isCharging) {
                batteryInfoJson.put("status", "Charging");
            } else {
                batteryInfoJson.put("status", "NOT_CHARGING");
            }
            batteryInfoJson.put("level", res);
        } catch (Exception e){
            e.printStackTrace();
        }

        return batteryInfoJson.toString();
    }
}
