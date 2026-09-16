"""Source/consumer rules for recovered item functions, with bounded wording.

Rules admit conditional functions, never an unconditional runtime action or
whole-question completion. Recipe input/output details remain source evidence.
"""
from collections import defaultdict
import re

from . import source_reader as reader
from . import semantic_results as semantic
from . import investigation as inv

from .recovery_source_index import stable_properties, water_form, module_imports, recipe_participants, recover_participation, import_evidence

from .recovery_crafting_roles import baking_roles, welding_roles, spear_roles

from .recovery_vocabulary import (
    ACTIVATION,
    ADD_ROPE,
    ADD_WATER,
    ALARM_DIALOG,
    ALARM_SETTING,
    ALARM_STOP,
    ALARM_STOPPING,
    AMMUNITION_FIELDS,
    AMMUNITION_ITEMS,
    AMMUNITION_LOADING_PATHS,
    ANIMAL_PREPARATION,
    ASH_CLEARING,
    ATTACHMENT_PURPOSES,
    BACK_CONTAINER,
    BAKING,
    BANDAGE_APPLICATION,
    BANDAGE_INFECTION,
    BANDAGE_ITEMS,
    BANDAGE_LIFE,
    BANDAGE_MATERIALS,
    BANDAGE_OR_BURN_PANIC,
    BANDAGE_PANIC,
    BANDAGE_RECIPE_WASHING,
    BANDAGE_REMOVAL,
    BANDAGE_WASHING,
    BARRICADE,
    BASE_OBJECT,
    BATTERY_INSERT,
    BATTERY_INSERTION,
    BATTERY_REMOVAL_RECIPE,
    BATTERY_REMOVE,
    BATTERY_TEMPLATE,
    BATTER_TEST,
    BBQ_MENU,
    BEAN_PREPARATION,
    BEARD_GROOMING,
    BEARD_TRIM,
    BELLOWS_USE,
    BISCUIT_PORTIONING,
    BLACKSMITH_MENU,
    BLOOD_CLEANING,
    BODY_DRYING,
    BODY_LABELS,
    BODY_LOCATIONS,
    BODY_WASHING,
    BOWL_PORTIONING,
    BOX_PACKING,
    BRAKE_WEAR,
    BROKEN_GLASS_ITEMS,
    BUILD_CLASSES,
    BUILD_FACTORIES,
    BULLET_REMOVAL,
    BURNT_VEHICLE,
    BURNT_VEHICLE_USE,
    BURN_CLEANING,
    BURN_CORPSE,
    CAKE_PAN_PREPARATION,
    CAMPFIRE_PLACEMENT,
    CAMP_ADD,
    CAMP_CLIENT,
    CAMP_COMMANDS,
    CAMP_FRICTION,
    CAMP_FUEL,
    CAMP_FUEL_USE,
    CAMP_IGNITER,
    CAMP_KINDLE_LIGHT,
    CAMP_KIT_PREPARATION,
    CAMP_LIGHT,
    CAMP_MENU,
    CAMP_OBJECT,
    CAMP_PETROL_LIGHT,
    CAMP_PETROL_USE,
    CAMP_PLACEMENT,
    CAMP_PLACEMENT_SOURCES,
    CAMP_SERVER,
    CAMP_TINDER_USE,
    CANDLE_EXTINGUISH_RECIPE,
    CANDLE_LIGHT_RECIPE,
    CANDLE_UNEQUIP,
    CANDY_OPENING,
    CANNED_COOKED,
    CAN_OPENING,
    CARPENTRY_MATERIAL,
    CARRYING,
    CHARGER_ACTIONS,
    CHARGER_CONTROLS,
    CHARGER_PLACEMENT,
    CHOP,
    CHOPPING,
    CHOP_CURSOR,
    CLEAN_BANDAGE,
    CLEAN_BLOOD,
    CLEAN_BURN,
    CLEAN_CURSOR,
    CLEAR_ASHES,
    CLIMB_ROPE,
    CLOCK_CHARACTER,
    CLOCK_PROMPT,
    CLOTHING_EXTRA,
    CLOTHING_FORM,
    CODE_LOCK_USE,
    CODE_UNLOCK,
    COMPOST_ACTIONS,
    COMPOST_TRANSFER,
    CONSOLIDATE,
    CONSUMING,
    CONTENTS_EMPTYING,
    CONTEXT_DELETE,
    CONTEXT_ELEMENT,
    CONTEXT_INVENTORY,
    CONTEXT_LOADER,
    CONTEXT_MANAGER,
    CONTEXT_MEDIA,
    CONTEXT_MOVABLE,
    CONTEXT_RADIO,
    CONTROL_SOURCES,
    COOKED_SLICING,
    COOKING_ACTION,
    COOKING_BASE,
    CORPSE_IGNITION,
    CRAFT_UI,
    CROP_WATERING,
    CURE_FLIES,
    CURE_MILDEW,
    CURTAIN_ACTIONS,
    CURTAIN_USE,
    DESTROY_ACTION,
    DESTROY_CURSOR,
    DEVICE_ASSEMBLY,
    DEVICE_DELAY,
    DEVICE_PANEL,
    DEVICE_PLACE,
    DEVICE_PLACEMENT,
    DEVICE_POWER,
    DEVICE_RETRIEVAL,
    DEVICE_TAKE,
    DEVICE_TIMER,
    DEVICE_TIMER_CONTROL,
    DEVICE_VOLUME,
    DEVICE_WORLD_PLACEMENT,
    DIGITAL_CODE,
    DIRTY_BANDAGING,
    DISINFECT,
    DISINFECTION,
    DISINFECTION_ADMIN_PAIN,
    DISINFECTION_USE,
    DOOR_KEY_USE,
    DOOR_LOCK,
    DOUGH_SLICING,
    DRAINABLE_MATERIALS,
    DRAINABLE_MATERIAL_FIELDS,
    DROP_OBJECT,
    DRUM_LOGS,
    DRUM_SOURCES,
    DRY_BODY,
    DUMP_CONTENTS,
    DUMP_WATER,
    DYE_APPLICATION,
    EFFECTS,
    EGG_CARTON_OPENING,
    EGG_PACKING,
    ELECTRICAL_FIELDS,
    ELECTRICAL_SOURCES,
    ELECTRONIC_SALVAGE,
    EMPTY_PETROL_ITEMS,
    ENGINE_ACTIONS,
    ENGINE_REPAIR,
    ENGINE_SALVAGE,
    EQUIPMENT_WASHING,
    EQUIPPED_RAIN_USE,
    ESCAPE_ROPE_CLIMB,
    ESCAPE_ROPE_INSTALL,
    ESCAPE_ROPE_REMOVE,
    EXTINGUISH_CONDITIONS,
    EXTINGUISH_CURSOR,
    FABRIC_ACTION,
    FARM_CLIENT,
    FARM_COMMANDS,
    FARM_MENU,
    FARM_SYSTEM,
    FERTILIZER_GROWTH,
    FERTILIZER_ROT,
    FERTILIZE_ACTION,
    FERTILIZING,
    FIREARM,
    FIREARM_FIELDS,
    FIREARM_ITEMS,
    FIREARM_RADIAL,
    FIREPLACE_MENU,
    FIRE_FIGHTING,
    FIRING,
    FISHING_ACTION,
    FISHING_EXECUTION,
    FISHING_LURES,
    FISHING_LURE_LOSS,
    FISHING_MATCHES,
    FISHING_PROPERTIES,
    FISHING_UI,
    FISH_CREATED,
    FISH_PREPARATION,
    FITNESS_SOURCES,
    FIXING_ACTION,
    FLOOR_GLASS_INJURY,
    FLOOR_GLASS_PICKUP,
    FOOD_ASSEMBLY,
    FOOD_NAMING,
    FOOD_PREPARATION_RECIPES,
    FOOD_SLICING,
    FOOD_TRANSFER,
    FOOD_TRAP_BAIT,
    FORGE_PREPARATION,
    FROG_PREPARATION,
    FUEL_FIELDS,
    FUNCTIONS,
    FURNACE_FUEL,
    FURROW_DIGGING,
    GARMENT_PATCHING,
    GARMENT_PATCH_REMOVAL,
    GARMENT_UI,
    GENERATOR_ACTIONS,
    GENERATOR_CONTROL,
    GENERATOR_EXTERIOR_USE,
    GENERATOR_HANDLING,
    GENERATOR_INFO,
    GENERATOR_INSPECTION,
    GENERATOR_MAP,
    GENERATOR_REFUEL,
    GENERATOR_REPAIR,
    GLASS_REMOVAL,
    GRAIN_VESSEL_PREPARATION,
    GRAVE_CURSOR,
    GRAVE_DIGGING,
    GRAVE_FILL,
    GRAVE_FILLING,
    GROUND_CURSOR,
    GROUND_FILL,
    GROUND_MENU,
    GROUND_POUR,
    GROUND_TOOLS,
    GUN_FIRE_MODES,
    GUN_FIRING_CYCLE,
    GUN_MAGAZINE_EJECTION,
    GUN_RACKING,
    GUN_ROUND_LOADING,
    GUN_ROUND_UNLOADING,
    HAIR_CUT,
    HAIR_GROOMING,
    HEADLIGHT_TEMPLATE,
    HEADPHONE_CONNECTION,
    HEALTH,
    HEARTH_FUEL,
    HEARTH_PETROL,
    HEARTH_TINDER,
    HEAT_ACTIONS,
    HEAT_FRICTION,
    HEAT_PATHS,
    HEAT_SOURCES,
    HEAVY_EQUIP,
    HOTBAR,
    HOTBAR_ATTACH,
    HOTBAR_SLOTS,
    INACTIVE_BUILD_FACTORIES,
    INDUSTRIAL_ACTIONS,
    INDUSTRIAL_PETROL,
    INDUSTRIAL_TINDER,
    INSERT_MAGAZINE,
    INVENTORY_PAGE,
    ITEM_TRANSFORMATION_RECIPES,
    JAR_BOX_OPENING,
    JAR_PREPARATION,
    KEY_ALARM,
    KEY_ITEMS,
    KEY_MECHANICS,
    LAMP_ACTION,
    LAMP_BATTERY,
    LAMP_BULB,
    LAMP_CONVERSION,
    LEARNING_PURPOSES,
    LEGACY_GUN_CONTROLS,
    LEGACY_GUN_ITEMS,
    LEGACY_MEDIA_MENU,
    LEGACY_RELOAD,
    LEGACY_RELOAD_SOURCES,
    LIGHT_BINDING,
    LIGHT_BULBS,
    LIGHT_CONTROL,
    LIGHT_FIELDS,
    LIGHT_ITEMS,
    LIGHT_RADIAL,
    LOADING,
    LOAD_MAGAZINE,
    LOG_BINDING,
    MAGAZINE_EMPTY,
    MAGAZINE_FILL,
    MAGAZINE_ITEMS,
    MAGAZINE_LOADING,
    MAKEUP_DEFINITIONS,
    MAKEUP_LIFECYCLE,
    MAKEUP_UI,
    MAKEUP_USE,
    MAP_ANNOTATION,
    MAP_DEFINITIONS,
    MAP_ERASURE,
    MAP_READING,
    MAP_REVEAL,
    MAP_SYMBOLS,
    MAP_TEXT,
    MAP_VIEW,
    MATERIAL_ASSEMBLY,
    MATERIAL_OBJECT_FIELDS,
    MATERIAL_OBJECT_ITEMS,
    MATTRESS_PREPARATION,
    MEAL_UTENSIL,
    MEDIA_DATA,
    MEDIA_INFO,
    MEDIA_INSERT,
    MEDIA_LABEL,
    MEDIA_LOADER,
    MEDICAL_CONSOLIDATION,
    MEDICAL_PANIC,
    MEDICINE_PURPOSES,
    MELEE,
    METAL_BARRICADE,
    METAL_UNBARRICADE,
    MIC_CONTROL,
    MOLOTOV_ASSEMBLY,
    MOVE_CURSOR,
    MOVE_TOOLS,
    MUFFIN_PORTIONING,
    NAME_DIALOG,
    NATURAL_FLOOR,
    NET_CHECK,
    NET_CHECKING,
    NET_OBJECT,
    NET_PLACEMENT,
    NET_REMOVAL,
    NONSMOKER_EFFECT,
    NOTE_ACCESS,
    NOTE_EDIT,
    NOTE_EDITOR,
    NOTE_IMPLEMENT,
    NOTE_LIMITS,
    NOTE_LOCK,
    NOTE_SAVE,
    OATMEAL_PREPARATION,
    OBJECT_COMMANDS,
    OBJECT_LABELS,
    OLD_BATTERY_RECHARGE,
    OMELETTE_PREPARATION,
    OPENED_FOOD,
    OPENING,
    PADLOCK_ACTION,
    PADLOCK_KEY_USE,
    PADLOCK_USE,
    PAINTING,
    PAINTING_REFERENCE,
    PAINT_ACTION,
    PAINT_ACTIONS,
    PAINT_CURSOR,
    PAINT_MENU,
    PANEL_DOOR,
    PANEL_FORMS,
    PANEL_INSTALL,
    PANEL_LOCK,
    PANEL_NAMES,
    PANEL_REMOVE,
    PANEL_TEMPLATES,
    PANEL_WINDOW,
    PARTICIPANT_FUNCTIONS,
    PATCH_GARMENT,
    PETROL_ITEMS,
    PHYSICS_ATTACK,
    PICKUP,
    PICKUP_GLASS,
    PICKUP_LOSS,
    PILLAR_BATTERY,
    PILLAR_INSERT,
    PILLAR_LIGHT,
    PILLAR_REMOVE,
    PILL_ITEMS,
    PILL_TAKING,
    PIZZA_SLICING,
    PLACED_PURPOSES,
    PLACEMENT,
    PLACE_OBJECT,
    PLAIN_OBJECT_FIELDS,
    PLAIN_OBJECT_LABELS,
    PLANT,
    PLANT_CURSOR,
    PLANT_CUTTING,
    PLANT_REMOVAL,
    PLASTER_ACTION,
    PLASTER_MIXING,
    PLASTER_USE,
    PLOW_ACTION,
    PLOW_CURSOR,
    PLUMBING,
    PLUMB_ACTION,
    POISONOUS_WILD_FOOD,
    POULTICES,
    POULTICE_PREPARATION,
    POULTICE_USE,
    PRODUCE_SACK_OPENING,
    PROPANE_ACTIONS,
    PROPANE_BARBECUE,
    PUMP_CONTAINER,
    PUT_OUT_FIRE,
    QUALIFIERS,
    RADIO_ACTION,
    RADIO_CHANNEL,
    RADIO_CODE_EFFECTS,
    RADIO_CRAFTING,
    RADIO_DISMANTLING,
    RADIO_FIELDS,
    RADIO_GENERAL,
    RADIO_GRID,
    RADIO_HEADPHONE_CONTROL,
    RADIO_INTERACTIONS,
    RADIO_MEDIA,
    RADIO_MEDIA_CONTROL,
    RADIO_MIC,
    RADIO_PANEL,
    RADIO_POWER,
    RADIO_PRESETS,
    RADIO_PRESET_EDITOR,
    RADIO_SIGNAL,
    RADIO_TUNING,
    RADIO_VOLUME,
    RADIO_WINDOW,
    RADIO_WINDOW_LIFETIME,
    RADIO_WORLD_FORM,
    READ_MAXIMUM,
    READ_MOOD,
    READ_PROGRESS,
    READ_SELECTION,
    RELOAD_ACTIONS,
    REMOTE_CONTROLLER_FIELDS,
    REMOTE_CONTROLLER_ITEMS,
    REMOTE_LINK,
    REMOTE_RESET,
    REMOTE_TRIGGER,
    REMOVE_BULLET,
    REMOVE_BUSH,
    REMOVE_GLASS,
    REMOVE_PATCH,
    REMOVE_ROPE,
    RENAME_ITEM,
    REVIEW_FUNCTIONS,
    ROD_FISHING,
    ROD_LINE_BREAK,
    ROD_REPAIR_INPUT,
    ROPE_MAKING,
    RUNNING_EXCHANGE,
    RUNNING_WEAR,
    SANDWICH_PREPARATION,
    SAWN_WOOD,
    SCRAP_RECOVERY,
    SEED_ACTION,
    SEED_DEFINITIONS,
    SEED_EXTRACTION,
    SEED_PACKING,
    SHOTGUN_SHORTENING,
    SHOVEL_GROUND,
    SHOVEL_PLANT,
    SHOVEL_SMITHING,
    SIGN_ACTION,
    SIMPLE_TRANSFORMATION,
    SLOT_USE,
    SMITHING_PARTS,
    SMOKER_EFFECT,
    SMOKING,
    SOWING,
    SOW_COUNTS,
    SPEAR_ATTACHMENTS,
    SPEAR_CONDITIONS,
    SPEAR_FISHING,
    SPEAR_FISHING_WEAR,
    SPEAR_ITEMS,
    SPEAR_STONE_LOSS,
    SPEAR_TOOL_WEAR,
    SPLINT,
    SPLINTING,
    SPLINT_REMOVAL,
    SPRAY_PREPARATION,
    SPRAY_TREATMENT,
    STAGE_ACTION,
    STITCH,
    STITCHING,
    STONE_TOOL_WEAR,
    STRAP_SPEED,
    STRUCTURE_DESTRUCTION,
    SUTURE_ASSISTANCE,
    TAKE_FUEL,
    TAKE_WATER,
    TENT_KIT_PREPARATION,
    TENT_PLACEMENT,
    TENT_REST,
    THROWN_DEVICE_FIELDS,
    THROWN_DEVICE_ITEMS,
    THUMPABLE_SCRAP,
    TIRE_ACTIONS,
    TIRE_DEFLATION,
    TIRE_INFLATION,
    TIRE_WEAR,
    TORCH_REFILL_RECIPE,
    TRANSFER_WATER,
    TRAP_ACTIONS,
    TRAP_ASSEMBLY,
    TRAP_BAIT,
    TRAP_BIRD,
    TRAP_BUILD,
    TRAP_CATCH,
    TRAP_CLIENT,
    TRAP_CLIENT_OBJECT,
    TRAP_COMMANDS,
    TRAP_CONTROLS,
    TRAP_DEFINITIONS,
    TRAP_LIFECYCLE,
    TRAP_MENU,
    TRAP_OBJECT,
    TRAP_PLACEMENT,
    TRAP_RABBIT_SQUIRREL,
    TRAP_RODENTS,
    TRAP_SYSTEM,
    TRAY_EMPTYING,
    TUTORIAL_MENU,
    TV_CHANNEL,
    TV_TUNING,
    UMBRELLA_CHANGE,
    UNBARRICADE,
    VEHICLE_BATTERY_CYCLE,
    VEHICLE_BATTERY_EXCHANGE,
    VEHICLE_BULB_EXCHANGE,
    VEHICLE_CALLBACKS,
    VEHICLE_COMMANDS,
    VEHICLE_CONTAINER,
    VEHICLE_DASHBOARD,
    VEHICLE_DOOR_ACTIONS,
    VEHICLE_EXCHANGE_REQUIREMENTS,
    VEHICLE_FUEL,
    VEHICLE_FUEL_ACTIONS,
    VEHICLE_FUEL_ENGINE,
    VEHICLE_INSTALL,
    VEHICLE_KEY_USE,
    VEHICLE_MECHANICS,
    VEHICLE_MENU,
    VEHICLE_RUNNING_FORMS,
    VEHICLE_RUNNING_TEMPLATES,
    VEHICLE_SEATING,
    VEHICLE_SEAT_ACTIONS,
    VEHICLE_SEAT_UI,
    VEHICLE_START,
    VEHICLE_STORAGE,
    VEHICLE_STORAGE_FORMS,
    VEHICLE_STORAGE_SOURCES,
    VEHICLE_TOOL_TEMPLATES,
    VEHICLE_TOOL_USE,
    VEHICLE_UNINSTALL,
    VEHICLE_USE_MENU,
    VEHICLE_WASHING,
    WASHING_OUTCOME,
    WASH_BODY,
    WASH_CLOTHING,
    WASH_TARGET,
    WASH_VEHICLE,
    WATER_DRINKING,
    WATER_EMPTYING,
    WATER_PLANT,
    WATER_STORAGE,
    WATER_TRANSFER,
    WEAPON_ATTACHMENT,
    WEAPON_ATTACHMENT_TOOL,
    WEAPON_EQUIP,
    WEAPON_PART_REMOVAL,
    WEAPON_REMOVAL,
    WEAPON_UPGRADE,
    WEARING,
    WEAR_ACTION,
    WEIGHT_EXERCISE,
    WELDED_PARTS,
    WELDING_CONSTRUCTION,
    WELDING_MENU,
    WINDOW_GLASS,
    WIRE_RECOVERY,
    WOOD_BARRICADE,
    WOOD_SHAPING,
    WOOD_UNBARRICADE,
    WORLD_MENU,
    WORLD_WATER_TRANSFER,
)


# These are equipment locations, not protection/visual-coverage claims. The
# exact script location remains in the state payload even when labels coincide.
RULES = {
    'plumbing_tool': {'positive': 'Exact PipeWrench selection joins world menu predicates, equip/action validity and the actual plumbObject server receiver.', 'scope': 'external-water-use flag plumbing', 'exclusions': 'No implicit pathfinding, repeated server tool/source check, water creation or purification claim.'},
    'weight_exercise': {'positive': 'Exact FitnessExercises item/prop registration joins fitness UI possession/equipment, action guards and animation-loop exerciseRepeat dispatch.', 'scope': 'barbell curls and two dumbbell exercises', 'exclusions': 'No direct XP/stiffness/strength arithmetic or constant equipment revalidation; commented showHandModel is not active.'},
    'back_container_wearing': {'positive': 'Exact Container/CanBeEquipped=Back joins inventory back-equipment selection, transfer/wear callback and ISWearClothing inventory, interruption and setWornItem branches.',
                              'scope': 'back container wearing', 'exclusions': 'Does not generalize the back menu to other declared slots or calculate native weight reduction/slot replacement.'},
    'literature_selection': {'positive': 'Exact non-writable Literature joins doLiteratureMenu, onLiteratureItems/readItem and ISReadABook validity, duration, progress and completion branches.',
                             'scope': 'selected literature reading conditions',
                             'exclusions': 'Driver validity is an early return, not a conjunction with the ordinary inventory/page guard. Completion read markers do not prove native learning or mood changes.'},
    'opened_food_preparation': {'positive': 'A fully reviewed opening recipe joins its exact Food result declaration and stable EvolvedRecipe entries to unique evolved recipes and the actual ingredient-addition menu/action. Opening and ingredient eligibility remain attached to the resulting-content function.',
                                 'exclusions': 'The unopened package is not relabeled as an ingredient. No arbitrary result fallback, consumed container substitution or unconditional nutrition/cooking outcome.'},
    'animal_trap': {'positive': 'Stable Trap=true and unique exact registered Traps.type join the world-menu inventory scan, TrapBO construction, mod-data identity and actual server hourly catch path. A positive registered Animals trap entry is required for the conditional catching function.',
                    'exclusions': 'No trap-name-only admission, fixed catch, probability or species exclusivity. Placement consumes the inventory trap. Loaded-square suppression is retained directly rather than inventing a fixed player-distance rule.'},
    'remote_control': {'positive': 'Stable RemoteController=true or Weapon/CanBeRemote=true joins exact selected-item/menu counterpart scans and direct ID setters. Assigned controller triggering joins the active sendClientCommand path to Commands.object.triggerRemote.',
                       'exclusions': 'The commented single-player dispatch is not used as live evidence. No guaranteed trigger, explosion, radius, global unlink or placed-device effect follows from ID linking or sending the request.'},
    'fertilizing': {'positive': 'Exact Fertilizer/CompostBag menu selection including compost priority joins ISFertilizeAction, the farming client/system command registration, Commands.fertilize and SPlantGlobalObject.fertilize/rottenThis. Alive/non-plowed, previous-count and nextGrowing lower-bound conditions stay attached to their respective effects.',
                    'exclusions': 'No continuous inventory/remaining-use check is invented. Schedule advance and excessive-application rot are separate conditional effects, not universal growth success or fertilizer efficacy.'},
    'food_trap_bait': {'positive': 'Actual Food selection with uncooked/no-extra/Drink exclusion and hunger/Worm condition joins adjacency, ISAddBaitAction fractional consumption and the registered server bait assignment.', 'exclusions': 'No continuous bait-inventory guard, arbitrary animal acceptance, guaranteed catch or promised full-food consumption.'},
    'food_selected_state': {'positive': 'Exact Food declarations join the completed-transfer chef setter and any exact evolved-result naming, CannedFood_OnCooked or registered Fishing.OnCreateFish consumer. Callback setters retain their actual conditions and arithmetic.', 'exclusions': 'No generic eating effect from field signs, age reset, cooked-result guarantee, inactive fish rename, unregistered fish initialization or runtime callback-dispatch guarantee.'},
    'vehicle_seating': {'positive': 'The exact NormalCarSeat template mapping joins seat UI and actual entry, switch, exit, stored-item clearing and stopping actions.', 'exclusions': 'No loose-seat sitting, guaranteed passenger binding/animation completion, rest effect or commented engine shutdown/start behavior.'},
    'vehicle_storage': {'positive': 'Exact numbered mechanics declarations join the matching template itemType or explicit Trunk override, actual ContainerAccess callbacks, inventory-page native access calls and transfer consumer. Gasoline templates additionally join the actual fuel actions/server command and engine check/update.', 'exclusions': 'No loose-item container, guaranteed native suffix compatibility/capacity, generic install operation for templates without work tables, unconditional fuel transfer or engine-start guarantee.'},
    'container_emptying': {'positive': 'Exact stable declarations join the single-selection water branch or a finite replacement chain reaching CanStoreWater and the separate dump actions. Contents replacement on completion and progressive water decrease remain distinct.', 'exclusions': 'No cyclic or ambiguous chain admission, intermediate output delivery, guaranteed terminal factory result, purification or transfer into a receiver.'},
    'drainable_consolidation': {'positive': 'Stable Drainable declarations not explicitly disabling consolidation join the actual canConsolidate guard, same-type receiver lookup and progressive transfer action.', 'exclusions': 'Missing CanConsolidate is not promoted to true; the native guard remains a condition. No unconditional combining, full-type lookup equivalence or exact depleted replacement.'},
    'fire_extinguishing': {'positive': 'Actual FireFighting short-type/water-source selection joins the active world menu, 2x2 cursor and ISPutOutFire visibility, per-square consumption and character/ground calls.', 'exclusions': 'No automatic protection, extinguishing guarantee, unlimited supply or recursive generic inventory selection.'},
    'ground_bags': {'positive': 'Exact dirt/gravel/sand forms and HoldDirt containers join the registered ground menu, collection cursor/action, shovelGround server command and natural-floor pour consumer.', 'exclusions': 'No output-as-input role, arbitrary bag substitution, guaranteed whole-bag fill, atomic terrain/inventory change, farming result or extra pour shovel/amount guard.'},
    'smithing_parts': {'positive': 'The two complete Make Door Knob/Make Hinge records bind IronIngot material and kept BallPeenHammer/Tongs tools to NearItem:Anvil, learned Blacksmith=3 eligibility, ISCraftAction and the actual Blacksmith15 XP callback.',
                       'exclusions': 'No MetalWelding substitution, anvil acquisition guarantee, output-as-input role, native nearby-object radius or unconditional XP/output delivery.'},
    'material_assembly': {'positive': 'Exact reviewed callback-free stone-tool, splint, drawer and fishing-gear clause sequences distinguish consumed assembly materials from the explicit kept SharpKnife/MeatCleaver cutting alternative. ISCraftAction provides eligibility and driving conditions.',
                          'exclusions': 'No recipe-name-only identity, arbitrary kept tool, output-as-input, finished tool effect or treatment outcome. Same-name fishing-rod overloads are matched by complete clauses.'},
    'radio_crafting': {'positive': 'Three exact makeshift radio recipe names, outputs and participant clauses join learned/skill/unbroken declarations, the Screwdriver group, ISCraftAction and RadioCraft callback. Only consumed component clauses receive material roles; the explicit screwdriver receives a tool role.',
                       'exclusions': 'Result-only participation is acquisition evidence. No powered-device functionality, fixed range, fixed weight, quality or quantitative yield is inferred from being a component.'},
    'rod_fishing': {'positive': 'Stable FishingRod tag or FishingLure=true with exact registered lure properties joins the water menu, inventory UI selection/equipment and ISFishingAction. Literal extra lure membership uses the supplied loop that registers each entry and appends it to each fish lure list.',
                    'exclusions': 'The rod function is conditional on the nonspear branch; no WeaponType classification is guessed. Registered bait is required, not any item with FishingLure alone. Catch chance, zone population, line breakage and fish/trash selection prevent a guaranteed fish result. No quantitative probability or species-exclusive claim is admitted.'},
    'dirty_bandage': {'positive': 'Stable CanBandage=true and an exact type-name Dirty match join the Health-panel application to ISApplyBandage.perform overriding the calculated bandageLife with zero before SetBandaged.',
                       'exclusions': 'BandagePower alone does not override the explicit zero branch. No healing, wound infection, infected-item flag or clean-bandage outcome is inferred.'},
    'campfire_fuel': {'positive': 'Exact positive literal fuel/tinder type entry or the declared Clothing/Literature category joins isValidFuel/isValidTinder, menu transfer/path selection, the fuel/light timed action and actual campfire client-to-server command receiver. Clothing fabric restrictions and container emptiness are retained.',
                      'exclusions': 'No item-name-only fuel inference outside the registry, no sprite-to-trash type substitution, no unconditional rain/heat/damage/duration guarantee. Fuel addition and tinder consumption/lighting remain separate functions; the menu excludes vehicle occupants.'},
    'electronic_salvage': {'positive': 'Unique Electrical recipe with reviewed DismantleElectronics test and a Screwdriver group joins exact consumed/destroyed device members to known electronic component results and absent or reviewed Dismantle/Dismantle2/TVRemote/Flashlight callbacks. Radio/TwoWay/HAM/TV callbacks include their explicit legacy aliases, NoBrokenItems and separate XP callback; their tool context is kept separate from other electronics. Digital-watch and camera groups use their actual type/name or tag predicates.',
                           'exclusions': 'No arbitrary keep-to-tool inference: the exact Screwdriver group and its consumer are required. No XP, fixed salvage amount, guaranteed recovered battery or whole-scope crafting completion is inferred.'},
    'carpentry_material': {'positive': 'An active addOption callback joins an exact factory need:FullType assignment, its reviewed object constructor/create consumer and buildUtil.consumeMaterial. The shared build action, material and object-specific placement checks are bound separately from menu reachability.',
                           'exclusions': 'Unreferenced/commented-out factories do not establish an active-menu use. No all-object eligibility, continuous material recheck, construction result/health guarantee or unconditional double-door consumption is inferred. Exact recipes and output relations remain outside the user-facing role.'},
    'battery_receiver': {'positive': 'Exact destroy-device/destroy-Battery/result-same-device recipe clauses join the TorchBatteryInsert zero-device-charge test and result:setUsedDelta(selected Battery usedDelta) callback through ISCraftAction.',
                         'exclusions': 'No illumination, charge increase, full battery or power-duration claim. Duplicate recipe display names do not collapse distinct exact participant records; admission requires one matching full clause sequence.'},
    'note_implements': {'positive': 'Stable Write/Pen/Pencil/RedPen/BluePen tag joins the writable-note editable predicate and onWriteSomething/ISUIWriteJournal/onWriteSomethingClick page/title setters.',
                        'exclusions': 'The item enables note editing; no arbitrary document or paper management, continuous implement-presence check, ink expenditure, or ownership-lock bypass is inferred.'},
    'map_annotation_tools': {'positive': 'Unambiguous item tags match the actual ISWorldMapSymbols colorButtonInfo/canWrite registry; exact Base.Eraser or Eraser tag matches canErase. ISMap creates this editor, whose add-text/add-texture and remove-index callbacks mutate the symbols API.',
                             'exclusions': 'Write or Erase tag alone is not substituted for the symbols editor registry. The characterless editor bypass is not an item function. No paper organization, arbitrary document editing, ink consumption or persistence guarantee is inferred.'},
    'umbrella_form': {'positive': 'Each exact four-clause Open/Close Umbrella recipe is joined by its unique consumed form, result declaration and reviewed form-change callback, then ISCraftAction eligibility/PerformMakeItem. Repeated display names are not treated as a unique recipe identity.',
                      'exclusions': 'No rain protection or continuous holding guarantee. Callback condition copying and hand flags are bounded to that recipe execution; an unrelated item named Umbrella is not admitted.'},
    'activation': {'positive': 'Unique ActivatedItem=true declaration joins selected-item canBeActivated/hand-or-attached checks and the menu onActivateItem setActivated(not isActivated) callback.',
                   'exclusions': 'Multiselection and CandleLit are excluded. The native Drainable predicate is retained without replacing it with a broader script-type assumption. No light emission, warmth, power consumption or other device effect is inferred.'},
    'stage_conditions': {'positive': 'Existing source-bound multistage material/tool role joins onMultiStageBuildSelected, canDoStage and ISMultiStageBuild start/perform/consumeMaterial.',
                         'exclusions': 'The start check is not described as continuous inventory validation. No guarantee of the engine doStage result, arbitrary building eligibility, or normal material consumption in cheat mode.'},
    'sowing': {'positive': 'Exact seedName registry binds menu seed selection/count and ISSeedAction consumption to the actual farming seed command and plowed-plant seed method. Packets additionally require their unique opening recipe result to match that seedName.',
               'exclusions': 'No packet-as-loose-seed alias, plant growth duration, harvest amount or guaranteed germination. Reach, quantity, inventory, interruption and server furrow-state predicates are retained.'},
    'moving_role_recovery': {'positive': 'Exact item FullType or unambiguous tag joins ItemTypeToTag and addToolDefinition; hasTool selects a matching item recursively from inventory for the object-requested pickup/place tool.',
                            'exclusions': 'No unqualified-token alias or broken-tool exclusion is invented. Furniture properties, reach and permissions remain required; membership does not guarantee all furniture can be moved.'},
    'fixing_role_recovery': {'positive': 'Exact Require or Fixer token in a unique raw fixing record is joined to the same item declaration and the selected fixing-rule consumer. Target and supplied repair material remain separate roles.',
                            'exclusions': 'No inference from weapon name, unrelated duplicate field or repair tooltip. No selection of a duplicate fixing definition and no guaranteed success or repaired amount.'},
    'fixing_conditions': {'positive': 'Existing exact repair role is joined to onFix required-item transfer and ISFixAction inventory predicates, walking/running interruption and FixingManager.fixItem dispatch.',
                          'exclusions': 'Vehicle target inventory is not required. No guaranteed repair, amount, skill sufficiency or success probability is inferred from a tooltip or raw fixing entry.'},
    'cooking_ingredient_recovery': {'positive': 'Unique declaration has an unambiguous EvolvedRecipe scalar whose exact names join unique evolved-recipe records; the menu and action treat the matched item as the ingredient receiver.',
                                   'exclusions': 'Conflicts in unrelated scalar fields do not erase ingredient membership. Their effects remain unresolved; no loader winner, nutrition or automatic recipe success is inferred.'},
    'melee': {'positive': 'Unique Weapon declaration with no projectile PhysicsObject and no explicit ranged true joins the active non-ranged Attack hook and its DoAttack dispatch. The hook does not restrict the branch to Bat swing animations.',
              'exclusions': 'Ranged and thrown forms are excluded. Runtime non-ranged, authorization, attack-start and vehicle predicates are retained. No inferred hit, damage, target, range or comparative weapon effectiveness.'},
    'cooking_base': {'positive': 'Exact BaseItem/ResultItem in a unique evolved recipe joins selected testItem to getEvolvedRecipe, the explicit isResultItem continuation menu and ISAddItemInRecipe base receiver.',
                     'exclusions': 'Result membership alone is not a use: admission requires the explicit continuation dispatch. No automatic cooking, nutrition, unlimited additions or guaranteed transformed FullType; runtime recipe acceptance remains required.'},
    'sheet_rope': {'positive': 'The unique Craft Sheet Rope raw record consumes the explicit CraftSheetRope group and produces SheetRope; the group implementation admits registered fabric unless noSheetRope or a named ClothingRecipesDefinitions entry.',
                   'exclusions': 'No keep-to-tool inference, no recipe-name-only membership, no denim/leather substitution, and no climbing or guaranteed runtime recipe eligibility.'},
    'alarm': {'positive': 'Exact AlarmClock/AlarmClockClothing declaration joins the native class and isDigital menu predicate to the dialog setters and ringing stop action.',
              'exclusions': 'No time-display, guaranteed digital classification, ringing schedule, sound attraction or battery effect. Runtime isDigital and access predicates remain explicit.'},
    'makeup': {'positive': 'Unique MakeUpType declaration joins the inventory makeup branch, explicit registered type choices and ISMakeUpUI selection/setWornItem followed by Apply inventory replacement.',
               'exclusions': 'No specific color, texture, protection, consumption or attractiveness effect. Preview and committed application are separate, with the menu mirror alternatives retained.'},
    'magazine_ammunition': {'positive': 'Exact seven Normal AmmoType/MaxAmmo declarations join the selected-magazine menu to guarded load/unload animation events and their inventory/count changes.', 'exclusions': 'No receiver inferred from GunType or a display name, no original-magazine identity retained after insertion, no guaranteed native animation or factory result.'},
    'weapon_attachment': {'positive': 'Unique WeaponPart with explicit MountOn and recognized PartType joins the weapon-selected mount-list/empty-slot branch to upgrade/removal menus and their distinct possession/slot guards, attach/detach calls and same-part inventory transfer.',
                          'exclusions': 'No inferred damage, range, recoil or aim improvement; weapon and part receivers remain distinct. Weapon compatibility is a prerequisite, not inferred from a name.'},
    'reading_mood': {'positive': 'Non-skill ISReadABook.start snapshots mood; update checks a negative exact mood-change field and restores the snapshot only if current mood has risen above it.',
                     'exclusions': 'Stabilization during reading is distinct from the engine ReadLiterature completion effect. No decrease below the starting value or skill-book mood benefit is asserted.'},
    'furniture_removal': {'positive': 'A unique Moveable WorldObjectSprite identifies the placed form; world-object cursor selection, canPickUpMoveable, normal ISMoveablesAction pickup and pickUpMoveableInternal bind conditional removal.',
                          'exclusions': 'No generic device capability or guaranteed acquisition FullType. World sprite moveability and part mapping remain prerequisites. Type-specific predicate overrides are not replaced by a universal empty-container rule; breakage and destroyed-window behavior are retained.'},
    'food_callbacks': {'positive': 'Exact Food OnEat declaration binds the unique recipecode OnEat_Cigarettes or OnEat_WildFoodGeneric body, explicitly documented as called by IsoGameCharacter.Eat. Branch-specific state setters retain trait, poison and portion conditions.',
                       'exclusions': 'No general nutrition or antibiotic effect inferred from script fields. Cigarette cancellation is excluded; positive facts do not close other native Eat effects.'},
    'furniture_placement': {'positive': 'Unique Moveable declaration with WorldObjectSprite joined to inventory sprite selection, canPlaceMoveable, and the placement action.',
                          'exclusions': 'Placement only. No universal tile validity, pickup, dismantling, appliance operation or decoration effect. Actual sprite/space eligibility remains conditional.'},
    'surface_painting': {'positive': 'Exact paint-type table or exact Paintbrush consumer joined through the active ISPaintCursor path to surface and sign actions.',
                        'exclusions': 'No arbitrary surface, color compatibility or numeric coverage guarantee; cheat bypass does not imply ordinary material-free painting.'},
    'package_opening': {'positive': 'Unique reviewed opening recipe family with one consumed exact package, unique declarations and direct output; optional reviewed CanOpener tag group, and only absent or reviewed OpenSackProduce/OpenEggCarton/OpenCannedFood/OpenBoxOfJars callbacks.',
                       'exclusions': 'No recipe-name-only admission, unknown callback, inferred loader winner, exact result enumeration in user output or arbitrary package opening.'},
    'firearm_operation': {'positive': 'Unique Weapon with explicit Ranged=true and AmmoType; active Hook.Attack routes canShoot to DoAttack and OnWeaponSwingHitPoint handles ammunition.',
                          'exclusions': 'No hit, damage, projectile, range, accuracy or reliability claim; jam/chamber and character conditions remain attached.'},
    'tree_chopping': {'positive': 'Unique Weapon with Axe category and ChopTree tag; predicateChopTree and doChopTree queue ISChopTreeAction, whose ChopTree animation invokes WeaponHit.',
                      'exclusions': 'No tree damage/rate, yield, durability or skill-efficiency claim; reach, held tool and attack validity remain attached.'},
    'native_food_consumption': {'positive': 'Unique Food declaration, no conflicting Type/CantEat/custom-label fields, CantEat not true. The menu custom option is a label and the Drink label selects the Drink animation within ISEatFoodAction; both call character:Eat.',
                                'exclusions': 'Unknown custom labels remain outside the rule. No hunger/thirst, mood, nutrition, poison or OnEat effect is inferred from consumption alone.'},
    'native_food_conditions': {'positive': 'ISEatFoodAction.isValidStart accepts FoodEaten below three OR calories below 1000; isValid requires inventory and any required companion. This corrects the predecessor satiety-only condition.',
                               'exclusions': 'No guarantee of consumption effects or completion after the action becomes invalid.'},
    'clothing_wear': {'positive': 'Unique Clothing and unambiguous BodyLocation joined to doWearClothingMenu/onWearItems and ISWearClothing setWornItem.',
                     'exclusions': 'Repeated unrelated ModelWeaponPart/visual fields do not erase stable Type/BodyLocation. No protection, insulation or body-location expansion beyond the source is inferred.'},
    'note_confirmation': {'positive': 'Journal onClick retains the edited page buffer; onWriteSomethingClick submits addPage and setName/setCustomName only for OK.',
                          'exclusions': 'No XP/mood/recipe learning claim. Calling an explicit item setter establishes the bounded write effect without requiring all engine internals to be reimplemented.'},
    'note_page_bounds': {'positive': 'PageToWrite is supplied to the journal; constructor sets numberOfPages and input length limits, and controls bound previous/next page navigation.',
                         'exclusions': 'Input-device integration correctness is a runtime validation limit, not an unresolved item permission predicate.'},
    'clothing_location': {'positive': 'Unambiguous Clothing BodyLocation is declared in the Human equipment location registry and passed to setWornItem by ISWearClothing.',
                          'exclusions': 'Equipment slot only; no inferred protected body parts, compatibility, thermal or visual effect.'},
    'cooking_conditions': {'positive': 'Accepted ingredient role joins addItemInEvoRecipe food-state filters, onAddItemInEvoRecipe transfers and ISAddItemInRecipe.isValid/new to the exact ingredient and base.',
                           'exclusions': 'Result/base membership is not an ingredient role. getItemsCanBeUse/needToBeCooked/addItem engine semantics and poison-policy state remain bounded dependencies; no guaranteed food benefit.'},
    'ammunition_loading': {'positive': 'Exact AmmoType/MagazineType reverse relation from unique receiver declarations, joined to doReloadMenuForBullets/doReloadMenuForMagazine and their loading actions.',
                           'exclusions': 'No caliber from name matching, guaranteed firing, numeric capacity or universal receiver compatibility. Gun versus magazine paths remain distinct source observations.'},
    'map_viewing': {'positive': 'Native Map declaration joins the selected IsMap branch to onCheckMap, ISMap and setMapItem; update requires continued inventory possession.',
                    'exclusions': 'No accuracy, complete geographical coverage or stash acquisition claim. LootMaps data initialization remains conditional.'},
    'reading_progress': {'positive': 'Positive-page non-writable Literature joins ISReadABook update/checkLevel/perform to item and character setAlreadyReadPages calls; supported SkillBook multiplier handling remains separate.',
                         'exclusions': 'Progress is updated, not guaranteed to increase. Insufficient-level/illiteracy reset and item-local completion reset are preserved; no direct XP or learned-recipe claim.'},
    'reading_parameters': {'positive': 'Unambiguous NumberOfPages and LvlSkillTrained join the unique SkillBook maxMultiplier slot selected in ISReadABook.new; checkMultiplier uses ten-percent progress steps.',
                           'exclusions': 'The book maximum is not a promise to overwrite a higher current multiplier. Supported skill levels, reading validity and progress thresholds remain attached.'},
    'container_carrying': {'positive': 'Unique positive-capacity Container already admitted for storage joins ISInventoryTransferAction.transferItem destContainer:AddItem(self.item); the same container object retains its internal inventory.',
                           'exclusions': 'No weight-reduction, unlimited carrying, item admission or access bypass; transfer prerequisites remain attached.'},
    'water_storage': {'positive': 'Unique CanStoreWater declaration and consistent WaterSource replacement, or an existing Drainable water form with positive UseDelta, join onTakeWater to ISTakeWaterAction filling and ordinary item transfer.',
                      'exclusions': 'No arbitrary liquid, purification, infinite source/capacity or unchanged empty-form identity. Conflicting replacement targets and missing water-form declarations are not admitted.'},
    'health_actions': {'positive': 'Exact Health-panel handler predicates join item alcohol power, short-type or tool tag to the selected treatment and explicit action setter; handler-specific eligibility and patient movement checks remain attached.',
                       'exclusions': 'No healing rate, infection cure, pain benefit, universal body-part eligibility or administrative-branch effect. Glass removal with a tool does not imply that bare-hand removal is impossible.'},
}


