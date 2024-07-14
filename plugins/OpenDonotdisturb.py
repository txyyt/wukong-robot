# -*- coding: utf-8-*-
from robot import config, logging
from robot.sdk.AbstractPlugin import AbstractPlugin

logger = logging.getLogger(__name__)

class Plugin(AbstractPlugin):

    def handle(self, text, parsed):
        self.say("勿扰模式已打开")
        config.set("/do_not_disturb", True)
        logger.info("进入勿扰模式")

    def isValid(self, text, parsed):
        return "打开勿扰模式" in text
