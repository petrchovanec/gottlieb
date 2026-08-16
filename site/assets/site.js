(() => {
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".primary-nav");

  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const open = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!open));
      nav.classList.toggle("is-open", !open);
    });

    nav.addEventListener("click", (event) => {
      if (event.target.closest("a")) {
        toggle.setAttribute("aria-expanded", "false");
        nav.classList.remove("is-open");
      }
    });
  }

  const search = document.querySelector("[data-source-search]");
  const status = document.querySelector("[data-source-status]");
  const cards = [...document.querySelectorAll("[data-source-card]")];
  const count = document.querySelector("[data-source-count]");
  const empty = document.querySelector("[data-source-empty]");

  const filterSources = () => {
    const query = (search?.value || "").trim().toLowerCase();
    const selectedStatus = status?.value || "";
    let visible = 0;

    cards.forEach((card) => {
      const matchesQuery = !query || card.dataset.search.includes(query);
      const matchesStatus = !selectedStatus || card.dataset.status === selectedStatus;
      const show = matchesQuery && matchesStatus;
      card.hidden = !show;
      if (show) visible += 1;
    });

    if (count) count.textContent = String(visible);
    if (empty) empty.hidden = visible !== 0;
  };

  search?.addEventListener("input", filterSources);
  status?.addEventListener("change", filterSources);
})();
