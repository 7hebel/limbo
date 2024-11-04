from modules.status_bar import status_bar
from modules import nodes
from modules import pos

import os


def read_until_seq(data: bytes | None, end_seq: bytes) -> tuple[bytes, bytes] | tuple[None, None]:
    """ Read buffer until end_seq is met. Returns (leftover, target) or (None, None) if not found. """
    if data is None:
        raise BufferError

    if end_seq not in data:
        return (None, None)

    target, leftover = data.split(end_seq, 1)
    return (leftover, target)


class LimbFormat:
    """ Custom (.limb) file format used to save nodes state. """
    FILE_HEADER = b"LIMB\0"
    NODE_HEADER = b"\\N"
    WIRE_HEADER = b"\\W"
    OUTPUTS_HEADER = b"\\O"
    CONSTS_HEADER = b"\\C"

    VAL_SEP = b","
    SEP = b"\n"
    PTR = b">"
    END = b"\0"
    EOF = b"\\EOF"
    FALSE = b"F"
    TRUE = b"T"
    VOID = b"^"

    @staticmethod
    def import_state(path: str) -> list[nodes.Node]:
        if not os.path.exists(path):
            return status_bar.error(f"Couldn't import state from file: {path} (file not found)")

        saved_nodes: list[nodes.Node] = []
        unlinked_wires: list[bytes] = []
        unattached_consts: list[bytes] = []
        
        def read_node(node_data: bytes) -> nodes.Node | None:
            node_data = node_data[len(LimbFormat.NODE_HEADER):]

            try:
                node_data, is_std = read_until_seq(node_data, LimbFormat.VAL_SEP)
                node_data, node_id = read_until_seq(node_data, LimbFormat.VAL_SEP)
                node_data, factory_id = read_until_seq(node_data, LimbFormat.VAL_SEP)
                node_data, position = read_until_seq(node_data, LimbFormat.END)

                if node_data is None or not node_data.startswith(LimbFormat.OUTPUTS_HEADER):
                    raise BufferError

                node_data = node_data.removeprefix(LimbFormat.OUTPUTS_HEADER)
                while LimbFormat.END in node_data:
                    node_data, wire_data = read_until_seq(node_data, LimbFormat.END)
                    if node_data is None or not wire_data:
                        break

                    unlinked_wires.append(wire_data)
                    
                    if node_data.startswith(LimbFormat.CONSTS_HEADER):
                        break

                node_data = node_data.removeprefix(LimbFormat.CONSTS_HEADER)
                while LimbFormat.END in node_data:
                    node_data, constant_data = read_until_seq(node_data, LimbFormat.END)
                    if node_data is None or not constant_data:
                        break
                    
                    unattached_consts.append(constant_data)
            
            except BufferError:
                return status_bar.error(f"Parsing {path}: failed to read node (left with: {node_data})")

            if node_data:
                return status_bar.error(f"Parsing {path} failed: expected end of line, left with: {node_data}")

            if is_std not in (LimbFormat.TRUE, LimbFormat.FALSE):
                return status_bar.error(f"Parsing {path}: invalid node's StdByte.")

            is_std = is_std == LimbFormat.TRUE
            node_id = node_id.decode()
            factory_id = factory_id.decode()
            position = position.decode()

            x, y = position.split(":")
            x, y = int(x), int(y)

            if not is_std:
                pass

            factory: nodes.NodeFactory = nodes.factories_register.get(factory_id)
            if factory is None:
                return status_bar.error(f"Parsing {path} failed due to invalid FactoryID found: {factory_id} ({nodes.factories_register.keys()})")

            target_node = factory.build_instance()
            target_node.node_id = node_id
            target_node.position = pos.Position(x, y)

            return target_node

        def get_node(node_id: str) -> nodes.Node | None:
            for node in saved_nodes:
                if node.node_id == node_id:
                    return node

        def link_connection(wire_data: bytes) -> bool | None:
            """ \W 59ebd926f0c34838ac5800ee89f3dadf/(FlowOut) > c1fad08a82974f51808d7541b7c0837c/(FlowIn) END """
            if not wire_data.startswith(LimbFormat.WIRE_HEADER):
                return status_bar.error(f"Parsing {path} failed due to invalid connection header at wire: {wire_data}")
            
            if LimbFormat.PTR not in wire_data:
                return status_bar.error(f"Parsing {path} failed due to missing connection pointer at: {wire_data}")
            
            wire_data = wire_data.removeprefix(LimbFormat.WIRE_HEADER)
            out_data, in_data = wire_data.split(LimbFormat.PTR)
            out_data, in_data = out_data.decode(), in_data.decode()
            
            out_nodeid, out_src = out_data.split("/", 1)
            in_nodeid, in_src = in_data.split("/", 1)
            
            out_node = get_node(out_nodeid)
            if out_node is None:
                return status_bar.error(f"Parsing {path} failed due to missing output source node: {out_nodeid}")
            
            in_node = get_node(in_nodeid)
            if in_node is None:
                return status_bar.error(f"Parsing {path} failed due to missing input source node: {in_nodeid}")
            
            out_src = out_node.get_output_src(out_src)
            if out_src is None:
                return status_bar.error(f"Parsing {path} failed due to missing output source: {out_nodeid}/{out_src}")

            in_src = in_node.get_input_src(in_src)
            if in_src is None:
                return status_bar.error(f"Parsing {path} failed due to missing input source: {in_nodeid}/{in_src}")
                
            nodes.connect_sources(out_src, in_src)
            return True

        def set_constant(constant_data: bytes) -> None:
            if LimbFormat.PTR not in constant_data:
                return status_bar.error(f"Parsing {path} failed due to missing pointer at constant: {constant_data}")
                
            src_path, value = constant_data.split(LimbFormat.PTR)
            node_id, input_name = src_path.decode().split("/", 1)
            
            node = get_node(node_id)
            if node is None:
                return status_bar.error(f"Parsing {path} failed due to missing constant source node: {node_id}")
            
            input_src = node.get_input_src(input_name)
            if input_src is None:
                return status_bar.error(f"Parsing {path} failed due to missing constant input source: {input_name}")
            
            input_src.set_constant(value.decode())
            return True

        with open(path, "rb") as file:
            header = file.readline().removesuffix(LimbFormat.SEP)
            if header != LimbFormat.FILE_HEADER:
                return status_bar.error(f"Couldn't import state from file: {path} (invalid file header)")

            if LimbFormat.EOF not in file.read():
                return status_bar.error(f"Couldn't import state from file: {path} (no EOF byte found)")

            file.seek(0)

            line = None
            while line != LimbFormat.EOF:
                line = file.readline().removesuffix(LimbFormat.SEP)

                if line.startswith(LimbFormat.NODE_HEADER):
                    parsed_node = read_node(line)
                    if parsed_node is None:
                        return

                    saved_nodes.append(parsed_node)

        for wire_data in unlinked_wires:
            if not link_connection(wire_data):
                return
            
        for constant_data in unattached_consts:
            if not set_constant(constant_data):
                return

        status_bar.set_message(f"Succesfully imported {len(saved_nodes)} nodes")
        return saved_nodes


    @staticmethod
    def export(nodes_state: list[nodes.Node], path: str) -> None:
        """ Save nodes state into file at given path. File should exist. """

        def parse_output_wire(output: nodes.NodeOutput) -> bytes:
            """ Parse wire connection between output and input. Returns blank bytes if target is None. """
            input_ = output.target
            if input_ is None:
                return b""

            content = LimbFormat.WIRE_HEADER
            content += f"{output.node.node_id}/{output.name}".encode()

            content += LimbFormat.PTR
            content += f"{input_.node.node_id}/{input_.name}".encode()

            content += LimbFormat.END

            return content
        
        def parse_const_value(input_src: nodes.NodeInput) -> bytes:
            if input_src is None or input_src.constant_value is None:
                return b""
            
            content = f"{input_src.node.node_id}/{input_src.name}".encode()
            content += LimbFormat.PTR

            const_value = input_src.constant_value
            if isinstance(const_value, bool):
                const_value = int(const_value)
                
            content += f"{const_value}".encode()
            content += LimbFormat.END
            
            return content

        def parse_node(node: nodes.Node) -> bytes:
            """
            Convert Node into savable format.

            Format (no spaces):
                \\N is_std; node_id; factory_id; position x:y; flow_out/Void; outputs;
            """
            content = LimbFormat.NODE_HEADER
            content += LimbFormat.TRUE if node.factory.factory_id.startswith("std/") else LimbFormat.FALSE

            content += LimbFormat.VAL_SEP
            content += node.node_id.encode()

            content += LimbFormat.VAL_SEP
            content += node.factory.factory_id.encode()

            content += LimbFormat.VAL_SEP
            content += f"{node.position.x}:{node.position.y}".encode()

            content += LimbFormat.END
            content += LimbFormat.OUTPUTS_HEADER

            if node.flow.output_src is not None:
                content += parse_output_wire(node.flow.output_src)

            for output_src in node.outputs:
                if output_src.target:
                    content += parse_output_wire(output_src)

            content += LimbFormat.END
            content += LimbFormat.CONSTS_HEADER
            
            for input_src in node.inputs:
                if input_src.constant_value is not None:
                    content += parse_const_value(input_src)

            return content

        content = LimbFormat.FILE_HEADER
        content += LimbFormat.SEP

        for node in nodes_state:
            content += parse_node(node)
            content += LimbFormat.SEP

        content += LimbFormat.EOF

        with open(path, "wb+") as file:
            file.write(content)

        status_bar.set_message(f"Saved into: {path}")


