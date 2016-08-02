# Under MIT License, see LICENSE.txt

from datetime import datetime, timedelta

__author__ = 'RoboCupULaval'


class RecorderModel:
    def __init__(self):
        """
            RecorderModel
        """
        self.is_installed = False

        # === DATA ===
        self._data_frames = None
        self._cursor_pst = None
        self._nb_frame = None

        # === TIME ===
        self._time_lapse = timedelta(seconds=30)
        self._time_max = None
        self._time_min = None
        self._last_req_time = None

        # === CTRL ===
        self._ctrl_play = False

    # === INIT ===
    def init(self, data):
        """ Initialise le Recorder """
        self._init_time_var(data[-1][0])
        self._init_data(data)

    def _init_data(self, data):
        """ Initialise les paramètres de données """
        data = list(data)
        self._nb_frame = self._get_limit_frame_number(data)
        self._data_frames = data[self._nb_frame:]
        self._cursor_pst = self._nb_frame
        self._last_req_time = datetime.now()

    def _init_time_var(self, p_time):
        """ Initialise les paramètres de temps """
        self._time_max = p_time
        self._time_min = self._time_max - self._time_lapse

    # === GETTER / SETTER ===
    def _get_limit_frame_number(self, data):
        """ Récupère le nombre de frame en fonction du laps de temps """
        iterator = -1
        while True:
            try:
                if data[iterator][0] < self._time_min:
                    return iterator
            except IndexError:
                iterator += 1
                self._time_min = data[iterator][0]
                return iterator
            iterator -= 1

    # === PUBLIC METHOD ===
    def play(self):
        """ Met le Recorder en mode lecture """
        self._ctrl_play = True

    def pause(self):
        """ Met le Recorder en mode pause """
        self._ctrl_play = False

    def back(self):
        """ Recule le cursor d'un frame """
        index = self._cursor_pst - 1
        if index >= self._nb_frame:
            self._cursor_pst = index

    def rewind(self):
        """ Recule le cursor au début """
        self._cursor_pst = self._nb_frame

    def forward(self):
        """ Avance le curseur d'un frame """
        index = self._cursor_pst + 1
        if index <= -1:
            self._cursor_pst = index

    def skip_to(self, percentage):
        """ Met le Recorder une position spécifique """
        index = self._nb_frame - self._nb_frame * percentage / 100 - 1
        self._cursor_pst = int(index)

    def get_last_frame(self):
        """ Recupère le frame en fonction du curseur de lecture du Recorder """
        if not self._ctrl_play:
            self._last_req_time = datetime.now()
            return self._data_frames[self._cursor_pst][1]
        else:
            if self._cursor_pst == -1:
                self._last_req_time = datetime.now()
                return self._data_frames[-1][1]
            else:
                dt_frame = self._data_frames[self._cursor_pst + 1][0] - self._data_frames[self._cursor_pst][0]
                dt_get = datetime.now() - self._last_req_time
                if dt_get > dt_frame:
                    self._last_req_time = datetime.now()
                    self._cursor_pst += 1
                return self._data_frames[self._cursor_pst][1]

    def get_cursor_percentage(self):
        """ Recupère le pourcentage de frame """
        if self._cursor_pst is not None and self._nb_frame is not None:
            return 100 - self._cursor_pst / self._nb_frame * 100
        else:
            return 0