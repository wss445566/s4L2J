import sys
from com.l2jserver.gameserver.model.quest		import State
from com.l2jserver.gameserver.model.quest		import QuestState
from com.l2jserver.gameserver.model.quest.jython	import QuestJython as JQuest

from com.l2jserver.gameserver.util import Broadcast
from com.l2jserver.gameserver.network.serverpackets import NpcSay
from com.l2jserver.gameserver.network.clientpackets import Say2
from com.l2jserver.gameserver.network import NpcStringId
from com.l2jserver.gameserver.datatables import SpawnTable


selfTalkData = {
	32975:[[1811294, 10]
		,[1811294, 12]
		,[1811294, 7]]
	,33025:[[1032340, 10]
		,[1032341, 13]
		,[1032342, 6]
		,[1032340, 11]
		,[1032341, 12]
		,[1032342, 9]
		,[1032340, 10]
		,[1032341, 12]
		,[1032342, 11]]
	,33026:[[1032319, 10]
		,[1032320, 7]
		,[1032321, 11]
		,[1032319, 12]
		,[1032320, 10]
		,[1032321, 12]
		,[1032319, 5]
		,[1032320, 10]
		,[1032321, 11]]
	,33229:[[1032318, 10]
		,[1032318, 11]
		,[1032318, 8]]
	,33271:[[1811245, 10]
		,[1811245, 7]
		,[1811245, 13]]
	,33284:[[1811248, 10]
		,[1811248, 6]
		,[1811248, 12]]
	,33285:[[1811247, 10]
		,[1811247, 8]
		,[1811247, 12]]
	,33487:[[11021702, 10]
		,[11021704, 11]
		,[11021706, 12]
		,[11021708, 10]
		,[11021702, 6]
		,[11021704, 12]
		,[11021706, 10]
		,[11021708, 11]
		,[11021702, 7]
		,[11021704, 10]
		,[11021706, 10]
		,[11021708, 11]]
}

class Quest(JQuest):
	qID = -1
	qn = "npcSelfTalk"
	qDesc = "custom"
	
	def myBroadcast(self, npc, npcstring):
		for player in npc.getKnownList().getKnownPlayers().values():
			if npc.isInsideRadius(player, 1000, False, False):
				player.sendPacket(NpcSay(npc.getObjectId(), Say2.NPC_SAY, npc.getNpcId(), NpcStringId.getNpcStringId(npcstring)))

	def __init__(self, id = qID, name = qn, descr = qDesc):
		self.qID, self.qn, self.qDesc = id, name, descr
		JQuest.__init__(self, id, name, descr)
		for npcid in selfTalkData:
			delay = selfTalkData[npcid][0][1]
			self.startQuestTimer("say_%d_%d" % (npcid, 0), 1000 * delay, None, None, False)
		print "%s loaded" % self.qn

	def onAdvEvent(self, event, npc, player):
		if event.startswith("say_"):
			dummy, npcid, index = event.split("_")
			npcid, index = int(npcid), int(index)
			for spawn in SpawnTable.getInstance().getSpawnTable():
				if npcid == spawn.getNpcid():
					self.myBroadcast(spawn.getLastSpawn(), selfTalkData[npcid][index][0])
			newindex = [index + 1, 0][index + 1 >= len(selfTalkData[npcid])]
			delay = selfTalkData[npcid][index][1]
			self.startQuestTimer("say_%d_%d" % (npcid, newindex), 1000 * delay, None, None, False)
			

Quest()			
			
			
			