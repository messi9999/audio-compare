import librosa
from sklearn.metrics.pairwise import cosine_similarity

import sounddevice as sd
import threading
import time
import datetime
import os

import asyncio


input = librosa.load('./audio/source/input.mp3')
[input_audio, input_sr] = input

async def slice_audio(audio, sr, sTime, eTime):
    slice_start = int(sTime * sr)
    slice_end = int(eTime * sr)
    return audio[slice_start:slice_end]

async def cal_similarity(sAudio1, sAudio2, fsr1, fsr2):
    # If necessary, resample the audio files to a common sample rate
    if fsr1 != fsr2:
        sAudio1 = librosa.resample(sAudio1, fsr1, fsr2)
        fsr1 = fsr2    
    
    # Extract MFCC features from the encoded audio files
    mfcc1 = librosa.feature.mfcc(y=sAudio1, sr=fsr1)
    mfcc2 = librosa.feature.mfcc(y=sAudio2, sr=fsr2)

    # Compute the cosine similarity between the MFCC features
    result = cosine_similarity(mfcc1.T, mfcc2.T)[0][0]
    
    # print("Similarity between the audio files: {:.2%}".format(similarity))
    await asyncio.sleep(0.01)
    return result


def play_audio():
    global input_audio
    global input_sr
    global playStatus
    playStatus = True
    sd.play(input_audio, input_sr)
    sd.wait()

def run():
    global input_audio
    global input_sr
    playStatus = False    
    file_list = os.listdir("./audio/samples")
    audios = []    
    for file in file_list:
        audios.append(librosa.load('./audio/samples/' + file))
    sliced_audios = []

    async def get_sliced_audios():
        res = await asyncio.gather(*(slice_audio(audio[0], audio[1], sTime=3.0, eTime=4.0) for audio in audios))
        return res
    sliced_audios = asyncio.run(get_sliced_audios())



    playStatus = True    
    start_time = time.time()
    temp_time = time.time()   

    similarities = []
    print("start..............")
    while True:
            
        try:
            if not playStatus:
                break
            time_now = time.time()
            if time_now - temp_time > 1:
                print(datetime.datetime.fromtimestamp(time_now))

                audio_time = time_now - start_time
                async def get_sliced_input():
                    res = await asyncio.gather(slice_audio(audio=input_audio, sr=input_sr, sTime=audio_time, eTime=audio_time + 1.0))
                    return res
                sliced_input_audio = asyncio.run(get_sliced_input())

                async def get_similarities():
                    res = await asyncio.gather(*(cal_similarity(sliced_input_audio[0], sliced_audio, input_sr, audios[index][1]) for index, sliced_audio in enumerate(sliced_audios)))
                    return res
                similarities = asyncio.run(get_similarities())

                max_result = max(similarities)
                max_index = similarities.index(max_result)

                print("Index: ", max_index + 1, "            Similarity:  ", max_result)

                # if max_index > 0.9:
                #     print("finished")
                #     print("Similarity = ", max_result)
                #     print("Index = ", max_index)
                #     break

                temp_time = time_now
        except:
            print("Error")
            break


if __name__ == "__main__":
    playThread = threading.Thread(target=play_audio)
    runThred = threading.Thread(target=run)
    playThread.start() 
    runThred.start() 
    playThread.join()
    runThred.join()


    




        

    
