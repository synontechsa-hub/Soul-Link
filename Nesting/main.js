/**
 * SYNONTECH NESTING ENGINE V2
 * Spreadsheet-Style Input & Multi-View Orchestrator
 */

// ── State ─────────────────────────────────────────────────────────────────────

let stockTableData = Array(10).fill(null).map((_, i) => ({
    id: i,
    l: i === 0 ? 2400 : '',
    w: i === 0 ? 1200 : '',
    active: i === 0
}));

let partsTableData = [
    { id: crypto.randomUUID(), l: 500, w: 300, label: 'BASE_PANEL', comment: 'Front housing' },
    { id: crypto.randomUUID(), l: 500, w: 300, label: 'BASE_PANEL', comment: 'Front housing' },
    { id: crypto.randomUUID(), l: 200, w: 150, label: 'BRACKET_A', comment: 'Support' }
];

let nestedResults = [];
let currentView = 'input'; // 'input' or 'result'

// ── DOM Elements ──────────────────────────────────────────────────────────────

const screenInput = document.getElementById('screen-input');
const screenResult = document.getElementById('screen-result');
const stockTbody = document.getElementById('stock-tbody');
const partsTbody = document.getElementById('parts-tbody');
const svgCanvas = document.getElementById('nest-svg');
const legendKey = document.getElementById('legend-key');

const btnMainAction = document.getElementById('btn-main-action');
const btnBack = document.getElementById('btn-back');
const btnAddRow = document.getElementById('btn-add-row');
const btnPrint = document.getElementById('btn-print');

// ── Initialization ────────────────────────────────────────────────────────────

function init() {
    renderStockGrid();
    renderPartsGrid();
    setupEventListeners();
}

function setupEventListeners() {
    btnMainAction.addEventListener('click', () => {
        if (currentView === 'input') runNesting();
        else switchView('input');
    });

    btnBack.addEventListener('click', () => switchView('input'));
    btnAddRow.addEventListener('click', addPartRow);
    btnPrint.addEventListener('click', () => window.print());
}

// ── View Transitions ─────────────────────────────────────────────────────────

function switchView(view) {
    currentView = view;
    if (view === 'result') {
        screenInput.classList.remove('active');
        screenResult.classList.add('active');
        btnMainAction.innerHTML = '🔱 NEW_MISSION';
    } else {
        screenInput.classList.add('active');
        screenResult.classList.remove('active');
        btnMainAction.innerHTML = '🔱 GENERATE_MISSION';
    }
}

// ── Grid Rendering ────────────────────────────────────────────────────────────

function renderStockGrid() {
    stockTbody.innerHTML = '';
    stockTableData.forEach((row, i) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>#${i + 1}</td>
            <td><input type="number" value="${row.l}" data-idx="${i}" data-field="l" placeholder="-"></td>
            <td><input type="number" value="${row.w}" data-idx="${i}" data-field="w" placeholder="-"></td>
            <td style="text-align: center;">
                <input type="checkbox" ${row.active ? 'checked' : ''} data-idx="${i}" data-field="active" style="width: 20px; height: 20px; margin-top: 8px;">
            </td>
        `;
        tr.querySelectorAll('input').forEach(input => {
            input.onchange = (e) => {
                const idx = e.target.dataset.idx;
                const field = e.target.dataset.field;
                stockTableData[idx][field] = e.target.type === 'checkbox' ? e.target.checked : parseFloat(e.target.value) || '';
            };
        });
        stockTbody.appendChild(tr);
    });
}

function renderPartsGrid() {
    partsTbody.innerHTML = '';
    partsTableData.forEach((row, i) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><input type="number" value="${row.l}" data-idx="${i}" data-field="l"></td>
            <td><input type="number" value="${row.w}" data-idx="${i}" data-field="w"></td>
            <td><input type="text" value="${row.label}" data-idx="${i}" data-field="label" placeholder="Component Name"></td>
            <td><input type="text" value="${row.comment}" data-idx="${i}" data-field="comment" placeholder="..."></td>
            <td style="text-align: center;"><button class="btn btn-ghost delete-part" data-idx="${i}">🗑</button></td>
        `;

        tr.querySelectorAll('input').forEach(input => {
            input.onchange = (e) => {
                const idx = e.target.dataset.idx;
                const field = e.target.dataset.field;
                partsTableData[idx][field] = e.target.type === 'number' ? parseFloat(e.target.value) || 0 : e.target.value;
            };
        });

        tr.querySelector('.delete-part').onclick = () => {
            partsTableData.splice(i, 1);
            renderPartsGrid();
        };

        partsTbody.appendChild(tr);
    });
}

