import sys
from com.l2jserver.gameserver.model.quest		import State
from com.l2jserver.gameserver.model.quest		import QuestState
from com.l2jserver.gameserver.model.quest.jython	import QuestJython as JQuest

from com.l2jserver.gameserver.handler import ChatHandler
from com.l2jserver import Config
from com.l2jserver.gameserver.handler import IChatHandler;
from com.l2jserver.gameserver.instancemanager import MapRegionManager;
from com.l2jserver.gameserver.model import BlockList;
from com.l2jserver.gameserver.model import L2World;
from com.l2jserver.gameserver.model.actor.instance import L2PcInstance;
from com.l2jserver.gameserver.network import SystemMessageId;
from com.l2jserver.gameserver.network.serverpackets import CreatureSay;
from com.l2jserver.gameserver.util import Util;

from com.l2jserver.gameserver import Announcements

class CQA(JQuest, IChatHandler):
	qID = -1
	qn = "cQA"
	qDesc = "custom"

	NPCID = 100
	isCritical = True #是否為重要公告形式顯示
	
	command_split_char = " _#_ "
	
	htm_header = "<html><body><title>搶答活動</title>"
	htm_footer = "</body></html>"

	gifts = {
		"金幣":57
		,"古幣":5575
		,"慶典":6673
		,"光彩":6393
		,"藍伊":4355
		,"金殷":4356
		,"銀席":4357
		,"血帕":4358
		,"夢幻":13067
	}
	
	item = qty = question = answer = None
	
	htm_input_reward = '獎品<combobox width=140 var="item" list=' + reduce(lambda a, b: str(a) + ";" + str(b), gifts.keys()) + '>'
	htm_input_qty = '數量<edit var="qty" width=140 height=12>'
	htm_input_question = '題目<multiedit var="question" width=200 height=50>'
	htm_input_answer = '答案<edit var="answer" width=140 height=12>'
	htm_input_submit = '<button value="發出問題" width=80 height=20 action="bypass -h Quest ' + qn + ' showQuestion $item%(s)s$qty%(s)s$question%(s)s$answer">' % {"s":command_split_char}
	
	htm_input_question = htm_input_reward + htm_input_qty + htm_input_question + htm_input_answer + htm_input_submit
	
	commands = [1]
	
	def handleChat(self, type, activeChar, target, text):
		if activeChar.isChatBanned() and Util.contains(Config.BAN_CHAT_CHANNELS, type):
			activeChar.sendPacket(SystemMessageId.CHATTING_IS_CURRENTLY_PROHIBITED)
			return
		cs = CreatureSay(activeChar.getObjectId(), type, activeChar.getName(), text)
		pls = L2World.getInstance().getAllPlayersArray()
		if Config.DEFAULT_GLOBAL_CHAT.lower() == "on" or (Config.DEFAULT_GLOBAL_CHAT.lower() == "gm" and activeChar.isGM()):
			region = MapRegionManager.getInstance().getMapRegionLocId(activeChar)
			for player in pls:
				if region == MapRegionManager.getInstance().getMapRegionLocId(player) and not BlockList.isBlocked(player, activeChar) and player.getInstanceId() == activeChar.getInstanceId():
					player.sendPacket(cs)
		elif Config.DEFAULT_GLOBAL_CHAT.lower() == "global":
			if not activeChar.isGM() and not activeChar.getFloodProtectors().getGlobalChat().tryPerformAction("global chat"):
				activeChar.sendMessage(1101)
				return
			for player in pls:
				if not BlockList.isBlocked(player, activeChar):
					player.sendPacket(cs)
		if not self.answer == None:
			if text == self.answer:
				self.answer = None
				Announcements.getInstance().announceToAll("恭喜 %s 獲得 %s 數量 %s 答案:%s" % (activeChar.getName(), self.item, self.qty, text), self.isCritical)
				activeChar.addItem(self.qn, self.gifts[self.item], int(self.qty), None, True)
			
	def getChatTypeList(self):
		return self.commands
	
	def __init__(self, id = qID, name = qn, descr = qDesc):
		self.qID, self.qn, self.qDesc = id, name, descr
		JQuest.__init__(self, id, name, descr)
		self.addStartNpc(self.NPCID)
		self.addFirstTalkId(self.NPCID)
		self.addTalkId(self.NPCID)
		ChatHandler.getInstance().registerHandler(self)
		print "%s loaded" % self.qn
	
	def onAdvEvent(self, event, npc, player):
		if event.startswith("showQuestion "):
			params = event[len("showQuestion "):]
			self.item, self.qty, self.question, self.answer = params.split(self.command_split_char)
			Announcements.getInstance().announceToAll("搶答活動 請使用大喊頻作答 第一位答中問題的玩家 將會得到 %s 數量 %s" % (self.item, self.qty), self.isCritical)
			Announcements.getInstance().announceToAll("問題:%s" % (self.question), self.isCritical)
			return
		print self.qn, "不明要求", npc, player, event
		return self.htm_header + "不明要求" + self.htm_footer
			
	def onFirstTalk(self, npc, player):
		if not player.isGM():
			return self.htm_header + "GM 發問題專用, 請勿偷看啊" + self.htm_footer
		return self.htm_header + self.htm_input_question + self.htm_footer

CQA()