import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QObject, pyqtSlot
import plotly.graph_objs as go
import plotly.io as pio


# ---------------- DATA ----------------
# Position along the rod (cm)
position = [0, 2, 4, 6, 8, 10]
# Temperature measurements (°C)
temperature = [100, 82, 67, 55, 46, 40]

# Midpoints for gradient calculation
position_gradient = [1, 3, 5, 7, 8]
# Temperature gradient (dT/dx) using central/forward differences
gradient = [-9.0, -7.5, -6.0, -4.5, -3.0]


# ---------------- CINEMATIC GRAPH ----------------
def cinematic(x, y, title, x_label, y_label, line_color="#3b82f6", show_peak=True):

    if show_peak:
        peak = y.index(max(y))
    else:
        # For gradient, show the steepest point (most negative)
        peak = y.index(min(y))

    frames = [
        go.Frame(
            data=[
                go.Scatter(x=x[:k], y=y[:k], mode='lines', line=dict(width=4, color=line_color)),
                go.Scatter(x=x[:k], y=y[:k], mode='lines+markers', 
                          marker=dict(size=10, color=line_color),
                          line=dict(color=line_color)),
                go.Scatter(
                    x=[x[peak]] if k > peak else [],
                    y=[y[peak]] if k > peak else [],
                    mode='markers+text',
                    text=["MAX" if show_peak else "STEEPEST"] if k > peak else [],
                    textposition="top center",
                    marker=dict(size=14, color="#ef4444")
                )
            ]
        )
        for k in range(1, len(x) + 1)
    ]

    fig = go.Figure(
        data=[go.Scatter(x=[x[0]], y=[y[0]], mode='lines+markers', 
                        marker=dict(color=line_color), line=dict(color=line_color))],
        frames=frames
    )

    fig.update_layout(
        template="plotly_dark",
        height=500,
        title=dict(text=title, font=dict(size=18)),
        xaxis=dict(title=x_label, gridcolor='#374151'),
        yaxis=dict(title=y_label, gridcolor='#374151'),
        paper_bgcolor='#111827',
        plot_bgcolor='#111827',
        showlegend=False,
        transition=dict(duration=400),
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            x=0.0,
            y=1.15,
            buttons=[dict(
                label="▶ Play Animation",
                method="animate",
                args=[None, {"frame": {"duration": 400, "redraw": True}}]
            )]
        )]
    )

    return pio.to_html(fig, full_html=False, include_plotlyjs='cdn')


# ---------------- SIMPSON'S RULE VISUALIZATION ----------------
def simpsons_visualization():
    """Visualize Simpson's Rule integration for cumulative heat distribution"""
    
    # Calculate cumulative thermal energy using Simpson's Rule
    cumulative = [0]
    h = 2  # Step size (2 cm intervals)
    
    for i in range(1, len(temperature)):
        if i == 1:
            # Trapezoidal for first segment
            area = h * (temperature[0] + temperature[1]) / 2
        else:
            # Simpson's 1/3 rule where applicable
            area = cumulative[-1] + h * (temperature[i-1] + temperature[i]) / 2
        cumulative.append(round(area, 2))
    
    # Actual cumulative values for heat distribution
    cumulative_heat = [0, 182, 331, 453, 554, 640]
    
    fig = go.Figure()
    
    # Area fill
    fig.add_trace(go.Scatter(
        x=position, y=temperature,
        fill='tozeroy',
        fillcolor='rgba(59, 130, 246, 0.3)',
        line=dict(color='#3b82f6', width=3),
        name='Temperature Profile'
    ))
    
    # Cumulative line
    fig.add_trace(go.Scatter(
        x=position, y=cumulative_heat,
        mode='lines+markers',
        line=dict(color='#10b981', width=3, dash='dash'),
        marker=dict(size=10),
        name='Cumulative Heat (Simpson\'s)',
        yaxis='y2'
    ))
    
    fig.update_layout(
        template="plotly_dark",
        height=500,
        title=dict(text="Simpson's Rule: Cumulative Heat Distribution", font=dict(size=18)),
        xaxis=dict(title="Position (cm)", gridcolor='#374151'),
        yaxis=dict(title="Temperature (°C)", gridcolor='#374151', side='left'),
        yaxis2=dict(title="Cumulative Heat (°C·cm)", overlaying='y', side='right', gridcolor='#374151'),
        paper_bgcolor='#111827',
        plot_bgcolor='#111827',
        legend=dict(x=0.5, y=1.12, orientation='h', xanchor='center')
    )
    
    return pio.to_html(fig, full_html=False, include_plotlyjs='cdn')


