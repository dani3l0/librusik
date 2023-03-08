var donottouch = true;
var autoupdate = null;
var maxusers = 0;
var maxuserset = 0;
var users = 0;
var runningtimex = null;
var todelete;
var tochange;
var todeletefull;
var tochangefull;
var newpasswd;
function gou(where) {
	window.location.href = where;
}
function agou(where) {
	document.body.style.opacity = 0;
	setTimeout(function() {
		gou(where);
	}, 350);
}
function setCookie(user, pass) {
	var cvalue = {
		"name": user.split('').reverse().join(''),
		"password": pass.split('').reverse().join('')
	}
	var d = new Date();
	d.setTime(d.getTime() + (28 * 24 * 60 * 60 * 1000));
	var expires = "expires=" + d.toUTCString();
	document.cookie = "librusik_a=" + encodeURIComponent(JSON.stringify(cvalue)) + ";" + expires + "; path=/";
}
function getCookie() {
	var name = "librusik_a=";
	var ca = document.cookie.split(";");
	for (var i = 0; i < ca.length; i++) {
		var c = ca[i];
		while (c.charAt(0) == ' ') {
			c = c.substring(1);
		}
		if (c.indexOf(name) == 0) {
			let meh = JSON.parse(decodeURIComponent(c.substring(name.length, c.length)));
			meh["name"] = meh["name"].split('').reverse().join('');
			meh["password"] = meh["password"].split('').reverse().join('');
			return meh;
		}
	}
	return {};
}
function rmCookie() {
	document.cookie = "librusik_a={}; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/";
	agou("panel/login");
}
function bool2str(bool, stryes, strnot) {
	return bool ? stryes : strnot;
}
function mktime(seconds) {
	var secs = "0" + Math.floor(seconds % 60);
	var mins = "0" + Math.floor(seconds / 60 % 60);
	var hours = "0" + Math.floor(seconds / 3600 % 24);
	var days = Math.floor(seconds / 86400);
	var strink = "";
	if (seconds >= 86400) strink += days + ":";
	if (seconds >= 3600) strink += hours.slice(-2) + ":";
	strink += mins.slice(-2) + ":";
	strink += secs.slice(-2);
	return strink;
}
function setmaxusers(divider) {
	if (divider === "+" && maxuserset < 64) maxuserset += 1;
	else if (divider === "-" && maxuserset > users && maxuserset > 2) maxuserset -= 1;
	else if (divider === "") maxuserset = maxusers;
	document.getElementById("maxusers").innerText = maxuserset;
}
function checkcookie() {
	var cokie = getCookie();
	if (cokie["name"] && cokie["password"]) {
		post("panel/api", {
			"method": "auth",
			"name": cokie["name"],
			"password": cokie["password"]
		}, function(data) {
			if (data.status == 200) {
				setCookie(cokie["name"], cokie["password"]);
				gou("panel");
			}
			else document.body.style.opacity = 1;
		});
	}
	else document.body.style.opacity = 1;
}
function buttons(state) {
	var buttons = document.getElementsByTagName("button");
	if (state === false) {
		for (let i = 0; i < buttons.length; i++) {
			buttons[i].disabled = true;
		}
	}
	else {
		for (let i = 0; i < buttons.length; i++) {
			buttons[i].disabled = false;
		}
	}
}
function last_seen(seconds) {
	if (seconds == -1) return "Not seen in this session";
	let now = Math.round(Date.now() / 1000);
	let diff = now - seconds;
	if (diff < 120) return `Last seen just now`;
	else if (diff < (120 * 60)) return `Last seen ${Math.floor(diff / 60)} minutes ago`;
	else if (diff < (72 * 60 * 60)) return `Last seen ${Math.floor(diff / 60 / 60)} hours ago`;
	return `Last seen ${Math.floor(diff / 60 / 60 / 24)} days ago`;
}
function rminputs() {
	var inputs = document.getElementsByTagName("input");
	for (let i = 0; i < inputs.length; i++) {
		inputs[i].value = "";
	}
}
function post(location, data, callback) {
	var xhr = new XMLHttpRequest();
	xhr.open("POST", location, true);
	xhr.setRequestHeader("Content-Type", "application/json");
	xhr.timeout = 3000;
	xhr.onreadystatechange = function() {
		if (this.readyState === 4) {
			callback(this);
		}
	}
	xhr.send(JSON.stringify(data));
}
function usernameit(div) {
	input = document.getElementById(div);
	value = (input.value).toLowerCase();
	value = value.replace(/[^a-z0-9]/g, "");
	input.value = value;
}
function mkerr(type, to, name, description) {
	var title = document.getElementById(type + "name");
	var desc = document.getElementById(type + "desc");
	var btn = document.getElementById(type + "btn");
	title.innerText = name;
	desc.innerHTML = description;
	btn.onclick = function() {
		showdiv(type, to, true);
	}
}
function login() {
	var user = document.getElementById("name").value;
	var pass = document.getElementById("passwd").value;
	if (user.length < 4 | user.length > 16 | pass.length < 4 | pass.length > 32) {
		return;
	}
	buttons(false);
	dim("login");
	post("panel/api", {
		"method": "auth",
		"name": user,
		"password": pass
	}, function(data) {
		if (data.status == 200) {
			showdiv("login", "succ");
			setCookie(user, pass);
			setTimeout(function() {
				agou("panel");
			}, 4500);
		}
		else {
			showdiv("login", "err");
		}
	});
}
function refresh() {
	var cookie = getCookie();
	if (!cookie["name"] | !cookie["password"]) {
		rmCookie();
	}
	post("panel/api", {
		"method": "get_data",
		"name": cookie["name"],
		"password": cookie["password"]
	}, function(data) {
		if (data.status == 200) {
			var resp = JSON.parse(data.responseText);
			var dbsize = document.getElementById("dbsize");
			var scpu = document.getElementById("scpu");
			var sstorage = document.getElementById("sstorage");
			var loadtext = document.getElementById("loadavg").getElementsByClassName("value")[0];
			var dbtext = document.getElementById("dbusage").getElementsByClassName("value")[0];
			var loadtext2 = document.getElementById("loadavg").getElementsByClassName("tooltip")[0];
			var dbtext2 = document.getElementById("dbusage").getElementsByClassName("tooltip")[0];
			var sstatus = document.getElementById("sstatus");
			var suptime = document.getElementById("suptime");
			var cloadavg = document.getElementById("cloadavg");
			var rss = document.getElementById("rss");
			var accountlist = document.getElementById("accountlist");
			var accountnum = document.getElementById("accountnum");
			accountnum.innerText = resp.userscount + " in total";
			var accounts = "";
			for (var i = 0; i < resp.userscount; i++) {
				let demos = '<p class="demos">' + resp.users[i].demotier + ' days left</p>'
				if (resp.users[i].demotier == -1) demos = "";
				accounts += '<div class="user"><div class="fullname">' + resp.users[i].first_name + ' ' + resp.users[i].last_name + '</div><div class="username"><div class="tiers tier ' + resp.users[i].tier + '"></div><div>' + resp.users[i].username + '</div></div><p class="last_seen">' + last_seen(resp.users[i].last_seen) + '</p><p class="joined">Joined ' + resp.users[i].joined + '</p>' + demos + '<button onclick="deluser(\'' + resp.users[i].username + '\', \'' + resp.users[i].first_name + ' ' + resp.users[i].last_name + '\')">Delete</button><button onclick="resetpass(\'' + resp.users[i].username + '\', \'' + resp.users[i].first_name + ' ' + resp.users[i].last_name + '\')">Reset password</button><button onclick="show_tiers(this)" class="tiers">Set tier</button></div>';
			}
			if (accounts != accountlist.innerHTML) accountlist.innerHTML = accounts;
			maxusers = resp.max_users;
			if (donottouch) {
				donottouch = false;
				maxuserset = maxusers;
				document.getElementById("maxusers").innerText = maxuserset;
			}
			users = resp["userscount"];
			document.getElementById("userlimit").innerText = "Current limit: " + maxusers;
			loadtext.innerHTML = resp.loadavg + "<b>%</b>";
			loadtext2.innerHTML = "Temp.: " + resp.cpu_temp + "°";
			dbtext.innerHTML = resp.db_usage + "<b>%</b>";
			dbtext2.innerHTML = "Using " + resp.userscount + " of " + resp.max_users;
			if (resp.loadavg > 100) setBar("loadavgp", 100);
			else setBar("loadavgp", resp.loadavg);
			if (resp.db_usage > 100) setBar("dbusagep", 100);
			else setBar("dbusagep", resp.db_usage);
			suptime.innerText = mktime(resp.uptime);
			dbsize.innerText = resp.userscount + "/" + resp.max_users + " (" + resp.db_size + " KB)";
			scpu.innerText = resp.cores + " core" + (resp.cores == 1 ? "" : "s");
			sstorage.innerText = resp.storage + " GB";
			rss.innerText = resp.rss ? (resp.rss + " MB") : "N/A";
			var lastref = new Date();
			clearInterval(runningtimex);
			runningtimex = setInterval(function() {
				var ref = new Date();
				var date = Math.round((ref.getTime() - lastref.getTime()) / 1000 + resp.uptime);
				suptime.innerText = mktime(date);
			}, 350);
			cloadavg.innerText = resp.loadavg_raw;
		}
		else if (data.status == 401) {
			rmCookie();
		}
	});
}
function show_tiers(div) {
	let username = div.parentNode.getElementsByClassName("username")[0].innerText;
	let fullname = div.parentNode.getElementsByClassName("fullname")[0].innerText;
	let tier = div.parentNode.getElementsByClassName("tier")[0].className.split(" ")[2];
	let x = document.getElementById("selectos").children;
	for (let i = 0; i < x.length; i++) {
		if (x[i].innerText == tier) x[i].classList.add("selected");
		else x[i].classList.remove("selected");
	}
	document.getElementById("tieruser").innerText = username;
	document.getElementById("tieruser2").innerText = `(${fullname})`;
	showdiv("userlist", "utiers");
}
function select_tier(e) {
	let tier = e.innerText;
	let x = e.parentNode.children;
	for (let i = 0; i < x.length; i++) {
		if (x[i].innerText == tier) x[i].classList.add("selected");
		else x[i].classList.remove("selected");
	}
}
function set_tier() {
	let selected_tier = document.getElementById("selectos");
	selected_tier = selected_tier.getElementsByClassName("selected")[0].innerText.toLowerCase();
	let user = document.getElementById("tieruser").innerText;
	buttons(false);
	let cookie = getCookie();
	post("panel/api", {
		"method": "changetier",
		"username": user,
		"tier": selected_tier,
		"name": cookie["name"],
		"password": cookie["password"]
	}, function(data) {
		buttons();
		if (data.status == 200) {
			showdiv("utiers", "userlist");
		}
		else {
			mkerr("err", "userlist", "Error", "Couldn't change desired user's tier.");
			showdiv("utiers", "err");
		}
	});
}
function index() {
	buttons(false);
	var cokie = getCookie();
	if (!cokie["name"] | !cokie["password"]) {
		gou("panel/login");
	}
	post("panel/api", {
		"method": "auth",
		"name": cokie["name"],
		"password": cokie["password"]
	}, function(data) {
		if (data.status == 200) {
			document.body.style.opacity = 1;
			buttons();
			setCookie(cokie["name"], cokie["password"]);
			setTimeout(function() {
				refresh();
				autoupdate = setInterval(refresh, 4000);
			}, 350);
			post("panel/api", {
				"method": "getconf",
				"name": cokie["name"],
				"password": cokie["password"]
			}, function(data) {
				if (data.status == 200) {
					let conf = JSON.parse(data.responseText);
					document.getElementById("mynotice").value = conf.notice;
					document.getElementById("contact").value = conf.contact_uri;
					if (conf.enable_tiers) document.getElementById("enable_tiers").classList.add("ed");
					document.getElementById("freereq").value = conf.tiers_requirements.free;
					document.getElementById("plusreq").value = conf.tiers_requirements.plus;
					document.getElementById("proreq").value = conf.tiers_requirements.pro;
					document.getElementById("tiers_text").value = conf.tiers_text;
				}
			});
		}
		else {
			gou("panel/login");
		}
	});
}
function dim(div) {
	document.getElementById(div).classList.add("hidden");
}
function showdiv(from, to, back) {
	buttons(false);
	var fromdiv = document.getElementById(from);
	var todiv = document.getElementById(to);
	if (!back) {
		fromdiv.classList.add("ttop");
		fromdiv.classList.add("hidden");
		todiv.classList.add("noanime");
		todiv.classList.add("tbottom");
	}
	else {
		fromdiv.classList.add("tbottom");
		fromdiv.classList.add("hidden");
		todiv.classList.add("noanime");
		todiv.classList.add("ttop");
	}
	todiv.classList.remove("noanime");
	setTimeout(function() {
		window.scrollTo(0, 0);
		fromdiv.style.display = "none";
		todiv.style.display = null;
		fromdiv.classList.add("noanime");
		fromdiv.classList.remove("ttop");
		fromdiv.classList.remove("tbottom");
		fromdiv.classList.remove("noanime");
		setTimeout(function() {
			todiv.classList.remove("ttop");
			todiv.classList.remove("tbottom");
			todiv.classList.remove("hidden");
			buttons();
		}, 50);
	}, 300);
}
function reboot(mhm) {
	if (!mhm) {
		return;
	}
	clearInterval(runningtimex);
	clearInterval(autoupdate);
	cookie = getCookie();
	post("panel/api", {
		"method": "reboot",
		"name": cookie["name"],
		"password": cookie["password"]
	}, function(data) {});
	var progress = document.getElementById("rebutstatus");
	progress.classList.add("rebut");
	setTimeout(function() {
		progress.style.width = "100%";
	}, 1000);
	showdiv("rebootc", "reboot");
	setTimeout(function() {
		showdiv("reboot", "main");
		refresh();
		autoupdate = setInterval(refresh, 5000);
	}, 11000);
	setTimeout(function() {
		progress.classList.remove("rebut");
		progress.style.width = 0;
	}, 12000);
}
function changename() {
	var newname = document.getElementById("newname").value;
	var passwd = document.getElementById("namepasswd").value;
	var cookie = getCookie();
	if (newname.length < 4 | newname.length > 16 | passwd.length < 4 | passwd.length > 32) {
		return;
	}
	buttons(false);
	dim("chgname");
	post("panel/api", {
		"method": "name",
		"name": cookie["name"],
		"newname": newname,
		"password": passwd
	}, function(data) {
		if (data.status == 200) {
			setTimeout(rminputs, 350);
			setCookie(newname, passwd);
			mkerr("succ", "app-settings", "Name changed", "Credentials for Panel updated successfully.");
			showdiv("chgname", "succ");
		}
		else if (data.status == 401) {
			mkerr("err", "chgname", "Unauthorized", "Please check your password.");
			showdiv("chgname", "err");
		}
		else {
			mkerr("err", "chgname", "Error", "Name couldn't be changed.");
			showdiv("chgname", "err");
		}
	});
}
function changepass() {
	var newpass = document.getElementById("newpass").value;
	var newpassconf = document.getElementById("newpassconf").value;
	var passwd = document.getElementById("pass").value;
	var cookie = getCookie();
	if (newpass.length < 4 | newpass.length > 32 | passwd.length < 4 | passwd.length > 32) {
		return;
	}
	buttons(false);
	dim("chgpasswd");
	if (newpass !== newpassconf) {
		mkerr("err", "chgpasswd", "Error", "New passwords do not match.");
		showdiv("chgpasswd", "err");
		return;
	}
	post("panel/api", {
		"method": "passwd",
		"name": cookie["name"],
		"newpass": newpass,
		"password": passwd
	}, function(data) {
		if (data.status == 200) {
			setTimeout(rminputs, 350);
			setCookie(cookie["name"], newpass);
			mkerr("succ", "app-settings", "Password changed", "Credentials for Panel updated successfully.");
			showdiv("chgpasswd", "succ");
		}
		else if (data.status == 401) {
			mkerr("err", "chgpasswd", "Unauthorized", "Please check your current password.");
			showdiv("chgpasswd", "err");
		}
		else {
			mkerr("err", "chgpasswd", "Error", "Password couldn't be changed.");
			showdiv("chgpasswd", "err");
		}
	});
}
function sendmaxusers() {
	var cookie = getCookie();
	buttons(false);
	dim("dblimit");
	post("panel/api", {
		"method": "chgmaxusers",
		"maxusers": maxuserset,
		"name": cookie["name"],
		"password": cookie["password"]
	}, function(data) {
		if (data.status == 200) {
			setTimeout(refresh, 350);
			setTimeout(rminputs, 350);
			mkerr("succ", "userlist", "Database limit changed", "Remember too many users may lead to unexpected results.");
			showdiv("dblimit", "succ");
		}
		else {
			mkerr("err", "dblimit", "Error", "Maximum number of stored accounts couldn't be changed.");
			showdiv("dblimit", "err");
		}
	});
}
function deluser(victim, fullname) {
	todelete = victim;
	todeletefull = fullname;
	document.getElementById("utbd").innerHTML = "<code>" + victim + "</code>" + " (" + fullname + ")";
	showdiv("userlist", "deluserc");
}
function resetpass(victim, fullname) {
	tochange = victim;
	tochangefull = fullname;
	document.getElementById("utbc").innerHTML = "<code>" + victim + "</code>" + " (" + fullname + ")";
	showdiv("userlist", "resetpassc");
}
function delaccount() {
	var cookie = getCookie();
	buttons(false);
	dim("deluserc");
	post("panel/api", {
		"method": "deluser",
		"username": todelete,
		"name": cookie["name"],
		"password": cookie["password"]
	}, function(data) {
		if (data.status == 200) {
			refresh();
			setTimeout(rminputs, 350);
			mkerr("succ", "userlist", "Account deleted", "User <b><code>" + todelete + "</code> (" + todeletefull + ")</b> no longer exists.");
			showdiv("deluserc", "succ");
		}
		else {
			mkerr("err", "userlist", "Error", "User couldn't be deleted.");
			showdiv("deluserc", "err");
		}
		todelete = null;
		todeletefull = null;
	});
}
function genpasswd() {
	var cookie = getCookie();
	buttons(false);
	dim("deluserc");
	post("panel/api", {
		"method": "genuserpass",
		"username": tochange,
		"name": cookie["name"],
		"password": cookie["password"]
	}, function(data) {
		if (data.status == 200) {
			refresh();
			setTimeout(rminputs, 350);
			document.getElementById("utbcr").innerHTML = "<code>" + tochange + "</code>" + " (" + tochangefull + ")";
			document.getElementById("passbox").innerText = data.responseText;
			showdiv("resetpassc", "resetpasswd");
		}
		else {
			mkerr("err", "userlist", "Error", "Couldn't generate new password.");
			showdiv("resetpassc", "err");
		}
		tochange = null;
		tochangefull = null;
	});
}
function purgepass() {
	setTimeout(function() {
		document.getElementById("passbox").innerText = "";
	}, 350);
}

