package mx.miguelgv.bitacoragym;

import android.Manifest;
import android.content.Context;
import android.content.Intent;
import android.os.Build;

import com.getcapacitor.JSObject;
import com.getcapacitor.PermissionState;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;
import com.getcapacitor.annotation.Permission;
import com.getcapacitor.annotation.PermissionCallback;

/**
 * Temporizador de descanso.
 * Con la app abierta, los sonidos los dispara la app (tick/done).
 * Con la pantalla bloqueada o la app en segundo plano, los toca RestTimerService,
 * un servicio en primer plano que se mantiene despierto solo mientras dura el descanso.
 */
@CapacitorPlugin(
    name = "RestAlarm",
    permissions = { @Permission(alias = "avisos", strings = { Manifest.permission.POST_NOTIFICATIONS }) }
)
public class RestAlarmPlugin extends Plugin {
    static volatile boolean visible = true;

    @Override protected void handleOnResume() { visible = true; }
    @Override protected void handleOnPause() { visible = false; }
    @Override protected void handleOnStop() { visible = false; }

    @PluginMethod
    public void schedule(PluginCall call) {
        // La hora llega en milisegundos (un número largo). call.getDouble() devuelve null con números
        // largos, por eso antes el servicio nunca arrancaba; se lee directo del JSON.
        long at = (long) call.getData().optDouble("at", 0);
        if (at <= 0) { call.reject("Falta 'at'"); return; }
        Context ctx = getContext();
        Intent i = new Intent(ctx, RestTimerService.class);
        i.setAction(RestTimerService.ACTION_START);
        i.putExtra("end", at);
        i.putExtra("label", call.getString("label", ""));
        try {
            if (Build.VERSION.SDK_INT >= 26) ctx.startForegroundService(i); else ctx.startService(i);
            JSObject r = new JSObject();
            r.put("ok", true);
            call.resolve(r);
        } catch (Exception e) {
            call.reject("No se pudo iniciar el temporizador: " + e.getMessage());
        }
    }

    /** Pide permiso para mostrar la cuenta regresiva en la barra de notificaciones (Android 13 o más nuevo). */
    @PluginMethod
    public void askNotif(PluginCall call) {
        if (Build.VERSION.SDK_INT < 33 || getPermissionState("avisos") == PermissionState.GRANTED) { notifResult(call); return; }
        requestPermissionForAlias("avisos", call, "notifDone");
    }

    @PermissionCallback
    private void notifDone(PluginCall call) { notifResult(call); }

    private void notifResult(PluginCall call) {
        JSObject r = new JSObject();
        r.put("granted", Build.VERSION.SDK_INT < 33 || getPermissionState("avisos") == PermissionState.GRANTED);
        call.resolve(r);
    }

    @PluginMethod
    public void cancel(PluginCall call) {
        Context ctx = getContext();
        try { ctx.stopService(new Intent(ctx, RestTimerService.class)); } catch (Exception ignored) { }
        call.resolve();
    }

    @PluginMethod
    public void tick(PluginCall call) {
        RestSound.tickOnce(getContext());
        call.resolve();
    }

    @PluginMethod
    public void done(PluginCall call) {
        RestSound.doneOnce(getContext());
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
