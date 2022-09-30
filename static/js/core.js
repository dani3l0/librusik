var current = 0;
console.log(" _     _ _                    _ _    \n| |   (_) |__  _ __ _   _ ___(_) | __\n| |   | | '_ \\| '__| | | / __| | |/ /\n| |___| | |_) | |  | |_| \\__ \\ |   < \n|_____|_|_.__/|_|   \\__,_|___/_|_|\\_\\ \n                                      ");
console.log("You are here at your own risk.");
function konfeti() {
	let confetti = new Confetti('body');
	confetti.setCount(100);
	confetti.setSize(1);
	confetti.setPower(25);
	confetti.setFade(false);
	confetti.destroyTarget(false);
}

function gou(where) {
	window.location.href = where;
}
function agou(where) {
	document.body.style.opacity = 0;
	setTimeout(function() {
		window.location.href = where;
	}, 320);
}
function setCookie(user, pass) {
	var cvalue = {
		"username": user.split('').reverse().join(''),
		"password": pass.split('').reverse().join('')
	}
	var d = new Date();
	d.setTime(d.getTime() + (28 * 24 * 60 * 60 * 1000));
	var expires = "expires=" + d.toUTCString();
	document.cookie = "librusik_u=" + encodeURIComponent(JSON.stringify(cvalue)) + ";" + expires + "; path=/";
}
function getCookie(cname) {
	var name = "librusik_u=";
	var ca = document.cookie.split(';');
	for (var i = 0; i < ca.length; i++) {
		var c = ca[i];
		while (c.charAt(0) == ' ') {
			c = c.substring(1);
		}
		if (c.indexOf(name) == 0) {
			let meh = JSON.parse(decodeURIComponent(c.substring(name.length, c.length)));
			meh["username"] = meh["username"].split('').reverse().join('');
			meh["password"] = meh["password"].split('').reverse().join('');
			return meh;
		}
	}
	return {};
}
function rmCookie() {
	document.cookie = "librusik_u={}; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/";
	agou("login");
}
function indexpage() {
	buttons(true);
	var cokie = getCookie();
	if (!cokie["username"] | !cokie["password"]) {
		gou("login");
		return;
	}
	document.body.style.opacity = 1;
	setCookie(cokie["username"], cokie["password"]);
	goto('home', 0, true);
	post("api", {
		"username": cokie["username"],
		"password": cokie["password"],
		"method": "get_me"
	}, function(data) {
		let resp = JSON.parse(data.responseText);
		if (resp.confetti) konfeti();
	});
}
function loginpage() {
	rminputs();
	var cokie = getCookie();
	if (!cokie["username"] | !cokie["password"]) {
		document.body.style.opacity = 1;
		return;
	}
	buttons(false);
	post("auth", {
		"username": cokie["username"],
		"password": cokie["password"]
	}, function(data) {
		if (data.status == 200) gou(".");
		else document.body.style.opacity = 1;
		buttons();
	});
}
function errorpage() {
	document.body.style.opacity = 1;
	var button = document.getElementById("returnbtn");
	button.onclick = function() {
		agou("");
	}
	return;
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
	xhr.timeout = 1500000;
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
	desc.innerText = description;
	btn.onclick = function() {
		showdiv(type, to, true);
	}
}
function login() {
	var user = document.getElementById("user").value;
	var pass = document.getElementById("passwd").value;
	if (user.length < 4 | user.length > 16 | pass.length < 4 | pass.length > 32) {
		return;
	}
	buttons(false);
	dim("login");
	post("auth", {
		"username": user,
		"password": pass
	}, function(data) {
		if (data.status == 200) {
			mkerr("succ", "succ", "Logged in", "You will be redirected in few seconds.");
			showdiv("login", "succ");
			setCookie(user, pass);
			setTimeout(function() {
				agou("");
			}, 4500);
		}
		else if (data.status == 401) {
			mkerr("err", "login", "Unauthorized", "Provided credentials are invalid.");
			showdiv("login", "err");
		}
		else {
			mkerr("err", "login", "Error", "Couldn't log in.");
			showdiv("login", "err");
		}
	});
}
function register() {
	var user = document.getElementById("nuser").value;
	var pass = document.getElementById("npasswd").value;
	var passc = document.getElementById("npasswdc").value;
	if (user.length < 4 | user.length > 16 | pass.length < 4 | pass.length > 32) {
		return;
	}
	buttons(false);
	dim("register");
	if (pass !== passc) {
		mkerr("err", "register", "Error", "Passwords do not match.");
		showdiv("register", "err");
		return;
	}
	var libruslogin = document.getElementById("l_user").value;
	var libruspass = document.getElementById("l_passwd").value;
	post("api", {
		"method": "mkaccount",
		"username": user,
		"password": pass,
		"librusLogin": libruslogin,
		"librusPassword": libruspass
	}, function(data) {
		if (data.status == 200) {
			mkerr("succ", "register", "Account created", "Hope you will enjoy using Librusik...");
			showdiv("register", "succ");
			setCookie(user, pass);
			setTimeout(function() {
				agou(".")
			}, 4500);
		}
		else if (data.status == 403) {
			mkerr("err", "register", "Error", data.responseText);
			showdiv("register", "err");
		}
		else {
			mkerr("err", "register", "Error", "Account couldn't be created.");
			showdiv("register", "err");
		}
	});
}
function delacc() {
	var confirmation = document.getElementById("delaccconf").value.toLowerCase();
	var passwor = document.getElementById("delaccpasswd").value;
	if (passwor.length < 4 | passwor.length > 32 | confirmation.toLowerCase().replace(/[^a-z0-9]/g, "") != "yesiamtotallysure") {
		return;
	}
	buttons(false);
	dim("rmaccount");
	var cookie = getCookie();
	post("api", {
		"username": cookie["username"],
		"password": passwor,
		"method": "delaccount"
	}, function(data) {
		if (data.status == 200) {
			document.cookie = "librusik_u={}; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/";
			mkerr("succ", "succ", "Account is gone", "Come back soon!");
			var btns = document.getElementsByTagName('button');
			for (var i = 0; i < btns.length; i++) {
				btns[i].onclick = null;
			}
			showdiv("rmaccount", "succ");
			setTimeout(function() {
				agou("login");
			}, 4500);
		}
		else if (data.status == 401) {
			mkerr("err", "rmaccount", "Unauthorized", "Please check your password.");
			showdiv("rmaccount", "err");
		}
		else {
			mkerr("err", "rmaccount", "Error", "Account couldn't be deleted.");
			showdiv("rmaccount", "err");
		}
	});
}
function changepasswd() {
	var newpass = document.getElementById("newpass").value;
	var newpassc = document.getElementById("newpassc").value;
	var pasword = document.getElementById("pass").value;
	if (newpass.length < 4 | newpass.length > 32 | pasword.length < 4 | pasword.length > 32) {
		return;
	}
	buttons(false);
	if (newpass !== newpassc) {
		mkerr("err", "chgpasswd", "Error", "Passwords do not match.");
		showdiv("chgpasswd", "err");
		return;
	}
	dim("chgpasswd");
	var cookie = getCookie();
	post("api", {
		"method": "chgpasswd",
		"username": cookie["username"],
		"password": pasword,
		"newpassword": newpass
	}, function(data) {
		if (data.status == 200) {
			setTimeout(rminputs, 320);
			setCookie(cookie["username"], newpass);
			mkerr("succ", "settings", "Password changed", "You're safe.");
			showdiv("chgpasswd", "succ")
		}
		else if (data.status == 401) {
			mkerr("err", "chgpasswd", "Unauthorized", "Please check your password.");
			showdiv("chgpasswd", "err")
		}
		else {
			mkerr("err", "chgpasswd", "Error", "Password couldn't be changed.");
			showdiv("chgpasswd", "err");
		}
	});
}
function newspass() {
	var newpass = document.getElementById("newspasswd").value;
	var pass = document.getElementById("newslibrusikpasswd").value;
	if (newpass.length < 4 | newpass.length > 32 | pass.length < 4 | pass.length > 32) {
		return;
	}
	buttons(false);
	dim("newsynergiapass");
	var cookie = getCookie();
	post("api", {
		"method": "chglibruspasswd",
		"username": cookie["username"],
		"password": pass,
		"newLibrusPassword": newpass
	}, function(data) {
		if (data.status == 200) {
			setTimeout(rminputs, 320);
			mkerr("succ", "synergie", "Password changed", "You can continue using Librusik.");
			showdiv("newsynergiapass", "succ")
		}
		else if (data.status == 401) {
			mkerr("err", "newsynergiapass", "Unauthorized", "Please check your password.");
			showdiv("newsynergiapass", "err")
		}
		else if (data.status == 403) {
			mkerr("err", "newsynergiapass", "Forbidden", data.responseText);
			showdiv("newsynergiapass", "err")
		}
		else {
			mkerr("err", "newsynergiapass", "Error", "Password for your Synergia account couldn't be changed.");
			showdiv("newsynergiapass", "err");
		}
	});
}
function newsaccount() {
	var newlogin = document.getElementById("newslogin").value;
	var newpass = document.getElementById("newspassword").value;
	var pass = document.getElementById("newslibrusikpass").value;
	if (newlogin.length < 4 | newlogin.length > 32 | newpass.length < 4 | newpass.length > 32 | pass.length < 4 | pass.length > 32) {
		return;
	}
	buttons(false);
	dim("newsynergia");
	var cookie = getCookie();
	post("api", {
		"method": "chglibrus",
		"username": cookie["username"],
		"password": pass,
		"newLibrusLogin": newlogin,
		"newLibrusPassword": newpass
	}, function(data) {
		if (data.status == 200) {
			setTimeout(rminputs, 320);
			mkerr("succ", "settings", "Synergia configured", "You can now continue using Librusik with your new Synergia account.");
			showdiv("newsynergia", "succ")
		}
		else if (data.status == 401) {
			mkerr("err", "newsynergia", "Unauthorized", "Please check your password.");
			showdiv("newsynergia", "err")
		}
		else if (data.status == 403) {
			mkerr("err", "newsynergia", "Forbidden", data.responseText);
			showdiv("newsynergia", "err")
		}
		else {
			mkerr("err", "newsynergia", "Error", "Synergia account couldn't be configured.");
			showdiv("newsynergia", "err");
		}
	});
}
function dim(div) {
	document.getElementById(div).classList.add("ttop");
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
function headchoice(from, to, btn) {
	buttons(false);
	let btnz = btn.parentNode.getElementsByTagName("div");
	for (var i = 0; i < btnz.length; i++) btnz[i].classList.remove("selected");
	btn.classList.add("selected");
	var fromdiv = document.getElementById(from);
	var todiv = document.getElementById(to);
	fromdiv.classList.add("hidden");
	setTimeout(function() {
		fromdiv.style.display = "none";
		todiv.style.display = null;
		setTimeout(function() {
			todiv.classList.remove("hidden");
			buttons();
		}, 50);
	}, 300);
}
function checkmsg(url) {
	if (url !== "home") return;
	var cokie = getCookie();
	post("api", {
		"method": "getstuff",
		"username": cokie["username"],
		"password": cokie["password"]
	}, function(data) {
		try {
			var messages = document.getElementById("messages");
			var messagest = messages.getElementsByTagName("div")[0];
			if (!messages) return;
			var lucky = document.getElementById("luckynum");
			var luckyt = lucky.getElementsByTagName("div")[0];
			if (data.status == 200) {
				document.getElementById("datafetcher").classList.add("hidden");
				var k = JSON.parse(data.responseText);
				if (k.messages > 0) {
					let addon = "s";
					if (k.messages == 1) addon = "";
					messagest.innerText =  k.messages + " new message" + addon;
					messages.classList.add("unread");
				}
				else messagest.innerText = "No new messages"
				messages.classList.remove("hidden");
				if (k.luckynum == "None") luckyt.innerText = "It seems there is no lucky number at this moment.";
				else {
					lucky.classList.add("yes");
					luckyt.innerHTML = "Today's lucky number is <b>" + k.luckynum + "</b>";
				}
				setTimeout(function() {
					messages.style.opacity = null;
				}, 300);
				setTimeout(function() {
					lucky.classList.remove("hidden");
				}, 1000);
			}
		}
		catch {}
	});
}
function goto(url, page, force, back) {
	var div = document.getElementById("content");
	var pages = document.getElementsByClassName("panelitem");
	pages[current].classList.remove("active");
	pages[page].classList.add("active");
	buttons(false);
	if (page > current) {
		div.classList.add("tleft");
		setTimeout(function(){
			div.classList.add("noanime");
			div.classList.remove("tleft");
			div.classList.add("tright");
		}, 300);
	}
	else if (page < current) {
		div.classList.add("tright");
		setTimeout(function(){
			div.classList.add("noanime");
			div.classList.remove("tright");
			div.classList.add("tleft");
		}, 300);
	}
	else if (force === true) {
		if (!back) {
			div.classList.add("ttop");
			setTimeout(function() {
				div.classList.add("noanime");
				div.classList.remove("ttop");
				div.classList.add("tbottom");
			}, 300);
		}
		else {
			div.classList.add("tbottom");
			setTimeout(function() {
				div.classList.add("noanime");
				div.classList.remove("tbottom");
				div.classList.add("ttop");
			}, 300);
		}
	}
	div.classList.add("hidden");
	current = page;
	var cookie = getCookie();
	var xhr = new XMLHttpRequest();
	var xhrstart = (new Date()).getTime()
	xhr.open("POST", url);
	xhr.timeout = 10000;
	xhr.setRequestHeader("Content-Type", "application/json");
	var svg = '<svg class="svge" viewBox="0 0 24 24"><path d="M11 15h2v2h-2v-2zm0-8h2v6h-2V7zm.99-5C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"/></svg>';
	xhr.onreadystatechange = function() {
		if (this.readyState !== 4) return;
		var fasten = 450 - (((new Date()).getTime()) - xhrstart);
		if (fasten <= 0) {
			fasten = 0;
		}
		var thys = this;
		setTimeout(function() {
			window.scrollTo(0, 0);
			if (thys.readyState === 4) {
				if (thys.status == 401) {
					rmCookie();
					return;
				}
				else if (thys.status == 0) div.innerHTML = svg + '<div class="error">Connection lost</div><div class="suggestion">Please check your Internet connection.</div><button class="highlighted" onclick="goto(\'' + url + '\', ' + page + ', \'true\')">Try again</button>';
				else div.innerHTML = thys.responseText;
				div.classList.remove("noanime");
				div.classList.remove("tright");
				div.classList.remove("tleft");
				div.classList.remove("ttop");
				div.classList.remove("tbottom");
				div.classList.remove("hidden");
				setTimeout(buttons, 100);
				checkmsg(url);
			}
		}, fasten);
	}
	xhr.ontimeout = function() {
		div.innerHTML = svg + '<div class="error">Timeout</div><div class="suggestion">This request took too much time.</div><button onclick="goto(\'' + url + '\', ' + page + ', \'true\')">Try again</button>';
		div.classList.remove("hidden");
		buttons();
	}
	xhr.send(JSON.stringify({
		"username": cookie["username"],
		"password": cookie["password"]
	}));
}
function uploadPic(field) {
	var cookie = getCookie();
	var files = field.files;
	var info = document.getElementById("uploadpicbtn").getElementsByClassName("subtitle")[0];
	info.classList.remove("err");
	if (files.length === 0) {
		info.innerText = "Up to 4 MB, but should not be bigger than 1000px";
		return;
	};
	var filename = files[0].name;
	if (files[0].size === 0) {
		info.classList.add("err");
		info.innerText = "File is empty!";
		return;
	}
	if (files[0].size > 4000000) {
		info.classList.add("err");
		info.innerText = "File is too big! (" + Math.round(files[0].size / 1000 / 10) / 100 + " MB / 4.00 MB)"
		return;
	}
	buttons(false);
	info.innerText = "Please wait...";
	var xhr = new XMLHttpRequest();
	xhr.open("POST", "api/uploadProfilePic", true);
	xhr.onload = function() {
		buttons();
		if (this.status == 200) goto('settings', 3, true, true);
		else {
			info.classList.add("err");
			info.innerText = "File is invalid or it's too big!";
		}
	};
	var stuff = new FormData();
	var file = field.files[0];
	stuff.append("file", file);
	stuff.append("username", cookie["username"]);
	stuff.append("password", cookie["password"]);
	console.log(stuff)
	xhr.send(stuff);
}
function setProfilePic(pic) {
	buttons(false);
	var cookie = getCookie();
	var xhr = new XMLHttpRequest();
	xhr.open("POST", "api/setProfilePic", true);
	xhr.onload = function() {
		buttons();
		if (this.status == 200) goto('settings', 3, true, true);
	};
	xhr.send(JSON.stringify({
		"username": cookie["username"],
		"password": cookie["password"],
		"picture": pic
	}));
}
function loadimg(elem) {
	elem.style.opacity = 1;
}
function getGrades() {
	let items = document.getElementById("averages").getElementsByTagName('input');
	let arr = [];
	for (var i = 0; i < items.length; i++) {
		arr.push(parseInt(items[i].value, 10));
	}
	return arr;
}
function sum(arr) {
	let r = 0;
	for (var i = 0; i < arr.length; i++) {
		r += arr[i]
	}
	return r;
}
function parseGrade(val) {
	if (val < 1) val = 1;
	else if (val > 6) val = 6;
	return val;
}
function parseInp(elem) {
	elem.scrollLeft = elem.scrollWidth;
	let val = elem.value.charAt(elem.value.length - 1);
	let isnum = /^\d+$/.test(val);
	let defn = elem.parentNode.getElementsByTagName("i")[0];
	if (!isnum) {
		elem.value = defn.innerText;
		defn.classList.remove('s');
		elem.blur();
		return;
	}
	if (val == defn.innerText) defn.classList.remove('s');
	else defn.classList.add('s');
	val = parseInt(val, 10);
	val = parseGrade(val);
	elem.value = val;
}
function calc(elem) {
	parseInp(elem);
	let grds = getGrades();
	document.getElementById('avg').innerText = (Math.round(sum(grds) * 100 / grds.length) / 100).toFixed(2);
}

// Czeka na papieżową
setInterval(function() {
	let active = document.getElementById('papaj');
	let time = new Date();
	time = `${time.getHours()}:${time.getMinutes()}`;
	if (time === "21:37") {
		if (active) return;
		let link = document.createElement('link');
		link.setAttribute('rel', 'stylesheet');
		link.setAttribute('href', 'css/papiez.css');
		link.setAttribute('id', 'papaj');
		document.head.appendChild(link);
	}
	else {
		if (!active) return;
		active.remove();
	}
}, 1000);

let timout = {};
function checkbox(elem) {
	elem = elem.getElementsByClassName("check")[0];
	elem.classList.toggle("ed");
}
function featureTile(elem, action) {
	var cokie = getCookie();
	checkbox(elem);
	clearTimeout(timout[action]);
	timout[action] = setTimeout(function() {
		post("api", {
			"method": action,
			"username": cokie["username"],
			"password": cokie["password"],
			"value": elem.getElementsByClassName("check")[0].classList.contains("ed")
		}, function(data) {});
	}, 1500);
}
function restartApp() {
	document.body.style.opacity = 0;
	setTimeout(function() {
		gou('.');
	}, 1500);
}