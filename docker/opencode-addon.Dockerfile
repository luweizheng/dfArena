# Add OpenCode to an existing local sandbox without reinstalling dataframe libraries.
ARG BASE_IMAGE=pandaslift-agent:latest
FROM ${BASE_IMAGE}
ARG OPENCODE_VERSION=1.18.29
RUN npm install -g opencode-ai@${OPENCODE_VERSION}
