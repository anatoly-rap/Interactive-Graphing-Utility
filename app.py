import math
from fractions import Fraction
import io
import base64
from flask import Flask, render_template, request, send_file
import matplotlib.pyplot as plt
from functools import lru_cache
import numpy as np

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    chart_data = None
    if request.method == 'POST':
        var1 = float(request.form.get('var1'))
        var2 = float(request.form.get('var2'))
        chart_data = generate_chart(var1, var2)
    return render_template('index.html', chart_data=chart_data)

@app.route('/convert_to_latex', methods=['GET','POST'])
def convert_to_latex():
    var1 = float(request.form.get('var1', 0))  
    var2 = float(request.form.get('var2', 0))
    latex_code = generate_latex(var1, var2)
    save_latex_to_file(latex_code)
    return send_file('sequence.tex', as_attachment=True)

@lru_cache(maxsize=10)
def generate_chart(var1, var2):
    fig, ax, x = gen_plot(var1, var2)
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)
    chart_data = base64.b64encode(buffer.read()).decode('utf-8')
    return chart_data

@lru_cache(maxsize=10)
def gen_plot(var1, var2):
    fig, ax = plt.subplots()
    x, y = list(range(1, 30)), [sum(math.pow(var1 * var2, j - 1) for j in range(1, i + 1)) for i in range(1, 30)]
    s = y[-1] 
    ax.axis([0, 30, 0, max(y) + 1])
    ax.scatter(x, y, s=1.8, color="red", label="a_n sequence")
    title = '$\sum_{i=1}^\infty' + str(var1) + '\cdot' + str(Fraction(var2).limit_denominator(10)) +'^{i-1}$'
    plt.title(title, fontsize=7)
    plot_limit_line(ax, s)
    plot_fill_between(ax, s, x)
    annotate_info(ax, var2, s, max(x), max(y), x)
    ax.legend(loc='lower right')
    return fig, ax, x

def plot_limit_line(ax, s):
    ax.axhline(y=s, color='g', alpha=0.8, linestyle='-', label="limit")

def plot_fill_between(ax, s, x):
    ax.fill_between(x, s - s * 0.08, s + s * 0.08, facecolor='plum', alpha=0.3)

def annotate_info(ax, var2, s, max_x, max_y, x):
    if abs(var2) < 1:
        annotation_text = 'Since chosen r, |{}| < 1:\n The sequence converges to {:.4f} for the first {} terms'.format(var2, s, np.amax(x))
        text_position = (max_x - 0.5, max_y + 0.5)
    elif abs(var2) >= 1:
        annotation_text = 'Since chosen r, 1 ≤ |{}|:\n The sequence diverges to {:.4f} for the first {} terms'.format(var2, s, np.amax(x))
        text_position = (max_x - 0.5, max_y + 0.5)

    ax.annotate(
        annotation_text,
        xy=(max_x, max_y),
        xytext=text_position,
        fontsize=7,
        arrowprops={"arrowstyle": "->", "color": "y"},
        bbox={'facecolor': 'white', 'alpha': 0.6, 'pad': 10},
        horizontalalignment='right',
        verticalalignment='top',
        transform=ax.transAxes
    )

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