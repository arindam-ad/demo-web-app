let categories = [];
let businesses = [];

const state = {
  query: "",
  location: "",
  category: "",
  sort: "recommended",
  filters: {
    openNow: false,
    verified: false,
    topRated: false,
    deals: false
  },
  saved: new Set(),
  selectedId: null,
  activeBusinessId: null
};

const categoryGrid = document.getElementById("categoryGrid");
const resultsList = document.getElementById("resultsList");
const resultsCount = document.getElementById("resultsCount");
const resultsTitle = document.getElementById("resultsTitle");
const detailPanel = document.getElementById("detailPanel");
const searchInput = document.getElementById("searchInput");
const locationSelect = document.getElementById("locationSelect");
const sortSelect = document.getElementById("sortSelect");
const savedCount = document.getElementById("savedCount");
const enquiryDrawer = document.getElementById("enquiryDrawer");
const submissionNote = document.getElementById("submissionNote");
const requirementInput = document.getElementById("requirementInput");

async function init() {
  try {
    await loadDirectoryData();
    renderCategories();
    bindEvents();
    state.selectedId = businesses[0]?.id || null;
    render();
  } catch (error) {
    resultsList.innerHTML = `
      <article class="listing-card">
        <h4 class="listing-name">Could not load Python API data</h4>
        <p class="listing-description">Start the app with python app.py and refresh this page.</p>
      </article>
    `;
    console.error(error);
  }
}

async function loadDirectoryData() {
  const [categoryResponse, businessResponse] = await Promise.all([
    fetch("/api/categories"),
    fetch("/api/businesses")
  ]);

  if (!categoryResponse.ok || !businessResponse.ok) {
    throw new Error("Directory API request failed");
  }

  const categoryData = await categoryResponse.json();
  const businessData = await businessResponse.json();
  categories = categoryData.categories || [];
  businesses = businessData.businesses || [];
}

function bindEvents() {
  document.getElementById("searchForm").addEventListener("submit", (event) => {
    event.preventDefault();
    state.query = searchInput.value.trim();
    state.category = findMatchingCategory(state.query);
    state.location = locationSelect.value;
    render();
  });

  document.querySelectorAll(".quick-pills button").forEach((button) => {
    button.addEventListener("click", () => {
      const query = button.dataset.query || "";
      searchInput.value = query;
      state.query = query;
      state.category = findMatchingCategory(query);
      render();
    });
  });

  document.querySelectorAll(".filter-chip").forEach((button) => {
    button.addEventListener("click", () => {
      const key = button.dataset.filter;
      state.filters[key] = !state.filters[key];
      button.classList.toggle("active", state.filters[key]);
      render();
    });
  });

  sortSelect.addEventListener("change", () => {
    state.sort = sortSelect.value;
    render();
  });

  document.getElementById("ctaLead").addEventListener("click", () => openDrawer());
  document.getElementById("promoLead").addEventListener("click", () => openDrawer());
  document.getElementById("savedToggle").addEventListener("click", () => {
    if (state.saved.size === 0) {
      submissionNote.textContent = "Save a few listings to showcase shortlist behavior.";
      return openDrawer();
    }
    state.query = "";
    searchInput.value = "";
    state.category = "";
    render(true);
  });

  document.getElementById("closeDrawer").addEventListener("click", closeDrawer);

  enquiryDrawer.addEventListener("click", (event) => {
    if (event.target === enquiryDrawer) {
      closeDrawer();
    }
  });

  document.getElementById("enquiryForm").addEventListener("submit", submitEnquiry);
}

function findMatchingCategory(query) {
  const normalized = query.trim().toLowerCase();
  const match = categories.find((category) => category.name.toLowerCase() === normalized);
  return match ? match.name : "";
}

function renderCategories() {
  categoryGrid.innerHTML = categories
    .map((category) => `
      <button class="category-button${state.category === category.name ? " active" : ""}" type="button" data-category="${category.name}">
        <strong>${category.icon}</strong>
        <span>${category.name}</span>
        <span>${category.count}</span>
      </button>
    `)
    .join("");

  categoryGrid.querySelectorAll(".category-button").forEach((button) => {
    button.addEventListener("click", () => {
      const nextCategory = button.dataset.category;
      state.category = state.category === nextCategory ? "" : nextCategory;
      state.query = nextCategory || "";
      searchInput.value = state.query;
      render();
    });
  });
}

