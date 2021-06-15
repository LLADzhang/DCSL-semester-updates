package com.collector_fcm;

import android.content.Context;
import android.support.annotation.NonNull;
import android.util.Log;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;

/**
 * Created by Henry on 05/02/2018.
 */

final class Server {
    private static final  String TAG = "Server";
    private static final String URL_SPEC = "http://128.46.73.216:8083";
    private static final Server instance = new Server(URL_SPEC);

    private final URL url;
    private Server(@NonNull String spec){
        try {
            this.url = new URL(spec);
        } catch (MalformedURLException e) {
            throw new RuntimeException(e);
        }
    }

    static Server getInstance() {
        return instance;
    }

    private void postJSON(@NonNull JSONObject object) throws IOException {
        Log.d(TAG, "postJSON: " + object);
        try {
            HttpURLConnection connection = HTTP.postJSON(url, object);
            connection.getInputStream().close();
            connection.disconnect();
        } catch (IOException e) {
            throw new IOException(e);
        }
    }

    void sendData(@NonNull File file) {
        String data = null;
        try {
            data = readFile(file);

            if (data != null) {
//                String TunedData = data.replaceAll("\\}\\{", "\\}--\\{");
                postJSON(new JSONObject().put("data", data));
                Log.i(TAG, "post data: " + data);
                deleteHistory(file);
            }
            else Log.i(TAG, "no data, sorry!!");
        } catch (Exception e) {
            e.printStackTrace();
            if ( data != null)
                storeToHistory(file, data);
        }
    }

    private void storeToHistory(File file, String data) {
        FileOutputStream outputStream;
        try{
            outputStream = new FileOutputStream(file);
            if (!file.exists())
                file.createNewFile();

            outputStream.write(data.getBytes("UTF-8"));
            outputStream.close();


        } catch (Exception e) {
            e.printStackTrace();
        }
    }



    private void deleteHistory(File file) {
        if(file.exists()) {
            file.delete();
                Log.d(TAG, "delete history file" + file.getAbsolutePath());
        }
        else {
                Log.d(TAG, "no file to delete");
        }
    }

    private String readFile(File file) throws FileNotFoundException {
        String data = null;
        if (file.exists()) {
            try{
                BufferedReader input = new BufferedReader(new InputStreamReader(new FileInputStream(file)));
                data = input.readLine();
            }
         catch (IOException e) {
            e.printStackTrace();
        }

        }
        return data;
    }
}
