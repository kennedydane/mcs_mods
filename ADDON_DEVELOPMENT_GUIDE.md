# Add-on Development Guide for This Project

This guide is the complete, step-by-step manual for creating, managing, and debugging add-ons within this specific server project.

## Core Architecture

Our project uses a robust system to safely load custom add-ons without interfering with the server's vanilla content. Here are the key files and directories you need to know:

-   **`addons/`**: This is your primary workspace. All your custom behavior packs and resource packs go in here. The server copies these at startup.
-   **`valid_known_packs.json`**: This is the server's "master list". A pack **must** be registered here for the server to consider it valid.
-   **`world_configs/`**: This directory contains files that tell your world which packs from the master list to actually *activate*.
-   **`docker-compose.yml`**: This file maps your local `addons`, `valid_known_packs.json`, and `world_configs` into the container.
-   **`entrypoint.sh`**: This script runs when the container starts, copying the contents of `addons/` into the live server directories.

---

## Part 1: Creating a New Melee Weapon (Lightsaber)

This covers the basics of creating a new item and its texture.

### Step 1: Define the Item's Behavior

Create a new JSON file at `addons/behavior_packs/enhanced_pickaxe/items/lightsaber.json`.

```json
{
  "format_version": "1.20.20",
  "minecraft:item": {
    "description": {
      "identifier": "dane:lightsaber",
      "category": "equipment",
      "is_experimental": true
    },
    "components": {
      "minecraft:max_stack_size": 1,
      "minecraft:hand_equipped": true,
      "minecraft:foil": true,
      "minecraft:durability": { "max_durability": 5000 },
      "minecraft:damage": 50,
      "minecraft:icon": { "texture": "lightsaber" },
      "minecraft:weapon": {}
    }
  }
}
```
**Crucial Points:**
-   `"identifier"`: Must be unique. Use a personal prefix like `dane:`.
-   `"is_experimental": true`: **Required** for all custom-namespaced items.
-   `"format_version"`: Must be a modern version (e.g., 1.20.20+) for custom items.

### Step 2: Create the Item's Resource Pack

