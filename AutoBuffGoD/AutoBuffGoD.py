import sys
from com.l2jserver.gameserver.model.quest import State
from com.l2jserver.gameserver.model.quest import QuestState
from com.l2jserver.gameserver.model.quest.jython import QuestJython as JQuest

from com.l2jserver.gameserver.datatables import SkillTable
from com.l2jserver.gameserver.datatables import SpawnTable

from com.l2jserver.gameserver.model.actor.instance import L2PcInstance
from com.l2jserver.gameserver.network.serverpackets import ExShowScreenMessage
from com.l2jserver.gameserver.network import NpcStringId
from com.l2jserver.gameserver.util import Util


class AutoBuffGoD(JQuest):
	qID = -1
	qn = "AutoBuffGoD"
	qDesc = "custom"
	
	NPCID = [33454] #初學者幫手

	radius = 50 # 半徑
	
	blacklist = []
	
	def __init__(self, id = qID, name = qn, descr = qDesc):
		JQuest.__init__(self, id, name, descr)
		self.startQuestTimer("check", 1000, None, None, True)
		print self.qn + " loaded"

	def giveBuff(self, npc, player, skill_id, skill_lv):
		skill = SkillTable.getInstance().getInfo(skill_id, skill_lv)
		if skill:
			if skill.getSkillType() == L2SkillType.BUFF:
				skill.getEffects(npc, player)
			else:
				skill.useSkill(player, (player,))

	def giveBuffs(self, npc, player):
		def getBuffList(p):
			myBuffList = []
			isPet = not isinstance(p, L2PcInstance)
			if isPet:
				t = p.getOwner()
				if 6 <= t.getLevel() <= 75:
					myBuffList += [5627, 5628, 5637]
					myBuffList += [5633, 5634, 5635, 5636]
					myBuffList += [5629, 5630, 5631, 5632]
			else:
				t = p
				if t.getLevel() <= 75:
					myBuffList += [5627, 5628, 5637]
					if t.isMageClass():
						myBuffList += [5633, 5634, 5635, 5636]
					else:
						myBuffList += [5629, 5630, 5631, 5632]
				if 16 <= t.getLevel() <= 34:
					myBuffList += [4338]
			return myBuffList
				
		def check(p):
			if p.isDead(): return False
			if isinstance(p, L2PcInstance):
				if p.isInStoreMode() or p.isInCraftMode() or p.isFakeDeath() or not p.isOnline() or p.isFishing(): return False
			return True
			
		def process(target):
			if check(target):
				skills = getBuffList(target)
				for skillid in skills:
					self.giveBuff(npc, target, skillid, 1)
				if len(skills) > 0:
					#1600027	初學者助手對「$s1」施展了輔助魔法。					
					#essm = ExShowScreenMessage(NpcStringId.NEWBIE_HELPER_HAS_CASTED_BUFFS_ON_S1, 2, 5000) #stringid, position, duration
					essm = ExShowScreenMessage(NpcStringId.getNpcStringId(1600027), 2, 5000) #stringid, position, duration
					essm.addStringParameter(target.getName())
					target.sendPacket(essm)
				
		process(player)
		

	def onAdvEvent(self, event, npc, player):
		if event == "check":
			old_blacklist = self.blacklist[:]
			self.blacklist = []
			for spawn in SpawnTable.getInstance().getSpawnTable():
				if spawn.getNpcid() in self.NPCID:
					npc = spawn.getLastSpawn()
					for player in npc.getKnownList().getKnownPlayersInRadius(self.radius):
						playeroid = player.getObjectId()
						self.blacklist.append(playeroid)
						if playeroid not in old_blacklist:
							self.giveBuffs(npc, player)
					for player in npc.getKnownList().getKnownSummons().values():
						if Util.checkIfInRange(self.radius, npc, player, True):
							playeroid = player.getObjectId()
							self.blacklist.append(playeroid)
							if playeroid not in old_blacklist:
								self.giveBuffs(npc, player)

AutoBuffGoD()

