var py = require('@andrewhead/python-program-analysis');
const fs = require('fs');

let rawdata = fs.readFileSync('cell_lines.json');
const cell_lines = JSON.parse(rawdata);


let code = fs.readFileSync('script.py', 'utf8');



const tree = py.parse(code);


const cfg = new py.ControlFlowGraph(tree);
const analyzer = new py.DataflowAnalyzer();
const flows = analyzer.analyze(cfg).dataflows;



function getCell(l) {
    var parent_cell = 'error'
    for (const cell in cell_lines) {
        if (cell_lines[cell][0] <= l && l <= cell_lines[cell][1]) {
            parent_cell = cell;
            break;
        }
    }

    return parent_cell;
}

function sameCell(l1, l2) {
    var cell1 = 'error';
    for (const cell in cell_lines) {
        if (cell_lines[cell][0] <= l1 && l1 <= cell_lines[cell][1]) {
            cell1 = cell;
            break;
        }
    }

    return (cell_lines[cell1][0] <= l2 && l2 <= cell_lines[cell1][1]);

}

var temp = []

for (const flow in flows.items) {
    let flow_item = flows.items[flow]
    let def_line = flow_item.fromNode.location.first_line
    let use_line = flow_item.toNode.location.first_line
    let cell1 = getCell(def_line);
    let cell2 = getCell(use_line);
    if (!sameCell(def_line, use_line) && flow_item.hasOwnProperty('fromRef') && cell1 != 'cell0' && cell2 != 'cell0'){
        let name = flow_item.fromRef.name;
        
        temp.push([cell1,cell2,name].join(','));
    }
}

fs.writeFile('dep.txt', temp.join('\n'), 'utf8',  function (err) {
    if (err) {
        console.error('error');
    }
});



