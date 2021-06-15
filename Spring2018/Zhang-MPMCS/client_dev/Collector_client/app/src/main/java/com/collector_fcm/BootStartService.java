package com.collector_fcm;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.os.IBinder;
import android.support.annotation.Nullable;
import android.util.Log;

import java.util.Calendar;
import java.util.GregorianCalendar;

import static com.collector_fcm.MainActivity.UploadAlarm;
import static com.collector_fcm.MainActivity.UploadFreq;
import static com.collector_fcm.MainActivity.uploadAlarmID;

/**
 * Created by Henry on 10/24/17.
 */

public class BootStartService extends Service {
    final String TAG ="BootStartService";
    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
    @Override
    public void onCreate() {
        Log.d(TAG, "service created");
        startUpload();

    }
    private void startUpload() {
        UploadAlarm = (AlarmManager) getSystemService(Context.ALARM_SERVICE);
        Calendar calendar= new GregorianCalendar();
        Intent UploadIntent = new Intent(getApplicationContext(), UploadReceiver.class);
        UploadIntent.setAction("upload_request");
        UploadIntent.putExtra("category", "repeat");
        PendingIntent scheduleUploadntent;
        scheduleUploadntent = PendingIntent.getBroadcast(getBaseContext(), uploadAlarmID, UploadIntent, PendingIntent.FLAG_UPDATE_CURRENT);

        //every 1 mins
        UploadAlarm.setRepeating(AlarmManager.ELAPSED_REALTIME_WAKEUP, 0, UploadFreq, scheduleUploadntent);
    }
}
