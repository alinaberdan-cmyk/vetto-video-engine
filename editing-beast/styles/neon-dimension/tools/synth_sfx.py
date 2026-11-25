"""Neon Dimension SFX kit: synthesized equivalents of the sounds measured on the reference cuts.
Usage: python synth_sfx.py <outdir>"""
import sys, os, wave, numpy as np
SR=48000; out=sys.argv[1]; os.makedirs(out,exist_ok=True); rng=np.random.default_rng(7)
def save(name,x,width=0.0):
    x=np.asarray(x,float); x=x/ (np.abs(x).max()+1e-9)*0.89
    if width>0:
        d=int(SR*0.011); r=np.concatenate([np.zeros(d),x[:-d]]); L=x; R=(1-width)*x+width*r
    else: L=R=x
    st=(np.stack([L,R],1)*32767).astype(np.int16)
    w=wave.open(os.path.join(out,name),'w'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes()); w.close()
def t(d): return np.arange(int(SR*d))/SR
def lp(x,fc):  # one-pole lowpass, fc may be array
    fc=np.broadcast_to(np.asarray(fc,float),x.shape); a=np.exp(-2*np.pi*fc/SR); y=np.zeros_like(x); s=0.0
    for i in range(len(x)): s=(1-a[i])*x[i]+a[i]*s; y[i]=s
    return y
def hp(x,fc): return x-lp(x,fc)
# 1 sub boom: pitch-dropping sine 90->32 Hz + click
d=1.6; tt=t(d); f=32+58*np.exp(-tt*9); ph=2*np.pi*np.cumsum(f)/SR
boom=np.sin(ph)*np.exp(-tt*2.6); boom[:240]+=rng.normal(0,0.6,240)*np.linspace(1,0,240)
save("ND_sub_boom.wav",np.tanh(boom*1.6))
# 2 swish (fast flick): bandpassed noise sweeping 9k->1.5k, 0.35s, asymmetric envelope
d=0.42; tt=t(d); n=rng.normal(0,1,len(tt)); env=np.sin(np.pi*np.clip(tt/d,0,1))**0.6*np.exp(-tt*4)
sw=hp(lp(n,np.linspace(9000,1500,len(tt))),np.linspace(2500,400,len(tt)))*env
save("ND_swish.wav",sw,0.6)
# 3 reverse riser into cut: noise + rising tone 1.2s, ends abruptly
d=1.2; tt=t(d); env=(tt/d)**2.5; n=lp(rng.normal(0,1,len(tt)),300+9000*(tt/d)**2)
tone=np.sin(2*np.pi*np.cumsum(120+900*(tt/d)**3)/SR)*0.35
save("ND_riser.wav",(n+tone)*env,0.5)
# 4 glitch stutter: bit-crushed square chirps chopped at 30 Hz
d=0.3; tt=t(d); sq=np.sign(np.sin(2*np.pi*np.cumsum(rng.choice([180,420,950,1700],len(tt)//1600+1).repeat(1600)[:len(tt)])/SR))
gate=(np.floor(tt*30)%2==0).astype(float); cr=np.round((sq*0.6+rng.normal(0,0.3,len(tt)))*6)/6
save("ND_glitch.wav",cr*gate*np.exp(-tt*5),0.8)
# 5 flash hit: bright noise burst + shimmer (for white light-burn transitions)
d=1.0; tt=t(d); n=hp(rng.normal(0,1,len(tt)),3000)*np.exp(-tt*7)
sh=sum(np.sin(2*np.pi*fq*tt+rng.uniform(0,6))*np.exp(-tt*3) for fq in (2637,3520,4186,5274))*0.15
save("ND_flash_hit.wav",n+sh+0.6*np.interp(tt,t(1.6),boom[:len(t(1.6))]),0.7)
# 6 energy burst: low growl + noise wash (neon plasma wipe)
d=0.9; tt=t(d); g=np.sin(2*np.pi*np.cumsum(55+40*np.sin(tt*30))/SR)*np.exp(-tt*3); w=lp(rng.normal(0,1,len(tt)),2500)*np.sin(np.pi*tt/d)
save("ND_energy_burst.wav",np.tanh(1.5*g+w*0.8),0.6)
# 7 dark cinematic bed: 72s, 70 BPM pulse, minor pad (A minor), sub heartbeats
d=72; tt=t(d); bpm=70; beat=60/bpm
def pad(freqs,amp): return sum(np.sin(2*np.pi*f*tt+np.sin(2*np.pi*0.07*tt+i)*1.5)*amp for i,f in enumerate(freqs))
padx=pad([55,110,130.81,164.81,220],0.18)+pad([110.5,165.3],0.08)
padx=lp(padx,900); padx*=0.6+0.4*np.sin(2*np.pi*tt/16)**2
kick=np.zeros_like(tt)
for k in np.arange(0,d,beat*2):
    i=int(k*SR); m=min(len(tt)-i,int(SR*0.6)); kt=np.arange(m)/SR
    kick[i:i+m]+=np.sin(2*np.pi*np.cumsum(45+70*np.exp(-kt*25))/SR)*np.exp(-kt*6)
hat=hp(rng.normal(0,1,len(tt)),7000)*0.05*((np.floor(tt/(beat/2))%2)==1)*np.exp(-((tt%(beat/2))*30))
air=lp(rng.normal(0,1,len(tt)),600)*0.05
bed=padx+0.9*kick+hat+air; bed[:SR*2]*=np.linspace(0,1,SR*2); bed[-SR*3:]*=np.linspace(1,0,SR*3)
save("ND_dark_bed_70bpm.wav",np.tanh(bed*1.2),0.4)
print("ok")
