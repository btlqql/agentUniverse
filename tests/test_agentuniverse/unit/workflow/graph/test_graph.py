# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 10:00
# @Author  : btlqql
# @Email   : 2977859784@qq.com
# @FileName: test_graph.py
"""Unit tests for the workflow Graph."""

import networkx as nx
import pytest

from agentuniverse.workflow.graph.graph import Graph
from agentuniverse.workflow.node.enum import NodeEnum
from agentuniverse.workflow.node.node_output import NodeOutput
from agentuniverse.workflow.workflow_output import WorkflowOutput


VALID_CONFIG = {
    'nodes': [
        {'id': 'start', 'type': 'start', 'outputs': [{'name': 'input'}]},
        {'id': 'end', 'type': 'end', 'inputs': {'prompt': {'name': 'p', 'value': 'ok'}},
         'outputs': [{'name': 'result'}]},
    ],
    'edges': [
        {'source_node_id': 'start', 'target_node_id': 'end'},
    ],
}


class TestGraph:
    def test_build_creates_nodes_and_edges(self):
        graph = Graph().build('wf', VALID_CONFIG)
        assert set(graph.nodes) == {'start', 'end'}
        assert len(graph.edges) == 1
        assert graph.nodes['start']['type'] == NodeEnum.START.value

    def test_build_empty_nodes_raises(self):
        with pytest.raises(ValueError, match='nodes configuration is empty'):
            Graph().build('wf', {'nodes': [], 'edges': []})

    def test_build_empty_edges_raises(self):
        with pytest.raises(ValueError, match='edges configuration is empty'):
            Graph().build('wf', {'nodes': VALID_CONFIG['nodes'], 'edges': []})

    def test_build_rejects_unsupported_node_type(self):
        config = {'nodes': [{'id': 'x', 'type': 'unknown'}],
                  'edges': [{'source_node_id': 'x', 'target_node_id': 'x'}]}
        with pytest.raises(ValueError, match='node type is not supported'):
            Graph().build('wf', config)

    def test_build_rejects_cycles(self):
        config = {
            'nodes': [{'id': 'a', 'type': 'start'}, {'id': 'b', 'type': 'end'}],
            'edges': [
                {'source_node_id': 'a', 'target_node_id': 'b'},
                {'source_node_id': 'b', 'target_node_id': 'a'},
            ],
        }
        with pytest.raises(ValueError, match='does not form a DAG'):
            Graph().build('wf', config)

    def test_has_node_been_executed(self):
        output = WorkflowOutput()
        output.workflow_node_results['n1'] = NodeOutput(node_id='n1')
        assert Graph._has_node_been_executed(output, 'n1') is True
        assert Graph._has_node_been_executed(output, 'n2') is False

    def test_graph_is_digraph(self):
        assert isinstance(Graph(), nx.DiGraph)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
