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

/** Alarma del fin de descanso: programa, cancela y reproduce el sonido propio de la app. */
@CapacitorPlugin(name = "RestAlarm")
public class RestAlarmPlugin extends Plugin {

    private PendingIntent pending() {
        Context ctx = getContext();
        Intent i = new Intent(ctx, RestAlarmReceiver.class);
        return PendingIntent.getBroadcast(ctx, 7001, i, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }

    @PluginMethod
    public void schedule(PluginCall call) {
        Double at = call.getDouble("at");
        if (at == null) { call.reject("Falta 'at'"); return; }
        AlarmManager am = (AlarmManager) getContext().getSystemService(Context.ALARM_SERVICE);
        PendingIntent pi = pending();
        am.cancel(pi);
        long when = at.longValue();
        boolean exact = true;
        if (Build.VERSION.SDK_INT >= 31) exact = am.canScheduleExactAlarms();
        if (exact) am.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, when, pi);
        else am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, when, pi);
        call.resolve();
    }

    @PluginMethod
    public void cancel(PluginCall call) {
        AlarmManager am = (AlarmManager) getContext().getSystemService(Context.ALARM_SERVICE);
        am.cancel(pending());
        call.resolve();
    }

    @PluginMethod
    public void tick(PluginCall call) {
        RestSound.tick(getContext());
        call.resolve();
    }

    @PluginMethod
    public void test(PluginCall call) {
        RestSound.done(getContext());
        call.resolve();
    }
}
