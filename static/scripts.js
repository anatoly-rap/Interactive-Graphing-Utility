function showForm(type) {
    document.getElementById('plotType').value = type;
    document.getElementById('input-box').style.display = 'block';
    if (type === 'geometric') {
        document.getElementById('geometric-inputs').style.display = 'block';
        document.getElementById('3dplot-inputs').style.display = 'none';
        document.getElementById('var1').disabled = false;
        document.getElementById('var2').disabled = false;
        document.getElementById('equation').disabled = true;
    } else {
        document.getElementById('geometric-inputs').style.display = 'none';
        document.getElementById('3dplot-inputs').style.display = 'block';
        document.getElementById('var1').disabled = true;
        document.getElementById('var2').disabled = true;
        document.getElementById('equation').disabled = false;
    }
}

document.getElementById('plotForm').onsubmit = function(event) {
    event.preventDefault();
    let formData = new FormData(event.target);
    let plotType = formData.get('plotType');
    let url = plotType === 'geometric' ? '/geometric' : '/3dplot';
    fetch(url, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        let graphDiv = document.getElementById('graph');
        if (plotType === 'geometric') {
            let img = document.createElement('img');
            img.src = 'data:image/png;base64,' + data.chart_data;
            img.className = 'responsive-image';
            graphDiv.innerHTML = '';
            graphDiv.appendChild(img);
        } else {
            if (data.error) {
                alert(data.error);
            } else {
                Plotly.newPlot(graphDiv, data.data, data.layout);
            }
        }
    });
};

