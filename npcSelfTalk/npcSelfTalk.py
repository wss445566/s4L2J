import sys
from com.l2jserver.gameserver.model.quest import State
from com.l2jserver.gameserver.model.quest import QuestState
from com.l2jserver.gameserver.model.quest.jython import QuestJython as JQuest

from com.l2jserver.gameserver.util import Broadcast
from com.l2jserver.gameserver.network.serverpackets import NpcSay
from com.l2jserver.gameserver.network.clientpackets import Say2
from com.l2jserver.gameserver.network import NpcStringId
from com.l2jserver.gameserver.datatables import SpawnTable
from com.l2jserver.util import Rnd

selfTalkData = {
	30006:[[1811308]]
#	,33685:[[1801645]]
#	,NPCID:[[StringId-1]]
#	,NPCID:[[StringId-1],[StringId-2],[StringId-3]]
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
			delay = Rnd.get(15, 25)
			self.startQuestTimer("say_%d_%d" % (npcid, 0), 1000 * delay, None, None, False)
		print "%s loaded" % self.qn

	def onAdvEvent(self, event, npc, player):
		if event.startswith("say_"):
			dummy, npcid, index = event.split("_")
			npcid, index = int(npcid), int(index)
			allSpawn = SpawnTable.getInstance().getSpawnTable()
			for spawn in allSpawn:
				if npcid == spawn.getNpcid():
					self.myBroadcast(spawn.getLastSpawn(), selfTalkData[npcid][index][0])
			newindex = [index + 1, 0][index + 1 >= len(selfTalkData[npcid])]
			delay = Rnd.get(15, 25)
			self.startQuestTimer("say_%d_%d" % (npcid, newindex), 1000 * delay, None, None, False)

Quest()