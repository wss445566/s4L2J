import _codecs
import sys
from com.l2jserver.gameserver import Announcements
from com.l2jserver.gameserver import Shutdown
from com.l2jserver.gameserver.instancemanager import QuestManager
from com.l2jserver.gameserver.model import L2World
from com.l2jserver.gameserver.model.quest.jython import QuestJython as JQuest
from com.l2jserver.gameserver.scripting import L2ScriptEngineManager
from com.l2jserver.gameserver.taskmanager import AutoAnnounceTaskManager
from com.sun.net.httpserver import *
from java.io import File, FileInputStream, InputStreamReader, BufferedReader, PrintWriter, StringWriter
from java.net import InetSocketAddress, InetAddress, URI, URL, URLDecoder
from java.util import Random
from javax.script import ScriptException, SimpleScriptContext, ScriptContext, ScriptEngineManager


class JSON:
	tab = 0
	def escape(self, t):
		return '"%s"' % str("%s" % t).replace('\\',r'\\').replace('"',r'\"').replace('/',r'\/').replace('\b',r'\b').replace('\f',r'\f').replace('\n', r'\n').replace('\r', r'\r').replace('\t',r'\t')
		
	def getTab(self, m = 0):
		self.tab += m
		return "\t" * self.tab

	def toJSON(self, d):
		if type(d) == type({}):
			return ["\n", ""][self.tab == 0] + self.getTab(0) + "{\n" + self.getTab(1) + str(",\n" + self.getTab(0)).join([self.toJSON(x) + ":" + self.toJSON(d[x]) for x in d]) + "\n" + self.getTab(-1) + "}"
		if type(d) in [type([]), type((0,))]:
			return ["\n", ""][self.tab == 0] + self.getTab(0) + "[\n" + self.getTab(1) + str(",\n" + self.getTab(0)).join([self.toJSON(x) for x in d]) + "\n" + self.getTab(-1) + "]"
		if type(d) == type(None):
			return 'null'
		return self.escape(d)

class BaseHttpHandler(HttpHandler):
	def handleImpl(self, exchange, ibuff):
		exchange.sendResponseHeaders(501, 0)

	def handle(self, exchange):
		if not exchange.getRemoteAddress().getAddress() == InetAddress.getByAddress([127,0,0,1]):
			exchange.sendResponseHeaders(403, 0)
			exchange.close()
			return
		try:
			i = exchange.getRequestBody()
			ibuff = ""
			while True:
				temp = i.read()
				if temp == -1:
					break
				ibuff += chr(temp)
			ibuff = _codecs.utf_8_decode(ibuff)[0]
			self.handleImpl(exchange, ibuff)
		except:
			exchange.sendResponseHeaders(500, 0)
		exchange.close()

class FileHttpHandler(BaseHttpHandler):
	ct = {
	"htm":"text/html",
	"html":"text/html",
	"jpg":"image/jpeg",
	"png":"image/png",
	"js":"application/x-javascript",
	"css":"text/css"
	}
	def handleImpl(self, exchange, ibuff):
		try:
			path = sourcepath.replace("\\", "/") + "/custom/WebAdmin/WebRoot" + exchange.getRequestURI().getPath()
			if path.endswith("/"):
				path += "index.html"
			try:
				i = open(path, "rb")
			except:
				exchange.sendResponseHeaders(404, 0)
				return
			r = i.read()
			i.close()
			ext = path.split(".")[-1]
			if ext in self.ct:
				rh = exchange.getResponseHeaders()
				rh.set("Content-Type", self.ct[ext])
			exchange.sendResponseHeaders(200, len(r))
			exchange.getResponseBody().write(r)
		except:
			exchange.sendResponseHeaders(500, 0)

