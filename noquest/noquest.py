from com.l2jserver.gameserver.model.quest.jython import QuestJython as JQuest

class Quest(JQuest):
	qID = -1
	qn = "no_quest_test"
	qDesc = "custom"
	
	NPCID = 100
	
	def __init__(self, id = qID, name = qn, descr = qDesc):
		self.qID, self.qn, self.qDesc = id, name, descr
		JQuest.__init__(self, id, name, descr)
		self.addStartNpc(self.NPCID)
		self.addFirstTalkId(self.NPCID)
		self.addTalkId(self.NPCID)
		print "%s loaded" % (self.qn,)

	def onFirstTalk(self, npc, player):
		print self.qn, npc, player, "[", self.getNoQuestMsg(player), "]"
		return self.getNoQuestMsg(player)

Quest()