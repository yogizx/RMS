document.addEventListener("DOMContentLoaded", () => {
  // Auto-refresh recent transactions every 10s
  const liveList = document.getElementById("live-transactions");
  if (liveList) {
    async function refresh() {
      try {
        const r = await fetch("./api/transactions/");
        const data = await r.json();
        liveList.innerHTML = "";
        data.transactions.forEach((t) => {
          const li = document.createElement("li");
          li.className = "tx";
          li.innerHTML = `<span>#${t.id}</span><span>${
            t.customer
          }</span><span>₹ ${t.amount.toFixed(2)}</span><span>${
            t.created_at
          }</span>`;
          liveList.appendChild(li);
        });
      } catch (e) {
        console.error(e);
      }
    }
    refresh();
    setInterval(refresh, 10000);
  }
});