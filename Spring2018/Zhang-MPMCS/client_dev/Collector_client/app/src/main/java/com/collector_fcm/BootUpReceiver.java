package com.collector_fcm;

/**
 * Created by Henry on 10/4/17.
 */
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.util.Log;
import android.widget.Toast;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;


/**
 * Created by Henry on 4/17/17.
 */

public class BootUpReceiver extends BroadcastReceiver
{

    public boolean debug = false;

    final String  TAG = "BootUpReceiver";

    @Override
    public void onReceive(Context context, Intent intent) {
        /****** For Start Activity *****/

        if (!checkFile(context)){

            if (debug)
                Log.d(TAG, "user info does not exist, restart the activity");
            Intent i = new Intent(context, MainActivity.class);
            i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            context.startActivity(i);
            Toast.makeText(context, "Please register again. Your registeration information is missed", Toast.LENGTH_LONG).show();
        }
        else {
            Intent i = new Intent(context, BootStartService.class);
            context.startService(i);
            Intent j = new Intent(context, GPS_Service.class);
            context.startService(j);
        }

    }

    private boolean checkFile(Context context) {
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
                    if (line.split(":")[0].equals("Name")){
                        if (debug)
                            Log.d(TAG, "read user name: " + line.split(":")[1] + "from file " + file.getAbsolutePath());
                        return true;
                    }

                    else if (line.split(":")[0].equals("Email")){
                        if (debug)
                            Log.d(TAG, "read user email: " + line.split(":")[1]+ " from file " + file.getAbsolutePath());
                        return true;
                    }
                    else
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


}