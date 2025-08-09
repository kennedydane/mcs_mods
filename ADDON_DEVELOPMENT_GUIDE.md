# Minecraft Bedrock Add-on Development Guide

## Overview

This guide covers best practices for developing Minecraft Bedrock Edition add-ons in 2025, based on the latest official documentation and tools from Microsoft/Mojang.

## What Are Add-ons?

Minecraft Bedrock add-ons consist of two main components:

- **Resource Packs**: Custom models, sounds, textures, and visual content
- **Behavior Packs**: Entity behaviors, loot drops, spawn rules, items, recipes, trade tables, and scripting logic

## Development Environment Setup

### Required Tools

1. **Visual Studio Code** - Free editor with excellent JSON support and Bedrock-specific extensions
2. **Minecraft Creator Tools (mctools.dev)** - Official Mojang toolset for project creation and validation
3. **Node.js** - Required for command-line creator tools
4. **Git** - Version control for your add-on projects

### Installing Creator Tools

```bash
# Install the command-line tools via npm
npm install -g @minecraft/creator-tools

# Or use the web interface at https://mctools.dev
```

### Development Folders

Use these special folders for active development:
- `development_resource_packs/` - Updated each time Minecraft launches
- `development_behavior_packs/` - Updated each time Minecraft launches

## Project Structure Best Practices

### Basic Add-on Structure

```
my-addon/
├── behavior_pack/
│   ├── manifest.json
│   ├── pack_icon.png
│   ├── entities/
│   ├── items/
│   ├── recipes/
│   ├── loot_tables/
│   ├── functions/
│   └── scripts/
│       └── main.js
└── resource_pack/
    ├── manifest.json
    ├── pack_icon.png
    ├── textures/
    ├── models/
    ├── sounds/
    └── animations/
```

### Manifest.json Format (2025)

#### Behavior Pack Manifest

```json
{
  "format_version": 2,
  "header": {
    "description": "My Custom Add-on",
    "name": "My Add-on",
    "uuid": "unique-uuid-here",
    "version": [1, 0, 0],
    "min_engine_version": [1, 21, 90]
  },
  "modules": [
    {
      "description": "Behavior Pack Module",
      "type": "data",
      "uuid": "another-unique-uuid",
      "version": [1, 0, 0]
    },
    {
      "description": "Script Module",
      "type": "script",
      "language": "javascript",
      "entry": "scripts/main.js",
      "uuid": "script-module-uuid",
      "version": [1, 0, 0]
    }
  ],
  "dependencies": [
    {
      "module_name": "@minecraft/server",
      "version": "2.0.0"
    }
  ]
}
```

#### Resource Pack Manifest

```json
{
  "format_version": 2,
  "header": {
    "description": "My Custom Add-on Resources",
    "name": "My Add-on Resources",
    "uuid": "resource-pack-uuid",
    "version": [1, 0, 0],
    "min_engine_version": [1, 21, 90]
  },
  "modules": [
    {
      "description": "Resource Pack Module",
      "type": "resources",
      "uuid": "resource-module-uuid",
      "version": [1, 0, 0]
    }
  ]
}
```

## Scripting API Best Practices (2025)

### Version 2.0.0 Migration

The Scripting API v2.0.0 is now the recommended version with significant improvements:

- **Earlier Initialization**: Scripts now initialize much earlier in world startup
- **Stable API Modules**: No breaking changes in stable releases
- **Improved Performance**: Better event handling and data management

### Core Modules

```javascript
// Import stable modules (no Beta APIs experiment needed)
import { world, system, BlockPermutation } from '@minecraft/server';
import { ActionFormData, MessageFormData } from '@minecraft/server-ui';

// Event-driven architecture example
world.afterEvents.itemUse.subscribe((event) => {
    const player = event.source;
    const item = event.itemStack;
    
    // Handle item usage
    player.sendMessage(`You used: ${item.typeId}`);
});

// Dynamic properties for data storage
world.setDynamicProperty('myData', 'persistent value');
const data = world.getDynamicProperty('myData'); // Returns 'persistent value'
```

### Modern API Patterns

```javascript
// Use system.runJob for async operations instead of runCommandAsync
system.runJob(function* () {
    yield;
    // Long-running operation
    for (let i = 0; i < 1000; i++) {
        // Process data
        yield; // Yield control back to the game
    }
});

// New knockback API pattern (v2.0.0)
entity.applyKnockback(
    { x: 1, z: 0 }, // Direction vector (normalized)
    5, // Horizontal strength
    2  // Vertical strength
);
```

