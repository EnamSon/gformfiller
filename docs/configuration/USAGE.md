# Configuration Guide

## Overview

gformfiller uses a hierarchical configuration system with the following priority:
```
CLI Arguments > Environment Variables > Config File > Defaults
```

## Quick Start

### First Time Setup
```bash
# Initialize configuration
gformfiller config init

# Check configuration
gformfiller config show

# Validate configuration
gformfiller config validate
```

## Configuration Files

All configuration files are stored in `$HOME/.gformfiller/config/`.

### `constants.toml`

Main configuration file. Edit with:
```bash
gformfiller config edit --file constants
```

#### Timeouts
```toml
[timeouts]
page_load = 30          # Page load timeout (seconds)
element_wait = 10       # Element wait timeout (seconds)
ai_response = 60        # AI response timeout (seconds)
```

#### AI Settings
```toml
[ai]
default_provider = "gemini"    # Default AI provider
max_tokens = 2000              # Maximum response tokens
temperature = 0.7              # Response creativity (0.0-2.0)
```

## Environment Variables

Set API keys using environment variables:
```bash
export GEMINI_API_KEY="your_key_here"
export CLAUDE_API_KEY="your_key_here"
export OPENAI_API_KEY="your_key_here"
```

Override configuration:
```bash
export GFORMFILLER_TIMEOUTS_PAGE_LOAD=60
export GFORMFILLER_AI_DEFAULT_PROVIDER=claude
```

## CLI Overrides

Override any configuration via CLI:
```bash
gformfiller start \
  --browser chrome \
  --ai claude \
  --url "https://forms.google.com/..." \
  --timeout-page-load 60
```

## Management Commands

### View Configuration
```bash
# Show as table
gformfiller config show

# Show with sources
gformfiller config show --source

# Show as JSON
gformfiller config show --format json
```

### Modify Configuration
```bash
# Edit in your default editor
gformfiller config edit

# Set specific value
gformfiller config set timeouts.page_load 60
gformfiller config set ai.default_provider claude
```

### Maintenance
```bash
# Clean old logs (older than 7 days)
gformfiller config clean-logs --older-than 7

# Clean cache
gformfiller config clean-cache --yes

# Reset to defaults (DANGEROUS)
gformfiller config reset
```

## Configuration Paths

View all configuration paths:
```bash
gformfiller config paths
```

Default structure:
```
$HOME/.gformfiller/
├── config/
│   ├── constants.toml
│   └── logging.toml
├── parsers/
├── responses/
├── prompts/
├── logs/
└── cache/
```

## Validation

Validate your configuration:
```bash
gformfiller config validate
```

This checks:
- Configuration file syntax
- Value ranges and types
- Required API keys
- Directory structure

## Examples

### Increase Timeouts for Slow Networks
```toml
[timeouts]
page_load = 60
element_wait = 20
ai_response = 120
```

### Use Claude with Custom Settings
```bash
export CLAUDE_API_KEY="your_key"
gformfiller start --ai claude --url "..." --parsers my_parsers.toml
```

### Debug Mode
```toml
[logging]
level = "DEBUG"
format = "simple"
console_timestamps = true
```

Or via CLI:
```bash
gformfiller start --verbose --log debug.log ...
```