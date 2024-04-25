from pathlib import Path
from typing import Dict
import demucs.api
import demucs.audio
import os
import argparse
import time
from mutagen.mp3 import MP3

def stem_path_from_source_path(audio_file_path: Path, output_folder: Path, stem: str) -> Path:
    return Path(output_folder) / Path(audio_file_path.stem + "-" + stem + ".mp3")

def stems_dict_from_source_path(audio_file_path: Path, output_folder: Path) -> Dict[str, Path]:
    stems_dict = {}
    for stem in ["vocals", "drums", "bass", "other"]:
        stems_dict[stem] = stem_path_from_source_path(audio_file_path, output_folder, stem)
    return stems_dict

def separate_stems(audio_file_path: Path, output_folder:Path) -> Dict[str,Path]: 
    
    stems = stems_dict_from_source_path(audio_file_path, output_folder)
    if os.path.exists(stems["vocals"]):
        print(f"Stems already exist for '{stems['vocals']}' so no stem separation will be performed -- delete the stems if you want to re-run the separation")
        return stems
    else:
        print(f"Stems file '{stems['vocals']}' does not exist so stem separation will be performed")
    
    separator = demucs.api.Separator()
    print(f"Loading model")
    #separator.load_model(model='mdx_extra')
    separator.load_model(model='htdemucs')
    print(f"Loading audio into model")
    separator.load_audios_to_model(audio_file_path)
    
    print(f"Separating audio into stems")
    separated = separator.separate_loaded_audio()
    
    start_time = time.perf_counter()
    print(f"start time is {start_time}")
    for file, sources in separated:
        for stem, source in sources.items():
            print(f"Saving stem file '{stems[stem]}'")
            demucs.audio.save_audio(source, stems[stem], samplerate=separator._samplerate)
    end_time = time.perf_counter()
    print(f"end time is {end_time}")
    
    # Calculate stemming time
    stemming_time = end_time - start_time
    print(f"Stemming process took {stemming_time:.2f} seconds")
    
    # Get MP3 duration using mutagen
    audio = MP3(audio_file_path)
    duration = audio.info.length
    print(f"Audio duration is {duration:.2f} seconds")
        
    print(f"Stemming took {stemming_time/duration:.2%} of the audio duration")
    
    return stems

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Separate audio into stems using Demucs')
    parser.add_argument('--mp3', type=str, required=True, help='Path to the source MP3 file')
    parser.add_argument('--output', type=str, default='output', help='Output directory for the separated stems (default: output)')
    args = parser.parse_args()

    audio_file_path = Path(args.mp3)
    output_folder = Path(args.output)

    if not output_folder.exists():
        os.makedirs(output_folder)

    separate_stems(audio_file_path, output_folder)
