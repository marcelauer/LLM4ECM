from basyx.aas import model
from basyx.aas.adapter import aasx
import xml.etree.ElementTree as ET

######################################################################
#                    AML File Parsing (Extract Technical Data)       #
######################################################################

def extract_internal_elements(xml_path):
    """
    Parses the AML (AutomationML) file to extract InternalElement data,
    including technical properties like name, type, unit, and value.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()
    namespace = {'caex': 'http://www.dke.de/CAEX'}
    internal_elements_data = []

    for internal_element in root.findall(".//caex:InternalElement", namespace):
        element_name = internal_element.get("Name")
        attributes = []

        for attribute in internal_element.findall("caex:Attribute", namespace):
            attr_name = attribute.get("Name")
            attr_type = attribute.get("AttributeDataType")
            attr_unit = attribute.get("Unit", "N/A")

            # Extract <Value> text if exists
            value_element = attribute.find("caex:Value", namespace)
            attr_value = value_element.text if value_element is not None else "N/A"

            attributes.append({
                "name": attr_name,
                "data_type": attr_type,
                "unit": attr_unit,
                "value": attr_value
            })

        internal_elements_data.append({
            "idShort": element_name,
            "technical_properties": attributes
        })

    return internal_elements_data


######################################################################
#                    AML Hierarchy Extraction                        #
######################################################################

def get_hierarchy_string(xml_file):
    """
    Builds a string representation of the AML file's hierarchy.
    """
    printed_names = set()
    hierarchy_str = []

    def traverse_internal_elements(element, level=0):
        # Avoid duplicate printing
        if "Name" in element.attrib:
            name = element.attrib["Name"]
            if name not in printed_names:
                hierarchy_str.append("  " * level + name)
                printed_names.add(name)

        # Recursively traverse children
        for child in element.findall("{http://www.dke.de/CAEX}InternalElement"):
            traverse_internal_elements(child, level + 1)

    tree = ET.parse(xml_file)
    root = tree.getroot()

    for instance_hierarchy in root.findall("{http://www.dke.de/CAEX}InstanceHierarchy"):
        for internal_element in instance_hierarchy.findall("{http://www.dke.de/CAEX}InternalElement"):
            traverse_internal_elements(internal_element)

    return "\n".join(hierarchy_str)


######################################################################
#                 Technical Data Submodel Creation                   #
######################################################################

def technical_data_submodel(element):
    """
    Creates a technical data submodel for a given internal element.
    Includes general info, product classification, and technical properties.
    """
    # General Information
    pop_general_Information_1 = model.Property(
        id_short="ManufacturerName",
        value_type=model.datatypes.String,
        value=f"Producer of {element['idShort']}",
        category='CONSTANT'
    )
    pop_general_Information_2 = model.Property(
        id_short="ManufacturerProductDesignation",
        value_type=model.datatypes.String,
        value=f"Function of {element['idShort']}",
        category='CONSTANT'
    )
    smc_general_information = model.SubmodelElementCollection(
        id_short='GeneralInformation',
        value=(pop_general_Information_1, pop_general_Information_2),
        category='PARAMETER'
    )

    # Product Classification
    smc_product_classification = model.SubmodelElementCollection(
        id_short='ProductClassifications',
        value=(
            model.Property("ProductClassificationSystem", model.datatypes.String, value="ECLASS", category='CONSTANT'),
            model.Property("ClassificationSystemVersion", model.datatypes.String, value="13.0", category='CONSTANT'),
            model.Property("ProductClassId", model.datatypes.String, value="27-02-22-90 High voltage three-phase current asynchronous motor", category='CONSTANT')
        ),
        category='CONSTANT'
    )

    # Technical Properties
    smc_technical_properties = tuple(
        model.Property(id_short=prop['name'], value_type=model.datatypes.String, value=prop['value'] + ' ' + prop['unit'])
        for prop in element['technical_properties']
    )
    smc_technical_properties = model.SubmodelElementCollection(
        id_short='TechnicalProperties',
        value=smc_technical_properties,
        category='CONSTANT'
    )

    # Final Submodel
    return model.Submodel(
        id_=f"https://www.aut.ruhr-uni-bochum.de/SM_{element['idShort']}",
        submodel_element=(smc_general_information, smc_product_classification, smc_technical_properties),
        id_short='TechnicalData'
    )


######################################################################
#                       Bill of Material (BOM)                       #
######################################################################

def parse_hierarchy(hierarchy_str):
    """
    Parses hierarchy string into nested dictionaries representing tree structure.
    """
    hierarchy = {}
    stack = []

    for line in hierarchy_str.split('\n'):
        indent_level = len(line) - len(line.lstrip())
        name = line.strip()
        entity = {"name": name, "children": []}

        while stack and stack[-1]["indent"] >= indent_level:
            stack.pop()

        if stack:
            stack[-1]["entity"]["children"].append(entity)
        else:
            hierarchy[name] = entity

        stack.append({"indent": indent_level, "entity": entity})

    return hierarchy


def create_bom_submodel(hierarchy_str) -> model.Submodel:
    """
    Creates a Bill of Materials (BOM) submodel using parsed hierarchy.
    """

    def create_entity(node):
        children = [create_entity(child) for child in node["children"]]
        entity_type = model.EntityType.SELF_MANAGED_ENTITY if children else model.EntityType.CO_MANAGED_ENTITY
        return model.Entity(
            id_short=node["name"],
            entity_type=entity_type,
            statement=children,
            global_asset_id=None if entity_type == model.EntityType.CO_MANAGED_ENTITY else f"https://www.aut.ruhr-uni-bochum.de/Asset_{node['name']}"
        )

    hierarchy = parse_hierarchy(hierarchy_str)
    entities = [create_entity(node) for node in hierarchy.values()]

    # Add archetype property
    entities.insert(0, model.Property(
        id_short="ArcheType",
        value_type=model.datatypes.String,
        value="Full"
    ))

    return model.Submodel(
        id_='https://www.aut.ruhr-uni-bochum.de/BillOfMaterial',
        submodel_element=entities,
        id_short='BOM',
        kind=model.ModellingKind.INSTANCE
    )


######################################################################
#                Automation Engineering Submodel                     #
######################################################################

def extract_file_info(xml_path):
    """
    Extracts metadata like file name and last writing date from the AML file.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()
    namespaces = {'ns': 'http://www.dke.de/CAEX'}

    file_name = root.attrib.get('FileName')
    source_document = root.find('ns:SourceDocumentInformation', namespaces)
    last_writing_date_time = source_document.attrib.get('LastWritingDateTime') if source_document is not None else None

    return file_name, last_writing_date_time


