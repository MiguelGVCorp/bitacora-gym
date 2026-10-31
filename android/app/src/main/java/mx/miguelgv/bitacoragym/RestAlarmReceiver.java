package mx.miguelgv.bitacoragym;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

/** Suena al terminar el descanso aunque el celular esté bloqueado o la app en segundo plano. */
public class RestAlarmReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        final PendingResult pr = goAsync();
        RestSound.done(context.getApplicationContext());
        new android.os.Handler(android.os.Looper.getMainLooper()).postDelayed(pr::finish, 2500);
    }
}
