#!/usr/bin/python3
"""
Control flow graph for Python programs.
"""

import collections
from typing import Any, Deque, Tuple, List, Optional, Iterator, Set, Dict
import ast  # type: ignore
from _ast import Compare  # For type-hinting
import astor  # type: ignore
import graphviz as gv  # type: ignore
try:
    # This was working before, but now it's not
    from graphviz.dot import Digraph  # type: ignore
except:
    from graphviz import Digraph
import re
from collections import Counter, deque
import os


class Block(object):
    """
    Basic block in a control flow graph.

    Contains a list of statements executed in a program without any control
    jumps. A block of statements is exited through one of its exits. Exits are
    a list of Links that represent control flow jumps.
    """

    __slots__ = (
        "id",
        "statements",
        "func_calls",
        "predecessors",
        "exits",
        "func_blocks",
        "highlight",
        "outline",
    )

    def __init__(self, id: int) -> None:
        # Id of the block.
        self.id = id
        # Statements in the block.
        self.statements: List[ast.AST] = []
        # Calls to functions inside the block (represents context switches to
        # some functions' CFGs).
        self.func_calls: List[str] = []
        # Links to predecessors in a control flow graph.
        self.predecessors: List[Link] = []
        # Links to the next blocks in a control flow graph.
        self.exits: List[Link] = []
        # Function blocks within this block
        self.func_blocks: List[FuncBlock] = []
        # Interactive styling
        self.highlight: bool = False
        # Debugger at this block
        self.outline: bool = False

    def __iter__(self):
        return iter(self.statements)

    def __str__(self) -> str:
        if self.statements:
            return "block:{}@{}".format(self.id, self.at())
        return "empty block:{}".format(self.id)

    def __repr__(self) -> str:
        txt = "{} with {} exits".format(str(self), len(self.exits))
        if self.statements:
            txt += ", body=["
            txt += ", ".join([ast.dump(node) for node in self.statements])
            txt += "]"
        return txt

    def at(self) -> int:
        """
        Get the line number of the first statement of the block in the program.
        """
        if self.statements and self.statements[0].lineno >= 0:
            return self.statements[0].lineno
        return -1

    def end(self) -> int:
        """
        Get the line number of the last statement of the block in the program.
        """
        if self.statements and self.statements[-1].lineno >= 0:
            return self.statements[-1].lineno
        return -1

    def is_empty(self) -> bool:
        """
        Check if the block is empty.

        Returns:
            A boolean indicating if the block is empty (True) or not (False).
        """
        return not self.statements

    def get_source(self) -> str:
        """
        Get a string containing the Python source code corresponding to the
        statements in the block.

        Returns:
            A string containing the source code of the statements.
        """
        src = ""
        for statement in self.statements:
            if type(statement) in [ast.If, ast.For, ast.While]:
                src += astor.to_source(statement).split("\n")[0] + "\n"
            elif (
                type(statement) == ast.FunctionDef
                or type(statement) == ast.AsyncFunctionDef
            ):
                src += (astor.to_source(statement)).split("\n")[0] + "...\n"
            else:
                src += astor.to_source(statement)
        return src

    def get_calls(self) -> str:
        """
        Get a string containing the calls to other functions inside the block.

        Returns:
            A string containing the names of the functions called inside the
            block.
        """
        txt = ""
        for func_name in list(set(self.func_calls)):
            txt += func_name + "\n"
        return txt

    def type(self, default: Optional[Any] = None) -> Any:
        default = ast.AST if default is None else default
        return type(self.statements[0]) if self.statements else default

    def __hash__(self) -> int:
        # Allows Block objects to be used as dict keys and set elements
        # return id(self)
        return self.id

    def add_statement(self, node: ast.AST):
        self.statements.append(node)

    def add_exit(self, next, exitcase=None) -> None:
        link = Link(self, next, exitcase)
        self.exits.append(link)
        next.predecessors.append(link)