def parse_internal_links(xml_path):
    """
    Parses internal links between components for connection modeling.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()
    namespace = {'ns': 'http://www.dke.de/CAEX'}

    id_to_name = {}
    id_to_parent_name = {}

    for internal_element in root.findall('.//ns:InternalElement', namespace):
        element_id = internal_element.get('ID')
        element_name = internal_element.get('Name')
        if element_id and element_name:
            id_to_name[element_id] = element_name

    for internal_element in root.findall('.//ns:InternalElement', namespace):
        parent_name = internal_element.get('Name')
        for external_interface in internal_element.findall('.//ns:ExternalInterface', namespace):
            element_id = external_interface.get('ID')
            if element_id:
                id_to_parent_name[element_id] = parent_name

    internal_links = root.findall('.//ns:InternalLink', namespace)
    entities = []

    for index, link in enumerate(internal_links, start=1):
        name = link.get('Name', f'Link{index}')
        ref_a = link.get('RefPartnerSideA')
        ref_b = link.get('RefPartnerSideB')
        ref_a_name = id_to_parent_name.get(ref_a, f'Unknown_{ref_a}')
        ref_b_name = id_to_parent_name.get(ref_b, f'Unknown_{ref_b}')

        wire_relation = model.RelationshipElement(
            id_short='WireRelation',
            first=model.ModelReference((
                model.Key(type_=model.KeyTypes.ASSET_ADMINISTRATION_SHELL, value=f'https://www.aut.ruhr-uni-bochum.de/AAS_{ref_a_name}'),
            ), model.AssetAdministrationShell),
            second=model.ModelReference((
                model.Key(type_=model.KeyTypes.ASSET_ADMINISTRATION_SHELL, value=f'https://www.aut.ruhr-uni-bochum.de/AAS_{ref_b_name}'),
            ), model.AssetAdministrationShell)
        )

        entity = model.Entity(
            id_short=name,
            entity_type=model.EntityType.SELF_MANAGED_ENTITY,
            statement={wire_relation},
            global_asset_id=f'https://www.aut.ruhr-uni-bochum.de_Entity_{name}'
        )

        entities.append(entity)

    return model.SubmodelElementCollection(
        id_short='Connections',
        value=tuple(entities),
        category='CONSTANT'
    )


def create_devices(hierarchy_str) -> model.SubmodelElementCollection:
    """
    Constructs a device hierarchy as SubmodelElementCollection using BOM logic.
    """
    hierarchy = parse_hierarchy(hierarchy_str)

    def create_entity(node):
        children = [create_entity(child) for child in node["children"]]
        entity_type = model.EntityType.SELF_MANAGED_ENTITY if children else model.EntityType.CO_MANAGED_ENTITY
        return model.Entity(
            id_short=node["name"],
            entity_type=entity_type,
            statement=children,
            global_asset_id=None if entity_type == model.EntityType.CO_MANAGED_ENTITY else f"https://www.aut.ruhr-uni-bochum.de/Asset_{node['name']}"
        )

    entities = [create_entity(node) for node in hierarchy.values()]
    entities.insert(0, model.Property("ArcheType", model.datatypes.String, value="Full"))

    return model.SubmodelElementCollection(
        id_short='Devices',
        value=entities,
        category='CONSTANT'
    )


def create_automation_engineering_submodel(xml_file_path):
    """
    Assembles the Automation Engineering submodel with general info, 
    connections, device structure, and PLC config.
    """
    file_name, last_writing_date_time = extract_file_info(xml_file_path)

    smc_general_information = model.SubmodelElementCollection(
        id_short='GeneralInformation',
        value=(
            model.Property("Name", model.datatypes.String, value=file_name),
            model.Property("CreatedAt", model.datatypes.String, value=last_writing_date_time)
        )
    )

    smc_connections = parse_internal_links(xml_file_path)
    smc_devices = create_devices(get_hierarchy_string(xml_file_path))

    smc_plc = model.SubmodelElementCollection(
        id_short='PLCConfiguration',
        value=(
            model.Property("ProductClassificationSystem2", model.datatypes.String, value="ECLASS", category='CONSTANT'),
            model.Property("ClassificationSystemVersion2", model.datatypes.String, value="13.0", category='CONSTANT')
        ),
        category='CONSTANT'
    )

    return model.Submodel(
        id_="https://www.aut.ruhr-uni-bochum.de/SM_Automation_Engineering",
        submodel_element=(smc_general_information, smc_connections, smc_devices, smc_plc),
        id_short='AutomationEngineering'
    )


######################################################################
#                       AAS Creation                                 #
######################################################################

def create_aas_with_submodels(internal_elements, hierarchy_str, xml_file_path):
    """
    Generates AAS objects with associated submodels:
    - TechnicalData per internal element
    - BOM and AutomationEngineering for entire system
    """
    aas_objects = []
    automation_Engineering_submodel = create_automation_engineering_submodel(xml_file_path)
    bom_submodel = create_bom_submodel(hierarchy_str)

    # Main project AAS including BOM and Automation Engineering
    aas_automation_project = model.AssetAdministrationShell(
        id_="https://www.aut.ruhr-uni-bochum.de/Bom_AAS",
        id_short="Automation_Project",
        asset_information=model.AssetInformation(
            asset_kind=model.AssetKind.INSTANCE,
            global_asset_id="https://www.aut.ruhr-uni-bochum.de/Asset_Bom"
        ),
        submodel={
            model.ModelReference.from_referable(bom_submodel),
            model.ModelReference.from_referable(automation_Engineering_submodel)
        }
    )
    aas_objects.extend([bom_submodel, automation_Engineering_submodel, aas_automation_project])

    for element in internal_elements:
        if element["idShort"] == "InternalElement":
            continue

        submodel = technical_data_submodel(element)
        aas = model.AssetAdministrationShell(
            id_=f"https://www.aut.ruhr-uni-bochum.de/AAS_{element['idShort']}",
            id_short=element["idShort"],
            asset_information=model.AssetInformation(
                asset_kind=model.AssetKind.INSTANCE,
                global_asset_id=f"https://www.aut.ruhr-uni-bochum.de/Asset_{element['idShort']}"
            ),
            submodel={model.ModelReference.from_referable(submodel)}
        )
        aas_objects.extend([submodel, aas])

    return model.DictObjectStore(aas_objects)


######################################################################
#                       Get All AAS IDs                              #
######################################################################

def get_all_aas_ids(object_store):
    """
    Returns a list of all Asset Administration Shell (AAS) IDs in the store.
    """
    return [obj.id for obj in object_store if isinstance(obj, model.AssetAdministrationShell)]
