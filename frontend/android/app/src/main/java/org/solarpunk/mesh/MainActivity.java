package org.solarpunk.mesh;

import android.content.Intent;
import android.os.Build;
import android.os.Bundle;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Start the mesh sync service (which also starts Python backend)
        startMeshSyncService();
    }

    private void startMeshSyncService() {
        Intent serviceIntent = new Intent(this, MeshSyncService.class);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            // For Android 8+, use startForegroundService
            startForegroundService(serviceIntent);
        } else {
            startService(serviceIntent);
        }
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        // Service continues running in background
        // Only stop if explicitly requested
    }
}
