import sys
from com.l2jserver.gameserver.handler import VoicedCommandHandler
from com.l2jserver.gameserver.handler import IVoicedCommandHandler
from com.l2jserver.gameserver.model.entity import TvTEvent
from com.l2jserver.gameserver.instancemanager import MapRegionManager
from com.l2jserver.gameserver.instancemanager import GrandBossManager

class VCEscape(IVoicedCommandHandler):

	commands = ["²æ°k"]
	
	def useVoicedCommand(self, command, player, params):
		if player.isInCombat(): return
		if player.isDead(): return
		if player.isInOlympiadMode(): return
		if player.isFakeDeath(): return
		if player.isFishing(): return
		if player.isInStoreMode() or player.isInCraftMode(): return
		if not TvTEvent.onEscapeUse(player.getObjectId()): return
		if player.isAfraid(): return
		if player.isCombatFlagEquipped(): return
		if player.isInOlympiadMode(): return
		#if GrandBossManager.getInstance().getZone(player) != None and not player.isGM(): return
		if player.isFestivalParticipant(): return
		if player.isInJail(): return
		if player.isInDuel(): return
		
		loc = MapRegionManager.getInstance().getTeleToLocation(player, MapRegionManager.TeleportWhereType.Town)
		if loc:
			player.setInstanceId(0)
			player.setIsIn7sDungeon(False)
			player.teleToLocation(loc, True)
			
	def getVoicedCommandList(self):
		return self.commands
		
	def __init__(self):
		VoicedCommandHandler.getInstance().registerHandler(self)
		print "vcEscape registered"
		print "ª±®a¥i¥Î .²æ°k"

VCEscape()