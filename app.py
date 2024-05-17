import math
from fractions import Fraction
import io
import base64
from flask import Flask, render_template, request, send_file, jsonify
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotLRU import plotLRU

app = Flask(__name__)
# Initialize the LRU caches
chart_lru_cache = plotLRU(capacity=15)
latex_lru_cache = plotLRU(capacity=15)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/geometric', methods=['POST'])
def geometric():
    var1 = float(request.form.get('var1'))
    var2 = float(request.form.get('var2'))
    chart_data = generate_chart(var1, var2)
    return jsonify(chart_data=chart_data)

@app.route('/3dplot', methods=['POST'])
def plot_3d():
    equation = request.form.get('equation')
    fig = generate_3d_plot(equation)
    graphJSON = fig.to_json()
    return graphJSON

@app.route('/convert_to_latex', methods=['GET', 'POST'])
def convert_to_latex():
    var1 = float(request.form.get('var1', 0))
    var2 = float(request.form.get('var2', 0))
    latex_code = generate_latex(var1, var2)
    save_latex_to_file(latex_code)
    return send_file('sequence.tex', as_attachment=True)

def generate_chart(var1, var2):
    cache_key = (var1, var2)
    if chart_lru_cache.contains_chart(cache_key):
        return chart_lru_cache.get(cache_key)
    
    fig, ax, x = gen_plot(var1, var2)
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)
    chart_data = base64.b64encode(buffer.read()).decode('utf-8')
    chart_lru_cache.put(cache_key, chart_data)
    return chart_data

def gen_plot(var1, var2):
    cache_key = (var1, var2)
    if chart_lru_cache.contains_chart(cache_key):
        return chart_lru_cache.get(cache_key)

    fig, ax = plt.subplots()
    x = list(range(1, 30))
    y = [sum(math.pow(var1 * var2, j - 1) for j in range(1, i + 1)) for i in range(1, 30)]
    s = y[-1]
    
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.set_axisbelow(True)
    ax.scatter(x, y, s=10, color="blue", marker='o', label="a_n sequence")
    
    title = '$\sum_{i=1}^\infty' + str(var1) + '\cdot' + str(Fraction(var2).limit_denominator(10)) + '^{i-1}$'
    plt.title(title, fontsize=10)
    
    plot_limit_line(ax, s)
    plot_fill_between(ax, s, x)
    annotate_info(ax, var2, s, max(x), max(y), x)
    
    ax.set_xlabel('Terms')
    ax.set_ylabel('Value')
    ax.legend(loc='best', fontsize=8)
    
    chart_lru_cache.put(cache_key, (fig, ax, x))
    return fig, ax, x

def plot_limit_line(ax, s):
    ax.axhline(y=s, color='green', alpha=0.8, linestyle='-', label="Limit")

def plot_fill_between(ax, s, x):
    ax.fill_between(x, s - s * 0.08, s + s * 0.08, facecolor='plum', alpha=0.3)

def annotate_info(ax, var2, s, max_x, max_y, x):
    if abs(var2) < 1:
        annotation_text = f'Since chosen r, |{var2}| < 1:\nThe sequence converges to {s:.4f} for the first {np.amax(x)} terms'
    else:
        annotation_text = f'Since chosen r, |{var2}| ≥ 1:\nThe sequence diverges for the first {np.amax(x)} terms'
    
    text_position = (0.5, 0.5)
    ax.annotate(
        annotation_text,
        xy=(0.5, 0.5),
        xycoords='axes fraction',
        xytext=text_position,
        fontsize=8,
        arrowprops=dict(facecolor='black', shrink=0.05),
        bbox=dict(boxstyle="round,pad=0.3", edgecolor='black', facecolor='white', alpha=0.8),
        horizontalalignment='center',
        verticalalignment='center'
    )

def generate_3d_plot(equation):
    x = np.linspace(-10, 10, 400)
    y = np.linspace(-10, 10, 400)
    X, Y = np.meshgrid(x, y)
    try:
        Z = eval(equation, {"__builtins__": None}, {"np": np, "x": X, "y": Y})
    except Exception as e:
        return jsonify({"error": str(e)})
    
    fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y)])
    fig.update_layout(title='Interactive 3D Plot', autosize=True,
                      scene=dict(
                          xaxis_title='X Axis',
                          yaxis_title='Y Axis',
                          zaxis_title='Z Axis'))
    return fig

def generate_latex(var1, var2):
    latex_template = r'''
    \documentclass{article}
    \usepackage{graphicx}
    \usepackage{amsmath}
    
    \begin{document}
    
    \begin{figure}
    \centering
    \includegraphics[width=0.8\textwidth]{{chart.png}}
    \caption{Sequence plot}
    \end{figure}
    
    \section*{Sequence Formula}
    
    The sequence formula:
    
    \[
    %s
    \]
    
    \end{document}
    '''
    
    formula = r'\sum_{i=1}^\infty %s \cdot %s^{i-1}' % (var1, Fraction(var2).limit_denominator(10))
    return latex_template % formula

def save_latex_to_file(latex_code):
    with open('sequence.tex', 'w') as f:
        f.write(latex_code)

if __name__ == '__main__':
    app.debug = True
    app.run()