function getFilteredBusinesses(savedOnly = false) {
  const query = state.query.toLowerCase();

  let filtered = businesses.filter((business) => {
    const matchesSaved = !savedOnly || state.saved.has(business.id);
    const matchesLocation = !state.location || business.area === state.location;
    const matchesCategory = !state.category || business.category === state.category;
    const matchesQuery =
      !query ||
      business.name.toLowerCase().includes(query) ||
      business.category.toLowerCase().includes(query) ||
      business.summary.toLowerCase().includes(query) ||
      business.services.some((service) => service.toLowerCase().includes(query));

    const matchesOpen = !state.filters.openNow || business.openNow;
    const matchesVerified = !state.filters.verified || business.verified;
    const matchesTopRated = !state.filters.topRated || business.rating >= 4.5;
    const matchesDeals = !state.filters.deals || Boolean(business.offer);

    return matchesSaved &&
      matchesLocation &&
      matchesCategory &&
      matchesQuery &&
      matchesOpen &&
      matchesVerified &&
      matchesTopRated &&
      matchesDeals;
  });

  filtered = filtered.sort((a, b) => {
    if (state.sort === "rating") {
      return b.rating - a.rating;
    }
    if (state.sort === "reviews") {
      return b.reviews - a.reviews;
    }
    if (state.sort === "deals") {
      return Number(Boolean(b.offer)) - Number(Boolean(a.offer));
    }

    const scoreA = Number(a.premium) * 5 + Number(a.verified) * 3 + a.rating;
    const scoreB = Number(b.premium) * 5 + Number(b.verified) * 3 + b.rating;
    return scoreB - scoreA;
  });

  return filtered;
}

function render(savedOnly = false) {
  renderCategories();

  const filtered = getFilteredBusinesses(savedOnly);
  const title = savedOnly
    ? "Saved businesses"
    : state.category
      ? `${state.category} near ${state.location || "all areas"}`
      : state.query
        ? `Search results for "${state.query}"`
        : "Recommended businesses";

  resultsTitle.textContent = title;
  resultsCount.textContent = `${filtered.length} listing${filtered.length === 1 ? "" : "s"}`;

  if (!filtered.length) {
    resultsList.innerHTML = `
      <article class="listing-card">
        <div class="listing-top">
          <div>
            <h4 class="listing-name">No exact matches found</h4>
            <p class="listing-description">Try another category, clear a filter, or switch the area to showcase broader discovery.</p>
          </div>
        </div>
      </article>
    `;
    detailPanel.innerHTML = `
      <div class="detail-placeholder">
        <p class="eyebrow">Business Preview</p>
        <h3>Nothing selected</h3>
        <p>Your filters are too narrow for the current mock dataset.</p>
      </div>
    `;
    return;
  }

  if (!filtered.some((business) => business.id === state.selectedId)) {
    state.selectedId = filtered[0].id;
  }

  resultsList.innerHTML = filtered.map(renderListingCard).join("");

  resultsList.querySelectorAll("[data-select-id]").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedId = Number(button.dataset.selectId);
      renderDetail();
      highlightSelected();
    });
  });

  resultsList.querySelectorAll("[data-save-id]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      const id = Number(button.dataset.saveId);
      toggleSave(id);
      render(savedOnly);
    });
  });

  resultsList.querySelectorAll("[data-enquiry-id]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      const business = businesses.find((item) => item.id === Number(button.dataset.enquiryId));
      openDrawer(business);
    });
  });

  renderDetail();
  highlightSelected();
  savedCount.textContent = String(state.saved.size);
}

function renderListingCard(business) {
  const badges = [
    business.verified ? '<span class="verified">Verified</span>' : "",
    business.premium ? '<span class="premium">Premium</span>' : "",
    business.offer ? `<span class="offer-pill">${business.offer}</span>` : ""
  ].join(" ");

  return `
    <article class="listing-card${state.selectedId === business.id ? " selected" : ""}" data-select-id="${business.id}">
      <div class="listing-top">
        <div>
          <h4 class="listing-name">${business.name}</h4>
          <div class="detail-badges">${badges}</div>
        </div>
        <div class="rating-pill">${business.rating} / 5</div>
      </div>
      <div class="listing-meta">
        <span>${business.category}</span>
        <span>${business.area}</span>
        <span>${business.reviews} reviews</span>
        <span>${business.openNow ? "Open now" : "Closed for now"}</span>
        <span>${business.priceBand}</span>
      </div>
      <p class="listing-description">${business.summary}</p>
      <div class="listing-actions">
        <button class="listing-action primary-lite" type="button" data-enquiry-id="${business.id}">Send Enquiry</button>
        <button class="listing-action" type="button" data-select-id="${business.id}">View Details</button>
        <button class="listing-action" type="button" data-save-id="${business.id}">
          ${state.saved.has(business.id) ? "Saved" : "Save"}
        </button>
      </div>
    </article>
  `;
}

