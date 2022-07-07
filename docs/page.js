let store = window.localStorage

let rt = document.querySelector(":root")
let darkMode = store.length == 0 ? "T" : store.getItem("dark")

function setDarkMode() {
	rt.style.setProperty("--background-main", "#16171a")
	rt.style.setProperty("--background-sub", "#191c22")
	rt.style.setProperty("--background-c", "#18191c")

	rt.style.setProperty("--text", "#eeeeee")

	darkMode = "T"
}

function setLightMode() {
	rt.style.setProperty("--background-main", "#f2f6ff")
	rt.style.setProperty("--background-sub", "#deeaff")
	rt.style.setProperty("--background-c", "#eceffd")

	rt.style.setProperty("--text", "#121212")

	darkMode = "F"
}

function visitLinkIfVisible(activatedID, link) {
	let activatedElement = document.getElementById(activatedID)
	let activatedElementStyle = window.getComputedStyle(activatedElement)

	if (activatedElementStyle.opacity == 1.0) {
		window.location = link
	}
}

function toggleDarkMode(activatedElementID) {
	let activatedElement = document.getElementById(activatedElementID)
	let activatedElementStyle = window.getComputedStyle(activatedElement)

	if (activatedElementStyle.opacity == 1.0) {
		if (darkMode == "T") {
			setLightMode()
			store.setItem("dark", darkMode)
		}
		else {
			setDarkMode()
			store.setItem("dark", darkMode)
		}
	}
}

setTimeout(() => {
	rt.style.setProperty("transition", "0.4s");

	let trElems = document.getElementsByClassName("tr");
	for (let i = 0; i < trElems.length; i++) {
		trElems[i].style.setProperty("transition", "0.4s");
	}
}, 250);



// Stuff to run on page load

document.getElementById("footer").innerHTML = `
<div width="80%" class="vcenter">
	<p class="center">Site &amp; Project by <a href="https://github.com/Fr75s">Fr75s.</a>
	<br>
	<a href="https://github.com/Fr75s/bigscraperqt">Source Code</a>
	<a href="https://discord.gg/DUAFMgrhAY">Discord (Support)</a>
	</p>

</div>
`

if (darkMode == "T") {
	setDarkMode()
}
else {
	setLightMode()
}
