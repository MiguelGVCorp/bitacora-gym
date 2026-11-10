package mx.miguelgv.bitacoragym;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.PowerManager;

/** Suena al terminar el descanso (y los tics 3-2-1) aunque el celular esté bloqueado o la app cerrada. */
public class RestAlarmReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        final PendingResult pr = goAsync();
        final Context app = context.getApplicationContext();
        PowerManager pm = (PowerManager) app.getSystemService(Context.POWER_SERVICE);
        final PowerManager.WakeLock wl = pm == null ? null : pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "bitacora:descanso");
        if (wl != null) wl.acquire(4000);
        boolean tick = "tick".equals(intent.getStringExtra("kind"));
        if (tick) RestSound.tick(app); else RestSound.done(app);
        new android.os.Handler(android.os.Looper.getMainLooper()).postDelayed(() -> {
            try { if (wl != null && wl.isHeld()) wl.release(); } catch (Exception ignored) { }
            pr.finish();
        }, tick ? 900 : 3000);
    }
}
