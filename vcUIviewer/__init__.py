import sys
from com.l2jserver.gameserver.handler import VoicedCommandHandler
from com.l2jserver.gameserver.handler import IVoicedCommandHandler

from com.l2jserver.gameserver.model.actor.instance import L2PcInstance
from com.l2jserver.gameserver.network.serverpackets import ShowBoard
def sendBBS(player, message):
	if not isinstance(player, L2PcInstance):
		print "not a player"
		return
	#print "message len", len(message)
	player.sendPacket(ShowBoard(message[0:4090], "101"))
	player.sendPacket(ShowBoard(message[4090:8180], "102"))
	player.sendPacket(ShowBoard(message[8180:], "103"))
	return

class VCUIviewer(IVoicedCommandHandler):
	htm_header = "<html><body><title>UI viewer</title><table border=0 cellpadding=2 cellspacing=0 width=756><TR></TR><TR></TR><TR><TD></TD><TD>"
	htm_footer = "</TD></TR></table></body></html>"
	
	commands = ["ui", "UI"]
	
	filelist = {}
	w = 756
	h = 400
	fl = 'l2ui'
	fn = ''
	page = 0
	ipp = 25
	
	def useVoicedCommand(self, command, player, params):
		if params:
			try:
				cmd , p = params.split(None,1)
				if cmd == 'fl':
					self.fl = p
				if cmd == 'wh':
					self.w, self.h = p.split()
				if cmd == 'fn':
					self.fn = p
				if cmd == 'p':
					self.page = int(p)
			except:
				pass
			
		r = self.htm_header
		r += """<table><tr>"""
		r += """<td><combobox width=100 var="filelist" list=%s sel="%s"></td>""" % (";".join(self.filelist.keys()), self.fl)
		r += """<td width=20><a action="bypass -h voice .ui fl $filelist">´«</a></td>"""
		r += """<td width=20>¼e</td><td><edit var="width" width=40 height=12></td>"""
		r += """<td width=20>°ª</td><td><edit var="height" width=40 height=12></td>"""
		r += """<td width=20><a action="bypass -h voice .ui wh $width $height">³]</a></td>"""
		r += """<td width=20>­¶</td><td><edit var="page" width=40 height=12 value="2"></td><td width=50>%d/%d</td>""" % (self.page, len(self.filelist[self.fl])/self.ipp)
		#r += """<td><combobox width=140 var="page" list=%s></td>""" % ";".join([str(x) for x in xrange((len(self.filelist[self.fl])/self.ipp)+1)])
		r += """<td width=20><a action="bypass -h voice .ui p $page">´«</a></td>"""
		r += """<td><combobox width=300 var="filename" list=%s sel="%s"></td>""" % (";".join(self.filelist[self.fl][self.ipp * self.page : self.ipp * (self.page+1)]), self.fn)
		r += """<td width=20><a action="bypass -h voice .ui fn $filename">¬Ý</a></td>"""
		r += """</tr></table>"""
		n = self.fl+"."+self.fn
		r += n
		r += """<img src="%s" width=%d height=%d>""" % (n, self.w, self.h)
		r += "======="
		r += self.htm_footer
		sendBBS(player, r)
		return

	def getVoicedCommandList(self):
		return self.commands

	def parseFile(self, filename):
		f = open(filename)
		f.readline()
		r = []
		for line in f:
			x = line.split()
			fn = x[1].split("'")
			if fn[0] == 'Texture':
				r += [fn[1]]
		return r
		
	def __init__(self):
		self.filelist['icon'] = self.parseFile(r"C:\L2JTW\game\data\scripts\custom\vcUIviewer\icon.txt")
		self.filelist['L2font-tw'] = self.parseFile(r"C:\L2JTW\game\data\scripts\custom\vcUIviewer\l2font-tw.txt")
		self.filelist['l2ui'] = self.parseFile(r"C:\L2JTW\game\data\scripts\custom\vcUIviewer\l2ui.txt")
		self.filelist['l2ui_ct1'] = self.parseFile(r"C:\L2JTW\game\data\scripts\custom\vcUIviewer\l2ui_ct1.txt")
		self.filelist['l2ui_ch3'] = self.parseFile(r"C:\L2JTW\game\data\scripts\custom\vcUIviewer\l2ui_ch3.txt")
		VoicedCommandHandler.getInstance().registerHandler(self)
		print "vcUIviewer loaded"

VCUIviewer()