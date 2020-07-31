"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var __1 = require("..");
var log_slicer_1 = require("../log-slicer");
var testcell_1 = require("./testcell");
function makeLog(lines) {
    var cells = lines.map(function (text, i) { return new testcell_1.TestCell(text, i + 1); });
    var logSlicer = new log_slicer_1.ExecutionLogSlicer(new __1.DataflowAnalyzer());
    cells.forEach(function (cell) { return logSlicer.logExecution(cell); });
    return logSlicer;
}
describe("log-slicer", function () {
    it("does the basics", function () {
        var lines = ["x=5", "y=6", "print(x+y)"];
        var logSlicer = makeLog(lines);
        var lastCell = logSlicer.cellExecutions[logSlicer.cellExecutions.length - 1].cell;
        var slices = logSlicer.sliceAllExecutions(lastCell.persistentId);
        expect(slices).toBeDefined();
        expect(slices).toHaveLength(1);
        var slice = slices[0];
        expect(slice).toBeDefined();
        expect(slice.cellSlices).toBeDefined();
        expect(slice.cellSlices).toHaveLength(3);
        slice.cellSlices.forEach(function (cs, i) {
            expect(cs).toBeDefined();
            expect(cs.textSliceLines).toEqual(lines[i]);
            expect(cs.textSlice).toEqual(lines[i]);
        });
    });
    it("does jim's demo", function () {
        var lines = [
            /*[1]*/ "import pandas as pd",
            /*[2]*/ "Cars = {'Brand': ['Honda Civic','Toyota Corolla','Ford Focus','Audi A4'], 'Price': [22000,25000,27000,35000]}\n" +
                "df = pd.DataFrame(Cars,columns= ['Brand', 'Price'])",
            /*[3]*/ "def check(df, size=11):\n" + "    print(df)",
            /*[4]*/ "print(df)",
            /*[5]*/ "x = df['Brand'].values"
        ];
        var logSlicer = makeLog(lines);
        var lastCell = logSlicer.cellExecutions[logSlicer.cellExecutions.length - 1].cell;
        var slice = logSlicer.sliceLatestExecution(lastCell.persistentId);
        expect(slice).toBeDefined();
        expect(slice.cellSlices).toBeDefined();
        [1, 2, 5].forEach(function (c, i) {
            return expect(slice.cellSlices[i].textSlice).toEqual(lines[c - 1]);
        });
        var cellCounts = slice.cellSlices.map(function (cell) { return cell.cell.executionCount; });
        [3, 4].forEach(function (c) { return expect(cellCounts).not.toContainEqual(c); });
    });
    it("works with a selected cell that has been executed twice", function () {
        var logSlicer = new log_slicer_1.ExecutionLogSlicer(new __1.DataflowAnalyzer());
        var lines = [
            ["0", "a = 1"],
            ["1", "b = 2"],
            ["2", "b"],
            ["1", "b = a + 1"],
            ["2", "b"]
        ];
        var cells = lines.map(function (_a, i) {
            var pid = _a[0], text = _a[1];
            return new testcell_1.TestCell(text, i + 1, undefined, pid);
        });
        cells.forEach(function (cell) { return logSlicer.logExecution(cell); });
        var slice = logSlicer.sliceLatestExecution("2");
        expect(slice.cellSlices).toHaveLength(3);
        var sliceText = slice.cellSlices.map(function (c) { return c.textSlice; });
        expect(sliceText).toContain(lines[0][1]);
        expect(sliceText).toContain(lines[3][1]);
        expect(sliceText).toContain(lines[4][1]);
    });
    describe("getDependentCells", function () {
        it("handles simple in-order", function () {
            var lines = ["x = 3", "y = x+1"];
            var logSlicer = makeLog(lines);
            var deps = logSlicer.getDependentCells(logSlicer.cellExecutions[0].cell.executionEventId);
            expect(deps).toBeDefined();
            expect(deps).toHaveLength(1);
            expect(deps[0].text).toBe(lines[1]);
        });
        it("handles variable redefinition", function () {
            var lines = ["x = 3", "y = x+1", "x = 4", "y = x*2"];
            var logSlicer = makeLog(lines);
            var deps = logSlicer.getDependentCells(logSlicer.cellExecutions[0].cell.executionEventId);
            expect(deps).toBeDefined();
            expect(deps).toHaveLength(1);
            expect(deps[0].text).toBe(lines[1]);
            var deps2 = logSlicer.getDependentCells(logSlicer.cellExecutions[2].cell.executionEventId);
            expect(deps2).toBeDefined();
            expect(deps2).toHaveLength(1);
            expect(deps2[0].text).toBe(lines[3]);
        });
        it("handles no deps", function () {
            var lines = ["x = 3\nprint(x)", "y = 2\nprint(y)"];
            var logSlicer = makeLog(lines);
            var deps = logSlicer.getDependentCells(logSlicer.cellExecutions[0].cell.executionEventId);
            expect(deps).toBeDefined();
            expect(deps).toHaveLength(0);
        });
        it("works transitively", function () {
            var lines = ["x = 3", "y = x+1", "z = y-1"];
            var logSlicer = makeLog(lines);
            var deps = logSlicer.getDependentCells(logSlicer.cellExecutions[0].cell.executionEventId);
            expect(deps).toBeDefined();
            expect(deps).toHaveLength(2);
            var deplines = deps.map(function (d) { return d.text; });
            expect(deplines).toContain(lines[1]);
            expect(deplines).toContain(lines[2]);
        });
        it("includes all defs within cells", function () {
            var lines = ["x = 3\nq = 2", "y = x+1", "z = q-1"];
            var logSlicer = makeLog(lines);
            var deps = logSlicer.getDependentCells(logSlicer.cellExecutions[0].cell.executionEventId);
            expect(deps).toBeDefined();
            expect(deps).toHaveLength(2);
            var deplines = deps.map(function (d) { return d.text; });
            expect(deplines).toContain(lines[1]);
            expect(deplines).toContain(lines[2]);
        });
        it("handles cell re-execution", function () {
            var lines = [
                ["0", "x = 2\nprint(x)"],
                ["1", "y = x+1\nprint(y)"],
                ["2", "q = 2"],
                ["0", "x = 20\nprint(x)"]
            ];
            var cells = lines.map(function (_a, i) {
                var pid = _a[0], text = _a[1];
                return new testcell_1.TestCell(text, i + 1, undefined, pid);
            });
            var logSlicer = new log_slicer_1.ExecutionLogSlicer(new __1.DataflowAnalyzer());
            cells.forEach(function (cell) { return logSlicer.logExecution(cell); });
            var rerunFirst = logSlicer.cellExecutions[3].cell.executionEventId;
            var deps = logSlicer.getDependentCells(rerunFirst);
            expect(deps).toBeDefined();
            expect(deps).toHaveLength(1);
            expect(deps[0].text).toContain(lines[1][1]);
        });
        it("handles cell re-execution no-op", function () {
            var lines = [
                ["0", "x = 2\nprint(x)"],
                ["1", "y = 3\nprint(y)"],
                ["2", "q = 2"],
                ["0", "x = 20\nprint(x)"]
            ];
            var cells = lines.map(function (_a, i) {
                var pid = _a[0], text = _a[1];
                return new testcell_1.TestCell(text, i + 1, undefined, pid);
            });
            var logSlicer = new log_slicer_1.ExecutionLogSlicer(new __1.DataflowAnalyzer());
            cells.forEach(function (cell) { return logSlicer.logExecution(cell); });
            var deps = logSlicer.getDependentCells(logSlicer.cellExecutions[3].cell.executionEventId);
            expect(deps).toBeDefined();
            expect(deps).toHaveLength(0);
        });
        it("return result in topo order", function () {
            var lines = [
                ["0", "x = 1"],
                ["0", "y = 2*x"],
                ["0", "z = x*y"],
                ["0", "x = 2"],
                ["1", "y = x*2"],
                ["2", "z = y*x"],
                ["0", "x = 3"]
            ];
            var cells = lines.map(function (_a, i) {
                var pid = _a[0], text = _a[1];
                return new testcell_1.TestCell(text, i + 1, undefined, pid);
            });
            var logSlicer = new log_slicer_1.ExecutionLogSlicer(new __1.DataflowAnalyzer());
            cells.forEach(function (cell) { return logSlicer.logExecution(cell); });
            var lastEvent = logSlicer.cellExecutions[logSlicer.cellExecutions.length - 1].cell
                .executionEventId;
            var deps = logSlicer.getDependentCells(lastEvent);
            expect(deps).toBeDefined();
            expect(deps).toHaveLength(2);
            expect(deps[0].text).toBe("y = x*2");
            expect(deps[1].text).toBe("z = y*x");
        });
        it("can be called multiple times", function () {
            var lines = [["0", "x = 1"], ["1", "y = 2*x"], ["2", "z = x*y"]];
            var cells = lines.map(function (_a, i) {
                var pid = _a[0], text = _a[1];
                return new testcell_1.TestCell(text, i + 1, undefined, pid);
            });
            var logSlicer = new log_slicer_1.ExecutionLogSlicer(new __1.DataflowAnalyzer());
            cells.forEach(function (cell) { return logSlicer.logExecution(cell); });
            var deps = logSlicer.getDependentCells(logSlicer.cellExecutions[0].cell.executionEventId);
            expect(deps).toBeDefined();
            expect(deps).toHaveLength(2);
            expect(deps[0].text).toBe("y = 2*x");
            expect(deps[1].text).toBe("z = x*y");
            var edits = [
                ["0", "x = 2"],
                ["1", "y = x*2"],
                ["2", "z = y*x"],
                ["0", "x = 3"]
            ];
            var cellEdits = edits.map(function (_a, i) {
                var pid = _a[0], text = _a[1];
                return new testcell_1.TestCell(text, i + 1, undefined, pid);
            });
            cellEdits.forEach(function (cell) { return logSlicer.logExecution(cell); });
            var lastEvent = logSlicer.cellExecutions[logSlicer.cellExecutions.length - 1].cell
                .executionEventId;
            var deps2 = logSlicer.getDependentCells(lastEvent);
            expect(deps2).toBeDefined();
            expect(deps2).toHaveLength(2);
            expect(deps2[0].text).toBe("y = x*2");
            expect(deps2[1].text).toBe("z = y*x");
        });
        it("handles api calls", function () {
            var lines = [
                [
                    "0",
                    "from matplotlib.pyplot import scatter\nfrom sklearn.cluster import KMeans\nfrom sklearn import datasets"
                ],
                [
                    "1",
                    "data = datasets.load_iris().data[:,2:4]\npetal_length, petal_width = data[:,1], data[:,0]"
                ],
                ["2", "k=3"],
                ["3", "clusters = KMeans(n_clusters=k).fit(data).labels_"],
                ["4", "scatter(petal_length, petal_width, c=clusters)"],
                ["2", "k=4"]
            ];
            var cells = lines.map(function (_a, i) {
                var pid = _a[0], text = _a[1];
                return new testcell_1.TestCell(text, i + 1, undefined, pid);
            });
            var logSlicer = new log_slicer_1.ExecutionLogSlicer(new __1.DataflowAnalyzer());
            cells.forEach(function (cell) { return logSlicer.logExecution(cell); });
            var lastEvent = logSlicer.cellExecutions[logSlicer.cellExecutions.length - 1].cell
                .executionEventId;
            var deps = logSlicer.getDependentCells(lastEvent);
            expect(deps).toBeDefined();
            expect(deps).toHaveLength(2);
            var sliceText = deps.map(function (c) { return c.text; });
            expect(sliceText).toContain(lines[3][1]);
            expect(sliceText).toContain(lines[4][1]);
        });
    });
});
//# sourceMappingURL=log-slicer.test.js.map