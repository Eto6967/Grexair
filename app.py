from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import config
import data_manager
import graf

app = Flask(__name__)

# --- OLDALAK ---

@app.route('/')
def demo():
    df = data_manager.load_and_clean_data(config.FILE_DEMO)
    graph_html = graf.get_graph_html(df, mode='demo')
    kpi = data_manager.calculate_kpi(df)
    return render_template('index.html', graph_html=graph_html, kpi=kpi, page='demo')

@app.route('/monitor')
def monitor():
    return render_template('monitor.html', page='monitor')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    graph_html = None
    error_msg = None
    kpi = None

    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            try:
                temp_path = "temp.csv"
                file.save(temp_path)
                df = data_manager.load_and_clean_data(temp_path)
                graph_html = graf.get_graph_html(df, mode='demo')
                kpi = data_manager.calculate_kpi(df)
                
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except Exception as e:
                error_msg = f"Hiba: {str(e)}"

    return render_template('live.html', graph_html=graph_html, error=error_msg, kpi=kpi, page='upload')

# --- API ---

@app.route('/api/monitor_data')
def api_data():
    # 2000 mérés a megfelelő trendekhez
    df = data_manager.get_latest_sensor_data(limit=2000)
    
    if df.empty: 
        return jsonify({'error': 'no data'}), 404
    
    # graph_html generálása (itt már a javított időket kapja a data_manager-től)
    graph_html = graf.get_graph_html(df, mode='live', is_live=True)
    
    kpi = data_manager.calculate_kpi(df)
    status_text, status_class = data_manager.get_status(kpi['current'])
    
    # --- IDŐZÓNA KORREKCIÓ A KIÍRÁSHOZ: +1 ÓRA ---
    now_corrected = pd.Timestamp.now() + pd.Timedelta(hours=1)
    
    return jsonify({
        'kpi': kpi,
        'status_text': status_text,
        'status_class': status_class,
        'graph_html': graph_html,
        'last_update': now_corrected.strftime("%H:%M:%S")
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)