# 🔗 Towards Interoperable Automation Engineering  
**Mapping AutomationML to AAS Submodels**

## 📄 Overview

This repository contains the implementation and supplementary materials for the paper:

**"Towards Interoperable Automation Engineering: Mapping AutomationML to AAS Submodels"**  
Hesam Rezaee Ahvanouee, Franz Christopher Kunze, Alexander Fay — Ruhr-University Bochum and Julian Rahm — EPLAN GmbH & Co. KG

The project introduces a middleware solution that maps **AutomationML (AML)** project descriptions to **Asset Administration Shell (AAS)** submodels, particularly focusing on the **Automation Engineering Submodel** as defined by the Industrial Digital Twin Association (IDTA).





![Mapping - Overview](Mapping.png)




## 🎯 Purpose

The goal of this project is to enhance interoperability in automation engineering by:
- Analyzing the semantic structures of AML and AAS.
- Mapping AML Component Descriptions to the Automation Engineering Submodel.
- Implementing a middleware using the **BaSyx Python SDK** to perform this transformation.
- Validating the approach with a case study.



## 🧩 Technologies Used

- **AutomationML (AML)**: XML-based format for data exchange in automation engineering.
- **Asset Administration Shell (AAS)**: Digital representation of assets following the Industry 4.0 paradigm.
- **BaSyx Python SDK**: SDK provided by Eclipse BaSyx for working with AAS.
- **Python 3.9+**



## 🧰 Dependencies

### 🔗 [Eclipse BaSyx Python SDK](https://github.com/eclipse-basyx/basyx-python-sdk)

This project leverages the **BaSyx Python SDK**, developed by the Eclipse BaSyx project, which provides essential tools for working with the Asset Administration Shell (AAS) and Digital Twins in Python. The SDK includes:

- AAS metamodel implementation in Python
- Functionality to create, modify, and serialize AAS submodels
- REST APIs for interaction with AAS components
- Utilities for developing AAS-based applications

> **Note:** Make sure to install this dependency using `pip` or clone the repo as part of your development environment.





## 🛠️ Project Structure

```bash
📁 aml-to-aas-middleware/
├── AML2AAS.py             # Main script to run the AML to AAS conversion
├── AML2AAS_Functions.py   # Core mapping logic and helper functions
├── AML_Vera.aml           # Input AutomationML file (VERA plant)
├── XML_Vera.xml           # Alternative or parsed XML version of the AML project
├── AAS_Vera.aasx          # Output Asset Administration Shell package
├── Vera.png               # VERA pilot plant image (used in documentation)
├── Mapping.png            # Developed Concept image (used in documentation)
└── README.md              # Project documentation and usage guide

```





## 🧪 Use Case

To validate our proposed mapping approach, we applied the middleware to a real-world automation project: the **VERA chemical pilot plant** (*Verfahrenstechnische Pilotanlage*), a modular process engineering test facility.

![VERA Pilot Plant - Overview](Vera.png)

The **AML project of VERA**, based on standard AutomationML libraries, served as the input for our transformation. This pilot plant includes:

- 8 process tanks with distinct roles in the chemical workflow
- various sensors and actuators
- A complex interconnecting piping system
- Standard industrial components from common automation suppliers

The 4 upper tanks of the plant serve as raw material reservoirs or intermediate storage units, feeding processes downstream. The rich structural data encoded in AML—including topology, component hierarchy, and connectivity—was successfully translated into the **Automation Engineering Submodel** format using our middleware.

### ✅ Benefits Demonstrated:
- **Accurate semantic mapping** of AML elements to AAS submodel elements
- **Improved consistency** in representing component relationships and functions
- **Support for lifecycle-wide interoperability**, from design to operation
- **Reusability** of engineering data across tools and platforms
- **Compatibility** with AAS-based digital twin frameworks and APIs

This case study proves the feasibility and practical value of our middleware solution, showcasing how AML-based projects can be enriched with AAS features such as security, multi-format support, and lifecycle integration.

## 📬 Contact

For questions, collaboration, or further information, feel free to contact us:

- **Hesam Rezaee Ahvanouee**  
  Ruhr-University Bochum, Chair of Automation  
  📧 [hesam.rezaeeahvanouee@rub.de](mailto:hesam.rezaeeahvanouee@rub.de)




