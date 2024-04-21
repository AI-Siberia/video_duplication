from moviepy.editor import VideoFileClip
from deep_translator import GoogleTranslator

import os
import torch
import torchaudio
import audio_effects as ae
from pydub import AudioSegment
import pandas as pd
from tqdm import tqdm
import stable_whisper
from TTS.api import TTS
import os
import csv
from tqdm import tqdm
import ssl
import locale
locale.getpreferredencoding = lambda: "UTF-8"


class Duplicate_video_model:
    def __init__(self):
        ssl._create_default_https_context = ssl._create_unverified_context
        locale.getpreferredencoding = lambda: "UTF-8"

        self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)

        self.model = stable_whisper.load_model('large')

        self.language_mapping = {
            'English': 'en',
            'Spanish': 'es',
            'French': 'fr',
            'German': 'de',
            'Italian': 'it',
            'Portuguese': 'pt',
            'Polish': 'pl',
            'Turkish': 'tr',
            'Russian': 'ru',
            'Dutch': 'nl',
            'Czech': 'cs',
            'Arabic': 'ar',
            'Chinese (Simplified)': 'zh',
            'Japanese': 'ja',
            'Hungarian': 'hu',
            'Korean': 'ko'
        }

    def extract_audio(self, video_file, output_audio_file):
        video_clip = VideoFileClip(video_file)
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(output_audio_file)
        audio_clip.close()

    def text_to_audio(self, text, start, end, language, user_id):
        try:

            audioclip = AudioSegment.from_file(f"{user_id}/output/audio/vocals.wav")
            audioclip = audioclip[start * 1000: end * 1000]
            audioclip.export(f"{user_id}/prom_say.wav", format="wav")

            self.tts.tts_to_file(text=text, speaker_wav=f"{user_id}/prom_say.wav", language=language, file_path=f"{user_id}/newspeak.wav", speed=4)

            AudioSegment.from_wav(f"{user_id}/newspeak.wav").export(f"{user_id}/newspeak.mp3", format="mp3")
        except:
            return False

    def convert_wav_to_mp3(self, input_wav, output_mp3):
        sound = AudioSegment.from_wav(input_wav)

        sound.export(output_mp3, format="mp3")

    def predict(self, video_file, target_language, save_folder, file_name, user_id):
        audio_file = f"{user_id}/audio.mp3"
        self.extract_audio(video_file, audio_file)
        result = self.model.transcribe(f"{user_id}/audio.mp3")
        result.to_tsv(f"{user_id}/audio.tsv")

        start, end, text = [], [], []
        tsv_file = open(f"{user_id}/audio.tsv")
        read_tsv = csv.reader(tsv_file, delimiter="\t")
        for row in read_tsv:
            if len(row) > 0:
                start.append(int(row[0]) / 1000)
                end.append(int(row[1]) / 1000)
                text.append(row[-1])

        d = {'start': start, 'end': end, 'start_train': start, 'end_train': end, 'text': text}
        df = pd.DataFrame(data=d)

        df = df[~df['text'].str.isupper()]

        target_language_code = self.language_mapping[target_language]
        if target_language_code == 'zh':
            fl = 'zh-CN'

            translator = GoogleTranslator(source='auto', target=fl)
        else:
            translator = GoogleTranslator(source='auto', target=target_language_code)

        data = df
        dt = data['text']
        translated_series = dt.apply(translator.translate)
        df['translated'] = translated_series

        os.system(f'spleeter separate -o "{user_id}/output/" "{user_id}/audio.mp3"')

        table = []
        for i in range(0, len(start)):
            table.append({
                'start': start[i],
                'end': end[i],
                'text': translator.translate(text[i])
            })

        all_sound = AudioSegment.from_file(f"{user_id}/audio.mp3", format="mp3")
        print(1)
        for i in tqdm(table):
            # print(i['text'])
            try:
                if self.text_to_audio(i["text"], i["start"], i["end"], target_language_code.lower(), user_id) == False:
                    assert 3 == 2  # en_speaker_3_long_wav файл с нашим текстом
            except:
                self.text_to_audio(translator.translate('ну'), i["start"], i["end"],
                              target_language_code.lower(), user_id)  # en_speaker_3_long_wav файл с нашим текстом

            new_replic = AudioSegment.from_file(f"{user_id}/newspeak.mp3", format="mp3")

            start = i["start"]
            end = i["end"]

            new_replic_len = new_replic.duration_seconds
            old_replic_len = end - start

            if old_replic_len < new_replic_len:
                # то ускоряем
                min_len = 0
                x0 = 1
                x = 2
                lr = 0.01
                accelerated_audio = new_replic.speedup(playback_speed=x0)
                while abs(accelerated_audio.duration_seconds - old_replic_len) >= 0.1 and x0 < x:
                    accelerated_audio = new_replic.speedup(playback_speed=x0)
                    x0 += lr
                accelerated_audio.export(f"{user_id}/itog.mp3", format="mp3")

            elif old_replic_len > new_replic_len:

                x0 = 1
                x = 0.5
                lr = 0.01
                current_audio_slow_down = ae.speed_down(new_replic, x0)
                while old_replic_len - current_audio_slow_down.duration_seconds >= -0.1:
                    current_audio_slow_down = ae.speed_down(new_replic, x0)
                    x0 -= lr
                current_audio_slow_down.export(f"{user_id}/itog.mp3", format="mp3")
            else:
                new_replic.export(f"{user_id}/itog.mp3", format="mp3")

            itog_new_sound = AudioSegment.from_file(f"{user_id}/itog.mp3", format="mp3")
            itog_new_sound_len = itog_new_sound.duration_seconds

            start_millisecond = int(round(start * 1000, 0))
            end_millisecond = int(round((start + itog_new_sound_len) * 1000, 0))

            sound_with_new_comment = all_sound[:start_millisecond] + itog_new_sound + all_sound[end_millisecond:]

            all_sound = sound_with_new_comment
        
        print(2)

        music_sound = AudioSegment.from_file(f"{user_id}/output/audio/accompaniment.wav", format="mp3")
        output = all_sound.overlay(music_sound, position=0)

        output.export(f"{user_id}/all_sound.mp3", format="mp3")

        print(3)

        # Пример использования
        input_wav = f"{user_id}/output/audio/vocals.wav"
        output_mp3 = f"{user_id}/vocals.mp3"

        self.convert_wav_to_mp3(input_wav, output_mp3)
        print(4)
        os.system(
            f'ffmpeg -i {user_id}/output/audio/accompaniment.wav -i {user_id}/all_sound.mp3 -filter_complex amix=inputs=2:duration=first:dropout_transition=3 {user_id}/output.mp3 -y')
        print(5)
        os.system(
            f'ffmpeg -i {video_file} -i {user_id}/output.mp3 -filter_complex "[0:a]volume=0.0[v0];[1:a]volume=2.0[v1];[v0][v1]amix=inputs=2:duration=first" -c:v copy -c:a aac -strict experimental {user_id}/final.mp4')
