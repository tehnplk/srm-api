---
trigger: always_on
---

# General Code Style & Formatting
- To create new module you have to separate file into 2 files  first is UI file (subfix as _ui) and second is logic file (explore code example in scaffolding directory).
- When need to implement style you should to implement style in _ui file.
- UI file should design in light theme and look modernize.
- Always use context7 when I need code generation, setup or configuration steps, or
library/API documentation. This means you should automatically use the Context7 MCP
tools to resolve library id and get library docs without me having to explicitly ask.
- Long task should implement by Qthread.
- A child form can be opened from both the Menu and the Toolbar.
- When a module is removed, its menu should also be removed.
- Do not use nested or unnecessary try-except blocks.
- Always print the error message to the console in each try-except block.
- when finnish build module . Explain it into modules.md