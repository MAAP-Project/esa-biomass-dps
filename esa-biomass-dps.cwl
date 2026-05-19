cwlVersion: v1.2

$namespaces:
  s: https://schema.org/
$schemas:
  - https://raw.githubusercontent.com/schemaorg/schemaorg/refs/heads/main/data/releases/9.0/schemaorg-current-http.rdf

s:author:
  - class: s:Organization
    s:name: MAAP
s:codeRepository: https://github.com/MAAP-Project/esa-biomass-dps
s:commitHash: 88aa9db196f812b752c43a884125ce6ee090a424
s:contributor:
  - class: s:Organization
    s:name: MAAP
s:dateCreated: 2026-05-19
s:keywords: [ESA, BIOMASS, STAC, COG]
s:releaseNotes: Initial CWL wrapper for the ESA BIOMASS DPS package.
s:softwareVersion: cleanup
s:version: cleanup

$graph:
  - class: Workflow
    id: esa-biomass-dps
    label: ESA BIOMASS DPS
    doc: |
      MAAP OGC Application Package that queries ESA BIOMASS Level 1B data
      within a user-defined bounding box and time range, retrieves GeoTIFF
      assets, loads the selected area through STAC/ODC, forward-fills the
      latest available time slice, and writes the result as a Cloud Optimized
      GeoTIFF (COG).

    inputs:
      bbox:
        label: Bounding box
        type: string
        doc: >-
          Comma-separated bounding box coordinates as min_x,min_y,max_x,max_y
          in the CRS supplied by `crs`.

      crs:
        label: CRS
        type: string
        doc: >-
          Coordinate reference system for the bounding box and output raster,
          for example `EPSG:4326`.

      datetime:
        label: Datetime range
        type: string
        doc: >-
          Datetime range for the ESA BIOMASS STAC query, formatted as an ISO
          8601 interval such as
          `2026-01-01T00:00:00Z/2026-01-31T23:59:59Z`.

      resolution:
        label: Output resolution
        type: double
        default: 0.01
        doc: >-
          Output resolution in CRS units.

    outputs:
      out:
        type: Directory
        outputSource: process/outputs_result

    steps:
      process:
        run: '#main'
        in:
          bbox: bbox
          crs: crs
          datetime: datetime
          resolution: resolution
        out:
          - outputs_result

  - class: CommandLineTool
    id: main

    requirements:
      DockerRequirement:
        dockerPull: esa-biomass-dps:latest
      NetworkAccess:
        networkAccess: true
      ResourceRequirement:
        ramMin: 8
        coresMin: 4
        outdirMax: 20

    baseCommand: /app/esa-biomass-dps/run.sh
    successCodes: [0]

    inputs:
      bbox:
        type: string
        inputBinding:
          position: 1
          prefix: --bbox
      crs:
        type: string
        inputBinding:
          position: 2
          prefix: --crs
      datetime:
        type: string
        inputBinding:
          position: 3
          prefix: --datetime
      resolution:
        type: double
        default: 0.01
        inputBinding:
          position: 4
          prefix: --resolution

    outputs:
      outputs_result:
        type: Directory
        outputBinding:
          glob: output
