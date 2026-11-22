/* Detection controls for the existing live camera dashboard.
   Intended for local development behind the same-origin trusted dashboard. */
(() => {
  const API = window.DETECTION_API_BASE || "http://127.0.0.1:8000/api/detection";
  const WS = API.replace(/^http/, "ws") + "/ws";
  const classes = ["person", "car", "motorcycle", "bus", "truck", "bicycle"];
  const labels = {person:"Person",car:"Car",motorcycle:"Motorcycle",bus:"Bus",truck:"Truck",bicycle:"Bicycle"};
  const statusByCamera = new Map();

  async function call(path, method, body) {
    const response = await fetch(API + path, {
      method, headers: {"Content-Type":"application/json"},
      body: body ? JSON.stringify(body) : undefined
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || ("HTTP " + response.status));
    return data;
  }

  function attach(card) {
    const id = card.id && card.id.startsWith("cam-") ? card.id.slice(4) : null;
    const actions = card.querySelector(".cam-actions");
    if (!id || !actions || card.querySelector(".detection-panel")) return;

    const panel = document.createElement("section");
    panel.className = "detection-panel";
    panel.style.cssText = "padding:10px 12px;border-top:1px solid #262d3a;color:#c9d1d9;font-size:11px";
    const options = classes.map(name =>
      '<label style="display:inline-flex;gap:4px;align-items:center;margin:4px 8px 4px 0">' +
      '<input type="checkbox" value="' + name + '" checked> ' + labels[name] + '</label>'
    ).join("");
    panel.innerHTML =
      '<div style="font-weight:700;margin-bottom:6px;color:#58a6ff">AI OBJECT DETECTION</div>' +
      '<div class="detection-options">' + options + '</div>' +
      '<div style="display:flex;gap:6px;margin-top:7px">' +
      '<button type="button" class="detection-start" style="background:#12351b;color:#3fb950;flex:1">Start AI</button>' +
      '<button type="button" class="detection-stop" style="background:#2a1f0d;color:#d29922;flex:1">Stop AI</button></div>' +
      '<div class="detection-summary" style="margin-top:7px;color:#7d8899">AI stopped · no detections yet</div>';
    card.appendChild(panel);

    panel.querySelector(".detection-start").addEventListener("click", async event => {
      const button = event.currentTarget; button.disabled = true;
      const selected = Array.from(panel.querySelectorAll("input:checked")).map(x => x.value);
      try {
        await call("/cameras/" + id + "/start", "POST",
          {enabled_classes:selected, fps:5, confidence:0.35});
        panel.querySelector(".detection-summary").textContent = "AI starting…";
      } catch (error) {
        panel.querySelector(".detection-summary").textContent = "Start failed: " + error.message;
      } finally { button.disabled = false; }
    });
    panel.querySelector(".detection-stop").addEventListener("click", async event => {
      const button = event.currentTarget; button.disabled = true;
      try {
        await call("/cameras/" + id + "/stop", "DELETE");
        panel.querySelector(".detection-summary").textContent = "AI stopped";
      } catch (error) {
        panel.querySelector(".detection-summary").textContent = "Stop failed: " + error.message;
      } finally { button.disabled = false; }
    });
  }

  function connect() {
    const socket = new WebSocket(WS);
    socket.onmessage = event => {
      const data = JSON.parse(event.data);
      if (data.type === "camera_status") {
        statusByCamera.set(String(data.camera_id), data.status);
        return;
      }
      if (data.type !== "detections") return;
      const card = document.getElementById("cam-" + data.camera_id);
      const summary = card && card.querySelector(".detection-summary");
      if (!summary) return;
      const counts = {};
      (data.objects || []).forEach(item => counts[item.class] = (counts[item.class] || 0) + 1);
      const text = Object.entries(counts).map(([name,count]) => name + ": " + count).join(" · ");
      summary.textContent = "AI live · " + data.object_count + " objects" + (text ? " · " + text : "");
    };
    socket.onclose = () => setTimeout(connect, 3000);
    socket.onerror = () => socket.close();
  }

  const observer = new MutationObserver(() =>
    document.querySelectorAll(".cam-card").forEach(attach));
  observer.observe(document.body, {childList:true, subtree:true});
  document.querySelectorAll(".cam-card").forEach(attach);
  connect();
})();
