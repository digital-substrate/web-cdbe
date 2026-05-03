import os

from dsviper import CommitMutableState
from flask import Flask, render_template, request, redirect, url_for
from dsviper import TypeKey, TypeSet, Type, TypeConcept, TypeClub, TypeAnyConcept
from dsviper import CommitDatabase, KeyNamer, ValueUUId, ValueKey, ValueSet
from dsviper import DocumentNode

from html_documents_renderer import HtmlDocumentsRenderer

FILENAME = "database.link"
if not os.path.exists(FILENAME):
    print(f'* The symbolic link to the CommitDatabase is missing.')
    print(f'use ln -sf <commit_database_path> {FILENAME}')
    print(f'\nRaptor demo:')
    print("$ ln -sf ~/Databases/Raptor/demo_sync_server.rapmc database.link")
    print(f'\nGraph Editor demo:')
    print("$ ln -sf ~/Databases/demo_sync_server.graph database.link")
    exit(1)

print(f' * Database: {os.readlink(FILENAME)}')

app = Flask(__name__)

@app.get('/')
def abstractions():
    db = CommitDatabase.open(FILENAME)
    definitions = db.definitions()
    types = []
    for concept in definitions.concepts():
        types.append(concept)

    for club in definitions.clubs():
        types.append(club)

    for attachment in definitions.attachments():
        if attachment.key_type() == Type.ANY_CONCEPT:
            types.append(Type.ANY_CONCEPT)
            break

    types.sort(key=lambda t: t.representation())
    return render_template("abstractions.html", types=types)


class TemplateKey:
    def __init__(self, key: ValueKey, name: str):
        self.__key = key
        self.__name = name

    @property
    def name(self) -> str:
        return self.__name

    @property
    def concept_runtime_id(self) -> str:
        return self.__key.type_concept().runtime_id().encoded()

    @property
    def instance_id(self) -> str:
        return self.__key.instance_id().encoded()


@app.route('/keys/<uuid:abstraction_runtime_id>')
def keys(abstraction_runtime_id):
    abstraction_runtime_id = ValueUUId.create(str(abstraction_runtime_id))
    db = CommitDatabase.open(FILENAME)
    definitions = db.definitions()
    viper_type = definitions.check_type(abstraction_runtime_id)
    type_key = TypeKey(viper_type)
    collected_keys = ValueSet(TypeSet(type_key))
    attachment_getting = db.state(db.last_commit_id()).attachment_getting()

    for attachment in definitions.attachments():
        if attachment.type_key() == type_key:
            collected_keys |= attachment_getting.keys(attachment)
    key_namer = KeyNamer(definitions)
    template_keys: list[TemplateKey] = []
    for key in collected_keys:
        name = key_namer.smart_name(key, attachment_getting) or '-'
        template_keys.append(TemplateKey(key, name))

    name = abstraction_name(viper_type)

    return render_template("keys.html",
                           abstraction_runtime_id=abstraction_runtime_id,
                           name=name,
                           keys=template_keys)


def abstraction_name(vpr_type: Type) -> str:
    if isinstance(vpr_type, TypeConcept):
        return TypeConcept.cast(vpr_type).type_name().name()
    elif isinstance(vpr_type, TypeClub):
        return TypeClub.cast(vpr_type).type_name().name()
    elif isinstance(vpr_type, TypeAnyConcept):
        return Type.ANY.type_name().name()
    return "???"


@app.route('/documents/<uuid:abstraction_runtime_id>/<uuid:concept_runtime_id>/<uuid:instance_id>')
def documents(abstraction_runtime_id, concept_runtime_id, instance_id):
    abstraction_runtime_id = ValueUUId.create(str(abstraction_runtime_id))
    concept_runtime_id = ValueUUId.create(str(concept_runtime_id))
    instance_id = ValueUUId.create(str(instance_id))

    db = CommitDatabase.open(FILENAME)
    definitions = db.definitions()
    concept = definitions.check_concept(concept_runtime_id)
    key = ValueKey.create(concept, instance_id)
    attachment_getting = db.state(db.last_commit_id()).attachment_getting()
    doc = DocumentNode.create_documents(key, attachment_getting)

    key_namer = KeyNamer(definitions)
    renderer = HtmlDocumentsRenderer(doc, abstraction_runtime_id, key_namer, attachment_getting)
    content = renderer.html()
    return render_template("documents.html",
                           abstraction_runtime_id=abstraction_runtime_id,
                           concept_runtime_id=concept_runtime_id,
                           instance_id=instance_id,
                           content=content)


