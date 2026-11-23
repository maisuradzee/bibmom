#!/usr/bin/env python3
"""Reproduce the NOEMA-2026-003 three-product temperature comparison."""
from __future__ import annotations
import argparse, csv, hashlib, itertools, json, math
from pathlib import Path
from statistics import median

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_DATA=ROOT/"data/noema-003/snapshots/2026.10"
DEFAULT_METADATA=DEFAULT_DATA/"sources.json"
DEFAULT_OUTPUT=ROOT/"data/noema-003/cross-dataset-results-2026-11-23.json"
START_YEAR,END_YEAR=1979,2025
BASELINE_START,BASELINE_END=1991,2020
EXPECTED_ARCHIVE_COMMIT="74218762d2d1dda92047a234360fa1d870d0857f"
EXPECTED_RETRIEVED="2026-10-19T06:17:45Z"
PINNED_SOURCE_HASHES={
 "gistemp.csv":"4c64eda288bce32b8d76926278f346ecea1e53506df8ee72a3d5accb0657c416",
 "hadcrut5_annual.csv":"7f750b673bb34aad722736ee21f122b5ea692c99877fa0b1066df65e51f32c04",
 "noaaglobaltemp_annual.asc":"74539ba18ba28c7c4d68abb008db8e1a1d9ccce2f3de80fa57466b788b3e738c",
}

def rounded(value:float)->float:
 return round(float(value),10)

def validate_period(rows:list[tuple[int,float]],label:str)->list[tuple[int,float]]:
 years=[year for year,_ in rows]
 expected=list(range(START_YEAR,END_YEAR+1))
 if len(years)!=len(set(years)): raise ValueError(f"{label}: duplicate years in analysis period")
 if years!=expected: raise ValueError(f"{label}: expected contiguous years {START_YEAR}-{END_YEAR}; received {years[0] if years else 'none'}-{years[-1] if years else 'none'} with {len(years)} rows")
 if any(not math.isfinite(value) for _,value in rows): raise ValueError(f"{label}: non-finite anomaly")
 return rows

def parse_gistemp(path:Path)->list[tuple[int,float]]:
 with path.open("r",encoding="utf-8-sig",newline="") as handle: table=list(csv.reader(handle))
 header_index=next((i for i,row in enumerate(table) if row and row[0].strip()=="Year"),None)
 if header_index is None: raise ValueError("GISTEMP: annual table header 'Year' not found")
 header=[column.strip() for column in table[header_index]]
 if "J-D" not in header: raise ValueError("GISTEMP: required annual J-D column not found")
 yi,ai=header.index("Year"),header.index("J-D")
 rows=[]
 for row in table[header_index+1:]:
  if not row or not row[yi].strip(): continue
  year=int(row[yi])
  if START_YEAR<=year<=END_YEAR:
   raw=row[ai].strip()
   if raw=="***" or not raw: raise ValueError(f"GISTEMP: missing complete annual value for {year}")
   rows.append((year,float(raw)))
 return validate_period(rows,"GISTEMP")

def parse_hadcrut(path:Path)->list[tuple[int,float]]:
 rows=[]
 with path.open("r",encoding="utf-8-sig",newline="") as handle:
  reader=csv.DictReader(handle)
  if not reader.fieldnames or not {"Time","Anomaly (deg C)"}.issubset(reader.fieldnames): raise ValueError("HadCRUT5: unexpected annual summary-series columns")
  for row in reader:
   year=int(row["Time"])
   if START_YEAR<=year<=END_YEAR: rows.append((year,float(row["Anomaly (deg C)"])))
 return validate_period(rows,"HadCRUT5")

def parse_noaa(path:Path)->list[tuple[int,float]]:
 rows=[]
 for line_number,line in enumerate(path.read_text(encoding="utf-8").splitlines(),start=1):
  parts=line.split()
  if not parts: continue
  if len(parts)<2: raise ValueError(f"NOAA: malformed row {line_number}")
  year=int(parts[0])
  if START_YEAR<=year<=END_YEAR: rows.append((year,float(parts[1])))
 return validate_period(rows,"NOAAGlobalTemp")

def verify_sources(data_dir:Path,metadata_path:Path)->dict:
 metadata=json.loads(metadata_path.read_text(encoding="utf-8"))
 if metadata.get("archive_commit")!=EXPECTED_ARCHIVE_COMMIT: raise ValueError("Source manifest archive commit does not match pinned snapshot")
 if metadata.get("retrieved")!=EXPECTED_RETRIEVED: raise ValueError("Source manifest retrieval timestamp does not match pinned snapshot")
 if metadata.get("common_reference_period")!="1991-2020": raise ValueError("Unexpected common reference period in source manifest")
 for name,expected_hash in PINNED_SOURCE_HASHES.items():
  item=metadata.get("files",{}).get(name)
  if not isinstance(item,dict): raise ValueError(f"Source manifest missing entry for {name}")
  if item.get("source_sha256")!=expected_hash: raise ValueError(f"Source manifest SHA-256 changed for {name}")
  actual=hashlib.sha256((data_dir/name).read_bytes()).hexdigest()
  if actual!=expected_hash: raise ValueError(f"SHA-256 mismatch for {name}: expected {expected_hash}, received {actual}")
 return metadata