function addPartRow() {
    partsTableData.push({ id: crypto.randomUUID(), l: '', w: '', label: '', comment: '' });
    renderPartsGrid();
}

// ── Nesting Logic ─────────────────────────────────────────────────────────────

function runNesting() {
    const spacing = 5; // Default spacing
    const activeStock = stockTableData.filter(m => m.active && m.l > 0 && m.w > 0);
    const validParts = partsTableData.filter(p => p.l > 0 && p.w > 0);

    if (activeStock.length === 0 || validParts.length === 0) {
        alert("🔱 SYNON_ERROR: Please define valid Stock and Components.");
        return;
    }

    nestedResults = [];
    let currentSheetIdx = 0;
    let currentSheet = activeStock[currentSheetIdx];

    // Preparation: Assign unique colors and ids
    const processParts = validParts.map(p => ({
        ...p,
        color: `hsl(${Math.random() * 360}, 70%, 50%)`
    }));

    // Sort by height descending
    processParts.sort((a, b) => b.w - a.w);

    let x = spacing;
    let y = spacing;
    let shelfHeight = 0;
    let placedCount = 0;

    processParts.forEach(part => {
        let orientations = [
            { l: part.l, w: part.w, rotated: false },
            { l: part.w, w: part.l, rotated: true }
        ];

        let bestFit = null;
        for (let orient of orientations) {
            // Check current shelf
            if (x + orient.l + spacing <= currentSheet.l && y + orient.w + spacing <= currentSheet.w) {
                if (!bestFit || orient.w < bestFit.w) bestFit = orient;
            }
        }

        if (!bestFit) {
            // New shelf
            x = spacing;
            y += shelfHeight + spacing;
            shelfHeight = 0;
            for (let orient of orientations) {
                if (x + orient.l + spacing <= currentSheet.l && y + orient.w + spacing <= currentSheet.w) {
                    if (!bestFit || orient.w < bestFit.w) bestFit = orient;
                }
            }
        }

        if (!bestFit) {
            // New sheet
            currentSheetIdx++;
            if (currentSheetIdx < activeStock.length) {
                currentSheet = activeStock[currentSheetIdx];
                x = spacing;
                y = spacing;
                shelfHeight = 0;
                for (let orient of orientations) {
                    if (x + orient.l + spacing <= currentSheet.l && y + orient.w + spacing <= currentSheet.w) {
                        if (!bestFit || orient.w < bestFit.w) bestFit = orient;
                    }
                }
            }
        }

        if (bestFit) {
            nestedResults.push({
                ...part,
                l: bestFit.l,
                w: bestFit.w,
                rotated: bestFit.rotated,
                sheetIdx: currentSheetIdx,
                x, y
            });
            x += bestFit.l + spacing;
            shelfHeight = Math.max(shelfHeight, bestFit.w);
            placedCount++;
        }
    });

    renderVisualization(activeStock);
    renderLegend();
    updateStats(activeStock, placedCount);
    switchView('result');
}

// ── Result Rendering ──────────────────────────────────────────────────────────