## Development Workflow

### 1. Project Creation

Start projects using mctools.dev for best practices:

```bash
# Command line approach
mc-tools create-project --template behavior-pack my-addon

# Or use the web interface at https://mctools.dev
```

### 2. Validation and Testing

```bash
# Validate your add-on structure
mc-tools validate ./my-addon

# Check for current platform version compliance
# Use the Inspector tool at mctools.dev
```

### 3. Packaging for Distribution

```bash
# Create .mcaddon file for distribution
mc-tools package ./my-addon --output my-addon.mcaddon
```

## File Organization Best Practices

### Entity Files

```
behavior_pack/entities/
├── custom_mob.json          # Entity definition
├── custom_mob_client.json   # Client-side behaviors
└── spawn_rules/
    └── custom_mob.json      # Spawn conditions
```

### Item Files

```
behavior_pack/items/
├── custom_sword.json        # Item definition
└── recipes/
    └── custom_sword.json    # Crafting recipe
```

### Function Files

```
behavior_pack/functions/
├── setup.mcfunction         # Initialization commands
├── tick.json               # Tick function configuration
└── utility/
    └── teleport.mcfunction  # Utility functions
```

## Testing and Debugging

### Local Testing

1. Place your add-on in development folders
2. Enable experimental features if using Beta APIs:
   - Beta APIs
   - Holiday Creator Features
   - Custom Biomes
   - Upcoming Creator Features

### Debugging Scripts

```javascript
import { world } from '@minecraft/server';

// Console logging for debugging
console.warn('Debug message'); // Shows in content log
world.sendMessage('Server message'); // Shows to all players

// Error handling
try {
    // Risky operation
    player.runCommand('risky command');
} catch (error) {
    console.error('Command failed:', error);
}
```

## Performance Optimization

### Script Performance

- Use `afterEvents` instead of `beforeEvents` unless cancellation is needed
- Batch operations using `system.runJob` with yields
- Limit dynamic property usage (32KB per property limit)
- Cache frequently accessed data

### Resource Optimization

- Optimize texture sizes (powers of 2: 16x16, 32x32, 64x64)
- Use efficient model geometries
- Compress audio files appropriately
- Minimize unused assets

## Distribution and Compatibility

### Version Management

- Follow N-1 rule for `min_engine_version`
- Use stable API versions for production
- Test on multiple Minecraft versions
- Document version requirements clearly

### Platform Considerations

- Test on multiple devices (mobile, console, PC)
- Consider performance limitations on mobile
- Ensure UI elements scale properly
- Test network synchronization in multiplayer

## Common Pitfalls to Avoid

1. **Using Beta APIs in Production**: Stick to stable APIs unless necessary
2. **Hardcoded Values**: Use configuration files and dynamic properties
3. **Excessive Command Usage**: Prefer Script API over commands when possible
4. **Poor Error Handling**: Always wrap risky operations in try-catch
5. **Memory Leaks**: Properly unsubscribe from events when needed
6. **Large Texture Files**: Optimize images for better performance

## Resources and Documentation

### Official Resources

- [Microsoft Learn - Minecraft Creator](https://learn.microsoft.com/en-us/minecraft/creator/)
- [Minecraft Creator Tools](https://mctools.dev/)
- [Script API Reference](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/)
- [Bedrock Samples on GitHub](https://github.com/Mojang/bedrock-samples)

### Community Resources

- [Bedrock Wiki](https://wiki.bedrock.dev/)
- [MCPEDL](https://mcpedl.com/) - Add-on distribution
- [CurseForge Bedrock](https://www.curseforge.com/minecraft-bedrock)

### Validation Tools

- Use mctools.dev Inspector for platform version validation
- Enable content logging in Minecraft for debugging
- Test in creative mode before survival deployment

## Next Steps

This guide provides the foundation for modern Minecraft Bedrock add-on development. The next phase would involve:

1. Choosing a specific add-on concept
2. Setting up the development environment
3. Creating the basic project structure
4. Implementing core functionality
5. Testing and iterating
6. Packaging for distribution

Remember to stay updated with the latest Minecraft versions and API changes, as the platform continues to evolve rapidly.