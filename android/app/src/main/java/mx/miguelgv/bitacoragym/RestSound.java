package mx.miguelgv.bitacoragym;

import android.content.Context;
import android.content.res.AssetFileDescriptor;
import android.media.AudioAttributes;
import android.media.MediaPlayer;
import android.os.Build;
import android.os.VibrationEffect;
import android.os.Vibrator;

/**
 * Sonido propio del fin de descanso.
 * Se reproduce con el volumen multimedia y SIN pedir el foco de audio,
 * así la música que estés escuchando no baja de volumen ni se pausa,
 * y no aparece ninguna notificación.
 */
public final class RestSound {
    private RestSound() {}

    public static void play(Context ctx, int rawRes, long[] vibration) {
        try {
            AssetFileDescriptor afd = ctx.getResources().openRawResourceFd(rawRes);
            MediaPlayer mp = new MediaPlayer();
            mp.setAudioAttributes(new AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_GAME)
                    .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                    .build());
            mp.setDataSource(afd.getFileDescriptor(), afd.getStartOffset(), afd.getLength());
            afd.close();
            mp.setOnCompletionListener(MediaPlayer::release);
            mp.prepare();
            mp.start();
        } catch (Exception ignored) { }
        if (vibration != null) {
            try {
                Vibrator v = (Vibrator) ctx.getSystemService(Context.VIBRATOR_SERVICE);
                if (v != null && v.hasVibrator()) {
                    if (Build.VERSION.SDK_INT >= 26) v.vibrate(VibrationEffect.createWaveform(vibration, -1));
                    else v.vibrate(vibration, -1);
                }
            } catch (Exception ignored) { }
        }
    }

    /** Fin del descanso: dos campanadas y una vibración larga-corta-larga. */
    public static void done(Context ctx) {
        play(ctx, R.raw.descanso, new long[]{0, 350, 120, 120, 120, 350});
    }

    /** Cuenta regresiva 3-2-1: un tic corto. */
    public static void tick(Context ctx) {
        play(ctx, R.raw.tic, new long[]{0, 40});
    }
}