for _rule, _scope in (('box_packing', 'exact single-input box recipes'), ('bowl_portioning', 'exact two/four-bowl food recipes')):
    RULES[_rule] = {'positive': 'Complete exact recipe clauses, unique declarations and actual ISCraftAction/recipecode consumers bind material roles and conditional transformation behavior.',
                    'scope': _scope, 'exclusions': 'No recipe-name-only admission, arbitrary keep-to-tool role or guaranteed native output/count/state propagation.'}
for _rule in ('seed_packing', 'jar_preparation'):
    RULES[_rule] = {'positive': 'Unique exact complete recipe clauses and expanded participant identity join ISCraftAction and the named creation/XP callback where present.', 'exclusions': 'No inferred empty package, keep-to-tool conversion, rewritten semicolon quantity, guaranteed native eligibility or preservation effect.'}
RULES['medical_consolidation'] = {'positive': 'The selected DrainableComboItem branch invokes checkConsolidate and dispatches its conditional same-type receiver choice to the actual fraction-transfer timed action.',
    'scope': 'The three reviewed medical drainable declarations, with native canConsolidate retained as a condition',
    'exclusions': 'A Merge label is not proof that canConsolidate is true. No unconditional support, full-type lookup equivalence or exact depleted replacement is claimed.',
    'source_refs': [semantic.MENU, CONSOLIDATE]}
RULES['bandage_lifecycle'] = {'positive': 'HApplyBandage selects positive BandagePower for the exact injured-or-stitched-or-splinted and unbandaged predicate, transfers the material and queues ISApplyBandage. Application records the material FullType and removes it; HRemoveBandage queues the corresponding removal branch for the applied state.',
    'scope': 'Uniquely declared positive-BandagePower and CanBandage materials, including repeated identical field declarations',
    'exclusions': 'No wound-healing guarantee, Dirty-to-infected inference or exact returned-form guarantee.',
    'source_refs': [HEALTH, semantic.BANDAGE]}
RULES['splint_lifecycle'] = {'positive': 'Exact support/sheet or finished-splint selection joins queued handler validity and actual ISSplint application/removal branches, factor assignment and conditional XP.', 'exclusions': 'No inverted drop guard treated as ordinary admission, finished-splint inventory recheck, item-condition preservation or native healing guarantee.'}
RULES['bandage_state'] = {'positive': 'Actual ISApplyBandage completion computes life and conditionally assigns infection/panic, with both menu entry predicates and action interruptions retained.', 'exclusions': 'No Dirty-name infection inference, guaranteed healing, uncapped native state semantics or missed already-bandaged inventory alternative.'}
RULES['burn_cleaning'] = {'positive': 'Exact positive BandagePower >=2 joins HCleanBurn guards, transfer and ISCleanBurn state assignments and Use.', 'exclusions': 'No continuing inventory/burn recheck or direct healing outcome is invented.'}
RULES['bandage_washing'] = {'positive': 'Four exact dirty forms join named cleaning recipes, water-object selection and ISCleanBandage replacement/water command.', 'exclusions': 'The direct action does not run OnTest; UI taint restriction depends on the text option, native result/debit and infection remain separate.'}
RULES['pill_controls'] = {'positive': 'Exact five Pills-prefixed declarations join first-selected transfer, timed inventory guard and JustTookPill handoff.', 'exclusions': 'No medicinal effect, timing or depletion is inferred from the name or FatigueChange sign.'}
RULES['bandage_materials'] = {'positive': 'Exact complete Disinfect Rag/Bandage and alcohol-cotton recipes identify preparation materials; direct and registered group inputs remain bound to their raw clauses, with semicolon quantities uninterpreted.',
    'scope': 'The reviewed callback-free bandaging-material preparation recipes',
    'exclusions': 'No semicolon-to-equals conversion, automatic keep-to-tool rule, native quantity/heat interpretation or output efficacy claim.',
    'source_refs': [semantic.CRAFT, semantic.GROUPS]}
RULES['item_naming'] = {'positive': 'The selected-item container/key/KeyRing/map branches offer the name dialog; its OK callback requires nonempty text and internal length at most 28 before setName and inventory refresh.',
    'scope': 'Unique Container, Key, Map declarations and exact KeyRing type token',
    'exclusions': 'No food custom-name eligibility, journal title editing or type/content transformation inferred.',
    'source_refs': [semantic.MENU, NAME_DIALOG]}
RULES['body_drying'] = {'positive': 'The inventory menu selects DishCloth or BathTowel for wet-body drying, transfers it and queues ISDryMyself with positive wetness/remaining-use/inventory checks.',
    'scope': 'Unique DishCloth and BathTowel declarations', 'exclusions': 'No clothing drying, complete dryness or reusable-tool guarantee.',
    'source_refs': [semantic.MENU, DRY_BODY]}
RULES['ash_clearing'] = {'positive': 'The world menu joins the declared ClearAshes tag to its unbroken-tool predicate, exact burnt-floor ash sprites, adjacent walk/equip and ISClearAshes object removal.',
    'scope': 'Unique declarations with ClearAshes in stable Tags', 'exclusions': 'No arbitrary dirt or blood removal; no inferred continuous tool check absent from the action.',
    'source_refs': [WORLD_MENU, CLEAR_ASHES]}
RULES['worn_attachment_slots'] = {
    'positive': 'Stable AttachmentsProvided entries join registered hotbar slot definitions; refresh derives slots from worn, non-hand items and removes lost-slot attachments. The inventory menu and attach action enforce their separate stated conditions.',
    'scope': 'Unique wearable declarations with the supplied paired belt, right holster or paired holster slot lists',
    'exclusions': 'No generic holding or inventory-management function; no added inventory capacity or unconditional attachment eligibility.',
    'source_refs': [HOTBAR, HOTBAR_SLOTS, HOTBAR_ATTACH, BODY_LOCATIONS, semantic.WEAR],
}
RULES['device_controls'] = {'positive': 'The registered ContextRadio entry opens the actual radio window; channel, volume, power, battery and two-way microphone modules dispatch to the exact timed action operations with their stated eligibility.',
    'scope': 'Unique Radio declarations and their TV/non-TV panel branches; exact Base.Battery donor in the battery control',
    'exclusions': 'No inferred broadcast, reception, transmission or audible output from control availability.',
    'source_refs': [CONTEXT_MANAGER, CONTEXT_INVENTORY, CONTEXT_LOADER, CONTEXT_ELEMENT, CONTEXT_RADIO, RADIO_WINDOW, RADIO_CHANNEL, TV_CHANNEL, RADIO_VOLUME, RADIO_MIC, RADIO_POWER, RADIO_GRID, RADIO_ACTION]}
RULES['recorded_media_controls'] = {'positive': 'A unique declared media category occurs in the loaded recording catalog; the registered media handler displays available assigned extra text, and the media panel verifies recorded state/type before insertion.',
    'scope': 'Declared media-category items under conditional assigned-recording state',
    'exclusions': 'No automatic recording assignment, category-to-numeric-type inference, playback or learning/mood effect.',
    'source_refs': [CONTEXT_MEDIA, MEDIA_INFO, MEDIA_LOADER, MEDIA_DATA, RADIO_MEDIA, RADIO_ACTION]}
RULES['clothing_form'] = {'positive': 'Paired ClothingItemExtraOption/ClothingItemExtra entries join unique wearable/container declarations to the actual extra menu, transfer callback and replacement/wear action.',
    'scope': 'Unique declared clothing and wearable-container variant relations with registered destination locations',
    'exclusions': 'No unpaired option, missing destination, changed protective stat, or native factory success guarantee.',
    'source_refs': [semantic.MENU, CLOTHING_EXTRA, BODY_LOCATIONS]}
RULES['world_blood_cleaning'] = {'positive': 'Active world menu and cursor require blood, bleach and an explicitly named cleaning tool; the caller transfers/equips supplies and the action applies square.removeBlood.',
    'scope': 'Exact Bleach/BathTowel/DishCloth/Broom/Mop type participants',
    'exclusions': 'No general cleaning, body disinfection, clothing washing, or continuous nonbroken-broom requirement is inferred.',
    'source_refs': [WORLD_MENU, CLEAN_CURSOR, CLEAN_BLOOD]}
RULES['radio_headphones'] = {'positive': 'Exact FullType verification in the active radio volume module joins AddHeadphones dispatch to the timed action and device-data handoff.',
    'scope': 'Base.Headphones and Base.Earbuds, portable nontelevision radio panel',
    'exclusions': 'Does not infer headphone audio isolation, sound playback or native item consumption.',
    'source_refs': [RADIO_VOLUME, RADIO_PANEL, RADIO_WINDOW, RADIO_ACTION]}
RULES['baking_preparation'] = {'positive': 'Exact complete dough/batter recipe clauses distinguish named ingredients, explicitly kept mixing/rolling utensils, and bowls or trays. WholeEgg is read independently of participation parsing.',
    'scope': 'Seven bound Base dough/batter recipe records',
    'exclusions': 'No generic input-to-ingredient or keep-to-tool rule, no semicolon-to-equals conversion, no output nutrition or finished baking guarantee.',
    'source_refs': ['scripts/recipes.txt', semantic.GROUPS, semantic.CRAFT]}


RULES['noise_device'] = {
    'positive': 'Exact Base.AlarmClock weapon/NoiseGenerator declaration joins the placement and positive-timer menu branches, timer setter and IsoTrap placement/retrieval actions.',
    'scope': 'The obsolete Base.AlarmClock noise device, distinct from Base.AlarmClock2 and digital watches.',
    'exclusions': 'No unconditional runtime availability, sound execution, exact delay/radius units or post-activation reuse guarantee.',
    'source_refs': ['scripts/newitems.txt', semantic.MENU, DEVICE_TIMER, DEVICE_PLACE, WORLD_MENU, DEVICE_TAKE],
}


RULES['ammo_strap_speed'] = {
    'positive': 'Exact AmmoStrap clothing forms and tags join setReloadSpeed primary-hand ammo matching and its 1.15 multiplication.',
    'scope': 'Base.AmmoStrap_Bullets and Base.AmmoStrap_Shells; reload, magazine and racking callers share the same primary-hand selection.',
    'exclusions': 'No guaranteed action duration, shotgun model-name classification or multiplication inferred from the inventory label.',
    'source_refs': ['scripts/clothing/clothing_others.txt', FIREARM, LOAD_MAGAZINE, INSERT_MAGAZINE, *RELOAD_ACTIONS],
}


RULES['vehicle_running_parts'] = {'positive': 'Exact vehicle-type declarations join four templates and actual installation/removal, wear, tire-pressure and server callbacks.',
                                'scope': 'brake, suspension, muffler and tire local consumers',
                                'exclusions': 'Native template expansion, traction/braking/sound/suspension effects and setter behavior are not inferred. Commented checks and unreachable post-return tire eligibility are excluded.'}
RULES['vehicle_panel_exchange'] = {
    'positive': 'Exact declared mechanical panel/window forms, template itemType leads and client FullType matching join the actual install/uninstall timed actions and server handlers.',
    'scope': 'Nine reviewed panel/glass families with VehicleType 1, 2 or 3; runtime compatibility remains an explicit condition.',
    'exclusions': 'No suffix-based proof of template expansion, guaranteed success, blanket skill gate or inferred walk/run interruption. Server uninstall uses its actual install-table skill and asymmetric failure branch.',
    'source_refs': ['scripts/vehicles/vehiclesitems.txt', *PANEL_TEMPLATES, VEHICLE_MECHANICS, VEHICLE_MENU,
                    VEHICLE_INSTALL, VEHICLE_UNINSTALL, VEHICLE_COMMANDS, VEHICLE_CALLBACKS],
}


RULES['vehicle_panel_controls'] = {
    'positive': 'The reviewed panel templates declare door or openable-window forms and use callbacks; actual menu, timed actions and server handlers change their open/lock states.',
    'scope': 'Installed compatible forms of the reviewed 27 panels; openable-window control is restricted to FrontWindow/RearWindow.',
    'exclusions': 'No protection/collision guarantee, fixed-windshield opening, unconditional unlock or unspecified walk/run cancellation.',
    'source_refs': [*PANEL_TEMPLATES, VEHICLE_USE_MENU, VEHICLE_MECHANICS, VEHICLE_MENU,
                    VEHICLE_COMMANDS, VEHICLE_CALLBACKS, *VEHICLE_DOOR_ACTIONS],
}


# These exact plain declarations were compared with the selected inventory and
# registered consumers. Literal uses outside acquisition lists are unrelated
# surname/debug strings, not item operations; fields and context remain checked.
RULES['washing_supplies'] = {
    'positive': 'Exact Soap2/CleaningLiquid2 inventory selection feeds the active body/equipment wash actions. Their actual soap-use loops, blood/dirt setters, water usage, makeup removal, wetness and time branches are interpreted. CleaningLiquid2 also reaches the conditional same-type consolidation action; Soap2 declares cantBeConsolided=TRUE and receives no positive consolidation claim.',
    'exclusions': 'Soap is not necessary for washing, dirt alone does not consume it, water can limit body coverage, and washing does not treat wounds or clean world blood.',
    'source_refs': [WORLD_MENU, WASH_BODY, WASH_CLOTHING, TAKE_WATER],
}
RULES['washing_target'] = {
    'positive': 'Exact Clothing/Weapon/Container declarations join the active manual-wash inventory categories and item-specific blood/dirt/hidden predicates. ISWashClothing requires water and changes blood, covered-part dirt and clothing wetness as represented.',
    'exclusions': 'No normal-item blanket washing, nonclothing dirt removal, durability repair, wound treatment or mandatory soap.',
    'source_refs': [WORLD_MENU, WASH_CLOTHING, TAKE_WATER],
}
RULES['welding_construction'] = {'positive': 'Seventeen exact active metal-welding menu callbacks join their learned group, numeric menu requirements, complete need:/use: declarations and existing construction classes. Named consumables and torch/mask equipment receive their actual material/tool roles.',
    'exclusions': 'The disableFurnaceAnvil branch does not establish furnace/anvil/drum construction. No generic metal ingredient, guaranteed equipment substitution, fixed finished-object performance or unconditional rod use.',
    'source_refs': [WELDING_MENU, semantic.BUILD_OBJECT, semantic.BUILD_ACTION, semantic.BUILD_UTIL]}


RULES['escape_rope'] = {'positive': 'Exact Rope/SheetRope and Nails selection in the active window/frame/hoppable menu joins transfer, count/type priority, timed actions and server add/remove dispatch; the installed-rope menu separately selects native ascent.',
    'exclusions': 'No mixed rope counts, guaranteed consumption/returned type/safe traversal, inferred hammer requirement or active descent dispatch. Callback validity does not invent a repeated nail check.',
    'source_refs': [WORLD_MENU, ADD_ROPE, REMOVE_ROPE, CLIMB_ROPE, OBJECT_COMMANDS]}
RULES['floor_glass'] = {'positive': 'Four exact BrokenGlass-tagged Moveable declarations retain the active world IsoBrokenGlass pickup consumer and its actual conditional hand injury setters, qualified by the placed sprite/object binding.',
    'exclusions': 'No glove requirement for menu admission, no active fingerless-glove exception, no window-frame equivalence or approach/foot injury inference; native sprite/returned-item identity remains bounded.',
    'source_refs': [WORLD_MENU, PICKUP_GLASS, WINDOW_GLASS, MOVE_TOOLS, semantic.PROPS]}
RULES['fabric_conditions'] = {
    'positive': 'Existing exact fabric-recovery material roles retain recipe eligibility, worn/unworn selection and the active Recipe.OnCreate.RipClothing callback branches. The four complete denim/leather recipes also establish the kept scissors-group tool role through the actual named/tag group consumer.',
    'exclusions': 'No use of the disabled legacy ripping menu, unconditional output, fixed yield or guaranteed thread. Native recipe participant ordering and output delivery remain separate.',
    'source_refs': [semantic.GROUPS, semantic.CLOTHING, semantic.CRAFT],
}
RULES['garment_patching'] = {
    'positive': 'The active inventory Inspect entry opens ISGarmentUI, whose displayed covered-part context invokes repairClothing/removePatch. Exact fabrics, thread and needle/tag selection join the real timed-action guards, consumption and addPatch/removePatch dispatch.',
    'exclusions': 'The commented legacy direct patch-menu call is not the active entry. No guaranteed full restoration, defense value or recovered fabric; no patching merely from a Clothing type without the represented coverage/fabric prerequisites.',
    'source_refs': [semantic.MENU, GARMENT_UI, PATCH_GARMENT, REMOVE_PATCH, semantic.CLOTHING],
}
RULES['item_map_controls'] = {
    'positive': 'Exact Map declarations select ISMap; the shared annotation editor changes symbols under actual implement/eraser predicates. Named Map tokens join exact LootMaps.Init registrations and revealKnownArea passes the initialized bounds to setKnownInSquares.',
    'exclusions': 'No automatic route finding, safe-route guarantee, physical visitation or initialized bounds for the generic Map with no declared map ID.',
    'source_refs': [semantic.MENU, MAP_VIEW, MAP_SYMBOLS, MAP_TEXT, MAP_DEFINITIONS],
}
RULES['spear_fishing'] = {
    'positive': 'Exact reviewed spear declarations with FishingSpear tags join inventory/water UI selection, native spear classification, no-lure equipment, catch selection and the spear-specific condition-loss branch.',
    'scope': 'The fourteen crafted and attachment-bearing spear forms under current migration review.',
    'exclusions': 'No unconditional native WeaponType mapping, guaranteed fish or rod-repair replacement for a broken spear.',
    'source_refs': ['scripts/items_weapons.txt', WORLD_MENU, FISHING_UI, FISHING_ACTION, FISHING_PROPERTIES],
}
RULES['spear_crafting'] = {
    'positive': 'Complete Create Spear and thirteen paired Attach/Reclaim recipe clauses identify exact material, cutting-tool, attachment and transformation-target roles. CreateSpear, UpgradeSpear and DismantleSpear callbacks are interpreted independently.',
    'scope': 'The 27 bound Base spear recipes and their exact admitted participants.',
    'exclusions': 'No keep-to-no-wear inference, guaranteed output durability, generic input-to-attachment rule or implicit result acquisition proof.',
    'source_refs': ['scripts/recipes.txt', semantic.GROUPS, semantic.CRAFT],
}


for _rule in ('water_consumers', 'crop_treatment', 'crop_spray_preparation'):
    RULES[_rule] = {'positive': 'Exact stable water/spray declarations join the actual menu, timed action and server consumer, preserving amount, validity, interruption and client/server differences.',
        'exclusions': 'No name-derived chemical, purification or safety effect, guaranteed full transfer/treatment, continuous guards absent in source, or atomic delivery.'}

RULES['key_lock_controls'] = {'positive': 'Exact Key declarations and actual world menu, padlock action, door action and code dialog bind conditional lock operations and asymmetric item creation/removal.',
    'exclusions': 'No inferred universal key compatibility, original padlock preservation, continuous validity recheck, guaranteed code input validation or native security outcome.'}


for _rule in ('camping_placement', 'camping_kit_preparation', 'shovel_smithing'):
    RULES[_rule] = {'positive': 'Exact declarations, complete recipe variants and active camping/building/timed-action/server consumers bind conditional functions and recipe-specific roles.',
                    'exclusions': 'No name-only legacy tent/flint alias, implicit import, generic kept-tool admission, atomic placement, preserved returned-kit state or guaranteed native outcome.'}


RULES['device_controls_extended'] = {'positive': 'Exact Radio fields and active registered panels, preset editor, timed device actions, Moveable radio branches and delivered-code handler bind their actual local guards and mutations.',
    'exclusions': 'No guaranteed native broadcast/recording assignment, audible output, returned item identity, arbitrary item-specific program code or atomic world placement.'}


for _rule in ('metal_forging', 'welded_parts', 'log_binding', 'mattress_preparation', 'frog_preparation', 'wire_recovery'):
    RULES[_rule] = {'positive': 'Complete exact reviewed recipe clauses bind each supplied or kept participant to its preparation context, with active action validity and actual named callback behavior.',
                    'exclusions': 'No recipe-name result inference, duplicate winner, implicit output identity, semicolon normalization, universal ingredient units or unconditional result delivery.'}

# Complete reviewed food and small wood preparation consumers.
RULES['food_preparation_recipes'] = {'positive': 'Complete exact preparation clauses and their named eligibility/result callbacks bind each actual ingredient, vessel and kept utensil separately.', 'exclusions': 'No output-as-input role, automatic cooking from category, recipe quantity normalization, invented Water participant, or freshness preservation absent a setter.'}


# Exact transformations and their independently reviewed callbacks.
RULES['item_transformation_recipes'] = {'positive': 'Complete literal recipe bodies and effective named callbacks bind actual roles and scoped conditions.', 'exclusions': 'No category/name inference of output behavior, generic keep-to-tool inference, overwritten callback revival or numerical normalization.'}

# Exact ammunition and physics-device declarations reviewed through their callers.
RULES['physics_device_controls'] = {'positive': 'Exact throwing declarations select actual attack request, positive timer and placement consumers separately.', 'exclusions': 'No declaration-based explosion/fire/noise/smoke/throw success, automatic placement for all variants or zero-damage negative claim.'}
RULES['ammunition_controls'] = {'positive': 'Exact ammunition identities bind the selected-ammunition menu and actual receiver loading consumers.', 'exclusions': 'No Count-to-stack guarantee, implicit .223 receiver, unbound global default or optional event success.'}

RULES['portable_light_controls'] = {'positive': 'Exact light declarations bind radial/key/menu activation and candle hand-change callers separately.', 'exclusions': 'No light-strength-to-illumination guarantee, uniform UI condition, original candle identity preservation or native charge-drain inference.'}
RULES['campfire_ignition'] = {'positive': 'Actual tinder/petrol/friction entry, timed action and server lighting predicates distinguish supplied roles and consumed objects.', 'exclusions': 'No tinder consumption attributed to igniter, guaranteed friction success, ignored unbound menu key or implicit fuel addition.'}

RULES['firearm_controls'] = {'positive': 'Exact ranged firearm declarations and complete selected-menu/radial/timed consumers bind ammunition, magazine, racking, firing-cycle and declared mode controls.', 'exclusions': 'No guaranteed hit/damage, constructor result, jam-free weapon, implicit continued possession guard or original magazine return.'}


RULES['legacy_firearm_controls'] = {'positive': 'Complete registered legacy manager, timed actions, base/shotgun/semi-auto/magazine class consumers establish conditional alternate loading and chamber manipulation for six exact type entries.', 'exclusions': 'No assumed new-reloading selector value, repaired global difficulty variable, guaranteed null-ammo lookup, modern/legacy hook ordering or original magazine identity return.'}

RULES['poultice_preparation'] = {'positive': 'Exact complete recipe clauses bind the named plant and kept group tool, with both hidden wild-garlic variants retained and the active crafting UI hidden filter interpreted.', 'exclusions': 'No duplicate winner, native hidden-flag case normalization, alternate entry eligibility or raw-plant medical action inference.'}
for _rule in ('appearance_actions', 'medical_action_outcomes'):
    RULES[_rule] = {'positive': 'Exact declaration selectors join the active character/inventory/health menus and actual appearance or medical consumers, retaining separate selection, action-validity and completion behavior.',
                    'exclusions': 'No display-name-only care effect, assumed consumption, guaranteed native visual/clinical outcome, or invented continuing eligibility check.'}


RULES['vegetation_tools'] = {'positive': 'Exact Weapon category/tag selects the reviewed world-menu, cursor and action paths; the actual plant server command and tree animation boundary remain attached.', 'exclusions': 'No grass-tool requirement, guaranteed loot, felling rate or native attack-result inference.', 'source_refs': [WORLD_MENU, CHOP, CHOP_CURSOR, PLANT_CURSOR, REMOVE_BUSH, OBJECT_COMMANDS, semantic.BUILD_OBJECT]}
RULES['barricade_controls'] = {'positive': 'Exact Hammer/RemoveBarricade tags or exact BlowTorch and materials join the separate menu, action and server branches with native result boundaries.', 'exclusions': 'CanBarricade is not substituted for Hammer tag; no metal mask/skill prerequisite, full salvage or atomic delivery is invented.', 'source_refs': [WORLD_MENU, BARRICADE, UNBARRICADE, OBJECT_COMMANDS]}
RULES['meal_utensils'] = {'positive': 'Exact Spoon/Fork tag or type joins ISEatFoodAction.start optional hand-model selection and its food-type priorities.', 'exclusions': 'No utensil requirement, eating benefit, consumption or real hand-equipment inference.', 'source_refs': [semantic.EAT]}
RULES['structure_destruction'] = {'positive': 'Exact Sledgehammer/Sledgehammer2 joins the active construction menu, object-selection cursor and destruction action with its actual grouped-object helpers.', 'exclusions': 'Inactive legacy dismantle menu is not an entry point; native delivery and source failure branches remain explicit.', 'source_refs': [semantic.BUILD, WORLD_MENU, DESTROY_CURSOR, DESTROY_ACTION, semantic.BUILD_UTIL, semantic.BUILD_OBJECT, OBJECT_COMMANDS]}


RULES['electrical_controls'] = {'positive': 'Exact complete light-bulb, Battery, CarBattery1/2/3, charger, generator and scrap declarations join their reviewed inventory/world/vehicle menus, actions and server handlers. Runtime installed-part/object binding remains explicit.',
    'exclusions': 'No charging from the unused old recharge class, generic colored-bulb vehicle compatibility, guaranteed native power/illumination, full generator repair or normalization of written charge/fuel arithmetic.',
    'source_refs': [*ELECTRICAL_SOURCES, semantic.MENU, WORLD_MENU, OBJECT_COMMANDS, semantic.PROPS,
        VEHICLE_MECHANICS, VEHICLE_MENU, VEHICLE_INSTALL, VEHICLE_UNINSTALL, VEHICLE_CALLBACKS, VEHICLE_COMMANDS,
        VEHICLE_START, semantic.BUILD, semantic.TRANSFER, DROP_OBJECT]}


RULES['ground_tools'] = {'positive': 'Exact DigPlow/TakeDirt/DigGrave declarations join selected farming, terrain and grave consumers with separate ongoing/server predicates.',
    'exclusions': 'No harvest, growth, guaranteed worm, both-square history guard or continuing tool recheck.',
    'source_refs': [FARM_MENU, PLOW_CURSOR, PLOW_ACTION, SHOVEL_PLANT, FARM_CLIENT, FARM_SYSTEM, FARM_COMMANDS, PLANT,
        WORLD_MENU, GRAVE_CURSOR, GRAVE_FILL, semantic.BUILD_OBJECT, semantic.BUILD_ACTION, semantic.BUILD_UTIL,
        GROUND_MENU, GROUND_CURSOR, SHOVEL_GROUND, OBJECT_COMMANDS]}
RULES['thumpable_tools'] = {'positive': 'Actual movable fallback, cursor and action bind Saw/Screwdriver to dismantlable thumpables; held stone-hammer wear is separately bound.',
    'exclusions': 'No inactive menu, arbitrary movable capability or displayed chance as execution.',
    'source_refs': [MOVE_CURSOR, semantic.PROPS, semantic.MOVE_ACTION, WORLD_MENU, semantic.BUILD_UTIL, OBJECT_COMMANDS, semantic.BUILD_ACTION]}
RULES['net_controls'] = {'positive': 'Exact net joins registered menu, class Type, cursor and actual check/remove functions, including timestamps and failures.',
    'exclusions': 'No guaranteed catch, individual-net timestamp, atomic return or invented continuing distance guard.',
    'source_refs': [WORLD_MENU, NET_OBJECT, NET_CHECK, semantic.BUILD_OBJECT, BASE_OBJECT]}


RULES['heat_controls'] = {'positive': 'Exact item/tag or the actual camping type/category tables join the reviewed menu, action and server branches. World-only drum behavior does not imply a carried MetalDrum binding.',
    'exclusions': 'No corrected Lua arithmetic, guaranteed ignition/heat, atomic transfer, disabled construction entry or invented consumption.',
    'source_refs': [*HEAT_SOURCES, CAMP_FUEL, CAMP_MENU, CAMP_PETROL_LIGHT, CAMP_CLIENT, CAMP_SERVER, CAMP_COMMANDS,
                    WORLD_MENU, OBJECT_COMMANDS, VEHICLE_USE_MENU, VEHICLE_MENU, VEHICLE_COMMANDS, *VEHICLE_FUEL_ACTIONS,
                    *GENERATOR_ACTIONS, semantic.PROPS]}


RULES['equipment_controls'] = {'positive': 'Exact reviewed declarations join actual trap, fishing, vehicle, weapon, plaster and compost dispatch through the referenced menu/action/server sources.',
    'exclusions': 'No discarded source branches, invented interruption guards, guaranteed native outcome or output-to-input role reversal.',
    'source_refs': [*CONTROL_SOURCES, TRAP_MENU, TRAP_OBJECT, TRAP_SYSTEM, TRAP_COMMANDS, TRAP_CLIENT, TRAP_CLIENT_OBJECT,
        TRAP_BUILD, TRAP_DEFINITIONS, TRAP_BAIT, FISHING_UI, FISHING_ACTION, FISHING_PROPERTIES,
        WORLD_MENU, VEHICLE_MENU, VEHICLE_USE_MENU, VEHICLE_MECHANICS, VEHICLE_CALLBACKS, VEHICLE_COMMANDS,
        VEHICLE_INSTALL, VEHICLE_UNINSTALL, semantic.MENU, WEAPON_UPGRADE, WEAPON_REMOVAL, PAINT_MENU,
        PAINT_CURSOR, semantic.BUILD_OBJECT, OBJECT_COMMANDS, BLACKSMITH_MENU]}