1.  Create a new directory: `addons/resource_packs/lightsaber_resources`.
2.  Create a `manifest.json` inside it. **You must generate two new, unique UUIDs** from a site like [uuidgenerator.net](https://www.uuidgenerator.net/).

    ```json
    {
      "format_version": 2,
      "header": {
        "description": "Lightsaber Resource Pack",
        "name": "Lightsaber Resources",
        "uuid": "GENERATE_A_NEW_UUID_HERE",
        "version": [1, 0, 1],
        "min_engine_version": [1, 21, 0]
      },
      "modules": [
        {
          "description": "Lightsaber resources",
          "type": "resources",
          "uuid": "GENERATE_ANOTHER_NEW_UUID_HERE",
          "version": [1, 0, 1]
        }
      ]
    }
    ```
3.  Create `textures/item_texture.json` to map the texture name to a file.
    ```json
    {
      "resource_pack_name": "lightsaber_resources",
      "texture_name": "atlas.items",
      "texture_data": {
        "lightsaber": { "textures": "textures/items/lightsaber" }
      }
    }
    ```
4.  Place your `lightsaber.png` file in `textures/items/`.

### Step 3: Register and Activate the Packs

1.  **Register:** Add the new resource pack to `valid_known_packs.json`. Use the UUID from your manifest's `header`.
    ```json
    {
        "file_system": "RawPath",
        "path": "resource_packs/lightsaber_resources",
        "uuid": "THE_UUID_FROM_YOUR_MANIFEST_HEADER",
        "version": "1.2.1"
    }
    ```
2.  **Activate:** Add the same UUID to `world_configs/world_resource_packs.json`.
    ```json
    {
        "pack_id": "THE_UUID_FROM_YOUR_MANIFEST_HEADER",
        "version": [ 1, 0, 1 ]
    }
    ```

---

## Part 2: Creating High-Performance Ranged Weapons

This section covers creating accurate, instant-firing projectile weapons like blasters. We'll use a proven two-component system: a shooter item + custom ammunition that spawns projectile entities.

### Architecture Overview

The most reliable approach uses three components:

1. **Shooter Item** (`dane:blaster`) - Uses `minecraft:shooter` with instant firing
2. **Ammunition Item** (`dane:blaster_bolt`) - Uses `minecraft:throwable` + `minecraft:projectile` 
3. **Projectile Entity** (`dane:blaster_bolt` entity) - Defines physics and damage

This hybrid approach gives you precise control over accuracy and performance.

### Step 1: Create the Instant-Fire Blaster

Create `addons/behavior_packs/enhanced_pickaxe/items/blaster.json`:

```json
{
  "format_version": "1.20.20",
  "minecraft:item": {
    "description": {
      "identifier": "dane:blaster",
      "category": "equipment",
      "is_experimental": false
    },
    "components": {
      "minecraft:max_stack_size": 1,
      "minecraft:hand_equipped": true,
      "minecraft:durability": { "max_durability": 250 },
      "minecraft:icon": { "texture": "blaster" },
      "minecraft:shooter": {
        "ammunition": [
          {
            "item": "dane:blaster_bolt",
            "use_offhand": true,
            "search_inventory": true,
            "use_in_creative": true
          }
        ],
        "max_draw_duration": 0.0,
        "scale_power_by_draw_duration": false,
        "charge_on_draw": false
      },
      "minecraft:use_animation": "bow",
      "minecraft:use_duration": 1.0
    }
  }
}
```

**Key Settings for Instant Firing:**
- `max_draw_duration: 0.0` - No charging required
- `scale_power_by_draw_duration: false` - Full power immediately  
- `charge_on_draw: false` - No charge animation

### Step 2: Create High-Accuracy Ammunition

Create `addons/behavior_packs/enhanced_pickaxe/items/blaster_bolt.json`:

```json
{
  "format_version": "1.20.20",
  "minecraft:item": {
    "description": {
      "identifier": "dane:blaster_bolt",
      "category": "equipment",
      "is_experimental": false
    },
    "components": {
      "minecraft:max_stack_size": 64,
      "minecraft:icon": { "texture": "blaster_bolt" },
      "minecraft:throwable": {
        "do_swing_animation": false,
        "launch_power_scale": 2.0,
        "max_draw_duration": 0.0,
        "max_launch_power": 2.0,
        "min_draw_duration": 0.0,
        "scale_power_by_draw_duration": false
      },
      "minecraft:projectile": {
        "minimum_critical_power": 0.0,
        "projectile_entity": "dane:blaster_bolt"
      }
    }
  }
}
```

**Accuracy-Critical Settings:**
- `do_swing_animation: false` - Removes animation delays
- `launch_power_scale: 2.0` - Consistent power delivery
- `minimum_critical_power: 0.0` - No accuracy penalty for low power

### Step 3: Create Optimized Projectile Entity

Create `addons/behavior_packs/enhanced_pickaxe/entities/blaster_bolt.json`. Base this on Mojang's proven patterns:

```json
{
  "format_version": "1.21.40",
  "minecraft:entity": {
    "description": {
      "identifier": "dane:blaster_bolt",
      "is_spawnable": false,
      "is_summonable": false
    },
    "components": {
      "minecraft:collision_box": {
        "width": 0.31,
        "height": 0.31
      },
      "minecraft:projectile": {
        "on_hit": {
          "impact_damage": {
            "damage": 20,
            "knockback": true,
            "semi_random_diff_damage": false
          }
        },
        "power": 3.5,
        "gravity": 0.005,
        "inertia": 1,
        "liquid_inertia": 1,
        "anchor": 1,
        "offset": [0, 0, 0],
        "semi_random_diff_damage": false,
        "uncertainty_base": 0.0,
        "reflect_on_hurt": false
      },
      "minecraft:physics": {},
      "minecraft:dimension_bound": {},
      "minecraft:pushable": {
        "is_pushable": true,
        "is_pushable_by_piston": true
      },
      "minecraft:conditional_bandwidth_optimization": {
        "default_values": {
          "max_optimized_distance": 80.0,
          "max_dropped_ticks": 7,
          "use_motion_prediction_hints": true
        }
      }
    }
  }
}
```

**Final Optimized Settings (after extensive testing):**
- Small collision box: `0.1x0.1` (prevents getting stuck)
- Zero gravity: `gravity: 0.0` (perfectly straight trajectories)  
- High speed: `power: 5.0` (matches player arrow speed)
- Perfect aim: `angle_offset: 0.0` with `anchor: 1`
- Anti-targeting: `multiple_targets: false`, `homing: false`
- **No physics component** (causes stuck-in-air issues with custom projectiles)
- `conditional_bandwidth_optimization` for network performance

### Critical Discoveries from Testing

**The Physics Component Problem:**
- Vanilla projectiles like snowballs use `minecraft:physics: {}`
- **Custom projectiles get stuck in mid-air with this component**
- Always omit `minecraft:physics` for reliable custom projectiles

**Collision Box Size Matters:**
- Large collision boxes (`0.25x0.25`) cause getting stuck on invisible edges
- Small collision boxes (`0.1x0.1`) prevent mid-air freezing
- Smaller is better for fast, high-powered projectiles

**Client Entity Rendering:**
- Must use exact vanilla patterns: `geometry.item_sprite` + `controller.render.item_sprite`
- Include billboard animation: `animation.actor.billboard`
- Use vanilla materials: `"snowball"` (not custom emissive materials)

**Accuracy Solutions:**
- Remove ALL uncertainty settings for custom projectiles (don't copy arrow patterns)
- Use `angle_offset: 0.0` instead of `uncertainty_base/multiplier` 
- Disable auto-targeting with `multiple_targets: false` and `homing: false`

### Performance Tuning Guide

**For Perfect Straight Flight:**
- `gravity: 0.0` - No drop whatsoever
- `angle_offset: 0.0` - No angular deviation
- Small collision box (`0.1x0.1`) - Won't catch on edges
- No `minecraft:physics` component - Prevents freezing

**For Maximum Speed & Range:**
- `power: 5.0` - Player arrow speed (proven maximum)
- `anchor: 1` - Eye-level spawn (consistent with vanilla)
- `offset: [0, -0.1, 0]` - Vanilla projectile offset pattern

**For Instant Firing:**
- `max_draw_duration: 0.0` in shooter
- `charge_on_draw: false`
- `scale_power_by_draw_duration: false`
- `minecraft:use_duration: 0.1` (must be > 0 to satisfy shooter component)

**For Visual Consistency:**
- Use vanilla texture paths: `"textures/items/snowball"`
- Copy exact client entity patterns from Mojang samples
- Include bandwidth optimization from vanilla projectiles

### Step 3: Add Textures and Client-Side Definitions

1.  Add `blaster.png` to `textures/items/` in your resource pack.
2.  Add `blaster_bolt.png` to a new `textures/entity/` directory.
3.  Update `item_texture.json` to include the new `blaster` texture.
4.  Create a **client entity file** at `addons/resource_packs/lightsaber_resources/entity/blaster_bolt.json`. This is crucial for telling the game how to *render* the projectile.

    ```json
    {
      "format_version": "1.10.0",
      "minecraft:client_entity": {
        "description": {
          "identifier": "dane:blaster_bolt",
          "materials": { "default": "entity_alphatest" },
          "textures": { "default": "textures/entity/blaster_bolt" },
          "geometry": { "default": "geometry.arrow" },
          "render_controllers": [ "controller.render.arrow" ]
        }
      }
    }
    ```

---

## Part 3: Workflow and Debugging

### Updating an Existing Pack

When you add new content (like the blaster) to an existing pack, you **must increment the version number** to force clients to re-download it.

**ALL 5 FILES** must be updated with the same version number:

1.  **Behavior Pack Manifest**: `addons/behavior_packs/enhanced_pickaxe/manifest.json`
    - Change `[1, 2, 1]` to `[1, 2, 2]` in both the `header` and `modules` sections.

2.  **Resource Pack Manifest**: `addons/resource_packs/lightsaber_resources/manifest.json`  
    - Change `[1, 2, 1]` to `[1, 2, 2]` in both the `header` and `modules` sections.

3.  **Server Pack Registry**: `valid_known_packs.json`
    - Change `"1.2.1"` to `"1.2.2"` for **both** behavior and resource pack entries.

4.  **World Behavior Pack Config**: `world_configs/world_behavior_packs.json`
    - Change `[1, 2, 1]` to `[1, 2, 2]`.

5.  **World Resource Pack Config**: `world_configs/world_resource_packs.json`
    - Change `[1, 2, 1]` to `[1, 2, 2]`.

⚠️ **Critical:** If even ONE file has the wrong version, clients won't reload the packs!

### Debugging Checklist

Follow these steps if something isn't working.

1.  **Restart the Server:** After any change, run `docker compose restart`.
2.  **Client Doesn't Download Packs?**
    -   You forgot to update the version numbers in **all 5 files** listed above after an update.
    -   Check that both behavior AND resource pack versions match everywhere.
3.  **`/give` Command Fails ("Unknown item")**
    -   Check the server logs: `docker compose logs`.
    -   Look for JSON parsing errors. A single missing comma or bracket will cause this.
    -   Did you forget `"is_experimental": false` in the item's description?
    -   Is the `"format_version"` high enough (e.g., 1.20.20+)?
4.  **Item Appears But Action Fails (e.g., Blaster doesn't shoot)**
    -   Again, check the logs. The server will report if it can't find the projectile entity (`dane:blaster_bolt`).
    -   This is likely an error in the projectile's entity file (`blaster_bolt.json`).
5.  **Item/Entity is Invisible or a Purple/Black Box**
    -   The link between the entity and its texture is broken.
    -   Did you create the client-side entity file (e.g., `resource_packs/.../entity/blaster_bolt.json`)?
    -   Are the paths in `item_texture.json` and the client entity file correct?
6.  **Weird On-Screen Text or Unwanted Effects**
    -   Your behavior pack likely has a "ticking function".
    -   Look for a `functions` directory in the behavior pack and check the `.mcfunction` files for commands like `/title` or `/effect`.

### Projectile Weapon Troubleshooting

**Weapon won't fire at all:**
- Check if you have ammunition (`dane:blaster_bolt` items) in inventory
- Verify `ammunition` array in shooter references the correct item
- Ensure `minecraft:use_duration` is set (try 1.0)
- Look for server logs mentioning missing entities

**Projectiles are inaccurate:**
- Remove `uncertainty_base` and `uncertainty_multiplier` entirely from entity
- Use `angle_offset: 0.0` in projectile entity (proven approach)
- Set `anchor: 1` and `offset: [0, -0.1, 0]` (vanilla pattern)
- Add `multiple_targets: false` and `homing: false` to prevent auto-targeting
- Set `do_swing_animation: false` in ammunition item

**Projectiles don't go far enough:**
- Increase `power` in projectile entity (3.5+ recommended)  
- Reduce `gravity` to 0.005 or lower
- Check that `max_launch_power` in ammunition matches requirements

**Projectiles shoot above crosshair:**
- This is caused by `offset: [0, 0.5, 0]` - change to `[0, 0, 0]`
- Wrong `anchor` value can also cause offset issues

**Slow projectile speed:**
- Increase `power` in entity (try 3.5+)
- Ensure `launch_power_scale` is 2.0+ in ammunition item
- Check `max_launch_power` in ammunition (should be 2.0+)

**Weapon requires charging (like bow):**
- Set `max_draw_duration: 0.0` in shooter component
- Use `charge_on_draw: false` 
- Set `scale_power_by_draw_duration: false`

**Inconsistent damage:**
- Set `semi_random_diff_damage: false` in both impact_damage and entity
- Use fixed damage values, avoid damage ranges

**Projectiles get stuck in mid-air:**
- **Remove `minecraft:physics: {}` component entirely** (major cause)
- Use smaller collision box (`0.1x0.1` instead of `0.25x0.25`)
- Check for auto-targeting issues (`multiple_targets: false`, `homing: false`)
- Avoid complex inertia settings (`inertia`, `liquid_inertia`)

**Projectiles are invisible/not rendering:**
- Use exact vanilla client entity patterns from Mojang samples
- Geometry: `"geometry.item_sprite"` (not `geometry.cube` or custom)
- Render controller: `"controller.render.item_sprite"`
- Material: `"snowball"` (proven to work)
- Include billboard animation: `"animation.actor.billboard"`
- Use vanilla texture paths: `"textures/items/snowball"`

**Network/Performance Issues:**
- Add `conditional_bandwidth_optimization` component to entity
- Use proven collision box sizes (`0.1x0.1` for fast projectiles)
- Set entities as `is_spawnable: false, is_summonable: false`
- Omit `minecraft:physics` component for custom projectiles