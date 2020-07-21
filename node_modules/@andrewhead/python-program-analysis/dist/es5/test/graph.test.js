"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var graph_1 = require("../graph");
describe("graph", function () {
    it("handles empty", function () {
        var g = new graph_1.Graph(function (s) { return s; });
        expect(g.nodes).toBeDefined();
        expect(g.nodes).toHaveLength(0);
    });
    it("tracks nodes", function () {
        var g = new graph_1.Graph(function (s) { return s; });
        g.addEdge("a", "b");
        g.addEdge("b", "c");
        var ns = g.nodes;
        expect(ns).toBeDefined();
        expect(ns).toHaveLength(3);
        expect(ns).toContain("a");
        expect(ns).toContain("b");
        expect(ns).toContain("c");
    });
    it("sorts forests", function () {
        var g = new graph_1.Graph(function (s) { return s; });
        g.addEdge("a", "b");
        g.addEdge("c", "d");
        var s = g.topoSort();
        expect(s).toBeDefined();
        expect(s).toHaveLength(4);
        expect(s).toContain("a");
        expect(s).toContain("b");
        expect(s).toContain("c");
        expect(s).toContain("d");
        // can't say exact order
        expect(s.indexOf("a")).toBeLessThan(s.indexOf("b"));
        expect(s.indexOf("c")).toBeLessThan(s.indexOf("d"));
    });
    it("sorts dags", function () {
        var g = new graph_1.Graph(function (s) { return s; });
        g.addEdge("a", "b");
        g.addEdge("b", "c");
        g.addEdge("a", "c");
        var s = g.topoSort();
        expect(s).toBeDefined();
        expect(s).toHaveLength(3);
        // must be in this order
        expect(s[0]).toBe("a");
        expect(s[1]).toBe("b");
        expect(s[2]).toBe("c");
    });
});
//# sourceMappingURL=graph.test.js.map