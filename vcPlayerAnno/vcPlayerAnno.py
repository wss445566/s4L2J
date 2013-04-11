from com.l2jserver.gameserver.handler import VoicedCommandHandler
from com.l2jserver.gameserver.handler import IVoicedCommandHandler
from com.l2jserver.gameserver.datatables import ItemTable
from com.l2jserver.gameserver.network.serverpackets import InventoryUpdate
from com.l2jserver.gameserver import Announcements

class VCPlayerAnno(IVoicedCommandHandler):
	isCritical = True #是否為重要公告形式顯示
	requireItemId = 57 #需求道具 ID
	requireItemCount = 100 #需求道具數量
	messageLength = 50 #訊息長度限制

	commands = ["公告"]
	
	def useVoicedCommand(self, command, player, params):
		if not player: return
		inv = player.getInventory()
		if not inv: return
		ditem = inv.destroyItemByItemId("vcplayeranno", self.requireItemId, self.requireItemCount, player, None) 
		if ditem:
			player.sendMessage("消耗了 %s %d 個" % (ditem.getName(), self.requireItemCount))
			Announcements.getInstance().announceToAll("%s:%s" % (player.getName(), params[:self.messageLength]), self.isCritical)
			iu = InventoryUpdate()
			iu.addModifiedItem(ditem)
			player.sendPacket(iu)
		else:
			item = ItemTable.getInstance().getTemplate(self.requireItemId)
			name = ""
			if item:
				name = item.getName()
			player.sendMessage("所需道具不足 需要 %s %d 個" % (name, self.requireItemCount))
			
	def getVoicedCommandList(self):
		return self.commands
		
	def __init__(self):
		VoicedCommandHandler.getInstance().registerHandler(self)
		print "vcPlayerAnno registered"
		print "玩家可用 .公告"

VCPlayerAnno()
