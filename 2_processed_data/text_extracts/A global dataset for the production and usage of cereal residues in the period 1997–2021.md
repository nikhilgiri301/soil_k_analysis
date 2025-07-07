## **OPEN**

### **Data Descriptor**



www.nature.com/scientificdata

# **A global dataset for the production** **and usage of cereal residues in the** **period 1997–2021**


**[Andrew Smerald](http://orcid.org/0000-0003-2026-273X)** [ ✉] **[, Jaber Rahimi & Clemens Scheer](http://orcid.org/0000-0002-2754-2358)**


**Crop residue management plays an important role in determining agricultural greenhouse gas**
**emissions and related changes in soil carbon stocks. However, no publicly-available global dataset**
**currently exists for how crop residues are managed. Here we present such a dataset, covering the period**
**1997–2021, on a 0.5° resolution grid. For each grid cell we estimate the total production of residues**
**from cereal crops, and determine the fraction of residues (i) used for livestock feed/bedding, (ii) burnt**
**on the field, (iii) used for other off-field purposes (e.g. domestic fuel, construction or industry), and**
**(iv) left on the field. This dataset is the first of its kind, and can be used for multiple purposes, such as**
**global crop modelling, including the calculation of greenhouse gas inventories, estimating crop-residue**
**availability for biofuel production or modelling livestock feed availability.**


**Background & Summary**
Above-ground crop residues, such as the stalks and stover of cereal plants, are an important resource, since they
represent more biomass than is harvested as grain and have an embodied energy equal to about 15% of global
human primary energy usage [1] (below-ground residues are not considered here since, for cereals, they are almost
never removed from the field). They account for approximately 19% of livestock feed by weight, and are therefore crucial for the production of meat and milk [2][,][3] . They also play an important role as a domestic fuel, especially
in poorer countries. For example, during the mid 1990s in China biomass burning, of which crop residues constituted more than 50%, provided more energy than was derived from oil [4] . Residues left on the field are also an
important source of C and N for agricultural soils, helping to maintain or enhance soil organic carbon (SOC)
stocks [5][–][7], resulting in better retention of nutrients in the soil, reduced sensitivity of plant growth to drought,
lower erosion rates and better soil aeration [8] . At the same time, approximately 10% of crop residues are treated as
a waste product and burnt on the field [9] . This clears the way for subsequent planting, helps to control pests and
diseases and avoids the costs associated with collecting and transporting the residues. However, burning releases
particles into the atmosphere that are damaging to human health and contributes to climate change via CH 4 and
N 2 O emissionsThe scientific literature contains a variety of suggestions for how a change in crop residue management could [10][–][12] .
address pressing global issues, such as climate change or the loss of naturally vegetated land. These include
partial replacement of fossil fuels with bioenergy generated from crop residues [1][,][13][–][15], leaving a higher fraction of crop residues on the field to increase SOC stocks and thus sequester CO 2 from the atmosphere [16] and
replacing human-edible grains in livestock diets with crop residues, allowing for a reduction in cropland area [17] .
Unfortunately, assessing the effectiveness of any of these proposals is hindered by a lack of knowledge about how
crop residues are currently being used, leading to an uncertain baseline and making it difficult to determine the
trade-offs associated with allocating a higher fraction of crop residues to a specific usage.
Here we address this knowledge gap by constructing a dataset showing crop residue management for cereals on a 0.5° global grid and at an annual timescale for the period 1997–2021. We focus on cereals, since they
account for the majority of crop residue production (approximately 73% in 2020 [18] ), and have a similar energy
and protein content, making them relatively uniform in their potential uses [19] . In each grid cell we estimate both
crop residue production and the fraction of crop residues that are (1) burnt on the field (2) used for animal
feed or bedding (3) used for other off-field purposes such as domestic fuel, industry, mushroom cultivation or
construction and (4) left on the field (see Fig. 1). We consider a relatively fine spatial scale, since the high cost


Institute of Meteorology and Climate Research, Atmospheric Environmental Research (IMK-IFU), Karlsruhe Institute of
Technology (KIT), Kreuzeckbahnstr. 19, 82467, Garmisch-Partenkirchen, Germany. [✉] [e-mail: andrew.smerald@kit.edu](mailto:andrew.smerald@kit.edu)



Scientific **Data** | _(2023) 10:685_ [| https://doi.org/10.1038/s41597-023-02587-0](https://doi.org/10.1038/s41597-023-02587-0) 1


www.nature.com/scientificdata/ www.nature.com/scientificdata



**a** **e** Global crop residue usage










|S. Asia<br>580 Tg|Animal<br>usage<br>1100 Tg<br>(950 -<br>1140 Tg)<br>Left on<br>field<br>1490 Tg<br>(1310 -<br>1720 Tg)<br>Other<br>540 Tg<br>(430 -<br>680 Tg)<br>Burnt<br>210 Tg|
|---|---|
|S. S. Afr.<br>290 Tg|S. S. Afr.<br>290 Tg|
|L. Am.<br>280 Tg<br>|L. Am.<br>280 Tg<br>|
|M.E.N.A.<br>140 Tg|M.E.N.A.<br>140 Tg|
|E. Asia<br>640 Tg|E. Asia<br>640 Tg|
|N. Am.<br>460 Tg|N. Am.<br>460 Tg|
|S.E. Asia<br>320 Tg|S.E. Asia<br>320 Tg|
|Europe<br>390 Tg<br>|Europe<br>390 Tg<br>|
|||
|Eurasia<br>180 Tg|Eurasia<br>180 Tg|






**Fig. 1** Management of cereal residues in the period 1997–2021. ( **a** – **d** ) The fraction of residues ( **a** ) burnt, ( **b** )
used for livestock, ( **c** ) used for other off-field purposes, ( **d** ) and left on the field, averaged over the period and
shown on a 0.5° global grid. ( **e** ) Crop residue production and usage on a regional scale, averaged over the
period. Values in brackets show the range of values when taking all 18 calculational schemes into account. ( **f** )
Timeseries of global crop residue management. The percentages show the average crop residue usage across the
period and brackets show the range across the 18 calculational schemes.


of transporting crop residues means that trade-offs between possible management options typically occur at a
local level [20] .
We envisage two main uses for the dataset. First, it can be used to improve assessments of the environmental
impact of current and possible future agricultural practices, where it has been shown that crop residue manageing (e.g. NOment affects greenhouse gas emissions 3− ) 23,27 . Currently, crop models, which are a common tool for such assessments, typically assume a [6][,][21][–][26], emissions of atmospheric pollutants (e.g. NH 3 ) and nutrient leachglobally uniform fraction of crop residues left on the field [28][–][31], and assess changes in crop residue management


Scientific **Data** | _(2023) 10:685_ [| https://doi.org/10.1038/s41597-023-02587-0](https://doi.org/10.1038/s41597-023-02587-0) 2


www.nature.com/scientificdata/ www.nature.com/scientificdata











































Crop residue
production





**Fig. 2** Schematic overview of the calculation of crop residue usage. Output data is shown in the bottom row.
Datasets (see Table 1) and data processing steps are coloured according to the output data to which they
contribute. Black lines show the number of independent calculations carried through the calculation scheme.
Each independent calculation is due to a different combination of input data/methods.

|Dataset name|Year(s) Sp|atial resolution|Description|
|---|---|---|---|
|Spatial Production Allocation<br>Model (SPAM)42,43|2010<br>5 a|rcmin global grid|Crop specifc production and harvested areas|
|FAOSTAT9|1997–2021<br>Co|untry|Crop and livestock production, GDP|
|Global Fire Emissions Database<br>(GFED4s)45,46|1997–2021 (monthly)<br>0.2|5° global grid|Biomass burning split by vegetation type|
|Te Fire Inventory from NCAR<br>(FINNv2.5)47,48|2001–2021<br>Po|int based|List of fres, including location, date, biomass burnt and<br>vegetation type|
|Global Distribution of<br>Ruminant Livestock Production<br>Systems (GRPS 5)55|2000s<br>5 a|rcmin global grid|Dominant livestock production system in each grid cell.|
|Gridded Livestock of the World<br>(GLW 3)50–53,56,57|2010<br>5 a|rcmin global grid|Livestock populations.|



**Table 1.** Global datasets used in the construction of the crop residue usage dataset.


relative to this uniform baseline [32][–][34] (although some models do have inbuilt ways of estimating crop residue
return [35][–][37] ). Incorporating our dataset into regional and global modelling will thus lead to better identification
of areas that are hotspots for environmentally harmful losses (e.g. of greenhouse gases) and of areas that would
see the greatest benefits from changes in residue management. Second, the dataset can be used to evaluate the
trade-offs between different crop residue management options in a spatially explicit way. For example, it can
be used to assess the trade-off between soil carbon sequestration, energy generation from biofuel production,
and feeding livestock. Currently these trade-offs are either not considered [34][,][36] or only considered at country [15],
regional [38] or global scale [39] .


**Methods**
The general strategy employed was to (1) determine crop residue production (2) estimate the quantity of crop
residues removed from the field via burning, for animal feed/bedding and other off-field uses and (3) assume
the remainder are left on the field after harvest (see Fig. 2). Since multiple methods have been proposed in the
literature for determining residue production, biomass burning and livestock feed requirements, we determined
a mean value of each of these quantities. This involved averaging three different methods for determining crop
residue production, two different datasets for agricultural biomass burning and three different methods for
estimating the quantity of crop residues fed to livestock. The same calculational scheme was also used to explore
the 18 possible combinations of input data. This resulted in an ensemble of results that allowed us to define a
measure of uncertainty (see Fig. 1e,f).


**Cereal residue production.** Crop residue production is typically estimated from grain production via harvest indices, which measure the ratio of residue to grain production [1][,][15][,][38][–][41] . Grain production data was taken
from the SPAM dataset, which provides gridded, crop-specific production and harvested areas at 5 arcminute resolution [42][,][43] . This was aggregated to 0.5° resolution and then scaled to match FAO data for yearly, country-specific


Scientific **Data** | _(2023) 10:685_ [| https://doi.org/10.1038/s41597-023-02587-0](https://doi.org/10.1038/s41597-023-02587-0) 3


www.nature.com/scientificdata/ www.nature.com/scientificdata

|Col1|a (−)|b (ha/Mg)|c (−)|d (ha/Mg)|
|---|---|---|---|---|
|Barley|1.822|0.149|2.77|0.27|
|Maize|2.656|0.103|2.2|0.13|
|Rice|2.45|0.084|2.56|0.22|
|Wheat|2.183|0.127|1.96|0.14|
|Millet|1.9|0.250|4.38|0.95|
|Sorghum|2.302|0.100|4.55|0.55|
|Other cereals|1.9|0.250|2.7|0.2|



**Table 2.** Parameters used to convert grain yields to residue yields.


grain production and harvested areas [9] (a similar approach was for example used in _Grogan et al_ . [44] ). The result was
a gridded time series for the target period of 1997–2021.
In order to convert grain production to crop residue production, we considered three different methods. (1)
_Residue production ratios -_ a set of fixed ratios was used to convert grain production to crop residue production.
These ratios are crop and region specific, but constant over time [17] . (2) _Exponential yield dependence_                 - grain yields
were converted to crop residue yields using the empirical formula [1],



_bY_



≤





 _aYe_ − _for Y_ ≤ 1/ _b_

_R_ =  _a_

 _be_ 1 _for Y_       - 1/ _b_



1/


1/



=












1



where _R_ is the crop residue yield (Mg/ha), _Y_ is the grain yield (Mg/ha) and _a_ and _b_ are crop specific parameters
determined by fitting measurement data and shown in Table 2 [1][,][40] . Using a yield-dependent function accounts for
variation in the residue production ratio over time, for example due to increasing grain yields. (3) _Linear yield_
_dependence_               - grain yields were converted to crop residue yields using the empirical formula,


_R_ = _Y c_ ( − _dY_ )


where _c_ and _d_ 2 [40] .
are crop specific parameters determined by fitting measurement data and shown in Table
Finally, crop-specific values for residue production were combined to give total cereal-residue production.


**On-field burning.** We considered two data sources for the on-field burning of agricultural biomass: (1) The
Global Fire Emissions Database (GFED4s) provides monthly estimates of total agricultural biomass burning at
a 0.25° resolution for the period 1997–2021. This is based on a combination of satellite observations and biogeochemical modelling [45][,][46] ; (2) The Fire Inventory from NCAR (FINNv2.5) provides a global list of fires with
associated location, date, vegetation-type and total biomass burned for the period 2002–2021 [47][,][48] . In both cases
we aggregated the data to determine the total yearly burning of agricultural biomass on a 0.5° global grid. While
cereal residues form the dominant type of agricultural residues burnt on a global scale (approximately 96% [9] ),
other residues can be locally important, especially sugar cane. For example, in Brazil sugar cane accounts for 24%
of burnt agricultural biomass [9] . This is partially accounted for by limiting the total biomass burning in each grid
cell to be a maximum of 90% of the cereal residue production (see validation section for additional discussion).


**Ruminant feed.** Cereal residues are an important feed for ruminants, especially cattle, sheep and goats, but
are unpalatable to monogastric animals such as pigs and chickens. As such, there is a clear divide, with most of
the residues fed to ruminants derived from cereals, while other important residue classes, such as those from
sugarcane and legumes, are predominantly fed to monogastrics [17][,][49] .
In order to calculate crop residue usage for ruminant feed, country specific data for meat and milk production from cattle, sheep and goats for the period 1997–2021 was obtained from FAOSTAT [9] . The production
was then apportioned to grid cells based on the Gridded Livestock of the World (GLW 3) dataset, which gives
estimates of animal numbers (including cattle, sheep and goats) for the year 2010 [50][–][53], resulting in a gridded
production time series for 1997–2021. Meat and milk production numbers in each grid cell were transformed
into crop residue usage via feed conversion ratios (FCRs) and crop residue feed fractions (CRFFs). FCRs give the
quantity of feed (kg-dry-matter) required to produce a given quantity of meat or milk protein at the herd level
(i.e. they take into account the need to also feed unproductive animals, such as juveniles). CRFFs give the typical
fraction by weight that crop residues make up in an animal’s diet. Regional averages for FCRs and CRFFs have
been tabulated in the literature and we use three different sources: (1) _Herrero et al_ . [2] provide FCRs and CRFFs
for 10 world regions, and further divide these by animal type (cattle or small ruminant), production type (meat
or milk), livestock production system (grazing, mixed, urban or other) and climate (arid, temperate or tropical);
(2) _Mekonnen and Hoekstra_ [54] give FCRs for 10 world regions divided by animal type (cattle or small ruminant),
production system (grazing, mixed and industrial) and production type (meat or milk, only cattle); (3) _Mottet_
_et al_ . [3] provides FCRs and CRFFs for two world regions (OECD and non-OECD), divided by production system
(grazing, mixed or feedlot). Since _Mekonnen and Hoekstra_ don’t give CRFFs, we combine their FCRs with the
CRFFs of _Herrero et al_ . The dominant livestock production system in each 0.5° grid cell is determined from the
Global Distribution of Ruminant Livestock Production Systems (GRPS 5) dataset, which documents livestock
production systems on a scale of 5 arcminutes, including climate information (arid, temperate or tropical) [55] .


Scientific **Data** | _(2023) 10:685_ [| https://doi.org/10.1038/s41597-023-02587-0](https://doi.org/10.1038/s41597-023-02587-0) 4


www.nature.com/scientificdata/ www.nature.com/scientificdata


Where necessary, the protein content of meat and milk was calculated using 138 g-protein/kg for bovine meat,
137 g-protein/kg for sheep and goat meat and 33 g-protein/kg for milk [2] . The outcome of these calculations was
three distinct estimates for crop residue usage by animals. These numbers were further modified by crop residue
availability (see below).


**Animal bedding and horse feed.** On a global scale, data concerning the use of crop residues for animal
bedding is scarce. However, it can form a significant fraction of livestock crop residue usage in richer countries,
where residues typically don’t form an important part of ruminant diets [2][,][3][,][54] . Here we use estimated bedding
requirements for the EU [15], and apply these on a global scale. Our assumption is that these numbers are reasonable
for richer countries, where bedding makes up a higher proportion of livestock residue usage. Taking into account
seasonal differences and differences between production systems, we consider a bedding usage of 0.375 kg/day for
cattle, 0.1 kg/day for sheep and goats, 1.5 kg/day for horses and 0.0625 kg/day for pigs [15] . These daily requirements
are converted to gridded yearly requirements using the GLW 3 dataset for animal populations [50][–][53][,][56][,][57] . For horses
we additionally include 420 kg-fresh-matter/year of straw usage for chewing [58] . Crop residue usage for poultry
bedding is not considered, since industrial farms typically use other materials, such as sawdust [59] .


**Trading of crop residues.** For some grid cells, the estimate of animal residue usage exceeds residue availability. This is unsurprising, since it is known that crop residues are traded for use as animal feed/bedding. For
example, in the UK crop residue demand in the livestock-dominated west, is partially met by importing cereal
residues from the arable-dominated east [60] . In order to reduce the mismatch between supply and demand, we allow
for trade from over- to under-supplied grid cells. We consider a grid cell to be in deficit if the combined on-field
burning and animal usage exceed 90% of crop residue production. Deficit grid cells are allowed to import surplus
production from nearby grid cells, favouring local supply, but with a maximum distance of 20 grid cells (approximately 1000 km at the equator). The total global deficit before taking trade into account is 270–510 Tg/yr (i.e. the
sum of residue deficits across all grid cells in which a deficit exists). After the trade correction this is reduced to
60–100 Tg/yr. Finally, remaining deficits are assumed to arise from a local overestimation of animal usage and are
set to zero, meaning that the combination of on-field burning and animal usage never exceeds 90% of production.


**Other off field uses.** In poorer countries, a significant fraction of crop residues may be burnt for domestic
fuel [4] . The extent of burning largely depends on the availability of other fuels, such as wood, and on competition
with the demand for animal feed. In large parts of Africa and South Asia, the high demand for animal feed leaves
little available for other off-field uses (see Fig. 1b). However, in China, where livestock production is dominated
by monogastrics [9] and forest cover is low by global standards [9], crop residues have been historically important as a
domestic fuel. In the mid-1990s, when China’s GDP was only marginally above the threshold that the World Bank
considers to be low income, _Sinton et al_ . [4] report that approximately 4 EJ of energy was generated by domestic
burning of crop residues. Assuming that 18 MJ/kg of energy is released [1], and that approximately 730 Tg/yr of
residues were produced in China at that time, results in 30% of crop residues being used for domestic fuel. We
take the figure of 30% as an upper bound for crop residue usage for other off-field purposes in poorer countries
(also including construction materials, mushroom cultivation etc.), with the proviso that outside of China a lack
of availability means that this boundary is rarely reached (see Fig. 1c and also Supplementary Note 1 for a comparison of the dataset to the results of site-scale farmer surveys in Africa and South Asia). When applying this
upper boundary we follow the World Bank in defining poor countries as those with GDP per capita of less than
$1046 in 2015 prices.
For rich countries, other off-field uses include usage for industry, construction, the cultivation of mushrooms
and strawberries, energy generation via biogas reactors and losses during transport and storage [18] . In Germany it
is estimated that these other uses account for approximately 4% of crop residue production (excluding losses) [58],
while in Denmark, which has an exceptionally large biogas generating capacity, they account for 23% [61] . We
assume that approximately 10% of crop residues are used for other off field purposes in rich countries, which are
defined as those with GDP per capita greater than $12735 at 2015 prices.
For each grid cell, the fraction of other off-field uses is determined by the GDP per capita of the corresponding country, along with crop residue availability. For middle income countries the maximum usage is determined by linearly interpolating between the poor country (30%) and rich country (10%) values according to
GDP per capita. Changes in GDP per capita over time thus result in a changing upper bound for other off-field
crop residue usage. Residue removal via a combination of on-field burning, animal usage and other usage is
capped at 90% of production.


**Crop residues left on field.** Crop residues not assigned another usage are assumed to be left on the field.
Due to the constraints above, at least 10% of residues are left on the field, and this is imposed due to the difficulty of fully removing residues. In addition, we impose a maximum fraction of crop residues left on the field
in a limited number of countries and regions, assigning any excess to other off-field uses. The aim is to further
improve the balance between on-field and off-field uses of crop residues, compensating for the lack of global
data about crop residue use for domestic fuel, industry, construction, biofuels etc. In China we impose a limit of
60% of residues returned to the field in every grid cell. This results in a good match to literature values, where it
was reported that 46% (2009) [62] and 52% (2019) [63] of residues were returned to the field. Using the 60% limit our
dataset estimates 47% (2009) and 51% (2019), while in the absence of such a limit the figures are 51% (2009) and
60% (2019) (see also Supplementary Note 2). In Europe, it has been estimated that 40–70% of crop residues need
to be returned to the field to maintain soil organic carbon and avoid erosion [15] . We thus assume that it is rare for
more than 70% of residues to be returned to the field, since this is not necessary for agricultural reasons, and
selling excess straw is a way to supplement farm income. In North America and Oceania we impose a higher limit


Scientific **Data** | _(2023) 10:685_ [| https://doi.org/10.1038/s41597-023-02587-0](https://doi.org/10.1038/s41597-023-02587-0) 5


www.nature.com/scientificdata/ www.nature.com/scientificdata


of 80%, since the often semi-arid conditions require a higher percentage of residues to be returned to the field to
guard against erosion [64] . For Australia we find good agreement between the estimate of our dataset (74% returned
to the field in 2012) and the Australian Bureau of Statistics (76% in 2012) [65] . On a global scale, the imposition of
maximum return rates results in 3% of production being shifted from on-field to off-field usage.


**Data Records**
[The datasets are stored as netCDF files in the RADAR4KIT repository and can be accessed at https://doi.](https://doi.org/10.35097/989)
[org/10.35097/989](https://doi.org/10.35097/989) [66] . The spatial resolution is a 0.5° global grid and the temporal resolution is annual for the
years 1997–2021.


**Main dataset.** Values obtained with mean input values are intended as the default dataset. The filename is:
crop_residue_usage_mean.nc


**Additional datasets.** There are 18 additional datasets, corresponding to all possible method combinations
(see Methods section above) [66] . The naming convention is:


crop_residue_usage_{ _residue_production_ratio_ }_{ _livestock_source_ }_{ _fire_dataset_ }.nc
where:
{ _residue_production_ratio_ } = constant, exponential, linear
{ _livestock_source_ } = herrero, mottet, mekonnen
{ _fire_dataset_ } = GFED4s, FINN


Each dataset has 5 layers and all units are Mg/year:


1. _residue_production_ :- crop residue production from cereals
2. _burnt_residues_ :- residues burnt on the field
3. _animal_usage_ :- residues used for livestock feed and bedding
4. _other_usage_ :- residues used for other off-field purposes (domestic fuel, construction…)
5.
_left_on_field_ :- residues left on the field


For each grid cell and year the residue production (1) is equal to the sum of (2), (3), (4) and (5), meaning that
all residues are assigned a use. Fractional residue usage is simply calculated by dividing the specific residue usage
by the residue production.


**Technical Validation**
In order to validate our dataset, we have collected literature values for cereal residue production and fractional
residue usage. We only considered studies that (1) fall within the period 1997–2021, (2) report at a country level
or higher and (3) include all major cereals grown within the country/region.
For crop residue production there is close agreement between our estimate and literature values. On a global
scale _Smil et al_ . [67] estimated 2500 Tg of cereal residue production in 1997, _Lal et al_ . [13] 2800 Tg in 2001 and _Shinde_
_et al_ . [18] 3860 Tg in 2020. These values can be compared with our estimates of 2930, 2930 and 3900 Tg in the
respective years. At the country and regional scale, Fig. 3a shows a comparison between this study and literature [11][,][13][,][15][,][38][,][40][,][41][,][60][–][63][,][68][–][75] = 0.96.
. Linear regression analysis gives a coefficient of best fit of 0.98 with r [2]
Data concerning fractional crop-residue usage is even sparser than that for crop-residue production. A linear
regression analysis comparing our study with literature values [9][,][11][,][40][,][60][–][63][,][65][,][68][–][71][,][73][,][75][–][80] results in a coefficient of
best fit of 1.05 and r [2] = 0.70 (see Fig. 3b), suggesting good agreement.
One point that stands out in Fig. 3b is that burnt fractions are typically higher in the literature than in our
study. For example, on a global scale the FAO estimates that 10–11% of rice, wheat and maize residues are burnt [9],
while we find 5–8%. Literature estimates for China range from 9% [9] to 27% [68] and for India from 9% [9] to 20% [79] .
This can be compared to our estimates, derived from satellite data, of 2–5% in China and 5–7% in India. It is not
clear whether this discrepancy results from satellite data not capturing all fires or from methodological problems
with other approaches, such as farmer surveys [78] .


**Data gaps.** There is significant scope to further improve our estimates of crop residue usage via improvements in the input data. Here we discuss which improvements would have the highest priority.


_Crop residue production._ Estimates of crop residue production fit well with the literature (see Fig. 3), but could
be further improved by better spatial and temporal resolution (harvest indices) or fitting empirical functions
to larger measurement datasets (exponential and linear approaches). However, this is not a high priority for
improving our crop residue dataset.


_Animal usage._ Improving the spatial and temporal resolution of residue feed fractions and feed conversion
ratios is the most obvious way to improve estimates of crop residue use for livestock feed. Since this is a significant use of crop residues, especially in poorer countries, this would better constrain what fraction of crop
residues are left for all other uses.


_Burning._ As discussed above, literature values for agricultural biomass burning vary significantly between
those derived from satellite data and those from other sources (which themselves have significant variation).
Finding a way to improve the consistency of these estimates would be a priority.


Scientific **Data** | _(2023) 10:685_ [| https://doi.org/10.1038/s41597-023-02587-0](https://doi.org/10.1038/s41597-023-02587-0) 6


www.nature.com/scientificdata/ www.nature.com/scientificdata


**Fig. 3** Comparison to literature values for residue production and fractional residue usage. ( **a** ) Cereal residue
production at country and regional level (see Supplementary Table 1). The solid line is a linear regression fit
(r [2] = 0.96) and the dashed line a 1:1 line. ( **b** ) Fractional usage of cereal residues at country and regional level (see
Supplementary Table 2). The point colour shows the usage type, the solid line is a linear regression fit (r [2] = 0.70)
and the dashed line a 1:1 line.


_Other off field uses._ There is a lack of global data for crop residue usage for domestic fuel, construction, biofuels
etc. The existence of such a dataset would significantly improve our estimates of crop residue management.


_Left on field._ The fraction of residues left on the field also lacks global data. However, even in the absence of
such a dataset, improvements in data for off-field usage would allow on-field usage to be better constrained, and
would remove the need for imposing minimum and maximum limits.


**Code availability**
[The codes used to generate the dataset are available at https://zenodo.org/record/7843730#.ZEIxAC0Rq3I](https://zenodo.org/record/7843730#.ZEIxAC0Rq3I) [81] .


Received: 21 April 2023; Accepted: 21 September 2023;
Published: xx xx xxxx


**References**
1. Bentsen, N. S., Felby, C. & Thorsen, B. J. Agricultural residue production and potentials for energy and materials services. _Prog._
_Energy Combust. Sci._ **40**, 59–73 (2014).
2. Herrero, M. _et al_ . Biomass use, production, feed efficiencies, and greenhouse gas emissions from global livestock systems. _Proc. Natl._
_Acad. Sci._ **110**, 20888–20893 (2013).
3. Mottet, A. _et al_ . Livestock: On our plates or eating at our table? A new analysis of the feed/food debate. _Glob. Food Secur._ **14**, 1–8
(2017).
4. Sinton, J. E. & Fridley, D. G. What goes up: recent trends in China’s energy consumption. _Energy Policy_ **28**, 671–687 (2000).
5. Powlson, D. S., Glendining, M. J., Coleman, K. & Whitmore, A. P. Implications for Soil Properties of Removing Cereal Straw: Results
from Long-Term Studies1. _Agron. J._ **103**, 279–287 (2011).
6. Liu, C., Lu, M., Cui, J., Li, B. & Fang, C. Effects of straw carbon input on carbon dynamics in agricultural soils: a meta-analysis. _Glob._
_Change Biol._ **20**, 1366–1381 (2014).
7. Janzen, H. H. Beyond carbon sequestration: soil as conduit of solar energy. _Eur. J. Soil Sci._ **66**, 19–32 (2015).
8. Lal, R. Soil health and carbon management. _Food Energy Secur._ **5**, 212–222 (2016).
9. FAO. FAOSTAT. Rome: Food and Agriculture Organization of the United Nations. (2023).
10. Marlier, M. E. _et al_ . El Niño and health risks from landscape fire emissions in southeast Asia. _Nat. Clim. Change_ **3**, 131–136 (2013).
11. Li, J., Bo, Y. & Xie, S. Estimating emissions from crop residue open burning in China based on statistics and MODIS fire products. _J._
_Environ. Sci._ **44**, 158–170 (2016).
12. Lin, M. & Begho, T. Crop residue burning in South Asia: A review of the scale, effect, and solutions with a focus on reducing reactive
nitrogen losses. _J. Environ. Manage._ **314**, 115104 (2022).
13. Lal, R. World crop residues production and implications of its use as a biofuel. _Environ. Int._ **31**, 575–584 (2005).
14. Hakala, K., Kontturi, M. & Pahkala, K. Field biomass as global energy source. _Agric. Food Sci._ **18**, 347–365 (2009).
15. Scarlat, N., Martinov, M. & Dallemand, J.-F. Assessment of the availability of agricultural crop residues in the European Union:
Potential and limitations for bioenergy use. _Waste Manag._ **30**, 1889–1897 (2010).
16. Minasny, B. _et al_ . Soil carbon 4 per mille. _Geoderma_ **292**, 59–86 (2017).
17. Sandström, V. _et al_ . Food system by-products upcycled in livestock and aquaculture feeds can increase global food supply. _Nat. Food_
**3**, 729–740 (2022).
18. Shinde, R. _et al_ . Management of crop residues with special reference to the on-farm utilization methods: A review. _Ind. Crops Prod._
**181**, 114772 (2022).


Scientific **Data** | _(2023) 10:685_ [| https://doi.org/10.1038/s41597-023-02587-0](https://doi.org/10.1038/s41597-023-02587-0) 7


www.nature.com/scientificdata/ www.nature.com/scientificdata


19. Wirsenius, S. Human Use of Land and Organic materials: Modeling the Turnover of Biomass in the Global Food System. (Chalmers
University of Technology and Göteborg University, 2000).
20. Searcy, E., Flynn, P., Ghafoori, E. & Kumar, A. The relative cost of biomass energy transport. _Appl. Biochem. Biotechnol._ **137**, 639–652
(2007).
21. Abdalla, M. _et al_ . Conservation tillage systems: a review of its consequences for greenhouse gas emissions. _Soil Use Manag._ **29**,
199–209 (2013).
22. Charles, A. _et al_ . Global nitrous oxide emission factors from agricultural soils after addition of organic amendments: A metaanalysis. _Agric. Ecosyst. Environ._ **236**, 88–98 (2017).
23. Xia, L. _et al_ . Trade-offs between soil carbon sequestration and reactive nitrogen losses under straw return in global agroecosystems.
_Glob. Change Biol._ **24**, 5919–5932 (2018).
24. Lugato, E., Leip, A. & Jones, A. Mitigation potential of soil carbon management overestimated by neglecting N2O emissions. _Nat._
_Clim. Change_ **8**, 219–223 (2018).
25. Guenet, B. _et al_ . Can N2O emissions offset the benefits from soil organic carbon storage? _Glob. Change Biol._ **27**, 237–256 (2021).
26. van der Gon, H. A. C. D. & Neue, H. U. Influence of organic matter incorporation on the methane emission from a wetland rice field.
_Glob. Biogeochem. Cycles_ **9**, 11–22 (1995).
27. Cheng, Y., Wang, J., Wang, J., Chang, S. X. & Wang, S. The quality and quantity of exogenous organic carbon input control microbial
NO3− immobilization: A meta-analysis. _Soil Biol. Biochem._ **115**, 357–363 (2017).
28. Grosso, S. J. D. _et al_ . Global scale DAYCENT model analysis of greenhouse gas emissions and mitigation strategies for cropped soils.
_Glob. Planet. Change_ **67**, 44–50 (2009).
29. Pugh, T. A. M. _et al_ . Simulated carbon emissions from land-use change are substantially enhanced by accounting for agricultural
management. _Environ. Res. Lett._ **10**, 124008 (2015).
30. Jägermeyr, J. _et al_ . Climate impacts on global agriculture emerge earlier in new generation of climate and crop models. _Nat. Food_ **2**,
873–885 (2021).
31. Smerald, A., Fuchs, K., Kraus, D., Butterbach-Bahl, K. & Scheer, C. Significant Global Yield-Gap Closing Is Possible Without
Increasing the Intensity of Environmentally Harmful Nitrogen Losses. _Front. Sustain. Food Syst_ . **6** (2022).
32. Wang, G., Zhang, W., Sun, W., Li, T. & Han, P. Modeling soil organic carbon dynamics and their driving factors in the main global
cereal cropping systems. _Atmospheric Chem. Phys._ **17**, 11849–11859 (2017).
33. Morais, T. G., Teixeira, R. F. M. & Domingos, T. Detailed global modelling of soil organic carbon in cropland, grassland and forest
soils. _PLOS ONE_ **14**, 1–27 (2019).
34. Haas, E., Carozzi, M., Massad, R. S., Butterbach-Bahl, K. & Scheer, C. Long term impact of residue management on soil organic
carbon stocks and nitrous oxide emissions from European croplands. _Sci. Total Environ._ **836**, 154932 (2022).
35. Bodirsky, B. L. _et al_ . N 2 O emissions from the global agricultural nitrogen cycle – current state and future scenarios. _Biogeosciences_ **9**,
4169–4197 (2012).
36. Herzfeld, T., Heinke, J., Rolinski, S. & Müller, C. Soil organic carbon dynamics from agricultural management practices under
climate change. _Earth Syst. Dyn._ **12**, 1037–1055 (2021).
37. Karstens, K. _et al_ . Management-induced changes in soil organic carbon on global croplands. _Biogeosciences_ **19**, 5125–5149 (2022).
38. Krausmann, F., Erb, K.-H., Gingrich, S., Lauk, C. & Haberl, H. Global patterns of socioeconomic biomass flows in the year 2000: A
comprehensive assessment of supply, consumption and constraints. _Ecol. Econ._ **65**, 471–487 (2008).
39. Wirsenius, S. The biomass metabolism of the food system: A model-based survey of the global and regional turnover of food
biomass. _J. Ind. Ecol._ **7**, 47–80 (2003).
40. Ronzon, T. & Piotrowski, S. Are primary agricultural residues promising feedstock for the European bioeconomy? _Industrial_
_Biotechnology_ **13**, 113–127 (2017).
41. García-Condado, S. _et al_ . Assessing lignocellulosic biomass production from crop residues in the European Union: Modelling,
analysis of the current scenario and drivers of interannual variability. _GCB Bioenergy_ **11**, 809–831 (2019).
42. Yu, Q. _et al_ . A cultivated planet in 2010 – Part 2: The global gridded agricultural-production maps. _Earth Syst. Sci. Data_ **12**,
3545–3572 (2020).
43. Institute, I. F. P. R. Global spatially-disaggregated crop production statistics data for 2010 version 2.0. _Harvard Dataverse,_ [https://doi.](https://doi.org/10.7910/DVN/PRFF8V)
[org/10.7910/DVN/PRFF8V (2019).](https://doi.org/10.7910/DVN/PRFF8V)
44. Grogan, D., Frolking, S., Wisser, D., Prusevich, A. & Glidden, S. Global gridded crop harvested area, production, yield, and monthly
physical area data circa 2015. _Sci. Data_ **9**, 15 (2022).
45. van der Werf, G. R. _et al_ . Global fire emissions estimates during 1997–2016. _Earth Syst. Sci. Data_ **9**, 697–720 (2017).
46. Randerson, J. T., Van der Werf, G. R., Giglio, L., Collatz, G. J. & Kasibhatla, P. S. Global fire emissions database, version 4.1
(GFEDv4). _ORNL DAAC,_ [https://doi.org/10.3334/ORNLDAAC/1293 (2017).](https://doi.org/10.3334/ORNLDAAC/1293)
47. Wiedinmyer, C. _et al_ . The Fire Inventory from NCAR version 2.5: an updated global fire emissions model for climate and chemistry
applications. _EGUsphere_ **2023**, 1–45 (2023).
48. Wiedinmyer, C. & Emmons, L. Fire inventory from NCAR version 2 fire emission. (2022).
49. FAO. _Global livestock assessment model version 3_ [. https://www.fao.org/gleam/en/ (2017).](https://www.fao.org/gleam/en/)
50. Gilbert, M. _et al_ . Global distribution data for cattle, buffaloes, horses, sheep, goats, pigs, chickens and ducks in 2010. _Sci. Data_ **5**,
180227 (2018).
51. Gilbert, M. _et al_ . Global cattle distribution in 2010 (5 minutes of arc)., _Harvard Dataverse_ [, https://doi.org/10.7910/DVN/GIVQ75](https://doi.org/10.7910/DVN/GIVQ75)
(2018).
52. Gilbert, M. _et al_ . Global sheep distribution in 2010 (5 minutes of arc)., _Harvard Dataverse_ [, https://doi.org/10.7910/DVN/BLWPZN](https://doi.org/10.7910/DVN/BLWPZN)
(2018).
53. Gilbert, M. _et al_ . Global goats distribution in 2010 (5 minutes of arc)., _Harvard Dataverse_ [, https://doi.org/10.7910/DVN/OCPH42](https://doi.org/10.7910/DVN/OCPH42)
(2018).
54. Mekonnen, M. M. & Hoekstra, A. Y. A Global Assessment of the Water Footprint of Farm Animal Products. _Ecosystems_ **15**, 401–415
(2012).
55. Robinson, T. P. _et al_ . Global distribution of ruminant livestock production systems V5 (5 minutes of arc). _Harvard Dataverse,_ [https://](https://doi.org/10.7910/DVN/WPDSZE)
[doi.org/10.7910/DVN/WPDSZE (2018).](https://doi.org/10.7910/DVN/WPDSZE)
56. Gilbert, M. _et al_ . Global horses distribution in 2010 (5 minutes of arc)., _Harvard Dataverse_ [, https://doi.org/10.7910/DVN/7Q52MV](https://doi.org/10.7910/DVN/7Q52MV)
(2018).
57. Gilbert, M. _et al_ . Global pigs distribution in 2010 (5 minutes of arc)., _Harvard Dataverse_ [, https://doi.org/10.7910/DVN/33N0JG (2018).](https://doi.org/10.7910/DVN/33N0JG)
58. Brosowski, A., Bill, R. & Thrän, D. Temporal and spatial availability of cereal straw in Germany—Case study: Biomethane for the
transport sector. _Energy Sustain. Soc._ **10**, 42 (2020).
59. Diarra, S., Lameta, S., Amosa, F. & Anand, S. Alternative Bedding Materials for Poultry: Availability, Efficacy, and Major Constraints.
_Front. Vet. Sci_ . **8** (2021).
60. Copeland, J. & Turley, D. _National and regional supply/demand balance for agricultural straw in Great Britain_ . (2008).
61. IEAbioenergy. _Mobilisation of agricultural residues for bioenergy and higher value bio-products: Resources, barriers and sustainability_ .

[https://www.ieabioenergy.com/wp-content/uploads/2018/01/TR2017-01-F.pdf (2017).](https://www.ieabioenergy.com/wp-content/uploads/2018/01/TR2017-01-F.pdf)
62. Jiang, D., Zhuang, D., Fu, J., Huang, Y. & Wen, K. Bioenergy potential from crop residues in China: Availability and distribution.
_Renew. Sustain. Energy Rev._ **16**, 1377–1382 (2012).


Scientific **Data** | _(2023) 10:685_ [| https://doi.org/10.1038/s41597-023-02587-0](https://doi.org/10.1038/s41597-023-02587-0) 8


www.nature.com/scientificdata/ www.nature.com/scientificdata


63. Xinxin, L., Zuliang, S., Jiuchen, W. & Rongfeng, J. Review on the Crop Straw Utilization Technology of China. _Am. J. Environ. Sci._
_Eng._ **4**, 61–64 (2020).
[64. Andrews, S. Crop residue removal for biomass energy production: Effects on soils and recommendations. https://www.nrcs.usda.](https://www.nrcs.usda.gov/sites/default/files/2022-10/Crop_Residue_Removal_for_Biomass_Energy_Production.pdf)
[gov/sites/default/files/2022-10/Crop_Residue_Removal_for_Biomass_Energy_Production.pdf (2006).](https://www.nrcs.usda.gov/sites/default/files/2022-10/Crop_Residue_Removal_for_Biomass_Energy_Production.pdf)
65. Land Management and Farming in Australia _, 2011-12_ [. https://www.abs.gov.au/ausstats/abs@.nsf/Lookup/4627.0main+](https://www.abs.gov.au/ausstats/abs@.nsf/Lookup/4627.0main+features62011-12)
[features62011-12.](https://www.abs.gov.au/ausstats/abs@.nsf/Lookup/4627.0main+features62011-12)
66. Smerald, A., Rahimi, J. & Scheer, C. Global crop residue management dataset (1997–2021). _RADAR4KIT_ [, https://doi.](https://doi.org/10.35097/989)
[org/10.35097/989. (2023)](https://doi.org/10.35097/989)
67. Smil, V. Nitrogen in crop production: An account of global flows. _Glob. Biogeochem. Cycles_ **13**, 647–662 (1999).
68. Zhang, G. _et al_ . Residue usage and farmers’ recognition and attitude toward residue retention in China’s croplands. _J. Agro-Environ._
_Sci._ **36**, 981–988 (2017).
69. Cao, G., Zhang, X. & Zheng, F. Inventory of black carbon and organic carbon emissions from China. _Atmos. Environ._ **40**, 6516–6527
(2006).
70. Ravindranath, N. H. _et al_ . Assessment of sustainable non-plantation biomass resources potential for energy in India. _Biomass_
_Bioenergy_ **29**, 178–190 (2005).
71. Weiser, C. _et al_ . Integrated assessment of sustainable cereal straw potential and different straw-based energy applications in
Germany. _Appl. Energy_ **114**, 749–762 (2014).
72. Cherubin, M. R. _et al_ . Crop residue harvest for bioenergy production and its implications on soil functioning and plant growth: A
review. _Sci. Agric_ . **75** (2018).
73. Gouro, A. & Ly, C. _Crop residues and agro-industrial by-products in West Africa_ . (FAO Regional Office for Africa, 2014).
74. Ayodele, O. P. & Aluko, O. A. Weed Management Strategies for Conservation Agriculture and Environmental Sustainability in
Nigeria. _IOSR J. Agric. Vet. Sci. IOSR-JAVS_ **10**, 1 (2017).
75. Li, X. _et al_ . A review of agricultural crop residue supply in Canada for cellulosic ethanol production. _Renew. Sustain. Energy Rev._ **16**,
2954–2965 (2012).
76. Sharma, D. C. Residue Management- Challenges and Solutions: A New Paradigm in Agriculture. _Agric. Environ. E Newsl._ **1**, 103
(2020).
77. Huang, T. _et al_ . Health and environmental consequences of crop residue burning correlated with increasing crop yields midst India’s
Green Revolution. _Npj Clim. Atmospheric Sci._ **5**, 81 (2022).
78. Yan, X., Ohara, T. & Akimoto, H. Bottom-up estimate of biomass burning in mainland China. _Atmos. Environ._ **40**, 5262–5273
(2006).
79. Devi, S., Gupta, C., Jat, S. L. & Parmar, M. S. Crop residue recycling for economic and environmental sustainability: The case of
India. _Open Agric._ **2**, 486–494 (2017).
80. Townsend, T. J., Sparkes, D. L., Ramsden, S. J., Glithero, N. J. & Wilson, P. Wheat straw availability for bioenergy in England. _Energy_
_Policy_ **122**, 349–357 (2018).
81. Smerald, A., Rahimi, J. & Scheer, C. Global crop residue management (1997–2021). _Zenodo,_ [https://doi.org/10.5281/zenodo.7843730](https://doi.org/10.5281/zenodo.7843730)
(2023).


**Acknowledgements**
The authors acknowledge funding by the German Federal Ministry of Education and Research (BMBF) under the
Make our Planet Great Again—German Research Initiative, Grant Number 306060, implemented by the German
Academic Exchange Service (DAAD). We acknowledge support by the KIT-Publication Fund of the Karlsruhe
Institute of Technology.


**Author contributions**
The study was designed and carried out by Andrew Smerald with help from Jaber Rahimi. Andrew Smerald wrote
the first version of the manuscript, and all authors contributed to improving the text.


**Funding**
Open Access funding enabled and organized by Projekt DEAL.


**Competing interests**
The authors declare no competing interests.


**Additional information**
**Supplementary information** [The online version contains supplementary material available at https://doi.](https://doi.org/10.1038/s41597-023-02587-0)
[org/10.1038/s41597-023-02587-0.](https://doi.org/10.1038/s41597-023-02587-0)


**Correspondence** and requests for materials should be addressed to A.S.


**Reprints and permissions information** [is available at www.nature.com/reprints.](http://www.nature.com/reprints)


**Publisher’s note** Springer Nature remains neutral with regard to jurisdictional claims in published maps and
institutional affiliations.


**Open Access** This article is licensed under a Creative Commons Attribution 4.0 International
License, which permits use, sharing, adaptation, distribution and reproduction in any medium or
format, as long as you give appropriate credit to the original author(s) and the source, provide a link to the Creative Commons licence, and indicate if changes were made. The images or other third party material in this
article are included in the article’s Creative Commons licence, unless indicated otherwise in a credit line to the
material. If material is not included in the article’s Creative Commons licence and your intended use is not permitted by statutory regulation or exceeds the permitted use, you will need to obtain permission directly from the
[copyright holder. To view a copy of this licence, visit http://creativecommons.org/licenses/by/4.0/.](http://creativecommons.org/licenses/by/4.0/)

© The Author(s) 2023


Scientific **Data** | _(2023) 10:685_ [| https://doi.org/10.1038/s41597-023-02587-0](https://doi.org/10.1038/s41597-023-02587-0) 9


