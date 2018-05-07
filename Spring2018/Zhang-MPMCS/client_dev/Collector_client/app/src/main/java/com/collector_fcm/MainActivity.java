package com.collector_fcm;

import android.Manifest;
import android.app.Activity;
import android.app.AlarmManager;
import android.app.AlertDialog;
import android.app.AppOpsManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Calendar;
import java.util.GregorianCalendar;
import java.util.HashMap;
import java.util.Map;

import android.os.Build;
import android.provider.Settings;
import android.support.v4.app.ActivityCompat;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import com.google.firebase.iid.FirebaseInstanceId;
import com.google.firebase.messaging.FirebaseMessaging;

public class MainActivity extends Activity {
    private static MainActivity ins;
    public static String userName = "";
    public static String userEmail = "";
    public static Boolean debug = false;
    public static String TAG = "MainActivity";
    public static AlarmManager UploadAlarm;
    public static int uploadAlarmID = 10000;
    private BroadcastReceiver locationReceiver;
    private BroadcastReceiver uploadReceiver;
    private Button btn_start;
    private EditText nameEdit;
    private EditText emailEdit;
    private String longitude = "null";
    private String latitude = "null";
    private Intent UploadIntent;
    public static long UploadFreq = 2 * 60000L;
    @Override
    protected void onResume() {
        super.onResume();

        if(locationReceiver == null){
            locationReceiver = new BroadcastReceiver() {
                @Override
                public void onReceive(Context context, Intent intent) {
                    String coordinates = (String) intent.getExtras().get("coordinates");

//                            append("\n" + coordinates);
//                    UploadIntent.putExtra("location", "fjdosjf");
                    if (debug)
                        Log.e(TAG, "Coordinates changed");
                    try {
                        assert coordinates != null;
                        longitude = coordinates.split("")[0];
                        latitude = coordinates.split("")[1];
                    } catch (NullPointerException e)
                    {
                        if (debug)
                            Log.e(TAG, e.toString());
                    }

                }
            };
        }
        registerReceiver(locationReceiver, new IntentFilter("location_Update"));
        registerReceiver(uploadReceiver, new IntentFilter("upload_request"));
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if(locationReceiver != null){
            unregisterReceiver(locationReceiver);
        }
        if (uploadReceiver != null) {
            unregisterReceiver(uploadReceiver);
        }
    }


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        ins = this;
        setContentView(R.layout.activity_main);

        btn_start = (Button) findViewById(R.id.start);
//        btn_stop = (Button) findViewById(R.id.stop);
        nameEdit = (EditText) findViewById(R.id.name);
        emailEdit = (EditText) findViewById(R.id.email);

