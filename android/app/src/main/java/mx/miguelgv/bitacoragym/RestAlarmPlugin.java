package mx.miguelgv.bitacoragym;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.os.Build;

import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

/**
 * Alarma del fin de descanso.
 * Programa el sonido final y los tics 3-2-1 como alarmas de reloj (setAlarmClock):
 * es el tipo de alarma que Android y Samsung respetan aunque la pantalla esté
 * bloqueada, la app en segundo plano o el celular en ahorro de batería.
 */
@CapacitorPlugin(name = "RestAlarm")
public class RestAlarmPlugin extends Plugin {
    static final int REQ_DONE = 7001;
    static final int[] REQ_TICKS = {7002, 7003, 7004};

    private PendingIntent pending(int req, String kind) {
        Context ctx = getContext();
        Intent i = new Intent(ctx, RestAlarmReceiver.class);
        i.setAction("mx.miguelgv.bitacoragym.REST_" + req);
        i.putExtra("kind", kind);
        return PendingIntent.getBroadcast(ctx, req, i, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }

    private PendingIntent showApp() {
        Context ctx = getContext();
        Intent i = new Intent(ctx, MainActivity.class);
        i.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        return PendingIntent.getActivity(ctx, 7010, i, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }

    private void set(AlarmManager am, long when, PendingIntent pi, boolean exact) {
        if (exact) am.setAlarmClock(new AlarmManager.AlarmClockInfo(when, showApp()), pi);
        else am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, when, pi);
    }

    private void cancelAll(AlarmManager am) {
        am.cancel(pending(REQ_DONE, "done"));
        for (int r : REQ_TICKS) am.cancel(pending(r, "tick"));
    }

    @PluginMethod
    public void schedule(PluginCall call) {
        Double at = call.getDouble("at");
        if (at == null) { call.reject("Falta 'at'"); return; }
        boolean ticks = call.getBoolean("ticks", true);
        AlarmManager am = (AlarmManager) getContext().getSystemService(Context.ALARM_SERVICE);
        cancelAll(am);
        long when = at.longValue(), now = System.currentTimeMillis();
        boolean exact = true;
        if (Build.VERSION.SDK_INT >= 31) exact = am.canScheduleExactAlarms();
        try {
            set(am, when, pending(REQ_DONE, "done"), exact);
            if (ticks && exact) {
                for (int k = 0; k < 3; k++) {
                    long t = when - (3 - k) * 1000L;
                    if (t > now + 400) set(am, t, pending(REQ_TICKS[k], "tick"), true);
                }
            }
        } catch (SecurityException e) {
            am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, when, pending(REQ_DONE, "done"));
        }
        call.resolve();
    }

    @PluginMethod
    public void cancel(PluginCall call) {
        cancelAll((AlarmManager) getContext().getSystemService(Context.ALARM_SERVICE));
        call.resolve();
    }

    @PluginMethod
    public void tick(PluginCall call) {
        RestSound.tick(getContext());
        call.resolve();
    }

    @PluginMethod
    public void test(PluginCall call) {
        RestSound.done(getContext(), call.getString("name"));
        call.resolve();
    }

    @PluginMethod
    public void setSound(PluginCall call) {
        String name = call.getString("name", "marimba");
        RestSound.setChosen(getContext(), name);
        call.resolve();
    }
}