def extend(base, builder):
    inputs = base['reader']
    sources = (*CONTROL_SOURCES, *HEAT_SOURCES, PLOW_CURSOR, PLOW_ACTION, SHOVEL_PLANT, GRAVE_CURSOR, GRAVE_FILL, NET_OBJECT, NET_CHECK, BASE_OBJECT,
               CRAFT_UI, PAINT_MENU, PAINT_CURSOR, PAINT_ACTION, SIGN_ACTION, MOVE_CURSOR,
               RADIO_VOLUME, RADIO_PANEL, RADIO_WINDOW, RADIO_ACTION,
               CLOCK_PROMPT, CLOCK_CHARACTER,
               CLEAN_BLOOD, CLEAN_CURSOR,
               CLOTHING_EXTRA,
               HOTBAR, HOTBAR_SLOTS, HOTBAR_ATTACH, LEGACY_MEDIA_MENU, LEGACY_RELOAD, TUTORIAL_MENU, PLACE_OBJECT, DROP_OBJECT, WASH_BODY, WASH_CLOTHING, GARMENT_UI, PATCH_GARMENT, REMOVE_PATCH,
               DRY_BODY, CLEAR_ASHES, PICKUP_GLASS, WINDOW_GLASS, MOVE_TOOLS, ADD_ROPE, REMOVE_ROPE, CLIMB_ROPE, WELDING_MENU,
               FIRE_FIGHTING, EXTINGUISH_CURSOR, PUT_OUT_FIRE, GROUND_MENU, GROUND_CURSOR, SHOVEL_GROUND, NATURAL_FLOOR, DUMP_CONTENTS, DUMP_WATER,
               NAME_DIALOG,
               CONSOLIDATE, DEVICE_TIMER, DEVICE_PLACE, DEVICE_TAKE, *RELOAD_ACTIONS,
               VEHICLE_MECHANICS, VEHICLE_MENU, VEHICLE_INSTALL, VEHICLE_UNINSTALL,
               VEHICLE_COMMANDS, VEHICLE_CALLBACKS, *PANEL_TEMPLATES, *VEHICLE_STORAGE_SOURCES, INVENTORY_PAGE, *VEHICLE_FUEL_ACTIONS,
               VEHICLE_SEAT_UI, *VEHICLE_SEAT_ACTIONS, *VEHICLE_RUNNING_TEMPLATES, *TIRE_ACTIONS,
               VEHICLE_USE_MENU, *VEHICLE_DOOR_ACTIONS,
               CONTEXT_MANAGER, CONTEXT_INVENTORY, CONTEXT_LOADER, CONTEXT_ELEMENT, CONTEXT_RADIO,
               CONTEXT_MOVABLE, CONTEXT_MEDIA, CONTEXT_DELETE, MEDIA_INFO, MEDIA_LOADER, MEDIA_DATA,
               RADIO_CHANNEL, TV_CHANNEL, RADIO_MEDIA, RADIO_SIGNAL, RADIO_MIC, RADIO_INTERACTIONS, RADIO_POWER, RADIO_GRID, RADIO_PRESET_EDITOR, RADIO_GENERAL, semantic.DYE, HAIR_CUT, BEARD_TRIM,
               semantic.PROPS, semantic.MOVE, semantic.MOVE_ACTION, semantic.CRAFT, semantic.GROUPS, semantic.CLOTHING, semantic.FIX, semantic.BUILD, semantic.STAGE,
               FIREARM, FIREARM_RADIAL, LIGHT_RADIAL, LIGHT_BINDING, CAMP_PETROL_LIGHT, CAMP_KINDLE_LIGHT, *LEGACY_RELOAD_SOURCES, WORLD_MENU, PADLOCK_ACTION, DOOR_LOCK, DIGITAL_CODE, VEHICLE_START, VEHICLE_DASHBOARD,
               TRANSFER_WATER, ADD_WATER, WATER_PLANT, WASH_VEHICLE, CURE_MILDEW, CURE_FLIES, semantic.DRINK,
               OBJECT_COMMANDS, PLUMB_ACTION, *FITNESS_SOURCES, CHOP, CHOP_CURSOR, PLANT_CURSOR, REMOVE_BUSH,
               BARRICADE, UNBARRICADE, DESTROY_CURSOR, DESTROY_ACTION, *ELECTRICAL_SOURCES,
               semantic.MENU, semantic.EAT, semantic.WEAR, BODY_LOCATIONS,
               LOAD_MAGAZINE, INSERT_MAGAZINE, WEAPON_UPGRADE, WEAPON_REMOVAL, MAP_VIEW, MAP_SYMBOLS, MAP_TEXT, MAP_DEFINITIONS, NOTE_EDITOR, MAKEUP_UI, MAKEUP_DEFINITIONS, ALARM_DIALOG, ALARM_STOP, semantic.READ, semantic.SKILLS, semantic.TRANSFER, TAKE_WATER,
               HEALTH, DISINFECT, SPLINT, STITCH, CLEAN_BURN, CLEAN_BANDAGE, semantic.PILLS, REMOVE_GLASS, REMOVE_BULLET, semantic.BANDAGE, semantic.COOK,
               FARM_MENU, SEED_ACTION, FERTILIZE_ACTION, FARM_CLIENT, FARM_SYSTEM, FARM_COMMANDS, PLANT, SEED_DEFINITIONS,
               CAMP_MENU, CAMP_FUEL, CAMP_ADD, CAMP_LIGHT, CAMP_CLIENT, CAMP_SERVER, CAMP_COMMANDS, CAMP_OBJECT, *CAMP_PLACEMENT_SOURCES,
               FISHING_UI, FISHING_ACTION, FISHING_PROPERTIES,
               TRAP_MENU, TRAP_BUILD, TRAP_DEFINITIONS, TRAP_CLIENT, TRAP_CLIENT_OBJECT, TRAP_SYSTEM, TRAP_OBJECT, TRAP_BAIT, TRAP_COMMANDS,
               semantic.BUILD_OBJECT, semantic.BUILD_ACTION, semantic.BUILD_UTIL, *sorted(BUILD_CLASSES.values()), *POULTICES.values())
    texts = {p: inputs.read(p).decode('utf-8-sig') for p in sources}
    builder.sources.update({p: inputs.bindings[p]['sha256'] for p in sources})
    refs = {p: builder.observe(p, 'source consumer functions', {'source_text': texts[p]}) for p in sources}
    base['inventory_context_sources'] = {p: refs[p] for p in (CONTEXT_MANAGER, CONTEXT_INVENTORY, CONTEXT_LOADER,
        CONTEXT_ELEMENT, CONTEXT_RADIO, CONTEXT_MOVABLE, CONTEXT_MEDIA, CONTEXT_DELETE)}
    media_categories = set(re.findall(r'^\s*category\s*=\s*"([^"]+)"', reader.mask(texts[MEDIA_DATA], lua=True), re.M))
    slot_text = reader.mask(texts[HOTBAR_SLOTS], lua=True)
    registered_slots = set()
    for variable, body in re.findall(r'local\s+(\w+)\s*=\s*\{(.*?)\n\}', slot_text, re.S):
        slot_types = re.findall(r'\btype\s*=\s*"([^"]+)"', body)
        if (len(slot_types) == 1 and 'attachments' in body
                and re.search(r'table\.insert\(ISHotbarAttachDefinition,\s*' + re.escape(variable) + r'\)', slot_text)):
            registered_slots.add(slot_types[0])
    declarations = defaultdict(list)
    recipes = []
    evolved = []
    fixings = []
    imports = defaultdict(list)
    for ref in base['semantic']['source_bindings']:
        if not ref['path'].startswith('scripts/'):
            continue
        script_text = inputs.read(ref['path'], ref['sha256']).decode('utf-8-sig')
        for header in module_imports(script_text, ref['path']):
            imports[header['module']].append(header)
        for record in reader.declarations(script_text, ref['path']):
            if record['kind'] == 'item':
                declarations[record['module'] + '.' + record['name']].append(record)
            elif record['kind'] == 'recipe':
                recipes.append(record)
            elif record['kind'] == 'evolvedrecipe':
                evolved.append(record)
            elif record['kind'] == 'fixing':
                fixings.append(record)
    targets = set(base['semantic']['target_ids'])
    base['declarations'] = declarations
    property_readings = {item: stable_properties(rows[0]) for item, rows in declarations.items() if len(rows) == 1}
    fields = {item: pair[0] for item, pair in property_readings.items()}
    for record in recipes:
        headers = imports.get(record['module'], [])
        if headers and len({tuple(h['imports']) for h in headers}) == 1:
            record['module_imports'] = headers
            record['ambiguous_item_ids'] = sorted(item for item, rows in declarations.items() if len(rows) != 1)
    trap_text = reader.mask(texts[TRAP_DEFINITIONS], lua=True)
    trap_types = defaultdict(list)
    for variable in re.findall(r'table.insert\(Traps,\s*(\w+)\)', trap_text):
        types = re.findall(r'\b' + re.escape(variable) + r'\.type\s*=\s*"([^"]+)"', trap_text)
        if len(types) == 1:
            trap_types[types[0]].append(variable)
    animal_variables = set(re.findall(r'table.insert\(Animals,\s*(\w+)\)', trap_text))
    animal_inputs = {}
    for variable in animal_variables:
        scalar = lambda field: re.findall(r'\b' + re.escape(variable) + r'\.' + field + r'\s*=\s*(\d+)\s*;', trap_text)
        hours = (scalar('minHour'), scalar('maxHour'))
        if not all(len(values) == 1 for values in hours):
            continue
        animal_inputs[variable] = {'hours': tuple(int(v[0]) for v in hours)}
        for field in ('traps', 'baits'):
            animal_inputs[variable][field] = {fulltype for fulltype, weight in re.findall(
                r'\b' + re.escape(variable) + r'\.' + field + r'\["([^"]+)"\]\s*=\s*(\d+)', trap_text) if int(weight) > 0}
    catching_types = {fulltype for variable, fulltype, weight in re.findall(r'(\w+)\.traps\["([^"]+)"\]\s*=\s*([0-9]+)', trap_text)
                      if variable in animal_variables and int(weight) > 0}
    fishing_text = reader.mask(texts[FISHING_PROPERTIES], lua=True)
    fish_lures = {}
    for variable in re.findall(r'table.insert\(fishes,\s*(\w+)\)', fishing_text):
        names = re.findall(r'\b' + re.escape(variable) + r'\.item\s*=\s*"([^"]+)"', fishing_text)
        if len(names) == 1:
            fish_lures[names[0]] = set(re.findall(r'table.insert\(' + re.escape(variable) + r'\.lure,\s*"([^"]+)"\)', fishing_text))
    registered_lures = set(re.findall(r'lure\["([^"]+)"\]\s*=\s*\w+\s*;', fishing_text))
    extra_lures = re.search(r'local lureItems\s*=\s*\{([^}]+)\}', fishing_text)
    if extra_lures and 'lure[itemType] = lure2' in fishing_text and 'table.insert(fish.lure, itemType)' in fishing_text:
        registered_lures.update(re.findall(r'"([^"]+)"', extra_lures.group(1)))
    camp_tables = {}
    camp_text = reader.mask(texts[CAMP_FUEL], lua=True)
    for name in ('campingFuelType', 'campingFuelCategory', 'campingLightFireType', 'campingLightFireCategory'):
        tables = re.findall(r'^' + name + r'\s*=\s*\{(.*?)\}', camp_text, re.M | re.S)
        inv.require(len(tables) == 1, 'ambiguous campfire fuel table')
        values = {}
        for key, amount in re.findall(r'^\s*(\w+)\s*=\s*(\d+(?:\.\d+)?(?:/\d+(?:\.\d+)?)?)\s*,?', tables[0], re.M):
            number = amount.split('/')
            values[key] = float(number[0]) / (float(number[1]) if len(number) == 2 else 1)
        camp_tables[name] = values
    ammo_receivers, magazine_receivers = defaultdict(list), defaultdict(list)
    for receiver, f in fields.items():
        for property_name, table in (('AmmoType', ammo_receivers), ('MagazineType', magazine_receivers)):
            token = f.get(property_name)
            if token and re.fullmatch(r'[A-Za-z0-9_.]+', token):
                table[reader.qualify(receiver.split('.', 1)[0], token)].append(receiver)
    existing_functions = {(f['item_id'], f['payload'].get('function')) for f in base['semantic']['facts']
                          if f['fact_kind'] == 'direct_function'}
    original_functions = {(f['item_id'], f['payload']['function']): f for f in base['semantic']['facts']
                          if f['fact_kind'] == 'direct_function'}
    decl_refs = {}

    def declaration(item):
        if item not in decl_refs:
            r = declarations[item][0]
            decl_refs[item] = builder.observe(r['path'], f"L{r['line']}-L{r['end_line']}:{item}",
                                             {'raw': r['raw'], 'clauses': r['clauses'], 'property_conflicts': property_readings[item][1]})
        return decl_refs[item]

    def function(item, name, predicate, rule, evidence, scopes=None):
        scopes = scopes or ['item:direct']
        fid = builder.fact(item, 'direct_function', {'function': name}, evidence, rule, scopes)
        builder.fact(item, 'condition', {'predicate': predicate}, evidence, rule, scopes, applies_to_fact_refs=[fid])
        return fid

    # Active source participation can recover an omitted instance of the same
    # world-work definition; unrelated or inactive factories do not open it.
    base['factory_relations'] = defaultdict(list)
    build_text = reader.mask(texts[semantic.BUILD], lua=True)
    active_factories = set(re.findall(r':addOption\([^\n]*,\s*ISBuildMenu\.(\w+)\s*[,)]', build_text))
    factory_bodies = {m[1]: m[0] for m in re.finditer(
        r'^ISBuildMenu\.(on\w+)\s*=\s*function\b.*?(?=^ISBuildMenu\.|\Z)', build_text, re.M | re.S)}
    world_items = {r['item_id'] for r in base['semantic']['results'] if r['scope_ref'] == 'activity:world_work'}
    recovered_world = defaultdict(list)
    for attempt in base['semantic']['attempts'].values():
        item = attempt['item_id']
        if attempt['route'] != 'D' or item not in fields:
            continue
        for old_ref in attempt['finding']['building_candidates']:
            observation = base['semantic']['observations'][old_ref]
            name = observation['content']['factory'].removeprefix('ISBuildMenu.')
            body = factory_bodies.get(name)
            if not body:
                continue
            if name in INACTIVE_BUILD_FACTORIES and name not in active_factories:
                base['factory_relations'][item].append({'factory': name, 'observation_ref': old_ref,
                    'status': 'no_active_menu_reference', 'source_ref': inputs.bindings[semantic.BUILD],
                    'reason': 'The function exists, but the supplied menu has no active addOption reference to it. This is a local menu-reachability disposition, not a global runtime absence claim.'})
                continue
            class_name = BUILD_FACTORIES.get(name)
            if name not in active_factories or class_name is None or class_name + ':new(' not in body:
                continue
            requirement = re.search(r'\["need:' + re.escape(item) + r'"\]\s*=\s*"([1-9][0-9]*)"', body)
            if not requirement:
                continue
            path = BUILD_CLASSES[class_name]
            inv.require('buildUtil.consumeMaterial(self)' in texts[path], 'carpentry material consumer changed')
            ref = builder.observe(semantic.BUILD, 'active factory:' + name,
                                  {'factory': name, 'body': body, 'required_item': item, 'count': int(requirement[1]),
                                   'constructor': class_name, 'consumer': path})
            evidence = [declaration(item), ref, refs[path], refs[semantic.BUILD], refs[semantic.BUILD_OBJECT],
                        refs[semantic.BUILD_ACTION], refs[semantic.BUILD_UTIL]]
            context = builder.fact(item, 'use_context', {'activity': 'carpentry_menu_construction'}, evidence,
                                   'carpentry_material', ['activity:world_work'])
            role = builder.fact(item, 'context_role', {'role': 'material'}, evidence,
                                'carpentry_material', ['activity:world_work'], context_fact_ref=context)
            builder.fact(item, 'condition', {'predicate': CARPENTRY_MATERIAL}, evidence,
                         'carpentry_material', ['activity:world_work'], applies_to_fact_refs=[context, role])
            base['factory_relations'][item].append({'factory': name, 'observation_ref': old_ref,
                'status': 'active_material', 'constructor': class_name, 'role_fact_ref': role,
                'source_ref': inputs.bindings[path], 'count': int(requirement[1])})
            if item not in world_items:
                recovered_world[item].append({'item_id': item, 'factory': name, 'role': 'material',
                    'count': int(requirement[1]), 'observation_ref': ref, 'previous_observation_ref': old_ref,
                    'role_fact_ref': role, 'evidence_refs': sorted(set(evidence)),
                    'omission_reason': 'The historical world-work opener used a fixed construction-material list despite this route D active factory need: observation.'})
    for item, links in welding_roles(base, builder, fields, targets, declaration, refs, texts).items():
        recovered_world[item].extend(links)
    base['recovered_world_participation'] = dict(recovered_world)
    base['world_participation_provenance'] = {
        item: builder.explain(item, 'investigation', sorted({r for p in links for r in p['evidence_refs']}),
            'Same-definition world-work participation from an active menu factory and exact need:/use:/equipment inputs; question-local conditions and outcome remain separate.')
        for item, links in recovered_world.items()}

    inv.require('item:getWorldSprite()' in texts[MOVE_CURSOR] and 'moveProps.isMoveable' in texts[MOVE_CURSOR]
                and 'placeMoveableViaCursor' in texts[semantic.MOVE_ACTION], 'placement consumer changed')
    paint_types = set(re.findall(r'paint\s*=\s*"([^"]+)"', texts[PAINT_MENU]))
    body_locations = set(re.findall(r'^group:getOrCreateLocation\("([^"]+)"\)', texts[BODY_LOCATIONS], re.M))
    seed_pairs = re.findall(r'farming_vegetableconf\.props\["([^"]+)"\]\.seedName\s*=\s*"([^"]+)"', texts[SEED_DEFINITIONS])
    seed_forms = {item: kind for kind, item in seed_pairs if sum(i == item for _, i in seed_pairs) == 1}
    seed_counts = {}
    for item, kind in seed_forms.items():
        counts = re.findall(r'farming_vegetableconf\.props\["' + re.escape(kind) + r'"\]\.seedsRequired\s*=\s*(\d+)', texts[SEED_DEFINITIONS])
        inv.require(len(counts) == 1 and int(counts[0]) in SOW_COUNTS, 'unsupported seed quantity')
        seed_counts[item] = int(counts[0])
    seed_evidence = [refs[p] for p in (FARM_MENU, SEED_ACTION, FARM_COMMANDS, PLANT, SEED_DEFINITIONS)]
    base['seed_sources'] = {item: {'crop': crop, 'required_count': seed_counts[item], 'observation_refs': seed_evidence}
                            for item, crop in seed_forms.items()}
    base['unsupported_wear'] = {}
    base['moveable_tool_relations'] = defaultdict(list)
    move_text = reader.mask(texts[semantic.MOVE], lua=True)
    aliases = dict(re.findall(r'\["([^"]+)"\]\s*=\s*"([^"]+)"', move_text.split('function ISMoveableDefinitions:getInstance')[0]))
    tool_definitions = re.findall(r'moveableDefinitions\.addToolDefinition\(\s*"([^"]+)"\s*,\s*\{([^}]+)\}', move_text)
    moving_contexts = {f['item_id']: f['fact_id'] for f in base['semantic']['facts']
                       if f['payload'] == {'activity': 'moving_furniture'}}
    moving_roles = {f['item_id'] for f in base['semantic']['facts'] if f['fact_kind'] == 'context_role'
                    and f['payload'] == {'role': 'tool'} and f.get('context_fact_ref') in moving_contexts.values()}
    for item in sorted(targets & fields.keys()):
        for name, values in tool_definitions:
            for token in re.findall(r'"([^"]+)"', values):
                if ((token in aliases and aliases[token] in fields[item].get('Tags', '').split(';'))
                        or (token not in aliases and token == item)):
                    base['moveable_tool_relations'][item].append({'definition': name, 'token': token, 'tag': aliases.get(token)})
        if base['moveable_tool_relations'][item] and item not in moving_roles:
            evidence = [declaration(item), refs[semantic.MOVE], refs[semantic.PROPS], refs[semantic.MOVE_ACTION]]
            context = moving_contexts.get(item)
            if context is None:
                context = builder.fact(item, 'use_context', {'activity': 'moving_furniture'}, evidence,
                                       'moving_role_recovery', ['activity:world_work'])
            role = builder.fact(item, 'context_role', {'role': 'tool'}, evidence,
                                'moving_role_recovery', ['activity:world_work'], context_fact_ref=context)
            builder.fact(item, 'condition', {'predicate': 'The object requests this tool; inventory, reachability, world object and multiplayer permission checks must hold.'},
                         evidence, 'moving_role_recovery', ['activity:world_work'], applies_to_fact_refs=[context, role])
    original_repair_contexts = {f['item_id']: f['fact_id'] for f in base['semantic']['facts']
                               if f['payload'] == {'activity': 'repair'}}
    original_repair_roles = {(f['item_id'], f['payload'].get('role')) for f in base['semantic']['facts']
                            if f['fact_kind'] == 'context_role' and f['item_id'] in original_repair_contexts}
    fixing_counts = defaultdict(int)
    for record in fixings:
        fixing_counts[record['module'], record['name']] += 1
    for record in fixings:
        if fixing_counts[record['module'], record['name']] != 1:
            continue
        props = reader.properties(record, ':')
        for role, key in (('repair_target', 'Require'), ('repair_material', 'Fixer')):
            for value in props.get(key, []):
                tokens = value.split(';') if key == 'Require' else [value.split(';', 1)[0].split('=', 1)[0]]
                for token in tokens:
                    if not re.fullmatch(r'[A-Za-z0-9_.]+', token.strip()):
                        continue
                    item = reader.qualify(record['module'], token.strip())
                    if item not in targets or item not in fields or (item, role) in original_repair_roles:
                        continue
                    ref = builder.observe(record['path'], f"L{record['line']}-L{record['end_line']}:{record['name']}",
                                          {'raw': record['raw'], 'clauses': record['clauses']})
                    evidence = [declaration(item), ref, refs[semantic.MENU], refs[semantic.FIX]]
                    context = original_repair_contexts.get(item)
                    if context is None:
                        context = builder.fact(item, 'use_context', {'activity': 'repair'}, evidence,
                                               'fixing_role_recovery', ['activity:world_work'])
                    role_ref = builder.fact(item, 'context_role', {'role': role}, evidence,
                                            'fixing_role_recovery', ['activity:world_work'], context_fact_ref=context)
                    builder.fact(item, 'condition', {'predicate': FIXING_ACTION}, evidence,
                                 'fixing_role_recovery', ['activity:world_work'], applies_to_fact_refs=[context, role_ref])
    base['cooking_base_relations'] = defaultdict(list)
    evolved_counts = defaultdict(int)
    for record in evolved:
        evolved_counts[record['module'], record['name']] += 1
    apple_names = {entry.split(':', 1)[0] for entry in fields.get('Base.Apple', {}).get('EvolvedRecipe', '').split(';')}
    base['apple_recipe_relations'] = {
        r['name']: {'path': r['path'], 'line': r['line'], 'clauses': r['clauses'],
                    'observation_ref': builder.observe(r['path'], f"L{r['line']}-L{r['end_line']}:{r['name']}", {'raw': r['raw'], 'clauses': r['clauses']})}
        for r in evolved if r['name'] in apple_names and evolved_counts[r['module'], r['name']] == 1}
    original_food_contexts = {f['item_id']: f['fact_id'] for f in base['semantic']['facts']
                             if f['payload'] == {'activity': 'food_preparation'}}
    original_ingredients = {f['item_id'] for f in base['semantic']['facts']
                            if f['fact_kind'] == 'context_role' and f['payload'] == {'role': 'ingredient'}}
    for item in sorted((targets & fields.keys()) - original_ingredients):
        entries = fields[item].get('EvolvedRecipe')
        if not entries or 'EvolvedRecipe' in property_readings[item][1]:
            continue
        names = [entry.split(':', 1)[0].strip() for entry in entries.split(';')]
        records = [r for r in evolved if r['name'] in names and evolved_counts[r['module'], r['name']] == 1]
        if len(records) != len(set(names)):
            continue
        evidence = [declaration(item), refs[semantic.MENU], refs[semantic.COOK]]
        for r in records:
            evidence.append(builder.observe(r['path'], f"L{r['line']}-L{r['end_line']}:{r['name']}",
                                            {'raw': r['raw'], 'clauses': r['clauses']}))
        context = original_food_contexts.get(item)
        if context is None:
            context = builder.fact(item, 'use_context', {'activity': 'food_preparation'}, evidence,
                                   'cooking_ingredient_recovery', ['activity:cooking'])
        role = builder.fact(item, 'context_role', {'role': 'ingredient'}, evidence,
                            'cooking_ingredient_recovery', ['activity:cooking'], context_fact_ref=context)
        builder.fact(item, 'condition', {'predicate': COOKING_ACTION}, evidence,
                     'cooking_ingredient_recovery', ['activity:cooking'], applies_to_fact_refs=[context, role])
    for record in evolved:
        if evolved_counts[record['module'], record['name']] != 1:
            continue
        props = reader.properties(record, ':')
        if len(props.get('BaseItem', [])) != 1 or len(props.get('ResultItem', [])) != 1:
            continue
        for field in ('BaseItem', 'ResultItem'):
            item = reader.qualify(record['module'], props[field][0])
            if item not in targets or item not in fields:
                continue
            ref = builder.observe(record['path'], f"L{record['line']}-L{record['end_line']}:{record['name']}",
                                  {'raw': record['raw'], 'clauses': record['clauses']})
            builder.activity(item, 'food_ingredient_addition', 'base',
                             [declaration(item), ref, refs[semantic.MENU], refs[semantic.COOK]],
                             'cooking_base', ['activity:cooking'], COOKING_BASE)
            base['cooking_base_relations'][item].append({'field': field, 'recipe': record['name'],
                                                        'path': record['path'], 'clauses': record['clauses']})
    for item in sorted(targets & fields.keys()):
        f = fields[item]
        patch_evidence = [declaration(item), *(refs[p] for p in (semantic.MENU, GARMENT_UI, PATCH_GARMENT, REMOVE_PATCH, semantic.CLOTHING))]
        if f.get('Type') == 'Clothing' and f.get('BloodLocation') and not {'Type', 'BloodLocation', 'FabricType'} & property_readings[item][1].keys():
            function(item, 'remove_garment_patch', GARMENT_PATCH_REMOVAL, 'garment_patching', patch_evidence)
            if f.get('FabricType'):
                function(item, 'receive_garment_patch', GARMENT_PATCHING, 'garment_patching', patch_evidence)
        sewing_needle = item == 'Base.Needle' or ('SewingNeedle' in f.get('Tags', '').split(';') and 'Tags' not in property_readings[item][1])
        if sewing_needle or item in {'Base.Thread', 'Base.RippedSheets', 'Base.DenimStrips', 'Base.LeatherStrips'}:
            function(item, 'apply_garment_patch', GARMENT_PATCHING, 'garment_patching', patch_evidence)
        if sewing_needle:
            function(item, 'unpick_garment_patch', GARMENT_PATCH_REMOVAL, 'garment_patching', patch_evidence)
        if f.get('Type') in {'Clothing', 'Weapon', 'Container'} and 'Type' not in property_readings[item][1]:
            wash_evidence = [declaration(item), *(refs[p] for p in (WORLD_MENU, WASH_CLOTHING, TAKE_WATER))]
            function(item, 'wash_carried_equipment', WASH_TARGET, 'washing_target', wash_evidence)
            changes = [('item_surface_blood', 'remove_by_washing')]
            if f['Type'] == 'Clothing':
                changes.extend([('clothing_surface_dirt', 'remove_by_washing'), ('clothing_wetness', 'set_100_by_washing')])
            for prop, direction in changes:
                effect = builder.fact(item, 'effect', {'property': prop, 'direction': direction}, wash_evidence,
                                      'washing_target', ['item:direct'])
                builder.fact(item, 'condition', {'predicate': WASH_TARGET}, wash_evidence, 'washing_target',
                             ['item:direct'], applies_to_fact_refs=[effect])
        if item in {'Base.Soap2', 'Base.CleaningLiquid2'} and f.get('Type') == 'Drainable':
            washing_evidence = [declaration(item), *(refs[p] for p in (WORLD_MENU, WASH_BODY, WASH_CLOTHING, TAKE_WATER))]
            function(item, 'wash_body', BODY_WASHING, 'washing_supplies', washing_evidence)
            function(item, 'wash_equipment', EQUIPMENT_WASHING, 'washing_supplies', washing_evidence)
            if item == 'Base.CleaningLiquid2':
                function(item, 'consolidate_drainable_supplies', MEDICAL_CONSOLIDATION, 'washing_supplies',
                         [declaration(item), refs[semantic.MENU], refs[CONSOLIDATE]])
            for prop in ('washed_surface_blood', 'washed_surface_dirt'):
                effect = builder.fact(item, 'effect', {'property': prop, 'direction': 'remove'}, washing_evidence,
                                      'washing_supplies', ['item:direct'])
                builder.fact(item, 'condition', {'predicate': WASHING_OUTCOME}, washing_evidence,
                             'washing_supplies', ['item:direct'], applies_to_fact_refs=[effect])
        if item in {'Base.Headphones', 'Base.Earbuds'}:
            function(item, 'connect_radio_headphones', HEADPHONE_CONNECTION, 'radio_headphones',
                     [declaration(item), *(refs[p] for p in (RADIO_VOLUME, RADIO_PANEL, RADIO_WINDOW, RADIO_ACTION))])
        if item.split('.', 1)[1] in {'Bleach', 'BathTowel', 'DishCloth', 'Broom', 'Mop'}:
            function(item, 'clean_world_blood', BLOOD_CLEANING, 'world_blood_cleaning',
                     [declaration(item), refs[WORLD_MENU], refs[CLEAN_CURSOR], refs[CLEAN_BLOOD]])
        if (f.get('Type') == 'Clothing' and f.get('OBSOLETE', '').lower() == 'true'
                and f.get('BodyLocation') and f['BodyLocation'] not in body_locations):
            base['unsupported_wear'][item] = {
                'declaration': f, 'location': f['BodyLocation'],
                'source_refs': [inputs.bindings[declarations[item][0]['path']], inputs.bindings[BODY_LOCATIONS], inputs.bindings[semantic.WEAR]],
                'reason': 'The obsolete declaration names a location absent from the supplied Human registry. The wear action passes that location to setWornItem; declaration Type/BodyLocation alone does not establish wearable behavior.'}
    for fact in base['semantic']['facts']:
        if fact['fact_kind'] == 'context_role' and fact['payload'].get('role') in {'material', 'tool'}:
            context = next(f for f in base['semantic']['facts'] if f['fact_id'] == fact['context_fact_ref'])
            if context['payload'] == {'activity': 'fabric_recovery'}:
                recipe_refs = [o for p in fact['provenance_refs'] for o in base['semantic']['provenance'][p]['observation_refs']
                               if 'OnCreate:Recipe.OnCreate.RipClothing' in base['semantic']['observations'][o]['content'].get('clauses', [])]
                if recipe_refs:
                    for observation_ref in recipe_refs:
                        observation = base['semantic']['observations'][observation_ref]
                        builder.sources[observation['source_path']] = observation['source_sha256']
                        builder.observe(observation['source_path'], observation['locator'], observation['content'])
                    builder.fact(fact['item_id'], 'condition', {'predicate': FABRIC_ACTION},
                                 [*recipe_refs, refs[semantic.GROUPS], refs[semantic.CLOTHING], refs[semantic.CRAFT]],
                                 'fabric_conditions', ['activity:crafting'],
                                 applies_to_fact_refs=[fact['fact_id'], context['fact_id']])
            stage_refs = [o for p in fact['provenance_refs'] for o in base['semantic']['provenance'][p]['observation_refs']
                          if ':multistagebuild:' in base['semantic']['observations'][o]['locator']]
            if context['payload'] == {'activity': 'construction'} and stage_refs and fields.get(fact['item_id']):
                builder.fact(fact['item_id'], 'condition', {'predicate': STAGE_ACTION},
                             [declaration(fact['item_id']), refs[semantic.BUILD], refs[semantic.STAGE]],
                             'stage_conditions', ['activity:world_work'], applies_to_fact_refs=[fact['fact_id']])
        if fact['fact_kind'] == 'context_role' and fact['payload'].get('role') in {'repair_target', 'repair_material'}:
            context = next(f for f in base['semantic']['facts'] if f['fact_id'] == fact['context_fact_ref'])
            if context['payload'] == {'activity': 'repair'} and fields.get(fact['item_id']):
                builder.fact(fact['item_id'], 'condition', {'predicate': FIXING_ACTION},
                             [declaration(fact['item_id']), refs[semantic.MENU], refs[semantic.FIX]],
                             'fixing_conditions', ['activity:world_work'],
                             applies_to_fact_refs=[fact['fact_id'], context['fact_id']])
        if fact['fact_kind'] == 'context_role' and fact['payload'] == {'role': 'ingredient'}:
            context = next(f for f in base['semantic']['facts'] if f['fact_id'] == fact['context_fact_ref'])
            if context['payload'] == {'activity': 'food_preparation'} and fields.get(fact['item_id']):
                builder.fact(fact['item_id'], 'condition', {'predicate': COOKING_ACTION},
                             [declaration(fact['item_id']), refs[semantic.MENU], refs[semantic.COOK]],
                             'cooking_conditions', ['activity:cooking'],
                             applies_to_fact_refs=[fact['fact_id'], context['fact_id']])
    inv.require('ISPaintCursor:new' in texts[PAINT_MENU] and 'ISPaintAction:new' in texts[PAINT_CURSOR]
                and 'ISPaintSignAction:new' in texts[PAINT_CURSOR] and 'self.paintPot:Use()' in texts[PAINT_ACTION],
                'paint dispatch changed')
    for item, name, predicate in (('camping.CampfireKit', 'place_campfire', CAMPFIRE_PLACEMENT),
                                  ('camping.CampingTentKit', 'pitch_tent', TENT_PLACEMENT)):
        if (item in targets and fields.get(item, {}).get('Type') == 'Normal'
                and not property_readings[item][1] and set(fields[item]) <= PLAIN_OBJECT_FIELDS):
            evidence = [declaration(item), *(refs[p] for p in (CAMP_MENU, CAMP_CLIENT, CAMP_SERVER,
                CAMP_COMMANDS, CAMP_OBJECT, semantic.BUILD_OBJECT, semantic.BUILD_ACTION, WORLD_MENU,
                *CAMP_PLACEMENT_SOURCES))]
            fid = function(item, name, predicate, 'camping_placement', evidence)
            builder.fact(item, 'condition', {'predicate': CAMP_PLACEMENT}, evidence, 'camping_placement',
                         ['item:direct'], applies_to_fact_refs=[fid])
            if name == 'pitch_tent':
                function(item, 'rest_at_placed_tent', TENT_REST, 'camping_placement', evidence)
    for item in sorted(targets & fields.keys()):
        f = fields[item]
        conflicts = property_readings[item][1]
        if not f:
            continue
        if f.get('Type') == 'Food' and set(conflicts) <= {'ThirstChange', 'Tags', 'WorldStaticModel'}:
            evidence = [declaration(item), refs[semantic.MENU], refs[semantic.TRANSFER], refs[semantic.EAT], refs[semantic.GROUPS]]
            try:
                bait_hunger = float(f.get('HungerChange', '0')) <= -5 or item == 'Base.Worm'
            except ValueError:
                bait_hunger = False
            if f.get('CustomContextMenu') != 'Drink' and bait_hunger:
                function(item, 'supply_trap_bait', FOOD_TRAP_BAIT, 'food_trap_bait',
                         [declaration(item), *(refs[p] for p in (TRAP_MENU, TRAP_BAIT, TRAP_CLIENT, TRAP_COMMANDS, TRAP_OBJECT))])
            chef = builder.fact(item, 'effect', {'property': 'food_chef_attribution', 'direction': 'set_transferring_character'},
                                evidence, 'food_selected_state', ['item:direct'])
            builder.fact(item, 'condition', {'predicate': FOOD_TRANSFER}, evidence, 'food_selected_state',
                         ['item:direct'], applies_to_fact_refs=[chef])
            selected = base.setdefault('food_selected_sources', {}).setdefault(item, {'source_refs': evidence, 'callback_interpretations': [],
                'repeated_properties': conflicts})
            selected['trap_bait_selection'] = {'declared_hunger': f.get('HungerChange'), 'custom_menu': f.get('CustomContextMenu'),
                'admitted': f.get('CustomContextMenu') != 'Drink' and bait_hunger,
                'consumer': 'Food menu requires native HungerChange <= -0.05 or Worm, uncooked/no extra ingredients and non-Drink. No positive intrinsic bait function is inferred for a declared insufficient hunger input.'}
            if item == 'Base.Maggots2' and f.get('FishingLure', '').lower() == 'true' and 'Maggots2' not in registered_lures:
                selected['lure_gap'] = {'source_path': FISHING_PROPERTIES, 'action': FISHING_ACTION,
                    'meaning': 'Maggots2 is commented out of lureItems and has no explicit registered lure entry in the supplied source. The UI queries isFishingLure, while ISFishingAction:new immediately reads Fishing.lure[type].plastic without a nil guard.',
                    'required_input': 'An authoritative reconciliation of the obsolete Maggots2 FishingLure declaration with the missing lure-properties registration; no successful rod-fishing function is admitted.'}
            result_relations = [r for r in base.get('cooking_base_relations', {}).get(item, []) if r['field'] == 'ResultItem']
            if result_relations:
                relation_refs = [builder.observe(r['path'], 'evolved food naming:' + r['recipe'],
                                                 {'recipe_name': r['recipe'], 'clauses': r['clauses'], 'field': r['field']})
                                 for r in result_relations]
                function(item, 'rename_prepared_food', FOOD_NAMING, 'food_selected_state', [*evidence, *relation_refs])
                selected['naming_relations'] = result_relations
            if f.get('OnCooked') == 'CannedFood_OnCooked':
                fid = builder.fact(item, 'effect', {'property': 'food_preservation_age', 'direction': 'rebase_on_cooking'},
                                   evidence, 'food_selected_state', ['item:direct'])
                builder.fact(item, 'condition', {'predicate': CANNED_COOKED}, evidence, 'food_selected_state',
                             ['item:direct'], applies_to_fact_refs=[fid])
                selected['callback_interpretations'].append('CannedFood_OnCooked')
            if f.get('OnCreate') == 'Fishing.OnCreateFish':
                fish_text = reader.mask(texts[FISHING_PROPERTIES], lua=True)
                names = re.findall(r'(\w+)\.item\s*=\s*"' + re.escape(item) + r'"', fish_text)
                if len(names) == 1 and re.search(r'table\.insert\(fishes,\s*' + re.escape(names[0]) + r'\)', fish_text):
                    sizes = {size: {key: re.findall(re.escape(names[0]) + r'\.' + size + r'\.' + key + r'\s*=\s*([0-9.]+)', fish_text)
                                    for key in ('minSize', 'maxSize', 'weightChange')} for size in ('little', 'medium', 'big')}
                    if all(len(v) == 1 and float(v[0]) > 0 for entry in sizes.values() for v in entry.values()):
                        fish_evidence = [*evidence, refs[FISHING_PROPERTIES]]
                        fid = builder.fact(item, 'effect', {'property': 'fish_size_nutrition', 'direction': 'initialize_from_registered_size'},
                                           fish_evidence, 'food_selected_state', ['item:direct'])
                        builder.fact(item, 'condition', {'predicate': FISH_CREATED}, fish_evidence, 'food_selected_state',
                                     ['item:direct'], applies_to_fact_refs=[fid])
                        selected['callback_interpretations'].append('Fishing.OnCreateFish')
                        selected['fish_size_declaration'] = sizes
        if (f.get('Type') == 'Drainable' and not conflicts and f.get('CanConsolidate', '').lower() != 'false'
                and f.get('cantBeConsolided', '').lower() != 'true'
                and item not in {'Base.Disinfectant', 'Base.AlcoholWipes', 'Base.AlcoholedCottonBalls', 'Base.Soap2', 'Base.CleaningLiquid2'}):
            function(item, 'consolidate_drainable_supplies', MEDICAL_CONSOLIDATION, 'drainable_consolidation',
                     [declaration(item), refs[semantic.MENU], refs[CONSOLIDATE]])
        if f.get('Type') == 'Drainable' and f.get('IsWaterSource', '').lower() == 'true' and not conflicts:
            function(item, 'dump_water', WATER_EMPTYING, 'container_emptying',
                     [declaration(item), refs[semantic.MENU], refs[DUMP_WATER]])
        elif f.get('Type') != 'Literature' and f.get('CanStoreWater', '').lower() != 'true' and not conflicts:
            chain = [item]
            current = item
            terminal = None
            while current in fields:
                values = fields[current]
                if property_readings[current][1]:
                    break
                if current != item and values.get('CanStoreWater', '').lower() == 'true':
                    terminal = current
                    break
                token = values.get('ReplaceOnUse') or (values.get('ReplaceOnDeplete') if values.get('Type') == 'Drainable' else None)
                if not token or not re.fullmatch(r'[A-Za-z0-9_.]+', token):
                    break
                current = reader.qualify(current.split('.', 1)[0], token)
                if current in chain:
                    break
                chain.append(current)
            if terminal:
                evidence = [*(declaration(i) for i in chain), refs[semantic.MENU], refs[DUMP_CONTENTS]]
                function(item, 'dump_contents', CONTENTS_EMPTYING, 'container_emptying', evidence)
                base.setdefault('container_emptying_relations', {})[item] = {'chain': chain, 'terminal': terminal,
                    'observation_refs': evidence, 'native_boundary': 'InventoryItem.Use final-item creation and delivery'}
        if (f.get('Type') == 'Drainable' and not conflicts and
                (item.split('.', 1)[1] in {'Extinguisher', 'Dirtbag', 'Gravelbag', 'Sandbag'}
                 or f.get('IsWaterSource', '').lower() == 'true')):
            evidence = [declaration(item), *(refs[p] for p in (WORLD_MENU, FIRE_FIGHTING, EXTINGUISH_CURSOR, PUT_OUT_FIRE))]
            function(item, 'extinguish_fire', EXTINGUISH_CONDITIONS, 'fire_extinguishing', evidence)
        ground_bag = item in {'Base.Dirtbag', 'Base.Gravelbag', 'Base.Sandbag'} and f.get('Type') == 'Drainable'
        empty_ground = 'HoldDirt' in f.get('Tags', '').split(';') and f.get('Type') == 'Container'
        if not conflicts and (ground_bag or empty_ground):
            evidence = [declaration(item), *(refs[p] for p in (GROUND_MENU, GROUND_CURSOR, SHOVEL_GROUND, NATURAL_FLOOR,
                         OBJECT_COMMANDS, WORLD_MENU, semantic.BUILD_OBJECT, semantic.BUILD_ACTION))]
            function(item, 'fill_ground_bag', GROUND_FILL, 'ground_bags', evidence)
            base.setdefault('ground_bag_relations', {})[item] = {'item_id': item, 'kind': 'filled' if ground_bag else 'empty',
                'observation_refs': evidence, 'source_paths': sorted({builder.observations[o]['source_path'] for o in evidence})}
            if ground_bag:
                function(item, 'pour_ground_cover', GROUND_POUR, 'ground_bags', evidence)
        if item in {'Base.SheetRope', 'Base.Rope', 'Base.Nails'} and f.get('Type') == 'Normal' and not conflicts:
            evidence = [declaration(item), *(refs[p] for p in (WORLD_MENU, ADD_ROPE, REMOVE_ROPE, CLIMB_ROPE, OBJECT_COMMANDS))]
            function(item, 'anchor_escape_rope' if item == 'Base.Nails' else 'supply_escape_rope', ESCAPE_ROPE_INSTALL, 'escape_rope', evidence)
            if item != 'Base.Nails':
                function(item, 'remove_installed_escape_rope', ESCAPE_ROPE_REMOVE, 'escape_rope', evidence)
                function(item, 'start_escape_rope_ascent', ESCAPE_ROPE_CLIMB, 'escape_rope', evidence)
        if (item in SPEAR_ITEMS and f.get('Type') == 'Weapon' and 'FishingSpear' in f.get('Tags', '').split(';')
                and not {'Type', 'Tags'} & conflicts.keys()):
            evidence = [declaration(item), refs[WORLD_MENU], refs[FISHING_UI], refs[FISHING_ACTION], refs[FISHING_PROPERTIES]]
            function(item, 'fish_with_spear', SPEAR_FISHING, 'spear_fishing', evidence)
            wear = builder.fact(item, 'effect', {'property': 'item_condition', 'direction': 'decrease'}, evidence,
                                'spear_fishing', ['item:direct'])
            builder.fact(item, 'condition', {'predicate': SPEAR_FISHING_WEAR}, evidence, 'spear_fishing',
                         ['item:direct'], applies_to_fact_refs=[wear])
        if item == 'Base.PipeWrench' and f.get('Type') == 'Weapon' and not conflicts:
            function(item, 'plumb_external_water', PLUMBING, 'plumbing_tool',
                     [declaration(item), refs[WORLD_MENU], refs[PLUMB_ACTION], refs[OBJECT_COMMANDS], refs[semantic.BUILD_UTIL]])
        if item in {'Base.BarBell', 'Base.DumbBell'} and f.get('Type') == 'Weapon' and not conflicts:
            registrations = [('barbellcurl', 'barbell_curl', 'twohands')] if item == 'Base.BarBell' else [
                ('dumbbellpress', 'dumbbell_press', 'switch'), ('bicepscurl', 'biceps_curl', 'switch')]
            fitness_text = reader.mask(texts[FITNESS_SOURCES[0]], lua=True)
            for key, name, prop in registrations:
                entry = re.search(r'\b' + key + r'\s*=\s*\{([^}]+)\}', fitness_text)
                if entry and 'item = "' + item + '"' in entry[1] and 'prop="' + prop + '"' in entry[1]:
                    function(item, 'exercise_' + name, WEIGHT_EXERCISE, 'weight_exercise',
                             [declaration(item), refs[HEALTH], refs[WORLD_MENU], *(refs[p] for p in FITNESS_SOURCES)])
        if not conflicts and set(f) <= ELECTRICAL_FIELDS:
            electrical = [declaration(item), *[refs[p] for p in RULES['electrical_controls']['source_refs']]]
            operations = []
            if item in LIGHT_BULBS and f.get('Type') == 'Normal':
                operations.append(('install_light_bulb', LAMP_BULB))
                if item == 'Base.LightBulb':
                    operations += [('install_vehicle_bulb', PANEL_INSTALL), ('remove_vehicle_bulb', PANEL_REMOVE)]
            if item == 'Base.Battery' and f.get('Type') == 'Drainable':
                operations += [('supply_lamp_battery', LAMP_BATTERY), ('supply_pillar_light_battery', PILLAR_BATTERY)]
            if item in {'Base.ElectronicsScrap', 'Base.Screwdriver'}:
                operations.append(('convert_lamp_to_battery', LAMP_CONVERSION))
            if item == 'Base.ElectronicsScrap':
                operations.append(('repair_generator', GENERATOR_REPAIR))
            if item == 'Base.CarBatteryCharger' and f.get('Type') == 'Normal':
                operations += [('place_vehicle_battery_charger', CHARGER_PLACEMENT),
                               ('operate_vehicle_battery_charger', CHARGER_CONTROLS)]
            if (item in {'Base.CarBattery1', 'Base.CarBattery2', 'Base.CarBattery3'} and f.get('Type') == 'Drainable'
                    and f.get('VehicleType') == item[-1] and f.get('Tags') == 'CarBattery'):
                operations += [('connect_to_vehicle_battery_charger', CHARGER_CONTROLS),
                               ('install_vehicle_battery', PANEL_INSTALL), ('remove_vehicle_battery', PANEL_REMOVE)]
                effect = builder.fact(item, 'effect', {'property': 'installed_vehicle_battery_charge',
                    'direction': 'adjust_on_engine_state'}, electrical, 'electrical_controls', ['item:direct'])
                builder.fact(item, 'condition', {'predicate': VEHICLE_BATTERY_CYCLE}, electrical,
                             'electrical_controls', ['item:direct'], applies_to_fact_refs=[effect])
            if item == 'Base.Generator' and f.get('Type') == 'Normal' and f.get('Tags') == 'HeavyItem':
                operations += [('control_installed_generator', GENERATOR_CONTROL), ('repair_generator', GENERATOR_REPAIR),
                    ('refuel_generator', GENERATOR_REFUEL), ('handle_generator', GENERATOR_HANDLING),
                    ('inspect_generator', GENERATOR_INSPECTION)]
            for name, predicate in operations:
                fid = function(item, name, predicate, 'electrical_controls', electrical)
                if name in {'install_vehicle_battery', 'remove_vehicle_battery', 'install_vehicle_bulb', 'remove_vehicle_bulb'}:
                    specific = VEHICLE_BATTERY_EXCHANGE if item.startswith('Base.CarBattery') else VEHICLE_BULB_EXCHANGE
                    builder.fact(item, 'condition', {'predicate': specific}, electrical,
                                 'electrical_controls', ['item:direct'], applies_to_fact_refs=[fid])
            if operations:
                base.setdefault('electrical_control_sources', {})[item] = {
                    'declaration': f, 'functions': sorted(name for name, _ in operations),
                    'observation_refs': sorted(set(electrical))}
        if item == 'Base.Screwdriver' and f.get('Tags') == 'Screwdriver' and not conflicts:
            function(item, 'convert_lamp_to_battery', LAMP_CONVERSION, 'electrical_controls',
                     [declaration(item), refs[WORLD_MENU], refs[LAMP_ACTION]])
        running_match = re.fullmatch(r'Base\.(' + '|'.join(VEHICLE_RUNNING_FORMS) + r')([123])', item)
        if (running_match and not conflicts and f.get('Type') == 'Normal'
                and f.get('MechanicsItem', '').lower() == 'true' and f.get('VehicleType') == running_match[2]):
            family = running_match[1]
            kind = VEHICLE_RUNNING_FORMS[family]
            path = 'scripts/vehicles/template_' + kind + '.txt'
            template = reader.mask(texts[path])
            if re.search(r'itemType\s*=\s*[^,\n]*\bBase\.' + re.escape(family) + r'(?=[;,])', template):
                evidence = [declaration(item), refs[path], *(refs[p] for p in (
                    VEHICLE_MECHANICS, VEHICLE_MENU, VEHICLE_INSTALL, VEHICLE_UNINSTALL, VEHICLE_COMMANDS, VEHICLE_CALLBACKS))]
                base.setdefault('vehicle_running_sources', {})[item] = {'kind': kind, 'template': path,
                    'declaration': f, 'native_vehicle_type': running_match[2], 'observation_refs': sorted(set(evidence)),
                    'exchange_conditions': RUNNING_EXCHANGE[kind]}
                for verb, predicate in (('install', PANEL_INSTALL), ('remove', PANEL_REMOVE)):
                    fid = function(item, verb + '_vehicle_' + kind, predicate, 'vehicle_running_parts', evidence)
                    builder.fact(item, 'condition', {'predicate': RUNNING_EXCHANGE[kind]}, evidence,
                                 'vehicle_running_parts', ['item:direct'], applies_to_fact_refs=[fid])
                wear = builder.fact(item, 'effect', {'property': 'installed_vehicle_part_condition', 'direction': 'decrease'},
                                    evidence, 'vehicle_running_parts', ['item:direct'])
                builder.fact(item, 'condition', {'predicate': BRAKE_WEAR if kind == 'brake' else RUNNING_WEAR},
                             evidence, 'vehicle_running_parts', ['item:direct'], applies_to_fact_refs=[wear])
                if kind == 'tire':
                    tire_evidence = [*evidence, *(refs[p] for p in TIRE_ACTIONS)]
                    function(item, 'inflate_vehicle_tire', TIRE_INFLATION, 'vehicle_running_parts', tire_evidence)
                    function(item, 'deflate_vehicle_tire', TIRE_DEFLATION, 'vehicle_running_parts', tire_evidence)
                    loss = builder.fact(item, 'effect', {'property': 'installed_tire_air_or_attachment', 'direction': 'lose'},
                                        tire_evidence, 'vehicle_running_parts', ['item:direct'])
                    builder.fact(item, 'condition', {'predicate': TIRE_WEAR}, tire_evidence,
                                 'vehicle_running_parts', ['item:direct'], applies_to_fact_refs=[loss])
        if item == 'Base.TirePump' and not conflicts and f.get('Type') == 'Normal':
            function(item, 'inflate_vehicle_tire', TIRE_INFLATION, 'vehicle_running_parts',
                     [declaration(item), *(refs[p] for p in (VEHICLE_MECHANICS, VEHICLE_MENU, WORLD_MENU, VEHICLE_COMMANDS, *TIRE_ACTIONS))])
        storage_match = re.fullmatch(r'Base\.(' + '|'.join(VEHICLE_STORAGE_FORMS) + r')([123])', item)
        if (storage_match and not conflicts and f.get('Type') == 'Normal' and f.get('MechanicsItem', '').lower() == 'true'
                and f.get('VehicleType') == storage_match[2]):
            family = storage_match[1]
            template_name, part_name, override, label = VEHICLE_STORAGE_FORMS[family]
            template_path = 'scripts/vehicles/template_' + template_name + '.txt'
            source_path = override or template_path
            source_text = reader.mask(texts[source_path])
            if (re.search(r'itemType\s*=\s*[^,\n]*\bBase\.' + re.escape(family) + r'(?=[;,])', source_text)
                    and (not override or 'template = Trunk/part/TruckBed,' in source_text)):
                evidence = [declaration(item), refs[template_path], refs[source_path], refs[VEHICLE_CALLBACKS],
                            refs[INVENTORY_PAGE], refs[semantic.TRANSFER]]
                base.setdefault('vehicle_storage_sources', {})[item] = {'family': family, 'template': template_path,
                    'part': part_name, 'override': override, 'observation_refs': sorted(set(evidence)),
                    'native_binding': 'VehiclePart.getItemType and installed inventory identity for VehicleType ' + f['VehicleType'],
                    'capacity_declaration': {k: f[k] for k in ('MaxCapacity', 'ConditionAffectsCapacity', 'ConditionMax') if k in f},
                    'exchange_table': template_name in {'seat', 'gastank'}}
                if template_name == 'gastank':
                    evidence += [refs[VEHICLE_USE_MENU], refs[VEHICLE_MENU], refs[VEHICLE_COMMANDS], *[refs[p] for p in VEHICLE_FUEL_ACTIONS]]
                    function(item, 'store_vehicle_fuel', VEHICLE_FUEL, 'vehicle_storage', evidence)
                    function(item, 'transfer_vehicle_fuel', VEHICLE_FUEL, 'vehicle_storage', evidence)
                    function(item, 'supply_vehicle_engine_fuel', VEHICLE_FUEL_ENGINE, 'vehicle_storage', evidence)
                else:
                    function(item, 'store_vehicle_items', VEHICLE_STORAGE, 'vehicle_storage', evidence)
                if template_name == 'seat':
                    function(item, 'use_vehicle_seat', VEHICLE_SEATING, 'vehicle_seating',
                             [*evidence, refs[VEHICLE_USE_MENU], refs[VEHICLE_SEAT_UI],
                              *[refs[p] for p in VEHICLE_SEAT_ACTIONS], *[refs[p] for p in VEHICLE_DOOR_ACTIONS]])
                if template_name in {'seat', 'gastank'}:
                    exchange_evidence = [*evidence, refs[VEHICLE_MECHANICS], refs[VEHICLE_MENU], refs[VEHICLE_INSTALL],
                                         refs[VEHICLE_UNINSTALL], refs[VEHICLE_COMMANDS]]
                    for name, predicate in (('install_vehicle_storage_part', PANEL_INSTALL), ('remove_vehicle_storage_part', PANEL_REMOVE)):
                        fid = function(item, name, predicate, 'vehicle_storage', exchange_evidence)
                        builder.fact(item, 'condition', {'predicate': VEHICLE_EXCHANGE_REQUIREMENTS[template_name]},
                                     exchange_evidence, 'vehicle_storage', ['item:direct'], applies_to_fact_refs=[fid])
        panel_match = re.fullmatch(r'Base\.(' + '|'.join(PANEL_FORMS) + r')([123])', item)
        if (panel_match and f.get('MechanicsItem', '').lower() == 'true' and f.get('Type') == 'Normal'
                and f.get('VehicleType') == panel_match[2] and not conflicts):
            family = panel_match[1]
            template = 'scripts/vehicles/template_' + PANEL_FORMS[family][0] + '.txt'
            if re.search(r'\bitemType\s*=\s*Base\.' + re.escape(family) + r'\s*,', reader.mask(texts[template])):
                evidence = [declaration(item), refs[template], *[refs[p] for p in (
                    VEHICLE_MECHANICS, VEHICLE_MENU, VEHICLE_INSTALL, VEHICLE_UNINSTALL, VEHICLE_COMMANDS, VEHICLE_CALLBACKS)]]
                function(item, 'install_vehicle_' + PANEL_FORMS[family][1], PANEL_INSTALL, 'vehicle_panel_exchange', evidence)
                function(item, 'remove_vehicle_' + PANEL_FORMS[family][1], PANEL_REMOVE, 'vehicle_panel_exchange', evidence)
                controls = [*evidence, refs[VEHICLE_USE_MENU], *[refs[p] for p in VEHICLE_DOOR_ACTIONS]]
                if family in {'EngineDoor', 'FrontCarDoor', 'RearCarDoor', 'RearCarDoorDouble', 'TrunkDoor'}:
                    function(item, 'operate_installed_vehicle_door', PANEL_DOOR, 'vehicle_panel_controls', controls)
                    function(item, 'operate_installed_vehicle_lock', PANEL_LOCK, 'vehicle_panel_controls', controls)
                elif family in {'FrontWindow', 'RearWindow'}:
                    function(item, 'operate_installed_vehicle_window', PANEL_WINDOW, 'vehicle_panel_controls', controls)
                base.setdefault('vehicle_panel_sources', {})[item] = {
                    'family': family, 'part_meaning': PANEL_FORMS[family][1], 'template': template,
                    'raw_item_type': 'Base.' + family, 'vehicle_type': f['VehicleType'],
                    'binding': 'Exact runtime FullType membership is required, not inferred by suffix expansion.'}
        if (item in STRAP_SPEED and f.get('Type') == 'Clothing' and f.get('BodyLocation') == 'AmmoStrap'
                and f.get('ClothingItem') == item.split('.', 1)[1] and not conflicts):
            evidence = [declaration(item), refs[FIREARM], refs[LOAD_MAGAZINE], refs[INSERT_MAGAZINE],
                        *[refs[p] for p in RELOAD_ACTIONS], refs[semantic.WEAR], refs[BODY_LOCATIONS]]
            speed = builder.fact(item, 'effect', {'property': 'reload_speed_setting', 'direction': 'multiply_1_15'},
                                 evidence, 'ammo_strap_speed', ['item:direct', 'activity:wearing'])
            builder.fact(item, 'condition', {'predicate': STRAP_SPEED[item]}, evidence,
                         'ammo_strap_speed', ['item:direct', 'activity:wearing'], applies_to_fact_refs=[speed])
        bandage_power = f.get('BandagePower', '')
        if (item in BANDAGE_ITEMS and f.get('CanBandage', '').lower() == 'true' and 'BandagePower' not in conflicts
                and re.fullmatch(r'\d+(?:\.\d+)?', bandage_power) and float(bandage_power) > 0):
            evidence = [declaration(item), refs[HEALTH], refs[semantic.BANDAGE], refs[semantic.MENU], refs[CLEAN_BURN]]
            original_bandage = original_functions.get((item, 'apply_bandage'))
            if original_bandage:
                builder.fact(item, 'condition', {'predicate': BANDAGE_APPLICATION}, evidence,
                             'bandage_lifecycle', ['item:direct'], applies_to_fact_refs=[original_bandage['fact_id']])
            else:
                function(item, 'apply_bandage', BANDAGE_APPLICATION, 'bandage_lifecycle', evidence)
            function(item, 'remove_applied_bandage', BANDAGE_REMOVAL, 'bandage_lifecycle', evidence)
            effects = [('bandage_patient_infection', 'set_true', BANDAGE_INFECTION),
                       ('treatment_panic', 'add_50', BANDAGE_OR_BURN_PANIC if float(bandage_power) >= 2 else BANDAGE_PANIC)]
            if 'Dirty' not in item.split('.', 1)[1]:
                effects.append(('applied_bandage_life', 'set_skill_random_plus_power', BANDAGE_LIFE))
            for prop, direction, predicate in effects:
                fid = builder.fact(item, 'effect', {'property': prop, 'direction': direction}, evidence, 'bandage_state', ['item:direct'])
                builder.fact(item, 'condition', {'predicate': predicate}, evidence, 'bandage_state', ['item:direct'], applies_to_fact_refs=[fid])
            if float(bandage_power) >= 2:
                burn_evidence = [declaration(item), refs[HEALTH], refs[CLEAN_BURN]]
                function(item, 'clean_burn', BURN_CLEANING, 'burn_cleaning', burn_evidence)
                for prop, direction in [('burn_wash_requirement', 'clear'), ('additional_pain', 'add_60_minus_doctor_level'), ('doctor_experience', 'add_10')]:
                    fid = builder.fact(item, 'effect', {'property': prop, 'direction': direction}, burn_evidence, 'burn_cleaning', ['item:direct'])
                    builder.fact(item, 'condition', {'predicate': BURN_CLEANING}, burn_evidence, 'burn_cleaning', ['item:direct'], applies_to_fact_refs=[fid])
        if item in PILL_ITEMS and (item, 'take_pills') in original_functions:
            builder.fact(item, 'condition', {'predicate': PILL_TAKING}, [declaration(item), refs[semantic.MENU], refs[semantic.PILLS]],
                         'pill_controls', ['item:direct'], applies_to_fact_refs=[original_functions[item, 'take_pills']['fact_id']])
        if ((f.get('Type') in {'Container', 'Key', 'Map'} and 'Type' not in conflicts)
                or item.split('.', 1)[1] == 'KeyRing'):
            function(item, 'rename_selected_item', RENAME_ITEM, 'item_naming',
                     [declaration(item), refs[semantic.MENU], refs[NAME_DIALOG]])
        if f.get('Type') == 'Key' and not conflicts:
            evidence = [declaration(item), refs[WORLD_MENU], refs[PADLOCK_ACTION], refs[DOOR_LOCK], refs[DIGITAL_CODE], refs[semantic.BUILD_UTIL]]
            if item in KEY_ITEMS:
                function(item, 'operate_door_lock', DOOR_KEY_USE, 'key_lock_controls', evidence)
                function(item, 'remove_matching_padlock', PADLOCK_KEY_USE, 'key_lock_controls', evidence)
                vehicle_evidence = [declaration(item), refs[VEHICLE_USE_MENU], refs[VEHICLE_START], refs[VEHICLE_DASHBOARD],
                                    refs[VEHICLE_COMMANDS], refs[VEHICLE_CALLBACKS], refs[VEHICLE_MECHANICS], *[refs[p] for p in VEHICLE_DOOR_ACTIONS]]
                for name, predicate in [('request_matching_vehicle_start', VEHICLE_KEY_USE),
                                        ('avoid_first_door_alarm_trigger', KEY_ALARM), ('satisfy_vehicle_mechanics_key', KEY_MECHANICS)]:
                    function(item, name, predicate, 'key_lock_controls', vehicle_evidence)
            if item == 'Base.Padlock' and f.get('Padlock', '').lower() == 'true':
                function(item, 'install_padlock', PADLOCK_USE, 'key_lock_controls', evidence)
            if item == 'Base.CombinationPadlock' and f.get('DigitalPadlock', '').lower() == 'true':
                function(item, 'install_combination_padlock', CODE_LOCK_USE, 'key_lock_controls', evidence)
                function(item, 'remove_combination_padlock', CODE_UNLOCK, 'key_lock_controls', evidence)
        if (item, 'dry_the_body') in original_functions:
            builder.fact(item, 'condition', {'predicate': BODY_DRYING},
                         [declaration(item), refs[semantic.MENU], refs[DRY_BODY]], 'body_drying', ['item:direct'],
                         applies_to_fact_refs=[original_functions[item, 'dry_the_body']['fact_id']])
        if 'ClearAshes' in {part.strip() for part in f.get('Tags', '').split(';')} and 'Tags' not in conflicts:
            function(item, 'clear_burnt_floor_ashes', ASH_CLEARING, 'ash_clearing',
                     [declaration(item), refs[WORLD_MENU], refs[CLEAR_ASHES]])
        slot_list = tuple(part.strip() for part in f.get('AttachmentsProvided', '').split(';') if part.strip())
        slot_function = {
            ('SmallBeltLeft', 'SmallBeltRight'): 'provide_belt_slots',
            ('HolsterRight',): 'provide_right_holster_slot',
            ('HolsterLeft', 'HolsterRight'): 'provide_paired_holster_slots',
        }.get(slot_list)
        if (slot_function and set(slot_list) <= registered_slots and f.get('Type') == 'Clothing'
                and f.get('BodyLocation') in body_locations
                and not {'AttachmentsProvided', 'Type', 'BodyLocation'} & conflicts.keys()):
            function(item, slot_function, SLOT_USE, 'worn_attachment_slots',
                     [declaration(item), *(refs[p] for p in (HOTBAR, HOTBAR_SLOTS, HOTBAR_ATTACH, BODY_LOCATIONS, semantic.WEAR))])
        if f.get('Type') == 'Radio' and 'Type' not in conflicts:
            evidence = [declaration(item), *(refs[p] for p in (CONTEXT_MANAGER, CONTEXT_INVENTORY, CONTEXT_LOADER,
                        CONTEXT_ELEMENT, CONTEXT_RADIO, RADIO_WINDOW, RADIO_PANEL, RADIO_ACTION))]
            function(item, 'open_device_controls', DEVICE_PANEL, 'device_controls', evidence)
            function(item, 'adjust_device_volume', DEVICE_VOLUME, 'device_controls', [*evidence, refs[RADIO_VOLUME]])
            power_evidence = [*evidence, refs[RADIO_POWER], refs[RADIO_GRID]]
            function(item, 'toggle_device_power', DEVICE_POWER, 'device_controls', power_evidence)
            if f.get('UsesBattery', '').lower() == 'true' and 'UsesBattery' not in conflicts:
                function(item, 'insert_device_battery', BATTERY_INSERT, 'device_controls', power_evidence)
                function(item, 'remove_device_battery', BATTERY_REMOVE, 'device_controls', power_evidence)
            if f.get('TwoWay', '').lower() == 'true' and 'TwoWay' not in conflicts:
                function(item, 'toggle_radio_microphone', MIC_CONTROL, 'device_controls', [*evidence, refs[RADIO_MIC]])
            if not {'IsTelevision', 'NoTransmit'} & conflicts.keys():
                if f.get('IsTelevision', '').lower() == 'true':
                    function(item, 'select_tv_channel', TV_TUNING, 'device_controls', [*evidence, refs[TV_CHANNEL]])
                elif f.get('IsTelevision', '').lower() == 'false' and f.get('NoTransmit', '').lower() != 'true':
                    function(item, 'tune_radio', RADIO_TUNING, 'device_controls', [*evidence, refs[RADIO_CHANNEL]])
            if not conflicts and set(f) <= RADIO_FIELDS:
                panel = next(fact['fact_id'] for fact in builder.facts.values()
                             if fact['item_id'] == item and fact['payload'] == {'function': 'open_device_controls'})
                builder.fact(item, 'condition', {'predicate': RADIO_WINDOW_LIFETIME},
                    [*evidence, refs[RADIO_GENERAL]], 'device_controls_extended', ['item:direct'], applies_to_fact_refs=[panel])
                if f.get('IsTelevision', '').lower() == 'false' and f.get('NoTransmit', '').lower() != 'true':
                    function(item, 'edit_radio_presets', RADIO_PRESETS, 'device_controls_extended',
                             [*evidence, refs[RADIO_CHANNEL], refs[RADIO_PRESET_EDITOR]])
                if f.get('IsPortable', '').lower() == 'true' and f.get('IsTelevision', '').lower() == 'false':
                    function(item, 'control_device_headphones', RADIO_HEADPHONE_CONTROL, 'device_controls_extended',
                             [*evidence, refs[RADIO_VOLUME]])
                if f.get('AcceptMediaType') in {'0', '1'}:
                    function(item, 'control_device_media', RADIO_MEDIA_CONTROL, 'device_controls_extended',
                             [*evidence, refs[RADIO_MEDIA]])
                if f.get('WorldObjectSprite'):
                    function(item, 'place_radio_world_form', RADIO_WORLD_FORM, 'device_controls_extended',
                        [*evidence, *(refs[p] for p in (CONTEXT_MOVABLE, semantic.PROPS, MOVE_CURSOR, semantic.MOVE_ACTION))])
                if f.get('NoTransmit', '').lower() != 'true' or f.get('AcceptMediaType') in {'0', '1'}:
                    code_refs = [*evidence, refs[RADIO_INTERACTIONS], refs[RADIO_MEDIA], refs[RADIO_SIGNAL]]
                    effect = builder.fact(item, 'effect', {'property': 'delivered_media_code_outcome', 'direction': 'apply_configured_code'},
                                          code_refs, 'device_controls_extended', ['item:direct'])
                    builder.fact(item, 'condition', {'predicate': RADIO_CODE_EFFECTS}, code_refs,
                                 'device_controls_extended', ['item:direct'], applies_to_fact_refs=[effect])
        if f.get('MediaCategory') in media_categories and 'MediaCategory' not in conflicts:
            evidence = [declaration(item), *(refs[p] for p in (CONTEXT_MANAGER, CONTEXT_INVENTORY, CONTEXT_LOADER,
                        CONTEXT_ELEMENT, CONTEXT_MEDIA, MEDIA_LOADER, MEDIA_DATA))]
            function(item, 'read_recorded_media_label', MEDIA_LABEL, 'recorded_media_controls', [*evidence, refs[MEDIA_INFO]])
            function(item, 'insert_recorded_media', MEDIA_INSERT, 'recorded_media_controls',
                     [*evidence, refs[RADIO_MEDIA], refs[RADIO_WINDOW], refs[RADIO_PANEL], refs[RADIO_ACTION]])
            code_refs = [*evidence, refs[RADIO_INTERACTIONS], refs[RADIO_MEDIA], refs[RADIO_ACTION]]
            effect = builder.fact(item, 'effect', {'property': 'delivered_media_code_outcome', 'direction': 'apply_configured_code'},
                                  code_refs, 'device_controls_extended', ['item:direct'])
            builder.fact(item, 'condition', {'predicate': RADIO_CODE_EFFECTS}, code_refs,
                         'device_controls_extended', ['item:direct'], applies_to_fact_refs=[effect])
        if item == 'Base.Battery' and f.get('Type') == 'Drainable':
            function(item, 'use_as_radio_battery', BATTERY_INSERT, 'device_controls',
                     [declaration(item), refs[RADIO_POWER], refs[RADIO_ACTION], refs[RADIO_PANEL], refs[RADIO_WINDOW]])
        if f.get('Trap', '').lower() == 'true' and 'Trap' not in conflicts and len(trap_types[item]) == 1:
            evidence = [declaration(item), *[refs[p] for p in (TRAP_MENU, TRAP_BUILD, TRAP_DEFINITIONS, TRAP_CLIENT,
                          TRAP_CLIENT_OBJECT, semantic.BUILD_OBJECT, semantic.BUILD_ACTION, TRAP_SYSTEM, TRAP_OBJECT, TRAP_BAIT, TRAP_COMMANDS)]]
            function(item, 'place_animal_trap', TRAP_PLACEMENT, 'animal_trap', evidence)
            if item in catching_types:
                function(item, 'catch_trap_animal', TRAP_CATCH, 'animal_trap', evidence)
            evidence += [refs[p] for p in TRAP_ACTIONS]
            fid = function(item, 'manage_animal_trap', TRAP_CONTROLS, 'equipment_controls', evidence)
            builder.fact(item, 'condition', {'predicate': TRAP_LIFECYCLE}, evidence, 'equipment_controls',
                         ['item:direct'], applies_to_fact_refs=[fid])
        controller = f.get('RemoteController', '').lower() == 'true' and 'RemoteController' not in conflicts
        controlled = (f.get('Type') == 'Weapon' and f.get('CanBeRemote', '').lower() == 'true'
                      and not {'Type', 'CanBeRemote'} & conflicts.keys())
        if controller or controlled:
            evidence = [declaration(item), refs[semantic.MENU]]
            function(item, 'link_remote_device', REMOTE_LINK, 'remote_control', evidence)
            function(item, 'reset_remote_id', REMOTE_RESET, 'remote_control', evidence)
            if controller:
                function(item, 'send_remote_trigger', REMOTE_TRIGGER, 'remote_control', [*evidence, refs[OBJECT_COMMANDS]])
        if item in {'Base.Fertilizer', 'Base.CompostBag'} and f.get('Type') == 'Drainable' and 'Type' not in conflicts:
            evidence = [declaration(item), *[refs[p] for p in (FARM_MENU, FERTILIZE_ACTION, FARM_CLIENT, FARM_SYSTEM, FARM_COMMANDS, PLANT)]]
            function(item, 'apply_fertilizer', FERTILIZING, 'fertilizing', evidence)
            for property_name, direction, predicate in (('crop_growth_schedule', 'advance', FERTILIZER_GROWTH), ('crop_state', 'set_rotten', FERTILIZER_ROT)):
                effect = builder.fact(item, 'effect', {'property': property_name, 'direction': direction}, evidence, 'fertilizing', ['item:direct'])
                for condition in (FERTILIZING, predicate):
                    builder.fact(item, 'condition', {'predicate': condition}, evidence, 'fertilizing', ['item:direct'], applies_to_fact_refs=[effect])
        fishing_evidence = [declaration(item), *[refs[p] for p in (WORLD_MENU, FISHING_UI, FISHING_ACTION, FISHING_PROPERTIES)]]
        trap_function = next((v['fact_id'] for v in builder.facts.values() if v['item_id'] == item and v['payload'] == {'function': 'catch_trap_animal'}), None)
        if trap_function:
            for animals, baits, hours, predicate in (
                (('rabbit', 'squirrel'), {'Base.Apple', 'Base.Corn'}, (19, 5), TRAP_RABBIT_SQUIRREL),
                (('bird',), {'Base.Worm', 'Base.Bread', 'Base.Corn'}, (0, 0), TRAP_BIRD),
                (('mouse', 'rat'), {'Base.Cheese', 'Base.PeanutButter'}, (0, 0), TRAP_RODENTS),
            ):
                if all(animal in animal_inputs and item in animal_inputs[animal]['traps']
                       and baits <= animal_inputs[animal]['baits'] and hours == animal_inputs[animal]['hours'] for animal in animals):
                    builder.fact(item, 'condition', {'predicate': predicate},
                                 [declaration(item), refs[TRAP_DEFINITIONS], refs[TRAP_OBJECT]],
                                 'animal_trap', ['item:direct'], applies_to_fact_refs=[trap_function])
        if 'Tags' not in conflicts and 'FishingRod' in f.get('Tags', '').split(';'):
            fishing_function = function(item, 'fish_with_rod', ROD_FISHING, 'rod_fishing', fishing_evidence)
            builder.fact(item, 'condition', {'predicate': FISHING_EXECUTION}, fishing_evidence, 'equipment_controls',
                ['item:direct'], applies_to_fact_refs=[fishing_function])
            if item in {'Base.FishingRod', 'Base.FishingRodTwineLine', 'Base.CraftedFishingRod', 'Base.CraftedFishingRodTwineLine'}:
                fid = builder.fact(item, 'effect', {'property': 'fishing_rod_form', 'direction': 'replace_on_line_break'},
                    fishing_evidence, 'equipment_controls', ['item:direct'])
                builder.fact(item, 'condition', {'predicate': ROD_LINE_BREAK}, fishing_evidence,
                    'equipment_controls', ['item:direct'], applies_to_fact_refs=[fid])
            if {'Worm', 'Cricket', 'Grasshopper', 'Cockroach', 'BaitFish', 'FishingTackle', 'FishingTackle2'} <= registered_lures:
                builder.fact(item, 'condition', {'predicate': FISHING_LURES}, fishing_evidence, 'rod_fishing',
                             ['item:direct'], applies_to_fact_refs=[fishing_function])
        if ('FishingLure' not in conflicts and f.get('FishingLure', '').lower() == 'true'
                and item.split('.', 1)[1] in registered_lures):
            fid = function(item, 'bait_rod_fishing', ROD_FISHING, 'rod_fishing', fishing_evidence)
            builder.fact(item, 'condition', {'predicate': FISHING_EXECUTION}, fishing_evidence,
                'equipment_controls', ['item:direct'], applies_to_fact_refs=[fid])
        matching_functions = [v['fact_id'] for v in builder.facts.values() if v['item_id'] == item
                              and (v['payload'] == {'function': 'fish_with_rod'} or
                                   (item in {'Base.BaitFish', 'Base.FishingTackle', 'Base.FishingTackle2'} and v['payload'] == {'function': 'bait_rod_fishing'}))]
        artificial = {'FishingTackle', 'FishingTackle2'}
        if (matching_functions and 'BaitFish' in fish_lures.get('Base.Pike', set())
                and all(artificial <= fish_lures.get(species, set()) for species in ('Base.Trout', 'Base.Bass', 'Base.Catfish'))
                and all(species in fish_lures and not artificial & fish_lures[species] for species in ('Base.Pike', 'Base.BaitFish'))):
            builder.fact(item, 'condition', {'predicate': FISHING_MATCHES}, fishing_evidence, 'rod_fishing',
                         ['item:direct'], applies_to_fact_refs=matching_functions)
        if matching_functions and item in {'Base.BaitFish', 'Base.FishingTackle', 'Base.FishingTackle2'}:
            token = item.split('.', 1)[1]
            variables = re.findall(r'lure\["' + re.escape(token) + r'"\]\s*=\s*(\w+)', fishing_text)
            if len(variables) == 1:
                variable = variables[0]
                plastic = re.findall(r'\b' + re.escape(variable) + r'\.plastic\s*=\s*(true|false)', fishing_text)
                chance = re.findall(r'\b' + re.escape(variable) + r'\.chanceOfBreak\s*=\s*(\d+)', fishing_text)
                if len(plastic) == len(chance) == 1 and int(chance[0]) > 0:
                    base.setdefault('fishing_lure_properties', {})[item] = {
                        'plastic': plastic[0] == 'true', 'chanceOfBreak': int(chance[0]),
                        'registry_variable': variable, 'source_path': FISHING_PROPERTIES}
                    builder.fact(item, 'condition', {'predicate': FISHING_LURE_LOSS}, fishing_evidence, 'rod_fishing',
                                 ['item:direct'], applies_to_fact_refs=matching_functions)
        if f.get('CanBandage', '').lower() == 'true' and 'CanBandage' not in conflicts and 'Dirty' in item.split('.', 1)[1]:
            evidence = [declaration(item), refs[HEALTH], refs[semantic.BANDAGE]]
            effect = builder.fact(item, 'effect', {'property': 'applied_bandage_life', 'direction': 'set_zero'},
                                  evidence, 'dirty_bandage', ['item:direct'])
            builder.fact(item, 'condition', {'predicate': DIRTY_BANDAGING}, evidence,
                         'dirty_bandage', ['item:direct'], applies_to_fact_refs=[effect])
        if not {'Type', 'FabricType'} & conflicts.keys():
            name, category = item.split('.', 1)[1], f.get('Type')
            heat_evidence = {declaration(item)}
            heat_operations = []
            for prefix, method, predicate in (('campingFuel', 'supply_hearth_fuel', HEARTH_FUEL),
                    ('campingLightFire', 'provide_hearth_tinder', HEARTH_TINDER)):
                types, categories = camp_tables[prefix + 'Type'], camp_tables[prefix + 'Category']
                if (types[name] if name in types else categories.get(category, 0)) > 0:
                    if category != 'Clothing' or f.get('FabricType'):
                        heat_operations.append((method, predicate))
                    if prefix == 'campingLightFire':
                        heat_operations.append(('provide_industrial_tinder', INDUSTRIAL_TINDER))
            tags = set(f.get('Tags', '').split(';')) if 'Tags' not in conflicts else set()
            igniter = name in {'Lighter', 'Matches'} or 'StartFire' in tags
            petrol = item in PETROL_ITEMS and category == 'Drainable' and tags == {'Petrol'} and not conflicts
            empty = item in EMPTY_PETROL_ITEMS and category == 'Normal' and tags == {'EmptyPetrol'} and not conflicts
            if petrol or empty:
                heat_operations += [('fill_petrol_container', PUMP_CONTAINER), ('transfer_vehicle_fuel', VEHICLE_CONTAINER)]
            if petrol:
                heat_operations.append(('refuel_generator', GENERATOR_REFUEL))
                function(item, 'light_campfire_with_petrol', CAMP_PETROL_USE, 'campfire_ignition',
                    [declaration(item), *[refs[p] for p in (CAMP_MENU, CAMP_LIGHT, CAMP_PETROL_LIGHT, CAMP_CLIENT, CAMP_SERVER, CAMP_COMMANDS, CAMP_OBJECT)]])
            if petrol or igniter:
                heat_operations += [('ignite_hearth_with_petrol', HEARTH_PETROL),
                    ('ignite_industrial_fire_with_petrol', INDUSTRIAL_PETROL), ('request_corpse_burning', CORPSE_IGNITION)]
            if igniter:
                heat_operations += [('ignite_hearth_with_tinder', HEARTH_TINDER), ('ignite_industrial_tinder', INDUSTRIAL_TINDER)]
            if item in {'Base.PercedWood', 'Base.WoodenStick', 'Base.TreeBranch'}:
                heat_operations.append(('kindle_heat_sources', HEAT_FRICTION))
            if item == 'Base.PropaneTank' and category == 'Drainable' and not conflicts:
                heat_operations.append(('supply_propane_barbecue', PROPANE_BARBECUE))
            if item in {'Base.Coal', 'Base.Charcoal'} and category == 'Drainable' and not conflicts:
                heat_operations.append(('supply_furnace_fuel', FURNACE_FUEL))
            if item == 'Base.Bellows' and category == 'Normal' and not conflicts:
                heat_operations.append(('use_furnace_bellows', BELLOWS_USE))
            if item == 'Base.Log' and category == 'Normal' and not conflicts:
                heat_operations.append(('supply_drum_logs', DRUM_LOGS))
            for method, predicate in heat_operations:
                evidence = [declaration(item), *[refs[p] for p in HEAT_PATHS[predicate]]]
                function(item, method, predicate, 'heat_controls', evidence)
                heat_evidence.update(evidence)
                if method == 'use_furnace_bellows':
                    fid = builder.fact(item, 'effect', {'property': 'forge_temperature', 'direction': 'increase'},
                        evidence, 'heat_controls', ['item:direct'])
                    builder.fact(item, 'condition', {'predicate': predicate}, evidence, 'heat_controls',
                        ['item:direct'], applies_to_fact_refs=[fid])
            if heat_operations:
                base.setdefault('heat_control_sources', {})[item] = {'functions': sorted({m for m, _ in heat_operations}),
                    'predicates': sorted({p for _, p in heat_operations}), 'observation_refs': sorted(heat_evidence)}
            if category != 'Clothing' or f.get('FabricType'):
                evidence = [declaration(item), *[refs[p] for p in
                            (CAMP_FUEL, CAMP_MENU, CAMP_ADD, CAMP_LIGHT, CAMP_CLIENT, CAMP_SERVER, CAMP_COMMANDS, CAMP_OBJECT)]]
                for prefix, method, predicate in (('campingFuel', 'supply_campfire_fuel', CAMP_FUEL_USE),
                                                   ('campingLightFire', 'provide_campfire_tinder', CAMP_TINDER_USE)):
                    by_type, by_category = camp_tables[prefix + 'Type'], camp_tables[prefix + 'Category']
                    amount = by_type[name] if name in by_type else by_category.get(category, 0)
                    if amount > 0:
                        function(item, method, predicate, 'campfire_fuel', evidence)
            if name in {'Lighter', 'Matches'} or ('Tags' not in conflicts and 'StartFire' in f.get('Tags', '').split(';')):
                function(item, 'light_campfire', CAMP_IGNITER, 'campfire_ignition',
                         [declaration(item), *[refs[p] for p in
                          (CAMP_MENU, CAMP_LIGHT, CAMP_PETROL_LIGHT, CAMP_CLIENT, CAMP_SERVER, CAMP_COMMANDS, CAMP_OBJECT)]])
        if 'Tags' not in conflicts:
            tags = set(f.get('Tags', '').split(';'))
            if tags & {'Write', 'Pen', 'Pencil', 'RedPen', 'BluePen'}:
                function(item, 'write_note_pages', NOTE_IMPLEMENT, 'note_implements',
                         [declaration(item), refs[semantic.MENU], refs[NOTE_EDITOR]])
            map_evidence = [declaration(item), refs[MAP_VIEW], refs[MAP_SYMBOLS], refs[MAP_TEXT]]
            if tags & {'Pen', 'Pencil', 'RedPen', 'BluePen'}:
                function(item, 'annotate_map', MAP_ANNOTATION, 'map_annotation_tools', map_evidence)
            if item == 'Base.Eraser' or 'Eraser' in tags:
                function(item, 'erase_map_annotations', MAP_ERASURE, 'map_annotation_tools', map_evidence)
        if item in LIGHT_ITEMS and f.get('Type') == 'Drainable' and not conflicts and set(f) <= LIGHT_FIELDS:
            light_evidence = [declaration(item), refs[semantic.MENU], refs[LIGHT_RADIAL], refs[LIGHT_BINDING]]
            if float(f.get('LightStrength', '0')) > 0 or item == 'Base.Candle':
                function(item, 'control_portable_light', LIGHT_CONTROL, 'portable_light_controls', light_evidence)
            if item == 'Base.CandleLit':
                function(item, 'extinguish_on_unequip', CANDLE_UNEQUIP, 'portable_light_controls', light_evidence)
            if item == 'Base.Matches':
                function(item, 'consolidate_drainable_supplies', MEDICAL_CONSOLIDATION, 'portable_light_controls',
                    [declaration(item), refs[semantic.MENU], refs[CONSOLIDATE]])
        if item in {'Base.PercedWood', 'Base.TreeBranch', 'Base.WoodenStick'} and f.get('Type') == 'Normal' and not conflicts:
            function(item, 'light_campfire_by_friction', CAMP_FRICTION, 'campfire_ignition',
                [declaration(item), refs[CAMP_MENU], refs[CAMP_KINDLE_LIGHT], refs[CAMP_CLIENT], refs[CAMP_SERVER], refs[CAMP_COMMANDS], refs[CAMP_OBJECT]])
        if f.get('ActivatedItem', '').lower() == 'true' and item.split('.', 1)[1] != 'CandleLit':
            function(item, 'toggle_activation', ACTIVATION, 'activation', [declaration(item), refs[semantic.MENU]])
        if item in seed_forms:
            fid = function(item, 'sow_seeds', SOWING, 'sowing', [declaration(item), *seed_evidence])
            builder.fact(item, 'condition', {'predicate': SOW_COUNTS[seed_counts[item]]},
                         [declaration(item), *seed_evidence], 'sowing', ['item:direct'], applies_to_fact_refs=[fid])
        if f.get('Type') in {'AlarmClock', 'AlarmClockClothing'}:
            evidence = [declaration(item), refs[semantic.MENU], refs[ALARM_DIALOG], refs[ALARM_STOP]]
            function(item, 'set_alarm', ALARM_SETTING, 'alarm', evidence)
            function(item, 'stop_alarm', ALARM_STOPPING, 'alarm', evidence)
        if (item == 'Base.AlarmClock' and f.get('Type') == 'Weapon'
                and f.get('PhysicsObject') == 'NoiseGenerator' and not conflicts):
            evidence = [declaration(item), refs[semantic.MENU], refs[DEVICE_TIMER],
                        refs[DEVICE_PLACE], refs[WORLD_MENU], refs[DEVICE_TAKE]]
            function(item, 'set_device_timer', DEVICE_DELAY, 'noise_device', evidence)
            function(item, 'place_noise_device', DEVICE_PLACEMENT, 'noise_device', evidence)
            function(item, 'retrieve_placed_device', DEVICE_RETRIEVAL, 'noise_device', evidence)
        if f.get('MakeUpType') in {'Eyes', 'Foundation', 'Lips'} and 'MakeUpType' not in conflicts:
            registered = 'makeup.makeuptypes["' + f['MakeUpType'] + '"] = true;'
            inv.require(registered in texts[MAKEUP_DEFINITIONS]
                        and 'makeup.makeuptypes[self.item:getMakeUpType()]' in texts[MAKEUP_UI]
                        and 'self.character:setWornItem(makeup:getBodyLocation(), makeup)' in texts[MAKEUP_UI]
                        and 'self.character:getInventory():AddItem(self.makeUpSelected)' in texts[MAKEUP_UI],
                        'makeup consumer changed')
            function(item, {'Eyes': 'apply_eye_makeup', 'Lips': 'apply_lip_makeup'}.get(f['MakeUpType'], 'apply_makeup'), MAKEUP_USE, 'makeup',
                     [declaration(item), refs[semantic.MENU], refs[MAKEUP_UI], refs[MAKEUP_DEFINITIONS]])
        if f.get('Type') == 'Food' and f.get('CantEat', '').lower() != 'true':
            callback = f.get('OnEat')
            if callback in {'OnEat_Cigarettes', 'OnEat_WildFoodGeneric'} and 'OnEat' not in conflicts:
                inv.require(len(re.findall(r'^function ' + callback + r'\(', texts[semantic.GROUPS], re.M)) == 1,
                            'ambiguous food callback')
                evidence = [declaration(item), refs[semantic.MENU], refs[semantic.EAT], refs[semantic.GROUPS]]
                scope = ['activity:ingestion']
                effects = [('food_sickness', POISONOUS_WILD_FOOD)]
                if callback == 'OnEat_Cigarettes':
                    effects = [('stress', SMOKER_EFFECT), ('unhappiness', SMOKER_EFFECT), ('food_sickness', NONSMOKER_EFFECT)]
                    if item == 'Base.Cigarettes' and f.get('RequireInHandOrInventory') == 'Matches/Lighter':
                        smoking = function(item, 'smoke_cigarette', SMOKING, 'food_callbacks', evidence, ['item:direct', *scope])
                        builder.fact(item, 'condition', {'predicate': CONSUMING}, evidence, 'food_callbacks',
                                     ['item:direct', *scope], applies_to_fact_refs=[smoking])
                for property_name, predicate in effects:
                    fid = builder.fact(item, 'effect', {'property': property_name, 'direction': 'increase' if property_name == 'food_sickness' else 'decrease'},
                                       evidence, 'food_callbacks', scope)
                    for condition in [predicate, CONSUMING, *([SMOKING] if callback == 'OnEat_Cigarettes' and item == 'Base.Cigarettes' else [])]:
                        builder.fact(item, 'condition', {'predicate': condition}, evidence, 'food_callbacks', scope,
                                     applies_to_fact_refs=[fid])
            if f.get('CustomContextMenu') == 'Take' and not f.get('CustomMenuOption') and f.get('Medical', '').lower() == 'true':
                function(item, 'take_food_medicine', CONSUMING, 'food_callbacks',
                         [declaration(item), refs[semantic.MENU], refs[semantic.EAT]], ['item:direct', 'activity:ingestion'])
        if f.get('DisplayCategory') == 'Ammo' and ammo_receivers[item]:
            receivers = [r for r in ammo_receivers[item] if
                         (fields[r].get('Type') == 'Weapon' and not fields[r].get('MagazineType'))
                         or (fields[r].get('Type') != 'Weapon' and fields[r].get('MaxAmmo'))]
            if receivers:
                function(item, 'load_matching_ammunition', LOADING, 'ammunition_loading',
                         [declaration(item), *(declaration(r) for r in sorted(receivers)),
                          refs[semantic.MENU], refs[FIREARM], refs[LOAD_MAGAZINE]])
        if item in AMMUNITION_ITEMS and f.get('Type') == 'Normal' and set(f) <= AMMUNITION_FIELDS and not conflicts:
            if any(fact['item_id'] == item and fact['payload'] == {'function': 'load_matching_ammunition'} for fact in builder.facts.values()):
                function(item, 'load_matching_ammunition', AMMUNITION_LOADING_PATHS, 'ammunition_controls',
                    [declaration(item), refs[semantic.MENU], refs[FIREARM], refs[FIREARM_RADIAL], refs[LOAD_MAGAZINE],
                     *(refs[path] for path in RELOAD_ACTIONS), *(refs[path] for path in LEGACY_RELOAD_SOURCES)])
        if item in THROWN_DEVICE_ITEMS and f.get('Type') == 'Weapon' and f.get('SwingAnim') == 'Throw' and set(f) <= THROWN_DEVICE_FIELDS and not conflicts:
            evidence = [declaration(item), refs[semantic.MENU], refs[FIREARM], refs[DEVICE_TIMER], refs[DEVICE_PLACE], refs[WORLD_MENU], refs[DEVICE_TAKE]]
            function(item, 'request_physics_attack', PHYSICS_ATTACK, 'physics_device_controls', evidence)
            if float(f.get('ExplosionTimer', '0')) > 0:
                function(item, 'set_device_timer', DEVICE_TIMER_CONTROL, 'physics_device_controls', evidence)
            if f.get('CanBePlaced', '').lower() == 'true':
                function(item, 'place_trigger_device', DEVICE_WORLD_PLACEMENT, 'physics_device_controls', evidence)
                function(item, 'retrieve_placed_device', DEVICE_RETRIEVAL, 'physics_device_controls', evidence)
        if f.get('Type') == 'WeaponPart' and f.get('MountOn') and f.get('PartType') in {'Scope', 'Clip', 'Sling', 'Stock', 'Canon', 'RecoilPad'}:
            mounts = [reader.qualify(item.split('.', 1)[0], token.strip()) for token in f['MountOn'].split(';')]
            if mounts and all(fields.get(m, {}).get('Type') == 'Weapon' and fields[m].get('Ranged', '').lower() == 'true' for m in mounts):
                function(item, 'attach_weapon_part', WEAPON_ATTACHMENT, 'weapon_attachment',
                         [declaration(item), *(declaration(m) for m in sorted(set(mounts))), refs[semantic.MENU], refs[WEAPON_UPGRADE]])
                function(item, 'remove_weapon_part', WEAPON_PART_REMOVAL, 'weapon_attachment',
                         [declaration(item), *(declaration(m) for m in sorted(set(mounts))), refs[semantic.MENU], refs[WEAPON_REMOVAL]])
        if item in MAGAZINE_ITEMS and f.get('Type') == 'Normal' and f.get('AmmoType') and int(f.get('MaxAmmo', '0')) > 0:
            evidence = [declaration(item), refs[semantic.MENU], refs[LOAD_MAGAZINE], refs[FIREARM],
                        refs['lua/client/TimedActions/ISUnloadBulletsFromMagazine.lua']]
            function(item, 'fill_magazine', MAGAZINE_FILL, 'magazine_ammunition', evidence)
            function(item, 'empty_magazine', MAGAZINE_EMPTY, 'magazine_ammunition', evidence)
        if magazine_receivers[item]:
            receivers = [r for r in magazine_receivers[item] if fields[r].get('Type') == 'Weapon']
            if receivers:
                function(item, 'insert_matching_magazine', MAGAZINE_LOADING, 'ammunition_loading',
                         [declaration(item), *(declaration(r) for r in sorted(receivers)),
                          refs[semantic.MENU], refs[INSERT_MAGAZINE], refs[RELOAD_ACTIONS[0]]])
        if f.get('Type') == 'Map':
            map_evidence = [declaration(item), *(refs[p] for p in (semantic.MENU, MAP_VIEW, MAP_SYMBOLS, MAP_TEXT, MAP_DEFINITIONS))]
            function(item, 'view_item_map', MAP_READING, 'map_viewing',
                     map_evidence)
            function(item, 'annotate_item_map', MAP_ANNOTATION, 'item_map_controls', map_evidence)
            function(item, 'erase_item_map_annotations', MAP_ERASURE, 'item_map_controls', map_evidence)
            map_id = f.get('Map')
            if map_id and re.search(r'^LootMaps\.Init\.' + re.escape(map_id) + r'\s*=\s*function\(mapUI\)', texts[MAP_DEFINITIONS], re.M):
                function(item, 'reveal_item_map_area', MAP_REVEAL, 'item_map_controls', map_evidence)
            base.setdefault('item_map_sources', {})[item] = {'declared_map_id': map_id, 'initializer': 'LootMaps.Init.' + map_id if map_id else None,
                'definition_observation_ref': refs[MAP_DEFINITIONS], 'generic_map': not map_id}
        if f.get('Type') == 'Moveable' and f.get('WorldObjectSprite'):
            function(item, 'place_moveable_furniture', PLACEMENT, 'furniture_placement',
                     [declaration(item), refs[MOVE_CURSOR], refs[semantic.PROPS], refs[semantic.MOVE_ACTION]])
            evidence = [declaration(item), refs[MOVE_CURSOR], refs[semantic.PROPS], refs[semantic.MOVE_ACTION]]
            removal = function(item, 'remove_placed_furniture', PICKUP, 'furniture_removal', evidence)
            builder.fact(item, 'constraint', {'predicate': PICKUP_LOSS}, evidence, 'furniture_removal',
                         ['item:direct'], applies_to_fact_refs=[removal])
        if (item in BROKEN_GLASS_ITEMS and f.get('Type') == 'Moveable' and f.get('Tags') == 'BrokenGlass'
                and f.get('WorldObjectSprite') == item.split('.', 1)[1] and not conflicts):
            evidence = [declaration(item), *(refs[p] for p in (WORLD_MENU, PICKUP_GLASS, MOVE_TOOLS, semantic.PROPS))]
            pickup = function(item, 'pickup_floor_glass', FLOOR_GLASS_PICKUP, 'floor_glass', evidence)
            injuries = [builder.fact(item, 'effect', {'property': prop, 'direction': 'apply_during_glass_pickup'},
                                    evidence, 'floor_glass', ['item:direct'])
                        for prop in ('hand_scratch', 'hand_embedded_glass')]
            builder.fact(item, 'condition', {'predicate': FLOOR_GLASS_INJURY}, evidence, 'floor_glass',
                         ['item:direct'], applies_to_fact_refs=[pickup, *injuries])
            builder.fact(item, 'condition', {'predicate': FLOOR_GLASS_PICKUP}, evidence, 'floor_glass',
                         ['item:direct'], applies_to_fact_refs=injuries)
        if item.startswith('Base.') and item[5:] in paint_types | {'Paintbrush'}:
            evidence = [declaration(item), *(refs[p] for p in (PAINT_MENU, PAINT_CURSOR, PAINT_ACTION, SIGN_ACTION))]
            for name in ('paint_supported_surface', 'paint_wall_sign'):
                fid = function(item, name, PAINTING, 'surface_painting', evidence)
                builder.fact(item, 'condition', {'predicate': PAINT_ACTIONS},
                    [*evidence, refs[semantic.BUILD_OBJECT]], 'surface_painting', ['item:direct'], applies_to_fact_refs=[fid])
        if (item in FIREARM_ITEMS and f.get('Type') == 'Weapon' and f.get('Ranged', '').lower() == 'true'
                and f.get('AmmoType') and set(f) <= FIREARM_FIELDS and set(conflicts) <= {'ModelWeaponPart'}):
            evidence = [declaration(item), refs[semantic.MENU], refs[FIREARM_RADIAL], refs[FIREARM],
                        refs[INSERT_MAGAZINE], refs[LOAD_MAGAZINE], *(refs[p] for p in RELOAD_ACTIONS)]
            function(item, 'rack_firearm', GUN_RACKING, 'firearm_controls', evidence)
            if f.get('MagazineType'):
                function(item, 'receive_firearm_magazine', MAGAZINE_LOADING, 'firearm_controls', evidence)
                function(item, 'eject_firearm_magazine', GUN_MAGAZINE_EJECTION, 'firearm_controls', evidence)
            else:
                function(item, 'load_firearm_rounds', GUN_ROUND_LOADING, 'firearm_controls', evidence)
                function(item, 'unload_firearm_rounds', GUN_ROUND_UNLOADING, 'firearm_controls', evidence)
            modes = f.get('FireModePossibilities', '').split('/')
            if len(modes) > 1:
                function(item, 'change_firearm_mode', GUN_FIRE_MODES, 'firearm_controls', evidence)
            mounts = [part for part, pf in fields.items() if pf.get('Type') == 'WeaponPart'
                      and item in {reader.qualify(part.split('.', 1)[0], x.strip()) for x in pf.get('MountOn', '').split(';')}]
            if mounts:
                part_evidence = evidence + [refs[WEAPON_UPGRADE], refs[WEAPON_REMOVAL], *(declaration(part) for part in sorted(mounts))]
                function(item, 'receive_weapon_upgrade', WEAPON_ATTACHMENT, 'firearm_controls', part_evidence)
                function(item, 'detach_weapon_upgrade', WEAPON_PART_REMOVAL, 'firearm_controls', part_evidence)
            if item in LEGACY_GUN_ITEMS:
                function(item, 'use_alternate_reload_controls', LEGACY_GUN_CONTROLS, 'legacy_firearm_controls',
                    [declaration(item), refs[semantic.MENU], refs[FIREARM], *(refs[p] for p in LEGACY_RELOAD_SOURCES)])
            base.setdefault('firearm_control_sources', {})[item] = {'declaration': f, 'repeated_visual_parts': conflicts.get('ModelWeaponPart', []),
                'compatible_parts': sorted(mounts), 'modes': modes if len(modes) > 1 else [],
                'source_paths': [semantic.MENU, FIREARM_RADIAL, FIREARM, INSERT_MAGAZINE, LOAD_MAGAZINE, *RELOAD_ACTIONS, WEAPON_UPGRADE, WEAPON_REMOVAL]}
        if f.get('Type') == 'Weapon' and f.get('Ranged', '').lower() == 'true' and f.get('AmmoType'):
            inv.require('Hook.Attack.Add(ISReloadWeaponAction.attackHook)' in texts[FIREARM]
                        and 'Events.OnWeaponSwingHitPoint.Add(ISReloadWeaponAction.onShoot)' in texts[FIREARM], 'firearm hook changed')
            firing = function(item, 'fire_ammunition', FIRING, 'firearm_operation', [declaration(item), refs[FIREARM]],
                     ['item:direct', 'activity:combat'])
            if item in base.get('firearm_control_sources', {}):
                builder.fact(item, 'condition', {'predicate': GUN_FIRING_CYCLE},
                    [declaration(item), refs[FIREARM], refs[FIREARM_RADIAL]], 'firearm_controls',
                    ['item:direct', 'activity:combat'], applies_to_fact_refs=[firing])
        if (f.get('Type') == 'Weapon' and not f.get('PhysicsObject')
                and f.get('Ranged', '').lower() != 'true' and not {'Type', 'PhysicsObject', 'Ranged'} & conflicts.keys()):
            function(item, 'melee_attack', MELEE, 'melee', [declaration(item), refs[FIREARM]],
                     ['item:direct', 'activity:combat'])
        if (f.get('Type') == 'Weapon' and 'Axe' in f.get('Categories', '').split(';')
                and 'ChopTree' in f.get('Tags', '').split(';')):
            inv.require('self.tree:WeaponHit(self.character, self.axe)' in texts[CHOP]
                        and 'ISChopTreeAction:new(playerObj, tree)' in texts[WORLD_MENU], 'chop consumer changed')
            function(item, 'chop_tree', CHOPPING, 'vegetation_tools',
                     [declaration(item), refs[WORLD_MENU], refs[CHOP], refs[CHOP_CURSOR], refs[semantic.BUILD_OBJECT]])
        if f.get('Type') == 'Weapon' and not {'Type', 'Tags'} & conflicts.keys():
            tags = set(f.get('Tags', '').split(';'))
            if 'CutPlant' in tags:
                function(item, 'cut_bushes_and_vines', PLANT_CUTTING, 'vegetation_tools',
                         [declaration(item), *[refs[p] for p in (WORLD_MENU, PLANT_CURSOR, REMOVE_BUSH, OBJECT_COMMANDS, semantic.BUILD_OBJECT)]])
            if 'Hammer' in tags:
                function(item, 'build_wooden_barricade', WOOD_BARRICADE, 'barricade_controls',
                         [declaration(item), refs[WORLD_MENU], refs[BARRICADE], refs[OBJECT_COMMANDS]])
            if 'RemoveBarricade' in tags:
                function(item, 'remove_barricade', WOOD_UNBARRICADE, 'barricade_controls',
                         [declaration(item), refs[WORLD_MENU], refs[UNBARRICADE], refs[OBJECT_COMMANDS]])
            if item in {'Base.Sledgehammer', 'Base.Sledgehammer2'}:
                function(item, 'destroy_structure', STRUCTURE_DESTRUCTION, 'structure_destruction',
                         [declaration(item), *[refs[p] for p in RULES['structure_destruction']['source_refs']]])
        if item in GROUND_TOOLS and f.get('Type') == 'Weapon' and not {'Type', 'Tags'} & conflicts.keys():
            evidence = [declaration(item), *[refs[p] for p in RULES['ground_tools']['source_refs']]]
            tags = set(f.get('Tags', '').split(';'))
            if 'DigPlow' in tags:
                function(item, 'dig_furrow', FURROW_DIGGING, 'ground_tools', evidence)
                function(item, 'remove_farm_plant', PLANT_REMOVAL, 'ground_tools', evidence)
            if 'TakeDirt' in tags:
                function(item, 'collect_ground_into_bag', GROUND_FILL, 'ground_tools', evidence)
            if 'DigGrave' in tags:
                function(item, 'dig_grave', GRAVE_DIGGING, 'ground_tools', evidence)
                function(item, 'fill_grave', GRAVE_FILLING, 'ground_tools', evidence)
        if not conflicts:
            operations = []
            if item in {'Base.EngineParts', 'Base.Wrench'}:
                paths = [VEHICLE_MECHANICS, VEHICLE_MENU, VEHICLE_USE_MENU, VEHICLE_CALLBACKS, VEHICLE_COMMANDS, *ENGINE_ACTIONS]
                operations.append(('repair_vehicle_engine', ENGINE_REPAIR, paths))
                if item == 'Base.Wrench':
                    operations.append(('salvage_vehicle_engine', ENGINE_SALVAGE, paths))
            if item in {'Base.Jack', 'Base.LugWrench', 'Base.Screwdriver'}:
                selected = [p for p in VEHICLE_TOOL_TEMPLATES
                    if re.search(r'\btype\s*=\s*' + re.escape(item) + r'\s*,', reader.mask(texts[p]))]
                if selected:
                    paths = [VEHICLE_MECHANICS, VEHICLE_MENU, VEHICLE_CALLBACKS, VEHICLE_COMMANDS,
                             VEHICLE_INSTALL, VEHICLE_UNINSTALL, *selected]
                    operations.append(('service_vehicle_parts', VEHICLE_TOOL_USE, paths))
                    base.setdefault('vehicle_tool_sources', {})[item] = {'templates': selected}
            if item == 'Base.Screwdriver' and f.get('Tags') == 'Screwdriver':
                operations.append(('manage_weapon_attachments', WEAPON_ATTACHMENT_TOOL, [semantic.MENU, WEAPON_UPGRADE, WEAPON_REMOVAL]))
            if item == 'Base.BucketPlasterFull' and f.get('Type') == 'Drainable':
                operations.append(('plaster_supported_structure', PLASTER_USE,
                    [PAINT_MENU, PAINT_CURSOR, PLASTER_ACTION, PAINTING_REFERENCE, semantic.BUILD_OBJECT, OBJECT_COMMANDS]))
            if item == 'Base.CompostBag' and f.get('Type') == 'Drainable':
                operations.append(('transfer_compost', COMPOST_TRANSFER, [WORLD_MENU, *COMPOST_ACTIONS]))
            if item == 'Base.EmptySandbag' and f.get('Type') == 'Container' and f.get('Tags') == 'HoldDirt':
                operations.append(('receive_compost', COMPOST_TRANSFER, [WORLD_MENU, *COMPOST_ACTIONS]))
            if item == 'Base.Sheet' and f.get('Type') == 'Normal':
                for name in ('install_sheet_curtain', 'control_sheet_curtain'):
                    operations.append((name, CURTAIN_USE, [WORLD_MENU, *CURTAIN_ACTIONS, OBJECT_COMMANDS, semantic.BUILD_UTIL]))
            if item == 'Base.BlowTorch' and f.get('Type') == 'Drainable':
                operations.append(('dismantle_burnt_vehicle', BURNT_VEHICLE_USE,
                    [VEHICLE_USE_MENU, BLACKSMITH_MENU, BURNT_VEHICLE, VEHICLE_COMMANDS]))
            for name, predicate, paths in operations:
                function(item, name, predicate, 'equipment_controls', [declaration(item), *[refs[p] for p in paths]])
            if operations:
                base.setdefault('equipment_control_sources', {})[item] = {'functions': [n for n, _, _ in operations],
                    'predicates': [p for _, p, _ in operations],
                    'observation_refs': sorted({declaration(item), *[refs[p] for _, _, paths in operations for p in paths]})}
        if item in {'Base.Saw', 'Base.GardenSaw', 'Base.Screwdriver'} and not conflicts:
            function(item, 'dismantle_built_object', THUMPABLE_SCRAP, 'thumpable_tools',
                     [declaration(item), *[refs[p] for p in RULES['thumpable_tools']['source_refs']]])
        if item == 'Base.Nails' and f.get('Type') == 'Normal' and not conflicts:
            function(item, 'build_wooden_barricade', WOOD_BARRICADE, 'barricade_controls',
                [declaration(item), refs[WORLD_MENU], refs[BARRICADE], refs[OBJECT_COMMANDS]])
        if item == 'Base.HammerStone' and f.get('Type') == 'Weapon' and not conflicts:
            evidence = [declaration(item), refs[semantic.BUILD_ACTION], refs[WORLD_MENU]]
            effect = builder.fact(item, 'effect', {'property': 'held_stone_hammer_condition', 'direction': 'may_decrease_on_build'},
                                  evidence, 'thumpable_tools', ['item:direct'])
            builder.fact(item, 'condition', {'predicate': STONE_TOOL_WEAR}, evidence,
                         'thumpable_tools', ['item:direct'], applies_to_fact_refs=[effect])
        if item == 'Base.FishingNet' and f.get('Type') == 'Normal' and not conflicts:
            evidence = [declaration(item), *[refs[p] for p in RULES['net_controls']['source_refs']]]
            for name, predicate in (('place_fishing_net', NET_PLACEMENT), ('check_fishing_net', NET_CHECKING), ('remove_fishing_net', NET_REMOVAL)):
                function(item, name, predicate, 'net_controls', evidence)
        if item in {'Base.MetalBar', 'Base.SheetMetal'} and f.get('Type') in {'Weapon', 'Normal'} and not conflicts:
            function(item, 'build_metal_barricade', METAL_BARRICADE, 'barricade_controls',
                [declaration(item), refs[WORLD_MENU], refs[BARRICADE], refs[OBJECT_COMMANDS]])
        if item == 'Base.BlowTorch' and f.get('Type') == 'Drainable' and not conflicts:
            for name, predicate in (('build_metal_barricade', METAL_BARRICADE), ('remove_metal_barricade', METAL_UNBARRICADE)):
                function(item, name, predicate, 'barricade_controls',
                         [declaration(item), refs[WORLD_MENU], refs[BARRICADE], refs[UNBARRICADE], refs[OBJECT_COMMANDS]])
        if item in {'Base.Spoon', 'Base.Fork'} and not conflicts and f.get('Type') == 'Weapon':
            function(item, 'serve_as_eating_utensil', MEAL_UTENSIL, 'meal_utensils', [declaration(item), refs[semantic.EAT]])
        conflicts = property_readings[item][1]
        short = item.split('.', 1)[1]
        try:
            alcohol = float(f.get('AlcoholPower', '0')) > 0
        except ValueError:
            alcohol = False
        if alcohol:
            evidence = [declaration(item), refs[HEALTH], refs[DISINFECT]]
            disinfect = function(item, 'disinfect_wound', DISINFECTION, 'health_actions', evidence)
            if item in {'Base.Disinfectant', 'Base.AlcoholWipes', 'Base.AlcoholedCottonBalls'} and f.get('Type') == 'Drainable':
                function(item, 'consolidate_drainable_supplies', MEDICAL_CONSOLIDATION, 'medical_consolidation',
                         [declaration(item), refs[semantic.MENU], refs[CONSOLIDATE]])
                alcohol = builder.fact(item, 'effect', {'property': 'wound_alcohol_level', 'direction': 'increase'},
                                       evidence, 'health_actions', ['item:direct'])
                builder.fact(item, 'condition', {'predicate': DISINFECTION}, evidence, 'health_actions',
                             ['item:direct'], applies_to_fact_refs=[alcohol])
                if float(f['AlcoholPower']) * 13 - 5 > 0:
                    pain = builder.fact(item, 'effect', {'property': 'additional_pain', 'direction': 'increase'},
                                        evidence, 'health_actions', ['item:direct'])
                    for predicate in (DISINFECTION, DISINFECTION_ADMIN_PAIN):
                        builder.fact(item, 'condition', {'predicate': predicate}, evidence, 'health_actions',
                                     ['item:direct'], applies_to_fact_refs=[pain])
            if f.get('Type') in {'Food', 'Drainable'}:
                builder.fact(item, 'condition', {'predicate': DISINFECTION_USE}, evidence, 'health_actions',
                             ['item:direct'], applies_to_fact_refs=[disinfect])
        if short in {'Splint', 'Plank', 'TreeBranch', 'WoodenStick', 'RippedSheets'}:
            function(item, 'apply_splint', SPLINTING, 'health_actions',
                     [declaration(item), refs[HEALTH], refs[SPLINT]])
            evidence = [declaration(item), refs[HEALTH], refs[SPLINT]]
            function(item, 'remove_applied_splint', SPLINT_REMOVAL, 'splint_lifecycle', evidence)
            fid = builder.fact(item, 'effect', {'property': 'splint_factor', 'direction': 'set_doctor_half'}, evidence, 'splint_lifecycle', ['item:direct'])
            builder.fact(item, 'condition', {'predicate': SPLINTING}, evidence, 'splint_lifecycle', ['item:direct'], applies_to_fact_refs=[fid])
        if item in {'Base.Needle', 'Base.Thread', 'Base.SutureNeedle'} or 'SewingNeedle' in f.get('Tags', '').split(';'):
            function(item, 'stitch_wound', STITCHING, 'health_actions',
                     [declaration(item), refs[HEALTH], refs[STITCH]])
        if short in {'SutureNeedleHolder', 'Tweezers'} or 'RemoveGlass' in f.get('Tags', '').split(';'):
            function(item, 'remove_embedded_glass', GLASS_REMOVAL, 'health_actions',
                     [declaration(item), refs[HEALTH], refs[REMOVE_GLASS]])
        if short in {'SutureNeedleHolder', 'Tweezers'} or 'RemoveBullet' in f.get('Tags', '').split(';'):
            function(item, 'remove_embedded_bullet', BULLET_REMOVAL, 'health_actions',
                     [declaration(item), refs[HEALTH], refs[REMOVE_BULLET]])
        if short in POULTICES:
            function(item, 'apply_poultice', POULTICE_USE, 'health_actions',
                     [declaration(item), refs[HEALTH], refs[POULTICES[short]]])
        medical_effects = []
        if item in {'Base.Needle', 'Base.Thread', 'Base.SutureNeedle'} or 'SewingNeedle' in f.get('Tags', '').split(';'):
            medical_effects.append(('stitched_state', 'set_true', STITCHING, STITCH))
        if short in {'SutureNeedleHolder', 'Tweezers'} or 'RemoveGlass' in f.get('Tags', '').split(';'):
            medical_effects.append(('embedded_glass', 'remove', GLASS_REMOVAL, REMOVE_GLASS))
        if short in {'SutureNeedleHolder', 'Tweezers'} or 'RemoveBullet' in f.get('Tags', '').split(';'):
            medical_effects.append(('embedded_bullet', 'remove', BULLET_REMOVAL, REMOVE_BULLET))
        if short in POULTICES:
            medical_effects.append(('poultice_factor', 'set_doctor_random', POULTICE_USE, POULTICES[short]))
        for prop, direction, predicate, action in medical_effects:
            evidence = [declaration(item), refs[HEALTH], refs[action]]
            fid = builder.fact(item, 'effect', {'property': prop, 'direction': direction}, evidence,
                               'medical_action_outcomes', ['item:direct'])
            builder.fact(item, 'condition', {'predicate': predicate}, evidence, 'medical_action_outcomes',
                         ['item:direct'], applies_to_fact_refs=[fid])
        if medical_effects:
            evidence = [declaration(item), refs[HEALTH], *(refs[row[3]] for row in medical_effects)]
            panic = builder.fact(item, 'effect', {'property': 'treatment_panic', 'direction': 'add_50'}, evidence,
                                 'medical_action_outcomes', ['item:direct'])
            builder.fact(item, 'condition', {'predicate': MEDICAL_PANIC}, evidence, 'medical_action_outcomes',
                         ['item:direct'], applies_to_fact_refs=[panic])
        if item == 'Base.SutureNeedleHolder' and not conflicts:
            function(item, 'assist_stitching', SUTURE_ASSISTANCE, 'medical_action_outcomes',
                     [declaration(item), refs[HEALTH], refs[STITCH]])
        if f.get('HairDye', '').lower() == 'true' and not conflicts:
            evidence = [declaration(item), refs[semantic.MENU], refs[semantic.DYE]]
            previous = original_functions.get((item, 'dye_hair_or_beard'))
            if previous:
                builder.fact(item, 'condition', {'predicate': DYE_APPLICATION}, evidence,
                             'appearance_actions', ['item:direct'], applies_to_fact_refs=[previous['fact_id']])
            else:
                function(item, 'dye_hair_or_beard', DYE_APPLICATION, 'appearance_actions', evidence)
            fid = builder.fact(item, 'effect', {'property': 'hair_or_beard_color', 'direction': 'set_dye_color'},
                               evidence, 'appearance_actions', ['item:direct'])
            builder.fact(item, 'condition', {'predicate': DYE_APPLICATION}, evidence,
                         'appearance_actions', ['item:direct'], applies_to_fact_refs=[fid])
        if not conflicts and (item in {'Base.Hairgel', 'Base.Razor', 'Base.Scissors'}
                or set(f.get('Tags', '').split(';')) & {'Razor', 'Scissors'}):
            evidence = [declaration(item), refs[CLOCK_CHARACTER], refs[HAIR_CUT], refs[BEARD_TRIM],
                        refs[semantic.WEAR], refs[WORLD_MENU]]
            function(item, 'groom_hair', HAIR_GROOMING, 'appearance_actions', evidence)
            if item != 'Base.Hairgel':
                function(item, 'groom_beard', BEARD_GROOMING, 'appearance_actions', evidence)
        if item == 'Base.Mirror' and f.get('Type') == 'Normal' and not conflicts:
            function(item, 'support_makeup_mirror', MAKEUP_LIFECYCLE, 'appearance_actions',
                     [declaration(item), refs[semantic.MENU], refs[MAKEUP_UI], refs[MAKEUP_DEFINITIONS]])
        if f.get('MakeUpType') in {'Eyes', 'Lips', 'Foundation'} and not conflicts:
            evidence = [declaration(item), refs[semantic.MENU], refs[MAKEUP_UI], refs[MAKEUP_DEFINITIONS]]
            functions = [fact['fact_id'] for fact in builder.facts.values() if fact['item_id'] == item
                         and fact['payload'].get('function') in {'apply_eye_makeup', 'apply_lip_makeup', 'apply_makeup'}]
            for fid in functions:
                builder.fact(item, 'condition', {'predicate': MAKEUP_LIFECYCLE}, evidence,
                             'appearance_actions', ['item:direct'], applies_to_fact_refs=[fid])
            function(item, 'remove_registered_makeup', MAKEUP_LIFECYCLE, 'appearance_actions', evidence)
        if not {'CanStoreWater', 'IsWaterSource', 'ReplaceOnUseOn', 'ReplaceTypes'} & conflicts.keys():
            filled = water_form(item, fields)
            if filled:
                evidence = [declaration(item), declaration(filled), refs[WORLD_MENU], refs[TAKE_WATER], refs[semantic.TRANSFER], refs[OBJECT_COMMANDS]]
                function(item, 'store_water', WATER_STORAGE, 'water_storage', evidence)
                carrying = function(item, 'carry_water', WATER_STORAGE, 'water_storage', evidence)
                builder.fact(item, 'condition', {'predicate': CARRYING}, evidence, 'water_storage',
                             ['item:direct'], applies_to_fact_refs=[carrying])
                transfer_evidence = [declaration(item), declaration(filled), refs[semantic.MENU], refs[TRANSFER_WATER], refs[semantic.TRANSFER]]
                function(item, 'receive_poured_water', WATER_TRANSFER, 'water_consumers', transfer_evidence)
                base.setdefault('water_container_sources', {})[item] = {'filled_item': filled,
                    'filled_declaration': fields[filled], 'is_filled_source': filled == item,
                    'observation_refs': sorted(set(evidence + transfer_evidence))}
                if filled == item:
                    function(item, 'pour_water_into_container', WATER_TRANSFER, 'water_consumers', transfer_evidence)
                    function(item, 'supply_world_water_storage', WORLD_WATER_TRANSFER, 'water_consumers',
                             [declaration(item), refs[WORLD_MENU], refs[ADD_WATER]])
                    crop_evidence = [declaration(item), refs[FARM_MENU], refs[WATER_PLANT], refs[FARM_CLIENT], refs[FARM_SYSTEM], refs[FARM_COMMANDS], refs[PLANT]]
                    function(item, 'water_seeded_crop', CROP_WATERING, 'water_consumers', crop_evidence)
                    effect = builder.fact(item, 'effect', {'property': 'crop_water_level', 'direction': 'increase_five_per_use'}, crop_evidence,
                                          'water_consumers', ['item:direct'])
                    builder.fact(item, 'condition', {'predicate': CROP_WATERING}, crop_evidence, 'water_consumers',
                                 ['item:direct'], applies_to_fact_refs=[effect])
                    function(item, 'wash_vehicle_blood', VEHICLE_WASHING, 'water_consumers',
                             [declaration(item), refs[VEHICLE_USE_MENU], refs[WASH_VEHICLE], refs[VEHICLE_COMMANDS]])
                    drinking = [f['fact_id'] for f in base['semantic']['facts'] if f['item_id'] == item and
                                (f['payload'] == {'function': 'drink_stored_water'} or f['fact_kind'] == 'effect' and
                                 f['payload'].get('property') in {'thirst', 'poison_level'})]
                    if drinking:
                        builder.fact(item, 'condition', {'predicate': WATER_DRINKING},
                                     [declaration(item), refs[semantic.MENU], refs[semantic.DRINK], refs[semantic.TRANSFER]],
                                     'water_consumers', ['item:direct', 'activity:expenditure'], applies_to_fact_refs=drinking)
                if filled != item:
                    base.setdefault('water_filling_relations', {}).setdefault(filled, []).append({
                        'empty_item': item, 'filled_item': filled, 'observation_refs': sorted(set(evidence)),
                        'declaration': {k: f.get(k) for k in ('CanStoreWater', 'IsWaterSource', 'ReplaceOnUseOn', 'ReplaceTypes')},
                        'consumer': 'onTakeWater -> getReplaceType(WaterSource) -> InventoryItemFactory.CreateItem -> ISTakeWaterAction',
                        'transition': 'Copies condition/favorite, transfers the old item, then on start inserts the new item, preserves either hand holding the old item and removes the old item. Progress updates UsedDelta; validity requires an item container and remaining source water. Stopping can leave a partial fill and still propagates taint.',
                        'water_debit': 'The item-source command matches item ID. The ordinary source command checks the submitted index bounds but iterates useWater over every object on the square; it does not address only the submitted object.'})
        if (item in {'farming.GardeningSprayMilk', 'farming.GardeningSprayCigarettes'} and not conflicts
                and f.get('Type') == 'Drainable' and f.get('UseDelta') == '0.1'
                and f.get('ReplaceOnDeplete') == 'GardeningSprayEmpty'):
            mildew = item.endswith('Milk')
            treatment_evidence = [declaration(item), refs[FARM_MENU], refs[CURE_MILDEW if mildew else CURE_FLIES],
                                  refs[FARM_CLIENT], refs[FARM_SYSTEM], refs[FARM_COMMANDS], refs[PLANT]]
            function(item, 'treat_crop_mildew' if mildew else 'treat_crop_flies', SPRAY_TREATMENT, 'crop_treatment', treatment_evidence)
            effect = builder.fact(item, 'effect', {'property': 'crop_mildew_level' if mildew else 'crop_flies_level', 'direction': 'decrease'},
                                  treatment_evidence, 'crop_treatment', ['item:direct'])
            builder.fact(item, 'condition', {'predicate': SPRAY_TREATMENT}, treatment_evidence, 'crop_treatment',
                         ['item:direct'], applies_to_fact_refs=[effect])
        if (item, 'store_and_retrieve_items') in original_functions:
            function(item, 'carry_stored_items', CARRYING, 'container_carrying',
                     [declaration(item), refs[semantic.TRANSFER]], ['activity:storage'])
            if f.get('CanBeEquipped') == 'Back' and not {'Type', 'CanBeEquipped'} & conflicts.keys():
                function(item, 'wear_container_on_back', BACK_CONTAINER, 'back_container_wearing',
                         [declaration(item), refs[semantic.MENU], refs[semantic.WEAR], refs[BODY_LOCATIONS]])
        if (item, 'read_literature') in original_functions:
            evidence = [declaration(item), refs[semantic.MENU], refs[semantic.READ], refs[semantic.SKILLS]]
            old_function = original_functions[item, 'read_literature']
            builder.fact(item, 'condition', {'predicate': READ_SELECTION}, evidence, 'literature_selection',
                         ['activity:reading', 'item:direct'], applies_to_fact_refs=[old_function['fact_id']])
            if not f.get('SkillTrained'):
                old_function = original_functions[item, 'read_literature']
                eligibility = next(g for g in base['semantic']['facts'] if g['item_id'] == item and g['fact_kind'] == 'condition'
                                   and old_function['fact_id'] in g['applies_to_fact_refs'])
                for field, property_name in [('BoredomChange', 'boredom'), ('StressChange', 'stress'), ('UnhappyChange', 'unhappiness')]:
                    try:
                        negative = float(f.get(field, '0')) < 0
                    except ValueError:
                        negative = False
                    if negative:
                        mood = builder.fact(item, 'effect', {'property': property_name, 'direction': 'cap_at_reading_start'},
                                            evidence, 'reading_mood', ['activity:reading'])
                        for predicate in (READ_MOOD, eligibility['payload']['predicate']):
                            builder.fact(item, 'condition', {'predicate': predicate}, evidence, 'reading_mood',
                                         ['activity:reading'], applies_to_fact_refs=[mood])
        if ((item, 'read_literature') in original_functions and f.get('NumberOfPages', '').isdigit()
                and int(f['NumberOfPages']) > 0):
            evidence = [declaration(item), refs[semantic.MENU], refs[semantic.READ], refs[semantic.SKILLS]]
            progress = builder.fact(item, 'effect', {'property': 'reading_page_progress', 'direction': 'update'},
                                    evidence, 'reading_progress', ['activity:reading'])
            builder.fact(item, 'condition', {'predicate': READ_PROGRESS}, evidence, 'reading_progress',
                         ['activity:reading'], applies_to_fact_refs=[progress])
            old_function = original_functions[item, 'read_literature']
            eligibility = next(f for f in base['semantic']['facts'] if f['item_id'] == item
                               and f['fact_kind'] == 'condition' and old_function['fact_id'] in f['applies_to_fact_refs'])
            builder.fact(item, 'condition', eligibility['payload'], evidence, 'reading_progress',
                         ['activity:reading'], applies_to_fact_refs=[progress])
            builder.fact(item, 'state', {'state': 'reading_page_count', 'value': int(f['NumberOfPages'])},
                         evidence, 'reading_parameters', ['activity:reading'])
            skill, level = f.get('SkillTrained'), f.get('LvlSkillTrained')
            if skill and level in {'1', '3', '5', '7', '9'}:
                slot = (int(level) + 1) // 2
                values = re.findall(r'^SkillBook\["' + re.escape(skill) + r'"\]\.maxMultiplier' + str(slot) + r'\s*=\s*([0-9]+);',
                                    texts[semantic.SKILLS], re.M)
                if len(values) == 1:
                    maximum = builder.fact(item, 'state', {'state': 'skill_book_max_multiplier', 'value': int(values[0])},
                                           evidence, 'reading_parameters', ['activity:reading'])
                    builder.fact(item, 'condition', {'predicate': READ_MAXIMUM}, evidence, 'reading_parameters',
                                 ['activity:reading'], applies_to_fact_refs=[maximum])
                    step = builder.fact(item, 'state', {'state': 'skill_book_progress_step', 'value': 10},
                                        evidence, 'reading_parameters', ['activity:reading'])
                    old_effects = {g['fact_id'] for g in base['semantic']['facts'] if g['item_id'] == item
                                   and g['payload'] == {'property': skill + '_experience_multiplier', 'direction': 'increase'}}
                    for qualifier in base['semantic']['facts']:
                        if qualifier['item_id'] == item and old_effects.intersection(qualifier.get('applies_to_fact_refs', [])):
                            builder.fact(item, 'condition', qualifier['payload'], evidence, 'reading_parameters',
                                         ['activity:reading'], applies_to_fact_refs=[maximum, step])
        if (item, 'eat_food') in original_functions:
            original = original_functions[item, 'eat_food']
            builder.fact(item, 'condition', {'predicate': CONSUMING},
                         [declaration(item), refs[semantic.MENU], refs[semantic.EAT]], 'native_food_conditions',
                         ['activity:ingestion'], applies_to_fact_refs=[original['fact_id']])
        if (f.get('Type') == 'Food' and not {'CantEat', 'CustomContextMenu', 'CustomMenuOption'} & conflicts.keys()
                and f.get('CantEat', '').lower() != 'true'
                and f.get('CustomContextMenu', '') in {'', 'Drink'} and not f.get('CustomMenuOption')
                and (item, 'eat_food') not in existing_functions):
            inv.require('self.character:Eat(self.item, self.percentage)' in texts[semantic.EAT]
                        and 'CharacterActionAnims.Drink' in texts[semantic.EAT], 'consumption dispatch changed')
            name = 'drink_food_contents' if f.get('CustomContextMenu') == 'Drink' else 'consume_edible_food'
            function(item, name, CONSUMING, 'native_food_consumption', [declaration(item), refs[semantic.MENU], refs[semantic.EAT]],
                     ['item:direct', 'activity:ingestion'])
        if (f.get('Type') in {'Clothing', 'AlarmClockClothing', 'Container'} and f.get('ClothingItem')
                and not {'Type', 'ClothingItem', 'ClothingItemExtra', 'ClothingItemExtraOption'} & conflicts.keys()):
            options = [v.strip() for v in f.get('ClothingItemExtraOption', '').split(';') if v.strip()]
            destinations = [v.strip() for v in f.get('ClothingItemExtra', '').split(';') if v.strip()]
            variants = []
            if options and len(options) == len(destinations):
                for option, token in zip(options, destinations, strict=True):
                    if not re.fullmatch(r'[\w.]+', token):
                        continue
                    destination = reader.qualify(item.split('.', 1)[0], token)
                    dest = fields.get(destination, {})
                    location = dest.get('CanBeEquipped') if dest.get('Type') == 'Container' else dest.get('BodyLocation')
                    dest_conflicts = property_readings.get(destination, ({}, {}))[1]
                    if (dest.get('Type') in {'Clothing', 'AlarmClockClothing', 'Container'} and dest.get('ClothingItem')
                            and location in body_locations
                            and not {'Type', 'ClothingItem', 'BodyLocation', 'CanBeEquipped'} & dest_conflicts.keys()):
                        variants.append({'option': option, 'destination': destination, 'location': location,
                                         'observation_ref': declaration(destination)})
            if variants:
                evidence = [declaration(item), *(v['observation_ref'] for v in variants),
                            refs[semantic.MENU], refs[CLOTHING_EXTRA], refs[BODY_LOCATIONS]]
                function(item, 'switch_declared_clothing_form', CLOTHING_FORM, 'clothing_form', evidence)
                base.setdefault('clothing_form_relations', {})[item] = variants
        if f.get('Type') == 'Clothing' and f.get('BodyLocation') in body_locations and (item, 'wear_on_body') not in existing_functions:
            function(item, 'wear_configured_clothing', WEARING, 'clothing_wear',
                     [declaration(item), refs[semantic.MENU], refs[semantic.WEAR]], ['item:direct', 'activity:wearing'])
        if f.get('Type') == 'Clothing' and f.get('BodyLocation') in body_locations & BODY_LABELS.keys():
            evidence = [declaration(item), refs[BODY_LOCATIONS], refs[semantic.WEAR], refs[semantic.MENU]]
            slot = builder.fact(item, 'state', {'state': 'worn_location', 'value': f['BodyLocation']},
                                evidence, 'clothing_location', ['activity:wearing'])
            builder.fact(item, 'condition', {'predicate': WEARING}, evidence, 'clothing_location',
                         ['activity:wearing'], applies_to_fact_refs=[slot])
            builder.fact(item, 'condition', {'predicate': WEAR_ACTION}, evidence, 'clothing_wear',
                         ['activity:wearing'], applies_to_fact_refs=[slot])
    recipe_counts = defaultdict(int)
    for record in recipes:
        recipe_counts[record['module'], record['name']] += 1
    recipe_groups = reader.groups(texts[semantic.GROUPS])
    reader.expand_structural_groups(recipe_groups, fields, texts[semantic.CLOTHING])
    recover_participation(base, builder, recipes, fields, recipe_groups, declaration)
    forging = []
    # title, result, iron, time, skill, XP, weapon callback, extra material
    for title, output, amount, time, skill, xp, callback, extra in (
            ('Cooking Pot', 'Pot', 55, 190, 2, 20, False, []),
            ('Roasting Pan', 'Pot', 80, 220, 2, 25, False, []),
            ('Saucepan', 'Saucepan', 45, 170, 2, 20, False, []),
            ('Baking Tray', 'BakingTray', 85, 220, 2, 25, False, []),
            ('Baking Pan', 'BakingPan', 85, 220, 2, 25, False, []),
            ('Pan', 'Pan', 30, 220, 2, 20, True, []),
            ('Letter Opener', 'LetterOpener', 23, 120, 3, 15, True, []),
            ('Scissors', 'Scissors', 12, 120, 3, 15, True, []),
            ('Sheet Metal', 'SheetMetal', 110, 190, 4, 25, False, []),
            ('Suture Needle Holder', 'SutureNeedleHolder', 13, 150, 5, 20, False, []),
            ('Tweezers', 'Tweezers', 3, 120, 5, 10, False, []),
            ('Suture Needle', 'SutureNeedle', 9, 150, 6, 15, False, []),
            ('Metal Drum', 'MetalDrum', 100, 250, 6, 25, False, []),
            ('Kitchen Knife', 'KitchenKnife', 15, 180, 7, 15, True, ['Plank']),
            ('Saw', 'Saw', 55, 250, 7, 25, False, ['Plank']),
            ('Hunting Knife', 'HuntingKnife', 50, 180, 8, 20, True, ['Plank']),
            ('9mm Bullets Mold', '9mmBulletsMold', 30, 200, 8, 25, False, []),
            ('308 Bullets Mold', '308BulletsMold', 30, 200, 8, 25, False, []),
            ('223 Bullets Mold', '223BulletsMold', 30, 200, 8, 25, False, []),
            ('Shotgun Shells Mold', 'ShotgunShellsMold', 30, 200, 8, 25, False, []),
            ('Axe', 'Axe', 170, 300, 10, 25, True, ['Handle']),
            ('Sledgehammer', 'Sledgehammer', 170, 300, 10, 25, True, ['Handle'])):
        forging.append(('Make ' + title, ['IronIngot=' + str(amount), *extra, 'keep BallPeenHammer', 'keep Tongs',
            'NearItem:Anvil', 'Result:' + output, 'Time:' + str(time) + '.0', 'Category:Smithing',
            'SkillRequired:Blacksmith=' + str(skill), 'OnGiveXP:Recipe.OnGiveXP.Blacksmith' + str(xp),
            *(['OnCreate:BSItem_OnCreate'] if callback else []), 'NeedToBeLearn:true']))
    for title, output, time in (('Crowbar', 'Crowbar', 300), ('Golfclub', 'Golfclub', 250)):
        forging.append(('Make ' + title, ['MetalBar', 'keep BallPeenHammer', 'keep Tongs', 'NearItem:Anvil',
            'Result:' + output, 'Time:' + str(time) + '.0', 'Category:Smithing', 'SkillRequired:Blacksmith=9',
            'OnGiveXP:Recipe.OnGiveXP.Blacksmith25', 'OnCreate:BSItem_OnCreate', 'NeedToBeLearn:true']))
    for title, output in (('Nails', 'Nails=2'), ('Paperclips', 'Paperclip=10')):
        forging.append(('Make ' + title, ['IronIngot=20', 'keep [Recipe.GetItemTypes.Hammer]', 'NearItem:Anvil',
            'Result:' + output, 'Time:120.0', 'Category:Smithing', 'SkillRequired:Blacksmith=3',
            'OnGiveXP:Recipe.OnGiveXP.Blacksmith10', 'NeedToBeLearn:true']))
    forging.append(('Make Butter Knife', ['IronIngot=14', 'keep [Recipe.GetItemTypes.Hammer]', 'keep Tongs',
        'NearItem:Anvil', 'Result:ButterKnife', 'Time:180.0', 'Category:Smithing', 'SkillRequired:Blacksmith=3',
        'OnGiveXP:Recipe.OnGiveXP.Blacksmith15', 'OnCreate:BSItem_OnCreate', 'NeedToBeLearn:true']))
    for title, output, amount, hammer, callback in (
            ('Ball Peen Hammer', 'BallPeenHammer', 40, '[Recipe.GetItemTypes.Hammer]', True),
            ('Tongs', 'Tongs', 30, '[Recipe.GetItemTypes.Hammer]', False),
            ('Hammer', 'Hammer', 40, 'BallPeenHammer', True)):
        forging.append(('Make ' + title, ['IronIngot=' + str(amount), 'keep ' + hammer, 'NearItem:Anvil',
            'Result:' + output, 'Time:170.0', 'SkillRequired:Blacksmith=4', 'Category:Smithing',
            'OnGiveXP:Recipe.OnGiveXP.Blacksmith20', *(['OnCreate:BSItem_OnCreate'] if callback else []), 'NeedToBeLearn:true']))
    for title, output, amount, powder, mold in (
            ('9mm Bullets', 'Bullets9mm', 22, 2, '9mmBulletsMold'),
            ('Shotgun Shells', 'ShotgunShells', 25, 3, 'ShotgunShellsMold'),
            ('308 Bullets', '308Bullets', 23, 2, '308BulletsMold'),
            ('223 Bullets', '223Bullets', 23, 2, '223BulletsMold')):
        forging.append(('Make ' + title, ['IronIngot=' + str(amount), 'GunPowder=' + str(powder), 'keep ' + mold,
            'keep Tongs', 'NearItem:Anvil', 'Result:' + output + '=2', 'Time:180.0', 'Category:Smithing',
            'SkillRequired:Blacksmith=8', 'OnGiveXP:Recipe.OnGiveXP.Blacksmith15', 'NeedToBeLearn:true']))
    preparation = [(name, clauses, 'metal_forging', FORGE_PREPARATION) for name, clauses in forging]
    for title, inputs_, output, time, skill, xp in (
            ('Metal Pipe', ['IronIngot=40'], 'MetalPipe', 150, None, 10),
            ('Metal Bar', ['MetalPipe', 'IronIngot=10'], 'MetalBar', 150, 2, 10),
            ('Metal Sheet', ['SmallSheetMetal=4'], 'SheetMetal', 250, 4, 25),
            ('Small Metal Sheet', ['SheetMetal'], 'SmallSheetMetal=3', 250, 4, 25)):
        preparation.append(('Make ' + title, [*inputs_, 'BlowTorch=2', 'keep [Recipe.GetItemTypes.WeldingMask]',
            'Result:' + output, 'Time:' + str(time) + '.0', 'Category:Welding',
            *(['SkillRequired:MetalWelding=' + str(skill)] if skill is not None else []),
            'OnGiveXP:Recipe.OnGiveXP.MetalWelding' + str(xp), 'NeedToBeLearn:true'], 'welded_parts', WELDED_PARTS))
    preparation.extend([
        ('Make Mattress', ['keep [Recipe.GetItemTypes.SewingNeedle]', 'Thread=5', 'Sheet=5', 'Pillow=5',
            'Result:Mattress', 'Time:180.0', 'Category:Carpentry'], 'mattress_preparation', MATTRESS_PREPARATION),
        ('Slice Frog', ['keep [Recipe.GetItemTypes.SharpKnife]/MeatCleaver', 'Frog', 'Result:FrogMeat',
            'Sound:SliceMeat', 'Time:50.0', 'Category:Cooking', 'OnGiveXP:Recipe.OnGiveXP.Cooking10'], 'frog_preparation', FROG_PREPARATION),
        ('Get Wire Back', ['BrokenFishingNet', 'Result:Wire;3', 'Time:100.0', 'Category:Fishing',
            'NeedToBeLearn:true'], 'wire_recovery', WIRE_RECOVERY)])
    for count, title in ((2, 'Two'), (3, 'Three'), (4, 'Four')):
        fields_ = ['Category:Carpentry', 'OnCreate:Recipe.OnCreate.CreateLogStack']
        if count != 2:
            fields_.reverse()
        preparation.append(('Make ' + title + '-Log Stack', ['Log=' + str(count), '[Recipe.GetItemTypes.CraftLogStack]=2',
            'CanBeDoneFromFloor:true', 'Result:LogStacks' + str(count), 'Time:60.0', *fields_,
            'OnGiveXP:Recipe.OnGiveXP.None', 'Sound:LogAddToStack'], 'log_binding', LOG_BINDING))
        preparation.append(('Unstack Logs', ['LogStacks' + str(count), 'CanBeDoneFromFloor:true', 'Result:Log=' + str(count),
            'Time:60.0', 'OnCreate:Recipe.OnCreate.SplitLogStack', 'Category:Carpentry', 'OnGiveXP:Recipe.OnGiveXP.None',
            'Sound:LogRemoveFromStack'], 'log_binding', LOG_BINDING))
    for name, clauses, context, predicate in preparation:
        matches = [r for r in recipes if r['module'] == 'Base' and r['name'] == name and r['clauses'] == clauses]
        if len(matches) != 1:
            continue
        record = matches[0]
        participants, opaque = recipe_participants(record, fields, recipe_groups)
        # Wire;3 remains an uninterpreted result. Its exact plain input is still
        # admitted, with no fabricated result participant or yield claim.
        if opaque and not (context == 'wire_recovery' and opaque == ['Wire;3']):
            continue
        ref = builder.observe(record['path'], f"L{record['line']}-L{record['end_line']}:{name}",
                              {'recipe_name': name, 'raw': record['raw'], 'clauses': clauses, 'uninterpreted_result': opaque})
        for participant in participants:
            item, role = participant['item_id'], participant['role']
            if item not in targets or item not in fields or role not in {'input', 'keep'}:
                continue
            evidence = [declaration(item), ref, refs[semantic.CRAFT], refs[semantic.GROUPS]]
            builder.activity(item, context, 'tool' if role == 'keep' else 'material', evidence,
                             context, ['activity:crafting'], predicate)
            direct = ('unbundle_logs' if name == 'Unstack Logs' else
                      'prepare_frog_meat' if item == 'Base.Frog' else
                      'process_broken_fish_net' if item == 'Base.BrokenFishingNet' else None)
            if direct:
                function(item, direct, predicate, context, evidence)
    for module, name, clauses, context, predicate in FOOD_PREPARATION_RECIPES:
        matches = [r for r in recipes if r['module'] == module and r['name'] == name and r['clauses'] == clauses]
        if len(matches) != 1:
            continue
        record = matches[0]
        participants, opaque = recipe_participants(record, fields, recipe_groups)
        ref = builder.observe(record['path'], f"L{record['line']}-L{record['end_line']}:{name}",
                              {'recipe_name': name, 'raw': record['raw'], 'clauses': clauses,
                               'uninterpreted_numeric_clauses': opaque})
        for participant in participants:
            item, role = participant['item_id'], participant['role']
            if item not in targets or item not in fields or role not in {'input', 'destroy', 'keep'}:
                continue
            # A held mixing bowl is a vessel, not an inferred cutting tool.
            # Replaced baking trays/pots remain vessels even when destroyed.
            vessel = item in {'Base.Bowl', 'Base.BakingTray', 'Base.WaterPot', 'Base.WaterSaucepan', 'Base.Cone'}
            semantic_role = 'container' if vessel else 'tool' if role == 'keep' else 'ingredient' if context not in {'woodworking', 'pumpkin_carving'} else 'material'
            builder.activity(item, context, semantic_role,
                [declaration(item), ref, refs[semantic.CRAFT], refs[semantic.GROUPS], *import_evidence(builder, participant)],
                'food_preparation_recipes', ['activity:crafting'], predicate)
    for name, clauses, context, predicate in ITEM_TRANSFORMATION_RECIPES:
        matches = [r for r in recipes if r['module'] == 'Base' and r['name'] == name and r['clauses'] == clauses]
        if len(matches) != 1:
            continue
        record = matches[0]
        participants, opaque = recipe_participants(record, fields, recipe_groups)
        ref = builder.observe(record['path'], f"L{record['line']}-L{record['end_line']}:{name}",
            {'recipe_name': name, 'raw': record['raw'], 'clauses': clauses,
             'uninterpreted_numeric_clauses': opaque})
        for participant in participants:
            item, role = participant['item_id'], participant['role']
            if item not in targets or item not in fields or role not in {'input', 'destroy', 'keep'}:
                continue
            # Roles are assigned within these reviewed operations, not from
            # keep/destroy syntax alone. A kept light is the charge receiver.
            if context == 'battery_removal':
                semantic_role = 'power_receiver'
            elif context in {'candle_extinguishing', 'food_container_emptying', 'shotgun_modification', 'bottle_breaking', 'ammunition_disassembly'} and role != 'keep':
                semantic_role = 'transformation_target'
            elif context == 'blowtorch_refilling':
                semantic_role = 'transformation_target' if item == 'Base.BlowTorch' else 'fuel'
            elif context == 'candle_lighting':
                semantic_role = 'transformation_target' if item == 'Base.Candle' else 'tool'
            elif item in {'Base.Bowl', 'Base.BakingPan', 'Base.Pan', 'Base.BucketEmpty', 'Base.BucketWaterFull'} and context in {'food_preparation', 'plaster_preparation'}:
                semantic_role = 'container'
            elif role == 'keep':
                semantic_role = 'tool'
            elif context in {'food_preparation', 'food_portioning', 'watermelon_breaking'}:
                semantic_role = 'ingredient'
            else:
                semantic_role = 'material'
            evidence = [declaration(item), ref, refs[semantic.CRAFT], refs[semantic.GROUPS], *import_evidence(builder, participant)]
            if context == 'shotgun_modification':
                evidence.extend(refs[path] for path in LEGACY_RELOAD_SOURCES)
            builder.activity(item, context, semantic_role, evidence,
                'item_transformation_recipes', ['activity:crafting'], predicate)
            direct = {'candle_lighting': 'light_candle', 'candle_extinguishing': 'extinguish_candle',
                      'battery_removal': 'remove_device_battery'}.get(context)
            if direct and (context != 'candle_lighting' or item == 'Base.Candle'):
                function(item, direct, predicate, 'item_transformation_recipes', evidence)

    kit_recipes = []
    for timber in ('Plank = 3', 'Log = 2'):
        kit_recipes.append(('Make Campfire Kit', [timber,
            'RippedSheets/RippedSheetsDirty/Sheet/Book/Magazine/Newspaper/Twigs', 'Result:CampfireKit',
            'Time:50.0', 'Category:Survivalist'], 'campfire_kit_preparation', CAMP_KIT_PREPARATION))
    for peg in ('TentPeg = 4', 'Stake = 4'):
        kit_recipes.append(('Make Tent Kit', ['Tarp', peg, 'WoodenStick = 2', 'Result:CampingTentKit',
            'Time:120.0', 'Category:Survivalist'], 'tent_kit_making', TENT_KIT_PREPARATION))
    for name, clauses, context, predicate in kit_recipes:
        matches = [r for r in recipes if r['module'] == 'camping' and r['name'] == name and r['clauses'] == clauses]
        if len(matches) != 1:
            continue
        record = matches[0]
        participants, opaque = recipe_participants(record, fields, recipe_groups)
        ref = builder.observe(record['path'], f"L{record['line']}-L{record['end_line']}:{name}",
                              {'raw': record['raw'], 'clauses': clauses, 'uninterpreted_numeric_clauses': opaque})
        for participant in participants:
            item = participant['item_id']
            if item in targets and item in fields and participant['role'] == 'input':
                builder.activity(item, context, 'material',
                    [declaration(item), ref, refs[semantic.CRAFT], *import_evidence(builder, participant)],
                    'camping_kit_preparation', ['activity:crafting'], predicate)
    for name, output, amount, xp, extra in (('Make Shovel', 'Shovel', '90', '25', ['Handle']),
                                           ('Make Hand Shovel', 'HandShovel', '50', '20', [])):
        clauses = ['IronIngot=' + amount, *extra, 'keep [Recipe.GetItemTypes.Hammer]', 'keep Tongs',
            'NearItem:Anvil', 'Result:' + output, 'Time:200.0', 'Category:Smithing',
            'SkillRequired:Blacksmith=6', 'OnGiveXP:Recipe.OnGiveXP.Blacksmith' + xp, 'NeedToBeLearn:true']
        matches = [r for r in recipes if r['module'] == 'farming' and r['name'] == name and r['clauses'] == clauses]
        if len(matches) != 1:
            continue
        record = matches[0]
        participants, opaque = recipe_participants(record, fields, recipe_groups)
        if opaque:
            continue
        ref = builder.observe(record['path'], f"L{record['line']}-L{record['end_line']}:{name}",
                              {'raw': record['raw'], 'clauses': clauses})
        for participant in participants:
            item, role = participant['item_id'], participant['role']
            if item in targets and item in fields and role in {'input', 'keep'}:
                builder.activity(item, 'shovel_smithing', 'tool' if role == 'keep' else 'material',
                    [declaration(item), ref, refs[semantic.CRAFT], refs[semantic.GROUPS], *import_evidence(builder, participant)],
                    'shovel_smithing', ['activity:crafting'], SHOVEL_SMITHING)
    for plant, title, result, hidden in (
            ('Plantain', 'Plantain', 'PlantainCataplasm', []),
            ('Comfrey', 'Comfrey', 'ComfreyCataplasm', []),
            ('WildGarlic', 'Wild Garlic', 'WildGarlicCataplasm', ['IsHidden:true']),
            ('WildGarlic2', 'Wild Garlic', 'WildGarlicCataplasm', ['isHidden:true'])):
        clauses = ['keep [Recipe.GetItemTypes.MortarPestle]', plant + '=5', 'Result:' + result,
                   'Time:60.0', 'Category:Health', *hidden]
        matches = [r for r in recipes if r['module'] == 'Base' and r['name'] == 'Make ' + title + ' Poultice'
                   and r['clauses'] == clauses]
        if len(matches) != 1:
            continue
        record = matches[0]
        participants, opaque = recipe_participants(record, fields, recipe_groups)
        if opaque:
            continue
        ref = builder.observe(record['path'], f"L{record['line']}-L{record['end_line']}:{record['name']}",
                              {'raw': record['raw'], 'clauses': clauses})
        for participant in participants:
            item, role = participant['item_id'], participant['role']
            if item in targets and item in fields and role in {'input', 'keep'}:
                builder.activity(item, 'poultice_preparation', 'tool' if role == 'keep' else 'material',
                    [declaration(item), ref, refs[semantic.CRAFT], refs[semantic.GROUPS], refs[CRAFT_UI]],
                    'poultice_preparation', ['activity:crafting'], POULTICE_PREPARATION)
    baking_roles(builder, recipes, fields, recipe_groups, targets, declaration, refs)
    spear_roles(base, builder, recipes, fields, recipe_groups, targets, declaration, refs)
    for fabric, result in (('Denim', 'DenimStrips'), ('Leather', 'LeatherStrips')):
        for test in ('IsWorn', 'IsNotWorn'):
            clauses = ['[Recipe.GetItemTypes.RipClothing_' + fabric + ']', 'keep [Recipe.GetItemTypes.Scissors]',
                       'Result:' + result, 'RemoveResultItem:true', 'InSameInventory:true', 'Sound:ClothesRipping',
                       'Time:100.0', 'AnimNode:RipSheets', 'OnCreate:Recipe.OnCreate.RipClothing',
                       'OnTest:Recipe.OnTest.' + test]
            matches = [r for r in recipes if r['module'] == 'Base' and r['name'] == 'Rip Clothing' and r['clauses'] == clauses]
            if len(matches) != 1:
                continue
            record = matches[0]
            participants, opaque = reader.recipe_participants(record, fields, recipe_groups)
            if opaque:
                continue
            observation = builder.observe(record['path'], f"L{record['line']}-L{record['end_line']}:Rip Clothing",
                                          {'recipe_name': record['name'], 'raw': record['raw'], 'clauses': clauses})
            for participant in participants:
                item = participant['item_id']
                if item in targets and participant['role'] == 'keep':
                    builder.activity(item, 'fabric_recovery', 'tool',
                                     [declaration(item), observation, refs[semantic.GROUPS], refs[semantic.CLOTHING], refs[semantic.CRAFT]],
                                     'fabric_conditions', ['activity:crafting'], FABRIC_ACTION)
    bandage_recipes = []
    for name, material, result in (('Disinfect Rag', 'RippedSheets', 'AlcoholRippedSheets'),
                                   ('Disinfect Bandage', 'Bandage', 'AlcoholBandage')):
        bandage_recipes.append((name, ['destroy ' + material, '[Recipe.GetItemTypes.Liquor];10',
                                     'Result:' + result, 'Time:40.0', 'Category:Health']))
        for vessel, amount in (('WaterPot', '5'), ('WaterSaucepan', '10')):
            bandage_recipes.append((name, ['destroy ' + material, vessel + ';' + amount, 'CanBeDoneFromFloor:true',
                                         'Result:' + result, 'Time:100.0', 'Heat:-0.22', 'Category:Health']))
        bandage_recipes.append((name, [('destroy ' if material == 'Bandage' else '') + material,
                                     '[Recipe.GetItemTypes.Disinfectant]=3', 'Result:' + result, 'Time:40.0', 'Category:Health']))
    bandage_recipes.extend([
        ('Douse Cotton in Alcohol', ['[Recipe.GetItemTypes.Disinfectant]=1', 'destroy CottonBalls',
                                    'Result:AlcoholedCottonBalls', 'Time:20', 'Category:Health']),
        ('Put Alcohol on Cotton', ['destroy CottonBalls', '[Recipe.GetItemTypes.Liquor];10',
                                  'Result:AlcoholedCottonBalls', 'Time:40.0', 'Category:Health']),
    ])
    for name, clauses in bandage_recipes:
        matches = [r for r in recipes if r['module'] == 'Base' and r['name'] == name and r['clauses'] == clauses]
        if len(matches) != 1:
            continue
        record = matches[0]
        participants, opaque = recipe_participants(record, fields, recipe_groups)
        ref = builder.observe(record['path'], f"L{record['line']}-L{record['end_line']}:{name}",
                              {'recipe_name': name, 'raw': record['raw'], 'clauses': clauses,
                               'uninterpreted_numeric_clauses': opaque})
        for participant in participants:
            item = participant['item_id']
            if item not in targets or item not in fields or participant['role'] not in {'input', 'destroy'}:
                continue
            builder.activity(item, 'bandaging_material_preparation', 'material',
                             [declaration(item), ref, refs[semantic.GROUPS], refs[semantic.CRAFT]],
                             'bandage_materials', ['activity:crafting'], BANDAGE_MATERIALS)
    for name, output in (('Make Door Knob', 'Doorknob'), ('Make Hinge', 'Hinge')):
        clauses = ['IronIngot=15', 'keep BallPeenHammer', 'keep Tongs', 'NearItem:Anvil',
                   'Result:' + output, 'Time:150.0', 'Category:Smithing', 'SkillRequired:Blacksmith=3',
                   'OnGiveXP:Recipe.OnGiveXP.Blacksmith15', 'NeedToBeLearn:true']
        matches = [r for r in recipes if r['module'] == 'Base' and r['name'] == name and r['clauses'] == clauses]
        if len(matches) != 1:
            continue
        callback_source = reader.mask(texts[semantic.GROUPS], lua=True)
        if not re.search(r'function Recipe\.OnGiveXP\.Blacksmith15\(recipe, ingredients, result, player\)\s*player:getXp\(\):AddXP\(Perks\.Blacksmith, 15\);\s*end', callback_source):
            raise ValueError('Blacksmith15 callback changed')
        record = matches[0]
        participants, opaque = reader.recipe_participants(record, fields, recipe_groups)
        if opaque:
            continue
        ref = builder.observe(record['path'], f"L{record['line']}-L{record['end_line']}:{name}",
                              {'recipe_name': name, 'raw': record['raw'], 'clauses': clauses})
        for participant in participants:
            item, role = participant['item_id'], participant['role']
            if item in targets and item in fields and role in {'input', 'keep'}:
                builder.activity(item, 'smithing_parts', 'tool' if role == 'keep' else 'material',
                                 [declaration(item), ref, refs[semantic.GROUPS], refs[semantic.CRAFT]],
                                 'smithing_parts', ['activity:crafting'], SMITHING_PARTS)
    for name, clauses in (
        ('Make Mildew Cure', ['GardeningSprayEmpty', '[Recipe.GetItemTypes.Milk]', 'Result:GardeningSprayMilk',
                             'Time:40.0', 'Category:Farming', 'NeedToBeLearn:true', 'AllowRottenItem:true', 'OnTest:Recipe.OnTest.WholeMilk']),
        ('Make Flies Cure', ['GardeningSprayEmpty', 'Water=3', 'Cigarettes=5', 'Result:GardeningSprayCigarettes',
                            'Time:40.0', 'Category:Farming', 'NeedToBeLearn:true']),
    ):
        matches = [r for r in recipes if r['module'] == 'farming' and r['name'] == name and r['clauses'] == clauses]
        if len(matches) != 1:
            continue
        record = matches[0]
        participants, opaque = recipe_participants(record, fields, recipe_groups)
        if opaque:
            continue
        ref = builder.observe(record['path'], f"L{record['line']}-L{record['end_line']}:{name}", {'recipe_name': name, 'raw': record['raw'], 'clauses': clauses})
        for participant in participants:
            item = participant['item_id']
            if item in targets and item in fields and participant['role'] == 'input':
                evidence = [declaration(item), ref, refs[semantic.CRAFT], refs[semantic.GROUPS],
                            *import_evidence(builder, participant)]
                builder.activity(item, 'crop_spray_preparation', 'material', evidence, 'crop_spray_preparation',
                                 ['activity:crafting'], SPRAY_PREPARATION)
    for title, token, count, output, sound, time in (
        ('.556 Ammo', '556Bullets', 60, '556Box', 'BoxOfRoundsOpenOne', '15.0'),
        ('.223 Ammo', '223Bullets', 40, '223Box', 'BoxOfRoundsOpenOne', '15.0'),
        ('.308 Ammo', '308Bullets', 40, '308Box', 'BoxOfRoundsOpenOne', '15.0'),
        ('Nails', 'Nails', 100, 'NailsBox', 'PutItemInBag', '5.0'),
        ('Screws', 'Screws', 100, 'ScrewsBox', 'PutItemInBag', '5.0'),
        ('9mm Bullets', 'Bullets9mm', 30, 'Bullets9mmBox', 'BoxOfRoundsOpenOne', '15.0'),
        ('.45 Auto Bullets', 'Bullets45', 30, 'Bullets45Box', 'BoxOfRoundsOpenOne', '15.0'),
        ('.38 Speciam Bullets', 'Bullets38', 30, 'Bullets38Box', 'BoxOfRoundsOpenOne', '15.0'),
        ('.44 Magnum Bullets', 'Bullets44', 12, 'Bullets44Box', 'BoxOfRoundsOpenOne', '15.0'),
        ('Shotgun Shells', 'ShotgunShells', 24, 'ShotgunShellsBox', 'BoxOfShellsOpenOne', '15.0'),
        ('Paperclips', 'Paperclip', 40, 'PaperclipBox', 'PutItemInBag', '5.0'),
    ):
        name = 'Place ' + title + ' in Box'
        clauses = [token + '=' + str(count), 'Result:' + output, 'Sound:' + sound, 'Time:' + time]
        matches = [r for r in recipes if r['module'] == 'Base' and r['name'] == name and r['clauses'] == clauses]
        item, result_item = 'Base.' + token, 'Base.' + output
        if len(matches) != 1 or item not in targets or item not in fields or result_item not in fields:
            continue
        record = matches[0]
        ref = builder.observe(record['path'], f"L{record['line']}-L{record['end_line']}:{name}", {'recipe_name': name, 'raw': record['raw'], 'clauses': clauses})
        evidence = [declaration(item), declaration(result_item), ref, refs[semantic.CRAFT]]
        function(item, 'pack_into_box', BOX_PACKING, 'box_packing', evidence)
        builder.activity(item, 'item_packaging', 'material', evidence, 'box_packing', ['activity:crafting'], BOX_PACKING)
        base.setdefault('box_packing_results', {})[result_item] = {'input_item': item, 'count': count,
            'recipe': name, 'path': record['path'], 'clauses': clauses, 'observation_refs': sorted(set(evidence))}
    for title, dirty, clean in (('Bandage', 'BandageDirty', 'Bandage'), ('Rag', 'RippedSheetsDirty', 'RippedSheets'),
                                ('Denim Strips', 'DenimStripsDirty', 'DenimStrips'), ('Leather Strips', 'LeatherStripsDirty', 'LeatherStrips')):
        name = 'Clean ' + title
        clauses = [dirty, 'Water', 'Result:' + clean, 'Time:40.0', 'Category:Health', 'OnTest:Recipe.OnTest.NotTaintedWater']
        matches = [r for r in recipes if r['module'] == 'Base' and r['name'] == name and r['clauses'] == clauses]
        item = 'Base.' + dirty
        if len(matches) != 1 or item not in targets or item not in fields:
            continue
        record = matches[0]
        ref = builder.observe(record['path'], f"L{record['line']}-L{record['end_line']}:{name}", {'recipe_name': name, 'raw': record['raw'], 'clauses': clauses})
        evidence = [declaration(item), declaration('Base.' + clean), ref, refs[WORLD_MENU], refs[CLEAN_BANDAGE],
                    refs[TAKE_WATER], refs[OBJECT_COMMANDS], refs[semantic.CRAFT], refs[semantic.GROUPS]]
        function(item, 'wash_bandaging_material', BANDAGE_WASHING, 'bandage_washing', evidence)
        builder.activity(item, 'bandaging_material_preparation', 'material', evidence, 'bandage_washing',
                         ['activity:crafting'], BANDAGE_RECIPE_WASHING)
        base.setdefault('bandage_washing_results', {})[item] = {'result_item': 'Base.' + clean, 'recipe': name,
            'path': record['path'], 'clauses': clauses, 'observation_refs': sorted(set(evidence))}
    for title, token in (('Carrots', 'Carrot'), ('Broccoli', 'Broccoli'), ('Radish', 'RedRadish'),
                         ('Strawberry', 'Strewberrie'), ('Tomato', 'Tomato'), ('Potato', 'Potato'), ('Cabbage', 'Cabbage')):
        name = 'Put ' + title + ' Seeds in Packet'
        clauses = [token + 'Seed=50', 'Result:' + token + 'BagSeed', 'Time:10.0', 'Category:Farming']
        matches = [r for r in recipes if r['module'] == 'farming' and r['name'] == name and r['clauses'] == clauses]
        item = 'farming.' + token + 'Seed'
        if len(matches) != 1 or item not in targets or item not in fields:
            continue
        record = matches[0]
        ref = builder.observe(record['path'], f"L{record['line']}-L{record['end_line']}:{name}", {'recipe_name': name, 'raw': record['raw'], 'clauses': clauses})
        builder.activity(item, 'seed_packaging', 'material', [declaration(item), ref, refs[semantic.CRAFT]],
                         'seed_packing', ['activity:crafting'], SEED_PACKING)
    for title, token, count, output in (
        ('Tomatoes', 'farming.Tomato', 5, 'CannedTomato'), ('Carrots', 'Carrots', 5, 'CannedCarrots'),
        ('Potatoes', 'farming.Potato', 5, 'CannedPotato'), ('Eggplants', 'Eggplant', 5, 'CannedEggplant'),
        ('Leeks', 'Leek', 5, 'CannedLeek'), ('Red Radishes', 'farming.RedRadish', 5, 'CannedRedRadish'),
        ('Bell Peppers', 'BellPepper', 5, 'CannedBellPepper'), ('Cabbage', 'farming.Cabbage', 3, 'CannedCabbage'),
        ('Broccoli', 'Broccoli', 5, 'CannedBroccoli')):
        name = 'Make Jar of ' + title
        clauses = ['EmptyJar', 'JarLid', token + '=' + str(count), 'Water=10', 'Vinegar=2',
                   '[Recipe.GetItemTypes.Sugar];1', 'Result:' + output, 'Time:100.0',
                   'OnCreate:Recipe.OnCreate.CannedFood', 'Category:Cooking', 'OnGiveXP:Recipe.OnGiveXP.Cooking10']
        matches = [r for r in recipes if r['module'] == 'Base' and r['name'] == name and r['clauses'] == clauses]
        if len(matches) != 1:
            continue
        record = matches[0]
        participants, opaque = recipe_participants(record, fields, recipe_groups)
        if set(opaque) - {'[Recipe.GetItemTypes.Sugar];1'}:
            continue
        ref = builder.observe(record['path'], f"L{record['line']}-L{record['end_line']}:{name}", {'recipe_name': name, 'raw': record['raw'], 'clauses': clauses, 'uninterpreted_numeric_clauses': opaque})
        for participant in participants:
            item = participant['item_id']
            if item in targets and item in fields and participant['role'] == 'input':
                builder.activity(item, 'vegetable_jarring', 'material',
                                 [declaration(item), ref, refs[semantic.CRAFT], refs[semantic.GROUPS]],
                                 'jar_preparation', ['activity:crafting'], JAR_PREPARATION)
        base.setdefault('jar_preparation_results', {})['Base.' + output] = {'recipe': name,
            'path': record['path'], 'clauses': clauses, 'observation_refs': [ref, refs[semantic.CRAFT], refs[semantic.GROUPS]]}
    for title, tokens, output in (
        ('Soup', 'PotOfSoup/PotOfSoupRecipe', 'SoupBowl'),
        ('Rice', 'WaterPotRice/WaterSaucepanRice/RicePot/RicePan', 'RiceBowl'),
        ('Pasta', 'WaterSaucepanPasta/WaterPotPasta/PastaPan/PastaPot', 'PastaBowl'),
        ('Stew', 'PotOfStew', 'StewBowl'),
    ):
        for count in (2, 4):
            name = 'Make ' + str(count) + ' Bowls of ' + title
            callback = 'Recipe.OnCreate.MakeBowlOf' + ('Stew' if title == 'Stew' else 'Soup') + str(count)
            clauses = [tokens, 'Bowl=' + str(count), 'Result:' + output + '=' + str(count),
                       'OnCreate:' + callback, 'Time:80.0', 'Category:Cooking', 'OnGiveXP:Recipe.OnGiveXP.None',
                       'OnCanPerform:Recipe.OnCanPerform.SliceCooked']
            matches = [r for r in recipes if r['module'] == 'Base' and r['name'] == name and r['clauses'] == clauses]
            if len(matches) != 1:
                continue
            record = matches[0]
            participants, opaque = reader.recipe_participants(record, fields, recipe_groups)
            if opaque:
                continue
            ref = builder.observe(record['path'], f"L{record['line']}-L{record['end_line']}:{name}", {'recipe_name': name, 'raw': record['raw'], 'clauses': clauses})
            result_item = 'Base.' + output
            for participant in participants:
                item = participant['item_id']
                if item not in targets or item not in fields or participant['role'] != 'input':
                    continue
                evidence = [declaration(item), declaration(result_item), ref, refs[semantic.CRAFT], refs[semantic.GROUPS]]
                function(item, 'receive_portioned_food' if item == 'Base.Bowl' else 'portion_into_bowls',
                         BOWL_PORTIONING, 'bowl_portioning', evidence)
                builder.activity(item, 'food_portioning', 'material', evidence, 'bowl_portioning', ['activity:crafting'], BOWL_PORTIONING)
            base.setdefault('bowl_portion_results', {}).setdefault(result_item, []).append({
                'recipe': name, 'path': record['path'], 'clauses': clauses, 'count': count, 'callback': callback,
                'observation_refs': [ref, refs[semantic.CRAFT], refs[semantic.GROUPS]]})
    assemblies = []
    assemblies.append(('Build Drawer', 'furniture_crafting', ['Plank', 'Nails', 'Doorknob', 'Result:Drawer', 'Time:150.0', 'Category:Carpentry']))
    for name, stone, result in (('Make Stone Axe', 'SharpedStone', 'AxeStone'), ('Make Stone Hammer', 'Stone', 'HammerStone'), ('Make Stone Knife', 'SharpedStone', 'FlintKnife')):
        assemblies.append((name, 'tool_crafting', ['TreeBranch', stone, 'RippedSheets/Twine/RippedSheetsDirty/DenimStrips/DenimStripsDirty',
                                                  'Result:' + result, 'Time:80.0', 'Category:Survivalist']))
    assemblies.append(('Make Splint', 'splint_crafting', ['RippedSheets/RippedSheetsDirty/DenimStrips/DenimStripsDirty',
                                                        'Plank/TreeBranch/WoodenStick', 'Result:Splint', 'Time:70.0', 'Category:Health']))
    assemblies.append(('Make Fishing Net', 'fishing_gear_crafting', ['Twine=10', 'Wire=5', 'Result:FishingNet', 'Time:150.0', 'Category:Fishing', 'NeedToBeLearn:true']))
    for line, result in (('Twine', 'CraftedFishingRodTwineLine'), ('FishingLine', 'CraftedFishingRod')):
        assemblies.append(('Make Fishing Rod', 'fishing_gear_crafting', ['keep [Recipe.GetItemTypes.SharpKnife]/MeatCleaver',
                           'WoodenStick', line + '=2', 'Paperclip/Nails', 'Result:' + result, 'Time:80.0', 'Category:Fishing', 'NeedToBeLearn:true']))
    for line, result in (('Twine', 'FishingRodTwineLine'), ('FishingLine', 'FishingRod')):
        assemblies.append(('Fix Fishing Rod', 'fishing_gear_crafting', ['FishingRodBreak', line + '=2',
                           'Paperclip/Nails', 'Result:' + result, 'Time:80.0', 'Category:Fishing', 'NeedToBeLearn:true']))
    for name, activity, clauses in assemblies:
        matches = [r for r in recipes if r['module'] == 'Base' and r['name'] == name and r['clauses'] == clauses]
        if len(matches) != 1:
            continue
        record = matches[0]
        participants, opaque = reader.recipe_participants(record, fields, recipe_groups)
        if opaque:
            continue
        ref = builder.observe(record['path'], f"L{record['line']}-L{record['end_line']}:{name}",
                              {'raw': record['raw'], 'clauses': record['clauses']})
        for participant in participants:
            item, role = participant['item_id'], participant['role']
            if item not in targets or item not in fields or role not in {'input', 'keep'}:
                continue
            builder.activity(item, activity, 'tool' if role == 'keep' else 'material',
                             [declaration(item), ref, refs[semantic.GROUPS], refs[semantic.CRAFT]],
                             'material_assembly', ['activity:crafting'], MATERIAL_ASSEMBLY)
            if item == 'Base.FishingRodBreak' and name == 'Fix Fishing Rod':
                repair_roles = [f['fact_id'] for f in builder.facts.values() if f['item_id'] == item
                                and f['payload'] == {'role': 'material'}]
                builder.fact(item, 'condition', {'predicate': ROD_REPAIR_INPUT},
                             [declaration(item), ref, refs[semantic.CRAFT], refs[FISHING_UI], refs[FISHING_ACTION]],
                             'material_assembly', ['activity:crafting'], applies_to_fact_refs=repair_roles)
    radio_recipes = {
        'Craft Makeshift Radio': ('Radio.RadioMakeShift', ['ElectronicsScrap=2', 'Amplifier', 'LightBulb', 'Radio.RadioReceiver', 'Radio.ElectricWire', 'Aluminum=2']),
        'Craft Makeshift HAM Radio': ('Radio.HamRadioMakeShift', ['ElectronicsScrap=4', 'Amplifier', 'LightBulb', 'LightBulbGreen', 'Radio.RadioReceiver', 'Radio.RadioTransmitter', 'Radio.ElectricWire=3', 'Aluminum=4']),
        'Craft Makeshift Walkie Talkie': ('Radio.WalkieTalkieMakeShift', ['ElectronicsScrap=3', 'Amplifier', 'LightBulb', 'LightBulbGreen', 'Radio.RadioReceiver', 'Radio.RadioTransmitter', 'Radio.ElectricWire=2', 'Aluminum=3']),
    }
    for record in recipes:
        reviewed = radio_recipes.get(record['name'])
        if not reviewed or record['module'] != 'Base' or recipe_counts[record['module'], record['name']] != 1:
            continue
        output, components = reviewed
        expected = components + ['keep [Recipe.GetItemTypes.Screwdriver]', 'NoBrokenItems:true', 'Result:' + output,
                                  'SkillRequired:Electricity=1', 'NeedToBeLearn:true', 'Time:100.0',
                                  'OnCreate:Recipe.OnCreate.RadioCraft', 'OnGiveXP:Recipe.OnGiveXP.RadioCraft', 'Category:Electrical']
        if record['clauses'] != expected or output not in fields:
            continue
        participants, opaque = reader.recipe_participants(record, fields, recipe_groups)
        if opaque:
            continue
        ref = builder.observe(record['path'], f"L{record['line']}-L{record['end_line']}:{record['name']}",
                              {'raw': record['raw'], 'clauses': record['clauses']})
        for participant in participants:
            item, role = participant['item_id'], participant['role']
            if item not in targets or item not in fields or role not in {'input', 'keep'}:
                continue
            evidence = [declaration(item), declaration(output), ref, refs[semantic.GROUPS], refs[semantic.CRAFT]]
            builder.activity(item, 'radio_crafting', 'tool' if role == 'keep' else 'material', evidence,
                             'radio_crafting', ['activity:crafting'], RADIO_CRAFTING)
    radio_dismantling = {'Recipe.OnCreate.DismantleRadio', 'Recipe.OnCreate.DismantleRadioTwoWay',
                         'Recipe.OnCreate.DismantleRadioHAM', 'Recipe.OnCreate.DismantleRadioTV'}
    for record in recipes:
        props = reader.properties(record, ':')
        radio_callback = len(props.get('OnCreate', [])) == 1 and props['OnCreate'][0] in radio_dismantling
        if (recipe_counts[record['module'], record['name']] != 1
                or props.get('Category') != ['Electrical']
                or props.get('OnTest') != ['Recipe.OnTest.DismantleElectronics']
                or props.get('OnGiveXP') != ['Recipe.OnGiveXP.DismantleRadio' if radio_callback else 'Recipe.OnGiveXP.DismantleElectronics']
                or any(k.startswith('On') and k not in {'OnTest', 'OnCreate', 'OnGiveXP'} for k in props)):
            continue
        callbacks = props.get('OnCreate', [])
        if not radio_callback and callbacks not in ([], ['Recipe.OnCreate.Dismantle'], ['Recipe.OnCreate.Dismantle2'],
                                                     ['Recipe.OnCreate.DismantleTVRemote'], ['Recipe.OnCreate.DismantleFlashlight']):
            continue
        if radio_callback and (props.get('NoBrokenItems') != ['true'] or props.get('Result') != ['ElectronicsScrap']):
            continue
        participants, opaque = reader.recipe_participants(record, fields, recipe_groups)
        if opaque or not participants or props.get('Result', [''])[0].split('=')[0] not in {'ElectronicsScrap', 'Receiver', 'Amplifier', 'MotionSensor'}:
            continue
        kept = {p['group'] for p in participants if p['role'] == 'keep'}
        if kept != {'Recipe.GetItemTypes.Screwdriver'}:
            continue
        output = reader.qualify(record['module'], props['Result'][0].split('=')[0])
        if output not in fields:
            continue
        ref = builder.observe(record['path'], f"L{record['line']}-L{record['end_line']}:{record['name']}",
                              {'raw': record['raw'], 'clauses': record['clauses']})
        for participant in participants:
            item, role = participant['item_id'], participant['role']
            if item not in targets or item not in fields or role == 'result':
                continue
            evidence = [declaration(item), declaration(output), ref, refs[semantic.GROUPS], refs[semantic.CRAFT]]
            predicate = RADIO_DISMANTLING if radio_callback else ELECTRONIC_SALVAGE
            if role in {'input', 'destroy'}:
                fid = function(item, 'dismantle_electronics', predicate, 'electronic_salvage', evidence)
                if output == 'Base.ElectronicsScrap' or callbacks in (['Recipe.OnCreate.Dismantle'], ['Recipe.OnCreate.Dismantle2'], ['Recipe.OnCreate.DismantleTVRemote']):
                    builder.fact(item, 'condition', {'predicate': SCRAP_RECOVERY}, evidence,
                                 'electronic_salvage', ['item:direct'], applies_to_fact_refs=[fid])
            builder.activity(item, 'radio_salvage' if radio_callback else 'electronic_salvage', 'tool' if role == 'keep' else 'transformation_target', evidence,
                             'electronic_salvage', ['activity:crafting'], predicate)
    for device in ('Torch', 'HandTorch', 'Rubberducky2'):
        clauses = ['destroy ' + device, 'destroy Battery', 'Result:' + device, 'Time:30',
                   'OnTest:Recipe.OnTest.TorchBatteryInsert', 'OnCreate:Recipe.OnCreate.TorchBatteryInsert', 'StopOnWalk:false']
        matches = [r for r in recipes if r['module'] == 'Base' and r['clauses'] == clauses]
        item = 'Base.' + device
        if len(matches) != 1 or item not in targets or item not in fields or 'Base.Battery' not in fields:
            continue
        record = matches[0]
        ref = builder.observe(record['path'], f"L{record['line']}-L{record['end_line']}:{record['name']}",
                              {'raw': record['raw'], 'clauses': record['clauses']})
        evidence = [declaration(item), declaration('Base.Battery'), ref, refs[semantic.GROUPS], refs[semantic.CRAFT]]
        function(item, 'accept_battery_charge', BATTERY_INSERTION, 'battery_receiver', evidence)
        function('Base.Battery', 'supply_portable_device_charge', BATTERY_INSERTION, 'battery_receiver', evidence)
        builder.activity(item, 'battery_insertion', 'power_receiver', evidence,
                         'battery_receiver', ['activity:crafting'], BATTERY_INSERTION)
    for color in ('Blue', 'Red', 'Black', 'White'):
        for opening in (True, False):
            source = ('ClosedUmbrella' if opening else 'Umbrella') + color
            result = ('Umbrella' if opening else 'ClosedUmbrella') + color
            callback = 'OpenUmbrella' if opening else 'CloseUmbrella'
            clauses = [source, 'Result:' + result, 'OnCreate:Recipe.OnCreate.' + callback, 'Time:10.0']
            matches = [r for r in recipes if r['module'] == 'Base' and r['clauses'] == clauses]
            item, output = 'Base.' + source, 'Base.' + result
            if len(matches) != 1 or item not in targets or item not in fields or output not in fields:
                continue
            record = matches[0]
            ref = builder.observe(record['path'], f"L{record['line']}-L{record['end_line']}:{record['name']}",
                                  {'raw': record['raw'], 'clauses': record['clauses']})
            function(item, 'unfold_umbrella' if opening else 'fold_umbrella', UMBRELLA_CHANGE,
                     'umbrella_form', [declaration(item), declaration(output), ref, refs[semantic.GROUPS], refs[semantic.CRAFT]])
            builder.activity(item, 'umbrella_form_change', 'transformation_target',
                             [declaration(item), declaration(output), ref, refs[semantic.GROUPS], refs[semantic.CRAFT]],
                             'umbrella_form', ['activity:crafting'], UMBRELLA_CHANGE)
    rope_records = [r for r in recipes if r['module'] == 'Base' and r['name'] == 'Craft Sheet Rope']
    if len(rope_records) == 1:
        record = rope_records[0]
        if (record['clauses'] == ['[Recipe.GetItemTypes.CraftSheetRope]', 'Result:SheetRope', 'Time:10.0']):
            ref = builder.observe(record['path'], f"L{record['line']}-L{record['end_line']}:Craft Sheet Rope",
                                  {'raw': record['raw'], 'clauses': record['clauses']})
            clean = reader.mask(texts[semantic.CLOTHING], lua=True)
            fabrics = set(re.findall(r'ClothingRecipesDefinitions\["FabricType"\]\["([^"]+)"\]\s*=\s*\{', clean))
            blocked = set(re.findall(r'ClothingRecipesDefinitions\["FabricType"\]\["([^"]+)"\]\.noSheetRope\s*=\s*true', clean))
            named = set(re.findall(r'ClothingRecipesDefinitions\["([^"]+)"\]\s*=\s*\{', clean)) - {'FabricType'}
            for item in sorted(targets & fields.keys()):
                f = fields[item]
                if ((f.get('Type') == 'Clothing' and f.get('FabricType') in fabrics - blocked)
                        or item.split('.', 1)[1] in named):
                    builder.activity(item, 'sheet_rope_making', 'material',
                                     [declaration(item), ref, refs[semantic.GROUPS], refs[semantic.CLOTHING], refs[semantic.CRAFT]],
                                     'sheet_rope', ['activity:crafting'], ROPE_MAKING)
    for record in recipes:
        name = record['name']
        if recipe_counts[record['module'], name] != 1:
            continue
        kind = ('unpack_produce' if name.startswith('Open Sack of ') else
                'unpack_seeds' if name.startswith('Open Packet of ') and name.endswith(' Seeds') else
                'unpack_ammunition' if name.startswith('Open Box of ') and re.search(r'Ammo|Bullets|Shells', name) else
                'unpack_box_contents' if name.startswith('Open Box of ') else
                'unpack_eggs' if name == 'Open Egg Carton' else
                'unpack_canned_food' if name.startswith('Open Canned ') or name in {'Open Dog Food', 'Open Condensed Milk'} else
                'unpack_jarred_food' if name.startswith('Open Jar of ') else None)
        if kind is None:
            continue
        clauses = record['clauses']
        participants = [c.strip() for c in clauses if ':' not in c]
        tools = [c for c in participants if c.startswith('keep ')]
        consumed = [c for c in participants if not c.startswith('keep ')]
        result = [c.split(':', 1)[1].strip() for c in clauses if c.strip().startswith('Result:')]
        callbacks = [c.split(':', 1)[1].strip() for c in clauses if c.strip().startswith(('OnCreate:', 'OnTest:', 'OnCanPerform:'))]
        if len(consumed) != 1 or len(result) != 1 or callbacks not in ([], ['Recipe.OnCreate.OpenSackProduce'], ['Recipe.OnCreate.OpenEggCarton'], ['Recipe.OnCreate.OpenCannedFood'], ['Recipe.OnCreate.OpenBoxOfJars']):
            continue
        if callbacks == ['Recipe.OnCreate.OpenBoxOfJars'] and (record['module'] != 'Base' or name != 'Open Box of Jars'
                or clauses != ['BoxOfJars', 'Result:EmptyJar=6', 'OnCreate:Recipe.OnCreate.OpenBoxOfJars', 'Sound:PutItemInBag', 'Time:15.0']):
            continue
        if tools and not (kind == 'unpack_canned_food' and tools == ['keep [Recipe.GetItemTypes.CanOpener]']):
            continue
        if not re.fullmatch(r'[A-Za-z0-9_.]+', consumed[0]):
            continue
        qualify = lambda token: token if '.' in token else record['module'] + '.' + token
        item = qualify(consumed[0])
        output = qualify(result[0].split('=')[0])
        if item not in targets or item not in fields or output not in fields or not fields[item] or not fields[output]:
            continue
        if kind in {'unpack_produce', 'unpack_eggs', 'unpack_canned_food', 'unpack_jarred_food'} and fields[output].get('Type') != 'Food':
            continue
        if kind == 'unpack_ammunition' and fields[output].get('DisplayCategory') != 'Ammo':
            continue
        ref = builder.observe(record['path'], f"L{record['line']}-L{record['end_line']}:{name}", {'raw': record['raw'], 'clauses': clauses})
        evidence = [declaration(item), declaration(output), ref, refs[semantic.CRAFT], refs[semantic.GROUPS]]
        predicate = ({'Recipe.OnCreate.OpenBoxOfJars': JAR_BOX_OPENING,
                      'Recipe.OnCreate.OpenEggCarton': EGG_CARTON_OPENING,
                      'Recipe.OnCreate.OpenSackProduce': PRODUCE_SACK_OPENING}.get(callbacks[0], OPENING)
                     if callbacks else OPENING)
        predicate = CAN_OPENING if tools else predicate
        function(item, kind, predicate, 'package_opening', evidence)
        base.setdefault('package_opening_results', {}).setdefault(item, []).append({'result_item': output,
            'result_clause': result[0], 'clauses': clauses, 'path': record['path'], 'observation_refs': sorted(set(evidence)),
            'opening_condition': predicate,
            'ammunition_receivers': sorted(target for target, values in fields.items() if values.get('AmmoType') == item),
            'receiver_source_paths': sorted({r['path'] for records in declarations.values() for r in records})})
        builder.activity(item, 'package_opening', 'material', evidence,
                         'package_opening', ['activity:crafting'], predicate)
        if kind == 'unpack_produce' and callbacks == ['Recipe.OnCreate.OpenSackProduce']:
            result_leads = [r for r in recipes if any(
                reader.qualify(r['module'], v.split('=')[0]) == item for v in reader.properties(r, ':').get('Result', []))]
            base.setdefault('produce_sack_sources', {})[item] = {'opening_recipe': name, 'opening_clauses': clauses,
                'opening_path': record['path'], 'opened_item': output, 'observation_refs': sorted(set(evidence)),
                'declared_result_leads': [{'path': r['path'], 'line': r['line'], 'clauses': r['clauses']} for r in result_leads],
                'recipe_source_bindings': [inputs.bindings[p] for p in sorted({r['path'] for r in recipes})]}
        entries = fields[output].get('EvolvedRecipe')
        if fields[output].get('Type') == 'Food' and entries and not {'Type', 'EvolvedRecipe'} & property_readings[output][1].keys():
            names = [entry.split(':', 1)[0].strip() for entry in entries.split(';')]
            cooking_records = [r for r in evolved if r['name'] in names and evolved_counts[r['module'], r['name']] == 1]
            if len(cooking_records) == len(set(names)):
                cooking_evidence = [*evidence, refs[semantic.MENU], refs[semantic.COOK]]
                for r in cooking_records:
                    cooking_evidence.append(builder.observe(r['path'], f"L{r['line']}-L{r['end_line']}:{r['name']}",
                                                           {'raw': r['raw'], 'clauses': r['clauses']}))
                fid = function(item, 'prepare_opened_food_ingredient', COOKING_ACTION, 'opened_food_preparation', cooking_evidence)
                for predicate in (OPENED_FOOD, CAN_OPENING if tools else OPENING):
                    builder.fact(item, 'condition', {'predicate': predicate}, cooking_evidence,
                                 'opened_food_preparation', ['item:direct'], applies_to_fact_refs=[fid])
        if kind == 'unpack_seeds' and output in seed_forms:
            fid = function(item, 'sow_extracted_seeds', SOWING, 'sowing', [*evidence, *seed_evidence])
            for predicate in (SEED_EXTRACTION, OPENING, SOW_COUNTS[seed_counts[output]]):
                builder.fact(item, 'condition', {'predicate': predicate}, [*evidence, *seed_evidence],
                             'sowing', ['item:direct'], applies_to_fact_refs=[fid])
        if tools:
            for tool in sorted(targets & fields.keys()):
                if 'CanOpener' in fields[tool].get('Tags', '').split(';'):
                    function(tool, kind, CAN_OPENING, 'package_opening', [declaration(tool), *evidence])
                    builder.activity(tool, 'package_opening', 'tool', [declaration(tool), *evidence],
                                     'package_opening', ['activity:crafting'], CAN_OPENING)


