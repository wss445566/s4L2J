import sys
from com.l2jserver.gameserver.model.quest		import State
from com.l2jserver.gameserver.model.quest		import QuestState
from com.l2jserver.gameserver.model.quest.jython	import QuestJython as JQuest

from com.l2jserver.gameserver.datatables		import ExperienceTable	#經驗值表
from com.l2jserver.gameserver.datatables		import SkillTable	#技能相關
from com.l2jserver.gameserver.network.serverpackets	import NpcHtmlMessage	#對話框

qID = -1		#任務 ID
qn = "Rebirth"		#任務名
qDesc = "custom"	#任務簡介/通常用於搜尋 htm 的資料夾位置 /gameserver/data/script/*****/*.htm

NPCID = [100]		#觸發的 NPC template ID, 可多個 NPC [65535, 88888, 99999]
maxRebirthTimes = 99	#最多轉生次數
maxRebirthPoint = 6		#素質獎勵上限
requireLevel = 85		#轉生要求等級
requireItem = [[57, 10000]]	#轉生要求道具及數量 [[物ID, 數量], [物ID, 數量], [物ID, 數量]] 或 [] 沒有

rewardItem = [[57, 123],[57,456]]	#轉生後獎勵道具及數量 [[物ID, 數量], [物ID, 數量], [物ID, 數量]] 或 [] 沒有
levelAfterRebirth = 85		#轉生後等級

baseClassID = [0, 10, 18, 25, 31, 38, 44, 49, 53, 123, 124, 135] #各種族的基本 classID + 戰鬥巡官 id 135

#素質獎勵用技能
skillSTR = 7033		#力量
skillDEX = 7034		#敏捷
skillCON = 7035		#體質
skillINT = 7036		#智力
skillWIT = 7037		#智慧
skillMEN = 7038		#精神
sixStatSkills = [skillSTR, skillDEX, skillCON, skillINT, skillWIT, skillMEN]
#用作提升素質時的下拉式選單
sixStatName = ['力量', '敏捷', '體質', '智力', '智慧', '精神']

remove_skill_blacklist = [5995,5996,5997,5998,5999,6000,6001,6002,6003,6004,6005,6006,6007,6008,6009,6010,6011,6012,6013,6014,6015,6016,6017,6018,6025,6026,6027]