function highlightSelected() {
  resultsList.querySelectorAll(".listing-card").forEach((card) => {
    const selected = Number(card.dataset.selectId) === state.selectedId;
    card.classList.toggle("selected", selected);
  });
}

function renderDetail() {
  const business = businesses.find((item) => item.id === state.selectedId);
  if (!business) {
    return;
  }

  const badges = [
    business.verified ? '<span class="detail-badge verified">Verified vendor</span>' : "",
    business.premium ? '<span class="detail-badge premium">Featured listing</span>' : "",
    business.offer ? '<span class="detail-badge offer">Active offer</span>' : ""
  ].join("");

  detailPanel.innerHTML = `
    <div class="detail-card">
      <div class="detail-head">
        <p class="eyebrow">Business Preview</p>
        <h3>${business.name}</h3>
        <div class="detail-badges">${badges}</div>
        <p class="detail-description">${business.summary}</p>
      </div>

      <div class="detail-actions">
        <button class="primary-button" type="button" id="detailEnquiry">Get Quote</button>
        <button class="secondary-button" type="button" id="detailSave">${state.saved.has(business.id) ? "Saved to shortlist" : "Save to shortlist"}</button>
      </div>

      <div class="detail-grid">
        <article>
          <strong>Category</strong>
          <p>${business.category}</p>
        </article>
        <article>
          <strong>Location</strong>
          <p>${business.area}</p>
        </article>
        <article>
          <strong>Hours</strong>
          <p>${business.hours}</p>
        </article>
        <article>
          <strong>Contact</strong>
          <p>${business.phone}</p>
        </article>
      </div>

      <div>
        <p class="eyebrow">Services</p>
        <div class="service-tags">
          ${business.services.map((service) => `<span>${service}</span>`).join("")}
        </div>
      </div>

      <div class="review-strip">
        <strong>${business.rating} rating from ${business.reviews} reviews</strong>
        <p class="review-quote">"${business.reviewQuote}"</p>
      </div>
    </div>
  `;

  document.getElementById("detailEnquiry").addEventListener("click", () => openDrawer(business));
  document.getElementById("detailSave").addEventListener("click", () => {
    toggleSave(business.id);
    renderDetail();
    savedCount.textContent = String(state.saved.size);
  });
}

function toggleSave(id) {
  if (state.saved.has(id)) {
    state.saved.delete(id);
  } else {
    state.saved.add(id);
  }
  savedCount.textContent = String(state.saved.size);
}

function openDrawer(business) {
  state.activeBusinessId = business?.id || null;
  enquiryDrawer.classList.add("open");
  enquiryDrawer.setAttribute("aria-hidden", "false");
  submissionNote.textContent = business
    ? `Enquiry will be sent for ${business.name}.`
    : "Share a requirement and match it with the right businesses.";
  requirementInput.value = business?.leadMessage || "";
}

function closeDrawer() {
  enquiryDrawer.classList.remove("open");
  enquiryDrawer.setAttribute("aria-hidden", "true");
}

async function submitEnquiry(event) {
  event.preventDefault();
  submissionNote.textContent = "Sending enquiry to Python backend...";

  const payload = {
    name: document.getElementById("nameInput").value,
    phone: document.getElementById("phoneInput").value,
    requirement: requirementInput.value,
    businessId: state.activeBusinessId
  };

  const response = await fetch("/api/enquiries", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  const data = await response.json();
  if (!response.ok) {
    submissionNote.textContent = data.error || "Could not submit enquiry.";
    return;
  }

  submissionNote.textContent = `${data.message} Reference #${data.enquiry.id}.`;
  event.target.reset();
  state.activeBusinessId = null;
}

init();
