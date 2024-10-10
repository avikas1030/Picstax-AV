import glob
import os
import subprocess
from abc import ABC, abstractmethod


class Processor(ABC):
    def __init__(self, frames_dir):
        self.frames_dir = frames_dir

    @abstractmethod
    def extract_frames(self, infile):
        pass

    @abstractmethod
    def assemble_output_video(self, outfile):
        pass


class FFMpeg(Processor):
    def __init__(self, frames_dir):
        super().__init__(frames_dir)

    def extract_frames(self, infile):
        os.makedirs(self.frames_dir, exist_ok=True)
        # os.system(f"ffmpeg -i {infile} -vf fps=1 {out_dir}/%d.png")
        subprocess.run(['ffmpeg', '-i', infile, f'{self.frames_dir}/frame%04d.png'])
        return glob.glob(f"{self.frames_dir}/*.png")

    def assemble_output_video(self, outfile):
        subprocess.run(['ffmpeg', '-r', '30', '-i', f'{self.frames_dir}/frame%04d.png', '-c:v', 'libx264', '-pix_fmt',
                        'yuva444p16le', outfile])