# These are explicitly authored vanilla purposes, linked by the declaration's
# Tooltip property. They do not infer effects from a drug name or numeric sign.


def supplement_player_uses(root, semantic):
    """Bounded successor correction over admitted declarations, not r6 reissue.

    The positive declaration supports the equipped protection capability, not
    a promise of complete dryness. The supplied Lua foraging accessor consumer
    additionally establishes a concrete use without inventing native wetness
    amounts or demanding a new runtime proof of the declared capability.
    """
    import hashlib
    from . import semantic_results as owner
    from . import source_reader as reader

    by_item = {}
    for ref, observation in semantic['observations'].items():
        content = observation.get('content', {})
        if not isinstance(content, dict) or not content.get('raw', '').lstrip().startswith('item '):
            continue
        item = observation['locator'].rsplit(':', 1)[-1]
        if item not in semantic['target_ids']:
            continue
        by_item.setdefault(item, []).append((ref, observation))
    selected, medicines, generators, leisure_reading = [], [], [], []
    reading_subjects = {f['item_id'] for f in semantic.get('facts', []) if f['fact_kind'] == 'direct_function'
                        and f['payload'].get('function') == 'read_literature'}
    consumption = {f['item_id'] for f in semantic.get('facts', []) if f['fact_kind'] == 'direct_function'
                   and f['payload'].get('function') in {'take_pills', 'take_food_medicine'}}
    generator_subjects = {f['item_id'] for f in semantic.get('facts', []) if f['fact_kind'] == 'direct_function'
                          and f['payload'].get('function') == 'control_installed_generator'}
    for item, declarations in sorted(by_item.items()):
        # Multiple observations of identical declaration bytes are harmless;
        # conflicting declarations or property values are not resolved here.
        if any(o['content'].get('property_conflicts') for _, o in declarations):
            continue
        # Existing owners use both :item:FullType and :FullType locators and
        # preserve different newline conventions for the same source span.
        unique = {(o['source_path'], o['source_sha256'], o['locator'].split(':', 1)[0],
                   o['content']['raw'].replace('\r\n', '\n')): (ref, o)
                  for ref, o in declarations}
        if len(unique) != 1:
            continue
        ref, observation = next(iter(unique.values()))
        content = observation['content']
        props = reader.properties({'clauses': content.get('clauses', [])}, '=')
        if item in reading_subjects and props.get('Type') == ['Literature'] and not props.get('SkillTrained') and not props.get('TeachedRecipes'):
            mood_values = [values[0] for key, values in props.items()
                           if key in {'BoredomChange', 'StressChange', 'UnhappyChange'} and len(values) == 1]
            if any(re.fullmatch(r'-\d+(?:\.\d+)?', value) and float(value) < 0 for value in mood_values):
                leisure_reading.append((item, ref, observation))
        if item in generator_subjects:
            generators.append((item, ref, observation))
        tooltip = props.get('Tooltip', [])
        if (len(tooltip) == 1 and tooltip[0] in MEDICINE_PURPOSES and props.get('Medical') == ['TRUE']
                and props.get('Type') in (['Drainable'], ['Food']) and item in consumption):
            medicines.append((item, ref, observation, tooltip[0]))
        if content.get('property_conflicts') or props.get('ProtectFromRainWhenEquipped') != ['TRUE']:
            continue
        selected.append((item, ref, observation))

    paths = ('lua/shared/Foraging/forageSystem.lua', 'lua/client/Foraging/ISSearchManager.lua')
    raw = {path: (root / path).read_bytes() for path in paths}
    texts = {path: data.decode('utf-8-sig') for path, data in raw.items()}
    body = texts[paths[0]].split('function forageSystem.getWeatherPenalty(_character, _square)', 1)
    if len(body) != 2:
        raise ValueError('rain-use source function unavailable')
    body = body[1].split('\nfunction ', 1)[0]
    required = ('if not _square:isOutside() then return 1; end;',
        '_character:getPrimaryHandItem()', '_character:getSecondaryHandItem()',
        'primaryItem:isProtectFromRainWhileEquipped()', 'secondaryItem:isProtectFromRainWhileEquipped()',
        'if umbrellaPrimary or umbrellaSecondary then', 'rainLevel = rainLevel * 0.1;',
        'weatherPenalty = rainLevel + fogLevel;', 'return 1 - (weatherPenalty * effectReduction);')
    if not all(text in body for text in required) or 'forageSystem.getWeatherPenalty(character, self.square)' not in texts[paths[1]]:
        raise ValueError('rain-use consumer no longer matches the reviewed rule')
    source_hashes = {path: hashlib.sha256(data).hexdigest() for path, data in raw.items()}
    source_hashes.update({o['source_path']: o['source_sha256'] for _, _, o in selected})
    builder = owner.Builder(source_hashes)
    rule = 'equipped_rain_use'
    caller = texts[paths[1]].split('function ISSearchManager:updateModifiers()', 1)[1].split('\nfunction ', 1)[0]
    refs = [builder.observe(paths[0], paths[0] + ':getWeatherPenalty', {'source_text': body}),
            builder.observe(paths[1], paths[1] + ':updateModifiers', {'source_text': caller})]
    for item, ref, observation in selected:
        builder.observations[ref] = observation
        evidence = [ref, *refs]
        protection = builder.fact(item, 'direct_function', {'function': 'provide_equipped_rain_protection'},
                                  evidence, rule, ['activity:equipment'])
        foraging = builder.fact(item, 'direct_function', {'function': 'reduce_foraging_rain_effect'},
                                evidence, rule, ['activity:foraging'])
        builder.fact(item, 'condition', {'predicate': EQUIPPED_RAIN_USE}, evidence, rule,
                     ['activity:equipment', 'activity:foraging'], applies_to_fact_refs=[protection, foraging])
    medicine_rule = 'declared_medicine_purpose'
    if medicines:
        tooltip_path = 'lua/shared/Translate/EN/Tooltip_EN.txt'
        tooltip_raw = (root / tooltip_path).read_bytes()
        tooltip_text = tooltip_raw.decode('utf-8-sig')
        source_hashes[tooltip_path] = hashlib.sha256(tooltip_raw).hexdigest()
        # Builder retains the shared source binding dictionary.
        for item, ref, observation, key in medicines:
            expected, function, _, _ = MEDICINE_PURPOSES[key]
            readings = re.findall(r'^\s*' + re.escape(key) + r'\s*=\s*"([^"\r\n]*)"\s*,?\s*$', tooltip_text, re.M)
            if readings != [expected]:
                raise ValueError('medicine purpose text no longer matches the reviewed rule: ' + key)
            source_hashes[observation['source_path']] = observation['source_sha256']
            builder.observations[ref] = observation
            label = builder.observe(tooltip_path, key, {'tooltip_key': key, 'purpose_text': expected})
            dispatch = [f for f in semantic['facts'] if f['item_id'] == item and f['fact_kind'] == 'direct_function'
                        and f['payload'].get('function') in {'take_pills', 'take_food_medicine'}]
            dispatch_refs = sorted({r for f in dispatch for p in f['provenance_refs']
                                    for r in semantic['provenance'][p]['observation_refs']})
            for dispatch_ref in dispatch_refs:
                observed = semantic['observations'][dispatch_ref]
                source_hashes[observed['source_path']] = observed['source_sha256']
                builder.observations[dispatch_ref] = observed
            builder.fact(item, 'direct_function', {'function': function}, [ref, label, *dispatch_refs],
                         medicine_rule, ['item:direct'])
    generator_rule = 'declared_exterior_generator_use'
    if generators:
        setting_path = 'lua/shared/Translate/EN/Sandbox_EN.txt'
        menu_path = 'lua/client/ISUI/ISWorldObjectContextMenu.lua'
        setting_raw, menu_raw = (root / setting_path).read_bytes(), (root / menu_path).read_bytes()
        setting_text, menu_text = setting_raw.decode('utf-8-sig'), menu_raw.decode('utf-8-sig')
        setting_key = 'Sandbox_AllowExteriorGenerator_tooltip'
        purpose = 'If enabled, generators will work on exterior tiles, allowing for example to power gas pump.'
        guard = 'if haveFuel and ((SandboxVars.AllowExteriorGenerator and haveFuel:getSquare():haveElectricity()) or (SandboxVars.ElecShutModifier > -1 and GameTime:getInstance():getNightsSurvived() < SandboxVars.ElecShutModifier)) then'
        if (re.findall(r'^\s*' + setting_key + r'\s*=\s*"([^"\r\n]*)"\s*,?\s*$', setting_text, re.M) != [purpose]
                or guard not in menu_text or 'ISWorldObjectContextMenu.doFillFuelMenu(haveFuel, player, context);' not in menu_text):
            raise ValueError('exterior generator purpose or fuel-pump consumer changed')
        source_hashes[setting_path] = hashlib.sha256(setting_raw).hexdigest()
        source_hashes[menu_path] = hashlib.sha256(menu_raw).hexdigest()
        setting_ref = builder.observe(setting_path, setting_key, {'purpose_text': purpose})
        menu_ref = builder.observe(menu_path, 'take fuel: exterior generator guard',
                                   {'source_text': guard, 'consumer': 'ISWorldObjectContextMenu.doFillFuelMenu(haveFuel, player, context);'})
        for item, ref, observation in generators:
            source_hashes[observation['source_path']] = observation['source_sha256']
            builder.observations[ref] = observation
            admitted = [f for f in semantic['facts'] if f['item_id'] == item and f['fact_kind'] == 'direct_function'
                        and f['payload'].get('function') == 'control_installed_generator']
            controls = sorted({r for f in admitted for p in f['provenance_refs'] for r in semantic['provenance'][p]['observation_refs']})
            for control in controls:
                observed = semantic['observations'][control]
                source_hashes[observed['source_path']] = observed['source_sha256']
                builder.observations[control] = observed
            evidence = [ref, setting_ref, menu_ref, *controls]
            fid = builder.fact(item, 'direct_function', {'function': 'power_exterior_fuel_pumps'}, evidence,
                               generator_rule, ['item:direct'])
            builder.fact(item, 'condition', {'predicate': GENERATOR_EXTERIOR_USE}, evidence,
                         generator_rule, ['item:direct'], applies_to_fact_refs=[fid])
    leisure_rule = 'declared_morale_reading_purpose'
    reading_path = 'lua/client/TimedActions/ISReadABook.lua'
    reading_raw = (root / reading_path).read_bytes()
    reading_text = reading_raw.decode('utf-8-sig')
    if not all(token in reading_text for token in ('effectiveness of morale-boosting', 'self.item:getBoredomChange() < 0.0', 'self.character:ReadLiterature(self.item)')):
        raise ValueError('authored morale-reading relationship changed')
    source_hashes[reading_path] = hashlib.sha256(reading_raw).hexdigest()
    reading_ref = builder.observe(reading_path, 'authored morale-boosting literature purpose', {'source_text': reading_text})
    for item, ref, observation in leisure_reading:
        source_hashes[observation['source_path']] = observation['source_sha256']
        builder.observations[ref] = observation
        builder.fact(item, 'direct_function', {'function': 'read_for_morale'}, [ref, reading_ref], leisure_rule, ['item:direct'])
    learning_rule = supplement_learning_media(root, semantic, by_item, builder, source_hashes)
    learning_rule[leisure_rule] = {'revision': '1', 'review_state': 'reviewed',
        'preconditions': 'Admitted read action and unique non-teaching Literature declaration with negative mood fields; authored ISReadABook description explicitly identifies morale-boosting literature.',
        'transformation': 'Expose the authored mood-lifting reading purpose, separately from learning.',
        'exceptions': 'No conversion of the during-reading cap into a decrease; no actual reduction amount, timing or guaranteed native result.'}
    battery_rule = 'installed_battery_power_purpose'
    battery_path = 'lua/server/Vehicles/Vehicles.lua'
    battery_bytes = (root / battery_path).read_bytes()
    battery_text = reader.mask(battery_bytes.decode('utf-8-sig'), lua=True)
    if not all(token in battery_text for token in ('function Vehicles.Update.Battery(', 'charge = charge - 0.025',
                                                  'vehicle:getBatteryCharge() <= 0.0', 'VehicleUtils.chargeBattery(vehicle, -0.000025')):
        raise ValueError('reviewed vehicle battery power consumer changed')
    source_hashes[battery_path] = hashlib.sha256(battery_bytes).hexdigest()
    battery_ref = builder.observe(battery_path, 'Vehicles.Update.Battery/Lightbar', {'source_text': battery_bytes.decode('utf-8-sig')})
    light_rule = 'installed_vehicle_light_purpose'
    headlight = battery_text.split('function Vehicles.Update.Headlight(', 1)[1].split('\nfunction ', 1)[0]
    if not all(token in headlight for token in ('vehicle:getHeadlightsOn()', 'not part:getInventoryItem()',
                                               'vehicle:getBatteryCharge() <= 0.0', 'part:setLightActive(active)')):
        raise ValueError('reviewed installed headlight consumer changed')
    for fact in semantic.get('facts', []):
        if fact['fact_kind'] != 'direct_function' or fact['payload'].get('function') not in {'install_vehicle_battery', 'install_vehicle_bulb'}:
            continue
        if any(o['content'].get('property_conflicts') for _, o in by_item.get(fact['item_id'], [])):
            continue
        refs = sorted({ref for pid in fact['provenance_refs'] for ref in semantic['provenance'][pid]['observation_refs']})
        for ref in refs:
            observation = semantic['observations'][ref]
            source_hashes[observation['source_path']] = observation['source_sha256']
            builder.observations[ref] = observation
        is_light = fact['payload']['function'] == 'install_vehicle_bulb'
        builder.fact(fact['item_id'], 'direct_function', {'function': 'provide_vehicle_headlight' if is_light else 'supply_vehicle_electrical_power'},
                     [battery_ref, *refs], light_rule if is_light else battery_rule, ['item:direct'])

    learning_rule.update(supplement_attachment_purposes(root, semantic, by_item, builder, source_hashes))
    learning_rule.update(supplement_placed_purposes(root, semantic, by_item, builder, source_hashes))
    learning_rule.update(supplement_native_device_purposes(root, semantic, by_item, builder, source_hashes))
    learning_rule.update(supplement_vehicle_tool_purposes(root, semantic, by_item, builder, source_hashes))
    from .purpose_evidence import supplement_latest
    learning_rule.update(supplement_latest(root, semantic, by_item, builder, source_hashes))
    from .purpose_participant_relations import supplement as supplement_participant_purposes
    learning_rule.update(supplement_participant_purposes(root, semantic, by_item, builder, source_hashes))

    path = 'Iris/tooling/src/iris_tooling/domains/layer3/recovery_sources.py'
    return {'owner': path, 'producer_sha256': hashlib.sha256((root / path).read_bytes()).hexdigest(),
        'basis': 'successor correction; predecessor semantic payload and adoption remain unchanged',
        'rules': {**learning_rule, light_rule: {'revision': '1', 'review_state': 'reviewed', 'preconditions': 'Admitted vehicle bulb installation and Vehicles.Update.Headlight requiring an installed item and battery power before activating the light.', 'transformation': 'Supply light in compatible vehicle headlights.', 'exceptions': 'No brightness, range, color or universal compatibility claim.'}, battery_rule: {'revision': '1', 'review_state': 'reviewed', 'preconditions': 'Admitted vehicle battery installation and active battery consumers in Vehicles.Update.', 'transformation': 'Supply electrical power for starting and vehicle electrical equipment.', 'exceptions': 'No promise of successful starting, universal compatibility or specific electrical equipment.'}, rule: {'revision': '1', 'review_state': 'reviewed',
            'preconditions': 'Unique admitted declaration with ProtectFromRainWhenEquipped=TRUE; active held-item accessor consumer in outdoor foraging.',
            'transformation': 'Equipped rain-protection capability and reduced precipitation contribution in outdoor foraging.',
            'exceptions': 'No complete dryness, native wetness amount, sprint behavior, reduced fog/snow/cloud effect, or guarantee of improved total foraging results.'},
            medicine_rule: {'revision': '1', 'review_state': 'reviewed',
                'preconditions': 'Unique admitted Medical declaration links an exact reviewed vanilla EN Tooltip purpose; admitted consumption dispatch exists.',
                'transformation': 'Expose the explicitly authored medicinal purpose, including sustained unhappiness relief, sleep context and the antibiotic zombification exclusion.',
                'exceptions': 'Not inferred from item names, FatigueChange sign or ReduceInfectionPower magnitude. No new dose, exact onset/duration, engine calculation or guaranteed cure claim.'},
            generator_rule: {'revision': '1', 'review_state': 'reviewed',
                'preconditions': 'Unique admitted generator declaration/control joins the explicit exterior-generator sandbox description and active fuel-pump power guard.',
                'transformation': 'Conditional exterior fuel-pump power purpose, with the exterior-generator setting retained.',
                'exceptions': 'No general indoor/all-device power claim, range, exact efficiency, native power calculation or guarantee of a particular pump being supplied.'}},
        'source_bindings': [{'path': p, 'sha256': h} for p, h in sorted(source_hashes.items())],
        'observations': builder.observations, 'provenance': builder.provenance,
        'facts': [builder.facts[f] for f in sorted(builder.facts)]}


