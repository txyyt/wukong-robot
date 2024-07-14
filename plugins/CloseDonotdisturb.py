# -*- coding: utf-8-*-
from robot import config, logging
from robot.sdk.AbstractPlugin import AbstractPlugin

logger = logging.getLogger(__name__)

class Plugin(AbstractPlugin):

    def handle(self, text, parsed):
        config.set("/do_not_disturb", False)
        logger.info("关闭入勿扰模式")
        self.say("勿扰模式已关闭")

    def isValid(self, text, parsed):
        return "关闭勿扰模式" in text
