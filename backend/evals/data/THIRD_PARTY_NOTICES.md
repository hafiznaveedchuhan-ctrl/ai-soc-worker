# Third-party notices — eval data

## OTRF Security-Datasets (6 events, mapped to the Wazuh alert shape)
Alerts EV-A035 … EV-A040 are derived from these public, simulated lab recordings
(`theshire.local` lab, hosts WORKSTATION5/WORKSTATION6, users wardog/pgustavo):
- `datasets/atomic/windows/credential_access/host/cmd_psexec_lsa_secrets_dump.zip`
- `datasets/atomic/windows/lateral_movement/host/covenant_sharpsc_create_dcerpc_smb_svcctl.zip`

Source: https://github.com/OTRF/Security-Datasets (downloaded 2026-11-12 with Naveed's "haan").

```
MIT License

Copyright (c) 2021 Open Threat Research Forge

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Wazuh ruleset v4.14.10 (rule ids only, GPLv2)
Rule ids, levels, descriptions and MITRE ids for 4151, 91809, 91844 and 92068 were read from
https://github.com/wazuh/wazuh/tree/v4.14.10/ruleset/rules (0900-firewall_rules.xml L27,
0915-win-powershell_rules.xml L74 and L432, 0800-sysmon_id_1.xml L734). No ruleset file is
copied into this repository.
