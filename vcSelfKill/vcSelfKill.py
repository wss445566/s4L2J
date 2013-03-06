import sys
from com.l2jserver.gameserver.handler import VoicedCommandHandler
from com.l2jserver.gameserver.handler import IVoicedCommandHandler

class vcSelfKill(IVoicedCommandHandler):

	commands = ["自殺", "賜死", "selfkill"]
	
	def useVoicedCommand(self, command, player, params):
		player.setIsInvul(False)
		player.getStatus().reduceHp(99999999, player)
			
	def getVoicedCommandList(self):
		return self.commands
		
	def __init__(self):
		VoicedCommandHandler.getInstance().registerHandler(self)
		print "vcSelfKill registered"
		print "玩家可用 .自殺"

vcSelfKill()