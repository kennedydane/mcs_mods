# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository appears to be for Minecraft server mods or configurations, specifically for Bedrock Edition servers. The repository currently contains:

- A Bedrock server distribution zip file (bedrock-server-1.21.100.7.zip)
- A .gitignore configured to exclude bedrock-server-*.zip files

## Repository Structure

This is a minimal repository that serves as a storage/working area for Minecraft Bedrock server files. The .gitignore indicates that server zip files are typically excluded from version control, though one is currently present.

## Development Notes

- Server files are handled as zip archives
- The repository follows a pattern of ignoring bedrock-server-*.zip files in version control
- This appears to be a working directory for server setup/configuration rather than active code development

## Common Tasks

Since this repository doesn't contain traditional development artifacts (no package.json, Cargo.toml, or other build systems), typical development commands like build/test/lint are not applicable. Work here would likely involve:

- Extracting and configuring server files
- Managing server configurations and world files
- Handling mod installations and updates