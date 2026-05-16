from basyx.aas import model
from basyx.aas.adapter import aasx
import xml.etree.ElementTree as ET
import AML2AAS_Functions as aml2aas

# --------------------------------------------------------------------------------------
# Step 1: Setting up a SupplementaryFileContainer and AAS & Submodel with File objects
# --------------------------------------------------------------------------------------

# Define file container
file_store = aasx.DictSupplementaryFileContainer()

# Define paths
xml_path = r"C:\Users\Rezaee\Desktop\Files\RUB\Paper\4 - ETFA 2025\VERA\XML_Vera.xml"
aas_path = r"C:\Users\Rezaee\Desktop\Files\RUB\Paper\4 - ETFA 2025\VERA\AAS_Vera.aasx"

# Extract internal elements and create AAS with submodels
internal_elements = aml2aas.extract_internal_elements(xml_path)
object_store = aml2aas.create_aas_with_submodels(
    internal_elements,
    aml2aas.get_hierarchy_string(xml_path),
    xml_path
)

# Write AASX package
with aasx.AASXWriter(aas_path) as writer:
    writer.write_aas(
        aas_ids=aml2aas.get_all_aas_ids(object_store),
        object_store=object_store,
        file_store=file_store
    )

    # Optionally write empty object store to a separate part
    objects_to_be_written: model.DictObjectStore[model.Identifiable] = model.DictObjectStore([])
    writer.write_all_aas_objects(
        part_name="/aasx/my_aas_part.xml",
        objects=objects_to_be_written,
        file_store=file_store
    )
