"""
Modern Dark Theme & Cyber Traffic Management Center Styling
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
    --bg-primary: #0A0E17;
    --bg-surface: #111827;
    --bg-card: rgba(17, 24, 39, 0.75);
    --border-color: rgba(255, 255, 255, 0.08);
    --border-glow: rgba(0, 242, 254, 0.25);
    --text-primary: #F3F4F6;
    --text-secondary: #9CA3AF;
    --text-muted: #6B7280;
    --accent-cyan: #00F2FE;
    --accent-blue: #4FACFE;
    --signal-green: #00E676;
    --signal-red: #FF1744;
    --signal-yellow: #FFC400;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: var(--text-primary);
}

/* Overall Streamlit background */
.stApp {
    background-color: var(--bg-primary);
    background-image: 
        radial-gradient(at 0% 0%, rgba(0, 242, 254, 0.05) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(79, 172, 254, 0.04) 0px, transparent 50%);
}

/* Headers */
h1, h2, h3, h4, h5 {
    font-family: 'Inter', sans-serif;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: -0.02em;
}

/* Control center header banner */
.control-banner {
    background: linear-gradient(135deg, rgba(17, 24, 39, 0.9) 0%, rgba(31, 41, 55, 0.9) 100%);
    border: 1px solid var(--border-glow);
    border-radius: 14px;
    padding: 22px 28px;
    margin-bottom: 24px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 0 15px rgba(0, 242, 254, 0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.banner-title {
    font-size: 24px;
    font-weight: 800;
    background: linear-gradient(90deg, #00F2FE 0%, #4FACFE 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}

.banner-badge {
    background: rgba(0, 242, 254, 0.12);
    color: #00F2FE;
    border: 1px solid rgba(0, 242, 254, 0.3);
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Metric Cards */
.metric-card {
    background: var(--bg-card);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.metric-card:hover {
    transform: translateY(-2px);
    border-color: rgba(0, 242, 254, 0.3);
}

.metric-label {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
}

.metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 26px;
    font-weight: 700;
    color: #FFFFFF;
}

.metric-sub {
    font-size: 11px;
    color: var(--text-muted);
    margin-top: 4px;
}

/* Traffic Light Pills */
.signal-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
}

.signal-pill.green {
    background: rgba(0, 230, 118, 0.15);
    color: #00E676;
    border: 1px solid rgba(0, 230, 118, 0.4);
    box-shadow: 0 0 10px rgba(0, 230, 118, 0.2);
}

.signal-pill.red {
    background: rgba(255, 23, 68, 0.15);
    color: #FF1744;
    border: 1px solid rgba(255, 23, 68, 0.4);
}

.signal-pill.yellow {
    background: rgba(255, 196, 0, 0.15);
    color: #FFC400;
    border: 1px solid rgba(255, 196, 0, 0.4);
}

.pulse-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0% { transform: scale(0.95); opacity: 0.8; }
    50% { transform: scale(1.2); opacity: 1; }
    100% { transform: scale(0.95); opacity: 0.8; }
}

/* Glass panel */
.glass-panel {
    background: rgba(17, 24, 39, 0.7);
    backdrop-filter: blur(10px);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
}

/* Code and formulas */
.formula-box {
    background: #0D1117;
    border: 1px solid rgba(0, 242, 254, 0.2);
    border-radius: 8px;
    padding: 14px 18px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    color: #58A6FF;
    margin: 12px 0;
}

/* Custom Table */
.dsa-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
    font-size: 13px;
}

.dsa-table th {
    background: rgba(31, 41, 55, 0.8);
    color: #9CA3AF;
    font-weight: 600;
    text-align: left;
    padding: 10px 14px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.dsa-table td {
    padding: 10px 14px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    color: #E5E7EB;
}

.dsa-table tr:hover td {
    background: rgba(255, 255, 255, 0.03);
}

.badge-emergency {
    background: #FF1744;
    color: white;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 11px;
    font-weight: bold;
    animation: flash 1s infinite alternate;
}

@keyframes flash {
    from { opacity: 0.8; }
    to { opacity: 1; filter: drop-shadow(0 0 6px #FF1744); }
}
</style>
"""

def apply_custom_styles():
    """Returns the CSS block for embedding into Streamlit."""
    return CUSTOM_CSS