# Subject matter is derived from taught recipe categories or an exact active
# knowledge consumer, never from magazine IDs or their display names.


def supplement_learning_media(root, semantic, by_item, builder, source_hashes):
    """Current declared learning purpose and category-scoped recorded content.

    Runtime learned-state mutation and a particular recording's identity are
    separate. A category-level existential capability never promises every
    recording contains the same lesson or effect.
    """
    import hashlib
    rule = 'declared_learning_and_recorded_content'
    def observe(path, locator=None, content=None):
        raw = (root / path).read_bytes()
        source_hashes[path] = hashlib.sha256(raw).hexdigest()
        text = raw.decode('utf-8-sig')
        return text, builder.observe(path, locator or path, content or {'source_text': text})
    read, read_ref = observe('lua/client/TimedActions/ISReadABook.lua')
    ui, ui_ref = observe('lua/client/ISUI/ISLiteratureUI.lua')
    tooltip, tooltip_ref = observe('lua/shared/Translate/EN/Tooltip_EN.txt')
    if not all(x in reader.mask(read, lua=True) for x in (
            'self.character:ReadLiterature(self.item)', 'self.item:getTeachedRecipes()')) or (
            'getKnownRecipes():containsAll(item.item:getTeachedRecipes())' not in ui or
            'Tooltip_Literature_TeachedRecipes = "Teaches Recipe: %1"' not in tooltip):
        raise ValueError('declared literature learning consumer changed')
    # Read current script declarations with the existing comment-aware reader.
    recipes = defaultdict(list)
    for path in sorted((root / 'scripts').rglob('*.txt')):
        text = path.read_text(encoding='utf-8-sig')
        for record in reader.declarations(text, path.relative_to(root).as_posix()):
            if record['kind'] == 'recipe':
                recipes[record['name']].append(record)
    special_sources = {
        'Mechanics': ('lua/client/Vehicles/ISUI/ISVehicleMechanics.lua', 'self.chr:isRecipeKnown(recipe)'),
        'Herbalist': ('lua/client/ISUI/ISInventoryPane.lua', 'playerObj:isRecipeKnown("Herbalist")'),
        'Generator': ('lua/client/ISUI/ISWorldObjectContextMenu.lua', 'playerObj:isRecipeKnown("Generator")'),
        'MetalConstruction': ('lua/client/Blacksmith/ISUI/ISBlacksmithMenu.lua', 'playerObj:isRecipeKnown("Make Metal Walls")'),
    }
    specials = {'Basic Mechanics': 'Mechanics', 'Intermediate Mechanics': 'Mechanics',
                'Advanced Mechanics': 'Mechanics', 'Herbalist': 'Herbalist', 'Generator': 'Generator',
                'Make Metal Walls': 'MetalConstruction', 'Make Metal Roof': 'MetalConstruction',
                'Make Metal Containers': 'MetalConstruction', 'Make Metal Fences': 'MetalConstruction'}
    reading = {f['item_id'] for f in semantic.get('facts', []) if f['payload'].get('function') == 'read_literature'}
    media_rows = []
    for item, declarations in sorted(by_item.items()):
        if any(o['content'].get('property_conflicts') for _, o in declarations):
            continue
        unique = {(o['source_path'], o['content']['raw'].replace('\r\n', '\n')): (ref, o)
                  for ref, o in declarations if not o['content'].get('property_conflicts')}
        if len(unique) != 1:
            continue
        ref, observation = next(iter(unique.values()))
        fields = reader.unique_properties(observation['content'])
        if fields is None or fields.get('OBSOLETE', '').lower() == 'true':
            continue
        source_hashes[observation['source_path']] = observation['source_sha256']
        builder.observations[ref] = observation
        if fields.get('MediaCategory'):
            media_rows.append((item, ref, fields['MediaCategory']))
        if item not in reading or fields.get('Type') != 'Literature' or not fields.get('TeachedRecipes'):
            continue
        topics = defaultdict(list)
        for knowledge in fields['TeachedRecipes'].split(';'):
            knowledge = knowledge.strip()
            if knowledge in specials:
                topic = specials[knowledge]
                path, guard = special_sources[topic]
                text, evidence = observe(path)
                if guard not in reader.mask(text, lua=True):
                    raise ValueError('literature knowledge consumer changed: ' + knowledge)
                topics[topic].append(evidence)
            else:
                candidates = recipes.get(knowledge, [])
                if not candidates:
                    continue  # No inferred subject from the title or a missing recipe.
                # Repeated recipe names are legitimate overloads. A shared
                # category across every declaration supports the same lesson;
                # never select a first overload or its particular result.
                categories = [reader.properties(recipe, ':').get('Category', []) for recipe in candidates]
                if any(len(c) != 1 for c in categories) or len({c[0] for c in categories}) != 1:
                    continue
                category = categories[0][0]
                if category not in LEARNING_PURPOSES:
                    continue
                for recipe in candidates:
                    _, evidence = observe(recipe['path'], str(recipe['line']) + ':recipe:' + knowledge, recipe)
                    topics[category].append(evidence)
        for topic, evidence in sorted(topics.items()):
            builder.fact(item, 'direct_function', {'function': 'learn_literature_' + topic.lower()},
                         [ref, read_ref, ui_ref, tooltip_ref, *sorted(set(evidence))], rule, ['activity:reading'])
    data, data_ref = observe(MEDIA_DATA)
    loader, loader_ref = observe(MEDIA_LOADER)
    interactions, interactions_ref = observe(RADIO_INTERACTIONS)
    if not all(x in loader for x in ('rc:register(v.category, k, v.itemDisplayName', 'data:addLine(j.text, j.r, j.g, j.b, j.codes)')) or not all(x in interactions for x in ('Events.OnDeviceText.Add', 'player:learnRecipe(recipe)', 'bodyDamage:setBoredomLevel(val)', '_player:getXp():AddXP')):
        raise ValueError('recorded-content consumer changed')
    skill_codes = set(re.findall(r'Interactions\.(\w+)\s*=\s*function[^\n]*doSkill', interactions))
    categories = defaultdict(set)
    for match in re.finditer(r'RecMedia\["([^"\n]+)"\]\s*=\s*\{(.*?)\n\};', data, re.S):
        category = re.search(r'category\s*=\s*"([^"\n]+)"', match[2])
        if category:
            categories[category[1]].update(code for value in re.findall(r'codes\s*=\s*"([^"\n]*)"', match[2]) for code in value.split(',') if code)
    for item, ref, category in media_rows:
        codes = categories.get(category, set())
        outcomes = set()
        if any(re.fullmatch(r'BOR-([0-9.]+)', c) and float(c[4:]) > 0 for c in codes): outcomes.add('boredom')
        if any(c[:3] in skill_codes and re.fullmatch(r'\w{3}\+([0-9.]+)', c) and float(c[4:]) > 0 for c in codes): outcomes.add('skills')
        if any(c.startswith('RCP=') and len(c)>4 for c in codes): outcomes.add('recipes')
        for prefix, outcome in (('STS', 'stress'), ('PAN', 'panic')):
            if any(c.startswith(prefix + '+') and float(c[4:]) > 0 for c in codes): outcomes.add(outcome)
        for outcome in sorted(outcomes):
            builder.fact(item, 'direct_function', {'function': 'recorded_content_' + outcome},
                         [ref, data_ref, loader_ref, interactions_ref], rule, ['item:direct'])
    return {rule: {'revision': '1', 'review_state': 'reviewed',
        'preconditions': 'Unique non-obsolete admitted Literature/MediaCategory declaration; active reading/knowledge UI or recorded content loader and interaction consumer.',
        'transformation': 'Declared taught knowledge is joined to recipe categories or exact active knowledge consumers. Recording purposes are existential over actual registered category contents and signed handlers.',
        'exceptions': 'No guaranteed native learning completion, particular recording identity, every-recording effect, timing, arithmetic, experience amount or automatic learning by the playback device.'}}


