import subprocess, os, sys
K="../../../styles/neon-dimension/sfx/kit/"; P="../../../sfx-library/celf-sfx-pack/"
ff=os.environ["HYPERFRAMES_FFMPEG_PATH"]
EV=[ # time, file, gain dB, align: 'start' or 'end' (riser ends at time)
 (1.22,K+"ND_swish.wav",-10),(1.22,K+"ND_sub_boom.wav",-9),(2.10,K+"ND_sub_boom.wav",-7),(2.42,P+"Whoosh_05_Fast_Flick.wav",-14),
 (2.74,K+"ND_flash_hit.wav",-11),(4.86,P+"Pop_02_Quick.wav",-12),(6.32,P+"Pop_01_Tap.wav",-12),
 (7.78,K+"ND_riser.wav",-14,"end"),(7.70,K+"ND_energy_burst.wav",-9),(7.78,K+"ND_sub_boom.wav",-8),
 (11.62,K+"ND_swish.wav",-11),(11.62,K+"ND_glitch.wav",-20),(12.54,K+"ND_flash_hit.wav",-11),(15.36,P+"Pop_02_Quick.wav",-12),
 (16.20,K+"ND_glitch.wav",-15),(16.24,K+"ND_swish.wav",-10),(18.14,K+"ND_sub_boom.wav",-12),(18.14,P+"Whoosh_02_Wave.wav",-15),(18.88,P+"Whoosh_05_Fast_Flick.wav",-12),
 (21.56,K+"ND_glitch.wav",-14),(21.60,K+"ND_sub_boom.wav",-10),(22.28,K+"ND_sub_boom.wav",-9),(22.62,K+"ND_energy_burst.wav",-11),
 (24.73,K+"ND_swish.wav",-11),(24.73,K+"ND_sub_boom.wav",-11),(25.21,K+"ND_flash_hit.wav",-11),
 (27.70,K+"ND_glitch.wav",-14),(27.74,K+"ND_sub_boom.wav",-10),(28.12,K+"ND_sub_boom.wav",-9),(28.80,P+"Whoosh_05_Fast_Flick.wav",-15),
 (30.12,K+"ND_swish.wav",-9),(31.14,P+"Whoosh_02_Wave.wav",-15),(32.44,K+"ND_flash_hit.wav",-11),(33.20,P+"Pop_02_Quick.wav",-12),
 (36.11,K+"ND_riser.wav",-14,"end"),(36.03,K+"ND_energy_burst.wav",-10),(36.11,K+"ND_sub_boom.wav",-8),(36.97,P+"Whoosh_05_Fast_Flick.wav",-15),
 (39.31,K+"ND_swish.wav",-11),(39.77,K+"ND_flash_hit.wav",-11),(40.91,P+"Pop_01_Tap.wav",-12),
 (43.09,K+"ND_riser.wav",-14,"end"),(43.01,K+"ND_energy_burst.wav",-10),(43.09,K+"ND_sub_boom.wav",-8),(43.11,P+"Mouse_Click_02_Tactile.wav",-12),
 (45.07,P+"Chime_01_Coin_Pickup.wav",-13),(45.07,K+"ND_sub_boom.wav",-10),(45.93,K+"ND_swish.wav",-12),
 (46.91,K+"ND_flash_hit.wav",-11),(47.0,P+"Sparkle_04_Scene_Reveal.wav",-18)]
def dur(f): return float(subprocess.check_output([ff.replace("ffmpeg","ffprobe") if False else os.environ["HYPERFRAMES_FFPROBE_PATH"],"-v","error","-show_entries","format=duration","-of","csv=p=0",f]))
ins=["-i","A_voice.wav","-i",K+"ND_dark_bed_70bpm.wav"]; fc=["[0:a]aformat=sample_rates=48000:channel_layouts=stereo,loudnorm=I=-15:TP=-2:LRA=9,apad=whole_dur=48.4[v]",
  "[1:a]atrim=0:48.4,volume=-20dB,afade=t=out:st=47.0:d=1.4[bed]"]
labs=["[v]","[bed]"]
for i,e in enumerate(EV):
    t,f,g=e[:3]; 
    if len(e)>3: t=t-dur(f)
    ins+=["-i",f]; d=int(max(0,t)*1000)
    fc.append(f"[{i+2}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={g}dB,adelay={d}|{d}[s{i}]"); labs.append(f"[s{i}]")
fc.append("".join(labs)+f"amix=inputs={len(labs)}:normalize=0:duration=first,alimiter=limit=0.89,atrim=0:48.4[out]")
subprocess.run([ff,"-v","error","-y",*ins,"-filter_complex",";".join(fc),"-map","[out]","-ar","48000","-c:a","pcm_s16le","mix_v1.wav"],check=True)
print("ok")
