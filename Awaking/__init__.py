from com.l2jserver.gameserver.model.quest.jython import QuestJython as JQuest
from com.l2jserver.gameserver.instancemanager import AwakingManager

class Quest(JQuest):
	qID = -1
	qn = "Awaking"
	qDesc = "custom"
	NPC = [33404,33397,33400,33402,33399,33398,33401,33403] #牧, 騎, 弓, 法, 匕, 鬥, 巫, 召
	data = {
	33404:[97,105,112]#牧
	,33397:[90,91,99,106]#騎
	,33400:[92,102,109,134]#弓
	,33402:[98,100,107,115,116,136]#法
	,33399:[93,101,108,117]#遊
	,33398:[88,89,113,114,118,131]#鬥
	,33401:[94,95,103,110,132,133]#巫
	,33403:[96,104,111]#召
	}
	
	def check(self, npc, player):
		if player.isAwaken():
			print "已覺醒"
			return False
		if player.getClassId().level() < 3:
			print "沒三轉"
			return False
		if not player.getClassId().getId() in self.data[npc.getNpcId()]:
			print "找錯NPC", npc.getNpcId(), player.getClassId().getId()
			return False
		i = player.getInventory().getAllItemsByItemId(17600)
		if len(i) == 0:
			print "缺道具 冥途之書"
			return False
		return True
	
	def __init__(self, id = qID, name = qn, descr = qDesc):
		self.qID, self.qn, self.qDesc = id, name, descr
		JQuest.__init__(self, id, name, descr)
		self.addFirstTalkId(self.NPC)
		self.addStartNpc(self.NPC)
		self.addTalkId(self.NPC)
		print "%s loaded" % self.qn

	def onFirstTalk(self, npc, player):
		if not self.check(npc, player):
			return "%d.htm" % (npc.getNpcId(),)
			return "<html><title></title><body>回去吧孩子 麥來亂(章大提供 XD)</body></html>"
		AwakingManager.getInstance().SendReqAwaking(player)

Quest()
