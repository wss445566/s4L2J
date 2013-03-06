from com.l2jserver.gameserver.model.quest.jython import QuestJython as JQuest
from com.l2jserver.gameserver.util import Util 

class Quest(JQuest):
	qID = -1 #腳本 ID, 自訂腳本 可用 -1
	qn = "partyDrop" #腳本名稱, 不能重覆就可以
	qDesc = "custom" #腳本類型 / 尋找腳本的 HTM 位置時用

	MOBID = 29068 #這個是地龍的 ID
	itemid = 1 #這個是 掉物品的 ID 不過 暫時用了 "hardcode" 所以 沒作用的
	itemcount = 1 #這個是 掉物品的數量 不過 暫時用了 "hardcode" 所以 沒作用的

	def __init__(self, id = qID, name = qn, descr = qDesc):
		self.qID, self.qn, self.qDesc = id, name, descr #設定 qid, qn 及 qdesc (如果在腳本最下以  Quest(-1, "abc", "custom") 形色呼叫)
		JQuest.__init__(self, id, name, descr) #呼叫父
		self.addKillId(self.MOBID) #加入 那一個怪物的 ID 被殺會呼叫 這裡的 onKill
		print "%s loaded" % self.qn #初始化完成 GS 顯示訊息

	def onKill(self, npc, player, isPet): #當怪物被殺時 會被呼叫.. player 是尾刀殺怪的玩家
		party = player.getParty() #獲得尾刀玩家的隊伍
		if party: #如果有組隊情況
			members = [] #初始化 成員變數
			cc = party.getCommandChannel() #取得 聯軍 (如果有)
			if cc: #有聯軍
				members = cc.getMembers() #取得聯軍所有成員
			else: #沒有聯軍
				members = party.getMembers() #取得一般隊伍所有成員
			for m in members: #在 members 變數取出每個成員 M
				if Util.checkIfInRange(2000, player, m, False): #計算 成員 M 跟 尾刀玩家的距離 是否在 2000 單位以內
					#m.addItem(self.qn, itemid, itemcount, null, True)
					m.addItem(self.qn, 1, 1, None, True) #直接增加物品到 M 成員的背包中.. 第1個參數是解發的參考名稱, 第二參數是 物品 ID,  第三 數量, 參考, 是否發訊息
					m.addItem(self.qn, 2, 1, None, True) #每增加一行 多掉一種物品.. 這裡 掉 六個
					m.addItem(self.qn, 3, 1, None, True)
					m.addItem(self.qn, 32272, 1, None, True)
					m.addItem(self.qn, 35704, 1, None, True)
					m.addItem(self.qn, 18549, 1, None, True)
				else: #距離不在 2000 單位以內
					player.sendMessage("不在範圍 不掉特別獎勵") #向玩家發出訊息
		else: #如果沒有組隊情況
			player.sendMessage("沒有隊伍 不掉特別獎勵") #向玩家發出訊息

Quest() #呼叫 Quest 的 __init__