# Add-on Development Guide for This Project

This guide provides a concrete, step-by-step walkthrough for creating and adding new custom add-ons to this specific server project. We will use the creation of a "Lightsaber" item as a practical example.

## Core Concepts

Our project uses a specific, robust method for managing add-ons to ensure they are loaded correctly by the dedicated server. The key components are:

-   **`addons/` directory**: A staging area where you place your behavior and resource pack files. This is the only directory you need to touch when developing.
-   **`valid_known_packs.json`**: A master list that tells the server which packs are legitimate and should be considered for loading.
-   **`world_configs/` directory**: Contains files that tell a specific world which packs to *activate* on startup.
-   **`entrypoint.sh`**: A script that automatically copies your add-ons from the `addons/` directory into the server's internal directories when the container starts.

---

## Tutorial: Creating a Lightsaber

### Step 1: Define the Item's Behavior

First, we need to tell the game what a lightsaber is and what it does.

1.  Navigate to `addons/behavior_packs/`. We will add our new item to the existing `enhanced_pickaxe` pack to keep things simple.
2.  Create a new file at `addons/behavior_packs/enhanced_pickaxe/items/lightsaber.json`.
3.  Add the following JSON content. This defines an item that does 50 damage, has high durability, and glows.

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
      "minecraft:durability": {
        "max_durability": 5000
      },
      "minecraft:damage": 50,
      "minecraft:enchantable": {
        "value": 15,
        "slot": "sword"
      },
      "minecraft:can_destroy_in_creative": false,
      "minecraft:icon": {
        "texture": "lightsaber"
      },
      "minecraft:weapon": {}
    }
  }
}
```

**Key Points:**
*   `"identifier": "dane:lightsaber"`: This is the unique name for our item. The `dane:` part is a custom namespace.
*   `"is_experimental": true`: This is **required** for custom items with unique identifiers.
*   `"format_version": "1.20.20"`: A modern format version is **required** for custom items.

### Step 2: Create the Item's Appearance (Resource Pack)

Now, let's create the resource pack that contains the lightsaber's texture.

1.  Create a new directory for the pack: `addons/resource_packs/lightsaber_resources`.
2.  Create the manifest file: `addons/resource_packs/lightsaber_resources/manifest.json`. This requires two **new, unique UUIDs**. You can generate them from a site like [uuidgenerator.net](https://www.uuidgenerator.net/).

```json
{
  "format_version": 2,
  "header": {
    "description": "Lightsaber Resource Pack",
    "name": "Lightsaber Resources",
    "uuid": "GENERATE_A_NEW_UUID_HERE",
    "version": [1, 0, 0],
    "min_engine_version": [1, 21, 0]
  },
  "modules": [
    {
      "description": "Lightsaber resources",
      "type": "resources",
      "uuid": "GENERATE_ANOTHER_NEW_UUID_HERE",
      "version": [1, 0, 0]
    }
  ]
}
```

3.  Create the texture definition file at `addons/resource_packs/lightsaber_resources/textures/item_texture.json`. This maps the item's texture name (`lightsaber`) to a file path.

```json
{
  "resource_pack_name": "lightsaber_resources",
  "texture_name": "atlas.items",
  "texture_data": {
    "lightsaber": {
      "textures": "textures/items/lightsaber"
    }
  }
}
```

4.  Create the actual texture file. Place a 16x16 PNG file at `addons/resource_packs/lightsaber_resources/textures/items/lightsaber.png`.

### Step 3: Register and Activate the New Packs

Now we tell the server and the world to load our new resource pack.

1.  **Register the Pack:** Open the main `valid_known_packs.json` file and add an entry for your new resource pack. You'll need the UUID from its `manifest.json`.

```json
[
    {
        "file_system": "RawPath",
        "path": "behavior_packs/enhanced_pickaxe",
        "uuid": "f4a1f1e0-1b2a-4b8e-9d4c-5a6b7c8d9e0f",
        "version": "1.0.0"
    },
    {
        "file_system": "RawPath",
        "path": "resource_packs/lightsaber_resources",
        "uuid": "THE_UUID_FROM_YOUR_MANIFEST_HEADER",
        "version": "1.0.0"
    }
]
```

2.  **Activate the Pack:** Open `world_configs/world_resource_packs.json` and add an entry to activate the pack for the world.

```json
[
    {
        "pack_id": "THE_UUID_FROM_YOUR_MANIFEST_HEADER",
        "version": [
            1,
            0,
            0
        ]
    }
]
```

### Step 4: Test In-Game

You're all set!

1.  **Restart the server:**
    ```bash
    docker compose restart
    ```
    *(If you ever change the `Dockerfile` or `entrypoint.sh`, you must use `docker compose up --build` instead).*

2.  **Connect to the server.** It should prompt you to download the resource packs. This is a great sign!

3.  **Give yourself the item.** Once in the world, run the command:
    ```bash
    /give @s dane:lightsaber
    ```

If it works, the lightsaber will appear in your inventory. If it fails, check the server logs (`docker compose logs`) for JSON parsing errors. The server is very specific about syntax, and a single missing comma can cause a pack to fail loading.
