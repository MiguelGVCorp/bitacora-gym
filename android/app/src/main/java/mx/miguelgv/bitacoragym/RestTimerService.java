package mx.miguelgv.bitacoragym;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.content.pm.ServiceInfo;
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.os.PowerManager;

/**
 * Servicio en primer plano que vive solo durante el descanso.
 * Mantiene el CPU despierto y toca los tics 3-2-1 y el sonido final
 * aunque la pantalla esté bloqueada. Muestra un aviso silencioso con la cuenta regresiva.
 */
public class RestTimerService extends Service {
    static final String ACTION_START = "mx.miguelgv.bitacoragym.REST_START";
    static final String CHANNEL = "temporizador";
    static final int NID = 7101;

    private final Handler h = new Handler(Looper.getMainLooper());
    private PowerManager.WakeLock wl;

    @Override public IBinder onBind(Intent intent) { return null; }

    private void channel() {
        if (Build.VERSION.SDK_INT < 26) return;
        NotificationManager nm = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm.getNotificationChannel(CHANNEL) != null) return;
        NotificationChannel ch = new NotificationChannel(CHANNEL, "Temporizador de descanso", NotificationManager.IMPORTANCE_LOW);
        ch.setDescription("Cuenta regresiva silenciosa mientras descansas entre series");
        ch.setSound(null, null);
        ch.enableVibration(false);
        ch.setShowBadge(false);
        nm.createNotificationChannel(ch);
    }

    private Notification notif(long end, String label) {
        Intent open = new Intent(this, MainActivity.class);
        open.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        PendingIntent pi = PendingIntent.getActivity(this, 7102, open, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        Notification.Builder b = Build.VERSION.SDK_INT >= 26 ? new Notification.Builder(this, CHANNEL) : new Notification.Builder(this);
        b.setSmallIcon(android.R.drawable.ic_lock_idle_alarm)
         .setContentTitle(label == null || label.isEmpty() ? "Descanso" : "Descanso · " + label)
         .setContentText("Te aviso con sonido al terminar")
         .setContentIntent(pi)
         .setOngoing(true)
         .setOnlyAlertOnce(true)
         .setShowWhen(true)
         .setWhen(end)
         .setUsesChronometer(true)
         .setCategory(Notification.CATEGORY_STOPWATCH);
        if (Build.VERSION.SDK_INT >= 24) b.setChronometerCountDown(true);
        if (Build.VERSION.SDK_INT < 26) b.setPriority(Notification.PRIORITY_LOW);
        return b.build();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent == null || !ACTION_START.equals(intent.getAction())) { stopSelf(); return START_NOT_STICKY; }
        long end = intent.getLongExtra("end", 0);
        String label = intent.getStringExtra("label");
        channel();
        Notification n = notif(end, label);
        try {
            if (Build.VERSION.SDK_INT >= 34) startForeground(NID, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE);
            else startForeground(NID, n);
        } catch (Exception e) {
            stopSelf();
            return START_NOT_STICKY;
        }
        h.removeCallbacksAndMessages(null);
        long now = System.currentTimeMillis();
        if (end <= now) { stopNow(); return START_NOT_STICKY; }
        if (wl == null) {
            PowerManager pm = (PowerManager) getSystemService(Context.POWER_SERVICE);
            wl = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "bitacora:descanso");
            wl.setReferenceCounted(false);
        }
        wl.acquire(end - now + 6000);
        for (int k = 3; k >= 1; k--) {
            long at = end - k * 1000L - now;
            if (at > 300) h.postDelayed(() -> { if (!RestAlarmPlugin.visible) RestSound.tick(getApplicationContext()); }, at);
        }
        h.postDelayed(() -> {
            if (!RestAlarmPlugin.visible) RestSound.done(getApplicationContext());
            h.postDelayed(this::stopNow, 2500);
        }, end - now);
        return START_NOT_STICKY;
    }

    private void stopNow() {
        h.removeCallbacksAndMessages(null);
        try { if (wl != null && wl.isHeld()) wl.release(); } catch (Exception ignored) { }
        if (Build.VERSION.SDK_INT >= 24) stopForeground(STOP_FOREGROUND_REMOVE); else stopForeground(true);
        stopSelf();
    }

    @Override
    public void onDestroy() {
        h.removeCallbacksAndMessages(null);
        try { if (wl != null && wl.isHeld()) wl.release(); } catch (Exception ignored) { }
        super.onDestroy();
    }
}