class Link(object):
    """
    Link between blocks in a control flow graph.

    Represents a control flow jump between two blocks. Contains an exitcase in
    the form of an expression, representing the case in which the associated
    control jump is made.
    """

    __slots__ = (
        "source",
        "target",
        "exitcase",
        "highlight",
    )

    def __init__(
        self,
        source: Block,
        target: Block,
        exitcase: Optional[ast.Compare] = None,
    ) -> None:
        assert isinstance(target, Block), "Source of a link must be a block"
        assert isinstance(target, Block), "Target of a link must be a block"
        # Block from which the control flow jump was made.
        self.source = source
        # Target block of the control flow jump.
        self.target = target
        # 'Case' leading to a control flow jump through this link.
        self.exitcase = exitcase
        # Interactive styling
        self.highlight: bool = False

    def __str__(self) -> str:
        return f"link from {self.source} to {self.target}"

    def __repr__(self) -> str:
        # This isn't how repr is supposed to be used... We should be able to
        # deep copy this object by calling eval(repr(link))`.
        if self.exitcase is not None:
            return f"{self}, with exitcase {ast.dump(self.exitcase)}"
        return str(self)

    def jumpfrom(self) -> Optional[int]:
        """Return the line of source end"""
        return self.source.end()

    def jumpto(self) -> Optional[int]:
        """Return the line of target start"""
        return self.target.at()

    def get_exitcase(self) -> str:
        """
        Get a string containing the Python source code corresponding to the
        exitcase of the Link.

        Returns:
            A string containing the source code.
        """
        if self.exitcase:
            return astor.to_source(self.exitcase)
        return ""


