from io import StringIO

from dsviper import AttachmentGetting

import html_renderer
from dsviper import DocumentNode, Html, ValueKey, ValueEnumeration, PathConst, KeyNamer, ValueUUId, ValueBool
from flask import url_for


class HtmlDocumentsRenderer:
    def __init__(self, document_nodes: list[DocumentNode],
                 abstraction_runtime_id: ValueUUId,
                 key_namer: KeyNamer,
                 attachment_getting: AttachmentGetting,
                 path: PathConst | None = None,
                 show_type: bool = False):
        self.document_nodes = document_nodes
        self.abstraction_runtime_id = abstraction_runtime_id
        self.key_namer = key_namer
        self.attachment_getting = attachment_getting
        self.path = path
        self.show_type = show_type
        self.io = StringIO()

    def html(self) -> str:
        for node in self.document_nodes:
            self.render_node(node, 0)
        return self.io.getvalue()

    def render_details(self, node: DocumentNode, level: int):
        open_attrib = "open" if self.is_open(node, level) else ""
        self.write(f'<details {open_attrib} id="{node.uuid().encoded()}">')

        self.write(f'<summary>{node.string_component()}')
        if self.show_type:
            self.render_type(node)

        if node.is_collection():
            self.write(html_renderer.sp())
            self.write(f'[{node.string_value()}]')
        self.write('</summary>')

        self.write('<div class="details_indent">')
        for child_node in node.children():
            self.render_node(child_node, level + 1)
        self.write('</div>')

        self.write(f'</details>')

    def render_node(self, node: DocumentNode, level: int):
        if node.is_expandable():
            self.render_details(node, level)
        else:
            self.render_value(node)

    def render_value(self, node: DocumentNode):
        self.write('<div>')
        self.write(f'{node.string_component()}')

        if node.is_collection():
            self.write(html_renderer.sp())
            self.write(f'[{node.string_value()}]')
        else:
            self.write(html_renderer.sp())
            editable = node.is_editable() and not node.is_blob_id()
            if editable:
                self.write(f'<form method="post" action="{url_for("update")}" autocomplete="off">')
                self.write(f'<button type="submit" disabled style="display:none" ></button>')
                self.write(f'<input type="hidden" name="abstraction_runtime_id" value="{self.abstraction_runtime_id}"/>')
                self.write(f'<input type="hidden" name="concept_runtime_id" value="{node.key().type_concept().runtime_id().encoded()}"/>')
                self.write(f'<input type="hidden" name="instance_id" value="{node.key().instance_id().encoded()}"/>')
                self.write(f'<input type="hidden" name="node_uuid" value="{node.uuid().encoded()}"/>')

                if node.is_boolean():
                    self.render_value_boolean(node)
                elif node.is_integer():
                    self.render_value_integer(node)
                elif node.is_real():
                    self.render_value_real(node)
                elif node.is_string():
                    self.render_value_string(node)
                elif node.is_enumeration():
                    self.render_value_enumeration(node)
                if self.show_type:
                    self.render_type(node)

                self.write("<button type='submit' class='update'>Update</button>")
                self.write(f'</form>')
            else:
                self.render_assigment()
                self.write(self.render_representation(node))
                if self.show_type:
                    self.render_type(node)

        self.write('</div>')

    def render_value_boolean(self, node: DocumentNode):
        checked = "checked" if ValueBool.cast(node.value()).encoded() else ""
        self.write(f'<input id="{node.uuid().encoded()}" name="value" type="checkbox" {checked}/>')

    def render_value_enumeration(self, node: DocumentNode):
        v = ValueEnumeration.cast(node.value())
        self.render_assigment()
        self.write(f'<select id="{node.uuid().encoded()}" name="value">')
        for elt in v.type_enumeration().cases():
            selected = 'selected' if elt.name() == v.name() else ""
            self.write(f'<option name="value" value=".{elt.name()}" {selected}>{elt.name()}</option>')
        self.write(f'</select>')

    def render_assigment(self):
        self.write(html_renderer.op("="))
        self.write(html_renderer.sp())

    def render_value_integer_with_range(self, node: DocumentNode, r_min: int, r_max: int):
        self.write(f'<input id="{node.uuid().encoded()}" type="number" name="value" value="{node.string_value()}" class="numeric" min="{r_min}"  max="{r_max}" required/>')

    def render_value_integer(self, node):
        if node.is_uint8():
            self.render_value_integer_with_range(node, 0, 255)
        elif node.is_uint16():
            self.render_value_integer_with_range(node, 0, 65536)
        elif node.is_uint32():
            self.render_value_integer_with_range(node, 0, 4294967296)
        elif node.is_uint64():
            self.render_value_integer_with_range(node, 0, 18446744073709551616)

        elif node.is_int8():
            self.render_value_integer_with_range(node, -128, 127)
        elif node.is_int16():
            self.render_value_integer_with_range(node, -32668, 32767)
        elif node.is_int32():
            self.render_value_integer_with_range(node, -2147483648, 2147483647)
        elif node.is_int64():
            self.render_value_integer_with_range(node, -9223372036854775808, 9223372036854775807)

    def render_value_real(self, node: DocumentNode):
        self.render_assigment()
        self.write(f'<input id="{node.uuid().encoded()}" type="text" name="value" value="{node.string_value()}" required class="numeric"/>')

    def render_value_string(self, node: DocumentNode):
        self.render_assigment()
        self.write(f'<input id="{node.uuid().encoded()}" type="text" name="value" value="{node.string_value()}" required class="string"/>')

    def render_representation(self, node: DocumentNode) -> str:
        v = node.value()
        if node.is_boolean():
            return html_renderer.keyword(v.representation())
        if node.is_string():
            return html_renderer.string(v.representation())
        if node.is_uuid():
            return html_renderer.uuid(v.representation())
        if node.is_blob_id():
            return html_renderer.uuid(v.representation())
        if node.is_enumeration():
            return html_renderer.user_type(v.representation())
        if node.is_key():
            return self.render_key(node)
        if node.is_numeric():
            return html_renderer.number(v.representation())

        return node.string_value()

    def render_key(self, node: DocumentNode) -> str:
        key = ValueKey.cast(node.value())
        url = url_for('documents',
                      abstraction_runtime_id=self.abstraction_runtime_id.encoded(),
                      concept_runtime_id=key.type_concept().runtime_id().encoded(),
                      instance_id=key.instance_id().encoded())

        result = f'<a href="{url}">{html_renderer.uuid(node.string_value())}</a>'
        name = self.key_namer.smart_name(key, self.attachment_getting)
        if name:
            result += f' [{name}]'
        return result

    def render_type(self, node: DocumentNode):
        self.write(html_renderer.op(':'))
        self.write(html_renderer.sp())
        self.write(Html.type(node.value().type()))

    def write(self, content: str):
        self.io.write(content)

    def is_open(self, node: DocumentNode, level: int):
        if level == 0:
            return True

        if self.path:
            return self.path.has_prefix(node.path())

        return False

