# Bitácora Gym

App de Android para registrar entrenamientos (pesos, placas, repeticiones, descansos) y comida (calorías y macros con Gemini, peso y pasos).

## Instalar o actualizar en el celular

1. Desde el celular abre **Releases → la más reciente** de este repositorio.
2. Descarga **BitacoraGym.apk** y ábrelo. La primera vez Android pedirá permitir instalar apps de tu navegador.
3. Para actualizar, repite lo mismo: se instala encima y tus datos se conservan.

## Cómo está hecha

- `www/index.html`: toda la app (HTML, CSS y JS sin dependencias externas).
- Capacitor 8 la empaqueta como app nativa: notificación de fin de descanso con pantalla bloqueada, pantalla encendida durante la sesión, compartir respaldos.
- `tools/build_www.py` genera `www/index.html` a partir de la versión web original (`tools/source-artifact.html`).
- Cada push a `main` compila el APK firmado con GitHub Actions y lo publica en Releases.
