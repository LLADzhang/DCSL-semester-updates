package com.collector_fcm;
import android.util.Log;

import com.google.firebase.iid.FirebaseInstanceId;
import com.google.firebase.iid.FirebaseInstanceIdService;

public final class InstanceIdService extends FirebaseInstanceIdService {
    private static final String TAG = "InstanceIdService";

    @Override
    public void onTokenRefresh() {
        Log.d(TAG, "onTokenRefresh called");

        String refreshedToken = FirebaseInstanceId.getInstance().getToken();
        Log.d(TAG, "refreshedToken: " + refreshedToken);

    }
}
