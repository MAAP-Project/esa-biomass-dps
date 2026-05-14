FROM condaforge/mambaforge:latest

WORKDIR /app/esa-biomass-dps

COPY environment.yml .
RUN mamba env create -f environment.yml && mamba clean -afy

COPY esa-biomass-dps.py .
COPY run.sh .
COPY build.sh .

RUN chmod +x run.sh build.sh

SHELL ["conda", "run", "-n", "esa_biomass_dps", "/bin/bash", "-c"]

ENTRYPOINT ["conda", "run", "-n", "esa_biomass_dps", "/bin/bash", "/app/ESA_BIOMASS_DPS_JOB/run.sh"]
