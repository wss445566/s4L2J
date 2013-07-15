from com.l2jserver.gameserver.model.quest.jython import QuestJython as JQuest
from com.l2jserver.gameserver.util import Util 

class Quest(JQuest):
	qID = -1 #腳本 ID, 自訂腳本 可用 -1
	qn = "partyDrop" #腳本名稱, 不能重覆就可以
	qDesc = "custom" #腳本類型 / 尋找腳本的 HTM 位置時用

	MOBSID = [22947,22948,22950,22956, 22957,23161]
	REWARD = [#[物品ID, 最少, 最多, 機率%]
	[57,1,100,50]
	,[57,2000,3000,99]
	]
	isSendMessage = False
	#isSendMessage = True

	def __init__(self, id = qID, name = qn, descr = qDesc):
		self.qID, self.qn, self.qDesc = id, name, descr #設定 qid, qn 及 qdesc (如果在腳本最下以  Quest(-1, "abc", "custom") 型色呼叫)
		JQuest.__init__(self, id, name, descr) #呼叫父
		for id in self.MOBSID:
			self.addKillId(id) #加入 那一個怪物的 ID 被殺會呼叫 這裡的 onKill
		print "%s loaded" % self.qn #初始化完成 GS 顯示訊息
		
	def sendMessage(self, player, message):
		if self.isSendMessage:
			player.sendMessage(message) #向玩家發出訊息
			
	def getIP(self, player):
		return player.getClient().getConnection().getInetAddress().getHostAddress()

	def onKill(self, npc, player, isPet): #當怪物被殺時 會被呼叫.. player 是尾刀殺怪的玩家
		party = player.getParty() #獲得尾刀玩家的隊伍
		if party: #如果有組隊情況
			members = [] #初始化 成員變數
			cc = party.getCommandChannel() #取得 聯軍 (如果有)
			if cc: #有聯軍
				members = cc.getMembers() #取得聯軍所有成員
			else: #沒有聯軍
				members = party.getMembers() #取得一般隊伍所有成員
			ipDict = {}
			for m in members:
				ipDict[self.getIP(m)] = ''
			if len(ipDict) != len(members):	#有組員的 IP 相同. 沒有特別獎勵
				return
			for m in members: #在 members 變數取出每個成員 M
				if Util.checkIfInRange(2000, player, m, False): #計算 成員 M 跟 尾刀玩家的距離 是否在 2000 單位以內
					for itemid, minc, maxc, c in self.REWARD:
						if self.getRandom(1000000) <= c*10000:
							m.addItem(self.qn, itemid, self.getRandom(minc, maxc), None, True)
				else: #距離不在 2000 單位以內
					self.sendMessage(player, "不在範圍 不掉特別獎勵") #向玩家發出訊息
		else: #如果沒有組隊情況
			self.sendMessage(player, "沒有隊伍 不掉特別獎勵") #向玩家發出訊息

Quest() #呼叫 Quest 的 __init__