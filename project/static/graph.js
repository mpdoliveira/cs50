document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("family-graph");
  if (!container) return;

  fetch("/graph-data")
    .then(res => res.json())
    .then(graph => {

      /* =========================
         DEGREE (BRANCH STRENGTH)
         ========================= */
      const degree = {};
      graph.nodes.forEach(n => (degree[n.id] = 0));
      graph.edges.forEach(e => {
        degree[e.from] = (degree[e.from] || 0) + 1;
        degree[e.to]   = (degree[e.to]   || 0) + 1;
      });

      const maxDegree =
        Math.max(...Object.values(degree), 1); // evita divisão por zero

      // normaliza degree pra [0,1]
      function degreeNormalized(nodeId) {
        return Math.min((degree[nodeId] || 0) / maxDegree, 1);
      }

      function edgeWidth(nodeId) {
        const d = degree[nodeId] || 1;
        return Math.min(2 + d * 0.8, 10);
      }

      /* =========================
         SVGs (sem mudanças funcionais)
         ========================= */
      function leafSVG(name) {
        const MAX_CHARS = 14;
        const words = name.split(" ");
        const lines = [];
        let current = "";

        for (const w of words) {
          if ((current + " " + w).trim().length <= MAX_CHARS) {
            current = (current + " " + w).trim();
          } else {
            lines.push(current);
            current = w;
          }
        }
        if (current) lines.push(current);

        const lineHeight = 18;
        const centerY = 72;
        const startY = centerY - ((lines.length - 1) * lineHeight) / 2;

        const tspans = lines
          .map(
            (line, i) =>
              `<tspan x="110" y="${startY + i * lineHeight}">${line}</tspan>`
          )
          .join("");

        return `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 140">
  <path
    d="M20,70
       C50,15 170,15 200,70
       C170,125 50,125 20,70
       Z"
    fill="#1E2F26"
    stroke="#7F906A"
    stroke-width="6"
  />
  <text
    text-anchor="middle"
    dominant-baseline="middle"
    fill="#F6F0D7"
    font-size="16"
    font-family="sans-serif"
  >
    ${tspans}
  </text>
</svg>`;
      }

      function logSVG(name) {
        const MAX_CHARS = 16;
        const words = name.split(" ");
        const lines = [];
        let current = "";

        for (const w of words) {
          if ((current + " " + w).trim().length <= MAX_CHARS) {
            current = (current + " " + w).trim();
          } else {
            lines.push(current);
            current = w;
          }
        }
        if (current) lines.push(current);

        const lineHeight = 18;
        const centerY = 60;
        const startY = centerY - ((lines.length - 1) * lineHeight) / 2;

        const tspans = lines
          .map(
            (line, i) =>
              `<tspan x="120" y="${startY + i * lineHeight}">${line}</tspan>`
          )
          .join("");

        return `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 120">
  <rect
    x="20"
    y="20"
    width="200"
    height="80"
    rx="40"
    ry="40"
    fill="#5A3A1E"
    stroke="#3E2614"
    stroke-width="6"
  />
  <ellipse cx="40" cy="60" rx="14" ry="22" fill="none" stroke="#7A5230" stroke-width="3"/>
  <ellipse cx="40" cy="60" rx="7" ry="11" fill="none" stroke="#9C6A3A" stroke-width="2"/>
  <text
    text-anchor="middle"
    dominant-baseline="middle"
    fill="#F6F0D7"
    font-size="16"
    font-family="sans-serif"
  >
    ${tspans}
  </text>
</svg>`;
      }

      /* =========================
         NODES (mass agora escala com degree)
         ========================= */
      const nodes = new vis.DataSet(
        graph.nodes.map(n => {
          const isRoot = n.id === 1;
          const deg = degree[n.id] || 0;
          // massa base 1, +0.25 por ligação, capped
          const mass = isRoot ? 4 : Math.min(1 + deg * 0.25, 6);

          return {
            id: n.id,
            group: isRoot ? "root" : "person",
            shape: "image",
            image:
              "data:image/svg+xml;charset=utf-8," +
              encodeURIComponent(isRoot ? logSVG(n.label) : leafSVG(n.label)),
            size: isRoot ? 70 : 48,
            mass: mass
          };
        })
      );

      /* =========================
         EDGES (agora com fator de cluster)
         ========================= */

      // constantes base por tipo (valores seguros)
      const BASE = {
        parent: { springConstant: 0.0012, springLength: 100 },
        sibling: { springConstant: 0.0020, springLength: 260 },
        spouse: { springConstant: 0.0060, springLength: 160 },
        friend: { springConstant: 0.0040, springLength: 180 },
        default: { springConstant: 0.0025, springLength: 200 }
      };

      function scaledForAffinity(baseValue, affinity, options = {}) {
        // affinity ∈ [0,1]
        // options: { min, max, invert }
        const min = options.min ?? baseValue * 0.5;
        const max = options.max ?? baseValue * 2.2;
        const v = baseValue * (1 + affinity * 1.0); // base scaling
        // clamp
        return Math.max(min, Math.min(max, v));
      }

      const edges = new vis.DataSet(
        graph.edges.map(e => {
          const type = e.type;
          // afinidade média entre os dois nós (0..1)
          const affinity =
            ((degree[e.from] || 0) + (degree[e.to] || 0)) / (2 * maxDegree);

          // largura visual baseada em grau
          const width = Math.max(edgeWidth(e.from), edgeWidth(e.to));

          if (type === "parent") {
            const base = BASE.parent;
            return {
              from: e.from,
              to: e.to,
              arrows: "to",
              width: width * 0.85,
              color: { color: "#4A2E1F" },
              physics: true,
              springConstant: scaledForAffinity(base.springConstant, affinity, { min: 0.0008, max: 0.006 }),
              springLength: Math.max(2, base.springLength - Math.round(affinity * 1000))
            };
          }

          if (type === "sibling") {
            const base = BASE.sibling;
            return {
              from: e.from,
              to: e.to,
              width: Math.max(1, width * 0.22),
              color: { color: "rgba(156,122,91,0.55)" },
              physics: true,
              springConstant: scaledForAffinity(base.springConstant, affinity * 0.6, { min: 0.0005, max: 0.008 }),
              springLength: Math.max(140, base.springLength - Math.round(affinity * 120)),
              smooth: { type: "continuous" }
            };
          }

          if (type === "spouse") {
            const base = BASE.spouse;
            return {
              from: e.from,
              to: e.to,
              width: 5,
              label: "✿",
              color: { color: "#F2A1C2" },
              font: {
                size: 18,
                color: "#F2A1C2",
                strokeWidth: 2,
                strokeColor: "#5A2A3A"
              },
              smooth: { type: "curvedCW", roundness: 0.3 },
              physics: true,
              springConstant: scaledForAffinity(base.springConstant, affinity, { min: 0.002, max: 0.01 }),
              springLength: Math.max(100, base.springLength - Math.round(affinity * 80))
            };
          }

          if (type === "ex-spouse") {
            return {
              from: e.from,
              to: e.to,
              width: 2,
              label: "✖",
              color: { color: "rgba(242,161,194,0.8)" },
              dashes: [6, 6],
              physics: true,
              springLength: 100
            };
          }

          if (type === "friend") {
            const base = BASE.friend;
            return {
              from: e.from,
              to: e.to,
              width: Math.max(1, width * 0.35),
              label: "☘",
              color: { color: "#6FAF8A" },
              physics: true,
              springConstant: scaledForAffinity(base.springConstant, affinity * 0.7, { min: 0.001, max: 0.008 }),
              springLength: Math.max(120, base.springLength - Math.round(affinity * 60))
            };
          }

          if (type === "pet") {
            return {
              from: e.from,
              to: e.to,
              width: 1.1,
              color: { color: "#bf6000" },
              physics: true,
              springLength: 80
            };
          }

          const base = BASE.default;
          return {
            from: e.from,
            to: e.to,
            width: 1,
            color: "#E0A800",
            physics: true,
            springConstant: scaledForAffinity(base.springConstant, affinity, { min: 0.0008, max: 0.006 }),
            springLength: Math.max(100, base.springLength - Math.round(affinity * 80))
          };
        })
      );

      const options = {
        physics: {
          enabled: true,
          solver: "forceAtlas2Based",
          forceAtlas2Based: {
            gravitationalConstant: -100,
            centralGravity: 0.018,
            springLength: 80,
            springConstant: 0.015,
            damping: 0.72
          },
          stabilization: { iterations: 400 }
        },
        interaction: {
          hover: true,
          zoomView: true,
          dragNodes: true
        },
        edges: {
          smooth: { type: "dynamic" },
          font: {
            color: "#D8D1B6",
            size: 12,
            strokeWidth: 3,
            strokeColor: "#16251D"
          }
        }
      };

      const network = new vis.Network(container, { nodes, edges }, options);

      network.on("click", params => {
        if (!params.nodes.length) return;
        const id = params.nodes[0];
        window.location.href = `/person/${id}`;
      });

      network.once("stabilizationIterationsDone", () => {
        network.fit({ animation: { duration: 400 } });
        createGraphLegend();
      });

      window.familyNetwork = network;

      function createGraphLegend() {
        if (document.getElementById("graph-legend")) return;

        const legend = document.createElement("div");
        legend.id = "graph-legend";

        legend.innerHTML = `
          <div class="legend-title">Legend</div>

          <div class="legend-item"><span class="node log"></span> Root person</div>
          <div class="legend-item"><span class="node leaf"></span> Person</div>

          <hr>

          <div class="legend-item"><span class="line parent"></span> Parent → Child</div>
          <div class="legend-item"><span class="line sibling"></span> Sibling</div>
          <div class="legend-item"><span class="symbol spouse">✿</span> Spouse</div>
          <div class="legend-item"><span class="line ex-spouse"></span> Ex-spouse</div>
          <div class="legend-item"><span class="symbol friend">☘</span> Friend</div>
          <div class="legend-item"><span class="line pet"></span> Pet</div>
        `;

        document.querySelector(".app-canvas").appendChild(legend);

        const style = document.createElement("style");
        style.innerHTML = `
          #graph-legend {
            position: absolute;
            bottom: 16px;
            left: 16px;
            background: rgba(22,37,29,0.95);
            color: #F6F0D7;
            padding: 14px 18px;
            border-radius: 14px;
            border: 1px solid #4F5F4A;
            font-size: 13px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.35);
            z-index: 10;
          }

          #graph-legend .legend-title {
            font-weight: 600;
            margin-bottom: 8px;
          }

          #graph-legend .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 4px 0;
          }

          #graph-legend hr {
            border: none;
            border-top: 1px solid #4F5F4A;
            margin: 6px 0;
          }

          .node {
            width: 20px;
            height: 12px;
            border-radius: 8px;
          }

          .node.log { background: #5A3A1E; border: 2px solid #3E2614; }
          .node.leaf { background: #1E2F26; border: 2px solid #7F906A; }

          .line {
            width: 26px;
            height: 0;
            border-top: 4px solid;
          }

          .line.parent { border-color: #4A2E1F; }
          .line.sibling { border-color: rgba(156,122,91,0.6); }
          .line.ex-spouse { border-color: rgba(242,161,194,0.8); border-top-style: dashed; }
          .line.pet { border-color: #bf6000; }

          .symbol.spouse { color: #F2A1C2; font-size: 16px; }
          .symbol.friend { color: #6FAF8A; font-size: 16px; }
        `;
        document.head.appendChild(style);
      }

    })
    .catch(err => console.error("Graph load failed:", err));
});