class FuncBlock(Block):
    __slots__ = ("args", "name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.args: List[FuncBlock] = []
        self.name: Optional[str] = None


class TryBlock(Block):
    __slots__ = ("except_blocks",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.except_blocks: Dict[Optional[Exception], Block] = {}

    def get_source(self) -> str:
        """
        Get a string containing the Python source code corresponding to the
        statements in the block.

        Returns:
            A string containing the source code of the statements.
        """
        if not self.statements[1:]:
            return "try:"
        src = ""
        for statement in self.statements[1:]:  # We just want try body
            if type(statement) in [ast.If, ast.For, ast.While]:
                src += astor.to_source(statement).split("\n")[0] + "\n"
            elif (
                type(statement) == ast.FunctionDef
                or type(statement) == ast.AsyncFunctionDef
            ):
                src += (astor.to_source(statement)).split("\n")[0] + "...\n"
            else:
                src += astor.to_source(statement)
        return src


class CFG(object):
    """
    Control flow graph (CFG).

    A control flow graph is composed of basic blocks and links between them
    representing control flow jumps. It has a unique entry block and several
    possible 'final' blocks (blocks with no exits representing the end of the
    CFG).
    """

    # Also serves as graph Key table
    # TODO Change value type to dict. Can be upacked into graph.node fn.
    node_styles = {
        "input": ("parallelogram", "#afeeee"),  # Pale Turquoise
        "default": ("rectangle", "#FFFB81"),  # Pale Yellow
        ast.If: ("diamond", "#FF6752"),  # Pale Red
        ast.For: ("hexagon", "#FFBE52"),  # Pale Orange
        ast.While: ("hexagon", "#FFBE52"),  # Pale Orange
        ast.Call: ("tab", "#E552FF"),  # Pale Purple
        ast.Return: ("parallelogram", "#98fb98"),  # Pale Green
        ast.Try: ("Mdiamond", "orange"),
        ast.Raise: ("house", "#98fb98"),
    }
    DEFAULT = node_styles["default"]

    def __init__(
        self, name: str, allfunctioncfgs, asynchr: bool = False, short: bool = True
    ) -> None:
        assert isinstance(name, str), "Name of a CFG must be a string"
        assert isinstance(asynchr, bool), "Async must be a boolean value"
        # Name of the function or module being represented.
        self.name = name
        # Type of function represented by the CFG (sync or async). A Python
        # program is considered as a synchronous function (main).
        self.asynchr = asynchr
        # Entry block of the CFG.
        self.entryblock: Optional[Block] = None
        # Final blocks of the CFG.
        self.finalblocks: List[Block] = []
        # Sub-CFGs for functions defined inside the current CFG.
        self.functioncfgs: dict = {}
        self.allfunctioncfgs = allfunctioncfgs
        # Sub-CFGs
        self.classcfgs: dict = {}
        self.isShort = short
        self.lineno: int = 0
        self.end_lineno: int = 0
        self.qualname = ""

    def __str__(self) -> str:
        return "CFG for {}".format(self.name)

    # def _build_key_subgraph(self, format: str) -> Digraph:
    #     # Generates a key for th?!?jedi=0, e CFG?!? (name=None, comment=None, filename=None, directory=None, format=None, engine=None, encoding=backend.ENCODING, graph_attr=None, node_attr=None, *_*edge_attr=None*_*, body=None, strict=False) ?!?jedi?!?
    #     key_subgraph = gv.Digraph(
    #         name="cluster_KEY",
    #         format=format,
    #         graph_attr={"label": "KEY", "fontname": "DejaVu Sans Mono"},
    #         node_attr={"fontname": "DejaVu Sans Mono"},
    #         edge_attr={"fontname": "DejaVu Sans Mono"},
    #     )
    #     for typeobj, (shape, color) in zip(
    #         self.node_styles.keys(), self.node_styles.values()
    #     ):
    #         key_subgraph.node(
    #             name=(
    #                 typeobj.__name__.lower()
    #                 if isinstance(typeobj, type)
    #                 else str(typeobj)
    #             ),
    #             _attributes={
    #                 "shape": shape,
    #                 "style": "filled",
    #                 "fillcolor": color,
    #             },
    #         )

        # # Adding edge helps with alignment.
        # key_subgraph.edge("if", "input", _attributes={"style": "invis"})
        # key_subgraph.edge("input", "call", _attributes={"style": "invis"})
        # key_subgraph.edge("for", "return", _attributes={"style": "invis"})
        # key_subgraph.edge("return", "default", _attributes={"style": "invis"})
        # key_subgraph.edge("try", "raise", _attributes={"style": "invis"})
        # return key_subgraph

    # default handler for graph nodes
    def _style_handler(
        self, block: Block, typeobject: Any
    ) -> Tuple[str, str, str]:

        shape, color = self.node_styles.get(typeobject, self.DEFAULT)
        # Left-align all remaining blocks
        text = "\l".join(line for line in block.get_source().splitlines())
        return shape, color, text

    # default handler for graph edges
    def _edge_handler(self, link: Link) -> Tuple[None, str, str]:
        return None, "black", link.get_exitcase().strip()

    def stylize_node(self, block: Block, default: None = None) -> tuple:
        # Since we're modelling ast objects, we might as well copy how they
        # implement handlers. This should allow us to implement new node types
        # simply defining a method `node_ASTNAME`
        typeobject = block.type(default)
        name = (
            typeobject.__name__ if isinstance(typeobject, type) else typeobject
        )
        style = getattr(self, f"node_{name}", self._style_handler)(
            block, typeobject
        )
        assert (
            len(style) == 3
        ), "Style handler must return (shape, color, label)"
        assert all(
            isinstance(attr, str) or attr or attr is None for attr in style
        ), "Style attributes must be str or NoneType"
        return style

    def stylize_edge(
        self, link: Link, default: None = None, default_target: None = None
    ) -> tuple:
        typeobject = link.source.type(default)
        name = (
            typeobject.__name__ if isinstance(typeobject, type) else typeobject
        )
        target_type = link.target.type(default_target)
        target_name = (
            target_type.__name__ if isinstance(typeobject, type) else typeobject
        )
        # Do specific attribute search of source->dest
        style_fn = getattr(self, f"{name}_to_{target_name}", None)

        # Do generic attribute search of source->any
        if style_fn is None:
            style_fn = getattr(self, f"edge_{name}", self._edge_handler)
        style = style_fn(link)
        assert (
            len(style) == 3
        ), "style handler must return (shape, color, label)"
        assert all(
            isinstance(attr, str) or attr is None for attr in style
        ), "style attributes must be str or NoneType"
        return style

    def _visit_func(
        self,
        graph: Digraph,
        block: FuncBlock,
        last: str = None,
        visited: Set[Block] = set(),
        interactive: bool = False,
    ) -> None:
        if block in visited:
            return
        visited.add(block)
        shape, color, _ = self.stylize_node(block)
        graph.node(
            str(block.id),
            label=block.name,
            linenum = str([block.at()]),
            _attributes={"shape": shape, "color": color, "style": "filled"},
        )
        if last is not None:
            graph.edge(last, str(block.id), _attributes={"color": "black"})
        for arg in block.args:
            self._visit_func(graph, arg, str(block.id), interactive=interactive)

    def _visit_blocks(
        self,
        graph: Digraph,
        block: Block,
        visited: Set[Block] = set(),
        calls: bool = True,
        format: str = None,
        interactive: bool = False,
    ) -> None:
        # Don't visit blocks twice.
        if block in visited:
            return
        visited.add(block)
        nodeshape, nodecolor, nodelabel = self.stylize_node(block)
        node_type = block.type()
        original_nodelabel = nodelabel
        nodelabel = ""
        if (
            self.isShort
            and not isinstance(node_type, ast.ClassDef)
            and not isinstance(node_type, ast.FunctionDef)
            and not isinstance(node_type, ast.If)
            and not isinstance(node_type, ast.While)
        ):
            sub_pattern = r"""(\"|')                # Group 1: " or '
                              (?=[^\"'\r\n]{20,})   # Enforce min length of 20
                              ([^\"'\r\n]{,20})     # Group 2: Words that stay
                              ([^\"'\r\n]{,9999})   # Group 3: Shorten these 
                              (\"|')"""  # Group 4: " or '
            original_nodelabel = original_nodelabel.replace("\l", "\n")
            for line in original_nodelabel.splitlines():
                tmp_line = re.sub(
                    sub_pattern, r"\1\2...\4", line, flags=re.VERBOSE
                )
                nodelabel += tmp_line + "\l"
        else:
            nodelabel = original_nodelabel
            
        
        linenums = [stat.lineno for stat in block]
        # print(block.id, block.at(), linenums)

        graph.node(
            str(block.id),
            label=nodelabel,
            linenum = str(linenums) if 1 not in linenums else str([block.at()]),
            _attributes={
                "style": f"filled,{self.border_style(block, interactive)}",
                "shape": nodeshape,
                "fillcolor": self.fillcolor(block, interactive, nodecolor),
            },
        )

        if isinstance(block, TryBlock):
            for except_block in block.except_blocks.values():
                self._visit_blocks(graph, except_block, visited, calls, format)

        if calls and block.func_calls:
            calls_node = str(block.id) + "_calls"

            # Remove any duplicates by splitting on newlines and creating a set
            calls_label = block.get_calls().strip()

            # Create a new subgraph for call statement
            calls_subgraph = gv.Digraph(
                name=f"cluster_{block.id}",
                format=format,
                graph_attr={
                    "rankdir": "TB",
                    "ranksep": "0.02",
                    "style": "filled",
                    "color": self.fillcolor(block, interactive, "purple"),
                    "compound": "true",
                    "fontname": "DejaVu Sans Mono",
                    "shape": self.node_styles[ast.Call][0],
                    "label": "",
                },
                node_attr={"fontname": "DejaVu Sans Mono"},
                edge_attr={"fontname": "DejaVu Sans Mono"},
            )    
            # print(self.classcfgs)
            # Generate control flow edges for function arguments
            for func_block in block.func_blocks:
                # print(f"func_block.name{func_block.name}")
                # print(func_block.name, self.allfunctioncfgs)
                if len(self.allfunctioncfgs) > 0 and func_block.name not in self.allfunctioncfgs:
                    if func_block.name not in self.classcfgs:
                        continue
                graph.edge(
                    str(block.id),
                    str(func_block.id),
                    label="calls",
                    _attributes={"style": "dashed"},
                )
                if_linked = False
                # print(func_block.name, self.allfunctioncfgs)
                for sub_func_name in self.functioncfgs:
                    if func_block.name != sub_func_name:
                        continue
                    for first_block in self.functioncfgs[sub_func_name]:
                        if sub_func_name in block.func_calls:
                            graph.edge(
                                    str(func_block.id),
                                    str(first_block.id),
                                    _attributes={"color": "green"}
                                )
                            if_linked = True
                        if if_linked:
                            break
                    if if_linked:
                        break
                for sub_func_name in self.allfunctioncfgs:
                    if func_block.name != sub_func_name:
                        continue
                    for first_block in self.allfunctioncfgs[sub_func_name]:
                        if sub_func_name in block.func_calls:
                            graph.edge(
                                    str(func_block.id),
                                    str(first_block.id),
                                    _attributes={"color": "green"}
                                )
                            if_linked = True
                        if if_linked:
                            break
                    if if_linked:
                        break
                for sub_func_name in self.classcfgs:
                    if func_block.name != sub_func_name:
                        continue
                    for first_block in self.classcfgs[sub_func_name]:
                        if sub_func_name in block.func_calls:
                            graph.edge(
                                    str(func_block.id),
                                    str(first_block.id),
                                    _attributes={"color": "green"}
                                )
                            if_linked = True
                        if if_linked:
                            break
                    if if_linked:
                        break
                self._visit_func(
                    calls_subgraph,
                    func_block,
                    visited=set(),
                    interactive=interactive,
                )
            graph.subgraph(calls_subgraph)

            tmp = ""
            for line in calls_label.splitlines():
                if "input" in line:
                    input_node = str(block.id) + "_input"
                    nodeshape, nodecolor = self.node_styles["input"]
                    graph.node(
                        input_node,
                        label=line,
                        linenum = str([block.at()]),
                        _attributes={
                            "style": f"filled,{self.border_style(block, interactive)}",
                            "shape": nodeshape,
                            "fillcolor": self.fillcolor(
                                block, interactive, nodecolor
                            ),
                        },
                    )
                    graph.edge(input_node, str(block.id))  # yellow
                    # _attributes={'style': 'dashed'})

                else:
                    line += "\l"
                    tmp += line

        # Recursively visit all the blocks of the CFG.
        for exit in block.exits:
            assert block == exit.source
            self._visit_blocks(
                graph,
                exit.target,
                visited,
                calls=calls,
                format=format,
                interactive=interactive,
            )
            edgeshape, edgecolor, edgelabel = self.stylize_edge(exit)
            graph.edge(
                str(block.id),
                str(exit.target.id),
                label=edgelabel,
                _attributes={"color": edgecolor},
            )

    subgraphs: dict = Counter()

    def _build_visual(
        self,
        format: str = "pdf",
        calls: bool = True,
        interactive: bool = False,
        build_own=False,
    ) -> Digraph:
        graph = gv.Digraph(
            name=f"cluster{self.subgraphs[self.name]}{self.name}",
            format=format,
            graph_attr={
                "label": self.name,
                "rankdir": "TB",
                "ranksep": "0.02",
                "fontname": "DejaVu Sans Mono",
                "compound": "True",
                "pack": "False",
            },
            node_attr={"fontname": "DejaVu Sans Mono"},
            edge_attr={"fontname": "DejaVu Sans Mono"},
        )
        self.subgraphs[self.name] += 1
        if self.entryblock is None:
            raise TypeError(
                "Expected self.entryblock to be not None but type is None"
            )
        self._visit_blocks(
            graph,
            self.entryblock,
            visited=set(),
            calls=calls,
            format=format,
            interactive=interactive,
        )
        if build_own:
            return graph
        # Build the subgraphs for the function definitions in the CFG and add
        # them to the graph.
        for subcfg in self.classcfgs:
            subgraph = self.classcfgs[subcfg]._build_visual(
                format=format, calls=calls, interactive=interactive,
            )
            graph.subgraph(subgraph)

        for subcfg in self.functioncfgs:
            subgraph = self.functioncfgs[subcfg]._build_visual(
                format=format, calls=calls, interactive=interactive,
            )
            graph.subgraph(subgraph)
        return graph

    @staticmethod
    def border_style(block: Block, interactive: bool):
        if interactive:
            return "bold" if block.outline else "dashed"
        else:
            return "solid"

    @staticmethod
    def fillcolor(
        block: Block, interactive: bool, color: str, default: str = ""
    ):
        if interactive:
            if block.highlight:
                return color
            else:
                return default
        else:
            return color

    # def build_key(self, **kwargs):
    #     """Build key graph"""
    #     key = self._build_key_subgraph(kwargs.get("format", "svg"))
    #     return key.render(**kwargs)

    def build_visual(
        self,
        filepath: str,
        format: str,
        calls: bool = True,
        show: bool = False,
        cleanup=True,
        directory=None,
        interactive=False,
        build_keys=False,
        build_own=False,
        diffable=None,
    ) -> str:
        """
        Build a visualisation of the CFG with graphviz and output it in a DOT
        file.

        Args:
            filename: The name of the output file in which the visualisation
                      must be saved.
            format: The format to use for the output file (PDF, ...).
            show: A boolean indicating whether to automatically open the output
                  file after building the visualisation.
        """

        if diffable is not None:
            with open(diffable, "w") as fp:
                for block in self:
                    print(
                        f"{block.id} {type(block.statements[0]).__name__}",
                        file=fp,
                    )

        graph = self._build_visual(format, calls, interactive, build_own)
        # if build_keys:
        #     graph.subgraph(self._build_key_subgraph(format))
        return graph.render(
            filepath, view=show, cleanup=cleanup, directory=directory
        )

    def __iter__(self) -> Iterator[Block]:
        """
        Generator that yields all the blocks in the current graph, then
        recursively yields from any sub graphs
        """
        yield from self.own_blocks()
        for subcfg in self.classcfgs.values():
            yield from subcfg

        for subcfg in self.functioncfgs.values():
            yield from subcfg

    def own_blocks(self) -> Iterator[Block]:
        """
        Generator that yields all blocks in the current graph, excluding any
        subgraphs
        """
        visited = set()
        if self.entryblock is None:
            raise TypeError(
                "Expected self.entryblock to be not None but type is None"
            )
        to_visit: Deque[Block] = deque([self.entryblock])
        while to_visit:
            block = to_visit.popleft()
            visited.add(block)
            for exit_ in block.exits:
                if exit_.target in visited or exit_.target in to_visit:
                    continue
                to_visit.append(exit_.target)
            yield block

    def node_ClassDef(
        self, block: Block, typeobj: type
    ) -> Tuple[str, str, str]:
        text = block.get_source().splitlines()[0] + "...\n"
        return (*self.node_styles.get(typeobj, self.DEFAULT), text)

    def node_Try(self, block: Block, typeobj: type) -> Tuple[str, str, str]:
        return (
            *self.node_styles.get(typeobj, self.DEFAULT),
            "\n".join(block.get_source().splitlines()),
        )

    def edge_If(self, link: Link) -> Tuple[None, str, str]:
        _, _, nodelabel = self.stylize_node(link.source)
        color = "red"
        edgelabel = link.get_exitcase().strip()
        if edgelabel in nodelabel:
            color = "green"
        return None, color, edgelabel

    def edge_While(self, link: Link) -> Tuple[None, str, str]:
        _, _, nodelabel = self.stylize_node(link.source)
        color = "red"
        edgelabel = link.get_exitcase().strip()
        if edgelabel in nodelabel:
            color = "green"
        return None, color, edgelabel

    def edge_For(self, link: Link) -> Tuple[None, str, str]:
        _, _, nodelabel = self.stylize_node(link.source)
        color = "red"
        edgelabel = link.get_exitcase().strip()
        if edgelabel in nodelabel:
            color = "green"
        return None, color, edgelabel

    def bsearch(
        self, lineno: int, lst: Optional[list] = None
    ) -> Optional[Block]:
        """Search for a block at line"""

        def _bsearch(lst, low, high, line):
            if high >= low:
                mid = (low + high) // 2
                block = lst[mid]
                if block.at() <= line <= block.end():
                    return block
                elif line < block.at():
                    return _bsearch(lst, low, mid - 1, line)
                else:
                    return _bsearch(lst, mid + 1, high, line)
            else:
                return None

        lst = list(self) if lst is None else lst  # Already sorted by lineno
        return _bsearch(lst, 0, len(lst) - 1, lineno)

    outlined_block = Block(0)
    highlighted_blocks: List[Block] = []

    def outline_block(self, lineno, lst=None) -> int:
        """In interactive mode, outline the block at lineno"""
        self.outlined_block.outline = False
        block = self.bsearch(lineno, lst)
        if block is None:
            return -1
        self.outlined_block = block  # type: ignore
        block.outline = True  # type: ignore
        return 0

    def highlight_blocks(self, lines, blocks=None) -> int:
        """In interactive mode, highlight the block at lineno"""
        for block in self.highlighted_blocks:
            block.highlight = False

        highlighted_blocks: List[Block] = []
        for line in list(lines):
            block = self.bsearch(line, blocks)
            if block is not None:
                block.highlight = True
                highlighted_blocks.append(block)

        self.highlighted_blocks = highlighted_blocks
        return 0

    def find_path(self, finalblock: Block) -> Deque[Link]:
        if self.entryblock is None:
            raise ValueError("entryblock cannot be none")

        assert finalblock in self.finalblocks
        visited: Set[Block] = set()
        path: Deque[Link] = collections.deque()

        def _find_path(link: Link):
            blk: Block = link.target
            if blk in visited:
                return False

            visited.add(blk)
            if blk == finalblock:
                return True

            for lk in blk.exits:
                path.append(lk)
                if _find_path(lk):
                    return True
                path.pop()

        for lk in self.entryblock.exits:
            path.append(lk)
            if _find_path(lk):
                return path
            path.pop()

        # TODO find all possible paths from entry to final and return set
        # TODO find path from any line to any line
        return collections.deque()
