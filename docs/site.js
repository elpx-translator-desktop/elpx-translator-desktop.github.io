const REPO = "elpx-translator-desktop/elpx-translator-desktop.github.io";
const API_URL = `https://api.github.com/repos/${REPO}/releases`;

function pickDownloads(assets) {
  const match = (pattern) => assets.find((asset) => pattern.test(asset.name));
  return [
    { label: "Linux", hint: ".deb para Debian y derivados compatibles", asset: match(/\.deb$/i) },
    { label: "Linux", hint: "AppImage para otras distribuciones", asset: match(/\.AppImage$/i) },
    { label: "Windows", hint: ".exe", asset: match(/\.exe$/i) },
    { label: "macOS", hint: ".dmg", asset: match(/\.dmg$/i) },
  ].filter((item) => item.asset);
}

function renderRelease(cardId, release, fallbackText) {
  const card = document.getElementById(cardId);
  if (!card) return;

  const title = card.querySelector("h3");
  const links = card.querySelector(".download-links");

  if (!release) {
    card.classList.add("is-hidden");
    title.textContent = fallbackText;
    links.innerHTML = "";
    return;
  }

  card.classList.remove("is-hidden");
  title.textContent = `${release.name || release.tag_name}`;
  const downloads = pickDownloads(release.assets || []);
  links.innerHTML = downloads.length
    ? downloads.map((item) => `
        <a class="download-link" href="${item.asset.browser_download_url}" target="_blank" rel="noopener noreferrer">
          <span>${item.label}</span>
          <span>Descargar ${item.hint}</span>
        </a>
      `).join("")
    : `<p class="release-copy">La release existe, pero todavía no aparecen artefactos adjuntos.</p>`;
}

async function loadReleases() {
  try {
    const response = await fetch(API_URL, {
      headers: { Accept: "application/vnd.github+json" },
    });
    if (!response.ok) throw new Error("GitHub API error");
    const releases = await response.json();

    const stable = releases.find((release) => !release.prerelease && !release.draft);
    const beta = releases.find((release) => release.prerelease && !release.draft);

    renderRelease("stable-release", stable, "Sin release estable");
    renderRelease("beta-release", beta, "Sin beta publicada");
  } catch (error) {
    renderRelease("stable-release", null, "No disponible");
    renderRelease("beta-release", null, "No disponible");
  }
}

loadReleases();
