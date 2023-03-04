function prepareGallery() {
	let g = document.getElementsByClassName("gallery")[0].children;
	for (let item of g) {
		item.onclick = function() {showPhoto(item)};
	}
}

function basename(uri) {
	return uri.slice(uri.lastIndexOf("/") + 1);
}

function showPhoto(e) {
	e.classList.add("hidden");
	let preview = document.getElementById("preview");
	preview.src = e.src;
	preview.classList.remove("hidden");
	document.getElementById("photo_helper").classList.remove("hidden");
	document.getElementById("photo_name").innerText = basename(e.src);
}

function hidePhoto(e) {
	e.classList.add("hidden");
	document.getElementById("photo_helper").classList.add("hidden");
	let imgs = document.getElementsByClassName("gallery")[0].children;
	for (let item of imgs) {
		if (item.src == e.src) {
			item.classList.remove("hidden");
			break;
		}
	}
}

function photo_move(n) {
	let g = document.getElementsByClassName("gallery")[0].children;
	for (let i = 0; i < g.length; i++) {
		let current = g[i].classList.contains("hidden");
		let target = i + n;
		if (current && target >= 0 && g.length > target) {
			g[i].classList.add("hidden");
			hidePhoto(g[i]);
			showPhoto(g[target]);
			break;
		}
	}
}