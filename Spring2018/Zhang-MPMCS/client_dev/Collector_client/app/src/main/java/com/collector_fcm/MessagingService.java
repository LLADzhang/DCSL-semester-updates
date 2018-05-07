package com.collector_fcm;

import android.content.Intent;
import android.support.annotation.NonNull;
import android.util.Log;

import com.google.firebase.messaging.FirebaseMessagingService;
import com.google.firebase.messaging.RemoteMessage;

import java.io.File;

/**
 * Created by Henry on 24/01/2018.
 */

public final class MessagingService extends FirebaseMessagingService {
    private static final String TAG = "MessagingService";


    @Override
    public void onMessageReceived(@NonNull RemoteMessage remoteMessage) {
        Log.d(TAG, "onMessageReceived: " + remoteMessage.getData());
//        Intent intent = new Intent();
//        intent.setAction("upload_request");
//        intent.putExtra("category", "fcm");
//        sendBroadcast(intent);
        Server.getInstance().sendData(new File(this.getFilesDir(), "history"));


    }
    @Override
    public void onDeletedMessages(){
        Log.d(TAG, "onDeleteMesages");
    }
}
