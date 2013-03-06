import sys
from com.l2jserver.gameserver.model.quest		import State
from com.l2jserver.gameserver.model.quest		import QuestState
from com.l2jserver.gameserver.model.quest.jython	import QuestJython as JQuest

from com.l2jserver.gameserver import Announcements
from com.l2jserver.gameserver.model.actor.instance import L2PcInstance

from com.l2jserver.gameserver.instancemanager import ZoneManager
from com.l2jserver.gameserver.model.zone.type import L2ScriptZone
from com.l2jserver.gameserver.model.zone.form import ZoneCylinder
from com.l2jserver.gameserver.model import L2World

class Quest(JQuest):
	qID = -1
	qn = "showQuestMovie101"
	qDesc = "custom"
	
	zone_id = 1234567
	
	def __init__(self, id = qID, name = qn, descr = qDesc):
		JQuest.__init__(self, id, name, descr)

		worldRegions = L2World.getInstance().getAllWorldRegions()
		self.zone = L2ScriptZone(self.zone_id)
		self.zone.setInstanceId(0)
		self.zone.setName("Fuck")
		self.zone.setZone(ZoneCylinder(-114359, 257451, -1200, -1100, 300))
		if ZoneManager.getInstance().checkId(self.zone_id):
			print "replace zone id:", self.zone_id
		ZoneManager.getInstance().addZone(self.zone_id, self.zone)

		for x in xrange(len(worldRegions)):
			for y in xrange(len(worldRegions[x])):
				ax = (x - L2World.OFFSET_X) << L2World.SHIFT_BY;
				bx = ((x + 1) - L2World.OFFSET_X) << L2World.SHIFT_BY;
				ay = (y - L2World.OFFSET_Y) << L2World.SHIFT_BY;
				by = ((y + 1) - L2World.OFFSET_Y) << L2World.SHIFT_BY;
				if self.zone.getZone().intersectsRectangle(ax, bx, ay, by):
					worldRegions[x][y].addZone(self.zone)
		self.addEnterZoneId(self.zone_id)
		print "Init:" + self.qn + " loaded"

	def onEnterZone(self, player, zonetype):
		if isinstance(player, L2PcInstance):
			st = player.getQuestState(self.qn)
			if not st:
				st = self.newQuestState(player)
				st.setState(State.STARTED)
			if not st.isCompleted():
				player.showQuestMovie(101)
				st.exitQuest(False)
		return JQuest.onEnterZone(self, player, zonetype)
		
Quest()
