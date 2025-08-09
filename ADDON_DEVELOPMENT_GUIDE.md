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

## Part 2: Creating a Ranged Weapon (Blaster)

This builds on Part 1 by adding a projectile entity.

### Step 1: Define the Blaster Item

Create `addons/behavior_packs/enhanced_pickaxe/items/blaster.json`. The key component is `minecraft:shooter`, which defines what projectile to fire and what ammunition it requires.

```json
{
  "format_version": "1.20.20",
  "minecraft:item": {
    "description": {
      "identifier": "dane:blaster",
      "category": "equipment",
      "is_experimental": true
    },
    "components": {
      "minecraft:max_stack_size": 1,
      "minecraft:hand_equipped": true,
      "minecraft:durability": { "max_durability": 250 },
      "minecraft:icon": { "texture": "blaster" },
      "minecraft:shooter": {
        "projectile": "dane:blaster_bolt",
        "launch_power": 3.0,
        "ammunition": [
          {
            "item": "minecraft:arrow",
            "use_offhand": true,
            "search_inventory": true,
            "use_in_creative": false
          }
        ]
      },
      "minecraft:use_animation": "bow",
      "minecraft:use_duration": 1.0
    }
  }
}
```

**Key Components:**
- `minecraft:shooter`: Defines projectile firing behavior
- `ammunition`: Requires arrows in inventory to fire 
- `use_duration`: 1.0 second charge time like a bow
- `launch_power`: 3.0 determines projectile speed

**Usage:**
- Give yourself the blaster: `/give @s dane:blaster`
- Get ammunition: `/give @s minecraft:arrow 64`
- Hold to charge like a bow, release to fire `dane:blaster_bolt`

### Step 2: Define the Projectile Entity

1.  Create a new directory: `addons/behavior_packs/enhanced_pickaxe/entities/`.
2.  Create `blaster_bolt.json` inside it. This defines the projectile's physics and damage.

    ```json
    {
      "format_version": "1.16.0",
      "minecraft:entity": {
        "description": {
          "identifier": "dane:blaster_bolt",
          "is_summonable": true
        },
        "components": {
          "minecraft:projectile": {
            "on_hit": { "impact_damage": { "damage": 15 } },
            "gravity": 0.0
          },
          "minecraft:physics": {}
        }
      }
    }
    ```

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
    -   Did you forget `"is_experimental": true` in the item's description?
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