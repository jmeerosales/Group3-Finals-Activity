import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QObject, pyqtSlot
import plotly.graph_objs as go
import plotly.io as pio


# ---------------- DATA ----------------
time = [0, 2, 4, 6, 8, 10]
energy = [0, 1.5, 3.5, 6.0, 9.0, 13.0]

time_power = [2, 4, 6, 8]
power = [0.875, 1.125, 1.375, 1.75]


# ---------------- CINEMATIC GRAPH ----------------
def cinematic(x, y, title, x_label, y_label, line_color="#3b82f6"):

    peak = y.index(max(y))

    frames = [
        go.Frame(
            data=[
                go.Scatter(
                    x=x[:k],
                    y=y[:k],
                    mode='lines+markers',
                    line=dict(width=4, color=line_color),
                    marker=dict(size=8, color=line_color)
                ),
                go.Scatter(
                    x=[x[peak]] if k > peak else [],
                    y=[y[peak]] if k > peak else [],
                    mode='markers+text',
                    text=["PEAK"] if k > peak else [],
                    textposition="top center",
                    marker=dict(size=14, color="#ef4444")
                )
            ]
        )
        for k in range(1, len(x) + 1)
    ]

    fig = go.Figure(
        data=[go.Scatter(
            x=[x[0]],
            y=[y[0]],
            mode='lines+markers',
            line=dict(color=line_color)
        )],
        frames=frames
    )

    fig.update_layout(
        template="plotly_dark",
        height=450,
        title=dict(text=title, font=dict(size=18)),
        xaxis=dict(title=x_label, gridcolor='#374151', tickmode='array', tickvals=x),
        yaxis=dict(title=y_label, gridcolor='#374151'),
        paper_bgcolor='#1f2937',
        plot_bgcolor='#1f2937',
        transition=dict(duration=400),
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            x=0.0,
            y=1.15,
            buttons=[dict(
                label="▶ Play Animation",
                method="animate",
                args=[None, {"frame": {"duration": 500, "redraw": True}}]
            )]
        )]
    )

    return pio.to_html(fig, full_html=False, include_plotlyjs='cdn')


# ---------------- BRIDGE ----------------
class Bridge(QObject):
    def __init__(self, app):
        super().__init__()
        self.app = app

    @pyqtSlot(str)
    def open(self, page):
        print(f"Bridge received: {page}")  # Debug log
        if page == "energy":
            self.app.show_fullscreen(time, energy, "⚡ Energy vs Time", "Hours", "kWh", "#00d4ff")
        elif page == "power":
            self.app.show_fullscreen(time_power, power, "⚡ Power vs Time", "Hours", "kW", "#f59e0b")
        elif page == "back":
            self.app.show_dashboard()