# Authored attachment purposes joined to admitted installation, not inferred from names.


def supplement_attachment_purposes(root, semantic, by_item, builder, source_hashes):
    """Expose the exact authored purpose, retaining native stat arithmetic as a boundary."""
    import hashlib
    from . import source_reader as reader
    rule = 'declared_attachment_purpose'
    path = 'lua/shared/Translate/EN/Tooltip_EN.txt'
    raw = (root / path).read_bytes()
    text = raw.decode('utf-8-sig')
    source_hashes[path] = hashlib.sha256(raw).hexdigest()
    for item, records in sorted(by_item.items()):
        if any(o['content'].get('property_conflicts') for _, o in records):
            continue
        unique = {(o['source_path'], o['source_sha256'], o['locator'].split(':', 1)[0],
                   o['content']['raw'].replace('\r\n', '\n')): (ref, o)
                  for ref, o in records}
        if len(unique) != 1:
            continue
        ref, observation = next(iter(unique.values()))
        content = observation['content']
        props = reader.properties({'clauses': content.get('clauses', [])}, '=')
        if content.get('property_conflicts') or props.get('Type') != ['WeaponPart'] or len(props.get('Tooltip', [])) != 1:
            continue
        purpose = ATTACHMENT_PURPOSES.get(props['Tooltip'][0])
        if purpose is None:
            continue
        expected, name, checks, _, _ = purpose
        for field, sign in checks:
            values = props.get(field, [])
            if len(values) != 1 or not re.fullmatch(r'-?\d+(?:\.\d+)?', values[0]) or float(values[0]) * sign <= 0:
                raise ValueError('attachment purpose declaration changed: ' + item + '/' + field)
        key = props['Tooltip'][0]
        readings = re.findall(r'^\s*' + re.escape(key) + r'\s*=\s*"([^"\r\n]*)"\s*,?\s*$', text, re.M)
        if readings != [expected]:
            raise ValueError('attachment purpose text changed: ' + key)
        dispatch = [f for f in semantic['facts'] if f['item_id'] == item and f['fact_kind'] == 'direct_function'
                    and f['payload'].get('function') == 'attach_weapon_part']
        if not dispatch:
            continue
        refs = sorted({r for f in dispatch for p in f['provenance_refs'] for r in semantic['provenance'][p]['observation_refs']})
        for r in [ref, *refs]:
            observed = semantic['observations'][r]
            source_hashes[observed['source_path']] = observed['source_sha256']
            builder.observations[r] = observed
        label = builder.observe(path, key, {'tooltip_key': key, 'purpose_text': expected})
        builder.fact(item, 'direct_function', {'function': 'attachment_purpose_' + name},
                     [ref, label, *refs], rule, ['item:direct'])
    return {rule: {'revision': '1', 'review_state': 'reviewed',
        'preconditions': 'Unique WeaponPart declaration, admitted compatible mount action, exact authored Tooltip purpose and consistent modifier declarations.',
        'transformation': 'Expose the explicitly authored attachment purpose and its stated tradeoffs, not just mount/remove procedures.',
        'exceptions': 'No invented purpose for missing tooltips, inferred function from item names, numeric effect, native recalculation guarantee or universal compatibility.'}}


