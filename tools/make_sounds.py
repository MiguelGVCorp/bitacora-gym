import math, struct, wave, sys
SR=44100
def render(path, notes, peak=0.55, tail=0.4):
    total=max(s+d for (_,d,s,_,_) in notes)+tail; n=int(total*SR); buf=[0.0]*n
    for f,d,s,timbre,dec in notes:
        att=0.012
        for i in range(int(d*SR)):
            t=i/SR; env=min(1,t/att)*math.exp(-t*dec)
            v=sum(a*math.sin(2*math.pi*f*m*t)*math.exp(-t*extra) for m,a,extra in timbre)
            j=int(s*SR)+i
            if j<n: buf[j]+=env*v
    # fade out final
    fo=int(0.05*SR)
    for k in range(fo): buf[n-1-k]*=k/fo
    pk=max(abs(x) for x in buf) or 1
    w=wave.open(path,'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(b''.join(struct.pack('<h',int(32767*peak*x/pk)) for x in buf)); w.close()
MARIMBA=[(1,1.0,0),(3.93,0.25,18),(9.2,0.06,40)]
KALIMBA=[(1,1.0,0),(2.0,0.15,6),(5.4,0.12,25)]
SOFT=[(1,1.0,0),(2.0,0.08,3)]
C5,E5,G5,C6=523.25,659.25,783.99,1046.5
# 1 Marimba: arpegio ascendente do-mi-sol
render('marimba.wav',[(C5,1.0,0.00,MARIMBA,5),(E5,1.0,0.13,MARIMBA,5),(G5,1.2,0.26,MARIMBA,4.5)])
# 2 Kalimba: sol - do agudo, como cajita de música
render('kalimba.wav',[(G5,1.2,0.00,KALIMBA,3.8),(C6,1.4,0.18,KALIMBA,3.2)])
# 3 Suave: dos notas cálidas que suben (la - mi)
render('suave.wav',[(440,1.4,0.00,SOFT,2.6),(659.25,1.6,0.22,SOFT,2.4)], peak=0.5)
# tic de cuenta regresiva: madera suave
render('tic.wav',[(880,0.10,0,[(1,1.0,0),(2.7,0.2,40)],35)], peak=0.32, tail=0.02)
