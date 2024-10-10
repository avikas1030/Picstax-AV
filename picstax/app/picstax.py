import os
from typing import List

from app.appstate import AppState
from app.av.processor import FFMpeg, Processor
from app.ml.cartoonify.filter import Cartoonify
from app.ml.filter import Filter
from app.view.layout import Layout

__temp_dir__ = "tmp"
__frames_dir__ = f'{__temp_dir__}/frames'


class PicStax:
    def __init__(self) -> None:
        super().__init__()
        self.app_state = AppState()
        self.uploaded_video = None
        self.layout = Layout()
        self.processor: Processor = FFMpeg(__frames_dir__)
        self.models: List[Filter] = []
        self.models.append(Cartoonify(self.layout, __frames_dir__))
        self.app_state.init_complete()

    def setup(self):
        if self.app_state.is_not_init():
            print("Should never reached here")
            raise Exception("App failed to initialized")
        if os.path.exists(__temp_dir__) and self.app_state.is_not_frames_extracted():
            os.system(f"rm -rf {__temp_dir__}")
        os.makedirs(__temp_dir__, exist_ok=True)
        self.app_state.setup_complete()

    def run(self):
        if self.app_state.is_not_setup():
            self.layout.show_warning(
                "Internal Error: App failed to initialized. Please refresh the page and try again.")
            return
        self._select_video()
        self._upload_selected_video()
        self._prompt_start()
        self._process_video()
        self._show_downloadable_video()

    def cleanup(self):
        if self.app_state.is_not_video_downloaded():
            return
        print("TODO: App complete, Do the cleanup here")

    def _select_video(self):
        self.layout.draw_navbar()
        self.uploaded_video = self.layout.video_file_selection_prompt()
        if self.uploaded_video is None:
            self.app_state.setup_complete()
        else:
            self.app_state.video_selected()

    def _upload_selected_video(self):
        if self.app_state.is_not_video_selected():
            self.layout.show_warning("Please upload a video file to get started")
            return

        self.layout.show_video_checkpoint("Video Uploaded Successfully!")
        file_name, extension = os.path.splitext(self.uploaded_video.name)
        self.outfile = f"{__temp_dir__}/{file_name}_cartoonify{extension}"
        print(f"Infile Name: {self.uploaded_video.name}, Outfile name: {self.outfile}")
        if os.path.exists(self.outfile):
            os.system(f"rm -f {self.outfile}")

        with open(f"{__temp_dir__}/{self.uploaded_video.name}", "wb") as tmp_file:
            tmp_file.write(self.uploaded_video.read())
            tmp_file.flush()
            self.infile = tmp_file.name

        self.app_state.video_uploaded()

    def _prompt_start(self):
        if self.app_state.is_not_video_uploaded():
            return
        self.layout.show_uploaded_video(self.uploaded_video)
        prompt = self.layout.show_start_button()
        if prompt:
            self.app_state.user_start_process()

    def _process_video(self):
        if self.app_state.is_not_user_start_process():
            return
        self.layout.load_spinner(self._convert_video)

    def _convert_video(self):
        self._extract_frames()
        self._apply_filters()
        self._assemble_video()
        return self.app_state.is_video_generated()

    def _extract_frames(self):
        if self.app_state.is_not_user_start_process():
            return
        self.layout.add_log("Extracting frames...")
        self.frames = self.processor.extract_frames(self.infile)
        self.app_state.frames_extracted()

    def _apply_filters(self):
        if self.app_state.is_not_frames_extracted():
            return
        self.layout.add_log("Applying filters...")
        for model in self.models:
            model.log_selection()
            for frame in self.frames:
                model.apply_filter(frame)
            model.log_completion()
        self.app_state.filters_passed()

    def _assemble_video(self):
        if self.app_state.is_not_filters_passed():
            return
        self.layout.add_log("Assembling video...")
        self.processor.assemble_output_video(self.outfile)
        self.app_state.video_generated()

    def _show_downloadable_video(self):
        if self.app_state.is_not_video_generated():
            return
        self.layout.add_log("Video generated successfully!")
        with open(self.outfile, 'rb') as f:
            video_file = f.read()
        self.layout.show_generated_video(video_file)
        self.layout.show_download_button(video_file, self.outfile)
        self.app_state.video_downloaded()