def supplement_native_device_purposes(root, semantic, by_item, builder, source_hashes):
    """Admit purposes from reviewed native consumers, not device names."""
    import hashlib
    import json
    from . import source_reader as reader
    path = 'Iris/build/description/source_support/b41_device_purposes.json'
    raw = (root / path).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != '29d555b32ff7e2740c06e31fce8f149543707b58636e4ddb5bdf428635e78ce0':
        raise ValueError('reviewed B41 device-purpose snapshot changed')
    data = json.loads(raw)
    source_hashes[path] = digest
    for binding in data['consumer_bindings']:
        if hashlib.sha256((root / binding['path']).read_bytes()).hexdigest() != binding['sha256']:
            raise ValueError('B41 device consumer changed: ' + binding['path'])
        source_hashes[binding['path']] = binding['sha256']
    admitted = {}
    for fact in semantic.get('facts', []):
        admitted.setdefault(fact['item_id'], set()).add(fact['payload'].get('function'))
    for item, records in sorted(by_item.items()):
        unique = {(o['source_path'], o['source_sha256'], o['locator'].split(':', 1)[0],
                   o['content']['raw'].replace('\r\n', '\n')): (ref, o) for ref, o in records}
        if len(unique) != 1 or any(o['content'].get('property_conflicts') for _, o in records):
            continue
        ref, observation = next(iter(unique.values()))
        fields = reader.properties({'clauses': observation['content'].get('clauses', [])}, '=')
        fields = {k: v[0] for k, v in fields.items() if len(v) == 1}
        functions = admitted.get(item, set())
        selected = []
        noise_range = fields.get('NoiseRange', '')
        if (fields.get('Type') == 'Weapon' and 'place_trigger_device' in functions
                and re.fullmatch(r'\d+(?:\.\d+)?', noise_range) and float(noise_range) > 0):
            selected.append(('noise', 'emit_attracting_noise'))
        def positive(key):
            value = fields.get(key, '')
            return bool(re.fullmatch(r'\d+(?:\.\d+)?', value)) and float(value) > 0

        # Placement reaches IsoTrap directly. An instantaneous non-ball throw
        # reaches the same consumer through IsoMolotovCocktail.Explode.
        thrown_trap = ('request_physics_attack' in functions
                       and fields.get('PhysicsObject') not in {None, '', 'Ball'}
                       and all(re.fullmatch(r'0+(?:\.0+)?', fields.get(key, '0'))
                               for key in ('ExplosionTimer', 'SensorRange'))
                       and fields.get('CanBeRemote', '').lower() != 'true')
        if fields.get('Type') == 'Weapon' and ('place_trigger_device' in functions or thrown_trap):
            for purpose, function, properties in (
                ('explosion', 'device_explosion_damage', ('ExplosionRange', 'ExplosionPower')),
                ('fire', 'device_start_fire', ('FireRange', 'FirePower')),
                ('smoke', 'device_smoke_distraction', ('SmokeRange',)),
            ):
                if all(positive(key) for key in properties):
                    selected.append((purpose, function))
        if 'control_installed_generator' in functions:
            selected.append(('power', 'supply_nearby_electricity'))
        for purpose, function in selected:
            proof = builder.observe(path, 'native:' + purpose, {'kind': 'reviewed_native_device_purpose',
                'reading': data['readings'][purpose], 'native_bindings': data['native_bindings'],
                'consumer_bindings': data['consumer_bindings']})
            builder.observations[ref] = observation
            source_hashes[observation['source_path']] = observation['source_sha256']
            builder.fact(item, 'direct_function', {'function': function}, [ref, proof],
                         'native_device_purpose', ['item:direct'])
    return {'native_device_purpose': {'revision': '2', 'review_state': 'reviewed',
        'preconditions': 'Unique admitted declaration and admitted placement, instantaneous non-ball throw or generator control. Each effect requires its positive consumed properties.',
        'transformation': 'Join placement/throwing to reviewed noise, blast, fire or smoke consumers; join generator control to nearby electricity.',
        'exceptions': 'No guaranteed hit, ignition, escape, universal zombie response, unlimited power range, item-name matching or unreviewed native behavior.'}}


