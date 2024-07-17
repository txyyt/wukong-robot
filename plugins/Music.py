# -*- coding: utf-8-*-
import os
import requests
from robot import config, logging
from robot.Player import MusicPlayer
from robot.sdk.AbstractPlugin import AbstractPlugin

logger = logging.getLogger(__name__)

class Plugin(AbstractPlugin):

    IS_IMMERSIVE = True  # 这是个沉浸式技能

    def __init__(self, con):
        super(Plugin, self).__init__(con)
        self.player = None
        self.song_name = None

    def get_song_id(self, song_name):
        search_url = "http://music.163.com/api/search/get/web"
        params = {
            "csrf_token": "",
            "hlpretag": "",
            "hlposttag": "",
            "s": song_name,
            "type": 1,
            "offset": 0,
            "total": "true",
            "limit": 1
        }
        response = requests.get(search_url, params=params)
        result = response.json()
        if result['code'] == 200 and result['result']['songs']:
            song_id = result['result']['songs'][0]['id']
            logger.info(f"歌曲名称: {song_name}, 歌曲ID: {song_id}")
            return song_id
        else:
            logger.warning(f"未找到歌曲: {song_name}")
            return None

    def get_song_url(self, song_id):
        return f"http://music.163.com/song/media/outer/url?id={song_id}.mp3"

    def init_music_player(self, song_url):
        return MusicPlayer([song_url], self)

    def handle(self, text, parsed):
        # 提前处理停止播放命令
        if "停止播放" in text:
            if self.player:
                self.player.stop()
                self.clearImmersive()  # 去掉沉浸式
                self.say('音乐播放已停止')
            else:
                self.say('当前没有播放任何音乐')
            return

        if self.song_name is None:
            if "播放音乐" in text:
                self.song_name = text.split("播放音乐")[-1].strip().lstrip("，").rstrip("。")
                song_id = self.get_song_id(self.song_name)
                if song_id:
                    song_url = self.get_song_url(song_id)
                    self.player = self.init_music_player(song_url)
                    self.player.play()
                    self.song_name = None
                else:
                    self.say(f"抱歉，我找不到歌曲 {self.song_name}")
                    self.song_name = None
            else:
                self.say("请告诉我你想听的歌曲名称。")
        else:
            if self.player:
                if self.nlu.hasIntent(parsed, 'CHANGE_TO_NEXT'):
                    self.player.next()
                elif self.nlu.hasIntent(parsed, 'CHANGE_TO_LAST'):
                    self.player.prev()
                elif self.nlu.hasIntent(parsed, 'CHANGE_VOL'):
                    slots = self.nlu.getSlots(parsed, 'CHANGE_VOL')
                    for slot in slots:
                        if slot['name'] == 'user_d':
                            word = self.nlu.getSlotWords(parsed, 'CHANGE_VOL', 'user_d')[0]
                            if word == '--HIGHER--':
                                self.player.turnUp()
                            else:
                                self.player.turnDown()
                            return
                        elif slot['name'] == 'user_vd':
                            word = self.nlu.getSlotWords(parsed, 'CHANGE_VOL', 'user_vd')[0]
                            if word == '--LOUDER--':
                                self.player.turnUp()
                            else:
                                self.player.turnDown()
                elif self.nlu.hasIntent(parsed, 'PAUSE'):
                    self.player.pause()
                elif self.nlu.hasIntent(parsed, 'CONTINUE'):
                    self.player.resume()
                else:
                    self.say('没听懂你的意思呢，要停止播放，请说停止播放')
                    self.player.resume()
            else:
                self.say('请先播放一首歌曲')

    def pause(self):
        if self.player:
            logger.info("pause")
            self.player.pause()

    def restore(self):
        if self.player and self.player.is_pausing():
            logger.info("restore")
            self.player.resume()

    def isValidImmersive(self, text, parsed):
        return any(self.nlu.hasIntent(parsed, intent) for intent in ['CHANGE_TO_LAST', 'CHANGE_TO_NEXT', 'CHANGE_VOL', 'CLOSE_MUSIC', 'PAUSE', 'CONTINUE', 'STOP_PLAYING'])

    def isValid(self, text, parsed):
        return text.startswith("播放音乐")
