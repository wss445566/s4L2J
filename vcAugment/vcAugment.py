import sys
from com.l2jserver.gameserver.handler import VoicedCommandHandler
from com.l2jserver.gameserver.handler import IVoicedCommandHandler
from com.l2jserver.gameserver.network.serverpackets import ExShowVariationCancelWindow
from com.l2jserver.gameserver.network.serverpackets import ExShowVariationMakeWindow

class VCAugment(IVoicedCommandHandler):

	commands = ["精煉"]
	
	def useVoicedCommand(self, command, player, params):
		player.sendPacket(ExShowVariationMakeWindow())
		player.sendPacket(ExShowVariationCancelWindow())
			
	def getVoicedCommandList(self):
		return self.commands
		
	def __init__(self):
		VoicedCommandHandler.getInstance().registerHandler(self)
		print "vcAugment registered"
		print "玩家可用 .精煉"

VCAugment()