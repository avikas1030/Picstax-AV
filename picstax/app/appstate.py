from enum import Enum


class AppState:
    class States(Enum):
        INVALID = -1
        INIT = 10
        SETUP = 20
        VIDEO_SELECTED = 30
        VIDEO_UPLOADED = 40
        USER_START_PROCESS = 50
        FRAMES_EXTRACT = 60
        FILTERS_PASSED = 70
        VIDEO_GENERATED = 80
        VIDEO_DOWNLOADED = 90

    def __init__(self) -> None:
        super().__init__()
        self.state = AppState.States.INVALID

    def __is_not_required_state__(self, min_state):
        return self.state.value < min_state.value

    def init_complete(self):
        self.state = AppState.States.INIT

    def is_not_init(self):
        return self.__is_not_required_state__(AppState.States.INIT)

    def setup_complete(self):
        self.state = AppState.States.SETUP

    def is_not_setup(self):
        return self.__is_not_required_state__(AppState.States.SETUP)

    def video_selected(self):
        self.state = AppState.States.VIDEO_SELECTED

    def is_not_video_selected(self):
        return self.__is_not_required_state__(AppState.States.VIDEO_SELECTED)

    def video_uploaded(self):
        self.state = AppState.States.VIDEO_UPLOADED

    def is_not_video_uploaded(self):
        return self.__is_not_required_state__(AppState.States.VIDEO_UPLOADED)

    def user_start_process(self):
        self.state = AppState.States.USER_START_PROCESS

    def is_not_user_start_process(self):
        return self.__is_not_required_state__(AppState.States.USER_START_PROCESS)

    def frames_extracted(self):
        self.state = AppState.States.FRAMES_EXTRACT

    def is_not_frames_extracted(self):
        return self.__is_not_required_state__(AppState.States.FRAMES_EXTRACT)

    def filters_passed(self):
        self.state = AppState.States.FILTERS_PASSED

    def is_not_filters_passed(self):
        return self.__is_not_required_state__(AppState.States.FILTERS_PASSED)

    def video_generated(self):
        self.state = AppState.States.VIDEO_GENERATED

    def is_not_video_generated(self):
        return self.__is_not_required_state__(AppState.States.VIDEO_GENERATED)

    def is_video_generated(self):
        return self.state.value >= AppState.States.VIDEO_GENERATED.value

    def video_downloaded(self):
        self.state = AppState.States.VIDEO_DOWNLOADED

    def is_not_video_downloaded(self):
        return self.__is_not_required_state__(AppState.States.VIDEO_DOWNLOADED)