function map(n, a, b, _a, _b) {
	let d = b - a;
	let _d = _b - _a;
	let u = _d / d;
	return _a + n * u;
}
function setBar(id, val) {
	var v = 220 - map(val, 0, 100, 0, 220);
	document.getElementById(id).style.strokeDashoffset = v;
}

function setNotice() {
	let cookie = getCookie();
	let text = document.getElementById("mynotice").value.trim();
	post("panel/api", {
		"method": "setnotice",
		"name": cookie["name"],
		"password": cookie["password"],
		"notice": text
	}, function(data) {
		if (data.status == 200) {
			let un = text == "" ? "" : "un";
			mkerr("succ", "app-settings", "Successful.", `Your notice has been ${un}set.`);
			showdiv("notice", "succ");
		}
		else {
			mkerr("err", "notice", "Error", "Couldn't update your notice.");
			showdiv("notice", "err");
		}
	});
}
function clearNotice() {
	document.getElementById("mynotice").value = ""
}

function setContact() {
	let cookie = getCookie();
	let contact = document.getElementById("contact").value.trim();
	post("panel/api", {
		"method": "setcontact",
		"name": cookie["name"],
		"password": cookie["password"],
		"contact_uri": contact
	}, function(data) {
		if (data.status == 200) {
			mkerr("succ", "app-settings", "Successful.", `Your contact information has been updated.`);
			showdiv("setcontact", "succ");
		}
		else {
			mkerr("err", "setcontact", "Error", "Couldn't update your notice.");
			showdiv("setcontact", "err");
		}
	});
}

function checkbox(elem) {
	elem = elem.getElementsByClassName("check")[0];
	elem.classList.toggle("ed");
}
function setTiers() {
	let cookie = getCookie();
	let enable = document.getElementById("enable_tiers").classList.contains("ed")
	let free = document.getElementById("freereq").value.trim();
	let plus = document.getElementById("plusreq").value.trim();
	let pro = document.getElementById("proreq").value.trim();
	let text = document.getElementById("tiers_text").value.trim();
	post("panel/api", {
		"method": "settiers",
		"name": cookie["name"],
		"password": cookie["password"],
		"enable_tiers": enable,
		"tiers_text": text,
		"tiers_requirements": {free, plus, pro}
	}, function(data) {
		if (data.status == 200) {
			mkerr("succ", "app-settings", "Successful.", "Tiers preferences have been saved.");
			showdiv("tiers", "succ");
		}
		else {
			mkerr("err", "tiers", "Error", "Couldn't update your notice.");
			showdiv("tiers", "err");
		}
	});
}