function renderVisualization(activeStock) {
    svgCanvas.innerHTML = '';
    let offsetY = 0;
    const sheetGap = 100;

    activeStock.forEach((sheet, i) => {
        const group = document.createElementNS("http://www.w3.org/2000/svg", "g");

        // Sheet Frame
        const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        rect.setAttribute("x", 0);
        rect.setAttribute("y", offsetY);
        rect.setAttribute("width", sheet.l);
        rect.setAttribute("height", sheet.w);
        rect.setAttribute("fill", "var(--surface-raised)");
        rect.setAttribute("stroke", "var(--text-muted)");
        rect.setAttribute("stroke-dasharray", "8,4");
        group.appendChild(rect);

        // Sheet Label
        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute("x", 10);
        text.setAttribute("y", offsetY - 15);
        text.setAttribute("fill", "var(--brand)");
        text.setAttribute("font-family", "var(--font-mono)");
        text.setAttribute("font-weight", "bold");
        text.textContent = `STOCK_UNIT_${i + 1} [${sheet.l} x ${sheet.w}]`;
        group.appendChild(text);

        // Nested Parts
        const items = nestedResults.filter(p => p.sheetIdx === i);
        items.forEach(p => {
            const pg = document.createElementNS("http://www.w3.org/2000/svg", "g");

            const pRect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
            pRect.setAttribute("x", p.x);
            pRect.setAttribute("y", offsetY + p.y);
            pRect.setAttribute("width", p.l);
            pRect.setAttribute("height", p.w);
            pRect.setAttribute("fill", p.color);
            pRect.setAttribute("fill-opacity", "0.25");
            pRect.setAttribute("stroke", p.color);
            pRect.setAttribute("stroke-width", "2");
            pRect.setAttribute("class", "nest-rect");

            const pLabel = document.createElementNS("http://www.w3.org/2000/svg", "text");
            pLabel.setAttribute("x", p.x + p.l / 2);
            pLabel.setAttribute("y", offsetY + p.y + p.w / 2);
            pLabel.setAttribute("fill", "white");
            pLabel.setAttribute("font-family", "var(--font-mono)");
            pLabel.setAttribute("font-size", Math.max(12, Math.min(p.l, p.w) / 5));
            pLabel.setAttribute("text-anchor", "middle");
            pLabel.setAttribute("dominant-baseline", "middle");
            pLabel.textContent = p.label || 'PART';

            pg.appendChild(pRect);
            pg.appendChild(pLabel);
            group.appendChild(pg);
        });

        svgCanvas.appendChild(group);
        offsetY += sheet.w + sheetGap;
    });

    const maxW = Math.max(...activeStock.map(s => s.l));
    svgCanvas.setAttribute("viewBox", `-50 -50 ${maxW + 100} ${offsetY + 50}`);
}

function renderLegend() {
    legendKey.innerHTML = '';
    const unique = [...new Map(nestedResults.map(p => [p.label + p.l + p.w, p])).values()];
    unique.forEach(p => {
        const item = document.createElement('div');
        item.className = 'legend-item';
        item.innerHTML = `
            <div class="legend-color" style="background: ${p.color}"></div>
            <div>
                <b>${p.label}</b> [${p.rotated ? p.w : p.l}x${p.rotated ? p.l : p.w}] ${p.rotated ? '<i style="color:var(--accent)">[R]</i>' : ''}<br>
                <small style="color:var(--text-muted)">${p.comment}</small>
            </div>
        `;
        legendKey.appendChild(item);
    });
}

function updateStats(activeStock, placedCount) {
    const totalArea = activeStock.reduce((sum, s) => sum + (s.l * s.w), 0);
    const usedArea = nestedResults.reduce((sum, p) => sum + (p.l * p.w), 0);
    const efficiency = totalArea > 0 ? (usedArea / totalArea) * 100 : 0;
    const waste = (totalArea - usedArea) / 1000000;

    document.getElementById('stat-efficiency').innerHTML = `YIELD: <b>${efficiency.toFixed(1)}%</b>`;
    document.getElementById('stat-parts').innerHTML = `COMPONENTS: <b>${placedCount}/${partsTableData.filter(p => p.l > 0).length}</b>`;
    document.getElementById('stat-waste').innerHTML = `WASTE_SCRAP: <b>${waste.toFixed(4)}m²</b>`;
}

init();
