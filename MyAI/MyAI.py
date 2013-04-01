import sys
from com.l2jserver.gameserver.ai import L2CharacterAI
from com.l2jserver.gameserver.model.actor.L2Character import AIAccessor
from com.l2jserver.gameserver.ai import CtrlIntention
from com.l2jserver.gameserver.model import L2CharPosition

npc29191 = 29191 #歐塔比斯
npc29192 = 29192 #歐塔比斯野獸

class MyAI29191(L2CharacterAI):#歐塔比斯
	horse = None
	def __init__(self, accessor):
		L2CharacterAI.__init__(self, accessor)
		
	def onEvtThink(self):
		if self.getIntention() == CtrlIntention.AI_INTENTION_ACTIVE:
			self.setIntention(CtrlIntention.AI_INTENTION_FOLLOW, self.getTarget())
		pass
	def onEvtAttacked(self, attacker):
		pass
	def onEvtCancel(self):
		pass
	def onEvtConfused(self, attacker):
		pass
	def onEvtFakeDeath(self):
		pass
	def onEvtForgetObject(self, object):
		pass
	def onEvtParalyzed(self, attacker):
		pass
	def onEvtRooted(self, attacker):
		pass	
	def onEvtSleeping(self, attacker):
		pass
	def onEvtStunned(self, attacker):
		pass
	def onEvtAttacked(self, attacker):
		pass
	#def onEvtArrived(self):
	#	print sys._getframe().f_code.co_name
	#	pass
		

class MyAI29192(L2CharacterAI):#歐塔比斯野獸
	runningCircleIndex = 0
	runningCircleSteps = 36
	radius = 500
	circlePoint = None
	npc = None
	def __init__(self, accessor):
		L2CharacterAI.__init__(self, accessor)
		self.npc = self.getActor()
		if self.npc.getNpcId() == npc29192:
			s = self.npc.getSpawn()
			self.circlePoint = self.plotCircle(s.getLocx(), s.getLocy(), self.radius, self.runningCircleSteps)
			self.onEvtThink()
		
	def onEvtArrived(self):
		if self.npc.getNpcId() == npc29192:
			x, y = self.circlePoint[self.runningCircleIndex]
			self.runningCircleIndex += 1
			if 0 < self.runningCircleIndex >= self.runningCircleSteps:
				self.runningCircleIndex = 0
			s = self.npc.getSpawn()
			self.setIntention(CtrlIntention.AI_INTENTION_MOVE_TO, L2CharPosition(x, y, s.getLocz(), s.getHeading()))
			self.npc.setRunning()
		
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
			npc.setAI(MyAI29191(AIAccessor(npc)))
			
		if npc.getNpcId() == npc29192:
			npc.setAI(MyAI29192(AIAccessor(npc)))
			s = npc.getSpawn()
			instid = s.getInstanceId()
			nextNpc = self.spawnNpc(npc29191, s.getLocx(), s.getLocy(), s.getLocz(), s.getHeading(), instid)
			if nextNpc:
				nextNpc.setRunning()
				nextNpc.setIsInvul(True)
				nextNpc.getAI().startFollow(npc)

			
	def spawnNpc(self, npcId, x, y, z, heading, instid):
		from com.l2jserver.gameserver.datatables import NpcTable
		from com.l2jserver.gameserver.model import L2Spawn
		from com.l2jserver.gameserver.datatables import SpawnTable
		npcTemplate = NpcTable.getInstance().getTemplate(npcId)
		npcSpawn = L2Spawn(npcTemplate)
		npcSpawn.setLocx(x)
		npcSpawn.setLocy(y)
		npcSpawn.setLocz(z)
		npcSpawn.setHeading(heading)
		npcSpawn.setAmount(1)
		npcSpawn.setInstanceId(instid)
		SpawnTable.getInstance().addNewSpawn(npcSpawn, False)
		npc = npcSpawn.doSpawn()
		#npc.setOnKillDelay(0)
		return npc
		
		
Quest()