def ols(rows:list[tuple[int,float]])->tuple[float,float]:
 years=[float(year) for year,_ in rows]; values=[value for _,value in rows]
 xm=sum(years)/len(years); ym=sum(values)/len(values)
 sxx=sum((year-xm)**2 for year in years)
 if sxx==0: raise ValueError("OLS requires more than one distinct year")
 slope=sum((year-xm)*(value-ym) for year,value in zip(years,values))/sxx
 residuals=[value-(ym+slope*(year-xm)) for year,value in zip(years,values)]
 sse=sum(v*v for v in residuals); sst=sum((v-ym)**2 for v in values)
 return slope*10.0,(1.0-sse/sst if sst else 1.0)

def theil_sen(rows:list[tuple[int,float]])->float:
 slopes=[(rows[j][1]-rows[i][1])/(rows[j][0]-rows[i][0]) for i in range(len(rows)) for j in range(i+1,len(rows))]
 return median(slopes)*10.0

def product_summary(rows:list[tuple[int,float]])->dict:
 baseline=[v for year,v in rows if BASELINE_START<=year<=BASELINE_END]
 if len(baseline)!=BASELINE_END-BASELINE_START+1: raise ValueError("A complete 1991-2020 baseline is required")
 baseline_mean=sum(baseline)/len(baseline)
 rebased=[(year,value-baseline_mean) for year,value in rows]
 slope,r2=ols(rows)
 return {"n":len(rows),"baseline_mean_1991_2020":rounded(baseline_mean),"ols_slope_c_per_decade":rounded(slope),"theil_sen_slope_c_per_decade":rounded(theil_sen(rows)),"r_squared":rounded(r2),"rebased_anomaly_2025_c":rounded(rebased[-1][1]),"rebased_series":rebased}

def pearson(left:list[float],right:list[float])->float:
 lm=sum(left)/len(left); rm=sum(right)/len(right)
 num=sum((x-lm)*(y-rm) for x,y in zip(left,right))
 lss=sum((x-lm)**2 for x in left); rss=sum((y-rm)**2 for y in right)
 if lss<=0 or rss<=0: raise ValueError("Pearson correlation requires non-constant series")
 return num/math.sqrt(lss*rss)

def analyze(data_dir:Path=DEFAULT_DATA,metadata_path:Path=DEFAULT_METADATA)->dict:
 verify_sources(data_dir,metadata_path)
 rows={"NASA_GISTEMP":parse_gistemp(data_dir/"gistemp.csv"),"HadCRUT5_5_2_0_0":parse_hadcrut(data_dir/"hadcrut5_annual.csv"),"NOAAGlobalTemp_6_1_0":parse_noaa(data_dir/"noaaglobaltemp_annual.asc")}
 summaries={name:product_summary(series) for name,series in rows.items()}
 public={name:{k:v for k,v in item.items() if k!="rebased_series"} for name,item in summaries.items()}
 pairwise={}
 for a,b in itertools.combinations(summaries,2):
  left=[v for _,v in summaries[a]["rebased_series"]]; right=[v for _,v in summaries[b]["rebased_series"]]
  diffs=[x-y for x,y in zip(left,right)]
  pairwise[f"{a}_vs_{b}"]={"correlation":rounded(pearson(left,right)),"rmse":rounded(math.sqrt(sum(x*x for x in diffs)/len(diffs))),"mean_difference":rounded(sum(diffs)/len(diffs)),"max_absolute_difference":rounded(max(abs(x) for x in diffs)),"anomaly_2025":{a:rounded(left[-1]),b:rounded(right[-1])}}
 slopes=[x["ols_slope_c_per_decade"] for x in public.values()]; lo=min(slopes); hi=max(slopes)
 return {
  "study_id":"NOEMA-2026-003","addendum":"Cross-dataset replication",
  "snapshot":{"archive_repository":"climate-resource/bookshelf-global-surface-temperature","archive_commit":EXPECTED_ARCHIVE_COMMIT,"retrieved":EXPECTED_RETRIEVED,"analysis_period":"1979-2025","common_reference_period":"1991-2020"},
  "datasets":public,
  "cross_dataset_trend":{"minimum_ols_slope_c_per_decade":rounded(lo),"maximum_ols_slope_c_per_decade":rounded(hi),"spread_c_per_decade":rounded(hi-lo),"max_to_min_percent_difference":rounded((hi/lo-1.0)*100.0),"all_slopes_positive":all(x>0 for x in slopes)},
  "pairwise_rebased_series_comparison":pairwise,
  "method_notes":[
   "Each product is rebased by subtracting its own 1991-2020 arithmetic mean; slopes are invariant to this constant shift.",
   "NASA GISTEMP annual value is the J-D column of the global land-ocean table.",
   "HadCRUT5 value is the published global (NH+SH)/2 annual analysis summary-series anomaly, ensemble mean.",
   "NOAAGlobalTemp value is the second column of the annual global 90S-90N series.",
   "Partial 2026 values are excluded; all three series are compared over the same 47 calendar years.",
   "Products have different input datasets and methods, and may share some underlying observations; product comparison is not a statistical independence claim."
  ]
 }

def main()->None:
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument("--data-dir",type=Path,default=DEFAULT_DATA)
 parser.add_argument("--metadata",type=Path,default=DEFAULT_METADATA)
 parser.add_argument("--output",type=Path,default=DEFAULT_OUTPUT)
 args=parser.parse_args(); result=analyze(args.data_dir,args.metadata)
 args.output.parent.mkdir(parents=True,exist_ok=True)
 args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("NOEMA-003 cross-dataset comparison OK: "+", ".join(f"{n}={s['ols_slope_c_per_decade']:.4f} C/decade" for n,s in result["datasets"].items()))

if __name__=="__main__": main()
