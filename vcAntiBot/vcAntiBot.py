import sys
from com.l2jserver.gameserver.model.quest		import State
from com.l2jserver.gameserver.model.quest		import QuestState
from com.l2jserver.gameserver.model.quest.jython	import QuestJython as JQuest

from com.l2jserver.gameserver.handler import VoicedCommandHandler
from com.l2jserver.gameserver.handler import IVoicedCommandHandler

from com.l2jserver.gameserver.model import L2World
from com.l2jserver.gameserver.model.actor import L2Character
from com.l2jserver.gameserver.model.actor.instance import L2PcInstance
from com.l2jserver.gameserver.network.serverpackets import ExShowScreenMessage
from com.l2jserver.gameserver.ai import CtrlIntention
from com.l2jserver.gameserver.instancemanager import TownManager
from java.util.logging import Logger
from com.l2jserver.gameserver.network.serverpackets import NpcHtmlMessage
import time

class VCAntiBot(JQuest, IVoicedCommandHandler):
	qID = -1
	qn = "AntiBot"
	qDesc = "custom"

	isShowHtml = True #是否顯示對話框
	
	interval = 1000 * 60 * 5 #5分鐘 隨機抽查一個玩家
	interval_random_delay_sec = 180 #隨機抽查延遲 預設 0 - 180 秒

	timepass_check = True #是否記錄及檢測個別玩家反外掛檢查後, 需要多久才會再有機會被查
	timepass = 60 * 20 #個別玩家檢測後的免測時間, 單位 秒, 預設 20分鐘

	question_duration = 1000 * 60 * 5 #問題顯示多久 1秒=1000 預設 5分鐘
	jail_duration = 0 #關多久後自動釋放, 單位 分鐘,  0 = 不自動釋放, 要 GM 手動釋放
	
	max_retry = 5 #可答錯多少次 才被關
	
	title = "反外掛檢測系統"
	desc = "請以一般文字頻道輸入 .ab 空格 然後答案"
	#可自訂多條題目 ["問題", "答案"],["問題", "答案"],["問題", "答案"],["問題", "答案"] 如此類推
	#答案應考濾 玩家有沒有能力輸入 問題不用太困難, 考慮玩家能否輸入中文 盡量不要用特別字 注音字
	#請自行修改及增加 自訂問題與答案
	qa = [ 
		["請輸入本服匕首安定值","3"]
		,["請輸入本伺服GM名稱","XXX"]
		,["一星期有多少天","7"]
		]
		
	#答中送禮 [物品ID, 最少, 最多, 機率], [物品ID, 最少, 最多, 機率], [物品ID, 最少, 最多, 機率]
	#機率 100 = 100% 必送
	#可自行增加 減少
	gifts = [
		[57,10000,99999,100]
		,[57,10,100,100]
		,[57,1,1,100]
	]

	#gifts = [] #如不送禮
	
	commands = ["反外掛", "ab", "AB", "abq"] #.abq 是 GM 測試問題 答案用
	
	def useVoicedCommand(self, command, player, params):
		if command == "abq" and player.isGM():
			self.showQuestion(player)
			return
		
		st = player.getQuestState(self.qn)
		if not st:
			st = self.newQuestState(player)
			st.setState(State.STARTED)
		if st.get("answer") == None or len(st.get("answer")) == 0:
			self.info("%s %s %s %s %s" % (self.qn, command, player, params, "沒有答案下作答"))
			player.sendMessage("目前不需要回答反外掛系統")
			return
		if params == None:
			self.showQuestion(player)
			return
		if st.get("answer") == params:
			self.info("%s %s %s %s %s" % (self.qn, command, player, params, "答案正確"))
			self.cancelQuestTimer("timeout_%d" % player.getObjectId(), None, player)
			self.showScreenMessage(player, "%s\n答案正確 打擾了" % self.title)
			st.set("try", "0")
			st.set("answer", "")
			for i in self.gifts:
				item_id, min_c, max_c, c = i
				if c >= self.getRandom(100):
					player.addItem(self.qn, item_id, min_c + self.getRandom(max_c - min_c), None, True)
		else:
			tried = str(st.getInt("try") + 1)
			st.set("try", tried)
			self.info("%s %s %s %s %s" % (self.qn, command, player, params, "答案錯誤 失敗次數%s" % tried))
			player.sendMessage("答案錯誤 失敗次數 %s" % tried)
			if int(tried) >= self.max_retry:
				st.set("answer", "")
				self.info("%s %s %s %s %s" % (self.qn, command, player, params, "答錯 %d 次 關起來" % tried))
				self.cancelQuestTimer("timeout_%d" % player.getObjectId(), None, player)
				self.showScreenMessage(player, "%s\n答案錯誤次數過多" % self.title)
				self.jail(player)
				return
			self.showQuestion(player)
			
	def getVoicedCommandList(self):
		return self.commands
		
	def __init__(self, id = qID, name = qn, descr = qDesc):
		self.qID, self.qn, self.qDesc = id, name, descr
		JQuest.__init__(self, id, name, descr)
		self.setOnEnterWorld(True)
		VoicedCommandHandler.getInstance().registerHandler(self)
		self.startQuestTimer("check", self.interval + (1000 * self.getRandom(self.interval_random_delay_sec)), None, None, False)
		print "玩家可用 .%s" % " .".join(self.commands)
		print "%s loaded" % self.qn
	
	def info(self, message):
		Logger.getLogger(self.qn).info(message)
		
	def jail(self, player):
		player.setPunishLevel(L2PcInstance.PunishLevel.JAIL, self.jail_duration)
		
	def showScreenMessage(self, player, message, duration = 10000):
		player.sendPacket(ExShowScreenMessage(message, duration))

	def genMathAddQuestion(self):
		q1, q2 = self.getRandom(100), self.getRandom(100) #2位數 加法
		return ["請計算 %d + %d = ?" % (q1, q2), str(q1+q2)]

	def genNumberConvertQuestion(self):
		t = ["","一","二","三","四","五","六","七","八","九"]
		o = ["","十","百","千","萬","十","百","千","億","十","百","千"]
		q = a = ""
		m = 5 #5位數字, 最多 12 位
		for x in xrange(m-1, -1, -1):
			r = self.getRandom(9)+1
			q += t[r] + o[x]
			a += str(r)
		return ["請以數字回答 %s" % q, a]
		
	def getQuestion(self):
		r = self.getRandom(100)
		if r in xrange(0,33): #33% 出現 加法題
			return self.genMathAddQuestion()
		elif r in xrange(33,66): #33% 出現 數字轉換題
			return self.genNumberConvertQuestion()
		return self.qa[self.getRandom(len(self.qa))] #其餘機率 出現自訂題
	
	def showQuestion(self, player):
		st = player.getQuestState(self.qn)
		if not st:
			st = self.newQuestState(player)
			st.setState(State.STARTED)
		q = self.getQuestion()
		self.info("%s %s %s %s" % (self.qn, player, q[0], q[1]))
		st.set('answer', str(q[1]))
		self.showScreenMessage(player, "%s\n%s\n%s" % (self.title, self.desc, q[0]), self.question_duration)
		if self.isShowHtml:
			player.sendPacket(NpcHtmlMessage(player.getObjectId(), "<html><body>%s<br>%s<br>%s</body></html>" % (self.title, self.desc, q[0])))
		
	def checkCondition(self, player):
		if player.isGM(): return False #GM 不檢, 注意 如果GM被關需要由另一位GM釋放
		if player.isInOlympiadMode(): return False #奧P 不檢
		if not TownManager.getTown(player.getX(), player.getY(), player.getZ()) == None: return False #在城鎮中 不檢
		if player.isInsideZone(L2Character.ZONE_PEACE): return False #安全地區 不檢
		if player.getAI().getIntention() == CtrlIntention.AI_INTENTION_IDLE: return False #發呆 不檢
		#if player.getAI().getIntention() == CtrlIntention.AI_INTENTION_FOLLOW: return False #跟隨 不檢
		#if player.getAI().getIntention() == CtrlIntention.AI_INTENTION_MOVE_TO: return False #跑路 不檢
		#if player.getAI().getIntention() == CtrlIntention.AI_INTENTION_REST: return False #坐下休息 不檢		
		if player.isInJail(): return False #監禁中 不檢
		st = player.getQuestState(self.qn)
		if not st:
			st = self.newQuestState(player)
			st.setState(State.STARTED)
		if self.timepass_check:
			last = st.get('last_time')
			if last and time.time() - float(last) < self.timepass: return False #免測時間內 不檢
		if st.getQuestTimer("timeout_%d" % player.getObjectId()): return False #已在檢測中 不檢
		return True

	def doCheck(self):
		l2world = L2World.getInstance()
		pl = [x for x in l2world.getAllPlayers().values() if self.checkCondition(x)]
		pc = len(pl)
		if pc < 1: return
		lucky_player = pl[self.getRandom(pc)]
		self.showQuestion(lucky_player)
		self.startQuestTimer("timeout_%d" % lucky_player.getObjectId(), self.question_duration, None, lucky_player, False)
		if self.timepass_check:
			st = lucky_player.getQuestState(self.qn)
			if not st:
				st = self.newQuestState(lucky_player)
				st.setState(State.STARTED)
			st.set('last_time', str(time.time()))
		
	def onAdvEvent(self, event, npc, player):
		if event == "check":
			self.startQuestTimer("check", self.interval + (1000 * self.getRandom(self.interval_random_delay_sec)), None, None, False)
			self.doCheck()
		elif event.startswith("timeout"):
			self.info("%s 反外掛檢測超時" % player.getName())
			self.jail(player)
			
	def onEnterWorld(self, player):
		st = player.getQuestState(self.qn)
		if not st:
			st = self.newQuestState(player)
			st.setState(State.STARTED)
		if st.getQuestTimer("timeout_%d" % player.getObjectId()):
			self.showQuestion(player)

VCAntiBot()