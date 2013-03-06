import sys
from com.l2jserver.gameserver.model.quest		import State
from com.l2jserver.gameserver.model.quest		import QuestState
from com.l2jserver.gameserver.model.quest.jython	import QuestJython as JQuest

from com.l2jserver.gameserver import Announcements
from com.l2jserver.gameserver.model.actor.instance import L2PcInstance

from com.l2jserver.gameserver.instancemanager import ZoneManager
from com.l2jserver.gameserver.model.zone.type import L2BossZone
from com.l2jserver.gameserver.model.zone.form import ZoneNPoly
from com.l2jserver.gameserver.model import L2World

class Valakas_fix(JQuest):
	qID = -1
	qn = "Valakas_fix"
	qDesc = "custom"
	
	zone_hell_id = 9999999
	valakas_zone_id = 12010
	
	def __init__(self, id = qID, name = qn, descr = qDesc):
		JQuest.__init__(self, id, name, descr)
		worldRegions = L2World.getInstance().getAllWorldRegions()
		self.zone_hell = L2BossZone(self.zone_hell_id)
		aX, aY = [196866,229289,229176,196880],[-130845,-130860,-98508,-98498]
		minZ = -22572
		maxZ = -2637
		self.zone_hell.setZone(ZoneNPoly(aX, aY, minZ, maxZ))
		self.zone_hell.setName("Valakas Hell")
		self.zone_hell.setParameter("default_enabled", "false")
		ZoneManager.getInstance().addZone(self.zone_hell_id, self.zone_hell)

		for x in xrange(len(worldRegions)):
			for y in xrange(len(worldRegions[x])):
				ax = (x - L2World.OFFSET_X) << L2World.SHIFT_BY;
				bx = ((x + 1) - L2World.OFFSET_X) << L2World.SHIFT_BY;
				ay = (y - L2World.OFFSET_Y) << L2World.SHIFT_BY;
				by = ((y + 1) - L2World.OFFSET_Y) << L2World.SHIFT_BY;
				if self.zone_hell.getZone().intersectsRectangle(ax, bx, ay, by):
					worldRegions[x][y].addZone(self.zone_hell)
		self.addEnterZoneId(self.zone_hell_id)
		print "Init:" + self.qn + " loaded"

	def onEnterZone(self, player, zonetype):
		if isinstance(player, L2PcInstance):
			vz = ZoneManager.getInstance().getZoneById(self.valakas_zone_id)
			vz.allowPlayerEntry(player, 30)
			player.teleToLocation(211042,-113579,-1600)
		return JQuest.onEnterZone(self, player, zonetype)
		
Valakas_fix()
