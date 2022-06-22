import random
import sys
import threading
import time

from kivy.core.window import Window
from kivymd.color_definitions import colors
from kivy.lang import Builder
from kivymd.app import MDApp

import os
import pafy
import re, urllib.parse, urllib.request
os.add_dll_directory(r'C:\Program Files\VideoLAN\VLC')
import vlc


class MainApp(MDApp):

    def build(self):
        self.theme_cls.colors = colors
        self.theme_cls.primary_palette = "Purple"
        self.theme_cls.accent_palette = "Purple"
        self.theme_cls.accent_hue = "600"
        self.icon = 'carrot.png'
        self.title = 'GEZER'
        return Builder.load_string(screen)

    def on_start(self):
        self.media = vlc.MediaPlayer()
        file = open('Artists.txt')

        # read the content of the file opened
        self.artists = file.readlines()
        self.num_of_artists = len(self.artists)
        self.search_results = []
        self.stop_shuffling = True

    def ButtonAction_take_request(self, text_field):
        self.media.stop()
        self.stop_shuffling = True
        self.streamer = threading.Thread(target=lambda x: self.play(str(text_field.text), 0), args=(50,))
        self.streamer.start()

    def ButtonAction_shuffle(self):
        self.media.stop()
        if self.stop_shuffling:
            self.stop_shuffling = False
            self.shuffler = threading.Thread(target=lambda x: self.shuffle(), args=(50,))
            self.shuffler.start()

    def play(self, name, result_num):

        query_string = urllib.parse.urlencode({"search_query": name})
        format_url = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)
        self.search_results = re.findall(r"watch\?v=(\S{11})", format_url.read().decode())
        clip2 = "https://www.youtube.com/watch?v=" + "{}".format(self.search_results[result_num])
        video = pafy.new(clip2)
        video_name = video.title
        video_length = video.length
        video_link = video.getbestaudio()

        self.media = vlc.MediaPlayer(video_link.url)
        self.media.play()
        self.update_title(video_name)

        current_time = 0
        while current_time < video_length:
            if self.media.is_playing():
                time.sleep(0.1)
                current_time += 0.1
                self.root.ids.progress_bar.value = (100 * current_time / video_length)

            elif str(self.media.get_state()) == "State.Stopped" or self.media.get_state() == "State.Ended":
                break

    def shuffle(self):
        self.media.stop()

        artist_num = random.randint(0, self.num_of_artists - 1)
        name = self.artists[artist_num]

        query_string = urllib.parse.urlencode({"search_query": name})
        format_url = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)
        self.search_results = re.findall(r"watch\?v=(\S{11})", format_url.read().decode())

        result_num = random.randint(0, len(self.search_results) - 1)
        clip2 = "https://www.youtube.com/watch?v=" + "{}".format(self.search_results[result_num // 10])
        video = pafy.new(clip2)
        video_name = video.title
        video_link = video.getbestaudio()
        video_length = video.length
        self.update_title(video_name)
        self.media = vlc.MediaPlayer(video_link.url)
        self.media.play()

        current_time = 0.1
        while current_time < video_length:
            if self.media.is_playing():
                time.sleep(0.1)
                current_time += 0.1
                self.root.ids.progress_bar.value = (100 * current_time / video_length)

            elif str(self.media.get_state()) == "State.Stopped" or str(self.media.get_state()) == "State.Ended":
                break

        if not self.stop_shuffling:
            self.shuffle()

    def stop_streamer(self):
        self.media.stop()

    def pause_streamer(self):
        self.media.pause()

    def continue_streamer(self):
        self.media.play()

    def update_title(self, song_name):
        self.root.ids.song_name.text = song_name

    def close_app(self):
        sys.exit()


screen = """
<HoverButton@HoverBehavior+MDIconButton>

MDScreen:
    id: screen

    Image:
        source: "wallpaper.png"

    MDLabel:
        id: song_name
        text: ""
        pos_hint: {'center_x': 0.5, 'center_y': 0.65}
        halign: 'center'
        valign: 'center'
        font_style: "Overline"

    MDTextField:
        id: request_taker
        on_text_validate:   app.ButtonAction_take_request(self)
        mode: "fill"
        pos_hint: {'center_x': 0.5, 'center_y': 0.1}
        size_hint_x: None
        width: 400
        height: 50
        halign: 'center'
        valign: 'center'

    HoverButton:
        icon: "shuffle"
        on_release: app.ButtonAction_shuffle()
        pos_hint: {'center_x': 0.35, 'center_y': 0.75}
        theme_text_color: "Custom"
        on_enter:   self.text_color = app.theme_cls.primary_color
        on_leave:   self.text_color = "000000"

    HoverButton:
        icon: "play"
        on_release: app.continue_streamer()
        pos_hint: {'center_x': 0.45, 'center_y': 0.75}
        theme_text_color: "Custom"
        on_enter:   self.text_color = app.theme_cls.primary_color
        on_leave:   self.text_color = "000000"

    HoverButton:
        icon: "pause"
        on_release: app.pause_streamer()
        pos_hint: {'center_x': 0.55, 'center_y': 0.75}
        theme_text_color: "Custom"
        on_enter:   self.text_color = app.theme_cls.primary_color
        on_leave:   self.text_color = "000000"

    HoverButton:
        icon: "stop"
        on_release: app.stop_streamer()
        pos_hint: {'center_x': 0.65, 'center_y': 0.75}
        theme_text_color: "Custom"
        on_enter:   self.text_color = app.theme_cls.primary_color
        on_leave:   self.text_color = "000000"

    HoverButton:
        icon: "close-circle-outline"
        on_release: app.close_app()
        pos_hint: {'center_x': .925, 'center_y': 0.9}
        theme_text_color: "Custom"
        opacity: 0.2
        on_enter:   self.text_color = app.theme_cls.primary_color
        on_leave:   self.text_color = "000000"
    
    MDProgressBar:
        id: progress_bar
        value: 0
        color: app.theme_cls.accent_color
        pos_hint: {'center_x': .5, 'center_y': 0.59}
        size_hint_x: .4
"""

Window.size = (400, 300)
Window.icon = 'carrot.png'
Window.borderless = True
Window.top = 50
Window.left = 1450

MainApp().run()