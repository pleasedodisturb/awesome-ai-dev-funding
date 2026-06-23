// Awesome AI Dev Funding — single-page filter/sort/search.
// Reads ./data/programs.json (relative to where the page is served).

const DATA_URL = "./data/programs.json";

const state = {
  programs: [],
  filtered: [],
  sortKey: "status",
  sortDir: 1,  // 1 asc, -1 desc
};

const dotClass = (p) => {
  if (p.status === "closed") return "red";
  if (p.status === "conditional") return "yellow";
  // open
  if (p.solo_ok === "yes") return "green";
  if (p.solo_ok === "conditional") return "yellow";
  if (p.solo_ok === "no") return "orange";
  return "grey";
};

const STATUS_RANK = { open: 0, conditional: 1, closed: 2, unknown: 3 };
const SOLO_RANK   = { yes: 0, conditional: 1, no: 2, unknown: 3 };

function fmt(p, key) {
  if (key === "amount_max_usd") return p.amount;
  if (key === "category") return p.category;
  return p[key] ?? "";
}

function compareBy(key, dir) {
  return (a, b) => {
    let av, bv;
    if (key === "status")             { av = STATUS_RANK[a.status]; bv = STATUS_RANK[b.status]; }
    else if (key === "solo_ok")       { av = SOLO_RANK[a.solo_ok]; bv = SOLO_RANK[b.solo_ok]; }
    else if (key === "amount_max_usd"){ av = a.amount_max_usd ?? -1; bv = b.amount_max_usd ?? -1; }
    else                              { av = (a[key] ?? "").toString().toLowerCase(); bv = (b[key] ?? "").toString().toLowerCase(); }
    if (av < bv) return -1 * dir;
    if (av > bv) return  1 * dir;
    // tiebreaker: name asc
    return a.name.localeCompare(b.name);
  };
}

function applyFilters() {
  const q       = document.getElementById("search").value.trim().toLowerCase();
  const cat     = document.getElementById("category").value;
  const status  = document.getElementById("status").value;
  const solo    = document.getElementById("solo").value;
  const friendly = document.getElementById("solo-friendly").checked;

  state.filtered = state.programs.filter(p => {
    if (cat    && p.category_id !== cat) return false;
    if (status && p.status      !== status) return false;
    if (solo   && p.solo_ok     !== solo) return false;
    if (friendly && !(p.status === "open" && p.solo_ok === "yes")) return false;
    if (q) {
      const hay = [p.name, p.notes, p.entity, p.geography, p.amount, p.type, p.category]
        .join(" ").toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });
  state.filtered.sort(compareBy(state.sortKey, state.sortDir));
  render();
}

function render() {
  const tbody = document.querySelector("#programs tbody");
  tbody.innerHTML = "";
  const frag = document.createDocumentFragment();
  for (const p of state.filtered) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><span class="dot ${dotClass(p)}" title="${p.status} / solo: ${p.solo_ok}"></span></td>
      <td class="program-name"><a href="${p.url}" target="_blank" rel="noopener">${escape(p.name)}</a></td>
      <td><span class="cat-pill">${escape(p.category)}</span></td>
      <td class="amount">${escape(p.amount)}</td>
      <td>${escape(p.type)}</td>
      <td>${escape(p.solo_ok_raw || p.solo_ok)}</td>
      <td>${escape(p.geography)}</td>
      <td class="notes">${escape(p.notes)}</td>
    `;
    frag.appendChild(tr);
  }
  tbody.appendChild(frag);
  document.getElementById("count").textContent =
    `${state.filtered.length} of ${state.programs.length} programs`;
  // sort indicator
  document.querySelectorAll("th[data-sort]").forEach(th => {
    th.classList.remove("sorted-asc", "sorted-desc");
    if (th.dataset.sort === state.sortKey) {
      th.classList.add(state.sortDir === 1 ? "sorted-asc" : "sorted-desc");
    }
  });
}

function escape(s) {
  return (s ?? "").toString()
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

async function init() {
  const res = await fetch(DATA_URL);
  if (!res.ok) {
    document.getElementById("count").textContent = "Failed to load data.";
    return;
  }
  const data = await res.json();
  state.programs = data.programs;
  document.getElementById("last-verified").textContent = data.last_verified;

  // populate category select
  const catSel = document.getElementById("category");
  for (const c of data.categories) {
    const o = document.createElement("option");
    o.value = c.id; o.textContent = c.label;
    catSel.appendChild(o);
  }

  // wire events
  for (const id of ["search", "category", "status", "solo", "solo-friendly"]) {
    document.getElementById(id).addEventListener("input", applyFilters);
  }
  document.querySelectorAll("th[data-sort]").forEach(th => {
    th.addEventListener("click", () => {
      const key = th.dataset.sort;
      if (state.sortKey === key) state.sortDir *= -1;
      else { state.sortKey = key; state.sortDir = key === "amount_max_usd" ? -1 : 1; }
      applyFilters();
    });
  });

  // URL hash deep links: #cat=ai-lab-credits&solo=yes
  const params = new URLSearchParams(location.hash.slice(1));
  if (params.get("cat"))  document.getElementById("category").value = params.get("cat");
  if (params.get("status")) document.getElementById("status").value = params.get("status");
  if (params.get("solo")) document.getElementById("solo").value = params.get("solo");
  if (params.get("q"))    document.getElementById("search").value = params.get("q");

  applyFilters();
}

init();