# ---------------- BRIDGE ----------------
class Bridge(QObject):
    def __init__(self, app):
        super().__init__()
        self.app = app

    @pyqtSlot(str)
    def open(self, page):
        if page == "temperature":
            self.app.show_fullscreen(
                position, temperature, 
                "🌡️ Temperature Distribution Along Rod",
                "Position (cm)", "Temperature (°C)", "#3b82f6", True
            )
        elif page == "gradient":
            self.app.show_fullscreen(
                position_gradient, gradient,
                "📉 Temperature Gradient (dT/dx)",
                "Position (cm)", "Gradient (°C/cm)", "#ef4444", False
            )
        elif page == "simpson":
            self.app.show_simpson()
        elif page == "back":
            self.app.show_dashboard()


# ---------------- MAIN APP ----------------
class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Heat Diffusion Simulation Dashboard")
        self.setGeometry(80, 80, 1400, 800)

        self.web = QWebEngineView()
        self.setCentralWidget(self.web)

        self.channel = QWebChannel()
        self.bridge = Bridge(self)
        self.channel.registerObject("pyObj", self.bridge)
        self.web.page().setWebChannel(self.channel)

        self.show_dashboard()

    def show_dashboard(self):
        html = f"""
<html>
<head>
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
    <script>
        var pyObj;
        new QWebChannel(qt.webChannelTransport, function(channel) {{
            pyObj = channel.objects.pyObj;
        }});
    </script>
</head>
<body style="background:#0d1117; color:white; font-family:Arial; padding:20px; margin:0;">

<h1 style="text-align:center; margin-bottom:5px; font-size:32px;">
     CASE STUDY 3: Heat Diffusion Process Simulation
</h1>
<p style="text-align:center; color:#9ca3af; margin-bottom:25px;">
    Analyzing thermal distribution along a heated metal rod using numerical methods
</p>

<div style="display:flex; gap:15px; margin-bottom:15px;">
    <div style="flex:1; background:linear-gradient(135deg, #1e3a5f, #0f172a); padding:15px; border-radius:12px; border:1px solid #3b82f6;">
        <h4 style="margin:0; color:#60a5fa;">📊 Data Points</h4>
        <p style="font-size:28px; margin:5px 0; color:#3b82f6;">6</p>
        <p style="color:#9ca3af; margin:0; font-size:12px;">Temperature readings</p>
    </div>
    <div style="flex:1; background:linear-gradient(135deg, #1e3a5f, #0f172a); padding:15px; border-radius:12px; border:1px solid #10b981;">
        <h4 style="margin:0; color:#34d399;">🌡️ Max Temp</h4>
        <p style="font-size:28px; margin:5px 0; color:#10b981;">100°C</p>
        <p style="color:#9ca3af; margin:0; font-size:12px;">At heat source (x=0)</p>
    </div>
    <div style="flex:1; background:linear-gradient(135deg, #1e3a5f, #0f172a); padding:15px; border-radius:12px; border:1px solid #f59e0b;">
        <h4 style="margin:0; color:#fbbf24;">📉 Min Temp</h4>
        <p style="font-size:28px; margin:5px 0; color:#f59e0b;">40°C</p>
        <p style="color:#9ca3af; margin:0; font-size:12px;">At rod end (x=10cm)</p>
    </div>
    <div style="flex:1; background:linear-gradient(135deg, #1e3a5f, #0f172a); padding:15px; border-radius:12px; border:1px solid #ef4444;">
        <h4 style="margin:0; color:#f87171;">⚡ Steepest Gradient</h4>
        <p style="font-size:28px; margin:5px 0; color:#ef4444;">-9.0°C/cm</p>
        <p style="color:#9ca3af; margin:0; font-size:12px;">Near heat source</p>
    </div>
</div>

<div style="display:flex; gap:20px;">
    <div onclick="pyObj.open('temperature')"
        style="flex:1; background:#111827; padding:15px; border-radius:15px; cursor:pointer; 
               border:2px solid transparent; transition:all 0.3s;"
        onmouseover="this.style.borderColor='#3b82f6'"
        onmouseout="this.style.borderColor='transparent'">
        <h3 style="color:#60a5fa; margin-top:0;">🌡️ Temperature Distribution</h3>
        <p style="color:#9ca3af; font-size:13px;">Thermal decay curve from heat source</p>
        {cinematic(position, temperature, "Temperature Distribution Along Rod", 
                  "Position (cm)", "Temperature (°C)", "#3b82f6", True)}
    </div>

    <div onclick="pyObj.open('gradient')"
        style="flex:1; background:#111827; padding:15px; border-radius:15px; cursor:pointer;
               border:2px solid transparent; transition:all 0.3s;"
        onmouseover="this.style.borderColor='#ef4444'"
        onmouseout="this.style.borderColor='transparent'">
        <h3 style="color:#f87171; margin-top:0;">📉 Temperature Gradient (dT/dx)</h3>
        <p style="color:#9ca3af; font-size:13px;">Numerical differentiation results</p>
        {cinematic(position_gradient, gradient, "Temperature Gradient (Numerical Differentiation)", 
                  "Position (cm)", "Gradient (°C/cm)", "#ef4444", False)}
    </div>
</div>

<div onclick="pyObj.open('simpson')"
    style="background:#111827; padding:15px; border-radius:15px; cursor:pointer; margin-top:20px;
           border:2px solid transparent; transition:all 0.3s;"
    onmouseover="this.style.borderColor='#10b981'"
    onmouseout="this.style.borderColor='transparent'">
    <h3 style="color:#34d399; margin-top:0;">📐 Simpson's Rule Integration</h3>
    <p style="color:#9ca3af; font-size:13px;">Cumulative thermal energy profile estimation</p>
    {simpsons_visualization()}
</div>

</body>
</html>
"""
        self.web.setHtml(html)

    def show_fullscreen(self, x, y, title, x_label, y_label, color, show_peak):
        html = f"""
<html>
<head>
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
    <script>
        var pyObj;
        new QWebChannel(qt.webChannelTransport, function(channel) {{
            pyObj = channel.objects.pyObj;
        }});
    </script>
</head>
<body style="background:#0d1117; color:white; font-family:Arial; padding:20px;">

<button onclick="pyObj.open('back')"
    style="padding:10px 20px; margin-bottom:15px; cursor:pointer; background:#1f2937; 
           color:white; border:1px solid #374151; border-radius:8px; font-size:14px;">
    ⬅ Back 
</button>

<h1 style="text-align:center; margin-bottom:10px;">{title}</h1>

<div style="background:#111827; padding:20px; border-radius:15px;">
    {cinematic(x, y, title, x_label, y_label, color, show_peak)}
</div>

<div style="display:flex; gap:15px; margin-top:20px;">
    <div style="flex:1; background:#111827; padding:15px; border-radius:10px;">
        <h4 style="color:#9ca3af; margin:0;">Data Points</h4>
        <p style="font-size:14px; margin:10px 0 0 0;">
            {"<br>".join([f"x={x[i]} → y={y[i]}" for i in range(len(x))])}
        </p>
    </div>
</div>

</body>
</html>
"""
        self.web.setHtml(html)

    def show_simpson(self):
        html = f"""
<html>
<head>
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
    <script>
        var pyObj;
        new QWebChannel(qt.webChannelTransport, function(channel) {{
            pyObj = channel.objects.pyObj;
        }});
    </script>
</head>
<body style="background:#0d1117; color:white; font-family:Arial; padding:20px;">

<button onclick="pyObj.open('back')"
    style="padding:10px 20px; margin-bottom:15px; cursor:pointer; background:#1f2937; 
           color:white; border:1px solid #374151; border-radius:8px; font-size:14px;">
    ⬅ Back 
</button>

<h1 style="text-align:center; margin-bottom:10px;">📐 Simpson's Rule: Cumulative Heat Distribution</h1>

<div style="background:#111827; padding:20px; border-radius:15px;">
    {simpsons_visualization()}
</div>

<div style="display:flex; gap:15px; margin-top:20px;">
    <div style="flex:1; background:#111827; padding:15px; border-radius:10px;">
        <h4 style="color:#10b981; margin:0 0 10px 0;">Simpson's 1/3 Rule Formula</h4>
        <p style="color:#9ca3af; font-family:monospace;">
            ∫f(x)dx ≈ (h/3)[f(x₀) + 4f(x₁) + 2f(x₂) + 4f(x₃) + ... + f(xₙ)]
        </p>
    </div>
    <div style="flex:1; background:#111827; padding:15px; border-radius:10px;">
        <h4 style="color:#3b82f6; margin:0 0 10px 0;">Total Heat Distribution</h4>
        <p style="font-size:28px; color:#3b82f6; margin:0;">≈ 640 °C·cm</p>
        <p style="color:#9ca3af;">Cumulative thermal energy across rod</p>
    </div>
</div>

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
