from com.l2jserver.gameserver.ai import L2CharacterAI
from com.l2jserver.gameserver.model.actor.L2Character import AIAccessor
from com.l2jserver.gameserver.ai import CtrlIntention
from com.l2jserver.gameserver.model import L2CharPosition

npc29191 = 29191 #歐塔比斯
npc29192 = 29192 #歐塔比斯野獸

class MyAI(L2CharacterAI):
	runningCircleIndex = 0
	runningCircleSteps = 36
	radius = 1000
	circlePoint = None
	def __init__(self, accessor):
		L2CharacterAI.__init__(self, accessor)
		npc = self.getActor()
		if npc.getNpcId() == npc29192:
			s = npc.getSpawn()
			self.circlePoint = self.plotCircle(s.getLocx(), s.getLocy(), self.radius, self.runningCircleSteps)
			self.onEvtThink()
		
	def onEvtAttacked(self, attacker):
		pass
		
	def onEvtArrived(self):
		pass
		
	def onEvtArrived(self):
		npc = self.getActor()
		if npc.getNpcId() == npc29192:
			x, y = self.circlePoint[self.runningCircleIndex]
			self.runningCircleIndex += 1
			if 0 < self.runningCircleIndex >= self.runningCircleSteps:
				self.runningCircleIndex = 0
			s = npc.getSpawn()
			self.setIntention(CtrlIntention.AI_INTENTION_MOVE_TO, L2CharPosition(x, y, s.getLocz(), s.getHeading()))
			npc.setRunning()
		
	def onEvtThink(self):
		self.onEvtArrived()

	def plotCircle(self, x, y, r, steps):
		import math
		ret = []
		anginc = math.pi * 2 / steps
		ang = 0
		for step in xrange(steps):
			ang += anginc
			xx = r * math.cos(ang)
			yy = r * math.sin(ang)
			ret += [(int(xx + x), int(yy + y))]
		return ret

from com.l2jserver.gameserver.model.quest.jython import QuestJython
		
class Quest(QuestJython):
	qID = -1
	qn = "MyAI"
	qDesc = "custom"
	
	def __init__(self, id=qID, name=qn, descr=qDesc):
		qID, qn, qDesc = id, name, descr
		QuestJython.__init__(self, id, name, descr)
		self.addSpawnId(npc29191)
		self.addSpawnId(npc29192)
		print "Init:" + self.qn + " loaded"

	def onSpawn(self, npc):
		if npc.getNpcId() == npc29191:
			pass
		if npc.getNpcId() == npc29192:
			npc.setAI(MyAI(AIAccessor(npc)))
		
		
Quest()
