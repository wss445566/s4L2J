from com.l2jserver.gameserver.handler import VoicedCommandHandler
from com.l2jserver.gameserver.handler import IVoicedCommandHandler

from com.l2jserver.gameserver import Announcements

class VCPlayerAnno(IVoicedCommandHandler):
	isCritical = True #是否為重要公告形式顯示

	commands = ["公告"]
	
	def useVoicedCommand(self, command, player, params):
		Announcements.getInstance().announceToAll("%s:%s" % (player.getName(), params), self.isCritical)
			
	def getVoicedCommandList(self):
		return self.commands
		
	def __init__(self):
		VoicedCommandHandler.getInstance().registerHandler(self)
		print "vcPlayerAnno registered"
		print "玩家可用 .公告"

VCPlayerAnno()
