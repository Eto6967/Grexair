document.addEventListener("DOMContentLoaded", function() {
    
    // Frissítési időköz: 5 másodperc
    const UPDATE_INTERVAL = 5000; 

    async function fetchMonitorData() {
        try {
            // 1. Új API végpont meghívása
            const response = await fetch('/api/monitor_data');
            
            if (!response.ok) {
                throw new Error(`HTTP hiba! Státusz: ${response.status}`);
            }

            const data = await response.json();

            // 2. KPI Kártyák frissítése
            // Segédfüggvénnyel, hogy ne legyen hiba, ha még nincs betöltve a HTML
            updateText('kpi-current', data.kpi.current);
            updateText('kpi-min', data.kpi.min);
            updateText('kpi-max', data.kpi.max);
            updateText('last-update', data.last_update);

            // 3. Státusz doboz frissítése (Ikon + Szöveg + Szín)
            const statusBox = document.getElementById('status-box');
            if (statusBox) {
                // Ikon kiválasztása állapot alapján
                let iconClass = 'fa-check-circle';
                if (data.status_class === 'status-warning') iconClass = 'fa-exclamation-triangle';
                if (data.status_class === 'status-danger') iconClass = 'fa-radiation-alt';

                // HTML tartalom csere (ikon + szöveg)
                statusBox.innerHTML = `<i class="fas ${iconClass}"></i> ${data.status_text}`;
                
                // CSS osztály csere (színekhez)
                // 'status-card' az alap, mellé tesszük a színt (pl. 'status-good')
                statusBox.className = `status-card ${data.status_class}`; 
            }

            // 4. Grafikon frissítése (Plotly HTML injektálás)
            const chartContainer = document.getElementById('chart-container');
            if (chartContainer && data.graph_html) {
                // Ez a technika biztosítja, hogy a <script> tagek is lefussanak a beillesztett HTML-ben
                const range = document.createRange();
                range.selectNode(chartContainer);
                const fragment = range.createContextualFragment(data.graph_html);
                
                chartContainer.innerHTML = ''; // Régi törlése
                chartContainer.appendChild(fragment); // Új beillesztése
            }

        } catch (error) {
            console.error("Hiba az adatok lekérésekor:", error);
            
            // Hiba jelzése a felhasználónak a státusz dobozban
            const statusBox = document.getElementById('status-box');
            if (statusBox) {
                statusBox.innerHTML = '<i class="fas fa-wifi"></i> Kapcsolódási hiba...';
                statusBox.className = 'status-card status-danger'; // Piros
            }
        }
    }

    // Segédfüggvény: Csak akkor írja át a szöveget, ha létezik az elem
    function updateText(id, text) {
        const el = document.getElementById(id);
        if (el) {
            el.textContent = text;
        }
    }

    // Első futtatás azonnal
    fetchMonitorData();
    
    // Ismétlés 5 másodpercenként
    setInterval(fetchMonitorData, UPDATE_INTERVAL);
});