@app.post('/update')
def update():
    abstraction_runtime_id = ValueUUId.create(request.form['abstraction_runtime_id'])
    concept_runtime_id = ValueUUId.create(request.form['concept_runtime_id'])
    instance_id = ValueUUId.create(request.form['instance_id'])
    node_uuid = ValueUUId.create(request.form['node_uuid'])
    value = request.form.get('value')

    db = CommitDatabase.open(FILENAME)
    definitions = db.definitions()
    concept = definitions.check_concept(concept_runtime_id)
    key = ValueKey.create(concept, instance_id)
    attachment_getting = db.state(db.last_commit_id()).attachment_getting()
    doc = DocumentNode.create_documents(key, attachment_getting)

    node = find_node(node_uuid, doc)
    if node:
        value = value_to_python(node, value)
        state = db.state(db.last_commit_id())
        mutable_state = CommitMutableState(state)
        mutable_state.attachment_mutating().update(node.attachment(), node.key(), node.path().regularized().const(), value)
        db.commit_mutations("Update From The Web", mutable_state)

    url = url_for("documents_node",
                  abstraction_runtime_id=abstraction_runtime_id.encoded(),
                  concept_runtime_id=concept_runtime_id.encoded(),
                  instance_id=instance_id.encoded(),
                  node_uuid=node.uuid().encoded())

    # return redirect(f'{url}#{node.uuid}')
    return redirect(f'{url}')


@app.route('/documents_node/<uuid:abstraction_runtime_id>/<uuid:concept_runtime_id>/<uuid:instance_id>/<uuid:node_uuid>')
def documents_node(abstraction_runtime_id, concept_runtime_id, instance_id, node_uuid):
    abstraction_runtime_id = ValueUUId.create(str(abstraction_runtime_id))
    concept_runtime_id = ValueUUId.create(str(concept_runtime_id))
    instance_id = ValueUUId.create(str(instance_id))
    node_uuid = ValueUUId.create(str(node_uuid))

    db = CommitDatabase.open(FILENAME)
    definitions = db.definitions()
    concept = definitions.check_concept(concept_runtime_id)
    key = ValueKey.create(concept, instance_id)
    attachment_getting = db.state(db.last_commit_id()).attachment_getting()
    doc = DocumentNode.create_documents(key, attachment_getting)

    key_namer = KeyNamer(definitions)
    node = find_node(node_uuid, doc)
    if node:
        renderer = HtmlDocumentsRenderer(doc, abstraction_runtime_id, key_namer, attachment_getting, node.path())
    else:
        renderer = HtmlDocumentsRenderer(doc, abstraction_runtime_id, key_namer, attachment_getting)

    content = renderer.html()
    return render_template("documents.html",
                           abstraction_runtime_id=abstraction_runtime_id,
                           concept_runtime_id=concept_runtime_id,
                           instance_id=instance_id,
                           content=content)


def find_node(uuid: ValueUUId, document_nodes: list[DocumentNode]) -> DocumentNode | None:
    for node in document_nodes:
        found = find_node_aux(uuid, node)
        if found:
            return found
    return None


def find_node_aux(uuid: ValueUUId, node: DocumentNode):
    if node.uuid() == uuid:
        return node
    if node.is_expandable():
        for child_node in node.children():
            found = find_node_aux(uuid, child_node)
            if found:
                return found
    return None


def value_to_python(node: DocumentNode, value: str):
    if node.is_boolean():
        return True if value else False
    if node.is_integer():
        return int(value)
    if node.is_real():
        return float(value)
    return value


if __name__ == '__main__':
    app.run()
