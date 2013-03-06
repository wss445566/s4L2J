import sys
from com.l2jserver.gameserver.model.quest		import State
from com.l2jserver.gameserver.model.quest		import QuestState
from com.l2jserver.gameserver.model.quest.jython	import QuestJython as JQuest
from com.l2jserver.gameserver.instancemanager import GlobalVariablesManager

qID = -1
qn = "Memo"
qDesc = "custom"

class Memo(JQuest):
	NPCID = [102] #觸發任務的 NPC 可修改.. 可以多 ID 例如 [100,102,103]
	max_lines = 15 #留言數目上限
	require_item = [[57,100000000]] #扣除道具 可多個 [[57,100000000], [5575, 1]], 或不扣道具 []
	read_reward_chance = 10000 * 5 #看留言版 獲得留言獎勵的機率 機率 1百萬 = 100%
	#獎品 [[道具ID,最少,最多,機率],[道具ID,最少,最多,機率]] 或 不獎 []... 機率 1百萬 = 100%
	reward_item = [[57,50000000,150000000,10000 * 1],[57,5000000,15000000,10000 * 50],[57,500000,1500000,10000 * 100]] 
	color_dict = dict({'白':'ffffff','紅':'ff0000','橙':'E0811B','黃':'FFFB00','綠':'00ff00','藍':'708DFF'})
	
	htm_header = "<html><body><title>留言版</title>"
	htm_input_text = "<table><tr><td><combobox width=35 var=color list=" + reduce(lambda a, b: a + ";" + b, color_dict.keys()) + "></td><td><multiedit var=\"value\" width=140 height=28></td><td><button value=\"留言扣一億\" width=80 height=20  action=\"bypass -h Quest " + qn + " add_Memo $color $value\"></td></tr></table>"
	htm_footer = "</body></html>"
	htm_not_enough_item = "<center>你沒有足夠道具, 無法留言<br1>需要道具<BR1>金幣:100000000</center>"
	htm_reward_rights_prompt = "<font color=\"ffaaaa\">現在留言 有機會獲得留言獎勵</font><BR1>"
	Memo = []
	def __init__(self, id, name, descr):
		JQuest.__init__(self, id, name, descr)
		for i in xrange(self.max_lines):
			self.Memo += [GlobalVariablesManager.getInstance().getStoredVariable('Memo'+str(i)) or ""]
		for id in self.NPCID:
			self.addStartNpc(id)
			self.addFirstTalkId(id)
			self.addTalkId(id)
		print "Init:" + qn + " loaded"

	def saveGlobalData(self):
		try:
			for i in xrange(self.max_lines):
				GlobalVariablesManager.getInstance().storeVariable('Memo'+str(i), self.Memo[i])
		except:
			print "save error"
		
	def onAdvEvent(self, event, npc, player):
		if event.startswith('add_Memo '):
			st = player.getQuestState(qn)
			for id, count in self.require_item:
				if st.getQuestItemsCount(id) < count: return self.htm_header + self.htm_not_enough_item + self.htm_footer
			for id, count in self.require_item:
				st.takeItems(id, count)
			color = event[9:10]
			memo = event[11:111]
			self.Memo = ["<font color=\""+self.color_dict[color]+"\">"+player.getName() + ":" + memo+"</font>"] + self.Memo[:self.max_lines]
			if st.getInt('reward') == 1:
				for id, minc, maxc, chance in self.reward_item:
					if self.getRandom(1000000) <= chance:
						st.giveItems(id, self.getRandom(maxc-minc)+minc)
		return self.onFirstTalk(npc, player)

	def getHtmMemo(self):
		r = ""
		for l in self.Memo:
			r += "" + l + "<br1>"
		return r
		
	def onFirstTalk(self, npc, player):
		st = player.getQuestState(qn)
		if not st:
			st = self.newQuestState(player)
			st.setState(State.STARTED)
		reward = ""
		if self.getRandom(1000000) <= self.read_reward_chance:
			st.set("reward", "1")
			reward = self.htm_reward_rights_prompt
		else:
			st.set("reward", "0")
		return self.htm_header + self.htm_input_text + reward + self.getHtmMemo() + self.htm_footer
		
Memo(qID, qn, qDesc)
