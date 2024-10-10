import base64

import streamlit as st

__default_tab_title__ = 'PicStax Video Filters!'
__default_favicon__ = '📷'
__page_title__ = 'Cartoonify your video!'
__start_button_text__ = "Start Cartoonify"
__start_button_help_text__ = "Click here to see magic!"
__start_button_type__ = "primary"
__button_disabled_text__ = "Processing..."
__spinner_text__ = "Please wait while we process your video!"
__process_complete_text__ = "Your video is ready!"
__process_failed_text__ = "Failed to process the video!"


class Layout:
    def __init__(self, tab_title=__default_tab_title__, favicon=__default_favicon__) -> None:
        super().__init__()
        st.set_page_config(page_title=tab_title, page_icon=favicon, layout='wide')
        self.title = st.empty()
        self.file_uploader = st.empty()
        self.warning = st.empty()
        self.video_upload_checkpoint = st.empty()
        self.upload_col, self.button_col, self.generated_col = st.columns(3)
        with self.upload_col:
            self.uploaded_video = st.empty()
        with self.button_col:
            self.start_button = st.empty()
            self.spinner = st.spinner(__spinner_text__)
            self.logs_window = st.container()
        with self.generated_col:
            self.generated_video = st.empty()
            self.download_button = st.empty()

    def draw_navbar(self):
        self.title.empty()
        self.title.title(__page_title__)

    def video_file_selection_prompt(self, on_change=None):
        self.file_uploader.empty()
        self.file_uploader.info("Upload a video file to get started")
        return self.file_uploader.file_uploader("Choose an video file to cartoonify", type=["mp4", "mkv", "mov"],
                                                on_change=on_change)

    def show_warning(self, warning_message):
        self.warning.empty()
        self.video_upload_checkpoint.empty()
        self.warning.warning(warning_message)

    def show_video_checkpoint(self, message):
        self.warning.empty()
        self.video_upload_checkpoint.empty()
        self.video_upload_checkpoint.success(message)

    def show_uploaded_video(self, uploaded_video):
        self._clear_cols()
        self.uploaded_video.video(uploaded_video)

    def _clear_cols(self):
        self.uploaded_video.empty()
        self.start_button.empty()
        self.generated_video.empty()
        self.download_button.empty()

    def show_start_button(self):
        self.start_button.empty()
        return self.start_button.button(__start_button_text__, type=__start_button_type__,
                                        help=__start_button_help_text__)

    def load_spinner(self, task, *arg, **kwargs):
        self.start_button.empty()
        self.start_button.button(__button_disabled_text__, disabled=True)
        with self.button_col:
            with self.spinner:
                result = task(*arg, **kwargs)
        if result:
            self.start_button.empty()
            self.start_button.success(__process_complete_text__)
        else:
            self.start_button.empty()
            self.start_button.error(__process_failed_text__)
        return result

    def add_log(self, log):
        self.logs_window.write(log)

    def log_filter_selection(self, filter_name):
        self.logs_window.write(f"  - Selected Filter: {filter_name}")

    def log_filter_completion(self, filter_name):
        self.logs_window.write(f"  - Filter {filter_name} applied successfully!")

    def show_generated_video(self, outfile):
        self.generated_video.empty()
        self.generated_video.video(outfile)

    @staticmethod
    def _get_video_download_link(outfile, download_filename):
        b64 = base64.b64encode(outfile).decode()
        href = f'<a href="data:file/mp4;base64,{b64}" download="{download_filename}">Download video file</a>'
        return href

    def show_download_button(self, outfile, filename):
        self.download_button.empty()
        self.download_button.markdown(self._get_video_download_link(outfile, filename), unsafe_allow_html=True)