def supplement_vehicle_tool_purposes(root, semantic, by_item, builder, source_hashes):
    """Recover kept tools from paired vehicle operations, without an item allowlist."""
    import hashlib
    from .recovery_relations import vehicle_tool_roles, VEHICLE_PART_CATEGORIES
    from . import source_reader as reader
    rule = 'paired_vehicle_template_tool'
    existing = {f['item_id'] for f in semantic.get('facts', [])
                if f['payload'].get('function') == 'service_vehicle_parts'}
    tool_templates = {}
    for path in sorted((root / 'scripts/vehicles').glob('template_*.txt')):
        text = path.read_text(encoding='utf-8-sig')
        template = re.search(r'\btemplate\s+vehicle\s+(\w+)', reader.mask(text))
        if not template or template[1] not in VEHICLE_PART_CATEGORIES:
            continue
        for item in set(re.findall(r'\btype\s*=\s*(\w+\.\w+)', reader.mask(text))):
            if item not in existing and item in by_item and vehicle_tool_roles(text, item):
                tool_templates.setdefault(item, []).append(path.relative_to(root).as_posix())
    paths = (VEHICLE_MENU, VEHICLE_MECHANICS, VEHICLE_INSTALL, VEHICLE_UNINSTALL,
             VEHICLE_CALLBACKS, VEHICLE_COMMANDS)
    consumer_refs = []
    for path in paths:
        raw = (root / path).read_bytes()
        text = raw.decode('utf-8-sig')
        if path == VEHICLE_MENU and not all(token in text for token in (
                'function ISVehiclePartMenu.equipRequiredItems', 'item.equip == "primary"',
                'item.equip == "secondary"', 'part:getTable("install")', 'part:getTable("uninstall")')):
            raise ValueError('reviewed vehicle tool consumer changed')
        source_hashes[path] = hashlib.sha256(raw).hexdigest()
        consumer_refs.append(builder.observe(path, 'paired vehicle tool consumer', {'source_text': text}))
    for item, paths in sorted(tool_templates.items()):
        records = by_item[item]
        unique = {(o['source_path'], o['source_sha256'], o['content']['raw'].replace('\r\n', '\n')):
                  (ref, o) for ref, o in records}
        if len(unique) != 1 or any(o['content'].get('property_conflicts') for _, o in records):
            continue
        ref, obs = next(iter(unique.values()))
        builder.observations[ref] = obs
        source_hashes[obs['source_path']] = obs['source_sha256']
        evidence = [ref, *consumer_refs]
        for path in paths:
            raw = (root / path).read_bytes()
            source_hashes[path] = hashlib.sha256(raw).hexdigest()
            evidence.append(builder.observe(path, 'paired vehicle tool template', {'source_text': raw.decode('utf-8-sig')}))
        builder.fact(item, 'direct_function', {'function': 'service_vehicle_parts'}, evidence, rule, ['item:direct'])
    return {rule: {'revision': '1', 'review_state': 'reviewed',
                  'preconditions': 'Unique admitted item declaration; explicit kept tool in both install and uninstall of a reviewed vehicle part category.',
                  'transformation': 'Join template requirements to inventory transfer, hand equipment and vehicle installation/removal consumers. Primary/both is the working tool; secondary or unequipped kept items support the operation.',
                  'exceptions': 'No item-name allowlist, inferred lifting animation, unpaired action, detailed part inventory or new runtime behavior.'}}


def supplement_placed_purposes(root, semantic, by_item, builder, source_hashes):
    """Join the reviewed B41 base-game sprite projection to admitted placement.

    The snapshot records original binary hashes and matching Lua consumers.
    No game install, native runtime dependency or mod-sprite inference is used
    by the producer. Only explicitly joined property consumers license a use.
    """
    import hashlib
    import json
    from . import source_reader as reader
    path = 'Iris/build/description/source_support/b41_placed_object_properties.json'
    raw = (root / path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != '9bad7eb46d3cea3dcef9e4368e73d33643e34105ce157f75982ec0d1b63cd74b':
        raise ValueError('reviewed B41 placed-property snapshot changed')
    data = json.loads(raw)
    source_hashes[path] = hashlib.sha256(raw).hexdigest()
    for binding in data['consumer_bindings']:
        if hashlib.sha256((root / binding['path']).read_bytes()).hexdigest() != binding['sha256']:
            raise ValueError('B41 property consumer changed: ' + binding['path'])
        source_hashes[binding['path']] = binding['sha256']
    functions_by_item = {}
    for fact in semantic.get('facts', []):
        functions_by_item.setdefault(fact['item_id'], set()).add(fact['payload'].get('function'))
    registry_path = 'lua/client/Moveables/ISMoveableDefinitions.lua'
    registry = (root / registry_path).read_text(encoding='utf-8-sig')
    scrap_tools = {}
    for material, first, second in re.findall(r'^\s*moveableDefinitions\.addScrapDefinition\(\s*"([^"]+)"\s*,\s*\{([^}]*)\}\s*,\s*\{([^}]*)\}', registry, re.M):
        if not re.search(r'moveableDefinitions\.addScrapItem\(\s*"' + re.escape(material) + '"', registry):
            continue
        tools1 = set(re.findall(r'"([^"]+)"', first)); tools2 = set(re.findall(r'"([^"]+)"', second))
        if tools1 == {'Base.BlowTorch'} and tools2 == {'Tag.WeldingMask', 'Base.WeldingMask'}: scrap_tools[material] = 'salvage_welding'
        elif tools1 == {'Base.Hammer'} and tools2 == {'Base.Saw'}: scrap_tools[material] = 'salvage_wood'
        elif tools1 == {'Base.Screwdriver'} and not tools2: scrap_tools[material] = 'salvage_screwdriver'
        elif tools1 == {'Base.Hammer'} and not tools2: scrap_tools[material] = 'salvage_hammer'
    for item, records in sorted(by_item.items()):
        unique = {(o['source_path'], o['source_sha256'], o['locator'].split(':', 1)[0],
                   o['content']['raw'].replace('\r\n', '\n')): (ref, o) for ref, o in records}
        if len(unique) != 1:
            continue
        ref, observation = next(iter(unique.values()))
        if observation['content'].get('property_conflicts'):
            continue
        props = reader.properties({'clauses': observation['content'].get('clauses', [])}, '=')
        props = {k: v[0] for k, v in props.items() if len(v) == 1}
        functions = functions_by_item.get(item, set())
        selected = []
        sprite = props.get('WorldObjectSprite')
        entry = data['sprites'].get(sprite)
        if entry and props.get('Type') == 'Moveable' and props.get('DisplayCategory') == 'Furniture' and 'place_moveable_furniture' in functions:
            fields = entry['properties']
            if 'bed' in fields: selected.append('sleep')
            if fields.get('container') in {'fridge', 'freezer'}: selected.append('cold_storage')
            elif fields.get('IsoType') == 'IsoStove': selected.append('cooking')
            elif fields.get('IsoType') == 'IsoClothingWasher': selected.append('washing')
            elif fields.get('IsoType') == 'IsoClothingDryer': selected.append('drying')
            elif fields.get('IsoType') == 'IsoFireplace': selected.append('hearth')
            elif fields.get('IsoType') == 'IsoBarbecue': selected.append('barbecue')
            elif fields.get('IsoType') == 'IsoMannequin': selected.append('mannequin')
            elif 'container' in fields: selected.append('storage')
            if float(fields.get('Surface', '0')) + float(fields.get('ItemHeight', '0')) > 0: selected.append('surface')
            if 'waterPiped' in fields: selected.append('water_piped')
            elif 'waterAmount' in fields: selected.append('water_storage')
            if 'lightswitch' in fields and all(k in fields for k in ('lightR', 'lightG', 'lightB')): selected.append('light')
            if 'IsMirror' in fields: selected.append('mirror')
            if 'CanScrap' in fields and 'ScrapUseTool' not in fields and fields.get('Material') in scrap_tools:
                selected.append(scrap_tools[fields['Material']])
            for purpose in selected:
                proof = builder.observe(path, 'sprite:' + sprite, {'kind': 'reviewed_sprite_properties',
                    'sprite': sprite, 'properties': fields, 'original_source': entry['source'],
                    'consumer_bindings': data['consumer_bindings'], 'native_bindings': data['native_bindings']})
                builder.observations[ref] = observation
                source_hashes[observation['source_path']] = observation['source_sha256']
                builder.fact(item, 'direct_function', {'function': 'placed_purpose_' + purpose},
                             [ref, proof], 'placed_sprite_purpose', ['item:direct'])
        # Positive aiming modifiers raise the threshold before the native
        # ranged hit-chance calculation applies its movement penalty. Missing
        # Tooltip alone must not hide that supported role. No lighting/stabbing
        # effect is inferred from a WeaponPart's name or mesh.
        if props.get('Type') == 'WeaponPart' and 'attach_weapon_part' in functions and float(props.get('AimingTimeModifier', '0')) > 0:
            proof = builder.observe(path, 'attachment:aiming', {'kind': 'reviewed_native_attachment_parameter',
                'reading': data['native_readings']['attachment'], 'scope_review': data['attachment_scope_review'], 'native_bindings': data['native_bindings']})
            builder.observations[ref] = observation
            source_hashes[observation['source_path']] = observation['source_sha256']
            builder.fact(item, 'direct_function', {'function': 'attachment_purpose_movement_aim'},
                         [ref, proof], 'native_attachment_purpose', ['item:direct'])
    return {'placed_sprite_purpose': {'revision': '1', 'review_state': 'reviewed',
        'preconditions': 'Unique admitted Moveable/Furniture declaration, admitted placement, exact WorldObjectSprite join and reviewed B41 property consumers.',
        'transformation': 'Expose supported placed-object purposes with supply conditions; retain unknown properties without inventing uses.',
        'exceptions': 'No inferred purpose from item names, mod properties, generic decoration or unjoined appliance behavior.'},
        'native_attachment_purpose': {'revision': '1', 'review_state': 'reviewed',
        'preconditions': 'Unique WeaponPart, admitted mount action, positive AimingTimeModifier, native part addition and ranged hit-chance movement-penalty consumption.',
        'transformation': 'Expose the supported movement-related aiming role even without Tooltip.',
        'exceptions': 'No light source, stabbing, damage or universal mount compatibility inferred from name.'}}
