# Document Upload Scripts

This directory contains upload scripts for managing policy and strategy documents that are used by the StrategyGenerationAgent for evidence-based strategy creation.

## Overview

The StrategyGenerationAgent uses document context from Anthropic's Files API to generate more informed and evidence-based public health strategies. These scripts help upload the necessary reference documents.

## Scripts

### 1. Policy Document Upload (`policy_upload.py`)

Uploads PDF policy documents from `documents/policies/` to Anthropic Files API.

**Usage:**
```bash
python utils/policy_upload.py
```

**Features:**
- Uploads COVID-19 policy briefs and guidelines
- Automatic file size validation
- Detailed upload progress and summary
- File listing and management
- Confirmation prompts before upload

**Expected Documents:**
- Policy briefs (COVID-19 specific)
- Regulatory guidelines
- Compliance documents
- Official health protocols

### 2. Strategy Document Upload (`strategy_upload.py`)

Uploads PDF strategy documents from `documents/strategy/` to Anthropic Files API.

**Usage:**
```bash
python utils/strategy_upload.py
```

**Features:**
- Uploads epidemic preparedness and response strategies
- Document type detection and categorization
- WHO/PAHO guidelines integration
- Strategy-specific file filtering and listing
- Integration with StrategyGenerationAgent

**Expected Documents:**
- Epidemic/outbreak response strategies
- Pandemic preparedness plans
- Crisis communication frameworks
- Emergency preparedness protocols
- WHO/PAHO guidelines and technical documents

**Current Strategy Documents:**
- `MARSH_outbreaks-epidemics-pandemics-preparedness-response-strategies-uk.pdf` (3.1 MB) → Epidemic/Outbreak Response
- `PAHO_2009-creating-communication-strategy-pandemic-influenza.pdf` (0.4 MB) → Pandemic Preparedness
- `PAHO_HSS_Tec_Doc5Eng_21_07_09.pdf` (0.2 MB) → WHO/PAHO Guidelines
- `PAHO_HSS_TecDoc_6_Eng_21_07_09.pdf` (0.2 MB) → WHO/PAHO Guidelines
- `PAHO_WHO_cd61-12-e-epidemic-intelligence-rev1.pdf` (0.3 MB) → Epidemic/Outbreak Response

## Configuration

Both scripts require:

1. **Anthropic API Key** (one of):
   - Environment variable: `ANTHROPIC_API_KEY`
   - `.env` file in project root
   - Backend configuration file

2. **Dependencies**:
   ```bash
   cd backend/app
   pip install -r requirements.txt
   ```

3. **Directory Structure**:
   ```
   documents/
   ├── policies/          # Policy documents (policy_upload.py)
   │   ├── policy-brief_covid-19_ipc.pdf
   │   ├── policy-brief_covid-19_rcce.pdf
   │   └── policy-brief_covid-19_testing.pdf
   └── strategy/          # Strategy documents (strategy_upload.py)
       ├── PAHO_WHO_cd61-12-e-epidemic-intelligence-rev1.pdf
       ├── PAHO_HSS_TecDoc_6_Eng_21_07_09.pdf
       ├── PAHO_HSS_Tec_Doc5Eng_21_07_09.pdf
       ├── PAHO_2009-creating-communication-strategy-pandemic-influenza.pdf
       └── MARSH_outbreaks-epidemics-pandemics-preparedness-response-strategies-uk.pdf
   ```

## Integration with StrategyGenerationAgent

The uploaded documents are automatically detected and used by the `StrategyGenerationAgent`:

### Document Detection Logic

**Policy Documents:**
- Filenames containing `policy`

**Strategy Documents:**
- Filenames containing: `strategy`, `paho`, `who`, `epidemic`, `outbreak`, `preparedness`, `response`

### Usage in Strategy Generation

1. **Automatic Detection**: Agent queries Anthropic Files API for relevant documents
2. **Context Integration**: Documents are attached to Claude API calls as reference material
3. **Evidence-Based Generation**: Strategies include references to uploaded guidelines and best practices
4. **Compliance Assurance**: Generated strategies align with official policies and proven methodologies

### Agent Integration Example

```python
from app.agents.strategy_generation_agent import StrategyGenerationAgent
from app.models.alert import AlertCreate

# Agent automatically uses uploaded documents
agent = StrategyGenerationAgent()
alert = AlertCreate(name="...", description="...", ...)
strategies = await agent.generate_strategies(alert)

# Generated strategies will reference:
# - Policy documents for compliance
# - Strategy documents for proven methodologies
# - WHO/PAHO guidelines for international standards
```

## Testing

### Test Strategy Upload (Without Actually Uploading)

```bash
python utils/test_strategy_upload.py
```

This validates:
- Script imports and initialization
- Directory structure and file discovery
- Document type detection
- Upload preview and size calculations

### Full Upload Process

1. **Preview Upload**:
   ```bash
   python utils/strategy_upload.py
   ```
   - Shows files to be uploaded
   - Displays document types and sizes
   - Requires confirmation before proceeding

2. **Monitor Progress**:
   - Real-time upload progress for each file
   - File ID assignment and validation
   - Error handling and retry logic

3. **Verify Upload**:
   - List uploaded files by type
   - Validate file accessibility
   - Test integration with StrategyGenerationAgent

## File Management

### Listing Uploaded Files

Both scripts provide options to list uploaded files:

```bash
# Strategy files only
List strategy-related files in your Anthropic account? (y/N): y

# All files
List ALL files in your Anthropic account? (y/N): y
```

### File ID Management

After upload, file IDs are provided for:
- Manual Claude API integration
- Direct file reference in conversations
- Debugging and validation

Example output:
```
🔗 File IDs for Claude usage in strategy generation:
   file-abc123def456 # PAHO_WHO_cd61-12-e-epidemic-intelligence-rev1.pdf
   file-def456ghi789 # MARSH_outbreaks-epidemics-pandemics-preparedness-response-strategies-uk.pdf
```

## Best Practices

1. **Document Quality**: Upload high-quality, official documents from reputable sources
2. **File Naming**: Use descriptive filenames that include organization, year, and topic
3. **Size Management**: Keep files under 100MB (Anthropic limit)
4. **Version Control**: Replace outdated documents with newer versions
5. **Categorization**: Organize documents by type (policy vs strategy) for better agent detection

## Troubleshooting

### Common Issues

1. **API Key Not Found**:
   ```
   ❌ Configuration error: Anthropic API key not found
   ```
   Solution: Set `ANTHROPIC_API_KEY` environment variable

2. **Directory Not Found**:
   ```
   ❌ Strategy directory not found: /path/to/documents/strategy
   ```
   Solution: Ensure directory exists and contains PDF files

3. **File Size Too Large**:
   ```
   ⚠️ Warning: large_file.pdf is 150.0 MB (may exceed limits)
   ```
   Solution: Compress or split large files

4. **Upload Failure**:
   ```
   ❌ API Error uploading file.pdf: Rate limit exceeded
   ```
   Solution: Wait and retry, or check API quotas

### Debug Mode

For detailed logging, set environment variable:
```bash
DEBUG=1 python utils/strategy_upload.py
```

## Future Enhancements

- **Automatic document updates** when files change
- **Document versioning** and change tracking  
- **Batch upload optimization** for large document sets
- **Document content analysis** and indexing
- **Integration with document management systems**
- **Automated document quality validation** 