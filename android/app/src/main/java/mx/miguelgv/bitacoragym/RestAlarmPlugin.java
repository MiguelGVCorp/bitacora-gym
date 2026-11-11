package mx.miguelgv.bitacoragym;

import android.content.Context;
import android.content.Intent;
import android.os.Build;

import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

/**
 * Temporizador de descanso.
 * Con la app abierta, los sonidos los dispara la app (tick/done).
 * Con la pantalla bloqueada o la app en segundo plano, los toca RestTimerService,
 * un servicio en primer plano que se mantiene despierto solo mientras dura el descanso.
 */
@CapacitorPlugin(name = "RestAlarm")
public class RestAlarmPlugin extends Plugin {
    static volatile boolean visible = true;

    @Override protected void handleOnResume() { visible = true; }
    @Override protected void handleOnPause() { visible = false; }
    @Override protected void handleOnStop() { visible = false; }

    @PluginMethod
    public void schedule(PluginCall call) {
        Double at = call.getDouble("at");
        if (at == null) { call.reject("Falta 'at'"); return; }
        Context ctx = getContext();
        Intent i = new Intent(ctx, RestTimerService.class);
        i.setAction(RestTimerService.ACTION_START);
        i.putExtra("end", at.longValue());
        i.putExtra("label", call.getString("label", ""));
        try {
            if (Build.VERSION.SDK_INT >= 26) ctx.startForegroundService(i); else ctx.startService(i);
            call.resolve();
        } catch (Exception e) {
            call.reject("No se pudo iniciar el temporizador: " + e.getMessage());
        }
    }

    @PluginMethod
    public void cancel(PluginCall call) {
        Context ctx = getContext();
        try { ctx.stopService(new Intent(ctx, RestTimerService.class)); } catch (Exception ignored) { }
        call.resolve();
    }

    @PluginMethod
    public void tick(PluginCall call) {
        RestSound.tick(getContext());
        call.resolve();
    }

    @PluginMethod
    public void done(PluginCall call) {
        RestSound.done(getContext());
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
