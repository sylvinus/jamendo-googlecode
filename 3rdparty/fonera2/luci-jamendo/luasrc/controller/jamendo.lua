
module("luci.controller.jamendo", package.seeall)

function index()
	local page = entry({"fon_services", "fon_jamendo"}, call("jamendo"), "Jamendo Radios", 90)
	page.icon_path = "/luci-static/resources/icons/"
	page.icon = "jamendo.png"
end



function jamendo()

	local http = require "luci.http"
	local tpl = require "luci.template"
	local sys = require "luci.sys"
	
	local radioid = http.formvalue("jamendo_radioid")
	
	if not radioid then
		radioid = "lounge"
	end


	-- Ugly but hey, this is a prototype ;)
	sys.call("killall madplay")
	sys.call("wget -O - http://m65.neofacto.lu:8000/" .. radioid .. ".mp3 | madplay - &")
		
		
	tpl.render("jamendo/index",{jamendo_radioid=radioid,selected=""})
end