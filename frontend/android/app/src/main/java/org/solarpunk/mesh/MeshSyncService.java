package org.solarpunk.mesh;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Intent;
import android.os.Build;
import android.os.IBinder;
import android.util.Log;
import androidx.core.app.NotificationCompat;

import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

/**
 * Background service for mesh network synchronization
 * Starts embedded Python backend and keeps mesh sync active
 */
public class MeshSyncService extends Service {

    private static final String TAG = "MeshSyncService";
    private static final String CHANNEL_ID = "mesh_sync_channel";
    private static final int NOTIFICATION_ID = 1;

    private PyObject pythonModule = null;
    private boolean pythonStarted = false;

    @Override
    public void onCreate() {
        super.onCreate();
        createNotificationChannel();
        initializePython();
    }

    private void initializePython() {
        // Start Python in background thread
        new Thread(() -> {
            try {
                // Initialize Python if not already started
                if (!Python.isStarted()) {
                    Python.start(new AndroidPlatform(getApplicationContext()));
                }

                Python py = Python.getInstance();
                pythonModule = py.getModule("android_main");

                // Initialize database first
                Log.i(TAG, "Initializing database...");
                PyObject initResult = pythonModule.callAttr("init_database");
                Log.i(TAG, "Database init result: " + initResult);

                // Start all servers
                Log.i(TAG, "Starting Python backend servers...");
                PyObject result = pythonModule.callAttr("start_all_servers");
                Log.i(TAG, "Server startup result: " + result);

                pythonStarted = true;

                // Update notification to show backend is ready
                updateNotification("Backend running - mesh sync active");

            } catch (Exception e) {
                Log.e(TAG, "Failed to start Python backend", e);
                updateNotification("Backend failed - " + e.getMessage());
            }
        }).start();
    }

    private void updateNotification(String message) {
        NotificationManager manager = getSystemService(NotificationManager.class);
        if (manager != null) {
            Notification notification = new NotificationCompat.Builder(this, CHANNEL_ID)
                .setContentTitle("Solarpunk Network")
                .setContentText(message)
                .setSmallIcon(android.R.drawable.ic_dialog_info)
                .setOngoing(true)
                .build();
            manager.notify(NOTIFICATION_ID, notification);
        }
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        // Create foreground notification
        Notification notification = createNotification();
        startForeground(NOTIFICATION_ID, notification);

        // Service will continue running
        return START_STICKY;
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @Override
    public void onDestroy() {
        // Stop Python servers
        if (pythonModule != null && pythonStarted) {
            try {
                Log.i(TAG, "Stopping Python backend...");
                pythonModule.callAttr("stop_all_servers");
            } catch (Exception e) {
                Log.e(TAG, "Error stopping Python backend", e);
            }
        }
        super.onDestroy();
        stopForeground(true);
    }

    /**
     * Check if Python backend is healthy
     */
    public boolean isBackendHealthy() {
        if (pythonModule == null || !pythonStarted) {
            return false;
        }
        try {
            PyObject result = pythonModule.callAttr("health_check");
            PyObject allHealthy = result.callAttr("get", "all_healthy");
            return allHealthy != null && allHealthy.toBoolean();
        } catch (Exception e) {
            Log.e(TAG, "Health check failed", e);
            return false;
        }
    }

    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                CHANNEL_ID,
                "Mesh Network Sync",
                NotificationManager.IMPORTANCE_LOW
            );
            channel.setDescription("Keeps mesh network active for offline synchronization");

            NotificationManager manager = getSystemService(NotificationManager.class);
            manager.createNotificationChannel(channel);
        }
    }

    private Notification createNotification() {
        Intent notificationIntent = new Intent(this, MainActivity.class);
        PendingIntent pendingIntent = PendingIntent.getActivity(
            this,
            0,
            notificationIntent,
            PendingIntent.FLAG_IMMUTABLE
        );

        return new NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Solarpunk Network")
            .setContentText("Mesh sync active - connecting with nearby peers")
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentIntent(pendingIntent)
            .setOngoing(true)
            .build();
    }
}