class Rebirth(JQuest):
	def __init__(self, id, name, descr):
		JQuest.__init__(self, id, name, descr)

	#取得可用的轉生點
	def getFreeRebirthPoint(self, player):
		usedPoint = 0
		for s in sixStatSkills:
			usedPoint += max(player.getSkillLevel(s), 1) -1
		st = player.getQuestState(qn)
		return min(st.getInt('times') - usedPoint, max(maxRebirthPoint - usedPoint, 0))
	def onAdvEvent(self, event, npc, player):
		#檢測轉生條件
		def check_rebirth_requirement(player):
			#檢測轉生要求等級
			if player.getLevel() < requireLevel: return False
			st = player.getQuestState(qn)
			#檢測轉生要求道具及數量
			for id, count in requireItem:
				if st.getQuestItemsCount(id) < count: return False
			#檢測轉生次數
			if st.getInt('times') >= maxRebirthTimes: return False
			#限制副職業不能轉生
			if player.isSubClassActive(): return False
			#檢測素質等級不能多於51
			sixStatId = st.getInt('newSixStat')
			if player.getSkillLevel(sixStatId) >= 51: return False
			#全部檢測通過
			return True
		#執行轉生
		def doRebirth(player):
			st = player.getQuestState(qn)
			#扣除道具
			for id, count in requireItem:
				st.takeItems(id, count)
			#降等
			player.removeExpAndSp(player.getExp() - ExperienceTable.getInstance().getExpForLevel(levelAfterRebirth), player.getSp())
			#記錄轉生次數
			st.set('times', str(st.getInt('times')+1))
			#移除技能
			for i in player.getAllSkills():
				if i.getId() not in sixStatSkills:
					if i.getId() not in remove_skill_blacklist:
						player.removeSkill(i)
			#轉種族
			newClass = st.getInt('newClass')
			st.getPlayer().setClassId(newClass)
			if player.isSubClassActive():
				player.getSubClasses().get(player.getClassIndex()).setClassId(player.getActiveClass())
			else:
				player.setBaseClass(player.getActiveClass())
			#st.getPlayer().setBaseClass(newClass)
			#st.getPlayer().setActiveClass(newClass)
			player.broadcastUserInfo()
			player.rewardSkills()
			player.sendSkillList()
			#player.stopAllToggles()
			#player.broadcastUserInfo()
			#變身..用作暫時解決轉種族後人物怪怪的問題
			#變身 瑪瑙獸 ID 617
			skillId = 617
			skillLevel = 1
			skill = SkillTable.getInstance().getInfo(skillId, skillLevel)
			if skill:
				skill.getEffects(player, player)
				#5秒後解除變身
				st.startQuestTimer('removeAllEffects', 5000)
				#player.untransform()
			#發道具獎勵
			for id, count in rewardItem:
				st.giveItems(id, count)
			#發素質獎勵
			if self.getFreeRebirthPoint(player) > 0:
				skillId = st.getInt('newSixStat')
				skillLevel = max(player.getSkillLevel(skillId), 1)
				player.addSkill(SkillTable.getInstance().getInfo(skillId, skillLevel + 1), True)
			return
		try:
			nEvent = int(event)
		except:
			nEvent = -1
		#顯示 轉生狀態畫面
		if event == 'request_info':
			return 'info.htm'
		#執行重設轉生素質
		elif event == 'request_reset_sixstat':
			#移除六大素質技能
			for i in player.getAllSkills():
				if i.getId() in sixStatSkills:
					player.removeSkill(i)
			return 'info.htm'
		#顯示設定轉生素質獎勵對話
		elif event == 'request_set_sixstat':
			return 'setSixStat.htm'
		#顯示 選擇新種族畫面
		elif event == 'request_choice_class':
			return 'choiceClass.htm'
		#記錄 新種族 及 下一步
		elif nEvent in baseClassID:
			st = player.getQuestState(qn)
			#記錄新種族
			st.set('newClass', event)
			return "choiceSixStat.htm"
		#記錄 轉生素質獎勵 及 下一步
		elif nEvent in sixStatSkills:
			st = player.getQuestState(qn)
			#記錄新素質要求
			st.set('newSixStat', event)
			return "confirm.htm"
		#確定要求轉生
		elif event == "request_rebirth":
			if check_rebirth_requirement(player):
				doRebirth(player)
				return "rebirth_ok.htm"
			else:
				return "rebirth_fail.htm"
		#移除所有狀態
		elif event == 'removeAllEffects':
			for e in player.getAllEffects():
				e.exit()
		#設定六大素質
		elif event.split()[0] == 'require_sixstat_add':
			try:
				c, n, v = event.split()
				v = max(int(v), 0)
				i = sixStatName.index(n)
			except:
				print qn + ":錯誤 event:" + event
				return ""
			newV = max(player.getSkillLevel(sixStatSkills[i]), 1) + v
			needPoint = v
			if needPoint == 0 or newV >= 51 or self.getFreeRebirthPoint(player) < needPoint or player.isSubClassActive():
				return "setSixStatFail.htm"
			else:
				skillId = sixStatSkills[i]
				skillLevel = newV
				player.addSkill(SkillTable.getInstance().getInfo(skillId, skillLevel), True)
			return "info.htm"
		else:
			print qn + ":不明的要求:" + event
			return ""
		return

	def onFirstTalk(self, npc, player):
		st = player.getQuestState(qn)
		if not st:
			st = self.newQuestState(player)
			st.setState(State.STARTED)
		return "onFirstTalk.htm"

	#自訂處理 HTM 增加變數轉換
	def showResult(self, player, htmString):
		if not player or not htmString or len(htmString) == 0: return True
		if htmString.endswith(".htm") or htmString.endswith(".html"):
			htmString = JQuest.getHtm(self, player.getHtmlPrefix(), htmString)
		if len(htmString) != 0:
			st = player.getQuestState(qn)
			if player.getTarget():
				htmString.replace("%objectId%", str(player.getTarget().getObjectId()))
			htmString = htmString.replace("%playername%", player.getName())		
			htmString = htmString.replace("%times%", str(max(st.getInt('times'), 0)))
			htmString = htmString.replace("%skillSTR%", str(max(player.getSkillLevel(skillSTR), 1)-1))
			htmString = htmString.replace("%skillDEX%", str(max(player.getSkillLevel(skillDEX), 1)-1))
			htmString = htmString.replace("%skillCON%", str(max(player.getSkillLevel(skillCON), 1)-1))
			htmString = htmString.replace("%skillINT%", str(max(player.getSkillLevel(skillINT), 1)-1))
			htmString = htmString.replace("%skillWIT%", str(max(player.getSkillLevel(skillWIT), 1)-1))
			htmString = htmString.replace("%skillMEN%", str(max(player.getSkillLevel(skillMEN), 1)-1))

			htmString = htmString.replace("%freeRebirthPoint%", str(self.getFreeRebirthPoint(player)))
			htmString = htmString.replace("%maxRebirthPoint%", str(maxRebirthPoint))
			htmString = htmString.replace("%levelAfterRebirth%", str(levelAfterRebirth))
			htmString = htmString.replace("%require_level%", str(requireLevel))
			htmString = htmString.replace("%require_item_count_1%", str(requireItem[0][1]))
			html = NpcHtmlMessage(player.getTarget().getObjectId())
			html.setHtml(htmString)
			player.sendPacket(html)
		return htmString

QUEST = Rebirth(qID, qn, qDesc)

for id in NPCID:
	QUEST.addStartNpc(id)
	QUEST.addFirstTalkId(id)
	QUEST.addTalkId(id)

