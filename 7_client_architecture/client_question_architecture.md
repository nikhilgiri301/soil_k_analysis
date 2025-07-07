# Client Question Architecture: Soil K Research Requirements

## Overview
This architecture defines the specific scientific questions about soil potassium dynamics that research literature should address. The questions focus on quantifying soil K supply parameters, temporal patterns, regional variations, and sustainability thresholds needed for agricultural demand modeling.

---

## Primary Question Categories

### 1. Quantitative Soil K Supply Parameters
**Core Scientific Question**: What are the measurable annual soil K supply rates that can be integrated into agricultural demand models?

**Sub-questions**:
- **1.1 Annual Supply Rates**: What is the annual release of plant-available K from soil reserves (kg K2O/ha/year)?
- **1.2 Pool Dynamics**: How do exchangeable and non-exchangeable K pools contribute to annual supply?
- **1.3 Release Mechanisms**: What biogeochemical processes control K release rates from soil minerals and organic matter?
- **1.4 Measurement Approaches**: What analytical methods provide reliable quantification of soil K supply rates?

### 2. Temporal Dynamics and Inflection Points
**Core Scientific Question**: How do soil K supply rates change over time, and when do critical transitions occur?

**Sub-questions**:
- **2.1 Seasonal Patterns**: How does soil K availability vary seasonally and what drives these cycles?
- **2.2 Short-term Transitions (2-5 years)**: Are there inflection points where soil K supply rates change significantly within 2-5 years?
- **2.3 Medium-term Transitions (5-15 years)**: What evidence exists for soil K depletion or transition points in 5-15 year timeframes?
- **2.4 Long-term Sustainability (15+ years)**: Can current soil K supply rates be maintained over 15+ year periods?
- **2.5 Depletion Trajectories**: What are the patterns and rates of soil K depletion under different conditions?
- **2.6 Recovery Dynamics**: How do soil K pools recover after depletion, and over what timeframes?

### 3. Probability and Conviction Assessment
**Core Scientific Question**: What is the likelihood that identified temporal patterns and inflection points will occur?

**Sub-questions**:
- **3.1 Pattern Reliability**: How consistently do identified temporal patterns appear across different studies and conditions?
- **3.2 Inflection Point Probability**: What is the scientific evidence strength for predicted inflection points?
- **3.3 Condition Dependencies**: Under what specific conditions are temporal transitions most likely to occur?
- **3.4 Uncertainty Characterization**: What are the confidence bounds around temporal pattern predictions?

### 4. Regional and Environmental Variations
**Core Scientific Question**: How do soil K dynamics vary across different geographic regions and environmental conditions?

**Sub-questions**:
- **4.1 Geographic Patterns**: How do soil K supply rates differ across major agricultural regions?
  - **4.1.1 China**: Soil K dynamics in Chinese agricultural systems
  - **4.1.2 India**: Soil K patterns in Indian agricultural regions
  - **4.1.3 Brazil**: Soil K behavior in Brazilian agricultural areas
  - **4.1.4 United States**: Soil K dynamics in US agricultural systems
  - **4.1.5 Europe**: Soil K patterns in European agricultural regions
- **4.2 Climate Effects**: How do temperature and precipitation patterns affect soil K dynamics?
- **4.3 Soil Type Dependencies**: How do soil texture, mineralogy, and chemistry influence K supply patterns?
- **4.4 Landscape Effects**: How do topography, drainage, and landscape position affect soil K dynamics?

### 5. Agricultural System Integration
**Core Scientific Question**: How do soil K dynamics interact with crops, management practices, and other nutrient cycles?

**Sub-questions**:
- **5.1 Crop Interactions**: How do different crops affect soil K depletion and cycling patterns?
- **5.2 Management Effects**: How do fertilization, tillage, and other practices influence soil K dynamics?
- **5.3 Nutrient Cycling Integration**: How does soil K interact with manure applications and crop residue cycling?
- **5.4 System Sustainability**: What management approaches maintain soil K supply over time?

### 6. Scaling and Extrapolation
**Core Scientific Question**: How can plot and field-scale measurements be scaled to regional and national levels?

