// Simple graph visualization using vis-network
// Requires: https://unpkg.com/vis-network/standalone/umd/vis-network.min.js

document.addEventListener('DOMContentLoaded', function() {
    if (!window.graphData) return;
    var container = document.getElementById('graph-network');
    if (!container) return;
    var nodes = new vis.DataSet(window.graphData.nodes);
    var edges = new vis.DataSet(window.graphData.edges);
    var data = { nodes: nodes, edges: edges };
    var options = {
        nodes: { shape: 'dot', size: 18, font: { size: 16 } },
        edges: { color: '#aaa', font: { align: 'top' } }, // removed arrows: 'to'
        physics: { stabilization: true, barnesHut: { springLength: 80 } },
        layout: { improvedLayout: true }
    };
    var network = new vis.Network(container, data, options);
});
