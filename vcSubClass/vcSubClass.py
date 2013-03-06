import sys
from com.l2jserver.gameserver.handler import VoicedCommandHandler
from com.l2jserver.gameserver.handler import IVoicedCommandHandler
from com.l2jserver.gameserver.network.serverpackets import NpcHtmlMessage
try:
	from com.l2jserver.gameserver.datatables import ClassListData
except:
	from com.l2jserver.gameserver.datatables import CharTemplateTable
from com.l2jserver.gameserver.network import SystemMessageId
from com.l2jserver.gameserver.model.actor.instance import L2PcInstance

class VCSubClass(IVoicedCommandHandler):

	commands = ["°ÆÂ¾"]
	
	htm_header = "<html><body><title>°ÆÂ¾Âà´«</title>"
	htm_footer = "</body></html>"
	
	def useVoicedCommand(self, command, player, params):
		def get_class_desc(cid):
			try:
				return ClassListData.getInstance().getClass(cid).getClientCode()
			except:
				return CharTemplateTable.getInstance().getClassNameById(cid)
				
		def make_link(sci, desc):
			return "<a action=\"bypass -h voice .%(vcn)s %(sci)d\">%(desc)s</a><br>" % {"desc":desc,"vcn":self.commands[0],"sci":sci}

		def check(p):
			if p.isInCombat() or p.isDead(): return False
			if isinstance(p, L2PcInstance):
				if p.isInStoreMode() or p.isInCraftMode() or p.isFakeDeath() or not p.isOnline() or p.isFishing(): return False
			return True

		if params:
			if int(params) > len(player.getSubClasses()): return
			if not player.getFloodProtectors().getSubclass().tryPerformAction("change class"): return
			if player.getClassIndex() == int(params): return
			if not check(player): return
			player.setActiveClass(int(params))
			player.sendPacket(SystemMessageId.SUBCLASS_TRANSFER_COMPLETED)
			return
		r = make_link(0, get_class_desc(player.getBaseClass()))
		sc = player.getSubClasses()
		for i in sc:
			r += make_link(i, get_class_desc(sc[i].getClassId()))
		htmString = self.htm_header + r + self.htm_footer
		html = NpcHtmlMessage(player.getObjectId())
		html.setHtml(htmString)
		player.sendPacket(html)
			
	def getVoicedCommandList(self):
		return self.commands
		
	def __init__(self):
		VoicedCommandHandler.getInstance().registerHandler(self)
		print "vcSubClass registered"
		print "ª±®a¥i¥Î .°ÆÂ¾"

VCSubClass()