**Sub-questions**:
- **6.1 Spatial Scaling**: How do soil K measurements scale from plots to fields to regions?
- **6.2 Temporal Scaling**: How do short-term measurements relate to long-term patterns?
- **6.3 System Scaling**: How do controlled studies relate to real-world agricultural systems?
- **6.4 Uncertainty Propagation**: How does uncertainty change when scaling across space, time, and systems?

---

## Integration Framework

### Demand Model Integration Context
These scientific questions specifically support integration with agricultural demand modeling where:
- **Layer 4.1 Parameter**: Soil K supply rate serves as a major component in demand calculations
- **Regional Specificity**: Different regions require region-specific soil K parameters
- **Temporal Dynamics**: Model assumptions about soil K need temporal sustainability validation
- **Uncertainty Quantification**: Confidence intervals around soil K parameters improve model reliability

### Scientific Priority Hierarchy
1. **Highest Priority**: Quantitative supply rates with temporal sustainability assessment
2. **High Priority**: Regional variations and inflection point identification
3. **Medium Priority**: Process understanding and scaling approaches
4. **Supporting Priority**: Methodological advances and measurement innovations

### Evidence Quality Requirements
- **Quantitative Data**: Numerical measurements with statistical characterization
- **Temporal Coverage**: Multi-year studies preferred over single-season measurements
- **Geographic Relevance**: Studies from target regions or comparable agroecological zones
- **Methodological Rigor**: Peer-reviewed studies with transparent analytical approaches
- **Scaling Validation**: Evidence for extrapolation from measurement scale to application scale

---

## Question Tree Structure for Analysis

```
Soil K Research Requirements
├── 1. Quantitative Parameters
│   ├── 1.1 Annual Supply Rates
│   ├── 1.2 Pool Dynamics  
│   ├── 1.3 Release Mechanisms
│   └── 1.4 Measurement Approaches
├── 2. Temporal Dynamics
│   ├── 2.1 Seasonal Patterns
│   ├── 2.2 Short-term Transitions (2-5y)
│   ├── 2.3 Medium-term Transitions (5-15y)
│   ├── 2.4 Long-term Sustainability (15+y)
│   ├── 2.5 Depletion Trajectories
│   └── 2.6 Recovery Dynamics
├── 3. Probability Assessment
│   ├── 3.1 Pattern Reliability
│   ├── 3.2 Inflection Point Probability
│   ├── 3.3 Condition Dependencies
│   └── 3.4 Uncertainty Characterization
├── 4. Regional Variations
│   ├── 4.1 Geographic Patterns
│   │   ├── 4.1.1 China
│   │   ├── 4.1.2 India
│   │   ├── 4.1.3 Brazil
│   │   ├── 4.1.4 United States
│   │   └── 4.1.5 Europe
│   ├── 4.2 Climate Effects
│   ├── 4.3 Soil Type Dependencies
│   └── 4.4 Landscape Effects
├── 5. Agricultural Integration
│   ├── 5.1 Crop Interactions
│   ├── 5.2 Management Effects
│   ├── 5.3 Nutrient Cycling Integration
│   └── 5.4 System Sustainability
└── 6. Scaling and Extrapolation
    ├── 6.1 Spatial Scaling
    ├── 6.2 Temporal Scaling
    ├── 6.3 System Scaling
    └── 6.4 Uncertainty Propagation
```

---

## Usage Guidelines for Analysis

### For Individual Paper Analysis (Stage 4)
Map each paper's findings to specific question branches where evidence exists, noting:
- **Direct Evidence**: Quantitative data that directly addresses the question
- **Indirect Evidence**: Related findings that inform the question
- **Evidence Quality**: Strength and reliability of evidence for each question
- **Geographic Relevance**: Applicability to target regions
- **Temporal Relevance**: Applicability to target timeframes

### For Cross-Paper Synthesis (Stage 5)
Aggregate evidence across papers for each question branch, characterizing:
- **Consensus**: Where multiple papers provide consistent evidence
- **Conflicts**: Where papers provide contradictory evidence
- **Gaps**: Questions with insufficient evidence across all papers
- **Confidence**: Overall confidence in answers to each question
- **Regional Coverage**: Geographic distribution of evidence

This architecture ensures systematic analysis focused purely on the soil K science needed for agricultural demand modeling.