from com.l2jserver.gameserver.handler import VoicedCommandHandler
from com.l2jserver.gameserver.handler import IVoicedCommandHandler

from com.l2jserver.gameserver.instancemanager import InstanceManager
from java.lang import System
from com.l2jserver.gameserver.network import SystemMessageId
from com.l2jserver.gameserver.network.serverpackets import SystemMessage

class vcInstanceZone(IVoicedCommandHandler):

	commands = ["即時地區"]
	
	def useVoicedCommand(self, command, player, params):
		world = InstanceManager.getInstance().getWorld(player.getInstanceId())
		if world and world.templateId >= 0:
			sm = SystemMessage.getSystemMessage(SystemMessageId.INSTANT_ZONE_CURRENTLY_INUSE_S1)
			sm.addInstanceName(world.templateId)
			player.sendPacket(sm)
		instanceTimes = InstanceManager.getInstance().getAllInstanceTimes(player.getObjectId())
		hasMessage = False
		if instanceTimes:
			for instanceId in instanceTimes.keySet():
				remainingTime = (instanceTimes.get(instanceId) - System.currentTimeMillis()) / 1000
				if remainingTime > 60:
					if not hasMessage:
						hasMessage = True
						player.sendPacket(SystemMessageId.INSTANCE_ZONE_TIME_LIMIT)
					hours = (int) (remainingTime / 3600)
					minutes = (int) ((remainingTime%3600) / 60)
					sm = SystemMessage.getSystemMessage(SystemMessageId.AVAILABLE_AFTER_S1_S2_HOURS_S3_MINUTES)
					sm.addInstanceName(instanceId)
					sm.addNumber(hours)
					sm.addNumber(minutes)
					player.sendPacket(sm)
				else:
					InstanceManager.getInstance().deleteInstanceTime(player.getObjectId(), instanceId)
		if not hasMessage:
			player.sendPacket(SystemMessageId.NO_INSTANCEZONE_TIME_LIMIT)
		return
			
	def getVoicedCommandList(self):
		return self.commands
		
	def __init__(self):
		VoicedCommandHandler.getInstance().registerHandler(self)
		print "vcInstanceZone registered"
		print "玩家可用 .即時地區"

vcInstanceZone()