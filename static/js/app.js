const API = "/api/expenses";
const totalAmountEl = document.getElementById("totalAmount");
const totalCountEl = document.getElementById("totalCount");
const expenseListEl = document.getElementById("expenseList");
const emptyStateEl = document.getElementById("emptyState");
const formEl = document.getElementById("expenseForm");
const errorEl = document.getElementById("formError");

function formatMoney(value) {
    return "₹" + Number(value).toLocaleString("en-IN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    });
}

function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

function renderExpenses(expenses) {
    expenseListEl.innerHTML = "";
    if (!expenses.length) {
        emptyStateEl.classList.remove("hidden");
        return;
    }
    emptyStateEl.classList.add("hidden");
    expenses.forEach((e) => {
        const card = document.createElement("div");
        card.className = "card-enter bg-zinc-900 border border-zinc-800 rounded-xl p-4 flex items-center justify-between gap-4";
        card.innerHTML = `
            <div class="flex-1 min-w-0">
                <p class="font-semibold text-zinc-100 truncate">${escapeHtml(e.title)}</p>
                <p class="text-xs text-zinc-500">${escapeHtml(e.category)} · ${new Date(e.timestamp).toLocaleString()}</p>
            </div>
            <span class="text-emerald-400 font-bold whitespace-nowrap">${formatMoney(e.amount)}</span>
        `;
        expenseListEl.appendChild(card);
    });
}

function updateSummary(expenses) {
    const total = expenses.reduce((sum, e) => sum + Number(e.amount || 0), 0);
    totalAmountEl.textContent = formatMoney(total);
    totalCountEl.textContent = expenses.length;
}

async function loadExpenses() {
    try {
        const res = await fetch(API);
        if (!res.ok) throw new Error("Failed to load");
        const data = await res.json();
        renderExpenses(data);
        updateSummary(data);
    } catch (err) {
        emptyStateEl.textContent = "Could not load expenses.";
        emptyStateEl.classList.remove("hidden");
    }
}

formEl.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorEl.classList.add("hidden");
    const title = document.getElementById("title").value.trim();
    const amount = document.getElementById("amount").value;
    const category = document.getElementById("category").value;

    try {
        const res = await fetch(API, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title, amount: Number(amount), category }),
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.error || "Failed to add expense");
        }
        formEl.reset();
        await loadExpenses();
    } catch (err) {
        errorEl.textContent = err.message;
        errorEl.classList.remove("hidden");
    }
});

loadExpenses();
