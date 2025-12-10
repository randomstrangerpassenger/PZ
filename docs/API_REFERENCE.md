# Pulse API Quick Reference

## Event System

```java
// Subscribe to events
EventBus.subscribe(GameTickEvent.class, event -> {
    // Handle event
}, "mymod");

// Post custom events
EventBus.post(new MyCustomEvent());

// Unsubscribe all listeners for a mod
EventBus.unsubscribeAll("mymod");
```

## Configuration

```java
@Config(modId = "mymod", file = "config.json")
public class MyConfig {
    @Config.Entry(comment = "Enable feature")
    public boolean enableFeature = true;
    
    @Config.Entry(min = 0, max = 100)
    public int amount = 50;
}

// Usage
ConfigManager.register(MyConfig.class);
MyConfig config = ConfigManager.get(MyConfig.class);
```

## Custom Items

```java
// Define item
ItemDefinition item = new ItemDefinition("mymod", "super_sword")
    .name("Super Sword")
    .type(ItemType.WEAPON)
    .weight(2.0f)
    .property("damage", 50)
    .tag("weapon", "melee");

// Register
ItemRegistry.register(item);
```

## Recipes

```java
RecipeRegistry.Recipe recipe = new RecipeRegistry.Recipe(
    Identifier.of("mymod", "craft_super_sword"),
    Identifier.of("mymod", "super_sword")
)
.ingredient(Identifier.of("base", "steel"), 5)
.ingredient(Identifier.of("base", "leather"), 2)
.tool(Identifier.of("base", "hammer"))
.craftTime(120);

RecipeRegistry.register(recipe);
```

## Networking

```java
// Define packet
public class MyPacket implements Packet {
    private String message;
    
    @Override public Identifier getId() {
        return Identifier.of("mymod", "my_packet");
    }
    // ... write/read methods
}

// Register
NetworkManager.registerPacket(MyPacket.class, MyPacket::new, NetworkSide.BOTH);

// Handle
NetworkManager.registerHandler(MyPacket.class, (packet, sender) -> {
    // Handle received packet
});

// Send
NetworkManager.sendToServer(new MyPacket("Hello!"));
```

## Inter-Mod Communication

```java
// Provide a service
IMC.registerService("mymod:api", MyAPI.class, MyAPI::new);

// Use a service
MyAPI api = IMC.getService("othermod:api", MyAPI.class);

// Send a message
IMC.sendMessage("othermod", "event_type", data);
```

## UI System

```java
// Create a button
Button btn = new Button(10, 10, 100, 30, "Click Me");
btn.setOnClick(button -> System.out.println("Clicked!"));

// Create a panel
Panel panel = new Panel(0, 0, 400, 300);
panel.add(btn);
panel.add(new Label(10, 50, "Hello World"));

// Show screen
UIScreen screen = new UIScreen("My Screen");
screen.add(panel);
UIScreen.open(screen);
```

## Developer Tools

```java
// Console commands
DevConsole.execute("mods list");
DevConsole.execute("mods reload mymod");

// Profiling
ProfilerSection section = ModProfiler.start("mymod", "heavyOperation");
try {
    // ... heavy work
} finally {
    section.end();
}

// Event monitoring
EventMonitor.enable();
EventMonitor.printStats();
```