class CommandHttpHandler(BaseHttpHandler):
	def getQuestInfo(self, param, quest):
		try:
			if param == "name": return quest.getName()
			if param == "id": return quest.getQuestIntId()
			if param == "desc": return quest.getDescr()
			if param == "file": return quest.getScriptFile().toString()
		except:
			pass
		return None
		
	def getPlayerInfo(self, param, player):
		try:
			if param == "name": return player.getName()
			if param == "x": return player.getX()
			if param == "y": return player.getY()
			if param == "z": return player.getZ()
			if param == "objid": return player.getObjectId()
			if param == "hp": return int(player.getCurrentHp())
			if param == "maxhp": return player.getMaxHp()
			if param == "mp": return int(player.getCurrentMp())
			if param == "maxmp": return player.getMaxMp()
			if param == "cp": return int(player.getCurrentCp())
			if param == "maxcp": return player.getMaxCp()
		except:
			pass
		return None

	def setPlayerInfo(self, param, value, player):
		if param == "cp":
			player.setCurrentCp(int(value))
			return
		if param == "hp":
			player.setCurrentHp(int(value))
			return
		if param == "mp":
			player.setCurrentMp(int(value))
			return

	def checkQuery(self, query, list = []):
		return reduce(lambda x,y: x and y, [k in query for k in list])

	def exec_script(self, engine_name, script, post_script="", attr={}):
		r = ""
		l2sem = L2ScriptEngineManager.getInstance()
		context = SimpleScriptContext()
		sw = StringWriter()
		pw = PrintWriter(sw, True)
		context.setAttribute("out_writer", pw, ScriptContext.ENGINE_SCOPE)
		for k in attr:
			context.setAttribute(str(k), attr[k], ScriptContext.ENGINE_SCOPE)
		context.setWriter(pw)
		context.setErrorWriter(pw)
		try:
			l2sem.eval(engine_name, script, context)
			r += sw.toString()
		except ScriptException, e:
			r += sw.toString()
			r += e.getMessage()
		l2sem.eval(engine_name, post_script, context)
		return r
		
		
	def handleImpl(self, exchange, ibuff):
		r = ""
		try:
			uri = exchange.getRequestURI()
			command = uri.getPath().split("/")
			if not command[1] == "ajax":
				raise

			query = {}
			try:
				for x in uri.getRawQuery().split("&"):
					x2 = URLDecoder().decode(x, 'UTF-8')
					k,v = x2.split("=", 1)
					query[k] = v
			except:
				pass

			if command[2] == "webadmin":

				if command[3] == "stop":
					q = QuestManager.getInstance().getQuest(WebAdmin.qn)
					try:
						q.cancelQuestTimers("webadmin_stop")
						q.startQuestTimer("webadmin_stop", 1000, None, None)
					except:
						pass
					r = "webAdmin stop"
				elif command[3] == "restart":
					q = QuestManager.getInstance().getQuest(WebAdmin.qn)
					try:
						q.cancelQuestTimers("webadmin_restart")
						q.startQuestTimer("webadmin_restart", 1000, None, None)
					except:
						pass
					r = "webAdmin restart"
				else:
					exchange.sendResponseHeaders(501, 0)
					return


			elif command[2] == "quest":
			
				if command[3] == "list":
					r2 = {}
					for quest in QuestManager.getInstance().getAllManagedScripts():
						qn = quest.getName()
						r2[qn] = {}
						if 'req' in query:
							for c in query['req'].split(","):
								r2[qn][c] = self.getQuestInfo(c, quest)
					r2 = r2.items()
					r2.sort()
					r = JSON().toJSON(r2)
					rh = exchange.getResponseHeaders()
					rh.set("Content-Type", "application/json")

				elif command[3] == "unload":
					if not self.checkQuery(query, ['name']):
						raise
					QuestManager.getInstance().getQuest(query['name']).unload()

				elif command[3] == "reload":
					if not self.checkQuery(query, ['name']):
						raise
					QuestManager.getInstance().getQuest(query['name']).reload()
					
				elif command[3] == "get_source":
					if not self.checkQuery(query, ['name']):
						raise
					file = QuestManager.getInstance().getQuest(query['name']).getScriptFile()
					try:
						i = open(file.toString(), "r")
					except:
						exchange.sendResponseHeaders(404, 0)
						return
					r = i.read()
					i.close()
					rh = exchange.getResponseHeaders()
					rh.set("Content-Type", "text/plain; charset=utf-8")					
					
				else:
					exchange.sendResponseHeaders(501, 0)
					return

			elif command[2] == "script":
				if command[3] == "writefile_exec":
					if not self.checkQuery(query, ['file']):
						raise
					query['file'] = query['file'].replace("\\", "/")
					query['file'] = query['file'].split("/")[-1]
					path = sourcepath.replace("\\", "/") + "/custom/WebAdmin/WebRoot/temp/" + query['file']
					o = open(path, "w")
					o.write(ibuff);
					o.close()
					file = File(path)
					try:
						L2ScriptEngineManager.getInstance().executeScript(file)
					except ScriptException, e:
						L2ScriptEngineManager.getInstance().reportScriptFileError(file, e)
					
				elif command[3] == "execjy":
					pre_script = """
import sys
sys.stdout = out_writer
sys.stderr = out_writer
"""					
					post_script = """
import sys
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__
"""					
					r = self.exec_script("jython", pre_script + ibuff, post_script)

				elif command[3] == "execbsh":
					r = self.exec_script("bsh", ibuff)

				elif command[3] == "execjs":
					r = self.exec_script("js", ibuff)
					
				elif command[3] == "execjava":
					r = self.exec_script("java", ibuff)
					
				else:
					exchange.sendResponseHeaders(501, 0)
					return


			elif command[2] == "player":

				if command[3] == "list":
					r2 = {}
					for player in L2World.getInstance().getAllPlayersArray():
						objid = self.getPlayerInfo("objid", player)
						r2[objid] = {}
						if 'req' in query:
							for c in query['req'].split(","):
								r2[objid][c] = self.getPlayerInfo(c, player)
					r = JSON().toJSON(r2)
					rh = exchange.getResponseHeaders()
					rh.set("Content-Type", "application/json")

				elif command[3] == "info":
					if not self.checkQuery(query, ['objid','req']):
						raise
					player = L2World.getInstance().getPlayer(int(query['objid']))
					if not player:
						raise
					r2 = {}
					for c in query['req'].split(","):
						r2[c] = self.getPlayerInfo(c, player)
					r = JSON().toJSON(r2)
					rh = exchange.getResponseHeaders()
					rh.set("Content-Type", "application/json")

				elif command[3] == "edit":
					if not self.checkQuery(query, ['objid']):
						raise
					player = L2World.getInstance().getPlayer(int(query['objid']))
					if not player:
						raise
					del query['objid']
					for c in query:
						self.setPlayerInfo(c, query[c], player=player)

				elif command[3] == "teleport":
					if not self.checkQuery(query, ['objid','x','y','z']):
						raise
					x = int("%d" % float(query['x']))
					y = int("%d" % float(query['y']))
					z = int("%d" % float(query['z']))
					player = L2World.getInstance().getPlayer(int(query['objid']))
					if not player:
						raise
					player.teleToLocation(x, y, z, 0, False)
				else:
					exchange.sendResponseHeaders(501, 0)
					return

			elif command[2] == "zone":
				if command[3] == "list":
					script = """
setAccessibility(true);
import com.l2jserver.gameserver.instancemanager.ZoneManager;
import com.l2jserver.gameserver.model.zone.form.ZoneCuboid;
import com.l2jserver.gameserver.model.zone.form.ZoneNPoly;
import com.l2jserver.gameserver.model.zone.form.ZoneCylinder;
import com.l2jserver.gameserver.model.zone.type.*;
import java.lang.Class;

T(n){
	r = n.substring(n.lastIndexOf('.')+1);
	return r;
}

for(zts : ZoneManager.getInstance()._classZones.values()){
	for(zt : zts.values()){
		z = zt.getZone();
		ztstring = T(zt.getClass().getName());
		zfstring = T(z.getClass().getName());
		out_writer.print(zt.getId() + "|" + zt.getName() + "|" + ztstring + "|" + zfstring + "|");
		switch(zfstring){
			case "ZoneNPoly":
				for(i = 0; i < z._x.length; i++){
					out_writer.print(String.valueOf(z._x[i])+","+String.valueOf(z._y[i])+"_");
				}
				break;
			case "ZoneCylinder":
				out_writer.print(String.valueOf(z._x)+","+String.valueOf(z._y)+","+String.valueOf(z._rad));
				break;
			case "ZoneCuboid":
				out_writer.print(String.valueOf(z._x1)+","+String.valueOf(z._x2)+","+String.valueOf(z._y1)+","+String.valueOf(z._y2));
				break;
		}
		out_writer.println("");
	}
}
"""					
					r2 = {}
					for z in self.exec_script("bsh", script).split("\n")[:-1]:
						id, zn, zt, zf, data = z.split("|")
						r3 = {"zn":zn, "zt":zt, "zf":zf}
						r4 = []
						if zf == "ZoneNPoly":
							for o in data.split("_")[:-1]:
								r4 += [o.split(",")]
						else:
							r4 = data.split(",")
						r3['data'] = r4
						r2[id] = r3
					r = JSON().toJSON(r2)
					rh = exchange.getResponseHeaders()
					rh.set("Content-Type", "application/json; charset=utf-8")
				
				
				else:
					exchange.sendResponseHeaders(501, 0)
					return
					
					
			elif command[2] == "server":

				if command[3] == "anno":
					if command[4] == "once":
						Announcements.getInstance().announceToAll(ibuff)
					elif command[4] == "show":
						for player in L2World.getInstance().getAllPlayersArray():
							Announcements.getInstance().showAnnouncements(player)
					elif command[4] == "list":
						script = """
setAccessibility(true);
import com.l2jserver.gameserver.Announcements;
for(s : Announcements.getInstance()._announcements)
	out_writer.println(random_string + s);
"""
						random_string = "".join([chr(Random().nextInt(26)+ord("a")) for x in xrange(10)])
						r3 = self.exec_script("bsh", script, attr={"random_string":random_string}).split(random_string)[1:]
						r2 = {}
						for x in xrange(len(r3)):
							r2[x] = r3[x]
						r = JSON().toJSON(r2)
						rh = exchange.getResponseHeaders()
						rh.set("Content-Type", "application/json; charset=utf-8")

					elif command[4] == "clist":
						script = """
setAccessibility(true);
import com.l2jserver.gameserver.Announcements;
for(s : Announcements.getInstance()._critAnnouncements)
	out_writer.println(random_string + s);
"""
						random_string = "".join([chr(Random().nextInt(26)+ord("a")) for x in xrange(10)])
						r3 = self.exec_script("bsh", script, attr={"random_string":random_string}).split(random_string)[1:]
						r2 = {}
						for x in xrange(len(r3)):
							r2[x] = r3[x]
						r = JSON().toJSON(r2)
						rh = exchange.getResponseHeaders()
						rh.set("Content-Type", "application/json; charset=utf-8")

					elif command[4] == "alist":
						r3 = []
						for a in AutoAnnounceTaskManager.getInstance().getAutoAnnouncements():
							for m in a.getMemo():
								r3 += [m]
						r2 = {}
						for x in xrange(len(r3)):
							r2[x] = r3[x]
						r = JSON().toJSON(r2)
						rh = exchange.getResponseHeaders()
						rh.set("Content-Type", "application/json; charset=utf-8")
						
					elif command[4] == "del":
						if not self.checkQuery(query, ['id']):
							raise
						Announcements.getInstance().delAnnouncement(int(query['id']))
						
					elif command[4] == "cdel":
						if not self.checkQuery(query, ['id']):
							raise
						Announcements.getInstance().delCritAnnouncement(int(query['id']))

					elif command[4] == "adel":
						if not self.checkQuery(query, ['id']):
							raise
						AutoAnnounceTaskManager.getInstance().deleteAutoAnnounce(int(query['id']))
						
					elif command[4] == "add":
						if not self.checkQuery(query, ['text']):
							raise
						Announcements.getInstance().addAnnouncement(query['text'])
						
					elif command[4] == "cadd":
						if not self.checkQuery(query, ['text']):
							raise
						Announcements.getInstance().addCritAnnouncement(query['text'])

					elif command[4] == "aadd":
						if not self.checkQuery(query, ['initial', 'delay', 'repeat', 'text', 'crit']):
							raise
						AutoAnnounceTaskManager.getInstance().addAutoAnnounce(int(query['initial']), int(query['delay']), int(query['repeat']), query['text'], [False, True][int(query['crit'])])
						
					else:
						exchange.sendResponseHeaders(501, 0)
						return

				elif command[3] == "shutdown":
					t = int("%d" % float(ibuff))
					Shutdown.getInstance().startTelnetShutdown("127.0.0.1", t, False)

				elif command[3] == "restart":
					t = int("%d" % float(ibuff))
					Shutdown.getInstance().startTelnetShutdown("127.0.0.1", t, True)

				else:
					exchange.sendResponseHeaders(501, 0)
					return
			else:
				exchange.sendResponseHeaders(501, 0)
				return

			r = _codecs.utf_8_encode(r)[0]
			if len(r) == 0:
				r = 'null'
			exchange.sendResponseHeaders(200, len(r))
			exchange.getResponseBody().write(r)
			return
		except:
			exchange.sendResponseHeaders(500, 0)

class WebAdmin(JQuest):
	qID = -1
	qn = "webAdmin"
	qDesc = "custom"

	def initWebServer(self):
		self.hs = HttpServer.create(InetSocketAddress("127.0.0.1", 8002), 0)
		self.hs.createContext("/", FileHttpHandler())
		self.hs.createContext("/ajax", CommandHttpHandler())
		self.hs.setExecutor(None)
		self.hs.start()

	def webadmin_stop(self):
		self.hs.stop(0)
		print "webserver stoped", "!" * 20

	def webadmin_restart(self):
		self.webadmin_stop()
		QuestManager.getInstance().reload(self.qn)

	def __init__(self, id = qID, name = qn, descr = qDesc):
		JQuest.__init__(self, id, name, descr)
		self.initWebServer()
		print "Init:" + self.qn + " loaded"

	def onAdvEvent(self, event, npc, player):
		if event == "webadmin_stop":
			self.webadmin_stop()
		elif event == "webadmin_restart":
			self.webadmin_restart()

WebAdmin()