        FirebaseMessaging.getInstance().subscribeToTopic("collector_request");
        Log.d(TAG, "token: " + FirebaseInstanceId.getInstance().getToken());
        startApp();

    }

    private void startApp() {
        runtime_permissions();
        Intent i = new Intent(getApplicationContext(), DummyService.class);
        startService(i);

        enable_buttons();
        updateUserInfo();
        String[] PERMISSIONS = {Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION, Manifest.permission.READ_PHONE_STATE, Manifest.permission.INTERNET,  Manifest.permission.RECEIVE_BOOT_COMPLETED};
        while (!hasPermissions(this, PERMISSIONS)){
            try {
                Log.d(TAG, "need your permission");
                Thread.sleep(50);
            }catch (Exception e){
                e.printStackTrace();
            }

        }

        Intent j = new Intent(getApplicationContext(), GPS_Service.class);
        startService(j);

        UploadAlarm = (AlarmManager) getSystemService(Context.ALARM_SERVICE);
        Calendar calendar= new GregorianCalendar();
        UploadIntent = new Intent(getApplicationContext(), UploadReceiver.class);
        UploadIntent.setAction("upload_request");
        UploadIntent.putExtra("category", "repeat");
        PendingIntent scheduleUploadntent;
        scheduleUploadntent = PendingIntent.getBroadcast(getBaseContext(), uploadAlarmID, UploadIntent, PendingIntent.FLAG_UPDATE_CURRENT);

        //every 1 mins
        UploadAlarm.setRepeating(AlarmManager.ELAPSED_REALTIME_WAKEUP, 0, UploadFreq, scheduleUploadntent);
    }

    private void updateUserInfo() {
        BufferedReader input = null;
        File file = null;
        try {
            file = new File(this.getFilesDir(), "userInfo");
            if (debug)
                Log.d(TAG, "trying to get user info from " + file.getAbsolutePath());

            if (file.exists()) {
                input = new BufferedReader(new InputStreamReader(new FileInputStream(file)));
                String line;
                StringBuffer buffer = new StringBuffer();
                while ((line = input.readLine()) != null) {
                    buffer.append(line);
                    if (line.split(":")[0].equals("Name")) {
                        nameEdit.setText(line.split(":")[1]);
                        if (debug)
                            Log.d(TAG, "update nameEdit");
                    }

                    else if (line.split(":")[0].equals("Email")){
                        emailEdit.setText(line.split(":")[1]);
                        if (debug)
                            Log.d(TAG, "update emailEdit");
                    }

                }
                if (debug)
                    Log.d(TAG, buffer.toString());
            }

        } catch (IOException e) {
            e.printStackTrace();
        }

    }

    private void enable_buttons() {

        btn_start.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View view) {

                userEmail = emailEdit.getText().toString();
                userName = nameEdit.getText().toString();
                SaveToFile();
                Toast.makeText(getInstace(), "App started", Toast.LENGTH_LONG).show();
//                userEmail = emailEdit.getText().toString();

            }

            private void SaveToFile() {
                String fileName = "userInfo";
                String content = "Name:" + userName + "\n" + "Email:" + userEmail ;
                FileOutputStream outputStream = null;
                try{
                    outputStream = openFileOutput(fileName, Context.MODE_PRIVATE);
                    outputStream.write(content.getBytes());
                    if (debug)
                        Log.d(TAG, "written to " + MainActivity.this.getFilesDir().getAbsolutePath());
                    outputStream.close();
                } catch (Exception e) {
                    e.printStackTrace();
                }

            }
        });

    }

    private void runtime_permissions() {

        int PERMISSION_ALL = 1;
        String[] PERMISSIONS = {Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION, Manifest.permission.READ_PHONE_STATE, Manifest.permission.INTERNET,  Manifest.permission.RECEIVE_BOOT_COMPLETED};
        if (!hasPermissions(this, PERMISSIONS))
            ActivityCompat.requestPermissions(this, PERMISSIONS, PERMISSION_ALL);
    }
    private boolean hasPermissions(Context context, String[] permissions) {
        if (android.os.Build.VERSION.SDK_INT >= Build.VERSION_CODES.M && context != null && permissions != null) {
            for (String permission : permissions) {
                if (ActivityCompat.checkSelfPermission(context, permission) != PackageManager.PERMISSION_GRANTED) {
                    return false;
                }
            }
        }
        return true;
    }

    @Override
    public void onRequestPermissionsResult(int requestCode,  String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        switch (requestCode){
            case 1:{
                Map<String, Integer> perms = new HashMap<>();
                perms.put(Manifest.permission.ACCESS_FINE_LOCATION, PackageManager.PERMISSION_GRANTED);
                perms.put(Manifest.permission.ACCESS_COARSE_LOCATION, PackageManager.PERMISSION_GRANTED);
                perms.put(Manifest.permission.READ_PHONE_STATE, PackageManager.PERMISSION_GRANTED);
                perms.put(Manifest.permission.INTERNET, PackageManager.PERMISSION_GRANTED);
                perms.put(Manifest.permission.RECEIVE_BOOT_COMPLETED, PackageManager.PERMISSION_GRANTED);

                if (grantResults.length > 0){
                    for (int i = 0; i < permissions.length; i++ )
                        perms.put(permissions[i], grantResults[i]);
                    if (perms.get(Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
                            && perms.get(Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED
                            && perms.get(Manifest.permission.READ_PHONE_STATE) == PackageManager.PERMISSION_GRANTED
                            && perms.get(Manifest.permission.INTERNET) == PackageManager.PERMISSION_GRANTED
                            && perms.get(Manifest.permission.RECEIVE_BOOT_COMPLETED) == PackageManager.PERMISSION_GRANTED){
                        Toast.makeText(this, "All permissions granted, working", Toast.LENGTH_LONG).show();
                    }
                    else{
                        if (ActivityCompat.shouldShowRequestPermissionRationale(this, Manifest.permission.ACCESS_FINE_LOCATION)
                                || ActivityCompat.shouldShowRequestPermissionRationale(this, Manifest.permission.ACCESS_COARSE_LOCATION)
                                || ActivityCompat.shouldShowRequestPermissionRationale(this, Manifest.permission.READ_PHONE_STATE)
                                || ActivityCompat.shouldShowRequestPermissionRationale(this, Manifest.permission.INTERNET)
                                || ActivityCompat.shouldShowRequestPermissionRationale(this, Manifest.permission.RECEIVE_BOOT_COMPLETED))
                        {
                            showDialogOK("SMS and Location Services Permission required for this app",
                                    new DialogInterface.OnClickListener() {
                                        @Override
                                        public void onClick(DialogInterface dialog, int which) {
                                            switch (which) {
                                                case DialogInterface.BUTTON_POSITIVE:
                                                    runtime_permissions();
                                                    break;
                                                case DialogInterface.BUTTON_NEGATIVE:
                                                    // proceed with logic by disabling the related features or quit the app.
                                                    break;
                                            }
                                        }
                                    });
                        }

                    }
                }

            }

        }

    }
    private void showDialogOK(String message, DialogInterface.OnClickListener okListener) {
        new AlertDialog.Builder(this)
                .setMessage(message)
                .setPositiveButton("OK", okListener)
                .setNegativeButton("Cancel", okListener)
                .create()
                .show();
    }
    public static MainActivity  getInstace(){
        return ins;
    }
    public static String getUserName(){ return userName;}
    public static String getUserEmail(){return userEmail;}

}