# ---------------- MAIN APP ----------------
class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("⚡ Electricity Consumption Analysis")
        self.setGeometry(80, 80, 1400, 850)

        self.web = QWebEngineView()
        self.setCentralWidget(self.web)

        # WebChannel setup - CRITICAL ORDER
        self.channel = QWebChannel()
        self.bridge = Bridge(self)
        self.channel.registerObject("pyObj", self.bridge)
        self.web.page().setWebChannel(self.channel)

        self.show_dashboard()

    # ---------------- DASHBOARD ----------------
    def show_dashboard(self):

        total_energy = energy[-1]
        avg_power = sum(power) / len(power)
        peak_power = max(power)

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
</head>
<body style="
    background: linear-gradient(135deg, #0d1117, #1a1a2e);
    color: white;
    font-family: 'Segoe UI', sans-serif;
    padding: 30px;
    margin: 0;
">

<!-- WebChannel Setup -->
<script>
    let pyObj = null;
    console.log('Setting up WebChannel...');
    
    new QWebChannel(qt.webChannelTransport, function(channel) {{
        console.log('WebChannel connected!');
        pyObj = channel.objects.pyObj;
        console.log('pyObj ready:', pyObj);
    }});
    
    // Test function
    function testConnection() {{
        if (pyObj) {{
            pyObj.open('back');
        }} else {{
            console.log('pyObj not ready yet');
        }}
    }}
</script>

<div style="text-align:center; margin-bottom:30px;">
    <h1 style="color:#00d4ff; text-shadow:0 0 20px #00d4ff;">⚡ Electricity Consumption & Power Analysis</h1>
    <p style="color:#9ca3af;">Numerical Methods Case Study</p>
</div>

<!-- STATS -->
<div style="display:flex; gap:20px; margin-bottom:30px; flex-wrap:wrap;">
    <div style="flex:1; min-width:200px; background:rgba(17,24,39,0.8); padding:20px; border-radius:12px; border:1px solid #374151;">
        <h4 style="color:#00d4ff; margin:0 0 10px 0;">Total Energy</h4>
        <div style="font-size:24px; font-weight:bold;">{total_energy} kWh</div>
    </div>
    <div style="flex:1; min-width:200px; background:rgba(17,24,39,0.8); padding:20px; border-radius:12px; border:1px solid #374151;">
        <h4 style="color:#f59e0b; margin:0 0 10px 0;">Avg Power</h4>
        <div style="font-size:24px; font-weight:bold;">{avg_power:.2f} kW</div>
    </div>
    <div style="flex:1; min-width:200px; background:rgba(17,24,39,0.8); padding:20px; border-radius:12px; border:1px solid #374151;">
        <h4 style="color:#ef4444; margin:0 0 10px 0;">Peak Power</h4>
        <div style="font-size:24px; font-weight:bold;">{peak_power} kW</div>
    </div>
</div>

<!-- GRAPHS -->
<div style="display:flex; gap:20px; flex-wrap:wrap;">

    <div onclick="if(pyObj){{pyObj.open('energy'); console.log('Opening energy');}}" 
         onmouseover="this.style.transform='scale(1.02)'; this.style.transition='0.2s';"
         onmouseout="this.style.transform='scale(1)';"
         style="flex:1; min-width:500px; background:rgba(17,24,39,0.8); padding:25px; border-radius:18px; cursor:pointer; border:2px solid #00d4ff; transition:0.3s;">
        <h3 style="color:#00d4ff; margin-top:0;">📊 Energy Consumption</h3>
        <p style="color:#9ca3af; margin-bottom:20px;">Cumulative energy usage over time</p>
        {cinematic(time, energy, "Energy vs Time", "Hours", "kWh", "#00d4ff")}
    </div>

    <div onclick="if(pyObj){{pyObj.open('power'); console.log('Opening power');}}" 
         onmouseover="this.style.transform='scale(1.02)'; this.style.transition='0.2s';"
         onmouseout="this.style.transform='scale(1)';"
         style="flex:1; min-width:500px; background:rgba(17,24,39,0.8); padding:25px; border-radius:18px; cursor:pointer; border:2px solid #f59e0b; transition:0.3s;">
        <h3 style="color:#f59e0b; margin-top:0;">⚡ Power Usage</h3>
        <p style="color:#9ca3af; margin-bottom:20px;">Instantaneous power from numerical differentiation</p>
        {cinematic(time_power, power, "Power vs Time", "Hours", "kW", "#f59e0b")}
    </div>

</div>

<!-- INSIGHTS -->
<div style="margin-top:30px; background:rgba(17,24,39,0.8); padding:25px; border-radius:12px; border:1px solid #374151;">
    <h3 style="color:#10b981;">📋 Key Findings</h3>
    <ul style="color:#9ca3af;">
        <li>Energy increases steadily → cumulative household consumption</li>
        <li>Power values show rate of consumption (numerical derivative)</li>
        <li>Peak usage occurs near 10 hours of monitoring</li>
    </ul>
</div>

<!-- Test button for debugging -->
<div style="text-align:center; margin-top:20px;">
    <button onclick="testConnection()" style="padding:10px 20px; background:#10b981; color:white; border:none; border-radius:8px; cursor:pointer;">
        🧪 Test Connection
    </button>
</div>

</body>
</html>
"""

        self.web.setHtml(html)


    # ---------------- FULLSCREEN ----------------
    def show_fullscreen(self, x, y, title, x_label, y_label, color):
        peak_val = max(y)
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
</head>
<body style="background:#0d1117; color:white; font-family:'Segoe UI',sans-serif; padding:30px; margin:0;">

<!-- FIXED BACK BUTTON -->
<div style="margin-bottom:30px;">
    <button id="backBtn" onclick="goBack()" 
            style="padding:12px 24px; background:linear-gradient(45deg,#ef4444,#dc2626); 
                   color:white; border:none; border-radius:25px; cursor:pointer; 
                   font-size:16px; font-weight:bold; box-shadow:0 4px 15px rgba(239,68,68,0.4);
                   transition:0.3s;">
        ⬅ Back
    </button>
</div>

<h1 style="color:#00d4ff; text-align:center; text-shadow:0 0 20px #00d4ff; margin-bottom:10px;">{title}</h1>
<div style="text-align:center; color:#9ca3af; margin-bottom:20px;">
    Peak Value: <strong style="color:#ef4444;">{peak_val}</strong>
</div>

{cinematic(x, y, title, x_label, y_label, color)}

<script>
    let pyObj = null;
    console.log('Fullscreen WebChannel setup...');
    
    new QWebChannel(qt.webChannelTransport, function(channel) {{
        console.log('Fullscreen WebChannel connected!');
        pyObj = channel.objects.pyObj;
        console.log('pyObj fullscreen ready:', pyObj);
        document.getElementById('backBtn').disabled = false;
    }});
    
    function goBack() {{
        console.log('Back button clicked!');
        if (pyObj) {{
            pyObj.open('back');
            console.log('Sent back command');
        }} else {{
            console.error('pyObj not available!');
            alert('Connection not ready. Please wait a moment.');
        }}
    }}
</script>

</body>
</html>
"""

        self.web.setHtml(html)


# ---------------- RUN ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Dashboard()
    window.show()
    sys.exit(app.exec())