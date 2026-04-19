import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QObject, pyqtSlot
import plotly.graph_objs as go
import plotly.io as pio


# ---------------- DATA ----------------
# Population vs Time (2020-2024)
years = [2020, 2021, 2022, 2023, 2024]
population = [10000, 10800, 11900, 13200, 14800]

# Growth Rate vs Time (2021-2023) - derived from numerical differentiation
years_growth = [2021, 2022, 2023]
growth_rate = [950, 1200, 1450]  # People/Year


# ---------------- CINEMATIC GRAPH ----------------
def cinematic(x, y, title, x_label, y_label, line_color="#3b82f6"):

    peak = y.index(max(y))

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
                    text=["PEAK"] if k > peak else [],
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
        height=450,
        title=dict(text=title, font=dict(size=18)),
        xaxis=dict(
            title=x_label,
            gridcolor='#374151',
            tickmode='array',
            tickvals=x
        ),
        yaxis=dict(
            title=y_label,
            gridcolor='#374151'
        ),
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
        if page == "population":
            self.app.show_fullscreen(years, population, "📈 Population vs Time", 
                                    "Year", "Population", "#3b82f6")
        elif page == "growth":
            self.app.show_fullscreen(years_growth, growth_rate, "📊 Growth Rate vs Time", 
                                    "Year", "People/Year", "#ef4444")
        elif page == "back":
            self.app.show_dashboard()


# ---------------- MAIN APP ----------------
class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Population Growth Analysis - Numerical Methods Case Study")
        self.setGeometry(80, 80, 1400, 850)

        self.web = QWebEngineView()
        self.setCentralWidget(self.web)

        # WebChannel setup
        self.channel = QWebChannel()
        self.bridge = Bridge(self)
        self.channel.registerObject("pyObj", self.bridge)
        self.web.page().setWebChannel(self.channel)

        self.show_dashboard()

    # ---------------- DASHBOARD ----------------
    def show_dashboard(self):

        html = f"""
<!DOCTYPE html>
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
<body style="
    background: linear-gradient(135deg, #0d1117 0%, #1a1a2e 100%);
    color: white;
    font-family: 'Segoe UI', Arial, sans-serif;
    padding: 30px;
    margin: 0;
">

<div style="text-align:center; margin-bottom:30px;">
    <h1 style="font-size:32px; margin-bottom:10px;">
        📊 Population Growth Analysis Using Numerical Methods
    </h1>
   
</div>

<div style="
    display: flex;
    gap: 25px;
    justify-content: center;
    flex-wrap: wrap;
">

    <div onclick="pyObj.open('population')"
        style="
            flex: 1;
            max-width: 600px;
            min-width: 450px;
            background: linear-gradient(145deg, #111827, #1f2937);
            padding: 20px;
            border-radius: 20px;
            cursor: pointer;
            border: 1px solid #374151;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            transition: transform 0.3s, box-shadow 0.3s;
        "
        onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 15px 50px rgba(59,130,246,0.3)';"
        onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 10px 40px rgba(0,0,0,0.3)';"
    >
        <h3 style="color:#3b82f6; margin-bottom:15px;">📈 Population vs Time</h3>
        <p style="color:#9ca3af; font-size:14px; margin-bottom:15px;">
            Shows upward curve indicating accelerating population growth from 10,000 to 15,000
        </p>
        {cinematic(years, population, "Population vs Time", "Year", "Population", "#3b82f6")}
    </div>

    <div onclick="pyObj.open('growth')"
        style="
            flex: 1;
            max-width: 600px;
            min-width: 450px;
            background: linear-gradient(145deg, #111827, #1f2937);
            padding: 20px;
            border-radius: 20px;
            cursor: pointer;
            border: 1px solid #374151;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            transition: transform 0.3s, box-shadow 0.3s;
        "
        onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 15px 50px rgba(239,68,68,0.3)';"
        onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 10px 40px rgba(0,0,0,0.3)';"
    >
        <h3 style="color:#ef4444; margin-bottom:15px;">📊 Growth Rate vs Time</h3>
        <p style="color:#9ca3af; font-size:14px; margin-bottom:15px;">
            Shows steady increase in growth rate (People/Year) using numerical differentiation
        </p>
        {cinematic(years_growth, growth_rate, "Growth Rate vs Time", "Year", "People/Year", "#ef4444")}
    </div>

</div>

<div style="
    margin-top: 30px;
    background: linear-gradient(145deg, #111827, #1f2937);
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #374151;
">
    <h3 style="color:#10b981; margin-bottom:15px;">📋 Key Findings</h3>
    <ul style="color:#d1d5db; line-height:1.8;">
        <li>The population graph shows an <strong style="color:#3b82f6;">upward curve</strong>, indicating accelerating growth</li>
        <li>The growth rate graph shows a <strong style="color:#ef4444;">steady increase</strong> in yearly population additions</li>
        <li>Population increased by <strong>5,000 people</strong> (50%) over the 4-year period</li>
        <li>Growth rate increased from <strong>1,000</strong> to <strong>1,500 people/year</strong></li>
    </ul>
</div>

</body>
</html>
"""

        self.web.setHtml(html)

    # ---------------- FULLSCREEN ----------------
    def show_fullscreen(self, x, y, title, x_label, y_label, color):

        html = f"""
<!DOCTYPE html>
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
<body style="
    background: linear-gradient(135deg, #0d1117 0%, #1a1a2e 100%);
    color: white;
    font-family: 'Segoe UI', Arial, sans-serif;
    padding: 30px;
    margin: 0;
">

<div style="text-align:center; margin-bottom:20px;">
    <h1 style="font-size:28px;">
        📊 Population Growth Analysis - Detailed View
    </h1>
</div>

<button onclick="pyObj.open('back')"
    style="
        padding: 12px 24px;
        margin-bottom: 20px;
        cursor: pointer;
        background: linear-gradient(145deg, #374151, #4b5563);
        color: white;
        border: none;
        border-radius: 10px;
        font-size: 16px;
        transition: background 0.3s;
    "
    onmouseover="this.style.background='linear-gradient(145deg, #4b5563, #6b7280)';"
    onmouseout="this.style.background='linear-gradient(145deg, #374151, #4b5563)';"
>
    ⬅ Back
</button>

<div style="
    background: linear-gradient(145deg, #111827, #1f2937);
    padding: 25px;
    border-radius: 20px;
    border: 1px solid #374151;
    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
">
    <h2 style="color:{color}; margin-bottom:20px;">{title}</h2>
    {cinematic(x, y, title, x_label, y_label, color)}
</div>

<div style="
    margin-top: 25px;
    background: linear-gradient(145deg, #111827, #1f2937);
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #374151;
">
    <h3 style="color:#10b981;">📈 Analysis</h3>
    <p style="color:#d1d5db; line-height:1.6;">
        This graph displays data points from the population study. Click the 
        <strong>"Play Animation"</strong> button to see the data visualization animate 
        through each time period. The peak value is highlighted when reached.
    </p>
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
