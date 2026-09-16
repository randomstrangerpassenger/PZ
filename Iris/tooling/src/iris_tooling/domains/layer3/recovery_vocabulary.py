"""Shared predicate, path and phrase definitions; no recovery work runs here."""

PAINT_MENU = 'lua/client/BuildingObjects/ISUI/ISPaintMenu.lua'

PAINT_CURSOR = 'lua/server/BuildingObjects/ISPaintCursor.lua'

PAINT_ACTION = 'lua/client/BuildingObjects/TimedActions/ISPaintAction.lua'

SIGN_ACTION = 'lua/client/BuildingObjects/TimedActions/ISPaintSignAction.lua'

MOVE_CURSOR = 'lua/server/BuildingObjects/ISMoveableCursor.lua'

PADLOCK_ACTION = 'lua/client/TimedActions/ISPadlockAction.lua'

DOOR_LOCK = 'lua/client/TimedActions/ISLockDoor.lua'

DIGITAL_CODE = 'lua/client/ISUI/ISDigitalCode.lua'

VEHICLE_START = 'lua/client/Vehicles/TimedActions/ISStartVehicleEngine.lua'

VEHICLE_DASHBOARD = 'lua/client/Vehicles/ISUI/ISVehicleDashboard.lua'

TRANSFER_WATER = 'lua/client/TimedActions/ISTransferWaterAction.lua'

ADD_WATER = 'lua/client/TimedActions/ISAddWaterFromItemAction.lua'

WATER_PLANT = 'lua/client/Farming/TimedActions/ISWaterPlantAction.lua'

WASH_VEHICLE = 'lua/client/Vehicles/TimedActions/ISWashVehicle.lua'

CURE_MILDEW = 'lua/client/Farming/TimedActions/ISCureMildewAction.lua'

CURE_FLIES = 'lua/client/Farming/TimedActions/ISCureFliesAction.lua'

FIREARM = 'lua/client/TimedActions/ISReloadWeaponAction.lua'

WORLD_MENU = 'lua/client/ISUI/ISWorldObjectContextMenu.lua'

OBJECT_COMMANDS = 'lua/server/ClientCommands.lua'

PLUMB_ACTION = 'lua/client/TimedActions/ISPlumbItem.lua'

FITNESS_SOURCES = ('lua/shared/Definitions/FitnessExercises.lua', 'lua/client/ISUI/ISFitnessUI.lua', 'lua/client/TimedActions/ISFitnessAction.lua')

CHOP = 'lua/client/TimedActions/ISChopTreeAction.lua'

BODY_LOCATIONS = 'lua/shared/NPCs/BodyLocations.lua'

LOAD_MAGAZINE = 'lua/client/TimedActions/ISLoadBulletsInMagazine.lua'

INSERT_MAGAZINE = 'lua/client/TimedActions/ISInsertMagazine.lua'

WEAPON_UPGRADE = 'lua/client/TimedActions/ISUpgradeWeapon.lua'

WEAPON_REMOVAL = 'lua/client/TimedActions/ISRemoveWeaponUpgrade.lua'

MAP_VIEW = 'lua/client/ISUI/Maps/ISMap.lua'

MAP_DEFINITIONS = 'lua/client/ISUI/Maps/ISMapDefinitions.lua'

LEGACY_MEDIA_MENU = 'lua/client/Context/World/ISContextDisksAndTapes.lua'

LEGACY_RELOAD = 'lua/shared/Reloading/ISReloadUtil.lua'

TUTORIAL_MENU = 'lua/client/Tutorial/Tutorial1.lua'

PLACE_OBJECT = 'lua/server/BuildingObjects/ISPlace3DItemCursor.lua'

WASH_BODY = 'lua/client/TimedActions/ISWashYourself.lua'

WASH_CLOTHING = 'lua/client/TimedActions/ISWashClothing.lua'

DROP_OBJECT = 'lua/client/TimedActions/ISDropWorldItemAction.lua'

GARMENT_UI = 'lua/client/ISUI/ISGarmentUI.lua'

PATCH_GARMENT = 'lua/client/TimedActions/ISRepairClothing.lua'

REMOVE_PATCH = 'lua/client/TimedActions/ISRemovePatch.lua'

MAP_SYMBOLS = 'lua/client/ISUI/Maps/ISWorldMapSymbols.lua'

MAP_TEXT = 'lua/client/ISUI/Maps/ISTextBoxMap.lua'

NOTE_EDITOR = 'lua/client/ISUI/ISUIWriteJournal.lua'

MAKEUP_UI = 'lua/client/ISUI/ISMakeUpUI.lua'

MAKEUP_DEFINITIONS = 'lua/shared/Definitions/MakeUpDefinitions.lua'

ALARM_DIALOG = 'lua/client/ISUI/ISAlarmClockDialog.lua'

ALARM_STOP = 'lua/client/TimedActions/ISStopAlarmClockAction.lua'

DEVICE_TIMER = 'lua/client/ISUI/ISBombTimerDialog.lua'

DEVICE_PLACE = 'lua/client/TimedActions/ISPlaceTrap.lua'

DEVICE_TAKE = 'lua/client/TimedActions/ISTakeTrap.lua'

RELOAD_ACTIONS = tuple('lua/client/TimedActions/' + name + '.lua' for name in (
    'ISEjectMagazine', 'ISRackFirearm', 'ISUnloadBulletsFromMagazine', 'ISUnloadBulletsFromFirearm'))

VEHICLE_MECHANICS = 'lua/client/Vehicles/ISUI/ISVehicleMechanics.lua'

VEHICLE_MENU = 'lua/client/Vehicles/ISUI/ISVehiclePartMenu.lua'

VEHICLE_INSTALL = 'lua/client/Vehicles/TimedActions/ISInstallVehiclePart.lua'

VEHICLE_UNINSTALL = 'lua/client/Vehicles/TimedActions/ISUninstallVehiclePart.lua'

VEHICLE_COMMANDS = 'lua/server/Vehicles/VehicleCommands.lua'

VEHICLE_CALLBACKS = 'lua/server/Vehicles/Vehicles.lua'

VEHICLE_RUNNING_FORMS = {**{grade + 'Tire': 'tire' for grade in ('Old', 'Normal', 'Modern')},
                         **{grade + 'Brake': 'brake' for grade in ('Old', 'Normal', 'Modern')},
                         **{grade + 'Suspension': 'suspension' for grade in ('Normal', 'Modern')},
                         **{grade + 'CarMuffler': 'muffler' for grade in ('Old', 'Normal', 'Modern')}}

VEHICLE_RUNNING_TEMPLATES = tuple('scripts/vehicles/template_' + k + '.txt' for k in ('tire', 'brake', 'suspension', 'muffler'))

TIRE_ACTIONS = ('lua/client/Vehicles/TimedActions/ISInflateTire.lua', 'lua/client/Vehicles/TimedActions/ISDeflateTire.lua')

VEHICLE_USE_MENU = 'lua/client/Vehicles/ISUI/ISVehicleMenu.lua'

VEHICLE_DOOR_ACTIONS = tuple('lua/client/Vehicles/TimedActions/' + name + '.lua' for name in (
    'ISOpenVehicleDoor', 'ISCloseVehicleDoor', 'ISUnlockVehicleDoor', 'ISLockVehicleDoor',
    'ISLockDoors', 'ISOpenCloseVehicleWindow', 'ISSmashVehicleWindow', 'ISOpenMechanicsUIAction'))

PANEL_FORMS = {
    'EngineDoor': ('engine_door', 'hood', '후드 패널'),
    'FrontCarDoor': ('door', 'front_door', '도어 패널'),
    'RearCarDoor': ('door', 'rear_door', '도어 패널'),
    'RearCarDoorDouble': ('door', 'double_rear_door', '도어 패널'),
    'TrunkDoor': ('trunk_door', 'trunk_lid', '트렁크 도어'),
    'FrontWindow': ('window', 'front_window', '측면 유리'),
    'RearWindow': ('window', 'rear_window', '후면 유리'),
    'Windshield': ('windshield', 'windshield', '전면 유리'),
    'RearWindshield': ('windshield', 'rear_windshield', '후면 유리'),
}

PANEL_TEMPLATES = tuple('scripts/vehicles/template_' + name + '.txt' for name in sorted({v[0] for v in PANEL_FORMS.values()}))

VEHICLE_STORAGE_FORMS = {
    'SmallTrunk': ('trunk', 'TruckBed', 'scripts/vehicles/vehicle_car_small.txt', '트렁크 모듈'),
    'NormalTrunk': ('trunk', 'TruckBed', None, '트렁크 모듈'),
    'BigTrunk': ('trunk', 'TruckBed', 'scripts/vehicles/vehicle_stepvan.txt', '트렁크 모듈'),
    'TrailerTrunk': ('trunk', 'TrailerTrunk', None, '트렁크 모듈'),
    'VanSeatsTrunk': ('trunk', 'TruckBed', 'scripts/vehicles/vehicle_van_seats.txt', '트렁크 모듈'),
    'GloveBox': ('glovebox', 'GloveBox', None, '글로브 박스'),
    'NormalCarSeat': ('seat', 'Seat*', None, '차량 좌석'),
    'SmallGasTank': ('gastank', 'GasTank', None, '연료 탱크'),
    'NormalGasTank': ('gastank', 'GasTank', None, '연료 탱크'),
    'BigGasTank': ('gastank', 'GasTank', None, '연료 탱크'),
}

VEHICLE_STORAGE_SOURCES = tuple(sorted({'scripts/vehicles/template_' + v[0] + '.txt' for v in VEHICLE_STORAGE_FORMS.values()}
                                       | {v[2] for v in VEHICLE_STORAGE_FORMS.values() if v[2]}))

INVENTORY_PAGE = 'lua/client/ISUI/ISInventoryPage.lua'

VEHICLE_SEAT_UI = 'lua/client/Vehicles/ISUI/ISVehicleSeatUI.lua'

VEHICLE_SEAT_ACTIONS = tuple('lua/client/Vehicles/TimedActions/' + name + '.lua' for name in (
    'ISEnterVehicle', 'ISSwitchVehicleSeat', 'ISExitVehicle', 'ISStopVehicle'))

VEHICLE_FUEL_ACTIONS = tuple('lua/client/Vehicles/TimedActions/' + name + '.lua' for name in (
    'ISAddGasolineToVehicle', 'ISTakeGasolineFromVehicle', 'ISRefuelFromGasPump'))

VEHICLE_EXCHANGE_REQUIREMENTS = {
    'seat': 'The seat template keeps a screwdriver in the primary hand, names Basic Mechanics and Mechanics:1, and requires an empty seat container for removal. These declarations feed the mechanics checks and success/damage roll; the commented hard skill gate is not reinstated.',
    'gastank': 'The gas-tank template keeps a screwdriver in the secondary hand and wrench in the primary hand, names Basic Mechanics and Mechanics:5, and requires an empty tank for removal. These declarations feed the mechanics checks and success/damage roll; the commented hard skill gate is not reinstated.',
}

FARM_MENU = 'lua/client/Farming/ISUI/ISFarmingMenu.lua'

SEED_ACTION = 'lua/client/Farming/TimedActions/ISSeedAction.lua'

FERTILIZE_ACTION = 'lua/client/Farming/TimedActions/ISFertilizeAction.lua'

FARM_CLIENT = 'lua/client/Farming/CFarmingSystem.lua'

FARM_SYSTEM = 'lua/server/Farming/SFarmingSystem.lua'

FARM_COMMANDS = 'lua/server/Farming/farmingCommands.lua'

PLANT = 'lua/server/Farming/SPlantGlobalObject.lua'

SEED_DEFINITIONS = 'lua/server/Farming/farming_vegetableconf.lua'

CAMP_MENU = 'lua/client/Camping/ISUI/ISCampingMenu.lua'

CAMP_FUEL = 'lua/server/Camping/camping_fuel.lua'

CAMP_ADD = 'lua/client/Camping/TimedActions/ISAddFuelAction.lua'

CAMP_LIGHT = 'lua/client/Camping/TimedActions/ISLightFromLiterature.lua'

CAMP_CLIENT = 'lua/client/Camping/CCampfireSystem.lua'

CAMP_SERVER = 'lua/server/Camping/SCampfireSystem.lua'

CAMP_COMMANDS = 'lua/server/Camping/SCampfireSystemCommands.lua'

CAMP_OBJECT = 'lua/server/Camping/SCampfireGlobalObject.lua'

FISHING_UI = 'lua/client/ISUI/ISFishingUI.lua'

FISHING_ACTION = 'lua/client/Fishing/TimedActions/ISFishingAction.lua'

FISHING_PROPERTIES = 'lua/shared/Fishing/fishing_properties.lua'

TRAP_MENU = 'lua/server/Traps/ISUI/ISTrapMenu.lua'

TRAP_BUILD = 'lua/server/Traps/BuildingObjects/TrapBO.lua'

TRAP_DEFINITIONS = 'lua/server/Traps/TrapDefinition.lua'

TRAP_CLIENT = 'lua/client/Traps/CTrapSystem.lua'

TRAP_CLIENT_OBJECT = 'lua/client/Traps/CTrapGlobalObject.lua'

TRAP_SYSTEM = 'lua/server/Traps/STrapSystem.lua'

TRAP_OBJECT = 'lua/server/Traps/STrapGlobalObject.lua'

TRAP_BAIT = 'lua/client/Traps/TimedActions/ISAddBaitAction.lua'

TRAP_COMMANDS = 'lua/server/Traps/trappingCommands.lua'

BUILD_FACTORIES = {
    'onStonePile': 'ISSimpleFurniture', 'onBarbedFence': 'ISBarbedWire',
    'onSangBagWall': 'ISWoodenWall', 'onGravelBagWall': 'ISWoodenWall',
    'onWoodenCross': 'ISSimpleFurniture', 'onWoodenPicket': 'ISSimpleFurniture',
    'onBarElement': 'ISWoodenContainer', 'onWoodenFenceStake': 'ISWoodenWall',
    'onWoodenFence': 'ISWoodenWall', 'onPillarLamp': 'ISLightSource',
    'onWoodenPillar': 'ISWoodenWall', 'onWoodenWallFrame': 'ISWoodenWall',
    'onWoodenWindowsFrame': 'ISWoodenWall', 'onWoodenFloor': 'ISWoodenFloor',
    'onWoodenCrate': 'ISWoodenContainer', 'onCreateBarrel': 'RainCollectorBarrel',
    'onCompost': 'ISCompost', 'onBed': 'ISDoubleTileFurniture',
    'onSmallWoodTable': 'ISSimpleFurniture', 'onSmallWoodTableWithDrawer': 'ISSimpleFurniture',
    'onLargeWoodTable': 'ISDoubleTileFurniture', 'onWoodChair': 'ISSimpleFurniture',
    'onBookcase': 'ISSimpleFurniture', 'onSmallBookcase': 'ISSimpleFurniture',
    'onShelve': 'ISSimpleFurniture', 'onSign': 'ISSimpleFurniture', 'onDoubleShelve': 'ISSimpleFurniture',
    'onBrownWoodenStairs': 'ISWoodenStairs', 'onDoubleWoodenDoor': 'ISDoubleDoor',
    'onWoodenDoor': 'ISWoodenDoor', 'onWoodenDoorFrame': 'ISWoodenDoorFrame',
}

BUILD_CLASSES = {name: ('lua/server/RainBarrel/BuildingObjects/' if name == 'RainCollectorBarrel'
                      else 'lua/server/BuildingObjects/') + name + '.lua' for name in set(BUILD_FACTORIES.values())}

INACTIVE_BUILD_FACTORIES = {'onWoodenWall', 'onWoodenBrownFloor', 'onWoodenLightBrownFloor',
                            'onDarkWoodenStairs', 'onLightBrownWoodenStairs'}

TAKE_WATER = 'lua/client/TimedActions/ISTakeWaterAction.lua'

PICKUP_GLASS = 'lua/client/TimedActions/ISPickupBrokenGlass.lua'

WINDOW_GLASS = 'lua/client/TimedActions/ISRemoveBrokenGlass.lua'

MOVE_TOOLS = 'lua/client/Moveables/ISMoveableTools.lua'

ADD_ROPE = 'lua/client/TimedActions/ISAddSheetRope.lua'

REMOVE_ROPE = 'lua/client/TimedActions/ISRemoveSheetRope.lua'

CLIMB_ROPE = 'lua/client/TimedActions/ISClimbSheetRopeAction.lua'

WELDING_MENU = 'lua/client/Blacksmith/ISUI/ISBlacksmithMenu.lua'

FIRE_FIGHTING = 'lua/server/FireFighting/FireFighting.lua'

EXTINGUISH_CURSOR = 'lua/server/FireFighting/ISExtinguishCursor.lua'

PUT_OUT_FIRE = 'lua/client/TimedActions/ISPutOutFire.lua'

GROUND_MENU = 'lua/client/BuildingObjects/ISUI/ISInventoryBuildMenu.lua'

GROUND_CURSOR = 'lua/server/BuildingObjects/ISShovelGroundCursor.lua'

SHOVEL_GROUND = 'lua/client/BuildingObjects/TimedActions/ISShovelGround.lua'

NATURAL_FLOOR = 'lua/server/BuildingObjects/ISNaturalFloor.lua'

DUMP_CONTENTS = 'lua/client/TimedActions/ISDumpContentsAction.lua'

DUMP_WATER = 'lua/client/TimedActions/ISDumpWaterAction.lua'

HEALTH = 'lua/client/XpSystem/ISUI/ISHealthPanel.lua'

DISINFECT = 'lua/client/TimedActions/ISDisinfect.lua'

SPLINT = 'lua/client/TimedActions/ISSplint.lua'

STITCH = 'lua/client/TimedActions/ISStitch.lua'

CLEAN_BURN = 'lua/client/TimedActions/ISCleanBurn.lua'

CLEAN_BANDAGE = 'lua/client/TimedActions/ISCleanBandage.lua'

REMOVE_GLASS = 'lua/client/TimedActions/ISRemoveGlass.lua'

REMOVE_BULLET = 'lua/client/TimedActions/ISRemoveBullet.lua'

POULTICES = {name: 'lua/client/TimedActions/' + action + '.lua' for name, action in
             (('ComfreyCataplasm', 'ISComfreyCataplasm'), ('PlantainCataplasm', 'ISPlantainCataplasm'),
              ('WildGarlicCataplasm', 'ISGarlicCataplasm'))}

PLACEMENT = 'The furniture must support placement, be available with all required parts, and meet space, surface, tool, skill, reach and multiplayer permission requirements.'

PICKUP = 'The placed form must be a movable world object with its required parts and satisfy the object-specific contents, capacity, support, water, fire, window, tool and skill checks. The character must stay within reach on the same floor and have multiplayer permission.'

PICKUP_LOSS = 'Removing furniture can break it. Removing the placed form does not guarantee return of an intact item or the same inventory item type.'

PAINTING = 'A paintbrush and the selected paint are required for a compatible paintable surface or wall sign; normal painting consumes paint.'

OPENING = 'The opening recipe must accept this package and all its companion tools and eligibility requirements must be satisfied; crafting is unavailable while driving.'

CAN_OPENING = 'The opening recipe requires a compatible CanOpener-tagged tool and the specified unopened can; both must be available and crafting eligibility must hold, including not driving.'

JAR_BOX_OPENING = OPENING + ' The exact Open Box of Jars recipe declares EmptyJar=6 and Time 15; its callback additionally requests six Base.JarLid items in the player inventory. Native recipe result/count delivery and AddItems creation remain separate from this source-level request.'

EGG_CARTON_OPENING = OPENING + ' OpenEggCarton copies the age of the first supplied input to the supplied result. The native recipe selects those arguments and delivers the declared results; the callback does not establish renewed freshness.'

PRODUCE_SACK_OPENING = OPENING + ' OpenSackProduce copies the age of the first supplied input to the supplied result and requests one EmptySandbag in the player inventory. Native argument selection and output delivery remain separate; opening does not establish a reverse packing recipe.'

FIRING = 'Normal firing requires an unjammed weapon and a chambered round when it has a chamber, otherwise ammunition remaining; the character must be permitted to attack.'

MELEE = 'The weapon must use the non-ranged attack branch, the character must not already be attacking, and player melee authorization must hold. Ordinary weapon attacks require being outside a vehicle; hit, damage and target results are not established by this dispatch.'

CHOPPING = 'A reachable existing tree and an axe held in the primary hand are required; the character must be able to attack and the axe must remain usable.'

CONSUMING = 'The item must remain in inventory, any required companion item must be present, and satiety or calorie state must permit starting consumption.'

SMOKING = 'A match or lighter must be present in inventory. The cigarette action must complete; cancellation does not apply its smoking effects.'

SMOKER_EFFECT = 'These cigarette effects apply to a character with the Smoker trait, scaled by the consumed portion and current cigarette stress value.'

NONSMOKER_EFFECT = 'This cigarette sickness effect applies to a character without the Smoker trait and depends on the consumed portion.'

POISONOUS_WILD_FOOD = 'The wild-food consumption effect applies only when the eaten food has positive poison power and depends on the consumed portion.'

WEARING = 'The clothing must remain in inventory and be worn at its configured body location.'

WEAR_ACTION = 'Clothing is transferred into inventory before wearing; it must remain there during the action. Already equipped items are skipped, and walking or running interrupts the wear action.'

COOKING_ACTION = 'The recipe must accept the ingredient for the selected food base. Both are transferred into inventory, the base must remain there, frozen ingredients require recipe permission, and required cooking must be satisfied. Poisonous ingredients must be permitted by the menu poisoning policy; walking or running interrupts adding the ingredient.'

COOKING_BASE = 'The evolved recipe must accept this selected base or prepared result and an available ingredient. Both are transferred into inventory and the base must remain there; ingredient freezing, cooking and poisoning-policy checks apply. Walking or running interrupts addition. Further ingredients and the resulting food state depend on the recipe and current contents.'

NOTE_SAVE = 'Page content and the title are submitted to the notebook only when the journal is confirmed with OK; cancelling does not submit these edits.'

NOTE_EDIT = 'Editing requires a writing implement, no other-user ownership lock, and the journal editing lock to be unlocked.'

NOTE_ACCESS = 'Journal editing controls require a writing implement and no ownership lock belonging to another user.'

NOTE_LIMITS = 'Writing uses the declared writable page count and the journal text-entry limits; viewing existing stored pages is separate from editing permission.'

NOTE_LOCK = 'In an editable journal window, lock and unlock controls immediately change the ownership lock; cancelling page edits does not undo a lock change.'

LOADING = 'The receiver must accept this exact ammunition type and have loading space and ammunition available; a gun is held in the primary hand and a magazine remains in inventory; loading uses action animation events.'

MAGAZINE_LOADING = 'The menu matches exact MagazineType to the magazine FullType and requires a firearm without a magazine. Hold that firearm in the primary hand and retain the magazine until loadFinished. The action does not recheck compatibility. Its animation removes the magazine from inventory/hands, copies its current ammunition count to the gun and sets containsClip; it queues racking only when no round is chambered and enough ammunition remains. Running interrupts, walking and aiming do not. Later ejection creates a new declared magazine and copies the remaining count rather than returning the original item identity or condition.'

MAGAZINE_FILL = 'Select the carried non-weapon magazine with positive MaxAmmo. The menu requires remaining capacity and matching AmmoType ammunition, transferring recursive supplies first. The action rechecks magazine possession and starts only with matching ammunition. Each guarded InsertBullet event removes one matching round and increments the count. Full capacity or exhausted ammunition ends loading; the requested menu count only controls progress display. Running interrupts but walking and aiming do not, and already loaded rounds remain. Animation-driven timing and native item counts remain separate.'

MAGAZINE_EMPTY = 'Select a carried magazine with a positive current ammunition count. The action rechecks its possession. Each guarded RemoveBullet event creates one declared AmmoType item, adds it to inventory and decrements the magazine count. Completion requires an empty magazine. Running interrupts while walking does not; already removed rounds remain and stopping does not roll back the count. Native ammunition creation and animation delivery remain separate.'

MAGAZINE_ITEMS = {'Base.' + name for name in ('9mmClip', '45Clip', '44Clip', '223Clip', '308Clip', '556Clip', 'M14Clip')}

WEAPON_ATTACHMENT = 'The menu requires a compatible MountOn weapon with the declared slot empty and an unbroken recursively found screwdriver. It transfers weapon and part, equips the screwdriver in the primary hand and part in the secondary hand. The action rechecks a nonrecursive unbroken Screwdriver-tagged item, the empty slot and possession of the part; it does not recheck weapon possession or MountOn compatibility. Walking or running interrupts. Completion calls attachWeaponPart, removes the part from inventory and clears the secondary hand. This does not establish weapon-performance changes.'

WEAPON_PART_REMOVAL = 'Select the installed part with an unbroken recursively found screwdriver; the menu transfers the weapon and equips the screwdriver. The action requires a nonrecursive unbroken Screwdriver-tagged item, possession of the weapon and the identical part still installed in its slot. Walking or running interrupts. Completion calls detachWeaponPart, adds that same part to inventory and refreshes equipped-hand models. Native part-stat recalculation remains separate.'

MAP_READING = 'Opening transfers the map to inventory when required; it must remain there or the window closes. The viewer supports panning, zooming and resetting the view. Its runtime map ID selects the initialization callback; missing initialization is reported without preventing the window from opening. Opening does not establish the accuracy of displayed contents.'

MAKEUP_USE = 'Select a cosmetic supported by the makeup type and confirm Apply. Opening the menu requires an inventory mirror, a nearby unobstructed world mirror, being in a vehicle, or available foundation makeup. Previewing alone does not commit the cosmetic replacement.'

ALARM_SETTING = 'The selected clock must satisfy the native digital-clock predicate. A clock outside the main inventory is transferred first unless it is a world item. Moving more than 0.1 on either position axis closes the dialog. Confirming OK writes the selected alarm-enabled state, hour and minute; actual ringing is a separate clock-engine behavior.'

ALARM_STOPPING = 'The digital-clock alarm must be ringing. With a player and alarm square, the clock must be in a player inventory or reachable in the world; a contained clock is transferred before the action. Running interrupts the action, and walking interrupts it for a world item. If the player or alarm square is missing, the callback instead calls stopRinging immediately; the timed action has no additional validity guard.'

ROPE_MAKING = 'The sheet-rope recipe must accept this fabric or named sheet and satisfy crafting eligibility; driving prevents crafting. The registered fabric must permit sheet rope, and the item is supplied as material rather than as a retained tool.'

FIXING_ACTION = 'The selected fixing rule must provide the required repair items, which are transferred into inventory. An item matching the selected fixer must remain there; the repair target must also remain there unless it is an installed vehicle part. Walking or running interrupts repair. Repair outcome and material consumption depend on the fixing engine.'

STAGE_ACTION = 'For multistage construction, the start check requires the learned recipe when specified, unbroken kept tools, and sufficient material counts or drainable uses in inventory or nearby ground supplies. The caller prepares up to two kept tools for the hands. Walking or running interrupts building. Normal completion performs the stage then consumes its listed materials or uses; construction cheat mode bypasses consumption.'

SOWING = 'Reach an existing unseeded plowed furrow with the required number of the configured loose seeds. The menu obtains that configured count recursively and transfers the selected list. The action checks possession of each listed seed and the plant world object, but not that the list still has the configured length or that the furrow remains unseeded. Walking/running interrupts; duration is 40 or one when instant, and farming cheat/instant mode bypasses walking. Completion removes the configured number from the list before sending coordinates/type to the server, which only accepts a still-plowed furrow. Client seed consumption is not atomic with server planting and does not guarantee growth or harvest.'

SEED_EXTRACTION = 'Open the packet first and use its resulting loose seeds for sowing; the unopened packet is not the item consumed by the sowing action.'

SOW_COUNTS = {n: f'The configured crop requires {n} loose seeds per furrow.' for n in (4, 6, 9, 12)}

ACTIVATION = 'Select a single activatable item held in a hand or attached to the character. If the menu recognizes it as Drainable, usedDelta must be positive.'

MAP_ANNOTATION = 'Use the character map editor with a matching writing implement in inventory. Choose an available implement color and a symbol or note position; adding text requires nonempty trimmed text and OK. Editing or moving existing annotations additionally requires an eraser.'

MAP_ERASURE = 'Use the character map editor with an eraser in inventory and select an existing note or symbol for removal. Editing or moving annotations additionally requires a compatible writing implement.'

NOTE_IMPLEMENT = 'When opening a writable note, a matching writing implement must be in inventory and another user must not own the note lock. Unlock an owned editing lock before changing pages or title; confirm with OK to save them. The implement check is at menu entry, not continuous consumption or durability validation.'

BATTERY_INSERTION = 'The compatible device must have zero remaining charge and a battery must be supplied to an eligible insertion recipe; crafting is unavailable while driving. The resulting device receives the selected battery remaining charge, which need not be full or positive. This recipe permits walking.'

ELECTRONIC_SALVAGE = 'An eligible dismantling recipe requires the matching device and a compatible Screwdriver-tagged tool. The device must not be a favorite unless it itself has the Screwdriver tag; crafting is unavailable while driving. Dismantling transforms the supplied device and yields the recipe parts, with extra battery recovery depending on the device callback and remaining charge or random outcome.'

SCRAP_RECOVERY = 'The selected dismantling recipe produces electronic scrap as its declared result or an explicit unconditional callback addition; no fixed quantity or extra battery recovery is implied.'

CAMP_FUEL_USE = 'Use the campfire menu outside a vehicle with a reachable existing campfire and a registered fuel item. At selection the item must not be a favorite, clothing must be unequipped with a fabric type, and a container must be empty. Transfer it to inventory and keep it there until the action completes; walking or running interrupts. Completion uses a drainable once or removes an ordinary item, then adds its registered fuel amount if the server campfire still exists.'

CAMP_TINDER_USE = 'Use the campfire menu outside a vehicle with a reachable unlit campfire, registered tinder and a matching fire-starting item. At selection tinder must not be a favorite, clothing must be unequipped with a fabric type, and a container must be empty. Both items must remain in inventory; walking or running interrupts. Completion removes the tinder and uses the starting item once. The server adds the tinder fuel and lights the still-existing campfire if it is unlit and has positive fuel.'

CARPENTRY_MATERIAL = 'For the selected active carpentry-menu object, its menu material/skill requirements and any required unbroken hammer must hold. Inventory and nearby-ground supplies count toward the object requirements; container materials must be empty. The object-specific placement checks and reachable same-level build action must hold. Normal creation consumes the declared materials; cheat mode bypasses consumption. Double-door consumption occurs only when creating its missing first part.'

UMBRELLA_CHANGE = 'The recipe must accept the matching open or closed umbrella and satisfy crafting eligibility; crafting is unavailable while driving. The form-change callback copies the supplied umbrella condition. Its hand placement depends on the supplied prior-hand flags; opening alone does not establish protection from rain.'

READ_PROGRESS = 'For a non-writable book with a positive page count, the native reading action records page progress per character; insufficient training level or illiteracy can reset progress, and a completed skill book resets its item-local page counter.'

READ_MAXIMUM = 'The book maximum corresponds to full reading progress; a multiplier is applied only when it exceeds the current multiplier, within the supported skill levels.'

READ_MOOD = 'During non-skill reading, when this mood value exceeds its value at reading start, the action restores that starting value. This does not establish the separate mood change when reading finishes.'

READ_SELECTION = 'Select only non-writable literature. The menu handles the first actual item, rejects illiteracy or insufficient training level, and disables reading while asleep. A container is required before transfer and queuing. Walking or running interrupts. For a driver, action validity returns whether the engine is off or speed is zero; otherwise it checks inventory and a positive incomplete-or-complete page count or a negative page count. Reading duration uses pages (five when nonpositive), day length, reader traits and server minutes per page. Nonempty taught-recipe lists mark the full type as read on completion; this marker is distinct from native recipe learning.'

BACK_CONTAINER = 'Select an unworn InventoryContainer whose canBeEquipped getter is Back. Transfer it to inventory and keep it there during the action; walking or running interrupts. Already-equipped items finish immediately. Completion removes the container from the hands, sets it as the worn Back item and refreshes backpack and clothing displays. Existing back equipment is shown as a replacement in the menu; native worn-slot replacement and load reduction are separate from this local dispatch.'

PLUMBING = 'Use an unbroken recursively found PipeWrench for an eligible indoor world object. One selector requires canBeWaterPiped and a found external water source; the waterPiped-sprite selector additionally excludes already external-fed objects and allows either a found source indoors or a room/pre-shutoff/canBeWaterPiped alternative. The callback equips the wrench and queues the action without its own path-to-object step. Continued validity checks only that the wrench is equipped; walking or running interrupts. Completion marks construction and sends the object coordinates/index. The server checks square/index, clears canBeWaterPiped and enables external-water use without repeating the client source or tool checks. Actual water delivery, source lookup and purification are not established by this flag change.'

WEIGHT_EXERCISE = 'Select the registered exercise with the exact weight recursively present in inventory. The UI disallows excessive endurance or heavy-load moodles, sitting on the ground, movement, climbing and being in a vehicle. It equips the barbell in both hands or the dumbbell initially in the primary hand, clears the other hand for dumbbells and queues removal of worn containers. The action waits for idle, starts only within the endurance threshold and remains valid outside a vehicle; it does not continually recheck the weight. Movement, endurance and elapsed chosen game time end the exercise, while aiming/climbing stop it. Each animation loop calls native Fitness.exerciseRepeat; dumbbell exercises switch hands using their counter. No direct XP, strength gain or stiffness magnitude is calculated here.'

CARRYING = 'The container must be transferable into the character inventory, with destination room and admission, source removal, access and multiplayer permissions satisfied; its contents remain with the same container item.'

WATER_STORAGE = 'Use a reachable water source in the same building context with water remaining and an unbroken compatible inventory container; an existing drainable water form must have filling space. Transfer the container and keep it in a container while water remains. An empty form is replaced when filling starts; stored amount increases with action progress and available water/capacity. Walking/running can leave a partial fill. Tainted source water taints the result even on interruption; filling does not clear existing taint or guarantee a full container.'

DISINFECTION = 'Select an injured, stitched or splinted but unbandaged body part in the Health panel using a positive-AlcoholPower item. Transfer the disinfectant to doctor inventory and keep it there. Running interrupts; walking interrupts below the groin. A different patient changing position invalidates treatment if driving or outside a vehicle; self-treatment and vehicle passengers have the stated movement exceptions.'

DIRTY_BANDAGING = 'Apply this bandaging material to an eligible body part from the Health panel while keeping the material in inventory and the patient within treatment reach. This is the application branch, not bandage removal; the material is removed when applied. A Dirty type-name match does not by itself establish the separate infected-item flag.'

SPLINTING = 'The Health menu excludes head/torso and requires an injured fractured part without stitches or a current splint. Use a finished Splint, or exact RippedSheets with Plank, TreeBranch or WoodenStick; no other fabric is selected. A queued HealthPanelAction rechecks injury and presence of a complete material option. The drag/drop handler has an inverted injury test, not an additional successful route under unchanged state. Materials are transferred first. The timed action rechecks patient movement and both materials only for the sheet-plus-support form; the finished-splint form has no continuing inventory check. Walking/running interrupts. Completion sets splint factor to (Doctor level + 1)/2, grants fifteen Doctor XP only if the body part allows it, consumes the support and any sheet, and records support FullType. Non-None access fixes Doctor level ten; instant timing does not itself do so. Native fracture healing remains separate.'

SPLINT_REMOVAL = 'Select an applied splint with positive splint factor through the Health panel. The queued handler rechecks that factor, while the removal action checks patient movement but not continuing splint state; walking/running interrupts. If a support FullType is recorded, create that item and additionally Base.RippedSheets unless the recorded type is exactly Base.Splint. Clear splinted state with factor zero. This does not preserve original item condition or establish native fracture recovery.'

STITCHING = 'A deep, unbandaged wound without glass is required, using a suture needle or a compatible needle with thread; the consumed suture/thread item remains in inventory and the patient stays within treatment reach.'

GLASS_REMOVAL = 'Select an injured, unbandaged body part containing glass, with the tool available at selection and the patient remaining within treatment reach; the menu also provides a separate bare-hand route.'

BULLET_REMOVAL = 'Select an injured, unbandaged body part containing a bullet, with a compatible tool available at selection and the patient remaining within treatment reach.'

POULTICE_USE = 'Select an injured, unbandaged body part with no plantain, comfrey or garlic poultice factor already applied; the poultice remains in inventory until application and is consumed, and the patient remains within treatment reach.'

ROD_FISHING = 'Select an unbroken rod and registered lure from inventory in the water fishing menu, in the nonspear branch. The UI must find nearby water at an allowed player level. Equip the rod in the primary hand and lure in the secondary hand and keep them there; walking, running or a different queued action interrupts. Fish availability, lure type, skill, time, season, random selection and line breakage affect the result; a fish catch is not guaranteed.'

RADIO_CRAFTING = 'Use the learned makeshift radio recipe with its declared components, a compatible screwdriver, Electricity skill of at least one and no broken items; RecipeManager eligibility must hold and the character must not be driving. The screwdriver is a kept tool. The RadioCraft callback only configures a result with device data, with skill-dependent randomized properties and no installed battery or stored power; component use does not promise a powered working radio.'

FOOD_TRAP_BAIT = 'At a placed unbaited trap with no captured animal, select uncooked Food from top-level inventory with no extra ingredients and no Drink custom menu. Its current HungerChange must be at most -0.05, except the exact Worm type. Names are deduplicated. Reach the trap; the action rechecks the trap object only, not bait possession or eligibility. Completion scales food values using the actual -0.05/HungChange formula, calls Use below the remaining-hunger threshold, and sends exact type, age and consumed fraction. The server records that bait on the trap. Animal acceptance, freshness and catch rolls are separate; supplying bait does not guarantee any animal or catch.'

FOOD_TRANSFER = 'When the inventory transfer consumer completes a Food item transfer, it calls setChef with the transferring character full name. This records chef attribution only; it does not itself award cooking XP or change food ingredients or nutrition.'

FOOD_NAMING = 'The selected Food must be a result recognized by an evolved recipe and have at least three extra ingredients. Confirm a nonempty name whose internal-text length is at most 28; the callback sets the name and custom-name flag and refreshes inventories. It does not trim whitespace, require an added transfer/continued-possession check, or change the food type, ingredients or nutrition.'

CANNED_COOKED = 'Only when Food.update dispatches this exact CannedFood_OnCooked callback: save Age divided by the previous OffAgeMax, set OffAge to 60 and OffAgeMax to 90, then set Age to 90 times the saved fraction. This preserves relative age rather than resetting to fresh zero. The callback does not check a zero denominator; native cooking dispatch and food-aging behavior remain separate.'

FISH_CREATED = 'Only when Fishing.OnCreateFish is invoked with this registered exact fish FullType: select a size branch using the actual random roll (Big at <=20, Medium at <=30, otherwise Small), then use its registered min/max size and weight divisor. Nutrition is scaled by new weight relative to prior actual weight; world scale, negative base/current hunger, actual weight and custom-weight flag are set. The commented fish renaming is not active. Native factory callback dispatch, random values and getter/setter state are separate; no fixed size, nutrition or catch outcome is promised.'

VEHICLE_SEATING = 'The compatible installed seat must be unoccupied and reachable through the actual seat/door/path checks. The seat UI can queue clearing stored items into other installed nonoccupied seats with room, enter through the selected or reachable alternate door, or switch seats. Driver switching/exiting first queues braking when speed exceeds 0.8; passengers cannot exit a moving vehicle. Enter starts native enter and completes on the animation signal; cancelling enter calls exit. Switching checks current/target occupancy and original seat, then calls switchSeat at completion. Exit requires a stopped vehicle and calls native exit at completion; cancelling leaves the occupant seated. Native installed-seat binding, passenger positions, reachability and animation completion remain dependencies; no comfort, rest recovery or engine start is implied.'

VEHICLE_STORAGE = 'This exact inventory form must be bound to the compatible installed vehicle part and its item container. The inventory page requires native canAccessContainer before exposing that container; transfers retain actual capacity and item admission/removal checks. Closed-trunk access requires being outside in its area and an open or absent installed trunk/rear door; open truck-bed/trailer access only requires being outside in its area. Glove-box access from inside uses front seat 0 or 1, or from outside its area with the front-right door open when present. Seat storage needs an installed, unoccupied seat, reachable through canSwitchSeat from the same vehicle or the actual exterior door/area rules. Loose parts are not portable containers; native part-type mapping, capacity and container access remain conditions.'

VEHICLE_FUEL = 'The exact tank form must be bound to the compatible GasTank part with Gasoline content. A stopped engine, tank space or available fuel, appropriate petrol/empty-petrol container and approach to the tank area govern the menus. Can addition and siphoning change container fractions and send tank-amount commands progressively; their action isValid returns true rather than rechecking the commented area condition. Empty siphon containers are replaced at start using PetrolSource or PetrolCan fallback. Pump filling needs a nearby fueled pump with menu electricity conditions and rechecks the work area, then reduces pump supply progressively. Cancellation can retain partial transfer. The server resolves vehicle/part then sets and transmits the requested amount. Native binding, capacity, factory results and non-atomic inventory/server delivery remain separate.'

VEHICLE_FUEL_ENGINE = 'An installed GasTank item with content rounded to three decimal places above zero passes the tank-specific engine check; this is not sufficient by itself to start the engine. With positive elapsed time, positive fuel and a running engine, its update calculates fuel use from engine speed, vehicle parameters and sandbox consumption, and adds a random loss for tank condition below 70. The amount setter owns clamping; this does not promise a fixed driving range or fuel-use rate.'

CONTENTS_EMPTYING = 'Select one nonwater, nonliterature item whose exact replacement chain reaches a water-storing form. Transfer it to inventory and keep it there. On completion the action follows the declared chain, substitutes the terminal type into ReplaceOnUse or drainable ReplaceOnDeplete (setting UseDelta to one in that branch), then calls Use once. Walking/running does not interrupt this action; cancellation before completion does not perform the replacement. The native final item/Use result is separate from the interpreted chain, and intermediate forms are skipped rather than received.'

WATER_EMPTYING = 'Select one water-source item, transfer it to inventory and keep it there. The action progressively decreases UsedDelta from its starting amount, including before cancellation, and on completion sets it to zero then calls Use. Walking/running does not interrupt. Empty-form replacement and resulting inventory identity depend on native Use; pouring out does not purify water, transfer it into another container or create a recoverable world water item.'

EXTINGUISH_CONDITIONS = 'A held or directly carried eligible supply needs one drainable use per affected square for the extinguisher or dirt/gravel/sand bag, or ten for a water source. The cursor requires a visible target with nonpermanent fire or a burning character in its selected 2x2 area, with mouse adjacency walking. The action requires the supply in inventory and enough uses, stops on walking/running, then processes visible squares: burning characters receive StopBurning/sendStopBurning, and burning squares receive transmitStopFire/stopFire. Uses are spent only on affected squares and processing stops when insufficient uses remain. Native extinguishing and use/replacement outcomes are not guaranteed by issuing these calls.'

GROUND_FILL = 'An unbroken TakeDirt-tagged tool and an empty HoldDirt container or matching not-full dirt/gravel/sand bag enable the active ground menu. The cursor excludes shovelled ground and client farm plants and matches actual ground sprites. It prefers a matching bag with room for another use, otherwise an empty HoldDirt container; adjacency, transfer and tool equipment precede the action. The action rechecks inventory, sprite and container emptiness/capacity, stops on walk/run, sends shovelGround, then replaces HoldDirt with the specified bag at one use or adds one use without exceeding full. A worm is a separate random return. Server terrain restoration/change and local item creation are separate operations, without an atomic-success guarantee.'

GROUND_POUR = 'Select the exact dirt/gravel/sand bag through the active ground menu, reach the floor and transfer it if needed. Placement rejects farm plants, water and an already poured floor of the same type, and requires a matching bag in recursive inventory and an existing floor. It adds the selected ground floor, preserves prior sprite names for later shovelling, marks the poured type and calls Use once; another same-type bag is selected if this one leaves inventory. No extra remaining-use check, shovel requirement, farming yield or native floor/use outcome is inferred.'

SMITHING_PARTS = 'The door-knob and hinge recipes specify IronIngot=15 as material, keep BallPeenHammer and Tongs, NearItem:Anvil, Blacksmith level 3 and a learned recipe. ISCraftAction requires native recipe eligibility and not driving before PerformMakeItem. The declared Blacksmith15 callback adds 15 Blacksmith XP when invoked; its native dispatch, ingredient quantities, nearby-object matching and resulting item delivery are not established by the Lua callback alone.'

MATERIAL_ASSEMBLY = 'Supply the exact materials and any kept cutting tool required by the selected supported recipe. A fishing-gear recipe must be learned where its declaration requires learning. RecipeManager must accept the selected recipe and participants, and the character must not be driving. A listed result is what the recipe produces, not a use of that result as a material; assembly does not establish the resulting tool or medical effect.'

RADIO_DISMANTLING = 'Supply a compatible unbroken radio or television and the kept screwdriver required by its dismantling recipe. The electronics test excludes favorite items except a screwdriver-tagged participant, RecipeManager eligibility must hold and the character must not be driving. The recipe declares electronic scrap; extra components depend on random and skill branches. Battery or headphone retrieval is delegated to device data and is not a guaranteed recovered item.'

FERTILIZING = 'Use the farming fertilize menu with fertilizer or compost in inventory and a reachable plant. Compost is selected first when present; otherwise fertilizer is selected. The timed action requires the plant object to remain, stops on walking or running, sends the plant coordinates to the farming server, uses the selected item once and calls inventory Remove with the FertilizerEmpty string. That removal is not proof an empty package was created. The server effect requires the plant still to exist, be alive and not be an empty plowed plot; the action does not continuously recheck item inventory or remaining uses, and client consumption is not atomic with server treatment.'

FERTILIZER_GROWTH = 'On the server, the living non-plowed plant has fewer than four previous fertilizer applications. Its fertilizer counter increases and the next-growth schedule is moved earlier with a lower bound of one; an earlier schedule is conditional on the previous schedule being above that bound.'

FERTILIZER_ROT = 'On the server, the living non-plowed plant already has at least four fertilizer applications. Another application calls rottenThis and sets the plant state to rotten.'

REMOTE_LINK = 'Select the controller or remote-capable weapon in the inventory menu, with a compatible counterpart in the top-level inventory and the branch-specific unassigned or differing IDs. Linking creates a controller ID when unassigned and copies it to the device. Linking does not itself place or trigger the device.'

REMOTE_RESET = 'The selected controller or remote-capable weapon has an assigned remote ID. Reset sets only that selected item ID to unassigned; it does not reset every other linked item.'

REMOTE_TRIGGER = 'The selected remote controller has an assigned ID. Trigger sends that ID and its range to the object command receiver, which calls IsoTrap.triggerRemote. Whether a matching trap is present, reachable in range or produces an effect remains a native trap outcome.'

TRAP_PLACEMENT = 'Select the registered trap from top-level inventory in the world trap menu. Placement requires that item still in inventory and an empty solid-floor square without solid obstruction, a tree, another trap or the checked adjacent hoppable/window obstruction. The ordinary build action must reach and complete placement. Placement initializes the exact trap type and removes the inventory trap, clearing either hand that held it.'

TRAP_CATCH = 'Use the placed, undestroyed trap with fresh bait accepted by the target animal, in that animal allowed time and zone. Bait selection requires an empty unbaited trap and uncooked food without extra ingredients or a drink menu, with enough hunger value or the worm exception. The hourly catch check skips loaded trap squares; unloaded-square catches still depend on trapping skill, trap/bait and zone rolls and final animal selection. A catch is not guaranteed.'

OPENED_FOOD = 'First open the package through its supported opening recipe. Only the resulting food contents, not the unopened package, serve as the ingredient in an evolved recipe that accepts that exact resulting form.'

FUNCTIONS = {
    'supply_trap_bait': ('trap bait supply', '조건에 맞는 음식은 설치된 덫의 미끼로 넣을 수 있다.', 'Eligible food can be supplied as bait to a placed trap.'),
    'rename_prepared_food': ('prepared-food naming', '조건에 맞는 완성 음식에 이름을 붙일 수 있다.', 'An eligible prepared food can be given a custom name.'),
    'use_vehicle_seat': ('vehicle seating', '대응하는 장착 좌석에 승차하거나 좌석을 이동하고 하차할 수 있다.', 'The compatible installed seat can be entered, switched to or exited.'),
    'store_vehicle_items': ('installed vehicle storage', '차량의 대응 수납 부품으로 연결된 상태에서 물품 보관에 쓰인다.', 'It serves as item storage when bound to the corresponding installed vehicle part.'),
    'store_vehicle_fuel': ('installed fuel storage', '차량의 대응 연료 탱크로 연결된 상태에서 연료를 담는다.', 'It holds fuel when bound to the compatible vehicle fuel-tank part.'),
    'transfer_vehicle_fuel': ('vehicle fuel transfer', '장착된 연료 탱크에 주유하거나 연료를 빼낼 수 있다.', 'Fuel can be added to or siphoned from the installed tank.'),
    'supply_vehicle_engine_fuel': ('engine fuel supply', '장착된 탱크의 연료가 엔진 연료 확인과 소비 처리에 사용된다.', 'Fuel in the installed tank participates in engine fuel checks and consumption.'),
    'install_vehicle_storage_part': ('storage-part installation', '대응 차량에 수납·연료 부품을 장착하는 작업을 할 수 있다.', 'It can be used in installation of the compatible vehicle storage or fuel part.'),
    'remove_vehicle_storage_part': ('storage-part removal', '장착된 수납·연료 부품을 탈거하는 작업을 할 수 있다.', 'The installed storage or fuel part can undergo removal.'),
    'dump_contents': ('contents disposal', '내용물을 버리는 작업을 할 수 있다.', 'Its contents can be discarded.'),
    'dump_water': ('water disposal', '담긴 물을 지면에 버릴 수 있다.', 'Its water can be poured onto the ground.'),
    'extinguish_fire': ('fire extinguishing', '불타는 지면이나 캐릭터에 불 끄기 작업을 할 수 있다.', 'It can be used to attempt to extinguish burning ground or characters.'),
    'fill_ground_bag': ('ground collection', '대응하는 지면에서 흙·자갈·모래를 포대에 담을 수 있다.', 'It can receive dirt, gravel or sand from the matching ground.'),
    'pour_ground_cover': ('ground pouring', '포대 내용물을 지면에 부을 수 있다.', 'Its contents can be poured onto a floor.'),
    'prepare_opened_food_ingredient': ('food_preparation', '개봉해 꺼낸 내용물을 받아들이는 요리의 재료로 쓸 수 있다.', 'Its opened contents can be used as an ingredient in a recipe that accepts that food.'),
    'place_animal_trap': ('animal_trapping', '동물 덫을 설치할 수 있다.', 'It can be placed as an animal trap.'),
    'catch_trap_animal': ('animal_trapping', '미끼를 넣어 대응하는 동물을 잡는 덫으로 쓸 수 있다.', 'With bait, it can be used as a trap for compatible animals.'),
    'link_remote_device': ('remote_linking', '조종기와 대응 장치의 원격 제어 ID를 연결할 수 있다.', 'It can link the remote-control IDs of a controller and compatible device.'),
    'reset_remote_id': ('remote_linking', '선택한 물품의 원격 제어 ID를 해제할 수 있다.', 'The selected item remote-control ID can be reset.'),
    'send_remote_trigger': ('remote_trigger', '연결 ID와 범위로 원격 작동 요청을 보낼 수 있다.', 'It can send a remote-trigger request with its linked ID and range.'),
    'apply_fertilizer': ('fertilizing', '작물에 비료를 주는 데 쓸 수 있다.', 'It can be used to fertilize a crop.'),
    'fish_with_rod': ('rod_fishing', '미끼와 함께 낚싯대로 물고기를 낚는 데 쓸 수 있다.', 'It can be used with a lure to fish with a rod.'),
    'bait_rod_fishing': ('fishing_bait', '낚싯대 낚시의 미끼로 쓸 수 있다.', 'It can be used as bait for rod fishing.'),
    'supply_campfire_fuel': ('campfire_fuel', '모닥불에 연료를 보충하는 데 쓸 수 있다.', 'It can be used to add fuel to a campfire.'),
    'provide_campfire_tinder': ('campfire_lighting', '발화 도구와 함께 모닥불을 붙이는 불쏘시개로 쓸 수 있다.', 'It can serve as tinder for lighting a campfire with a fire-starting item.'),
    'light_campfire': ('campfire_lighting', '불쏘시개와 함께 모닥불을 붙이는 데 쓸 수 있다.', 'It can be used with tinder to light a campfire.'),
    'dismantle_electronics': ('electronic_salvage', '분해해 전자 부품을 회수할 수 있다.', 'It can be dismantled to recover electronic parts.'),
    'accept_battery_charge': ('battery_insertion', '건전지를 넣어 그 건전지에 남은 충전량을 공급받을 수 있다.', 'A battery can be inserted to supply its remaining charge to the device.'),
    'write_note_pages': ('note_writing', '메모의 페이지와 제목을 작성하거나 수정하는 필기구로 쓸 수 있다.', 'It can serve as a writing implement for writing or editing note pages and titles.'),
    'annotate_map': ('map_annotations', '지도에 기호나 글로 주석을 남길 수 있다.', 'It can be used to add symbols or written notes to a map.'),
    'erase_map_annotations': ('map_annotations', '지도의 글이나 기호 주석을 지울 수 있다.', 'It can be used to remove written or symbol annotations from a map.'),
    'unfold_umbrella': ('umbrella', '우산을 펼칠 수 있다.', 'The umbrella can be opened.'),
    'fold_umbrella': ('umbrella', '우산을 접을 수 있다.', 'The umbrella can be folded.'),
    'toggle_activation': ('activation', '활성 상태를 켜거나 끌 수 있다.', 'Its activated state can be switched on or off.'),
    'sow_seeds': ('sowing', '경작한 고랑에 씨앗을 심을 수 있다.', 'The seeds can be sown in a plowed furrow.'),
    'sow_extracted_seeds': ('sowing packet contents', '봉지에서 꺼낸 씨앗을 경작한 고랑에 심을 수 있다.', 'The loose seeds taken from the packet can be sown in a plowed furrow.'),
    'melee_attack': ('melee attacks', '근접 공격에 사용할 수 있다.', 'It can be used for melee attacks.'),
    'set_alarm': ('alarm settings', '알람의 켜짐 상태와 시각을 설정할 수 있다.', 'Its alarm can be enabled or disabled and its hour and minute can be set.'),
    'stop_alarm': ('alarm ringing', '울리는 알람을 끌 수 있다.', 'Its ringing alarm can be stopped.'),
    'apply_makeup': ('makeup', '호환되는 화장을 선택해 적용할 수 있다.', 'It can be used to select and apply compatible makeup.'),
    'apply_eye_makeup': ('eye makeup', '눈가에 호환되는 화장을 적용할 수 있다.', 'It can be used to apply compatible makeup around the eyes.'),
    'apply_lip_makeup': ('lip makeup', '입술에 호환되는 화장을 적용할 수 있다.', 'It can be used to apply compatible makeup to the lips.'),
    'remove_weapon_part': ('weapon attachments', '총기에 장착된 부품을 떼어 회수할 수 있다.', 'An installed weapon part can be detached and recovered.'),
    'attach_weapon_part': ('weapon attachments', '호환되는 총기에 개조 부품으로 장착할 수 있다.', 'It can be attached as an upgrade part to a compatible firearm.'),
    'smoke_cigarette': ('smoking', '담배를 피울 수 있다.', 'The cigarette can be smoked.'),
    'take_food_medicine': ('medicine', '복용할 수 있다.', 'It can be taken as medicine.'),
    'place_moveable_furniture': ('furniture', '가구의 배치 조건을 충족하면 공간에 놓을 수 있다.', 'It can be placed as furniture when its placement requirements are met.'),
    'remove_placed_furniture': ('furniture removal', '설치된 가구의 형태를 떼어낼 수 있다.', 'Its placed furniture form can be removed.'),
    'paint_supported_surface': ('surface painting', '도색 가능한 표면을 칠할 때 쓸 수 있다.', 'It can be used to paint a compatible surface.'),
    'paint_wall_sign': ('wall signs', '벽에 표식을 그릴 때 쓸 수 있다.', 'It can be used to paint signs on a wall.'),
    'unpack_produce': ('produce', '자루를 열어 담긴 농산물을 꺼낼 수 있다.', 'The sack can be opened to take out the produce.'),
    'unpack_seeds': ('seeds', '봉지를 열어 씨앗을 꺼낼 수 있다.', 'The packet can be opened to take out seeds.'),
    'unpack_ammunition': ('ammunition', '상자를 열어 탄약을 꺼낼 수 있다.', 'The box can be opened to take out ammunition.'),
    'unpack_box_contents': ('boxed supplies', '상자를 열어 담긴 물품을 꺼낼 수 있다.', 'The box can be opened to take out its contents.'),
    'unpack_eggs': ('eggs', '포장을 열어 달걀을 꺼낼 수 있다.', 'The carton can be opened to take out the eggs.'),
    'unpack_canned_food': ('canned food', '통조림을 열어 내용물을 꺼낼 수 있다.', 'It can be used to open canned food and take out the contents.'),
    'unpack_jarred_food': ('jarred food', '병을 열어 담긴 식품을 꺼낼 수 있다.', 'The jar can be opened to take out its food contents.'),
    'fire_ammunition': ('firearms', '탄약을 장전해 사격에 사용할 수 있다.', 'It can be loaded with ammunition and used for shooting.'),
    'chop_tree': ('forestry', '나무를 찍어 베는 데 쓸 수 있다.', 'It can be used to chop down trees.'),
    'consume_edible_food': ('consumption', '먹을 수 있다.', 'It can be eaten.'),
    'drink_food_contents': ('drinking', '마실 수 있다.', 'It can be drunk.'),
    'wear_configured_clothing': ('wearing', '몸에 착용할 수 있다.', 'It can be worn on the body.'),
    'load_matching_ammunition': ('ammunition', '해당 탄종을 받는 총기나 탄창에 장전할 수 있다.', 'It can be loaded into a firearm or magazine that accepts this ammunition type.'),
    'fill_magazine': ('magazines', '탄창에 규격이 맞는 탄약을 넣을 수 있다.', 'The magazine can be filled with matching ammunition.'),
    'empty_magazine': ('magazines', '탄창에 든 탄약을 꺼낼 수 있다.', 'Ammunition can be removed from the magazine.'),
    'insert_matching_magazine': ('magazines', '호환되는 총기에 탄창을 끼울 수 있다.', 'The magazine can be inserted into a compatible firearm.'),
    'view_item_map': ('maps', '지도를 열어 내용을 볼 수 있다.', 'The map can be opened and viewed.'),
    'carry_stored_items': ('storage', '담긴 물건과 함께 용기를 소지하고 운반할 수 있다.', 'The container can be carried with its stored items.'),
    'store_water': ('water storage', '물을 담아 보관할 수 있다.', 'It can be filled with water for storage.'),
    'carry_water': ('water storage', '담은 물을 용기에 넣어 운반할 수 있다.', 'The stored water can be carried in the container.'),
    'disinfect_wound': ('wound care', '상처를 소독하는 데 쓸 수 있다.', 'It can be used to disinfect a wound.'),
    'apply_splint': ('fracture care', '골절 부위에 부목을 대는 데 쓸 수 있다.', 'It can be used to apply a splint to a fracture.'),
    'stitch_wound': ('wound care', '깊은 상처를 봉합하는 데 쓸 수 있다.', 'It can be used to stitch a deep wound.'),
    'remove_embedded_glass': ('wound care', '상처에 박힌 유리를 제거할 때 쓸 수 있다.', 'It can be used to remove glass embedded in a wound.'),
    'remove_embedded_bullet': ('wound care', '상처에 박힌 총알을 제거할 때 쓸 수 있다.', 'It can be used to remove a bullet embedded in a wound.'),
    'apply_poultice': ('wound care', '다친 부위에 약초 찜질제를 바를 수 있다.', 'It can be applied as an herbal poultice to an injured body part.'),
}

QUALIFIERS = {
    PLUMBING: ('파손되지 않은 파이프 렌치를 소지품에서 찾아 장착하고 배관 가능한 실내 물체에 사용한다. 선택 조건은 외부 수원 발견 또는 수도 단절 전의 배관 가능 물체 경로를 구분한다. 동작은 별도 접근 이동을 예약하지 않고 렌치 착용 여부만 계속 검사하며 걷거나 달리면 중단된다. 서버는 좌표·물체 인덱스를 확인해 외부 수원 사용 표시를 켠다. 실제 급수·수원 연결·정수 효과를 확정하는 동작은 아니다.', PLUMBING),
    WEIGHT_EXERCISE: ('해당 바벨·덤벨을 소지하고 운동을 선택한다. 심한 지침·과적, 앉기·이동·등반·차량 탑승은 메뉴에서 제한한다. 바벨은 양손에, 덤벨은 처음에 주 손에 들며 착용 가방은 벗는다. 유휴 상태에서 시작하고 동작 중에는 차량 밖인지 검사하지만 운동기구 소지를 계속 검사하지 않는다. 이동·지침·선택한 시간 경과로 종료되며 덤벨은 반복 중 손을 바꾼다. 반복마다 엔진의 운동 처리를 호출하므로 경험치·근력·근육통 수치를 이 코드만으로 확정하지 않는다.', WEIGHT_EXERCISE),
    BACK_CONTAINER: ('등 착용 위치가 지정된 미착용 가방을 선택한다. 먼저 소지품으로 옮기고 계속 소지해야 하며 걷거나 달리면 중단된다. 완료하면 손에서 내려 등에 착용하고 가방 표시를 갱신한다. 기존 등 장비가 있으면 교체 대상으로 표시하며 실제 위치 교체·하중 감소 계산은 엔진 처리에 따른다.', 'Select an unworn container configured for the back. Transfer it to inventory and retain it; walking or running interrupts. Completion removes it from the hands, wears it on the back and refreshes bag displays. Existing back equipment is shown as a replacement; actual slot replacement and load reduction depend on native handling.'),
    READ_SELECTION: ('쓰기용이 아닌 읽을거리 중 첫 선택 항목을 읽는다. 문맹·기술 부족·수면 상태는 메뉴에서 제한되며 먼저 물품을 소지품으로 옮긴다. 걷거나 달리면 중단된다. 운전자는 엔진 정지 또는 속도 0 조건으로 동작 유효성을 검사하고, 그 밖에는 소지 여부와 쪽수 상태를 검사한다. 독서 시간은 쪽수·하루 길이·독서 특성·서버 설정에 따른다. 제조법 목록이 있는 책의 완독 기록과 실제 제조법 학습은 별개다.', 'Read the first selected non-writable literature item. The menu restricts illiteracy, insufficient skill and sleep, and transfers the item to inventory first. Walking or running interrupts. Driver validity uses engine-off or zero speed; otherwise possession and page state are checked. Duration depends on pages, day length, reader traits and server settings. A completion marker for recipe literature is distinct from actual recipe learning.'),
    FOOD_TRAP_BAIT: ('동물·미끼가 없는 설치된 덫에, 직접 소지한 익히지 않은 음식을 넣는다. 추가 재료·음료 메뉴가 없어야 하며 현재 허기 값이 -0.05 이하이거나 지렁이여야 한다. 이름이 같은 후보는 하나만 표시된다. 덫에 인접해야 하고 행동은 덫 물체만 다시 검사한다. 완료 시 식품 값을 일부 줄이고 남은 허기 기준에 따라 사용 처리를 한 뒤 종류·나이·소모 비율을 서버에 보낸다. 동물별 미끼 허용·신선도·포획 확률은 별개이며 포획을 보장하지 않는다.', 'Supply an unbaited placed trap with no captured animal using directly carried uncooked food without extra ingredients or a Drink menu. Current hunger change must be at most -0.05, except Worm; candidates are deduplicated by name. Reach the trap; action validity rechecks only the trap object. Completion reduces food values, conditionally calls Use and sends type, age and consumed fraction. Animal acceptance, freshness and catch rolls are separate and no catch is guaranteed.'),
    FOOD_TRANSFER: ('식품 옮기기가 완료되면 옮긴 캐릭터의 이름을 조리자 정보에 기록한다. 이 기록 자체가 조리 경험치를 지급하거나 재료·영양을 바꾸지는 않는다.', 'A completed food transfer records the transferring character name as chef attribution. This alone does not award cooking XP or change ingredients or nutrition.'),
    FOOD_NAMING: ('조리법의 결과로 인정되는 식품에 추가 재료가 셋 이상 있어야 한다. 비어 있지 않고 내부 텍스트 길이가 28 이하인 이름을 확인하면 이름과 사용자 지정 이름 표시를 바꾼다. 공백을 잘라내거나 별도 소지 조건을 추가하지 않으며 식품 종류·재료·영양은 바꾸지 않는다.', 'The food must be recognized as an evolved-recipe result with at least three extra ingredients. Confirm a nonempty name with internal-text length at most 28 to set its name/custom-name flag. Whitespace is not trimmed, no extra possession guard is added, and type, ingredients and nutrition are unchanged.'),
    CANNED_COOKED: ('해당 조리 콜백이 호출되면 기존 경과 나이를 이전 부패 기준으로 나눈 비율을 보존하고 신선도·부패 기준을 60·90으로 설정한 뒤 나이를 90×기존 비율로 바꾼다. 나이를 0으로 초기화하지 않는다. 콜백에는 0인 분모 검사가 없으며 조리 시점의 호출과 실제 식품 노화 처리는 별도다.', 'When the declared cooking callback runs, it preserves Age/old OffAgeMax, sets freshness/rot thresholds to 60/90 and sets age to 90 times that fraction. Age is not reset to zero. The callback has no zero-denominator guard; cooking dispatch and actual aging remain separate.'),
    FISH_CREATED: ('등록된 정확한 생선 종류의 생성 콜백이 호출될 때 무작위 크기 구간과 등록된 길이·무게 값을 사용해 영양·표시 크기·허기 값·실제 무게를 설정한다. 영양은 새 무게와 기존 실제 무게의 비율로 조정한다. 이름 변경 코드는 비활성이며 고정 크기·영양이나 포획 성공을 보장하지 않는다.', 'When the creation callback runs for the registered exact fish type, random size branches and registered length/weight values set nutrition, world scale, hunger values and actual weight. Nutrition scales by new versus prior actual weight. The name-changing code is inactive; no fixed size/nutrition or catch success is guaranteed.'),
    VEHICLE_SEATING: ('장착된 빈 좌석과 실제 문·경로·좌석 간 접근 조건이 필요하다. 물건이 있으면 여유 있는 다른 장착 좌석으로 옮기기를 시도한다. 운전자는 속도 0.8 초과에서 좌석 이동·하차 전 제동을 요청하고, 동승자는 움직이는 차에서 내릴 수 없다. 승차는 시작 때 적용되고 취소 시 나가며, 좌석 이동·하차는 애니메이션 후 완료 때 적용된다. 실제 좌석 연결·도달·애니메이션 완료는 별도 처리이며 휴식 회복·안락함·시동 성공을 보장하지 않는다.', 'Use an installed unoccupied seat with the actual door/path and seat-reachability conditions. Stored items may be moved to other installed seats with room. A driver queues braking above speed 0.8 before switching/exiting; passengers cannot exit a moving vehicle. Entry occurs at action start and is undone by cancellation; switching/exiting applies at animation completion. Native seat binding, reachability and animation completion remain separate, without implying rest recovery, comfort or engine-start success.'),
    VEHICLE_EXCHANGE_REQUIREMENTS['seat']: ('좌석 작업표는 주손에 보존하는 드라이버, 기초 차량 정비 제작법과 정비 1을 지정하며 탈거할 때 수납 공간이 비어 있어야 한다. 기술 값은 실제 판정·성공 및 손상 계산에 쓰이며 주석 처리된 강제 기술 제한을 다시 적용하지 않는다.', 'The seat work table specifies a kept primary-hand screwdriver, Basic Mechanics and Mechanics:1, with empty storage required for removal. Skill values feed the actual checks and success/damage calculation; the commented hard skill gate is not reinstated.'),
    VEHICLE_EXCHANGE_REQUIREMENTS['gastank']: ('탱크 작업표는 보조손 드라이버와 주손 렌치를 보존하며 기초 차량 정비 제작법과 정비 5를 지정한다. 탈거할 때 탱크가 비어 있어야 한다. 기술 값은 실제 판정·성공 및 손상 계산에 쓰이며 주석 처리된 강제 기술 제한을 다시 적용하지 않는다.', 'The tank work table keeps a secondary-hand screwdriver and primary-hand wrench, specifies Basic Mechanics and Mechanics:5, and requires an empty tank for removal. Skill values feed the actual checks and success/damage calculation; the commented hard skill gate is not reinstated.'),
    VEHICLE_STORAGE: ('대응 차량 부품과 수납 공간에 연결된 상태여야 하며 접근·용량·물품 허용 판정을 만족해야 한다. 닫힌 적재함은 차 밖의 작업 구역에서 트렁크·뒷문이 열렸거나 탈거돼 있어야 하고, 열린 적재함·트레일러는 차 밖의 해당 구역을 사용한다. 글로브박스는 같은 차량의 앞좌석 0·1 또는 앞오른쪽 문이 열려 있는 외부 구역에서 접근한다. 좌석은 장착됐고 비어 있어야 하며 차량 안에서 좌석 간 접근이 가능하거나 외부 문·구역 조건을 만족해야 한다. 분리된 부품 자체가 휴대용 가방이 되는 것은 아니다.', 'The item must be bound to the matching vehicle part/container and pass access, capacity and item admission checks. Closed-trunk access requires being outside in its area with the trunk/rear door open or uninstalled; open-bed/trailer access uses its exterior area. The glove box is accessible from front seat 0/1 of the same vehicle or its exterior area with the front-right door open when present. A seat must be installed and unoccupied, reachable through seat switching or its exterior door/area rules. A loose part is not a portable bag.'),
    VEHICLE_FUEL: ('대응하는 차량 연료 탱크에 연결돼야 한다. 메뉴는 엔진 정지, 연료나 빈 공간, 알맞은 연료 용기와 접근 조건을 사용한다. 용기 주유·회수는 진행 중 용기 양과 차량에 보낼 연료 양을 바꾸며 행동의 유효성 함수는 구역을 다시 검사하지 않는다. 빈 회수 용기는 시작 때 교체된다. 주유기는 가까운 연료·전력 조건과 행동 중 작업 구역 확인을 사용한다. 취소해도 일부 이동은 남을 수 있다. 서버는 차량·부품을 찾아 요청량을 설정하며 용기 생성·용량·서버와 소지품의 동시 반영은 별도 처리다.', 'The item must bind to the compatible fuel-tank part. Menus require a stopped engine, fuel or tank space, a suitable petrol container and approach. Can filling/siphoning changes container fractions and sends tank amounts during progress; action validity does not repeat the commented area check. Empty receivers are replaced at start. Pump filling requires nearby fuel/electricity conditions and checks the work area during the action. Cancellation may leave partial transfer. The server resolves vehicle/part and sets the requested amount; container creation, capacity and joint server/inventory delivery remain separate.'),
    VEHICLE_FUEL_ENGINE: ('장착된 탱크의 연료가 소수 셋째 자리 반올림 후 양수면 탱크의 엔진 검사를 통과하지만, 이것만으로 시동 성공이 보장되지는 않는다. 경과 시간이 양수이고 연료가 있는 운전 중 엔진은 차량·엔진·설정 값에 따라 연료를 소비하며 탱크 상태가 70 미만이면 추가 무작위 손실이 있을 수 있다. 고정 주행 거리나 일정 소비량을 보장하지 않는다.', 'An installed tank with fuel rounded to three decimal places above zero passes the tank-specific engine check, without guaranteeing engine start. With positive elapsed time and fuel while the engine runs, consumption uses vehicle/engine/settings values; tank condition below 70 can add random loss. No fixed driving range or consumption rate is guaranteed.'),
    CONTENTS_EMPTYING: ('물이나 책이 아닌 물품 하나를 선택하며 교체 경로가 물을 담을 수 있는 용기에 도달해야 한다. 물품을 소지품으로 옮겨 계속 소지한다. 완료 시 중간 교체 형태를 건너뛰고 최종 용기로 교체 경로를 설정한 뒤 한 번 사용한다. 걷거나 달려도 중단되지 않지만 완료 전 취소하면 이 교체는 수행되지 않는다. 실제 최종 물품 지급은 사용 처리에 달려 있다.', 'Select one nonwater, nonliterature item whose replacement chain reaches a water-storing form. Transfer it into inventory and keep it there. Completion skips intermediate forms, sets replacement to the terminal form and calls Use once. Walking/running does not interrupt, but cancellation before completion does not perform this replacement. Actual final-item delivery depends on Use.'),
    WATER_EMPTYING: ('물 용기 하나를 소지품으로 옮겨 계속 소지해야 한다. 진행에 따라 물이 줄어들어 중간에 취소해도 줄어든 양은 돌아오지 않으며, 완료하면 남은 양을 0으로 만들고 사용 처리를 한다. 걷거나 달려도 중단되지 않는다. 빈 용기 교체는 사용 처리에 달려 있으며 정수·다른 용기로 옮기기·회수 가능한 지면 물 생성은 아니다.', 'Transfer one water-source item into inventory and keep it there. Water decreases progressively and remains spent if cancelled; completion sets the amount to zero and calls Use. Walking/running does not interrupt. Empty-form replacement depends on Use; this does not purify water, transfer it into another container or create recoverable ground water.'),
    EXTINGUISH_CONDITIONS: ('소화기·흙·자갈·모래 포대는 영향을 주는 칸마다 사용량 1회, 물 용기는 10회가 필요하다. 손에 들었거나 직접 소지한 대상 중 선택하며, 보이는 비영구 화재나 불붙은 캐릭터가 있는 2×2 영역을 지정한다. 마우스 조작은 인접 이동이 필요하다. 행동은 소지·남은 양을 확인하고 걷거나 달리면 중단된다. 완료 시 보이는 칸의 캐릭터·지면에 소화 처리를 요청하며 영향을 준 칸에만 양을 쓰고 부족해지면 멈춘다. 실제 소화와 소모·교체 결과는 해당 처리에 달려 있다.', 'An extinguisher or dirt/gravel/sand bag requires one use per affected square; a water source requires ten. Selection uses held or directly carried supplies and a visible nonpermanent fire or burning character in a 2×2 area, with adjacency walking for mouse control. Inventory and remaining uses are checked; walking/running interrupts. Completion requests extinguishing on visible burning characters/ground, spends supply only on affected squares and stops when insufficient uses remain. Actual extinguishing and use/replacement outcomes depend on those operations.'),
    GROUND_FILL: ('망가지지 않은 TakeDirt 도구와 빈 HoldDirt 용기 또는 같은 내용물 포대에 한 번 더 담을 공간이 필요하다. 이미 퍼낸 지면·재배 중인 지면을 제외하고 대응하는 지면을 선택한다. 같은 종류의 덜 찬 포대를 우선 선택하고 없으면 빈 용기를 쓰며 인접 이동·옮기기·도구 장착 후 작업한다. 걷거나 달리면 중단된다. 완료 시 지면 변경을 요청하고 빈 용기를 사용량 1회의 포대로 바꾸거나 기존 포대에 1회를 더한다. 지면 변경과 물품 생성은 별개이며 둘의 동시 성공을 보장하지 않는다.', 'Use an unbroken TakeDirt tool and an empty HoldDirt container or a matching bag with room for another use. Select matching ground excluding already shovelled ground and client farm plants. A matching partly filled bag takes priority over an empty container; adjacency, transfer and tool equipment precede the action. Walking/running interrupts. Completion requests terrain change and replaces the empty container with a one-use bag or adds one use to the existing bag. Terrain change and item creation are separate, without guaranteed joint success.'),
    GROUND_POUR: ('해당 포대를 소지하고 기존 바닥에 도달해야 하며 필요하면 포대를 옮긴다. 작물·물·이미 같은 종류를 부은 바닥에는 할 수 없다. 지면을 추가하고 이전 모습의 복원 정보를 남긴 뒤 포대를 한 번 사용한다. 포대가 소지품에서 사라지면 같은 종류를 다시 찾는다. 이 경로에 별도 남은 양 검사나 삽 조건을 추가하지 않으며 지면 생성·소모 결과는 해당 처리에 달려 있다.', 'Carry the matching bag, reach an existing floor and transfer it when needed. Plants, water and an already poured floor of the same type are excluded. The action adds ground, retains prior-sprite restoration data and uses the bag once; it finds another of the same type if the bag leaves inventory. This path adds no separate remaining-use check or shovel requirement; floor creation and consumption depend on the called operations.'),
    SMITHING_PARTS: ('문손잡이·경첩 단조법은 철괴 재료와 보존하는 볼핀 망치·집게를 지정하며, 모루 근접·대장장이 기술 3·제작법 학습 조건이 있다. 제작 가능 판정을 만족하고 운전 중이 아니어야 한다. 지정 경험치 콜백은 호출될 때 대장장이 경험치 15를 더하지만, 실제 호출·재료 처리·모루 근접 판정·결과 지급은 제작 처리에 달려 있다.', 'The door-knob and hinge smithing recipes specify iron-ingot material and kept ball-peen hammer/tongs, proximity to an anvil, Blacksmith level 3 and recipe learning. Crafting must be valid and the character must not be driving. The declared callback adds 15 Blacksmith XP when invoked; dispatch, material handling, anvil proximity and result delivery depend on crafting processing.'),
    OPENED_FOOD: ('지원되는 개봉 제작법으로 먼저 포장을 열어야 한다. 개봉 전 포장 자체가 아니라 꺼낸 음식 형태를 받아들이는 요리에서 그 내용물을 재료로 사용한다.', 'First open the package through its supported opening recipe. Use the resulting food contents, rather than the unopened package, in an evolved recipe that accepts that exact food form.'),
    TRAP_PLACEMENT: ('최상위 소지품의 등록된 덫을 월드 덫 메뉴에서 선택한다. 계속 소지한 상태에서 움직이는 물체·고체 장애물·나무·다른 덫이 없는 단단한 바닥이 필요하며 인접한 넘을 수 있는 구조물과 창문 검사도 통과해야 한다. 배치 동작이 접근해 완료되면 해당 타입의 덫을 만들고 소지품의 덫을 제거하며 들고 있던 손을 비운다.', 'Select the registered trap from top-level inventory in the world trap menu. Keep it in inventory and use a solid-floor square without moving objects, solid obstructions, trees or another trap; adjacent hoppable/window checks must pass. Once the build action reaches and completes placement, the exact trap type is initialized and the inventory trap is removed, clearing hands that held it.'),
    TRAP_CATCH: ('설치되어 파괴되지 않은 덫에 대상 동물이 받아들이는 신선한 미끼가 필요하며 그 동물의 시간·지역 조건을 만족해야 한다. 미끼를 넣을 때는 동물과 미끼가 없는 덫에 추가 재료나 음료 메뉴가 없는 익히지 않은 음식을 사용하며 충분한 허기 값이나 지렁이 예외가 필요하다. 매시간 포획 검사는 덫의 칸이 로드되어 있으면 건너뛴다. 로드되지 않은 칸에서도 덫·미끼·기술·지역의 확률 검사와 동물 선택에 달려 있으므로 포획은 보장되지 않는다.', 'Use a placed undestroyed trap with fresh bait accepted by the animal, at its allowed time and zone. Adding bait requires a trap without bait or an animal and uncooked food without extra ingredients or a drink menu, with enough hunger value or the worm exception. Hourly catch checks skip loaded trap squares. Even in unloaded squares, trap/bait, skill, zone rolls and animal selection determine the result; a catch is not guaranteed.'),
    REMOTE_LINK: ('소지품 메뉴에서 조종기나 원격 제어 가능한 무기를 선택하고, 최상위 소지품에 대응 물품이 있어야 한다. 선택한 분기의 ID 미지정 또는 불일치 조건을 만족하면 미지정 조종기에 ID를 만들고 장치에 복사한다. 연결만으로 장치가 배치되거나 작동하지 않는다.', 'Select the controller or remote-capable weapon in the inventory menu with a compatible counterpart in top-level inventory. The selected branch requires an unassigned or differing ID. Linking assigns an ID to an unassigned controller and copies it to the device; it does not itself place or trigger it.'),
    REMOTE_RESET: ('선택한 조종기나 원격 제어 가능한 무기에 ID가 지정되어 있어야 한다. 해제는 선택한 물품의 ID만 미지정으로 바꾸며 연결된 다른 물품 전체를 초기화하지 않는다.', 'The selected controller or remote-capable weapon must have an assigned ID. Reset makes only the selected item ID unassigned; other linked items are not all reset.'),
    REMOTE_TRIGGER: ('선택한 조종기에 ID가 지정되어 있어야 한다. 요청은 그 ID와 범위를 object 명령 수신부에 보내고 IsoTrap.triggerRemote를 호출한다. 대응 덫의 존재·범위 및 실제 효과는 native 덫 처리에 달려 있다.', 'The selected controller must have an assigned ID. The request sends its ID and range to the object command receiver, which calls IsoTrap.triggerRemote. A matching trap, range and actual effect depend on native trap handling.'),
    FERTILIZING: ('소지한 비료나 퇴비로 접근 가능한 작물의 비료 주기 메뉴를 사용한다. 퇴비가 있으면 먼저 선택하며 없을 때 비료를 선택한다. 동작 중 작물 객체가 남아 있어야 하고 걷거나 달리면 중단된다. 완료 시 선택 물품을 한 번 사용하고 서버로 작물 좌표를 보낸다. 서버의 효과는 작물이 계속 존재하고 살아 있으며 빈 경작지가 아닐 때만 적용된다. 동작은 물품 소지나 잔여 사용량을 계속 검사하지 않는다.', 'Use the fertilize menu with fertilizer or compost in inventory and a reachable plant. Compost is selected first when present, otherwise fertilizer. The plant object must remain during the action; walking or running interrupts. Completion uses the selected item once and sends the plant coordinates to the server. Server effects require an existing living plant that is not an empty plowed plot. The action does not continuously recheck inventory or remaining uses.'),
    FERTILIZER_GROWTH: ('서버에서 빈 경작 상태가 아닌 살아 있는 작물에 이전 비료 사용이 네 번 미만일 때 비료 횟수를 늘리고 다음 성장 예정 시점을 하한 1까지 앞당긴다. 이전 예정 시점이 그 하한보다 높을 때만 실제로 앞당겨진다.', 'For a living non-plowed plant with fewer than four previous applications, the server increments the fertilizer count and advances the next-growth schedule with a lower bound of one. The schedule only moves earlier when its previous value is above that bound.'),
    FERTILIZER_ROT: ('서버에서 빈 경작 상태가 아닌 살아 있는 작물이 이미 비료를 네 번 이상 받았을 때 추가로 주면 rottenThis가 작물을 부패 상태로 바꾼다.', 'If a living non-plowed plant on the server already has at least four fertilizer applications, another application calls rottenThis and sets it to rotten.'),
    RADIO_DISMANTLING: ('분해 제작법에 맞는 파손되지 않은 라디오·텔레비전과 보존하는 드라이버를 제공해야 한다. 전자 기기 검사는 드라이버 태그 참여 물품 외의 즐겨찾기 물품을 제외하며 제작 가능 판정이 필요하고 운전 중에는 할 수 없다. 제작법은 전자 스크랩을 결과로 지정하지만 추가 부품은 확률·기술 분기에 달려 있다. 건전지나 헤드폰 회수는 기기 데이터에 위임하므로 회수품을 보장하지 않는다.', 'Supply the compatible unbroken radio or television and kept screwdriver required by the dismantling recipe. The electronics test excludes favorites except screwdriver-tagged participants; recipe eligibility and not driving are required. The recipe declares electronic scrap, while extra components depend on random and skill branches. Battery and headphone retrieval is delegated to device data and is not guaranteed.'),
    MATERIAL_ASSEMBLY: ('선택한 지원 제작법에 지정된 재료와 필요한 보존형 절삭 도구를 제공해야 한다. 낚시 장비 제작법이 학습을 요구하면 먼저 익혀야 한다. 제작법과 참여 물품의 제작 가능 판정이 필요하며 운전 중에는 할 수 없다. 결과물 지정은 생산 대상을 뜻하며 그 결과물의 재료 역할이나 도구·치료 효과를 보장하지 않는다.', 'Supply the materials and any kept cutting tool specified by the selected supported recipe. Learn the fishing-gear recipe where required. The recipe and participants must pass recipe eligibility, and the character must not be driving. A declared result identifies the produced item; it does not establish a material role or the resulting tool or medical effect.'),
    RADIO_CRAFTING: ('해당 간이 무전기 제작법을 익히고 지정 부품과 대응 드라이버를 갖춰야 한다. 전기 기술 1 이상, 파손되지 않은 물품, 제작 가능 판정이 필요하며 운전 중에는 할 수 없다. 드라이버는 보존하는 도구다. 완성품에 기기 데이터가 있을 때만 callback이 기술에 따른 임의 속성을 설정하며 건전지와 저장 전력은 없는 상태로 설정한다. 부품 사용이 전원이 공급된 무전기를 보장하지 않는다.', 'Learn the makeshift radio recipe and supply its specified components and a compatible screwdriver. Electricity skill of at least one, unbroken items, recipe eligibility and not driving are required. The screwdriver is kept. Only a result with device data receives skill-dependent randomized properties from the callback, with no installed battery or stored power. Component use does not guarantee a powered radio.'),
    ROD_FISHING: ('물가의 낚시 메뉴에서 소지한 부서지지 않은 낚싯대와 등록된 미끼를 선택하는 창 낚시 외의 경로에 해당한다. UI가 허용된 높이에서 가까운 물을 찾아야 한다. 낚싯대는 주 손, 미끼는 보조 손에 계속 들고 있어야 하며 걷기·달리기나 다른 대기 동작으로 중단된다. 물고기 잔량, 미끼, 기술, 시간, 계절, 확률 선택과 낚싯줄 파손에 따라 결과가 달라지며 포획은 보장되지 않는다.', 'In the nonspear branch, select an unbroken rod and registered lure from inventory through the water fishing menu. The UI must find nearby water at an allowed player level. Keep the rod in the primary hand and lure in the secondary hand; walking, running or another queued action interrupts. Fish availability, lure, skill, time, season, random selection and line breakage affect the result; a catch is not guaranteed.'),
    DIRTY_BANDAGING: ('건강 패널에서 붕대를 적용할 수 있는 부위에 사용하며, 재료를 소지하고 환자가 치료 범위 안에 있어야 한다. 붕대를 제거하는 동작과 구분되며 적용 시 재료를 소모한다. 더러운 붕대라는 구분만으로 별도의 감염 상태까지 확정하지는 않는다.', 'Apply to an eligible body part from the Health panel with the material in inventory and the patient within treatment reach. This is bandage application, and the material is consumed. The dirty-bandage classification alone does not establish a separate infected state.'),
    CAMP_FUEL_USE: ('차량 밖에서 접근 가능한 기존 모닥불에 사용한다. 선택할 때 즐겨찾기한 물품은 제외하며 옷은 착용하지 않은 직물 의류여야 하고 용기는 비어 있어야 한다. 소지품으로 옮겨 동작이 끝날 때까지 보유해야 하며 걷거나 달리면 중단된다. 완료 시 소모형 물품은 한 번 사용하고 일반 물품은 제거한 뒤, 모닥불이 계속 존재하면 등록된 연료량을 더한다.', 'Use outside a vehicle at a reachable existing campfire. At selection, favorites are excluded, clothing must be unequipped fabric clothing, and containers must be empty. Transfer the item to inventory and keep it there until completion; walking or running interrupts. Completion uses a drainable once or removes an ordinary item, then adds the registered fuel amount if the campfire still exists.'),
    CAMP_TINDER_USE: ('차량 밖에서 접근 가능한 꺼진 모닥불, 등록된 불쏘시개, 대응하는 발화 도구가 필요하다. 선택할 때 불쏘시개는 즐겨찾기하지 않은 물품이어야 하고 옷은 벗은 직물 의류, 용기는 빈 상태여야 한다. 두 물품을 계속 소지해야 하며 걷거나 달리면 중단된다. 완료 시 불쏘시개를 제거하고 발화 도구를 한 번 사용한다. 모닥불이 계속 존재하면 불쏘시개의 연료를 더하고, 꺼져 있고 연료가 남은 경우 불을 붙인다.', 'Outside a vehicle, use a reachable unlit campfire with registered tinder and a matching fire-starting item. At selection, tinder must not be a favorite; clothing must be unequipped fabric clothing and containers must be empty. Keep both items in inventory; walking or running interrupts. Completion removes tinder and uses the starting item once. If the campfire still exists, tinder fuel is added and the fire is lit when unlit with positive fuel.'),
    ELECTRONIC_SALVAGE: ('대응하는 기기와 호환 드라이버를 제공하고 분해 제작 조건을 충족해야 한다. 기기 자체도 드라이버로 인정되는 경우를 제외하면 즐겨찾기한 기기는 분해할 수 없으며 운전 중에는 제작할 수 없다. 기기는 제작법에 따라 부품으로 바뀌고, 추가 건전지 회수는 기기별 분해 방식과 남은 충전량 또는 무작위 결과에 달려 있다.', 'Supply the matching device and a compatible screwdriver and meet the dismantling requirements. A favorite device is excluded unless it also qualifies as a screwdriver; crafting is unavailable while driving. The device is transformed into recipe parts, while extra battery recovery depends on its dismantling behavior and remaining charge or a random outcome.'),
    SCRAP_RECOVERY: ('이 분해 방식은 전자 스크랩을 회수하며, 일정한 수량이나 추가 건전지 회수를 보장하지는 않는다.', 'This dismantling operation recovers electronic scrap, without promising a fixed quantity or an extra battery.'),
    CARPENTRY_MATERIAL: ('선택한 목공 메뉴 물체의 재료·기술 조건과 지정된 경우 부서지지 않은 망치가 필요하다. 소지품과 주변 바닥의 물품을 재료로 확인하며 용기 재료는 비어 있어야 한다. 해당 물체의 배치 조건과 같은 높이에서 접근 가능한 건축 동작 조건을 충족해야 한다. 일반 생성 시 지정 재료를 소모하지만 치트 모드에서는 소모하지 않으며, 양문은 없는 첫 부분을 만들 때만 재료를 소모한다.', 'Meet the selected carpentry object material/skill requirements and any required unbroken hammer. Inventory and nearby-ground supplies count; container materials must be empty. The object-specific placement checks and reachable same-level build action must hold. Normal creation consumes its declared materials, except in cheat mode; double doors consume them only when creating a missing first part.'),
    BATTERY_INSERTION: ('대응하는 기기의 충전량이 0이어야 하며 건전지를 제공하고 삽입 제작 조건을 충족해야 한다. 운전 중에는 제작할 수 없으며 이 제작법은 걷기를 허용한다. 결과 기기는 선택된 건전지의 남은 충전량을 받으므로 완충이나 양의 충전량이 보장되지는 않는다.', 'The compatible device must have zero charge, with a battery supplied and insertion requirements satisfied. Crafting is unavailable while driving, but this recipe permits walking. The result receives the selected battery remaining charge, which is not guaranteed to be full or positive.'),
    NOTE_IMPLEMENT: ('작성 가능한 메모를 열 때 대응하는 필기구를 소지해야 하고 다른 사용자가 메모를 잠근 상태가 아니어야 한다. 자신의 편집 잠금도 푼 뒤 페이지나 제목을 바꾸고 확인해야 저장된다. 필기구 보유 여부는 메뉴를 열 때 확인한다.', 'When opening a writable note, keep a matching writing implement in inventory and ensure another user has not locked the note. Unlock your own editing lock before changing pages or title, then confirm to save. The implement check occurs when opening the menu.'),
    MAP_ANNOTATION: ('지도 편집 화면에서 대응하는 필기구를 소지해야 한다. 사용 가능한 필기구 색과 기호나 글의 위치를 선택하며, 글은 공백이 아닌 내용을 입력하고 확인해야 추가된다. 기존 주석을 수정하거나 옮기려면 지우개도 필요하다.', 'Use the map editor with a matching writing implement in inventory. Select an available implement color and a symbol or note position; text must be nonempty and confirmed. Editing or moving existing annotations also requires an eraser.'),
    MAP_ERASURE: ('지도 편집 화면에서 지우개를 소지하고 기존 글이나 기호를 선택해야 한다. 주석을 수정하거나 옮기려면 대응하는 필기구도 필요하다.', 'Use the map editor with an eraser in inventory and select an existing note or symbol. Editing or moving annotations also requires a compatible writing implement.'),
    UMBRELLA_CHANGE: ('제작법이 대응하는 펼친 우산이나 접힌 우산을 받아들이고 제작 조건을 충족해야 하며 운전 중에는 제작할 수 없다. 형태를 바꿀 때 이전 우산의 상태를 복사하며, 손에 배치되는 방식은 이전에 들고 있던 손에 따라 달라진다.', 'The recipe must accept the matching open or closed umbrella and satisfy crafting eligibility; crafting is unavailable while driving. The form change copies the prior umbrella condition, and hand placement depends on how it was held.'),
    ACTIVATION: ('손에 들거나 몸에 부착한 활성화 가능 물품 하나를 선택해야 한다. 소모형으로 취급되는 물품은 사용량이 남아 있어야 한다.', 'Select one activatable item held in a hand or attached to the character. Items treated as consumable must have some uses remaining.'),
    STAGE_ACTION: ('단계별 건축은 시작할 때 지정된 제작법 습득 여부, 부서지지 않은 유지 도구, 소지품이나 주변 바닥의 충분한 재료 수·사용량을 확인한다. 유지 도구는 최대 두 개를 손에 준비한다. 걷거나 달리면 중단되며 일반 완료 시 건축 단계를 적용한 뒤 지정 재료나 사용량을 소모한다. 건축 치트 모드에서는 소모하지 않는다.', 'At the start of a multistage build, the specified learned recipe, unbroken kept tools and sufficient inventory or nearby-ground materials/uses are checked. Up to two kept tools are prepared for the hands. Walking or running interrupts building. Normal completion applies the stage then consumes its listed materials or uses; construction cheat mode bypasses consumption.'),
    SOWING: ('씨앗이 아직 없는 경작된 고랑에 접근하고 해당 종류의 낱알 씨앗을 필요한 수만큼 갖춰야 한다. 고른 씨앗을 소지품으로 옮기며 소모될 때까지 소지해야 한다. 걷거나 달리면 중단되고 서버에서도 고랑이 아직 경작 상태여야 한다. 성장이나 수확을 보장하지 않는다.', 'Reach an unseeded plowed furrow with the required number of configured loose seeds. Selected seeds are transferred into inventory and must remain there until consumed. Walking or running interrupts sowing; the server also requires a still-plowed furrow. Growth or harvest is not guaranteed.'),
    SEED_EXTRACTION: ('봉지를 먼저 열어 나온 낱알 씨앗을 사용해야 하며, 심기 동작이 소모하는 물품은 미개봉 봉지가 아니다.', 'Open the packet first and use the resulting loose seeds; sowing does not consume the unopened packet.'),
    FIXING_ACTION: ('선택한 수리 규칙의 필요 물품을 확보해 소지품으로 옮겨야 한다. 지정된 수리 재료에 해당하는 물품을 계속 소지해야 하며 차량 장착 부품이 아니면 수리 대상도 소지해야 한다. 걷거나 달리면 중단된다. 수리 결과와 재료 소모는 수리 엔진의 처리에 달려 있다.', 'Required items for the selected fixing rule are transferred into inventory. An item matching the selected fixer must remain there; the target must also remain there unless it is an installed vehicle part. Walking or running interrupts repair. Outcome and material consumption depend on the fixing engine.'),
    MELEE: ('비원거리 공격 분기에 해당하고 아직 공격을 시작하지 않았으며 플레이어의 근접 공격이 허용되어야 한다. 일반 무기 공격은 차량 밖에서 해야 하고, 명중·피해·대상 결과는 이 호출만으로 보장하지 않는다.', 'The weapon must use the non-ranged branch, no attack may already be underway, and player melee authorization must hold. Ordinary weapon attacks require being outside a vehicle. This dispatch does not establish hits, damage or target outcomes.'),
    COOKING_BASE: ('조리법이 선택한 바탕 물품이나 이미 준비된 결과물과 추가할 재료를 받아들여야 한다. 둘을 소지품으로 옮기고 바탕 물품을 계속 소지해야 하며 재료의 냉동·익힘·독성 허용 조건을 충족해야 한다. 걷거나 달리면 중단되고, 더 넣을 수 있는 재료와 결과 상태는 조리법과 현재 내용물에 달려 있다.', 'The recipe must accept this selected base or prepared result and an ingredient. Both are transferred into inventory and the base must remain there; ingredient freezing, cooking and poisoning-policy checks apply. Walking or running interrupts addition. Further ingredients and resulting food state depend on the recipe and current contents.'),
    ROPE_MAKING: ('시트 로프 제작법이 이 직물이나 지정된 시트를 받아들이고 제작 조건을 충족해야 하며 운전 중에는 제작할 수 없다. 등록된 직물이 시트 로프 제작을 허용해야 하고, 물품은 남겨 두는 도구가 아닌 재료로 제공된다.', 'The sheet-rope recipe must accept this fabric or named sheet and satisfy crafting eligibility; crafting is unavailable while driving. The registered fabric must permit sheet rope. The item is supplied as material, not a retained tool.'),
    ALARM_SETTING: ('선택한 시계가 게임의 디지털 시계 조건을 만족해야 한다. 월드에 놓인 시계가 아니면 먼저 기본 소지품으로 옮긴다. 창을 연 위치에서 어느 축이든 0.1보다 많이 움직이면 창이 닫힌다. 확인을 눌러 알람 켜짐 상태·시·분을 저장하며 실제 울림은 별도의 시계 동작에 달려 있다.', 'The clock must satisfy the native digital-clock predicate. Unless it is a world item, it is transferred to the main inventory first. Moving more than 0.1 on either position axis closes the dialog. Confirm OK to save alarm-enabled state, hour and minute; actual ringing depends on separate clock behavior.'),
    ALARM_STOPPING: ('디지털 시계의 알람이 울리고 있어야 한다. 플레이어와 알람 위치가 있으면 플레이어 소지품 안에 있거나 월드에서 접근할 수 있어야 하며, 다른 용기에 있으면 먼저 옮긴다. 달리면 중단되며 월드 물품은 걸어도 중단된다. 플레이어나 알람 위치가 없으면 즉시 울림 중지를 호출한다.', 'The digital-clock alarm must be ringing. With a player and alarm square, it must be in a player inventory or reachable in the world; a contained clock is transferred first. Running interrupts stopping; walking also interrupts it for a world item. If the player or alarm square is missing, ringing is stopped immediately.'),
    MAKEUP_USE: ('화장품 종류가 지원하는 분장을 골라 적용을 눌러야 한다. 메뉴를 열려면 소지한 거울, 벽에 가리지 않는 주변 거울, 차량 탑승 상태 또는 사용 가능한 파운데이션이 필요하다. 미리보기만으로는 분장 교체를 확정하지 않는다.', 'Choose makeup supported by this type and confirm Apply. The menu requires an inventory mirror, a nearby unobstructed mirror, being in a vehicle, or available foundation makeup. Preview alone does not commit the replacement.'),
    WEAPON_ATTACHMENT: ('호환 총기의 해당 슬롯이 비어 있고 부서지지 않은 드라이버가 있어야 한다. 총기와 부품을 옮기고 드라이버는 주 손, 부품은 다른 손에 든다. 동작은 바로 소지한 드라이버·부품과 빈 슬롯을 검사하며 총기 소지와 호환 목록은 다시 검사하지 않는다. 걷거나 뛰면 중단되며 완료 시 장착하고 부품을 인벤토리에서 빼고 다른 손을 비운다. 실제 성능 변화는 엔진 처리가 필요하다.', WEAPON_ATTACHMENT),
    WEAPON_PART_REMOVAL: ('부서지지 않은 드라이버로 장착 부품의 회수를 선택한다. 동작 중에는 바로 소지한 드라이버와 총기, 해당 슬롯에 같은 부품이 남아 있는지 검사한다. 걷거나 뛰면 중단되며 완료 시 같은 부품을 떼어 인벤토리에 넣고 손의 모델을 갱신한다. 성능 수치의 재계산은 엔진 처리에 남는다.', WEAPON_PART_REMOVAL),
    READ_MOOD: ('기술서가 아닌 책을 읽는 동안 해당 수치가 읽기 시작 때보다 높아지면 시작 때의 값으로 되돌린다. 읽기를 마칠 때 적용되는 별도 기분 변화까지 확정하는 의미는 아니다.', 'During non-skill reading, this value is restored to its reading-start value if it rises above it. This does not establish the separate mood change at completion.'),
    PICKUP: ('이동 가능한 설치물과 필요한 부품이 있어야 하며, 개체 종류에 따른 내용물·수용량·받침·물·화기·창문·도구·기술 조건을 충족해야 한다. 같은 층에서 작업 거리와 멀티플레이 권한을 유지해야 한다.', 'The placed object must be movable with its required parts, meeting its object-specific contents, capacity, support, water, fire, window, tool and skill checks. Stay within reach on the same floor with multiplayer permission.'),
    PICKUP_LOSS: ('떼어내다가 부서질 수 있으며 온전한 물품이나 같은 종류의 소지품을 돌려받는다고 보장하지 않는다.', 'Removal may break it and does not guarantee return of an intact item or the same inventory item type.'),
    SMOKING: ('성냥이나 라이터를 소지하고 흡연 동작을 완료해야 한다. 취소하면 흡연 효과를 적용하지 않는다.', 'A match or lighter must be in inventory and the smoking action must complete. Cancelling does not apply the smoking effects.'),
    SMOKER_EFFECT: ('흡연가 특성이 있을 때 적용되며 섭취한 비율과 담배의 현재 스트레스 값에 따라 달라진다.', 'Applies with the Smoker trait, scaled by the consumed portion and the cigarette’s current stress value.'),
    NONSMOKER_EFFECT: ('흡연가 특성이 없을 때 섭취한 비율에 따라 적용된다.', 'Applies without the Smoker trait, according to the consumed portion.'),
    POISONOUS_WILD_FOOD: ('먹은 야생 식품의 독성이 양수일 때 섭취한 비율에 따라 적용된다.', 'Applies when the eaten wild food has positive poison power, according to the consumed portion.'),
    PLACEMENT: ('가구와 필요한 부품을 갖추고 공간·바닥이나 벽면·도구·기술·접근 및 멀티플레이 권한 조건을 충족해야 한다.',
                'The furniture and required parts must be available, with suitable space and support, tools, skills, access and multiplayer permissions.'),
    PAINTING: ('호환되는 도색 면이나 벽 표식에 붓과 해당 페인트가 필요하며, 일반 도색은 페인트를 소모한다.',
               'A brush and the selected paint are needed for a compatible surface or wall sign; normal painting consumes paint.'),
    OPENING: ('개봉 제작법에서 요구하는 도구와 사용 조건을 충족해야 하며, 운전 중에는 제작할 수 없다.',
              'The opening recipe must meet its tool and eligibility requirements; crafting is unavailable while driving.'),
    CAN_OPENING: ('해당 통조림과 제작법이 받는 캔따개가 필요하며 둘 다 사용할 수 있어야 한다. 제작 조건을 충족해야 하고 운전 중에는 제작할 수 없다.',
                  'The specified can and a compatible can opener must both be available. Recipe eligibility must hold; crafting is unavailable while driving.'),
    FIRING: ('총기가 걸리지 않았고 약실이 있으면 탄이 약실에 들어 있어야 하며, 약실이 없는 총기는 탄약이 남아 있어야 한다. 캐릭터가 공격 가능한 상태여야 한다.',
             'The weapon must not be jammed. A weapon with a chamber needs a chambered round; otherwise ammunition must remain. The character must be allowed to attack.'),
    CHOPPING: ('접근 가능한 나무가 있고 주로 쓰는 손에 사용 가능한 도끼를 든 채 공격할 수 있어야 한다.',
               'An existing tree must be within reach, with a usable axe held in the primary hand and the character able to attack.'),
    CONSUMING: ('소지품에 남아 있고 필요한 보조 물품을 갖춰야 하며, 포만감이나 열량 상태가 섭취를 시작할 수 있는 상태여야 한다.',
                'It must remain in inventory, any required companion item must be present, and satiety or calorie state must permit starting consumption.'),
    WEARING: ('의류를 소지하고 해당 의류의 지정된 신체 부위에 착용해야 한다.',
              'The clothing must be in inventory and worn at its designated body location.'),
    WEAR_ACTION: ('착용 전에 소지품으로 옮기며 동작 중에도 소지해야 한다. 이미 착용한 물품은 건너뛰고 걷거나 뛰면 착용 동작이 중단된다.',
                  'It is transferred into inventory before wearing and must remain there during the action. Already equipped items are skipped; walking or running interrupts wearing.'),
    COOKING_ACTION: ('선택한 음식에 제작법이 허용하는 재료여야 한다. 둘 다 소지품으로 옮기고 바탕 음식을 계속 소지해야 하며, 냉동 재료는 제작법의 허용이 필요하고 필요한 조리 조건도 충족해야 한다. 독성 재료는 메뉴의 독 사용 정책이 허용해야 한다. 걷거나 뛰면 재료 추가 동작이 중단된다.',
                     'The recipe must accept the ingredient for the selected food. Both are transferred into inventory and the base must remain there. Frozen ingredients need recipe permission and required cooking must be satisfied. Poisonous ingredients must be permitted by the menu poisoning policy. Walking or running interrupts adding the ingredient.'),
    NOTE_SAVE: ('확인을 눌렀을 때 쪽의 내용과 제목을 저장하며, 취소하면 이 편집 내용을 제출하지 않는다.',
                'Page edits and the title are saved when OK is confirmed; cancelling does not submit these edits.'),
    NOTE_EDIT: ('필기구가 필요하고 다른 사용자가 잠근 상태가 아니어야 하며, 자신의 편집 잠금도 풀어야 한다.',
                'A writing implement is required, another user must not own the lock, and the journal editing lock must be unlocked.'),
    NOTE_ACCESS: ('필기구가 있어야 하며 다른 사용자의 소유 잠금이 없어야 편집 제어를 사용할 수 있다.',
                  'Editing controls require a writing implement and no ownership lock belonging to another user.'),
    NOTE_LIMITS: ('정해진 작성 가능 쪽수와 입력 길이 범위에서 기록하며, 기존 쪽의 열람과 편집 권한은 구별된다.',
                  'Writing follows the writable page count and text-entry limits; viewing existing pages is separate from editing permission.'),
    NOTE_LOCK: ('편집 가능한 기록 창에서 잠금이나 해제를 누르면 즉시 적용되며, 쪽 편집을 취소해도 잠금 변경은 취소되지 않는다.',
                'Lock and unlock controls in an editable journal apply immediately; cancelling page edits does not undo a lock change.'),
    LOADING: ('호환되는 탄약과 장전할 여유가 필요하다. 총기를 직접 장전할 때는 주로 쓰는 손에 들고, 탄창을 채울 때는 탄창을 소지해야 하며 장전 동작의 애니메이션 이벤트에서 반영된다.',
              'Matching ammunition and loading space are required. Direct gun loading requires the primary hand; magazine filling requires the magazine in inventory. Loading is applied by action animation events.'),
    MAGAZINE_FILL: ('소지한 탄창의 여유 용량과 맞는 탄약을 확인하고 필요한 탄약을 옮긴다. 동작은 탄창 소지를 검사하며 삽입 애니메이션마다 탄약 하나를 빼고 탄창의 탄수를 늘린다. 가득 차거나 탄약이 없어지면 끝나며 메뉴에서 요청한 수량은 진행 표시용이다. 뛰면 중단되지만 걷기와 조준은 허용되고 이미 넣은 탄은 유지된다.', MAGAZINE_FILL),
    MAGAZINE_EMPTY: ('탄이 남은 소지 탄창을 선택한다. 동작은 탄창 소지를 검사하고 탄약 제거 애니메이션마다 해당 탄약을 하나 생성해 인벤토리에 넣고 탄수를 줄인다. 비어야 완료되며 뛰면 중단되지만 걷기는 허용되고 이미 꺼낸 탄은 유지된다.', MAGAZINE_EMPTY),
    MAGAZINE_LOADING: ('호환 탄창이 없는 총기를 주 손에 들고 삽입 애니메이션까지 탄창을 소지한다. 동작은 호환성을 재검사하지 않는다. 삽입 시 탄창을 소지품과 손에서 빼고 탄수를 총기에 복사하며 약실이 비고 탄이 충분하면 장전 동작을 잇는다. 뛰면 중단되지만 걷기와 조준은 허용된다. 이후 배출은 원래 물건을 반환하지 않고 새 탄창에 남은 탄수를 복사한다.', MAGAZINE_LOADING),
    MAP_READING: ('필요하면 지도를 소지품으로 옮겨 열며, 계속 소지하지 않으면 창이 닫힌다. 화면 이동·확대·축소·보기 초기화를 지원한다. 실행 중 지도 ID로 초기화 함수를 선택하고, 함수가 없으면 오류를 알리지만 창 열기를 막지는 않는다. 표시 내용의 정확성은 보장하지 않는다.',
                  'The map is transferred to inventory when needed and the window closes if it is no longer held there. Pan, zoom and reset the view. The runtime map ID selects initialization; a missing initializer is reported without blocking the window. Displayed accuracy is not guaranteed.'),
    READ_PROGRESS: ('쪽수가 정해진 읽을거리에서는 캐릭터별 독서 진행이 기록된다. 기술 수준이 부족하거나 문맹이면 진행이 초기화될 수 있다. 기술서를 완독하면 캐릭터의 기록과 별개로 책에 기록된 읽은 쪽수는 초기화된다.',
                     'Reading progress is recorded for each character when the book has a defined page count. Insufficient training or illiteracy can reset progress. Completing a skill book resets the pages read on the book itself, separately from the character record.'),
    READ_MAXIMUM: ('책의 최대 배율에는 완독이 필요하며, 지원 기술 수준에서 현재보다 높은 배율일 때만 적용된다.',
                    'The book maximum requires full reading progress and applies only when higher than the current multiplier, within the supported skill levels.'),
    CARRYING: ('용기를 캐릭터의 소지품으로 옮길 수 있어야 한다. 넣을 공간·허용 여부·꺼내기·접근 및 멀티플레이 권한 조건을 충족해야 하며 내용물은 용기에 담긴 채로 옮겨진다.',
               'The container must be transferable into the character inventory, meeting space, admission, removal, access and multiplayer requirements. Its contents move with the container.'),
    WATER_STORAGE: ('같은 건물 맥락의 물이 남은 수원에 접근하고, 소지품에서 파손되지 않은 호환 용기를 골라야 한다. 이미 물이 든 용기는 채울 여유가 있어야 한다. 용기를 옮긴 뒤 계속 어느 소지품 안에 있어야 하며, 빈 형태는 채우기 시작 때 교체된다. 수량은 진행도·남은 물·용량에 따라 늘고 걷기·달리기로 중단하면 일부만 채워질 수 있다. 오염된 수원은 중단 시에도 물을 오염시키며, 기존 오염 제거나 가득 채움을 보장하지 않는다.',
                    'Reach a source with water in the same building context and select an unbroken compatible inventory container. An existing water form needs filling space. Transfer the item and keep it in a container; an empty form is replaced when filling starts. Amount follows progress, remaining water and capacity, so walking/running can leave a partial fill. Tainted source water taints even an interrupted fill; existing taint is not cleared and a full container is not guaranteed.'),
    DISINFECTION: ('건강 패널에서 붕대가 감기지 않은 상처·봉합·부목 부위를 선택하고 소독제를 치료자의 소지품에 유지한다. 달리면 중단되고 사타구니 아래 부위는 걸어도 중단된다. 다른 환자의 위치가 바뀌면 차량 밖이거나 운전 중인 경우 중단되며 자가 치료와 차량 탑승에는 해당 예외가 있다.',
                   'Select an injured, stitched or splinted but unbandaged part in the Health panel and keep the disinfectant in doctor inventory. Running interrupts, as does walking below the groin. A different patient changing position interrupts when outside a vehicle or driving, with exceptions for self-treatment and vehicle passengers.'),
    SPLINTING: ('봉합되거나 이미 부목이 대어진 곳을 제외한 골절 부위가 필요하며 머리와 몸통은 대상이 아니다. 완성 부목 또는 적합한 지지 재료와 찢어진 천을 준비하고 환자가 시술 거리 안에 있어야 한다.',
                 'The fracture must not already be stitched or splinted; head and torso are excluded. A finished splint or compatible support material with ripped sheets is required, with the patient within treatment reach.'),
    STITCHING: ('유리가 없고 붕대가 감기지 않은 깊은 상처에 봉합 바늘 또는 적합한 바늘과 실을 사용한다. 소모되는 봉합 재료를 소지하고 환자가 시술 거리 안에 있어야 한다.',
                 'Use a suture needle or a compatible needle and thread on a deep, unbandaged wound without glass. Keep the consumed suture material in inventory and the patient within treatment reach.'),
    GLASS_REMOVAL: ('붕대가 감기지 않고 유리가 박힌 다친 부위를 선택한다. 시작할 때 도구를 갖추고 환자가 시술 거리 안에 있어야 한다. 맨손 제거는 메뉴의 별도 경로다.',
                     'Select an injured, unbandaged part containing glass, with the tool available at selection and the patient within treatment reach. Bare-hand removal is a separate menu route.'),
    BULLET_REMOVAL: ('붕대가 감기지 않고 총알이 박힌 다친 부위를 선택한다. 시작할 때 적합한 도구를 갖추고 환자가 시술 거리 안에 있어야 한다.',
                      'Select an injured, unbandaged part containing a bullet, with a compatible tool available at selection and the patient within treatment reach.'),
    POULTICE_USE: ('붕대가 감기지 않은 다친 부위에 다른 약초 찜질제가 적용되어 있지 않아야 한다. 찜질제를 소지한 상태로 바르면 소모되며 환자가 시술 거리 안에 있어야 한다.',
                   'The injured, unbandaged body part must have no other herbal poultice applied. Keep the poultice in inventory until application, which consumes it, and the patient within treatment reach.'),
}

QUALIFIERS.update({predicate: (f'해당 작물은 고랑 하나에 낱알 씨앗 {n}개가 필요하다.',
                              f'This crop requires {n} loose seeds per furrow.') for n, predicate in SOW_COUNTS.items()})

EFFECTS = {
    ('thirst', 'decrease'): ('갈증을 줄인다.', 'It reduces thirst.'),
    ('poison_level', 'increase'): ('독 수치를 높일 수 있다.', 'It can increase poison level.'),
    ('food_chef_attribution', 'set_transferring_character'): ('식품의 조리자 정보를 옮긴 캐릭터로 기록한다.', 'It records the transferring character as the food chef.'),
    ('food_preservation_age', 'rebase_on_cooking'): ('조리 콜백에서 식품의 신선도·부패 기준과 상대 나이를 조정한다.', 'Its cooking callback rebases freshness/rot thresholds and relative age.'),
    ('fish_size_nutrition', 'initialize_from_registered_size'): ('생성 콜백에서 등록된 크기에 따라 생선의 무게·영양·허기 값을 설정한다.', 'Its creation callback sets fish weight, nutrition and hunger values from the registered size.'),
    ('body_wetness', 'decrease'): ('몸의 젖은 정도를 줄인다.', 'It reduces body wetness.'),
    ('crop_growth_schedule', 'advance'): ('작물의 다음 성장 예정 시점을 앞당길 수 있다.', 'It can advance the crop next-growth schedule.'),
    ('crop_state', 'set_rotten'): ('과다 사용하면 작물을 부패 상태로 바꾼다.', 'Excessive application sets the crop to rotten.'),
    ('applied_bandage_life', 'set_zero'): ('적용한 붕대의 유효 시간 값을 0으로 설정한다.', 'It sets the applied bandage life value to zero.'),
    ('boredom', 'cap_at_reading_start'): ('독서 중 지루함이 읽기 시작 때보다 높아지지 않게 한다.', 'While reading, boredom is kept from exceeding its reading-start value.'),
    ('stress', 'cap_at_reading_start'): ('독서 중 스트레스가 읽기 시작 때보다 높아지지 않게 한다.', 'While reading, stress is kept from exceeding its reading-start value.'),
    ('unhappiness', 'cap_at_reading_start'): ('독서 중 불행 수치가 읽기 시작 때보다 높아지지 않게 한다.', 'While reading, unhappiness is kept from exceeding its reading-start value.'),
    ('stress', 'decrease'): ('스트레스를 줄인다.', 'It reduces stress.'),
    ('unhappiness', 'decrease'): ('불행 수치를 줄인다.', 'It reduces unhappiness.'),
    ('food_sickness', 'increase'): ('식중독 수치를 높인다.', 'It increases food sickness.'),
    ('written_note_pages', 'update'): ('기록한 쪽의 내용이 저장된다.', 'The written page content is saved.'),
    ('written_note_title', 'update'): ('기록물의 제목을 바꿀 수 있다.', 'The note title can be changed.'),
    ('written_note_lock', 'update'): ('기록물의 편집 잠금을 설정하거나 해제할 수 있다.', 'The note editing lock can be set or removed.'),
    ('reading_page_progress', 'update'): ('읽은 쪽의 진행 상태가 기록된다.', 'Read-page progress is recorded.'),
}

BODY_LABELS = {
    'Hat': ('머리', 'head'), 'FullHat': ('머리', 'head'),
    'Pants': ('하체', 'lower body'), 'Tshirt': ('상체', 'upper body'),
    'Shirt': ('상체', 'upper body'), 'ShortSleeveShirt': ('상체', 'upper body'),
    'TankTop': ('상체', 'upper body'), 'Jacket': ('겉옷', 'outerwear'),
    'JacketHat': ('후드가 있는 겉옷', 'hooded outerwear'),
    'JacketHat_Bulky': ('후드가 있는 겉옷', 'hooded outerwear'),
    'Jacket_Bulky': ('겉옷', 'outerwear'), 'Jacket_Down': ('겉옷', 'outerwear'),
    'JacketSuit': ('겉옷', 'outerwear'), 'Sweater': ('상체', 'upper body'),
    'SweaterHat': ('후드가 있는 상의', 'hooded upper clothing'),
    'UnderwearBottom': ('하의 속옷', 'lower underwear'), 'UnderwearTop': ('상의 속옷', 'upper underwear'),
    'Underwear': ('속옷', 'underwear'), 'UnderwearInner': ('속옷', 'underwear'),
    'UnderwearExtra1': ('추가 속옷', 'additional underwear'), 'UnderwearExtra2': ('추가 속옷', 'additional underwear'),
    'Ears': ('귀', 'ears'), 'EarTop': ('귀 윗부분', 'upper ear'),
    'BellyButton': ('배꼽', 'belly button'), 'Nose': ('코', 'nose'),
    'Shoes': ('발', 'feet'), 'Socks': ('양말', 'socks'), 'Hands': ('손', 'hands'),
    'Dress': ('원피스', 'dress'), 'Skirt': ('치마', 'skirt'),
    'Neck': ('목', 'neck'), 'Necklace': ('목걸이', 'necklace'), 'Necklace_Long': ('긴 목걸이', 'long necklace'),
    'Scarf': ('목도리', 'scarf'), 'Eyes': ('눈', 'eyes'),
    'LeftEye': ('왼쪽 눈', 'left eye'), 'RightEye': ('오른쪽 눈', 'right eye'),
    'Mask': ('얼굴', 'face'), 'MaskEyes': ('얼굴', 'face'), 'MaskFull': ('얼굴', 'face'),
    'LeftWrist': ('왼쪽 손목', 'left wrist'), 'RightWrist': ('오른쪽 손목', 'right wrist'),
    'Left_MiddleFinger': ('왼손 중지', 'left middle finger'), 'Right_MiddleFinger': ('오른손 중지', 'right middle finger'),
    'Left_RingFinger': ('왼손 약지', 'left ring finger'), 'Right_RingFinger': ('오른손 약지', 'right ring finger'),
    'TorsoExtra': ('상체 덧옷', 'additional torso clothing'), 'TorsoExtraVest': ('조끼', 'vest'),
    'Boilersuit': ('전신 작업복', 'coveralls'), 'FullSuit': ('전신 의복', 'full suit'),
    'FullSuitHead': ('머리가 포함된 전신 의복', 'full suit with headwear'),
    'FullTop': ('상체 의복', 'full upper clothing'), 'BathRobe': ('가운', 'robe'),
    'Torso1': ('상체 내의', 'upper long underwear'), 'Torso1Legs1': ('전신 내의', 'long underwear'),
    'Legs1': ('하체 내의', 'lower long underwear'), 'Belt': ('허리띠', 'belt'),
    'BeltExtra': ('허리 부착물', 'belt accessory'), 'AmmoStrap': ('탄약 띠', 'ammunition strap'),
    'Tail': ('꼬리 부착물', 'tail accessory'),
    'MakeUp_FullFace': ('얼굴 분장', 'face makeup'), 'MakeUp_Eyes': ('눈가 분장', 'eye makeup'),
    'MakeUp_EyesShadow': ('아이섀도', 'eye shadow'), 'MakeUp_Lips': ('입술 분장', 'lip makeup'),
}

BAKING = 'The selected supported dough or batter recipe must accept its exact ingredients, kept utensils and containers. Learn it where its declaration requires learning, and do not drive while crafting.'

BOX_PACKING = 'Provide the exact ammunition, nails, screws or paperclips and count in the selected box-packing recipe, satisfy recipe eligibility and do not drive. These reviewed recipes have one input clause and no empty-box input, kept tool or callback. RecipeManager owns consumption and creation of the declared box; unpacking is a separate recipe and does not by itself prove this packing route.'

QUALIFIERS[JAR_BOX_OPENING] = ('병 상자 개봉 제조법은 빈 병 6개와 시간 15를 지정하며 콜백은 인벤토리에 병뚜껑 6개를 추가하도록 요청한다. 제작 조건을 만족하고 운전 중이 아니어야 한다. 실제 결과 수량 전달과 물품 생성은 엔진 처리에 달려 있다.', JAR_BOX_OPENING)

QUALIFIERS[EGG_CARTON_OPENING] = ('달걀 포장 개봉 조건을 만족하고 운전 중이 아니어야 한다. 콜백은 첫 입력의 신선도 경과값을 전달된 결과에 복사하므로 새것으로 되돌리지 않는다. 입력·결과 인수 선택과 실제 결과 전달은 엔진 처리에 달려 있다.', EGG_CARTON_OPENING)

QUALIFIERS[PRODUCE_SACK_OPENING] = ('농산물 자루 개봉 조건을 만족하고 운전 중이 아니어야 한다. 콜백은 첫 입력의 신선도 경과값을 결과에 복사하고 빈 자루 한 개를 추가하도록 요청한다. 실제 인수 선택·결과 전달은 엔진 처리에 달려 있으며 이 동작은 재포장 경로를 뜻하지 않는다.', PRODUCE_SACK_OPENING)

BOWL_PORTIONING = 'Provide a listed soup, stew, rice or pasta vessel and two or four bowls in the exact portioning recipe, satisfy eligibility and do not drive. SliceCooked accepts the supplied Food argument when cooked OR burnt and accepts a non-Food argument; nil fails. The callback divides hunger, unmodified thirst/mood and nutrition values by the portion count and copies taint. Stew for two uses base hunger for both hunger values. Soup/rice/pasta return a pot or saucepan with the source condition; stew adds a pot without copying condition. The callback does not explicitly copy age, cooked or burnt state. Native selected-argument, result delivery/count and other food-state propagation remain separate.'

FUNCTIONS.update({
    'pack_into_box': ('box packing', '지정 수량을 모아 상자로 포장할 수 있다.', 'The specified quantity can be packed into a box.'),
    'portion_into_bowls': ('food portioning', '냄비 음식을 여러 그릇으로 나눌 수 있다.', 'The prepared vessel contents can be divided into bowls.'),
    'receive_portioned_food': ('food portioning', '음식을 나누어 담는 그릇으로 쓸 수 있다.', 'It can serve as a bowl for portioning prepared food.'),
})

QUALIFIERS[BOX_PACKING] = ('지정 탄약·못·나사·클립을 제조법의 수량만큼 준비하고 제작 조건을 만족해야 하며 운전 중에는 제작할 수 없다. 이 포장법은 빈 상자나 도구를 별도 재료로 요구하지 않고 콜백도 없다. 실제 소비와 상자 생성은 엔진의 제조법 처리에 따른다.', BOX_PACKING)

QUALIFIERS[BOWL_PORTIONING] = ('지정 냄비 음식과 그릇 2개 또는 4개를 준비하고 제작 조건을 만족해야 하며 운전 중에는 제작할 수 없다. 음식 인수를 검사할 때 익었거나 탄 상태를 허용한다. 콜백은 배고픔·갈증·기분·영양 값을 분량 수로 나누고 오염 여부를 복사한다. 2인분 스튜는 현재 배고픔 값에도 기본 값을 사용한다. 수프·밥·파스타는 원래 상태의 냄비나 소스팬을 돌려주고 스튜는 상태를 복사하지 않은 냄비를 만든다. 신선도·익음·탐의 복사는 이 콜백에서 확정하지 않는다.', BOWL_PORTIONING)

SEED_PACKING = 'The exact seed-packing recipe requires fifty of the named seeds and creates their corresponding packet, with Time 10 and Category Farming. It declares no empty-packet input, tool or callback. ISCraftAction requires native recipe eligibility and disallows crafting while driving. Actual consumption and result delivery remain native.'

JAR_PREPARATION = 'The exact recipe supplies an EmptyJar, JarLid, the specified vegetable count, Water=10, Vinegar=2 and the Sugar recipe group with raw suffix ;1. It uses Time 100, Category Cooking and Cooking10 XP callback. Native eligibility and consumption apply; crafting while driving is disallowed. CannedFood selects the Food participant with greatest raw Age and copies that participant Age, OffAge and OffAgeMax to the jar result, without filtering for the vegetable type. Jarring alone does not establish prolonged preservation; the separately bound cooking callback changes aging thresholds while preserving relative age. The raw sugar suffix is not rewritten as an equals count.'

QUALIFIERS[SEED_PACKING] = ('지정 씨앗 50개를 해당 봉지로 포장하는 제조법이며 빈 봉지나 도구·콜백은 요구하지 않는다. 시간 10과 농사 분류를 사용하고 운전 중에는 제작할 수 없다. 실제 소비와 결과물 생성은 엔진의 제조법 처리에 따른다.', SEED_PACKING)

QUALIFIERS[JAR_PREPARATION] = ('빈 병·뚜껑·지정 채소 수량·물 10·식초 2와 설탕 그룹의 원문 ;1 조건을 요구한다. 시간 100, 요리 분류와 Cooking10 경험치 콜백을 사용하고 운전 중에는 만들 수 없다. 콜백은 채소 종류를 가리지 않고 Food 재료 중 Age가 가장 큰 것을 골라 신선도와 부패 기준을 결과에 복사한다. 병에 담는 것만으로 보존 기간이 늘어나지는 않으며 가열 콜백은 별도다. 설탕의 세미콜론 표기를 등호 수량으로 바꾸지 않는다.', JAR_PREPARATION)

RADIO_VOLUME = 'lua/client/RadioCom/RadioWindowModules/RWMVolume.lua'

RADIO_PANEL = 'lua/client/RadioCom/RadioWindowModules/RWMPanel.lua'

RADIO_WINDOW = 'lua/client/RadioCom/ISRadioWindow.lua'

RADIO_ACTION = 'lua/client/RadioCom/ISRadioAction.lua'

CLOCK_PROMPT = 'lua/client/ISUI/ISButtonPrompt.lua'

CLOCK_CHARACTER = 'lua/client/XpSystem/ISUI/ISCharacterScreen.lua'

CLEAN_BLOOD = 'lua/client/TimedActions/ISCleanBlood.lua'

CLEAN_CURSOR = 'lua/server/BuildingObjects/ISCleanBloodCursor.lua'

CLOTHING_EXTRA = 'lua/client/TimedActions/ISClothingExtraAction.lua'

CONTEXT_MANAGER = 'lua/client/Context/ISContextManager.lua'

CONTEXT_INVENTORY = 'lua/client/Context/ISMenuContextInventory.lua'

CONTEXT_LOADER = 'lua/client/Context/ISMenuContext.lua'

CONTEXT_ELEMENT = 'lua/client/Context/ISMenuElement.lua'

CONTEXT_RADIO = 'lua/client/Context/Inventory/InvContextRadio.lua'

CONTEXT_MOVABLE = 'lua/client/Context/Inventory/InvContextMovable.lua'

CONTEXT_MEDIA = 'lua/client/Context/Inventory/InvContextMedia.lua'

CONTEXT_DELETE = 'lua/client/DebugUIs/ISRemoveItemTool.lua'

MEDIA_INFO = 'lua/client/RecordedMedia/ISMediaInfo.lua'

MEDIA_LOADER = 'lua/shared/RecordedMedia/ISRecordeMedia.lua'

MEDIA_DATA = 'lua/shared/RecordedMedia/recorded_media.lua'

RADIO_CHANNEL = 'lua/client/RadioCom/RadioWindowModules/RWMChannel.lua'

TV_CHANNEL = 'lua/client/RadioCom/RadioWindowModules/RWMChannelTV.lua'

RADIO_MEDIA = 'lua/client/RadioCom/RadioWindowModules/RWMMedia.lua'

RADIO_SIGNAL = 'lua/client/RadioCom/RadioWindowModules/RWMSignal.lua'

RADIO_MIC = 'lua/client/RadioCom/RadioWindowModules/RWMMicrophone.lua'

RADIO_INTERACTIONS = 'lua/client/RadioCom/ISRadioInteractions.lua'

RADIO_POWER = 'lua/client/RadioCom/RadioWindowModules/RWMPower.lua'

RADIO_GRID = 'lua/client/RadioCom/RadioWindowModules/RWMGridPower.lua'

HOTBAR = 'lua/client/Hotbar/ISHotbar.lua'

HOTBAR_SLOTS = 'lua/client/Hotbar/ISHotbarAttachDefinition.lua'

HOTBAR_ATTACH = 'lua/client/TimedActions/ISAttachItemHotbar.lua'

DRY_BODY = 'lua/client/TimedActions/ISDryMyself.lua'

CLEAR_ASHES = 'lua/client/TimedActions/ISClearAshes.lua'

NAME_DIALOG = 'lua/client/ISUI/ISTextBox.lua'

CONSOLIDATE = 'lua/client/TimedActions/ISConsolidateDrainable.lua'

MEDICAL_CONSOLIDATION = 'Select one drainable item for which native canConsolidate permits the operation. Choose another not-full item returned by the inventory same-type lookup, excluding receivers already in the water-pour list. Both items must remain in inventory. The action transfers at most the donor remaining fraction or the receiver free fraction, updates both as it progresses, and interrupts on walking or running. A depleted donor is passed to Use; exact native eligibility, lookup and depleted-form interpretation remain separate.'

FUNCTIONS['consolidate_drainable_supplies'] = ('supply consolidation', '같은 유형의 소모품으로 남은 양을 모을 수 있다.', 'Remaining supply can be consolidated into another item of the same type.')

QUALIFIERS[MEDICAL_CONSOLIDATION] = ('합치기가 허용되는 물품 하나를 선택하고, 같은 유형으로 조회되는 물품 중 가득 차지 않은 대상을 고른다. 물 붓기 목록에 이미 있는 대상은 제외한다. 두 물품을 소지해야 하며 남은 양과 받을 여유 중 작은 만큼 진행에 따라 옮긴다. 걷거나 달리면 중단되며, 비워진 원본은 소모 처리가 적용된다.', 'Select one item for which consolidation is permitted and choose a not-full receiver found by the same-type lookup, excluding receivers already listed for pouring water. Keep both items in inventory. Supply moves progressively up to the smaller of donor remainder and receiver space; walking or running interrupts. An emptied donor receives depletion processing.')

DISINFECTION_ADMIN_PAIN = 'In the supplied disinfection action, additional pain is changed only when the treating character access level is not None. That branch sets doctor level to 10, so the added pain is AlcoholPower times 13 minus 5. This is not the ordinary-player branch.'

EFFECTS[('wound_alcohol_level', 'increase')] = ('상처에 적용된 알코올 수치를 높인다.', 'It increases the alcohol level applied to the wound.')

EFFECTS[('additional_pain', 'increase')] = ('추가 통증 수치를 높인다.', 'It increases additional pain.')

QUALIFIERS[DISINFECTION_ADMIN_PAIN] = ('제공된 소독 동작에서는 치료자가 일반 플레이어 외의 접근 권한을 가진 경우에만 추가 통증이 변한다. 이 분기에서 적용하는 추가량은 해당 물품의 알코올 강도와 고정된 치료 기술 수준으로 계산한다.', 'In the supplied disinfection action, additional pain changes only for a treating character with nonordinary access privileges. That branch calculates the added amount from this item alcohol power and its fixed doctor level.')

BANDAGE_APPLICATION = 'The Health panel selects positive BandagePower for an injured, stitched or splinted part that is not bandaged. The separate inventory menu requires every selected item to be CanBandage and uses only the first actual item: scratches, deep wounds, bites, stitches or bleeding qualify regardless of current bandaging, while only the burnt branch checks not-bandaged because of Lua operator precedence. Transfer the material to doctor inventory and retain it; the action does not recheck injury or existing bandaging. Application removes the material. Running interrupts, and walking interrupts for body-part indices below the groin. A different patient moving invalidates treatment when driving or outside a vehicle; self-treatment and vehicle passengers have movement exceptions.'

BANDAGE_REMOVAL = 'After this material has been applied, select its bandaged body part and use the Health-panel removal option. The action requires that part to remain bandaged and applies the same patient-movement, running and lower-body walking restrictions. It clears the bandaged state and requests an item of the recorded bandage type; depleted bandage life additionally calls Use on that returned item. The exact returned/depleted form is a separate native creation/Use boundary.'

FUNCTIONS['remove_applied_bandage'] = ('bandage removal', '감아 둔 붕대는 건강 패널에서 제거할 수 있다.', 'An applied bandage can be removed through the Health panel.')

QUALIFIERS.update({
    BANDAGE_REMOVAL: ('이 재료로 감아 둔 부위의 붕대 제거 메뉴를 사용한다. 붕대가 감긴 상태여야 하며 환자 이동·달리기·하체 치료 중 걷기에 같은 제한이 적용된다. 붕대 상태를 해제하고 기록된 붕대 종류의 물품을 돌려주는 경로를 사용한다. 수명이 다한 붕대는 추가 소모 처리가 있어 반환되는 정확한 형태를 별도로 확인해야 한다.', 'Use the remove-bandage option for a part bandaged with this material. It must remain bandaged; the same patient-movement, running and lower-body walking restrictions apply. The action clears bandaged state and requests an item of the recorded type. Depleted bandages receive additional use processing, so the exact returned form remains separate.'),
})

QUALIFIERS[SPLINTING] = ('건강 메뉴에서 머리·몸통을 제외한 골절 상처에 부목을 댄다. 봉합·기존 부목은 제외하고 완성 부목 또는 판자·나뭇가지·막대와 정확한 RippedSheets를 쓴다. 앞선 검사 동작이 상처와 재료 선택지를 확인하며 끌어놓기의 반대 조건을 정상 성공 경로로 간주하지 않는다. 재료를 옮긴 뒤 동작은 환자 이동을 검사하고 천·지지대 조합만 계속 소지를 확인한다. 걷거나 뛰면 중단된다. 완료 시 부목 계수는 의료 수준에 1을 더해 2로 나눈 값이며 허용된 부위에 의료 경험치 15를 주고 재료를 소모해 지지대 종류를 기록한다. 관리자 의료 수준은 10이고 실제 골절 회복은 엔진에 남는다.', SPLINTING)

QUALIFIERS[SPLINT_REMOVAL] = ('건강 패널에서 부목 계수가 양수인 부위의 제거를 선택한다. 앞선 검사 후 동작은 환자 이동만 확인하며 부목 상태는 재검사하지 않는다. 걷거나 뛰면 중단된다. 기록된 지지대 종류를 생성하고 그것이 Base.Splint가 아니면 RippedSheets도 생성한 뒤 부목 상태와 계수를 해제한다. 원래 물품 상태 보존이나 골절 회복을 보장하지 않는다.', SPLINT_REMOVAL)

FUNCTIONS['remove_applied_splint'] = ('splint removal', '적용해 둔 부목을 제거하고 재료를 돌려받는 동작을 할 수 있다.', 'An applied splint can be removed through an action that returns its materials.')

EFFECTS[('splint_factor', 'set_doctor_half')] = ('부목 계수를 의료 수준에 1을 더해 2로 나눈 값으로 설정한다.', 'It sets splint factor to (Doctor level + 1) / 2.')

BANDAGE_ITEMS = {'Base.' + name for name in ('Bandage', 'BandageDirty', 'AlcoholBandage', 'Bandaid',
    'RippedSheets', 'RippedSheetsDirty', 'AlcoholRippedSheets', 'DenimStrips', 'DenimStripsDirty', 'LeatherStrips', 'LeatherStripsDirty')}

PILL_ITEMS = {'Base.' + name for name in ('Pills', 'PillsAntiDep', 'PillsBeta', 'PillsSleepingTablets', 'PillsVitamins')}

BANDAGE_LIFE = 'Only successful application of a material without Dirty in its exact type name: bandage life is ZombRandFloat((Doctor level + 1) * 0.5, (Doctor level + 1) * 1.0) plus native BandagePower. Instant timed actions force the doctor level to ten. Dirty types override life to zero. Doctor XP five is added only when the body part permits bandage XP and computed life is positive. SetBandaged records life, native isAlcoholic and material FullType; actual healing/aging remains native.'

BANDAGE_INFECTION = 'Only application when the supplied material native isInfected flag is true calls bodyPart.SetInfected(true). A Dirty type name only forces zero bandage life and does not establish that infected flag. Injury eligibility, inventory retention and treatment interruption conditions still apply.'

BANDAGE_PANIC = 'At completion of either bandage application or removal, the treating character with Hemophobic receives current panic plus fifty only when the treated body part bleeding time is positive. The treatment guards and interruptions still apply; native panic limits remain separate.'

BURN_CLEANING = 'The Health panel requires BandagePower at least two, an injured/stitched/splinted unbandaged body part and needBurnWash. Transfer the chosen material first. The action only rechecks patient movement, not material possession or burn state; walking/running interrupts. Completion adds ten Doctor XP, adds 60 minus doctor level to additional pain, clears needBurnWash and calls Use on the material. Non-None access sets doctor level ten for the pain calculation; instant actions shorten time without themselves changing that level. A Hemophobic treating character gains fifty panic regardless of bleeding. This does not prove the burn heals.'

BANDAGE_WASHING = 'At a selected water object outside the washer/dryer branches, at least one water unit and an exact dirty bandage/fabric type with its named cleaning recipe are required. Tainted water disables the menu only when EnableTaintedWaterText is enabled. Transfer the item and approach the water object. The timed action requires the item directly in inventory and source hasWater, not recipe eligibility or a repeated taint check; walking/running interrupts. Completion removes the old item, creates recipe.getResult().getType(), preserves its occupied hands and sends a one-unit water command. No condition, favorite or infection flag is explicitly copied. This direct water-object action does not invoke the recipe OnTest callback.'

BANDAGE_RECIPE_WASHING = 'The exact Clean Bandage/Rag/Denim Strips/Leather Strips recipe supplies its named dirty form and Water, uses Time 40 and Category Health, and returns the corresponding clean form. NotTaintedWater rejects a participant only if it is a water source and is tainted. Native recipe eligibility, consumption and output delivery apply; crafting while driving is disallowed. Unlike the separate water-object action, this recipe declares OnTest and does not merely rely on the tainted-water-text option.'

BANDAGE_OR_BURN_PANIC = 'Only a Hemophobic treating character gains fifty panic. For bandage application or removal the treated part bleeding time must be positive; for successful burn cleaning there is no bleeding requirement. Each route retains its own eligibility, patient-movement and interruption conditions. Native panic limits remain separate.'

PILL_TAKING = 'All selected types must start with the case-sensitive Pills prefix; only the first actual item is taken. Transfer it to main inventory, retain it throughout the action and wait for the queued 165-time action. Running interrupts while walking does not. Completion calls BodyDamage.JustTookPill with that exact item; the Lua action does not itself reduce pain, panic, unhappiness or fatigue, induce sleep or call Use. Native medication and depletion behavior remain separate.'

QUALIFIERS[BANDAGE_APPLICATION] = ('건강 패널은 양수 붕대 강도와 아직 붕대가 없는 상처·봉합·부목 부위를 요구한다. 별도 소지품 메뉴는 선택 물품 모두가 붕대 가능해야 하고 첫 물품만 사용한다. 그 메뉴의 긁힘·깊은 상처·물림·봉합·출혈 분기는 이미 감긴 붕대 여부를 제한하지 않으며 화상 분기에만 미착용 조건이 붙는다. 재료를 치료자에게 옮겨 소지하고 적용하면 소모한다. 동작은 상처·붕대 상태를 다시 검사하지 않는다. 달리기와 하체 치료 중 걷기는 중단하며 다른 환자 이동에는 차량·자가 치료 예외가 있다.', BANDAGE_APPLICATION)

QUALIFIERS.update({
    BANDAGE_LIFE: ('더러운 유형이 아닌 재료를 적용할 때 붕대 수명은 의료 수준에 1을 더한 값의 0.5~1배 무작위 값과 붕대 강도의 합이다. 즉시 동작은 의료 수준을 10으로 처리한다. 더러운 유형은 수명을 0으로 덮어쓴다. 해당 부위가 경험치를 허용하고 수명이 양수일 때만 의료 경험치 5를 준다. 실제 치유·경과와 알코올 상태 해석은 엔진에 남는다.', BANDAGE_LIFE),
    BANDAGE_INFECTION: ('적용 재료의 실제 감염 플래그가 참일 때만 부위를 감염 상태로 설정한다. 더러운 이름은 수명을 0으로 만들 뿐 감염 플래그를 증명하지 않는다. 적용·소지·치료 중단 조건이 함께 적용된다.', BANDAGE_INFECTION),
    BANDAGE_PANIC: ('붕대 적용 또는 제거 완료 시 치료자에게 혈액공포증이 있고 해당 부위의 출혈 시간이 양수이면 치료자의 공포에 50을 더한다. 치료 조건과 중단 규칙이 적용되며 공포 상한은 엔진 처리에 남는다.', BANDAGE_PANIC),
    BURN_CLEANING: ('붕대 강도 2 이상 재료와 씻을 필요가 있는 미붕대 상처·봉합·부목 부위를 요구하고 재료를 옮긴다. 동작은 환자 이동만 다시 검사하며 재료·화상 상태는 재검사하지 않는다. 걷거나 뛰면 중단된다. 완료 시 의료 경험치 10, 추가 통증에 60에서 의료 수준을 뺀 값, 세척 필요 해제와 재료 Use를 적용한다. 관리자 수준은 통증 계산에서 의료 10을 사용하며 혈액공포증 치료자는 출혈과 무관하게 공포 50을 받는다. 화상 치유를 보장하지 않는다.', BURN_CLEANING),
    BANDAGE_WASHING: ('세탁기·건조기 경로 밖의 물체에서 물 1 이상과 지정 더러운 붕대·천 및 세척 제조법이 필요하다. 오염수는 오염 표시 설정이 켜졌을 때 메뉴를 막는다. 재료를 옮기고 물체에 접근한다. 동작은 직접 소지와 남은 물만 확인하며 제조법 유효성·오염을 재검사하지 않는다. 걷거나 뛰면 중단된다. 완료 시 이전 물품을 없애고 제조법 결과 종류의 새 물품으로 바꾸며 손 점유를 유지하고 물 1 사용을 요청한다. 상태·즐겨찾기·감염 복사와 OnTest 실행은 없다.', BANDAGE_WASHING),
    PILL_TAKING: ('선택한 모든 물품의 종류가 Pills로 시작해야 하고 첫 물품만 복용한다. 주 인벤토리로 옮겨 계속 소지하며 시간 165 동작을 진행한다. 뛰면 중단되고 걷기는 허용된다. 완료 시 정확한 물품으로 엔진의 JustTookPill을 호출하며 효과·수면·소모를 이 Lua 코드가 직접 계산하지 않는다.', PILL_TAKING),
})

QUALIFIERS[BANDAGE_RECIPE_WASHING] = ('해당 더러운 붕대·천과 물을 쓰는 시간 40의 의료 제조법이다. OnTest는 물 공급원인 재료가 오염되었으면 거부한다. 엔진의 제작 조건·소모·결과 처리가 필요하며 운전 중에는 만들 수 없다. 별도 물체 세척 동작과 달리 오염수 표시 설정에만 의존하지 않는다.', BANDAGE_RECIPE_WASHING)

QUALIFIERS[BANDAGE_OR_BURN_PANIC] = ('혈액공포증이 있는 치료자만 공포 50을 받는다. 붕대 적용·제거에서는 해당 부위 출혈 시간이 양수여야 하지만 화상 세척에서는 출혈을 요구하지 않는다. 각 경로의 치료·환자 이동·중단 조건을 따르며 공포 상한은 엔진에 남는다.', BANDAGE_OR_BURN_PANIC)

FUNCTIONS.update({'clean_burn': ('burn cleaning', '씻어야 하는 화상 부위를 처리하는 재료로 쓸 수 있다.', 'It can be used as a material for cleaning a burn that requires washing.'),
                  'wash_bandaging_material': ('bandage cleaning', '물체의 물을 사용해 더러운 붕대·천을 세척하는 동작을 할 수 있다.', 'Its dirty bandage or fabric form can be cleaned using water from an object.')})

EFFECTS.update({
    ('applied_bandage_life', 'set_skill_random_plus_power'): ('의료 수준과 재료의 붕대 강도로 적용 수명을 계산한다.', 'Applied bandage life is calculated from Doctor level and material bandage power.'),
    ('bandage_patient_infection', 'set_true'): ('해당 부위를 감염 상태로 설정한다.', 'It sets the treated body part infected.'),
    ('treatment_panic', 'add_50'): ('치료자의 공포 수치에 50을 더한다.', 'It adds fifty to the treating character panic.'),
    ('burn_wash_requirement', 'clear'): ('화상 세척 필요 상태를 해제한다.', 'It clears the need-to-wash-burn state.'),
    ('additional_pain', 'add_60_minus_doctor_level'): ('추가 통증에 60에서 의료 수준을 뺀 값을 더한다.', 'It adds sixty minus Doctor level to additional pain.'),
    ('doctor_experience', 'add_10'): ('의료 경험치 10을 추가한다.', 'It adds ten Doctor XP.'),
})

BANDAGE_MATERIALS = 'Provide the specified cloth or cotton and disinfectant, liquor or water-filled cooking vessel in the selected bandaging-material recipe. The source distinguishes input and destroyed material and retains its raw quantity and heat requirements. Recipe eligibility must hold and the character must not drive. This input role does not guarantee the resulting sterilized form, chemical efficacy or a boiling temperature.'

QUALIFIERS[BANDAGE_MATERIALS] = ('선택한 붕대·소독솜 준비법에서 천이나 솜과 지정된 소독제·술 또는 물이 든 조리용기를 제공한다. 해당 재료·수량·온도 조건에 맞아야 하며 운전 중에는 제작할 수 없다. 이 재료 역할만으로 소독 결과나 끓는 온도를 보장하지는 않는다.', 'Supply the cloth or cotton and the specified disinfectant, liquor or water-filled cooking vessel for the selected bandaging-material recipe. Its material, quantity and heat requirements must be met, and crafting is unavailable while driving. This input role alone does not guarantee sterilization or boiling temperature.')

RENAME_ITEM = 'The inventory menu offers renaming for a selected inventory container, key, KeyRing or map. Confirm a nonempty name that passes the callback length limit (Lua internal-text length at most 28). The callback changes the item name and refreshes inventory displays; it does not change contents or type and imposes no timed-action walking or running condition.'

FUNCTIONS['rename_selected_item'] = ('item naming', '메뉴에서 물품의 이름을 바꿀 수 있다.', 'Its item name can be changed through the menu.')

FUNCTIONS['wear_container_on_back'] = ('back container', '가방을 등에 메어 착용할 수 있다.', 'The container can be worn on the back.')

FUNCTIONS['plumb_external_water'] = ('plumbing', '배관 가능한 물체를 외부 수원 사용 상태로 설정하는 데 쓸 수 있다.', 'It can be used to set an eligible object to use an external water source.')

for _name, _ko, _en in (('barbell_curl', '바벨 컬', 'barbell curls'), ('dumbbell_press', '덤벨 프레스', 'dumbbell presses'), ('biceps_curl', '바이셉스 컬', 'biceps curls')):
    FUNCTIONS['exercise_' + _name] = ('weight exercise', _ko + ' 운동에 사용할 수 있다.', 'It can be used for ' + _en + '.')

QUALIFIERS[RENAME_ITEM] = ('이름 바꾸기를 지원하는 물품을 선택하고 빈칸이 아닌 이름을 확인해야 한다. 게임의 이름 길이 제한을 통과해야 하며 내용물이나 물품 종류는 바뀌지 않는다.', 'Select an item that supports renaming and confirm a nonempty name within the game name-length limit. This does not change its contents or item type.')

BODY_DRYING = 'The selected dishcloth or bath towel is transferred to main inventory. Body wetness and towel remaining uses must stay positive and the towel must stay in inventory. The action periodically reduces body wetness and spends towel uses, with another use at completion. Walking or running interrupts; complete dryness is not guaranteed.'

ASH_CLEARING = 'The world menu requires an unbroken tool tagged ClearAshes in accessible inventory and a targeted burnt-floor ash object. The callback walks adjacent and equips a qualifying tool before removal. Walking or running interrupts. The supplied action does not continuously recheck the tool tag or inventory membership; removal targets that ash object, not arbitrary dirt or blood.'

FUNCTIONS.update({
    'clear_burnt_floor_ashes': ('ash clearing', '불탄 바닥의 재를 치울 때 쓸 수 있다.', 'It can be used to clear burnt-floor ashes.'),
})

QUALIFIERS.update({
    BODY_DRYING: ('몸이 젖어 있고 수건의 사용량이 남아 있어야 한다. 수건을 주 소지품으로 옮기고 동작 중에도 소지해야 한다. 몸의 물기를 줄이면서 수건을 소모하며 완료 시에도 한 번 사용한다. 걷거나 달리면 중단되고 완전히 마르는 것은 보장되지 않는다.', 'The body must be wet and the towel must have uses remaining. It is moved to main inventory and must remain there. Drying reduces body wetness while spending towel uses, including one at completion. Walking or running interrupts; complete dryness is not guaranteed.'),
    ASH_CLEARING: ('불탄 바닥의 재를 대상으로, 재 청소가 가능한 파손되지 않은 도구가 소지품에 있어야 메뉴가 열린다. 재 옆으로 이동해 적합한 도구를 장비한 뒤 치우며 걷거나 달리면 중단된다. 다른 오염이나 혈흔의 청소와는 별도 기능이다.', 'Target burnt-floor ashes with an unbroken ash-clearing tool in accessible inventory to open the menu. Move adjacent and equip a qualifying tool before clearing; walking or running interrupts. This is separate from cleaning other dirt or blood.'),
})

SLOT_USE = 'Wear the slot-providing item without holding it in either hand. The registered slot accepts only matching attachment types; the inventory attachment menu requires an unbroken item that is not already attached and is not excluded by worn-item replacements. The attached item must remain in inventory during the action; running interrupts. Replacing an occupied slot detaches its previous item, and removing the provider removes its slots and their attachments.'

FUNCTIONS.update({
    'provide_belt_slots': ('belt attachment slots', '착용하면 좌우 벨트 부착 슬롯을 제공한다.', 'When worn, it provides left and right belt attachment slots.'),
    'provide_right_holster_slot': ('holster attachment slot', '착용하면 오른쪽 홀스터 부착 슬롯을 제공한다.', 'When worn, it provides a right holster attachment slot.'),
    'provide_paired_holster_slots': ('holster attachment slots', '착용하면 좌우 홀스터 부착 슬롯을 제공한다.', 'When worn, it provides left and right holster attachment slots.'),
})

QUALIFIERS[SLOT_USE] = ('손에 들지 않고 착용해야 슬롯이 생긴다. 슬롯과 맞는 유형의 파손되지 않은 물품을 장착하며, 이미 부착된 물품이나 다른 착용물의 제한에 걸린 물품은 장착 메뉴에서 제외된다. 장착할 물품은 동작 중 소지품에 있어야 하고 달리면 중단된다. 슬롯을 교체하면 이전 물품이 분리되며 슬롯 제공 물품을 벗으면 해당 슬롯의 부착도 해제된다.', 'Wear the provider without holding it in either hand. Attach an unbroken item of a matching type; already-attached items and worn-item exclusions are unavailable in the attachment menu. The item must remain in inventory during attachment; running interrupts. Replacing a slot detaches its previous item, and removing the provider removes its slots and attachments.')

DEVICE_POWER = 'The device and character must be valid and reachable. Its power toggle is allowed when a battery-powered device has positive power, or the device can be powered at its current location. Running interrupts.'

BATTERY_INSERT = 'The device must support batteries and have an empty battery slot. The battery control accepts Base.Battery and selects an offered battery with positive remaining delta. The character/device and required world or vehicle access must remain valid; running interrupts.'

BATTERY_REMOVE = 'The device must support batteries and have an installed battery, with a valid character inventory and required device access. Running interrupts. The action retrieves the installed battery through the device into the character inventory.'

FUNCTIONS.update({
    'toggle_device_power': ('device power', '기기의 전원을 켜거나 끌 수 있다.', 'Its device power can be turned on or off.'),
    'insert_device_battery': ('device battery', '기기의 빈 배터리 칸에 배터리를 넣을 수 있다.', 'A battery can be inserted into its empty battery slot.'),
    'remove_device_battery': ('device battery', '기기에 장착된 배터리를 꺼낼 수 있다.', 'Its installed battery can be removed.'),
    'use_as_radio_battery': ('radio battery', '배터리를 사용하는 기기의 빈 칸에 넣어 쓸 수 있다.', 'It can be inserted into the empty slot of a battery-powered device.'),
})

QUALIFIERS.update({
    DEVICE_POWER: ('접근 가능한 지원 기기에서, 배터리형이면 전력이 남아 있거나 현재 위치에서 전원을 공급받을 수 있어야 한다. 달리면 동작이 중단된다.', 'Use a reachable supported device. Either a battery-powered device must have remaining power, or the device must be powerable at its current location. Running interrupts.'),
    BATTERY_INSERT: ('배터리형 기기의 칸이 비어 있어야 한다. 제공한 배터리 중 남은 양이 있는 배터리를 골라 넣으며 캐릭터·기기와 월드·차량 접근 조건이 유효해야 한다. 달리면 중단된다.', 'The battery-powered device slot must be empty. An offered battery with remaining charge is selected, and character/device plus world or vehicle access must be valid. Running interrupts.'),
    BATTERY_REMOVE: ('배터리형 기기에 배터리가 장착되어 있고 캐릭터의 소지품과 기기 접근 조건이 유효해야 한다. 달리면 중단되며 꺼낸 배터리는 캐릭터의 소지품으로 전달된다.', 'The battery-powered device must have a battery installed, with valid character inventory and device access. Running interrupts; the retrieved battery is passed into character inventory.'),
})

MIC_CONTROL = 'A two-way device exposes its microphone mute control. The device and character must be valid and reachable; the action changes the mute flag only while the device is on with positive power. Running interrupts. Changing this flag does not establish microphone pickup or radio transmission.'

FUNCTIONS['toggle_radio_microphone'] = ('microphone control', '양방향 기기의 마이크 음소거를 바꿀 수 있다.', 'The two-way device microphone can be muted or unmuted.')

QUALIFIERS[MIC_CONTROL] = ('양방향 기기의 유효한 마이크 조작에서 접근 조건을 충족해야 한다. 기기가 켜져 있고 전력이 남아 있을 때 음소거 상태를 바꾸며 달리면 중단된다. 마이크 입력이나 신호 송신 자체를 보장하지 않는다.', 'Use the reachable two-way device microphone control with a valid character/device. It changes mute state only while the device is on with positive power; running interrupts. Microphone pickup and radio transmission are not guaranteed.')

DEVICE_PANEL = 'Outside Tutorial mode, the inventory radio handler opens device controls for an item held in either hand, or for a floor entry linked by RadioItemID to an IsoRadio on that square. The radio window requires a player, recognized device object and device data. Opening controls does not establish signal reception or transmission.'

RADIO_TUNING = 'The nontelevision, non-NoTransmit channel panel needs a valid selected preset. Reach the device as required by its inventory/world/vehicle placement. The timed action sets the preset frequency only while the device is on with positive power; running interrupts. Setting a channel does not guarantee reception or transmission.'

TV_TUNING = 'The television channel panel needs a valid selected preset and access to its device. The timed action sets the selected frequency only while the device is on with positive power; running interrupts. Selecting a channel does not establish a received television program.'

DEVICE_VOLUME = 'Use the device volume controls with valid device data and required access. The timed action needs an on device with positive power; muting requires positive volume, and unmuting requires nonpositive volume. Running interrupts. The control sets device volume without guaranteeing audible output.'

MEDIA_LABEL = 'For an item with a registered media category, label reading is available only when it is recorded media in the player main inventory and its assigned media data has translated extra text. The panel displays that text; category declaration alone does not supply a recording, its contents or its effects.'

MEDIA_INSERT = 'The item must currently be recorded media and its media type must match a device with a supported media panel. The device slot must be empty, required world/vehicle access must hold, and running interrupts. The action hands the item to DeviceData.addMediaItem; playback, recording assignment and audiovisual or learning effects remain separate.'

FUNCTIONS.update({
    'open_device_controls': ('device controls', '지원되는 기기 조작 창을 열 수 있다.', 'Its supported device control panel can be opened.'),
    'tune_radio': ('radio tuning', '등록된 채널로 라디오 주파수를 맞출 수 있다.', 'It can be tuned to a selected preset radio frequency.'),
    'select_tv_channel': ('television channel', '등록된 TV 채널을 선택할 수 있다.', 'A preset television channel can be selected.'),
    'adjust_device_volume': ('device volume', '기기 음량을 조절하거나 음소거를 바꿀 수 있다.', 'Its device volume can be adjusted or muted/unmuted.'),
    'read_recorded_media_label': ('recording label', '배정된 녹음·영상의 안내 문구를 읽을 수 있다.', 'The information text of its assigned recording can be read.'),
    'insert_recorded_media': ('media insertion', '같은 미디어 유형을 받는 기기에 넣는 조작을 할 수 있다.', 'It can be submitted to a device that accepts the same media type.'),
})

QUALIFIERS.update({
    DEVICE_PANEL: ('튜토리얼 외 모드에서 한 손에 든 라디오나 해당 바닥 물품과 연결된 월드 라디오의 조작 창을 열 수 있다. 플레이어와 지원 기기가 있어야 하며 조작 창을 여는 것과 실제 신호 송수신은 별개다.', 'Outside Tutorial mode, controls are available for a radio held in either hand or the world radio linked to its floor item. A player and supported device are required; opening controls is separate from signal reception or transmission.'),
    RADIO_TUNING: ('주파수 조절을 지원하는 TV 외 기기의 유효한 등록 채널을 선택하고 기기에 접근해야 한다. 켜져 있고 전력이 남아 있을 때 주파수를 설정하며 달리면 중단된다. 주파수 설정과 실제 송수신은 별개다.', 'Choose a valid preset on a nontelevision device that supports radio tuning and satisfy device access. It must be on with positive power; running interrupts. Setting the frequency is separate from actual reception or transmission.'),
    TV_TUNING: ('TV의 유효한 등록 채널을 선택하고 기기에 접근해야 한다. 켜져 있고 전력이 남아 있을 때 채널을 설정하며 달리면 중단된다. 채널 선택은 방송 수신 보장이 아니다.', 'Choose a valid television preset and satisfy device access. The action sets its frequency only while on with positive power; running interrupts. Channel selection does not guarantee a received program.'),
    DEVICE_VOLUME: ('접근 가능한 기기가 켜져 있고 전력이 남아 있어야 한다. 음소거는 양의 음량, 해제는 0 이하의 음량에서 가능하며 달리면 중단된다. 기기의 음량 값을 바꾸는 기능으로 실제 소리 출력은 별도다.', 'The accessible device must be on with positive power. Muting requires positive volume; unmuting requires nonpositive volume. Running interrupts. This changes device volume; actual sound output remains separate.'),
    MEDIA_LABEL: ('등록된 미디어 범주의 품목이 실제 기록된 미디어 상태이고 플레이어의 주 소지품에 있어야 한다. 배정된 미디어 데이터에 번역된 안내 문구가 있을 때 표시한다. 범주 지정만으로 녹음·영상의 배정이나 내용·효과를 보장하지 않는다.', 'The item must have recorded-media state, be in the player main inventory, and have assigned media data with translated information text. A registered category alone does not guarantee recording assignment, contents or effects.'),
    MEDIA_INSERT: ('기록이 담긴 매체이며 기기가 받는 미디어 유형과 같아야 한다. 기기의 슬롯이 비어 있고 월드·차량 접근 조건을 충족해야 하며 달리면 중단된다. 삽입만으로 재생 내용이나 시청각·학습 효과가 결정되지는 않는다.', 'The item must contain a recording of the type accepted by the device. Its slot must be empty and world/vehicle access requirements satisfied; running interrupts. Insertion alone does not determine playback content or audiovisual and learning effects.'),
})

CLOTHING_FORM = 'Choose a declared clothing/container variant whose paired menu option and destination declaration are available. The item is transferred to inventory and must remain there; walking or running interrupts. The action replaces the source item with the selected variant and wears it at the destination location. It copies appearance, condition and relevant clothing/container/alarm state; factory/visual availability and the destination wear-menu restrictions still apply. A hat change may first lower a worn hood through its declared DownHoodie option.'

FUNCTIONS['switch_declared_clothing_form'] = ('clothing variants', '지정된 다른 착용 형태로 바꿔 착용할 수 있다.', 'It can be changed to and worn in a declared alternate clothing form.')

QUALIFIERS[CLOTHING_FORM] = ('연결된 메뉴 선택지와 대상 물품 정의가 있는 착용 형태를 선택해야 한다. 물품을 소지품으로 옮기며 동작 중에도 소지해야 하고 걷거나 달리면 중단된다. 원래 물품을 선택한 형태로 교체해 해당 위치에 착용하며 외형·상태와 해당되는 의류·가방·알람 정보를 복사한다. 대상 물품·외형을 만들 수 있어야 하고 착용 메뉴의 제한도 적용된다. 모자 변경은 입고 있는 후드의 내리기 선택지를 먼저 실행할 수 있다.', 'Choose an alternate form with a paired menu option and destination declaration. The item is transferred into inventory and must remain there; walking or running interrupts. It is replaced and worn at the destination location, with appearance, condition and applicable clothing, container and alarm state copied. Destination creation/visual availability and wear-menu restrictions apply. A hat change may first lower a worn hood through its declared option.')

BLOOD_CLEANING = 'Select a square with blood and carry bleach plus a mop, unbroken broom, dish cloth or bath towel. The caller walks adjacent, transfers the selected supplies, and equips the tool by mop/broom/cloth/towel priority. The action still requires bleach and one named cleaning tool in inventory; walking or running interrupts. It reduces the bleach supply and calls removeBlood on that square, not on clothing or body wounds.'

DISINFECTION_USE = 'Wound disinfection spends a use of drainable disinfectant or a portion of a Food disinfectant. The selected form and remaining supply determine depletion.'

FUNCTIONS['clean_world_blood'] = ('blood cleaning', '표백제와 청소 도구를 함께 사용해 월드의 혈흔을 지우는 작업에 쓸 수 있다.', 'It can be used with bleach and a cleaning tool to remove blood from a world square.')

QUALIFIERS[BLOOD_CLEANING] = ('혈흔이 있는 칸을 선택하고 표백제와 대걸레·부서지지 않은 빗자루·행주·목욕 수건 중 하나를 소지해야 한다. 가까이 이동한 뒤 대걸레·빗자루·행주·수건 순으로 도구를 골라 옮기고 장착한다. 동작 중에도 표백제와 해당 청소 도구가 필요하며 걷거나 달리면 중단된다. 표백제 양을 줄이고 해당 월드 칸의 혈흔 제거를 호출하며 의류나 상처 세척은 아니다.', 'Choose a blood-marked square with bleach and a mop, unbroken broom, dish cloth or bath towel. The caller walks adjacent, transfers and equips a tool in that priority order. The action requires bleach and a named tool in inventory; walking or running interrupts. It reduces bleach supply and removes blood from that world square, not clothing or wounds.')

QUALIFIERS[DISINFECTION_USE] = ('상처 소독에는 사용량형 소독제의 사용 횟수나 식품형 소독제의 일부가 소비된다. 소진 여부는 선택한 형태와 남은 양에 따른다.', 'Wound disinfection spends a use of drainable disinfectant or a portion of a food-form disinfectant. Depletion depends on its form and remaining supply.')

FISHING_LURES = 'Registered rod-fishing lure examples include worms, crickets, grasshoppers, cockroaches, bait fish and both fishing-tackle types. These are examples, not a complete list or a guarantee of a catch.'

FISHING_MATCHES = 'In the supplied fish/lure tables, bait fish can match pike, and either artificial fishing-tackle type can match trout, bass and catfish. Pike and bait fish have no artificial-tackle match in those tables. The fishing action selects by the current lure type; fish availability and catch selection still apply, and runtime registry additions are outside this snapshot statement.'

FISHING_LURE_LOSS = 'The rod-fishing action can spend a lure use on a failed attraction according to its registered chanceOfBreak, then clears the secondary hand. The catch routine spends nonplastic bait and clears that hand when it reaches its bait-removal branch. A broken rod line removes the lure from inventory. Plastic tackle skips the routine nonplastic-bait use but is not immune to loss; this does not establish physical durability damage.'

ROD_REPAIR_INPUT = 'The declared Fishing Rod Without line form is an input to the two learned Fix Fishing Rod recipes, with fishing line or twine and a paperclip or nail. It is a line-repair form, not a declaration that the weapon condition equals zero. The supplied fishing UI selects unbroken items carrying a FishingRod or FishingSpear tag; this declaration supplies neither tag.'

QUALIFIERS[ROD_REPAIR_INPUT] = ('낚싯줄이 없는 형태로, 학습한 수리법에서 낚싯줄 또는 끈과 종이클립이나 못을 함께 사용한다. 무기 내구도가 0이라는 뜻은 아니다. 이 형태에는 낚시 도구 선택에 쓰이는 낚싯대·창 태그가 지정되어 있지 않다.', 'This is the rod-without-line form, used by a learned repair recipe with fishing line or twine and a paperclip or nail. It does not mean the weapon condition is zero. This form does not declare the rod or spear tag used by fishing-tool selection.')

QUALIFIERS[FISHING_LURE_LOSS] = ('낚기에 실패했을 때 미끼별 확률 조건에 따라 미끼를 소모할 수 있다. 포획 처리에서는 생미끼를 사용하고 손에서 해제하며, 낚싯줄이 끊어지면 미끼도 잃는다. 인공 루어는 평상시 생미끼 소모에서 제외되지만 분실될 수 있다.', 'A failed attraction can spend the lure according to its registered loss condition. The catch routine uses nonplastic bait and clears it from the hand; a broken rod line also loses the lure. Artificial tackle skips routine nonplastic-bait consumption but can still be lost.')

TRAP_RABBIT_SQUIRREL = 'The supplied animal definitions give this trap positive rabbit and squirrel matches. Both accept apple or corn among their baits and pass the time check from 19:00 through 05:00. Zone, bait freshness, loaded-square exclusion and random catch checks still apply.'

TRAP_BIRD = 'The supplied bird definition gives this trap a positive match and accepts worms, bread or corn among its baits. Equal minimum and maximum hours remove the time-of-day restriction; zone, bait freshness, loaded-square exclusion and random catch checks still apply.'

TRAP_RODENTS = 'The supplied mouse and rat definitions give this trap positive matches and accept cheese or peanut butter among their baits. Equal minimum and maximum hours remove the time-of-day restriction; zone, bait freshness, loaded-square exclusion and random catch checks still apply.'

QUALIFIERS[TRAP_RABBIT_SQUIRREL] = ('제공된 동물 정의에서 토끼·다람쥐에 대응하는 덫이다. 두 동물은 사과·옥수수 등을 미끼로 받으며 19시부터 다음 날 5시까지 시간 검사를 통과한다. 지역·미끼 신선도·로드된 칸의 포획 제외·확률 조건은 계속 적용된다.', 'The supplied definitions match this trap to rabbits and squirrels, with apple or corn among their baits and a time window from 19:00 through 05:00. Zone, bait freshness, loaded-square exclusion and random catch checks still apply.')

QUALIFIERS[TRAP_BIRD] = ('제공된 새 정의에 대응하는 덫이며 지렁이·빵·옥수수 등을 미끼로 받는다. 시작·종료 시간이 같아 시간대 제한은 없지만 지역·미끼 신선도·로드된 칸의 포획 제외·확률 조건은 적용된다.', 'The supplied bird definition matches this trap, with worms, bread or corn among its baits. Equal start/end hours mean no time-of-day restriction; zone, bait freshness, loaded-square exclusion and random catch checks still apply.')

QUALIFIERS[TRAP_RODENTS] = ('제공된 생쥐·쥐 정의에 대응하는 덫이며 치즈·땅콩버터 등을 미끼로 받는다. 시작·종료 시간이 같아 시간대 제한은 없지만 지역·미끼 신선도·로드된 칸의 포획 제외·확률 조건은 적용된다.', 'The supplied mouse and rat definitions match this trap, with cheese or peanut butter among their baits. Equal start/end hours mean no time-of-day restriction; zone, bait freshness, loaded-square exclusion and random catch checks still apply.')

QUALIFIERS[FISHING_LURES] = ('등록된 낚싯대 미끼에는 지렁이·귀뚜라미·메뚜기·바퀴벌레·미끼용 작은 물고기와 두 종류의 인공 루어 등이 있다. 예시 목록이며 포획을 보장하지 않는다.', 'Registered rod-fishing lures include worms, crickets, grasshoppers, cockroaches, bait fish and both tackle types. This is an example list and does not guarantee a catch.')

QUALIFIERS[FISHING_MATCHES] = ('제공된 물고기·미끼 표에서는 작은 물고기 미끼가 파이크에, 두 인공 루어가 송어·배스·메기에 대응한다. 이 표의 파이크와 미끼용 작은 물고기는 인공 루어에 대응하지 않는다. 실제 미끼 유형과 물고기 잔량·포획 선택 조건이 적용되며 실행 중 등록 추가는 이 소스 범위에 포함되지 않는다.', 'In the supplied fish/lure tables, bait fish matches pike; either artificial tackle matches trout, bass and catfish. Pike and bait fish do not match artificial tackle in these tables. Current lure type, fish availability and catch selection still apply; runtime registry additions are outside this source scope.')

HEADPHONE_CONNECTION = 'The radio volume panel accepts Base.Headphones or Base.Earbuds for a portable nontelevision device. Its device, device data and character must exist; the headphone slot must be empty. World devices require adjacent access and vehicle devices require occupying that vehicle. Running stops the action; the action hands the selected item to DeviceData.addHeadphones, without establishing audio playback or continuous inventory possession.'

FUNCTIONS['connect_radio_headphones'] = ('radio headphones', '지원하는 라디오 장치에 헤드폰·이어버드를 연결하는 조작을 할 수 있다.', 'It can be submitted to a supported radio device through its headphone connection action.')

QUALIFIERS[HEADPHONE_CONNECTION] = ('휴대 가능한 TV 이외 기기의 라디오 음량 패널에서 헤드폰·이어버드를 받는다. 캐릭터·기기·기기 데이터가 존재하고 연결 슬롯이 비어 있어야 한다. 월드 기기는 인접 접근, 차량 기기는 해당 차량 탑승이 필요하다. 달리면 중단된다. 선택 물품을 기기 데이터에 전달하는 경로이며 실제 재생이나 지속적인 소지 검사를 보장하지 않는다.', 'The volume panel accepts headphones or earbuds for portable nontelevision devices. A character, device and device data must exist, with an empty headphone slot. World devices require adjacent access; vehicle devices require occupying that vehicle. Running interrupts. The selected item is handed to device data; actual playback and continuous inventory possession are not established.')

BATTER_TEST = 'For cake batter and muffin preparation, the WholeEgg test rejects a cooked participant. A participant without the Egg tag then passes; an Egg-tagged participant needs absolute hunger change at least its absolute base hunger when fresh, or at least three quarters of that base otherwise. Native recipe selection still determines which participants are tested.'

QUALIFIERS[BAKING] = ('해당 반죽 제작법에 지정된 재료·보존 도구·용기를 갖추고 제작 조건을 충족해야 한다. 학습이 필요한 제작법은 익혀야 하며 운전 중에는 제작할 수 없다.', 'Supply the ingredients, kept utensils and containers required by the selected dough or batter recipe. Learn it where required, satisfy recipe eligibility, and do not drive while crafting.')

QUALIFIERS[BATTER_TEST] = ('케이크·머핀 반죽의 WholeEgg 검사는 익힌 참여 물품을 거부한다. 그 뒤 Egg 태그가 없으면 통과하며, 태그가 있는 알은 신선할 때 기본 허기 절댓값 전부, 그 외에는 4분의 3 이상에 해당하는 남은 허기 값을 요구한다. 실제 검사 대상 선택은 제작 판정에 따른다.', 'For cake and muffin batter, WholeEgg rejects cooked participants. It then accepts a participant without the Egg tag; a tagged egg needs remaining absolute hunger of at least its full absolute base hunger when fresh, or three quarters otherwise. Native recipe selection determines the tested participants.')

DEVICE_DELAY = 'For an available hand weapon with a positive explosion timer, confirm a positive numeric delay in the timer dialog. Sensor range selects the activation/explosion label. This writes the timer setting; sound execution and the obsolete declaration runtime availability are separate.'

DEVICE_PLACEMENT = 'An available hand weapon must permit placement and remain in inventory. The action places it on the character square selected when the action is created; walking or running interrupts. Completion creates an IsoTrap and removes the inventory item and hand bindings. Subsequent sound and reuse are separate native behavior.'

DEVICE_RETRIEVAL = 'A placed IsoTrap must still exist and expose an item. Reach an adjacent square and complete the action without walking or running; it returns that exposed item to inventory and removes the world trap. Whether the item survives activation is separate.'

FUNCTIONS.update({
    'set_device_timer': ('device delay', '장치의 타이머를 설정할 수 있다.', 'Its device timer can be set.'),
    'place_noise_device': ('device placement', '장치를 현재 칸에 설치할 수 있다.', 'The device can be placed on the current square.'),
    'retrieve_placed_device': ('device retrieval', '회수 가능한 설치 장치를 소지품으로 가져올 수 있다.', 'A recoverable placed device can be returned to inventory.'),
})

QUALIFIERS.update({
    DEVICE_DELAY: ('사용 가능한 무기의 타이머 값이 양수일 때 타이머 창에서 양수의 지연 값을 확인한다. 감지 범위에 따라 작동·폭발 표기가 달라진다. 설정값 저장과 실제 소리 발생은 별개이며, 이 구형 정의의 실제 사용 가능 여부는 확인되지 않았다.', 'For an available weapon with a positive timer, confirm a positive delay in the dialog. Sensor range selects the activation/explosion label. Saving the setting is separate from actual sound, and runtime availability of this obsolete form is unconfirmed.'),
    DEVICE_PLACEMENT: ('설치를 허용하는 사용 가능한 무기를 계속 소지해야 한다. 동작을 만들 때의 현재 칸에 설치하며 걷거나 달리면 중단된다. 완료하면 월드 장치를 만들고 소지품과 손에서 제거한다. 이후 소리 발생과 재사용은 별도 동작에 달려 있다.', 'Keep an available placement-enabled weapon in inventory. It is placed on the square selected when the action starts; walking or running interrupts. Completion creates the world device and removes the inventory item and hand bindings. Later sound and reuse depend on separate behavior.'),
    DEVICE_RETRIEVAL: ('설치된 장치가 남아 있고 회수할 물품을 제공해야 한다. 인접한 칸까지 접근한 뒤 걷거나 달리지 않고 완료하면 해당 물품을 소지품에 넣고 월드 장치를 제거한다. 작동 후에도 회수할 물품이 남는지는 별도로 확인해야 한다.', 'The placed device must still exist and expose a recoverable item. Reach an adjacent square and finish without walking or running to receive that item and remove the world device. Survival of the item after activation is separate.'),
})

STRAP_SPEED = {
    'Base.AmmoStrap_Bullets': 'While worn in the AmmoStrap slot with its clothing form available, the bullet strap matches a primary-hand item whose ammo type is not Base.ShotgunShells. The reload-speed calculation multiplies its skill/panic-adjusted value by 1.15 before driver and animation-speed factors; actual action duration is separate.',
    'Base.AmmoStrap_Shells': 'While worn in the AmmoStrap slot with its clothing form available, the shell strap matches a primary-hand item whose ammo type is Base.ShotgunShells. The reload-speed calculation multiplies its skill/panic-adjusted value by 1.15 before driver and animation-speed factors; actual action duration is separate.',
}

for _strap, _predicate in STRAP_SPEED.items():
    _shell = _strap.endswith('_Shells')
    QUALIFIERS[_predicate] = (
        '탄띠 착용 위치에 해당 의류 형태로 착용하고 주 손에 든 물품의 탄종이 ' + ('산탄( Base.ShotgunShells )이어야 한다.' if _shell else '산탄( Base.ShotgunShells ) 이외여야 한다.') + ' 장전 속도 계산에서 기술·공황을 반영한 값에 1.15를 곱한 뒤 운전·애니메이션 배율을 적용한다. 실제 동작 소요 시간은 별도 처리에 달려 있다.',
        'Wear the available strap clothing form in the AmmoStrap slot, with a primary-hand item using ' + ('Base.ShotgunShells.' if _shell else 'an ammo type other than Base.ShotgunShells.') + ' The calculation multiplies the skill/panic-adjusted reload-speed value by 1.15 before driver and animation-speed factors. Actual action duration depends on separate processing.')

EFFECTS[('reload_speed_setting', 'multiply_1_15')] = ('조건에 맞는 장전 속도 설정에 1.15 배율을 적용한다.', 'It applies a 1.15 multiplier to the matching reload-speed setting.')

RUNNING_EXCHANGE = {
    'tire': 'The tire template keeps a Jack and primary-hand LugWrench, with Mechanics 1 used in the success roll and no recipe requirement. Installation requires the matching brake and suspension. The successful install/uninstall callback clears/sets the native tire-removed flag for the wheel. Native vehicle-type/template expansion and exact wheel binding remain required.',
    'brake': 'The brake template keeps a Jack and primary-hand Wrench, requires Basic Mechanics knowledge and uses Mechanics 3 in the success roll. It declares matching-tire removal for both work tables; the supplied uninstall test enforces that prerequisite while the install test does not read requireUninstalled, although the tooltip displays it. Native canInstallPart may add checks; the tooltip alone is not proof of enforcement.',
    'suspension': 'The suspension template keeps a Jack and primary-hand Wrench, requires Basic Mechanics knowledge and uses Mechanics 3 in the success roll. Matching-tire removal is declared for both work tables; the supplied uninstall test enforces it, while install only displays that prerequisite in the tooltip and delegates to native canInstallPart. Native enforcement is not inferred from the display.',
    'muffler': 'The muffler template keeps a primary-hand Wrench, requires Basic Mechanics knowledge and uses Mechanics 5 in the success roll. Its work area is TruckBed. Both callbacks read the install table for EngineDoor opening/closing and duration, including uninstall even though that work table does not declare the door.',
}

RUNNING_WEAR = 'With an installed part, the engine running and forward speed above 10 km/h, the shared wear callback combines the item normal/offroad wear getter, vehicle offroad efficiency, speed and absolute steering into a random condition-loss chance. Positive condition can fall by one, then condition and part stats are updated. The callback does not use elapsedMinutes to scale this chance; native getter mapping, clamping and update frequency remain separate.'

BRAKE_WEAR = 'With an installed brake and the engine running, a positive native brake-speed-since-update reading determines a random chance capped by speed 80. Success decreases part condition by one and transmits/updates stats. This branch has no positive-condition guard and does not scale by elapsedMinutes. It does not calculate stopping distance or actual brake force.'

TIRE_WEAR = 'With an installed tire, engine running and forward speed above 10 km/h, shared wear can lower condition; a separate roll can lose one air unit. Below five air units, zero air or a successful low-air roll drops the existing tire onto the vehicle square and removes it. Below condition 15, zero condition or a successful condition roll removes it with a tire-explosion sound, without the world-item drop. Removal clears the installed item/model and sets the removed flag. CheckOperate.Tire immediately returns true, so this code does not establish that a flat or absent tire prevents driving.'

TIRE_INFLATION = 'Use the mechanics menu for an installed Air container below capacity plus five, with a recursively found TirePump. Exit the vehicle, path to its part area and equip the pump. The target is capacity when current pressure rounded to two decimals is below it, otherwise capacity plus five. The action requires only that a tire remain installed, not continued area or pump possession; it sends interpolated pressure when the integer changes and its last calculated pressure on completion. Cancellation keeps prior server requests. The server resolves vehicle/part, sets content and tire inflation ratio, then transmits mod data; exact clamping and synchronization remain native.'

TIRE_DEFLATION = 'Use the mechanics menu for an installed Air container with nonzero content; no pump is required. Exit the vehicle and path to the part area. The action targets zero, sends intermediate pressure when the integer changes and zero on completion; its validity returns true without a continued area or installed-tire check. Cancellation retains earlier requests. The server resolves vehicle/part and calls native content/inflation setters; a successful synchronized zero-pressure result is not guaranteed by the Lua dispatch alone.'

for _kind, _ko, _en in (('tire', '타이어', 'tire'), ('brake', '브레이크', 'brake'), ('suspension', '서스펜션', 'suspension'), ('muffler', '머플러', 'muffler')):
    for _verb, _ko_verb in (('install', '장착'), ('remove', '탈거')):
        FUNCTIONS[_verb + '_vehicle_' + _kind] = ('vehicle ' + _kind, '호환 차량의 ' + _ko + '를 ' + _ko_verb + '할 수 있다.', 'The compatible vehicle ' + _en + ' can be ' + ('installed.' if _verb == 'install' else 'removed.'))

FUNCTIONS['inflate_vehicle_tire'] = ('tire inflation', '장착된 차량 타이어에 공기를 넣을 수 있다.', 'Air can be added to an installed vehicle tire.')

FUNCTIONS['deflate_vehicle_tire'] = ('tire deflation', '장착된 차량 타이어의 공기를 뺄 수 있다.', 'Air can be released from an installed vehicle tire.')

QUALIFIERS.update({
    RUNNING_EXCHANGE['tire']: ('잭과 주 손의 휠 렌치를 사용하며 정비 1 수준을 성공 판정에 반영한다. 별도 제조법 지식 요구는 없고 장착할 때 같은 위치의 브레이크와 서스펜션이 필요하다. 성공한 장착·탈거는 해당 바퀴의 타이어 제거 표시를 갱신한다.', RUNNING_EXCHANGE['tire']),
    RUNNING_EXCHANGE['brake']: ('잭·주 손의 렌치·기본 정비 지식이 필요하며 정비 3 수준을 성공 판정에 반영한다. 대응 타이어 탈거는 양쪽 작업 표에 있지만 Lua는 탈거 검사에서만 강제하고 장착에서는 안내로 표시한다. 엔진의 추가 장착 검사는 별도다.', RUNNING_EXCHANGE['brake']),
    RUNNING_EXCHANGE['suspension']: ('잭·주 손의 렌치·기본 정비 지식이 필요하며 정비 3 수준을 성공 판정에 반영한다. 대응 타이어 탈거는 양쪽 작업 표에 있지만 Lua는 탈거 검사에서만 강제하며 장착 안내만으로 강제를 확정하지 않는다.', RUNNING_EXCHANGE['suspension']),
    RUNNING_EXCHANGE['muffler']: ('주 손의 렌치와 기본 정비 지식이 필요하며 정비 5 수준을 성공 판정에 반영한다. 적재함 작업 위치를 사용하고, 장착·탈거 모두 장착 표에서 엔진 덮개 여닫기와 작업 시간을 읽는다.', RUNNING_EXCHANGE['muffler']),
    RUNNING_WEAR: ('장착 상태에서 엔진이 작동하고 전진 속도가 10km/h를 넘으면 노면·속도·조향에 따른 난수 판정으로 양수인 부품 상태가 1 감소할 수 있다. 경과 시간으로 확률을 비례 조정하지 않으며 엔진의 수치 해석·갱신 주기는 별도다.', RUNNING_WEAR),
    BRAKE_WEAR: ('브레이크가 장착되고 엔진이 작동하며 직전 갱신 이후의 제동 속도 값이 양수일 때 난수 판정으로 상태가 1 감소할 수 있다. 양수 상태를 미리 요구하지 않으며 실제 제동력·정지 거리를 계산하는 코드는 아니다.', BRAKE_WEAR),
    TIRE_WEAR: ('엔진 작동·전진 속도 10km/h 초과·장착 상태에서 마모와 공기 손실이 일어날 수 있다. 공기가 5 미만이면 조건부로 타이어를 바닥에 떨어뜨리고 탈거하며, 상태가 15 미만이면 별도 판정으로 떨어뜨리지 않고 제거하며 파열음을 낸다. 공기나 상태가 0이면 각 제거 분기를 바로 실행한다. 주행 허용 검사는 즉시 참을 반환하므로 주행 불가를 뜻하지 않는다.', TIRE_WEAR),
    TIRE_INFLATION: ('장착된 타이어와 펌프가 필요하고 공기량이 용량+5 미만이어야 한다. 차량에서 내려 작업 위치로 이동해 펌프를 들며 용량 미만이면 용량까지, 그 밖에는 용량+5까지 주입한다. 동작 중에는 타이어 존재만 검사하며 계속된 위치·펌프 소지는 검사하지 않는다. 진행 중 서버로 보낸 압력은 취소해도 되돌리지 않는다. 최종 반영·상한·동기화는 엔진 처리에 따른다.', TIRE_INFLATION),
    TIRE_DEFLATION: ('공기가 남은 장착 타이어에서 펌프 없이 사용한다. 차량에서 내려 작업 위치로 이동하고 0을 목표로 압력을 낮추는 요청을 보낸다. 동작 유효성은 항상 참이며 위치·타이어 존재를 재검사하지 않는다. 취소해도 이전 요청은 유지되고 완료 시 0을 요청한다. 실제 수치 반영과 동기화는 엔진 처리에 따른다.', TIRE_DEFLATION),
})

EFFECTS[('installed_vehicle_part_condition', 'decrease')] = ('장착된 차량 부품의 상태가 감소할 수 있다.', 'The installed vehicle part can lose condition.')

EFFECTS[('installed_tire_air_or_attachment', 'lose')] = ('장착된 타이어의 공기가 줄거나 타이어가 제거될 수 있다.', 'An installed tire can lose air or be removed.')

PANEL_INSTALL = 'The runtime vehicle part must accept this exact FullType, be empty and permit installation. Use a positive-condition item from the accessible mechanics containers; transfer it and the required tools, leave the vehicle and reach the specified work area. The selected recipe/profession/trait, prerequisite-part and key/access tests must pass. The timed action requires the item in inventory and continued canInstallPart approval. Server success installs it and runs the selected completion callback; failure returns it, possibly damaged. Required skill shortfall affects success/damage rolls rather than acting as the commented-out skill gate.'

PANEL_REMOVE = 'The compatible vehicle part must contain the item and permit removal. Reach its work area with the selected tools, recipe/profession/trait and key/access requirements; prerequisite removal and any empty-content/seat rules apply. The timed action requires an installed item and continued canUninstallPart approval. The server uses install-table skills for its roll: success clears the part, copies its content amount to the returned item and runs the uninstall callback; failure can damage the installed part. Completion is not guaranteed.'

PANEL_NAMES = {
    'hood': ('후드', 'hood'), 'front_door': ('앞문', 'front door'), 'rear_door': ('뒷문', 'rear door'),
    'double_rear_door': ('양문형 뒷문', 'double rear door'), 'trunk_lid': ('트렁크 덮개', 'trunk lid'),
    'front_window': ('앞문 유리', 'front window'), 'rear_window': ('뒷문 유리', 'rear window'),
    'windshield': ('앞유리', 'windshield'), 'rear_windshield': ('뒷유리', 'rear windshield'),
}

for _part, (_ko_part, _en_part) in PANEL_NAMES.items():
    FUNCTIONS['install_vehicle_' + _part] = ('vehicle ' + _en_part + ' installation', '호환 차량의 ' + _ko_part + ' 자리에 장착할 수 있다.', 'It can be installed as the ' + _en_part + ' in a compatible vehicle.')
    FUNCTIONS['remove_vehicle_' + _part] = ('vehicle ' + _en_part + ' removal', '차량의 ' + _ko_part + ' 자리에서 탈거할 수 있다.', 'It can be removed from the vehicle ' + _en_part + ' position.')

QUALIFIERS[PANEL_INSTALL] = ('차량의 빈 부품 자리가 이 정확한 유형을 받고 장착을 허용해야 한다. 상태가 남은 물품과 지정 도구를 소지품으로 옮긴 뒤 차량에서 내려 작업 위치에 접근한다. 지정 제작 지식·직업·특성·선행 부품과 열쇠 또는 열린 문·창문 등의 접근 조건을 만족해야 한다. 동작 중 물품을 계속 소지하고 장착 판정을 통과해야 한다. 서버 성공 시 장착되며 실패하면 반환되거나 손상되어 반환될 수 있다. 요구 기술보다 낮으면 시도 금지 대신 성공·손상 확률에 반영된다.', 'The empty runtime part must accept this exact type and allow installation. Transfer a positive-condition item and specified tools, leave the vehicle and reach the work area. Required recipe knowledge, profession, traits, prerequisite parts and key/access conditions must pass. Keep the item in inventory and continue to pass installation checks. Server success installs it; failure returns it, possibly damaged. A skill shortfall affects success/damage rolls rather than prohibiting the attempt.')

QUALIFIERS[PANEL_REMOVE] = ('호환 차량에 해당 물품이 장착되어 있고 탈거 판정을 통과해야 한다. 도구와 지정 제작 지식·직업·특성·열쇠 또는 접근 조건을 갖추고 작업 위치에 도달한다. 필요한 선행 탈거와 빈 적재 공간·좌석 조건도 적용된다. 동작 중 부품이 남아 있고 탈거 판정을 계속 통과해야 한다. 서버는 장착 표의 기술 요구로 판정하며 성공하면 부품을 비우고 해당 물품을 반환한다. 실패하면 장착된 부품이 손상될 수 있다.', 'The compatible part must contain the item and allow removal. Reach the work area with the specified tools, recipe knowledge, profession, traits and key/access conditions. Prerequisite removals and any empty-container/seat rules also apply. The item must remain installed and removal checks must continue to pass. The server rolls using install-table skills; success clears the part and returns the item, while failure can damage the installed part.')

PANEL_DOOR = 'After this form is installed in a compatible door/hood/trunk part, use its available door control. Opening or closing requires the opposite open state and a stopped vehicle. The action updates the open state locally and sends the server setDoorOpen command. A required unlock can fail under native key/lock handling. Hood use also opens/closes the mechanics UI. First opening of an alarmed, not previously entered vehicle without its key in inventory or ignition triggers its alarm and marks it previously entered.'

PANEL_LOCK = 'The installed compatible door must expose a lock control. Locking requires an unlocked door and sends setDoorLocked; the server changes the state only when the lock is not broken. Unlocking invokes the native toggle and stops if it remains locked. The in-vehicle group control requires remaining in that vehicle and sends commands for passenger doors; it is not a key requirement for every lock action.'

PANEL_WINDOW = 'After installation in a compatible openable window part, use the vehicle window control. The window must not be destroyed and its open state must differ from the requested state. The action updates opening progress, restores progress if interrupted, and sends setWindowOpen at completion. The radial control selects the seated passenger door child window; mechanics-menu visibility has its separate in-vehicle/debug restrictions. Fixed windshields are not admitted as openable.'

FUNCTIONS['operate_installed_vehicle_door'] = ('installed door controls', '장착된 차량 문·후드·트렁크 덮개를 열거나 닫을 수 있다.', 'The installed vehicle door, hood or trunk lid can be opened or closed.')

FUNCTIONS['operate_installed_vehicle_lock'] = ('installed door lock controls', '장착된 차량 문의 잠금 상태를 조작할 수 있다.', 'The installed vehicle door lock can be controlled.')

FUNCTIONS['operate_installed_vehicle_window'] = ('installed window controls', '장착된 개폐식 차량 창문을 열거나 닫을 수 있다.', 'The installed openable vehicle window can be opened or closed.')

QUALIFIERS[PANEL_DOOR] = ('호환 차량에 장착되어 해당 문 조작을 사용할 수 있어야 한다. 차량이 멈춰 있고 현재 상태가 요청한 열림·닫힘과 달라야 한다. 필요한 잠금 해제는 열쇠·잠금 판정에 따라 실패할 수 있다. 후드 사용은 정비 창도 열거나 닫는다. 이전에 들어가지 않은 경보 차량을 열쇠 소지나 시동 장치의 열쇠 없이 처음 열면 경보를 작동시킨다.', 'Install it in a compatible part with an available door control. The vehicle must be stopped and the current open state must differ from the request. A required unlock can fail under key/lock checks. Hood use also opens or closes the mechanics UI. First opening an alarmed vehicle not previously entered, without its key in inventory or ignition, triggers its alarm.')

QUALIFIERS[PANEL_LOCK] = ('호환 차량에 장착된 문의 잠금 조작이 제공되어야 한다. 잠글 때는 현재 잠기지 않아야 하며 서버는 잠금 장치가 고장 나지 않았을 때 상태를 바꾼다. 잠금 해제 판정 후에도 잠겨 있으면 동작이 중단된다. 차량 안의 일괄 조작은 그 차량에 계속 탑승한 채 승객용 문에 적용되며, 모든 잠금 조작에 열쇠가 필요한 것은 아니다.', 'The compatible installed door must expose a lock control. Locking requires an unlocked door, and the server changes it only if the lock is not broken. An unlock attempt stops if the door remains locked. Group controls require staying in that vehicle and apply to passenger doors; a key is not required for every lock action.')

QUALIFIERS[PANEL_WINDOW] = ('호환 차량의 개폐식 창문 자리에 장착되어야 하며 파괴되지 않고 현재 상태가 요청한 열림·닫힘과 달라야 한다. 원형 메뉴는 탑승 좌석 문의 창문을 선택한다. 동작은 개폐 진행도를 바꾸고 중단 시 원래 상태에 맞춰 복원하며 완료하면 창문 상태를 바꾼다. 고정 앞유리·뒷유리에 개폐 기능을 부여하지 않는다.', 'Install it in a compatible openable window part. It must not be destroyed and its current open state must differ from the request. The radial menu selects the window of the seated passenger door. The action updates opening progress, restores it on interruption and changes the state at completion. Fixed windshields are not treated as openable.')

SPEAR_ATTACHMENTS = (
    ('Bread Knife', 'BreadKnife', 'SpearBreadKnife'), ('Butter Knife', 'ButterKnife', 'SpearButterKnife'),
    ('Fork', 'Fork', 'SpearFork'), ('Letter Opener', 'LetterOpener', 'SpearLetterOpener'),
    ('Scalpel', 'Scalpel', 'SpearScalpel'), ('Spoon', 'Spoon', 'SpearSpoon'),
    ('Scissors', 'Scissors', 'SpearScissors'), ('Hand Fork', 'HandFork', 'SpearHandFork'),
    ('Screwdriver', 'Screwdriver', 'SpearScrewdriver'), ('Kitchen Knife', 'KitchenKnife', 'SpearKnife'),
    ('Hunting Knife', 'HuntingKnife', 'SpearHuntingKnife'), ('Machete', 'Machete', 'SpearMachete'),
    ('Ice Pick', 'IcePick', 'SpearIcePick'),
)

SPEAR_ITEMS = {'Base.SpearCrafted', *('Base.' + result for _, _, result in SPEAR_ATTACHMENTS)}

OBJECT_LABELS = {
    **{'Base.' + name + 'Pic': '사진' for name in ('Bob', 'Casey', 'Chris', 'Cortman', 'Hank', 'James', 'Kate', 'Marianne')},
    **{'Base.' + name: '인형' for name in ('BorisBadger', 'Doll', 'FluffyfootBunny', 'FreddyFox', 'FurbertSquirrel', 'JacquesBeaver', 'MoleyMole', 'PancakeHedgehog')},
    'Base.CatToy': '고양이 장난감', 'Base.ToyBear': '곰 장난감', 'Base.ToyCar': '장난감 자동차',
    'Base.Spiffo': '스피포 인형', 'Base.SpiffoBig': '큰 스피포 인형', 'Base.Disc': 'CD', 'Base.VHS': '비디오테이프',
}

PLAIN_OBJECT_LABELS = {'Base.' + name: label for name, label in {
    'PoolBall': '당구공', 'Money': '현금', 'Baseball': '야구공', 'Basketball': '농구공', 'Button': '단추',
    'ChessBlack': '검은 체스말', 'ChessWhite': '흰 체스말', 'Cologne': '콜로뉴', 'CreditCard': '신용카드',
    'DogChew': '개 장난감', 'Football': '풋볼', 'GolfBall': '골프공', 'Leash': '목줄', 'Perfume': '향수',
    'Pipe': '재료', 'RubberBand': '고무줄', 'SoccerBall': '축구공', 'Sponge': '스펀지', 'TennisBall': '테니스공',
    'Yarn': '재료', 'Bricktoys': '블록 장난감', 'Frame': '액자', 'Rubberducky': '고무 오리', 'Cork': '코르크 마개',
    'Toothbrush': '칫솔', 'Toothpaste': '치약', 'CardDeck': '카드 한 벌', 'Comb': '빗', 'Dice': '주사위', 'String': '끈',
    'Wallet': '지갑', 'Wallet2': '지갑', 'Wallet3': '지갑', 'Wallet4': '지갑', 'Yoyo': '요요', 'CameraFilm': '잡동사니',
    'Chopsticks': '젓가락', 'Plate': '접시', 'PlateBlue': '파란 접시', 'PlateOrange': '주황 접시', 'PlateFancy': '장식 접시',
    'OvenMitt': '오븐 장갑', 'PaperNapkins': '종이 냅킨', 'KitchenTongs': '주방 집게', 'Straw': '빨대',
    'PlasticTray': '플라스틱 쟁반', 'FountainCup': '음료 컵', 'CuttingBoardPlastic': '플라스틱 도마',
    'CuttingBoardWooden': '나무 도마', 'GamePieceBlack': '검은 게임 말', 'GamePieceRed': '빨간 게임 말',
    'GamePieceWhite': '흰 게임 말', 'CheckerBoard': '체커판', 'BackgammonBoard': '백개먼 판', 'PokerChips': '포커 칩',
    'Staples': '스테이플 심', 'Stapler': '스테이플러', 'HolePuncher': '홀펀처',
}.items()}

OBJECT_LABELS.update(PLAIN_OBJECT_LABELS)

PLAIN_OBJECT_FIELDS = {'DisplayCategory', 'Weight', 'Type', 'DisplayName', 'Icon', 'WorldStaticModel'}

MATERIAL_OBJECT_ITEMS = {'Base.' + name for name in (
    'BakingTray', 'BarbedWire', 'Belt', 'ConcretePowder', 'Doorknob', 'Drawer', 'Hinge', 'Pillow',
    'PlasterPowder', 'RoastingPan', 'Teabag', 'Aluminum', 'UnusableMetal', 'Coldpack', 'MotionSensor',
    'Receiver', 'TriggerCrafted', 'Sparklers', 'Amplifier', 'Timer', 'TimerCrafted', 'Bell', 'CleaningLiquid',
    'Dart', 'KnittingNeedles', 'ScrapMetal', 'SheetMetal', 'Underwear1', 'Underwear2', 'WaterDish',
    'Stone', 'Tarp', 'Earrings', 'Necklacepearl', 'Ring', 'Soap', 'Umbrella', 'DigitalWatch', 'Scotchtape',
    'Locket', 'Radio', 'WeddingRing_Man', 'WeddingRing_Woman', 'Lamp', 'FireWoodKit', 'EmptyJar',
    'JarLid', 'SmallSheetMetal', 'TinCanEmpty', 'Tongs', '9mmBulletsMold', 'ShotgunShellsMold',
    '308BulletsMold', '223BulletsMold', 'Handle', 'BeerCanEmpty', 'PopEmpty', 'Pop2Empty', 'Pop3Empty',
    'MuffinTray', 'GrillBrush', 'CarvingFork', 'Spatula', 'BakingPan')}

MATERIAL_OBJECT_ITEMS |= {'Radio.ElectricWire', 'Radio.RadioReceiver', 'Radio.RadioTransmitter', 'Radio.ScannerModule'}

MATERIAL_OBJECT_FIELDS = PLAIN_OBJECT_FIELDS | {'MetalValue', 'OBSOLETE', 'Obsolete', 'Tooltip', 'SurvivalGear',
    'StaticModel', 'ColorRed', 'ColorGreen', 'ColorBlue', 'Count', 'AlwaysWelcomeGift'}

BODY_WASHING = 'Use a reachable water source in the same building context, excluding washing machines/dryers; the body must have blood or dirt and the menu requires at least one water unit. Soap2 and CleaningLiquid2 are collected from inventory. The action clears blood/dirt on processed body parts, using one remaining soap use for each bloody part and one water unit per processed part; dirt alone uses no soap. Limited water can leave other parts unwashed. All four makeup slots are removed. Walking/running interrupts; the body action adds no continuous validity guard. Insufficient soap increases its calculated action time by 1.8 but does not prevent washing.'

EQUIPMENT_WASHING = 'Use a reachable water source in the same building context, excluding washing machines/dryers. Select carried visible bloody/dirty clothing or containers, or a bloody weapon; each action requires ten water units and rechecks water. Soap2/CleaningLiquid2 are collected from inventory. For clothing, the supplied with-soap branch consumes one available use per bloody covered part; dirt alone consumes none. Blood/dirt are cleared, clothing becomes fully wet, and the water command is sent. Without enough soap the calculated time is multiplied by five subject to minimum/maximum caps, but washing remains possible. Walking/running interrupts; inventory/soap membership is not continuously rechecked by this action.'

WASHING_OUTCOME = 'During the represented body/equipment washing action with water, blood and dirt are removed only from the processed body parts or clothing covered parts. Body washing can be partial with limited water; clothing becomes wet. Soap is consumed for blood when available under the selected branch, not for dirt alone, and is not required for washing to occur. No wound treatment, infection cure or world-square blood cleaning is implied.'

WASH_TARGET = 'The manual water-source menu selects carried bloody weapons or nonhidden bloody/dirty clothing and containers. The source must share the character building context and be reachable; washers/dryers are excluded. Each action requires and continuously checks ten water units. Completion clears the item blood level; clothing also clears blood/dirt on covered parts, resets dirtyness and becomes fully wet. For nonclothing containers the action clears blood, not a dirt field, even if dirt made the menu available. Soap changes consumption/calculated time but is not required. Walking/running interrupts; the action does not continuously recheck inventory ownership. This does not repair durability or treat wounds.'

FUNCTIONS.update({
    'wash_body': ('body washing', '몸을 물로 씻을 때 세척제로 사용된다.', 'It serves as a cleaning supply when washing the body with water.'),
    'wash_equipment': ('equipment washing', '옷이나 피 묻은 장비를 물로 씻을 때 세척제로 사용된다.', 'It serves as a cleaning supply when washing clothing or bloody equipment with water.'),
    'wash_carried_equipment': ('equipment washing', '소지한 물품을 물로 씻어 피를 지울 수 있다.', 'The carried item can be washed with water to remove blood.'),
})

QUALIFIERS.update({
    WASH_TARGET: ('소지한 피 묻은 무기 또는 숨김 상태가 아닌 피·때 묻은 의류·용기를 선택한다. 같은 건물 맥락의 접근 가능한 물 공급원이 필요하며 세탁기·건조기는 제외된다. 동작마다 물 10단위가 필요하고 계속 확인한다. 완료하면 피 수치를 지우며 의류는 덮개 부위의 피·때와 더러움을 지우고 완전히 젖는다. 의류가 아닌 용기는 때로 메뉴에 나타나도 이 동작이 지우는 것은 피다. 세제는 소비량·계산된 시간을 바꾸지만 필수는 아니다. 걷기·달리기로 중단되며 내구도 수리나 상처 치료가 아니다.', 'Select a carried bloody weapon or nonhidden bloody/dirty clothing or container. Use a reachable water source in the same building context, excluding washers/dryers. Each action needs ten water units, checked continuously. Completion clears blood; clothing also clears covered-part blood/dirt and dirtyness and becomes fully wet. For nonclothing containers, dirt can expose the menu but this action clears blood only. Soap changes consumption/calculated time but is optional. Walking/running interrupts; washing does not repair durability or treat wounds.'),
    BODY_WASHING: ('같은 건물 맥락의 접근 가능한 물 공급원에서 사용하며 세탁기·건조기는 제외된다. 몸에 피나 때가 있고 물이 1단위 이상 있어야 한다. 소지한 비누·세정액은 피 묻은 신체 부위마다 남은 사용량을 한 번 소비하지만 때만 있으면 소비하지 않는다. 처리한 부위의 피·때를 지우고 부위당 물 1단위를 사용하므로 물이 부족하면 일부 부위가 남는다. 얼굴·눈·아이섀도·입술 화장도 제거한다. 걷기·달리기로 중단되며 세제 부족은 계산된 시간을 1.8배로 늘려도 세척을 막지는 않는다.', 'Use a reachable water source in the same building context, excluding washers/dryers, with body blood or dirt and at least one water unit. Carried soap/liquid loses one available use per bloody body part, but none for dirt alone. Processed parts lose blood/dirt and each uses one water unit, so limited water can leave parts unwashed. Face, eye, eye-shadow and lip makeup are also removed. Walking/running interrupts. Insufficient soap multiplies calculated time by 1.8 without preventing washing.'),
    EQUIPMENT_WASHING: ('같은 건물 맥락의 접근 가능한 물 공급원에서 소지한 피·때 묻은 옷·용기나 피 묻은 무기를 씻는다. 세탁기·건조기는 이 메뉴에서 제외되고 동작마다 물 10단위가 필요하다. 세제를 쓰는 의류 분기는 피 묻은 덮개 부위마다 남은 세제 사용량을 한 번 소비하며 때만 있으면 소비하지 않는다. 피·때를 지우고 옷은 완전히 젖는다. 세제 부족은 계산된 시간을 5배로 늘린 뒤 상·하한을 적용하지만 세척 자체는 가능하다. 걷기·달리기로 중단되며 물은 계속 확인한다.', 'At a reachable water source in the same building context, wash carried bloody/dirty clothing or containers, or bloody weapons. Washers/dryers are excluded and each action needs ten water units. The with-soap clothing branch uses one available supply use per bloody covered part, none for dirt alone. Blood/dirt are cleared and clothing becomes fully wet. Insufficient soap multiplies calculated time by five before duration caps; washing still works. Walking/running interrupts and water is rechecked.'),
    WASHING_OUTCOME: ('물을 사용하는 몸·장비 세척 동작의 결과다. 처리한 신체 부위나 의류 덮개 부위의 피·때만 지우며 물이 부족한 몸 세척은 일부만 처리할 수 있고 옷은 젖는다. 해당 분기에서 사용량이 남은 세제는 피를 씻을 때 소비하지만 때만 씻을 때에는 소비하지 않으며 세제 없이도 세척은 가능하다. 상처 치료·감염 치료나 월드 혈흔 청소를 뜻하지 않는다.', 'This is the outcome of body/equipment washing with water. Only processed body or clothing covered parts lose blood/dirt; limited water can leave body parts unwashed and clothing becomes wet. Available soap is used for blood in the selected branch, not for dirt alone; washing can also proceed without it. This is not wound treatment, infection treatment or world-blood cleaning.'),
})

EFFECTS.update({
    ('item_surface_blood', 'remove_by_washing'): ('세척이 끝나면 물품의 피를 지운다.', 'Completed washing clears blood from the item.'),
    ('clothing_surface_dirt', 'remove_by_washing'): ('세척이 끝나면 옷의 때를 지운다.', 'Completed washing clears clothing dirt.'),
    ('clothing_wetness', 'set_100_by_washing'): ('세척이 끝나면 옷이 완전히 젖는다.', 'Completed washing leaves clothing fully wet.'),
    ('washed_surface_blood', 'remove'): ('세척한 신체·의류 부위의 피를 지운다.', 'Washing clears blood from the processed body/clothing parts.'),
    ('washed_surface_dirt', 'remove'): ('세척한 신체·의류 부위의 때를 지운다.', 'Washing clears dirt from the processed body/clothing parts.'),
})

WELDING_CONSTRUCTION = 'Use the active metal-welding menu outside LastStand and while not in a vehicle, with an inventory blowtorch and welding mask/type-tag. Learn the selected metal container, wall, fence or roof group and meet its MetalWelding skill and exact material/use requirements. Inventory and nearby-ground material/use counts are combined, but the mask is required in inventory. The construction action selects its declared torch/mask equipment, checks object-specific placement and reachable same-level access, and interrupts on walking/running. Normal creation consumes need: materials and use: supplies; welding-rod uses are floor((torchUses+0.1)/2), so a one-use torch route requires no rods. Double-door consumption occurs only for its missing first part. Cheat mode bypasses ordinary requirements/consumption; a finished world object is not guaranteed by supplying a part.'

QUALIFIERS[WELDING_CONSTRUCTION] = ('LastStand 외 모드에서 차량에 타지 않고 토치와 용접 마스크를 소지해야 한다. 선택한 금속 수납물·벽·울타리·지붕 제작군을 익히고 해당 용접 기술·재료·사용량을 갖춘다. 재료와 사용량은 소지품·주변 바닥을 합산하되 마스크는 소지해야 한다. 지정 장비 선택과 물체별 배치·같은 층 접근 조건을 충족해야 하며 걷기·달리기로 중단된다. 일반 생성은 지정 재료와 사용량을 소비한다. 용접봉 양은 토치 양에 따라 계산되므로 토치 1회 경로에는 용접봉이 필요하지 않다. 이중문은 없는 첫 부품을 만들 때만 소비한다. 재료 제공만으로 설치 완료를 보장하지 않는다.', 'Outside LastStand and while not in a vehicle, carry a blowtorch and welding mask. Learn the selected metal container, wall, fence or roof group and meet its welding skill, material and use requirements. Inventory and nearby-ground material/uses are combined, while the mask must be carried. Satisfy declared equipment selection, object placement and same-floor reach; walking/running interrupts. Normal creation consumes declared materials and uses. Rod uses depend on torch uses, with no rods required for a one-use torch route. Double doors consume only when creating the missing first part. Supplying a part does not guarantee completed placement.')

ESCAPE_ROPE_INSTALL = 'Use an eligible window, window frame or hoppable attachment above ground level, with nails and the required count of one rope type; windows must not be barricaded. Walk adjacent and transfer the nail and ropes. Enough SheetRope takes priority over Rope; the two counts are not added together. The action rechecks attachment eligibility and a sufficient rope count, but does not recheck nails itself. Walking/running interrupts. The server dispatches addition to the matching window/frame/thumpable/hoppable object; native code owns length, consumption and attachment outcome.'

ESCAPE_ROPE_REMOVE = 'Use an attachment that currently has an escape rope and reach it by the adjacent window/door route. It must still have a rope when the removal action runs; walking/running interrupts. The server checks the object index and supported attachment type, then calls native removal. Returning an intact rope or the same inventory form is not guaranteed by the Lua caller.'

ESCAPE_ROPE_CLIMB = 'Use a currently installed rope square accepted by canClimbSheetRope and the menu strength check, then walk to that square. The queued action rechecks canClimbSheetRope at the current square and hands ascent to native climbSheetRope. Walking/running interrupts the queued action. This local menu selects ascent; it does not prove descent dispatch, successful arrival, fall safety or rope durability.'

FUNCTIONS.update({'supply_escape_rope': ('escape rope installation', '탈출용 로프를 설치하는 재료로 쓸 수 있다.', 'It can be supplied to install an escape rope.'),
                  'anchor_escape_rope': ('escape rope installation', '탈출용 로프 설치에 필요한 못으로 제공된다.', 'It supplies the nail required for escape-rope installation.'),
                  'remove_installed_escape_rope': ('escape rope removal', '설치된 탈출용 로프의 제거 조작을 할 수 있다.', 'Its installed escape-rope form supports a removal action.'),
                  'start_escape_rope_ascent': ('escape rope climbing', '설치된 탈출용 로프를 타고 올라가는 조작을 시작할 수 있다.', 'Ascent on its installed escape-rope form can be started.')})

QUALIFIERS.update({
    ESCAPE_ROPE_INSTALL: ('지상층보다 높은 적합한 창문·창틀·넘을 수 있는 부착 지점에 못과 한 종류의 로프를 필요한 수만큼 준비한다. 창문은 바리케이드가 없어야 한다. 옆으로 접근해 재료를 옮기며, 시트 로프가 충분하면 일반 로프보다 우선 사용하고 두 종류의 수량을 합치지 않는다. 동작 중 설치 가능 여부와 로프 수량을 다시 검사하며 걷기·달리기로 중단된다. 설치 길이·소비량·완료 결과는 게임의 설치 판정에 달려 있다.', 'Use a supported window, frame or hoppable attachment above ground, with nails and enough of one rope type. Windows must not be barricaded. Walk adjacent and transfer supplies; sufficient sheet rope takes priority over regular rope, without combining their counts. The action rechecks attachment eligibility and rope count; walking/running interrupts. Native installation determines length, consumption and completion.'),
    ESCAPE_ROPE_REMOVE: ('탈출용 로프가 있는 부착 지점에 접근해야 하고 제거 동작 때도 로프가 있어야 한다. 걷거나 달리면 중단된다. 서버가 물체 위치·종류를 확인해 제거를 요청하며, 온전한 로프나 같은 물품 형태를 돌려받는지는 별도 판정이다.', 'Reach an attachment with an escape rope; the rope must still exist for removal. Walking or running interrupts. The server checks object location/type and requests removal; return of an intact rope or the same inventory form is a separate outcome.'),
    ESCAPE_ROPE_CLIMB: ('설치된 로프 칸에서 게임의 올라가기 가능 판정과 메뉴의 힘 조건을 통과해야 한다. 해당 칸으로 이동한 뒤 현재 칸의 가능 여부를 다시 검사해 올라가기를 요청한다. 대기 동작은 걷기·달리기로 중단된다. 이 메뉴는 올라가기를 선택하며 내려가기·안전한 도착·낙하 방지·로프 내구성을 보장하지 않는다.', 'Use an installed rope square accepted by the native climb check and menu strength condition. Walk there, recheck ascent at the current square and request climbing. Walking/running interrupts the queued action. This menu selects ascent and does not guarantee descent, safe arrival, fall prevention or rope durability.'),
})

BROKEN_GLASS_ITEMS = {f'Base.brokenglass_1_{i}' for i in range(4)}

FLOOR_GLASS_PICKUP = 'Select this sprite as a placed IsoBrokenGlass object and reach its adjacent square. The pickup menu does not require gloves. Walking/running interrupts; the action validity function itself always returns true. Completion requires movable sprite properties, the world object and successful item creation, then uses the forced pickup path. Native sprite-to-object and returned-item identity remain separate; window-frame glass removal is a different action.'

FLOOR_GLASS_INJURY = 'During the IsoBrokenGlass pickup branch, having no item in the hands clothing slot permits a one-in-three check to scratch a randomly selected hand. Only inside that branch, another one-in-five check can leave glass in that hand. Any hands-slot clothing blocks this Lua injury branch; the commented fingerless-glove restriction is not active. This describes pickup, not merely approaching or stepping on glass.'

FUNCTIONS['pickup_floor_glass'] = ('floor glass pickup', '바닥에 놓인 유리 파편 형태를 주울 수 있다.', 'Its placed floor-glass form can be picked up.')

EFFECTS.update({('hand_scratch', 'apply_during_glass_pickup'): ('유리를 주울 때 손이 긁힐 수 있다.', 'Picking up the glass can scratch a hand.'),
                ('hand_embedded_glass', 'apply_during_glass_pickup'): ('유리를 주울 때 손에 유리가 박힐 수 있다.', 'Picking up the glass can leave glass in a hand.')})

QUALIFIERS[FLOOR_GLASS_PICKUP] = ('이 스프라이트의 바닥 유리 물체를 선택하고 옆 칸에 접근해야 한다. 장갑 없이도 메뉴를 열 수 있고 걷거나 달리면 중단된다. 완료 시 이동 가능한 스프라이트, 해당 월드 물체와 물품 생성이 필요하다. 돌려받는 물품의 종류는 별도 판정이며 창틀 파편 제거와는 다른 동작이다.', 'Select the placed floor-glass object for this sprite and reach an adjacent square. Gloves are not required by the menu; walking or running interrupts. Completion needs movable sprite properties, the world object and item creation. Returned item identity remains separate, and window-frame glass removal is a different action.')

QUALIFIERS[FLOOR_GLASS_INJURY] = ('바닥 유리 수거 분기에서 손 착용 칸에 물품이 없으면 3분의 1 확률 검사로 임의의 한쪽 손을 긁는다. 이 분기 안에서 다시 5분의 1 확률 검사에 성공하면 같은 손에 유리가 박힌다. 손 칸의 착용 물품이 있으면 이 Lua 부상 분기는 실행되지 않는다. 단순 접근이나 밟는 동작의 위험을 뜻하지 않는다.', 'In the floor-glass pickup branch, an empty hands clothing slot permits a one-in-three check to scratch a randomly selected hand. A nested one-in-five check can embed glass in that same hand. Having an item in the hands clothing slot skips this Lua injury branch. This does not describe merely approaching or stepping on glass.')

FABRIC_ACTION = 'Use the selected ripping recipe and its exact named-cloth or fabric group. Clothing has separate worn and unworn recipes; denim and leather require a kept scissors-group tool. Same-inventory and other declared recipe requirements apply, and crafting is unavailable while driving. The recipe declares removal of its nominal result; the callback takes the first participant and creates the mapped fabric: quantity depends on covered parts and tailoring, with dirt/blood selecting a dirty form only when registered. A tailoring-dependent random branch can also return partially used thread; neither a fixed material quantity nor thread is guaranteed.'

QUALIFIERS[FABRIC_ACTION] = ('선택한 찢기 제작법의 지정 천 또는 직물 그룹에 맞아야 한다. 의류는 착용 중·미착용 제작법이 따로 있고 데님·가죽에는 보존되는 가위 그룹 도구가 필요하다. 같은 소지품과 해당 제작 조건을 만족해야 하며 운전 중에는 제작할 수 없다. 회수량은 덮는 부위와 재봉 기술에 따라 달라지고, 오염 상태는 등록된 더러운 형태가 있을 때 그 형태 선택에 영향을 준다. 기술에 따른 확률로 일부 사용된 실도 나올 수 있으나 일정 수량이나 실 회수는 보장되지 않는다.', 'Use the exact named-cloth or fabric group accepted by the selected ripping recipe. Clothing has separate worn and unworn recipes; denim and leather require a kept scissors-group tool. Meet same-inventory and other recipe requirements while not driving. Recovered quantity depends on covered parts and tailoring; contamination can select a dirty form when one is registered. A skill-dependent random branch may also return partly used thread, without guaranteeing a fixed quantity or thread.')

GARMENT_PATCHING = 'Open the carried garment inspection panel with a displayed covered part and a fabric type. Select an unpatched part, with a hole for hole patching or without a hole for padding. Have RippedSheets, DenimStrips or LeatherStrips, Thread, and a Needle or SewingNeedle-tagged tool. The callback transfers supplies and garment; the action requires all four items in inventory and no existing patch. Completion calls addPatch, removes one fabric, uses thread and grants tailoring XP. Walking/running interrupts. Native canFullyRestore/addPatch determines restoration and protection; neither full repair nor a fixed defense gain is guaranteed.'

GARMENT_PATCH_REMOVAL = 'In the carried garment inspection panel, select a displayed covered part with an existing patch and have a Needle or SewingNeedle-tagged tool. The callback transfers needle and garment; both must remain in inventory and the patch must still exist. Walking/running interrupts. Completion removes the patch and grants tailoring XP; a skill-dependent random check can return its mapped fabric and additional XP. Returning material is not guaranteed, and the native patch type/protection mapping remains separate.'

FUNCTIONS.update({
    'receive_garment_patch': ('garment patching', '의류의 구멍에 천을 덧대거나 패딩을 추가할 수 있다.', 'Fabric can be applied to a garment hole or added as padding.'),
    'remove_garment_patch': ('garment patching', '의류에 붙은 패치를 제거할 수 있다.', 'An existing garment patch can be removed.'),
    'apply_garment_patch': ('garment patching', '의류에 천을 덧대거나 패딩을 추가하는 작업에 쓰인다.', 'It is used to patch garment holes or add padding.'),
    'unpick_garment_patch': ('garment patching', '의류의 패치를 제거하는 도구로 쓰인다.', 'It is used as a tool to remove a garment patch.'),
})

QUALIFIERS.update({
    GARMENT_PATCHING: ('소지한 의류의 검사 화면에 표시되는 덮개 부위와 직물 유형이 있어야 한다. 기존 패치가 없는 부위에 구멍을 덧대거나 패딩을 추가한다. 천 조각·데님 조각·가죽 조각 중 하나와 실, 바늘 또는 재봉 바늘 태그 도구가 필요하다. 의류와 세 재료·도구를 소지해야 하며 완료 시 천 하나와 실 사용량을 소비하고 재봉 경험치를 얻는다. 걷기·달리기로 중단된다. 완전 복구나 방어력 증가량은 게임의 패치 판정에 달려 있어 보장되지 않는다.', 'Use a displayed covered part of a carried garment with a fabric type. Patch a hole or add padding only where no patch exists. Supply ripped sheets, denim or leather strips, thread, and a needle or SewingNeedle-tagged tool. Keep the garment and all supplies in inventory. Completion consumes one fabric and a thread use and grants tailoring XP. Walking/running interrupts. Full restoration and protection gains depend on the native patch calculation and are not guaranteed.'),
    GARMENT_PATCH_REMOVAL: ('소지한 의류의 검사 화면에 표시되는 부위에 패치가 있어야 하며 바늘 또는 재봉 바늘 태그 도구가 필요하다. 의류·바늘을 계속 소지하고 패치가 남아 있어야 한다. 걷기·달리기로 중단된다. 완료하면 패치를 제거하고 재봉 경험치를 얻으며, 기술에 따른 확률 검사에 성공하면 대응하는 천과 추가 경험치를 돌려받을 수 있다. 천 회수는 보장되지 않는다.', 'Select an existing patch on a displayed part in the carried garment inspection panel and have a needle or SewingNeedle-tagged tool. Keep garment and needle in inventory while the patch remains. Walking/running interrupts. Completion removes the patch and grants tailoring XP; a skill-dependent random check may return the mapped fabric and additional XP. Fabric recovery is not guaranteed.'),
})

MAP_REVEAL = 'On the first viewer update while the map remains in inventory, initialize its runtime map ID and pass the viewer bounds to WorldMapVisited.setKnownInSquares. The named initializer supplies those bounds; this marks a known area, not a physically visited area or a safe route. Missing map data and native map-ID binding can affect the displayed content.'

FUNCTIONS.update({
    'annotate_item_map': ('map annotations', '지도에 기호나 글을 추가할 수 있다.', 'Symbols or notes can be added to the map.'),
    'erase_item_map_annotations': ('map annotations', '지도의 기존 주석을 지울 수 있다.', 'Existing map annotations can be erased.'),
    'reveal_item_map_area': ('map knowledge', '지도를 열면 표시 범위를 월드맵의 알려진 지역으로 등록한다.', 'Opening the map registers its displayed bounds as a known world-map area.'),
})

QUALIFIERS[MAP_REVEAL] = ('지도를 계속 소지한 상태에서 보기 화면의 첫 갱신 시 지도 ID에 맞게 초기화하고 표시 범위를 알려진 지역으로 등록한다. 실제 방문이나 안전한 이동 경로를 뜻하지 않는다. 지도 데이터와 실행 중 지도 ID 결속에 따라 표시 내용은 달라질 수 있다.', 'While the map remains in inventory, the first viewer update initializes its map ID and marks the displayed bounds as known. This does not mean physical visitation or a safe route. Map data and runtime map-ID binding affect the displayed content.')

SPEAR_FISHING = 'Select an unbroken inventory item tagged FishingSpear that the native WeaponType classifier treats as a spear. The UI searches adjacent water at an allowed level and equips it in both hands without a lure; the action requires the same primary item, an initially nearby target and no conflicting queued action. Walking or running interrupts. Fish availability, skill, time, winter, abundance and random selection affect catches. The spear branch accepts the selected fish/lure-table row without a bait match and can lose spear condition during the break check; a catch is not guaranteed.'

SPEAR_FISHING_WEAR = 'In spear fishing, a named-fish selection reaches the size/skill-dependent break check. If its random threshold passes, the spear loses one condition. A broken spear is removed from the hands and stops fishing; an unbroken spear can continue the catch. No fishing-rod broken-form replacement is created by this branch.'

FUNCTIONS['fish_with_spear'] = ('spear fishing', '창 낚시에 사용할 수 있다.', 'It can be used for spear fishing.')

QUALIFIERS[SPEAR_FISHING] = ('소지한 부서지지 않은 낚시 창 중 게임이 창으로 분류하는 물품을 선택한다. 허용된 높이에서 인접한 물을 찾고 미끼 없이 양손에 장비한다. 같은 물품을 주 손에 계속 들고 있어야 하며 시작 대상은 가까워야 한다. 걷기·달리기나 다른 대기 동작으로 중단된다. 물고기 잔량·낚시 기술·시간·겨울·풍부도·확률 선택이 결과를 바꾸며 창이 마모될 수 있으므로 포획은 보장되지 않는다.', 'Select an unbroken inventory fishing spear recognized as a spear by the game. Find adjacent water at an allowed level and equip it in both hands without bait. Keep the same primary-hand item; the initial target must be nearby. Walking, running or a conflicting queued action interrupts. Fish availability, skill, time, winter, abundance and random selection affect catches, and the spear can wear; a catch is not guaranteed.')

QUALIFIERS[SPEAR_FISHING_WEAR] = ('창 낚시에서 물고기 크기·기술에 따른 파손 확률 검사를 통과하면 창 상태가 1 감소한다. 부서지면 손에서 제거하고 낚시를 중단하며, 부서지지 않았으면 포획을 계속할 수 있다. 이 분기는 부러진 낚싯대 형태를 만들지 않는다.', 'When the size/skill-dependent break check passes during spear fishing, the spear loses one condition point. If broken, it is removed from the hands and fishing stops; otherwise the catch can continue. This branch does not create a broken fishing-rod form.')

SPEAR_TOOL_WEAR = 'During CreateSpear, a participating HandWeapon with SmallBlade, LongBlade or Axe category loses one condition point even when the recipe keeps it. This is the callback change, separate from native recipe selection and output creation.'

SPEAR_STONE_LOSS = 'During CreateSpear, a participating item whose type is SharpedStone is removed from inventory when the callback ZombRand(3) result equals zero, despite the kept input clause.'

QUALIFIERS[SPEAR_TOOL_WEAR] = ('창 제작 callback에서 소형 칼날·장검·도끼 범주의 참여 무기는 보존 도구로 지정되어 있어도 상태가 1 감소한다. 제작 대상 선택과 결과 생성은 별도 처리다.', 'In the spear-creation callback, a participating SmallBlade, LongBlade or Axe weapon loses one condition point even when kept by the recipe. Recipe selection and output creation are separate.')

QUALIFIERS[SPEAR_STONE_LOSS] = ('창 제작 callback의 ZombRand(3) 결과가 0이면 참여한 깎인 돌을 소지품에서 제거한다. 제작법의 보존 표기만으로 반복 사용을 보장하지 않는다.', 'The spear-creation callback removes the participating chipped stone when ZombRand(3) returns zero. The kept-input clause does not guarantee repeated use.')

EFFECTS[('item_condition', 'decrease')] = ('물품의 상태가 감소한다.', 'The item loses condition.')

EFFECTS[('inventory_presence', 'remove')] = ('참여 물품이 소지품에서 제거된다.', 'The participating item is removed from inventory.')

SPEAR_CONDITIONS = {
    'spear_crafting': 'Use the exact Create Spear recipe with a plank or branch and an admitted kept cutting alternative, under valid crafting conditions and while not driving. The callback sets output condition from Woodwork and a random draw, bounded by the output maximum then a minimum of two. Kept cutting tools may still wear or be removed; native selection/output delivery is separate.',
    'spear_upgrade': 'Use the exact attachment recipe with a crafted spear, its named attachment and DuctTape=2, under valid crafting conditions and while not driving. The callback starts from crafted-spear condition, subtracts half the condition deficit of other participating HandWeapons, caps at the output maximum then applies a minimum of two. Native output delivery remains separate.',
    'spear_reclaim': 'Use the exact reclaim recipe under valid crafting conditions and while not driving; destroyed inputs are allowed. The callback additionally adds Base.SpearCrafted with selected-item condition capped at the selected maximum then raised to at least two. The named attachment result and its condition are handled separately by RecipeManager.',
}

QUALIFIERS[SPEAR_CONDITIONS['spear_crafting']] = ('판자 또는 나뭇가지와 지정 절삭 도구를 갖추고 제작 조건을 만족해야 하며 운전 중에는 제작할 수 없다. 결과 상태는 목공 기술과 난수로 정해지며 결과 최대값과 최소 2의 제한을 순서대로 적용한다. 보존 도구도 마모되거나 제거될 수 있다.', 'Use a plank or branch and the specified cutting alternative with valid crafting conditions, while not driving. Output condition uses Woodwork and a random draw, capped at the output maximum and then raised to at least two. Kept tools can still wear or be removed.')

QUALIFIERS[SPEAR_CONDITIONS['spear_upgrade']] = ('제작한 창·지정 부착물·덕트 테이프를 갖추고 제작 조건을 만족해야 하며 운전 중에는 제작할 수 없다. 결과 상태는 입력 창 상태에서 다른 참여 무기의 상태 부족분 절반을 빼고, 결과 최대값과 최소 2의 제한을 순서대로 적용한다.', 'Use the crafted spear, named attachment and duct tape with valid crafting conditions, while not driving. Output condition starts from the input spear, subtracts half the condition deficit of other participating weapons, and is capped at the output maximum then raised to at least two.')

QUALIFIERS[SPEAR_CONDITIONS['spear_reclaim']] = ('파괴된 창도 해당 회수 제작법에 사용할 수 있으며 제작 조건을 만족하고 운전 중이 아니어야 한다. 제작한 창을 추가로 돌려주는 경로는 선택한 입력 상태를 최대값으로 제한한 뒤 최소 2로 올려 적용한다. 부착물 결과와 그 상태는 별도의 제작 처리에 달려 있다.', 'The matching reclaim recipe allows destroyed spears and requires valid crafting conditions while not driving. Its additional crafted-spear return uses the selected input condition, capped at its maximum then raised to at least two. The attachment result and its condition depend on separate crafting processing.')

QUALIFIERS[SOWING] = ('설정된 수량의 낱알 씨앗과 씨를 아직 심지 않은 고랑이 필요하다. 메뉴에서 재귀 소지품의 씨앗 목록을 모아 옮긴다. 동작은 목록의 각 씨앗 보유와 식물 물체만 검사하고 목록 길이나 미파종 상태는 재검사하지 않는다. 걷기·달리기로 중단되며 시간은 40, 즉시 동작은 1이다. 치트·즉시 모드는 접근 이동을 면제한다. 완료 시 설정 수량을 목록에서 소비한 뒤 서버에 심기를 요청하며, 서버는 여전히 빈 고랑인 경우만 받는다. 소비와 심기는 원자적이지 않고 성장·수확을 보장하지 않는다.', SOWING)

QUALIFIERS[FERTILIZING] = ('소지한 퇴비를 우선하고 없으면 비료를 골라 접근 가능한 작물에 쓴다. 동작은 식물 물체만 계속 검사하고 걷기·달리기로 중단된다. 좌표를 서버에 보낸 뒤 물품을 한 번 소비하고 FertilizerEmpty 문자열로 소지품 제거를 호출하지만 빈 포장이 만들어졌다는 뜻은 아니다. 서버는 살아 있는 파종 작물에만 효과를 적용한다. 보유·잔량 재검사와 소비·처리의 원자성을 보장하지 않는다.', FERTILIZING)

WATER_TRANSFER = 'Select one water source and a different top-level inventory receiver that can store water; a filled drainable receiver needs at least one use of free space. Before queuing, an empty receiver is replaced through CreateItem(getReplaceType(WaterSource),0), copying favorite, condition and held hands. The native factory initializes its contents. Transfer the donor if needed. Amounts use each item UseDelta to convert fractions into water units and transfer only receiver space. The action always reports valid, linearly updates both fractions and stops on walking/running without rollback. At start donor taint sets receiver taint; clean water does not clear prior taint. Completion depletes an emptied donor with Use and updates receiver weight. There is no ongoing possession, capacity or source-type recheck.'

WORLD_WATER_TRANSFER = 'The world menu prefers a rain collector, then metal drum, dispenser or supported world inventory water item with free capacity, and selects top-level carried water sources. Walk adjacent and equip the source. The action rechecks source water classification/possession, target object index and space. At start it computes min(free capacity, available water), rounding a near-integer remainder above .99 upward; duration is max(6,units)*7. Progress debits whole units. Walking/running stops and commits whole transferred units, including taint even at zero transferred units if the started transfer was positive. Completion commits the full planned amount, depletes a near-empty donor and propagates taint without purification. Normal objects transmit modData; completion of a world inventory target explicitly leaves usedDelta synchronization as a TODO. No continuous distance or planned-amount recomputation is performed.'

CROP_WATERING = 'The farming menu selects a seeded plant below water level 100 and a held water source with whole uses, otherwise top-level inventory water sources. The callback caps uses by supply, ceil((100-waterLvl)/5), 20 and the requested amount, equips and walks adjacent unless farming cheat/instant mode bypasses walking. Duration is 20+6*uses, or one when instant. The timed action rechecks plant existence/water below 100, possession and enough whole uses capped at 20; it does not recheck seeded state, water classification or held identity. Walking/running interrupts before consumption. Completion sends water coordinates/uses; the server only finds the plant, adds five per requested use capped at 100 and records the current last-water hour. Client Use is separate, capped by its local water level, and the remaining fraction is rounded down to whole uses. No taint check or atomic client/server delivery is present. The repeat cursor checks a live seeded plant; its exhausted-source fallback only succeeds immediately for a source meeting the requested uses, so a smaller fallback does not guarantee another action.'

VEHICLE_WASHING = 'The vehicle menu requires blood on an existing supported area and at least one recursively carried Drainable water-source use. It chooses Front/Rear/Left/Right in the source order, paths to the area and rechecks only that the character remains in it. Update repeatedly queries water and stops when none remains. Its accumulators convert water into five blood percentage points per unit; instant mode uses the ceiling of the current blood requirement limited by available water. Repeated equal rounded intensity submissions are skipped. Water fractions are debited across recursive sources and depleted donors receive Use. The server finds the vehicle and sets the requested area intensity without repeating local water or area checks. Already applied changes persist on cancellation; completion queues the next bloody supported area while water remains. No taint, soap, dirt-removal, full-cleaning or atomic delivery guarantee is established.'

WATER_DRINKING = 'The manual menu requires thirst above .1 and selects min(ceil(thirst/.1),10,remaining whole uses), then transfers the source. The action requires possession, allows walking and stops on running. Completion drinks all selected portions; stopping while still possessed drinks floor(uses*progress+.001), with progress above .95 promoted to full. Each portion only consumes while thirst is positive, lowers thirst by .1 with a zero floor, and calls Use. Tainted water adds ten poison capped at twenty only when poison is below twenty and sickness below .3. Duration is at least 120 or 30 per selected use. Native Use, remaining-water binding and bodily consequences remain separate.'

SPRAY_TREATMENT = 'Select the matching positive plant disease in Treat Problem and its exact Milk or Cigarettes spray with remaining whole uses, preferring the held item then recursive inventory. Choose one through min(10,remaining uses), displayed as five disease points per use; the count is not capped by disease severity. Walk adjacent and equip the spray, with farming cheat/instant walking bypass. Duration is 50 per use, or one in instant mode. Timed validity only refreshes the plant and checks its world object, not inventory, spray quantity or disease; walking/running interrupts. Completion sends the matching disease command, whose server requires a positive level and subtracts five per requested use with a zero floor. Separately the client calls Use for every requested use only while its starting/local level is below 100; exactly 100 skips all item consumption although the server may still treat it, and below 100 it can spend uses beyond zero disease. Flies advances the action queue before sending, mildew afterward. No other crop disease is treated and client/server mutation is not atomic.'

SPRAY_PREPARATION = 'The learned Farming recipe uses an empty gardening spray can and the Milk group for mildew cure, or Water=3 and Cigarettes=5 for flies cure, with Time 40 and no kept tool or creation callback. Do not drive and satisfy native recipe eligibility. Mildew cure explicitly permits rotten ingredients and invokes WholeMilk: non-Milk-tag arguments pass; Milk-tag arguments require absolute current hunger at least absolute base hunger when fresh, 45 percent when rotten, otherwise 75 percent. The Milk group includes Milk-tag items and the existing Milk type. The callback does not universally require an unspoiled full carton. Native argument selection, consumption and result delivery remain separate from treatment efficacy.'

QUALIFIERS[SPRAY_PREPARATION] = ('학습한 농사 제조법에서 빈 분무기에 우유 그룹 재료를 넣어 흰가루병 치료제를, 물 3·담배 5를 넣어 파리 치료제를 만든다. 시간은 40이며 도구 보존·생성 콜백은 없다. 운전 중에는 만들 수 없고 엔진의 제작 조건을 만족해야 한다. 흰가루병 제조법은 썩은 재료도 허용하며 WholeMilk는 우유 태그 재료의 현재 배고픔 절댓값을 기본값의 신선 100%·부패 45%·그 외 75% 이상인지 검사한다. 우유 태그가 없는 인수는 통과하므로 신선한 완전 우유팩만 허용한다고 일반화하지 않는다. 소비·결과 전달은 별도 엔진 처리다.', SPRAY_PREPARATION)

for _name, _ko, _en in (
        ('pour_water_into_container', '다른 물 용기에 물을 부을 수 있다.', 'Water can be poured into another water container.'),
        ('receive_poured_water', '소지한 물 용기에서 물을 받을 수 있다.', 'It can receive water from a carried water container.'),
        ('supply_world_water_storage', '지원하는 물받이나 급수 물체에 물을 부을 수 있다.', 'It can supply water to a supported world water-storage object.'),
        ('water_seeded_crop', '씨를 심은 작물에 물을 줄 수 있다.', 'It can water a seeded crop.'),
        ('wash_vehicle_blood', '차량의 혈흔을 씻는 물로 사용할 수 있다.', 'Its water can wash blood from a vehicle.'),
        ('treat_crop_mildew', '작물의 흰가루병 수치를 낮출 수 있다.', 'It can reduce a crop mildew level.'),
        ('treat_crop_flies', '작물의 파리 피해 수치를 낮출 수 있다.', 'It can reduce a crop flies level.')):
    FUNCTIONS[_name] = (_name.replace('_', ' '), _ko, _en)

for _predicate, _ko in (
        (WATER_TRANSFER, '물 공급원 하나와 별도의 소지 용기를 선택하며, 차 있는 용기는 최소 한 사용량의 여유가 필요하다. 빈 용기는 큐에 넣기 전에 엔진이 물 형태로 만들고 즐겨찾기·상태·손 배치를 복사한다. 각 용기의 사용 단위로 수량을 환산해 여유만큼 옮긴다. 동작은 보유나 용량을 재검사하지 않고 양쪽 잔량을 진행에 따라 바꾼다. 걷기·달리기로 중단해도 되돌리지 않으며 시작 시 오염이 전해진다. 완료 때 빈 원본을 소모 처리하고 대상 무게를 갱신한다. 초기 결과 잔량은 엔진 생성에 달려 있다.'),
        (WORLD_WATER_TRANSFER, '여유가 있는 빗물받이·드럼·급수기·지원 월드 물품에 인접해 소지 물을 붓는다. 동작은 소지·물 분류·대상 인덱스·여유를 검사하고, 시작 시 여유와 남은 물 중 작은 양을 정한다. 진행 때 정수 단위를 소비하며 걷기·달리기로 중단해도 그 양과 오염을 반영한다. 양수 전송을 시작했다면 실제 이동이 0이어도 중단 시 오염이 전해질 수 있다. 완료는 계획된 전체 양을 적용하며, 월드 인벤토리 대상의 잔량 동기화는 코드에 미구현으로 남아 있다. 거리나 계획량을 계속 다시 계산하지 않는다.'),
        (CROP_WATERING, '물 수치 100 미만의 심어진 작물과 남은 소지 물을 고른다. 사용량은 보유량·부족량·20·선택량 중 작은 값이며 장비하고 인접한다. 치트·즉시 동작은 이동을 면제한다. 동작은 식물·수치·보유·충분한 양만 재검사하며 걷기·달리기로 중단된다. 완료 시 서버는 사용당 5씩 최대 100까지 더하고 급수 시간을 기록한다. 물 소비는 별도 클라이언트 처리이며 잔량을 정수 사용량으로 내린다. 오염 검사나 원자적 처리는 없다. 반복 커서에서 부족한 대체 물병을 찾았다는 사실만으로 다음 급수가 허용되지는 않는다.'),
        (VEHICLE_WASHING, '지원 차량 부위에 혈흔이 있고 재귀 소지품에 물 한 사용량 이상이 있어야 한다. 해당 부위로 이동하고 그 영역 안에 있는지만 유효성에서 검사한다. 진행 중 물을 다시 조회해 사용당 혈흔 5%포인트를 제거하도록 요청하며 부족하면 중단한다. 물은 소지 용기들에서 소비하고 빈 용기는 소모 처리한다. 서버는 차량을 찾아 요청 수치를 설정하며 물이나 영역을 다시 검사하지 않는다. 중단 전 변화는 남고 완료 후 물이 남으면 다음 혈흔 부위로 이어진다. 오염·비누·먼지 제거·전체 세척 성공을 보장하지 않는다.'),
        (WATER_DRINKING, '갈증이 0.1보다 높을 때 남은 정수 사용량·갈증 필요량·10 중 작은 값을 마신다. 소지가 필요하고 걷기는 허용하지만 달리기로 중단된다. 중단 시 소지 중이면 진행 분량을 마시며 95% 초과 진행은 전량으로 친다. 갈증이 양수인 동안 사용당 0.1씩 최소 0까지 줄이고 물을 소비한다. 오염수는 현재 독 수치 20 미만과 sickness 0.3 미만일 때 독을 10씩 최대 20까지 높인다. 실제 소모·신체 경과는 엔진 처리에 달려 있다.'),
        (SPRAY_TREATMENT, '해당 질병이 양수인 작물과 맞는 우유·담배 살포제를 선택한다. 손의 물품을 우선하고 없으면 소지품 안에서 찾는다. 남은 사용량과 10 중 작은 수까지 선택하며 질병 정도로 소비량을 제한하지 않는다. 인접해 장비하며 치트·즉시 동작은 이동을 면제한다. 유효성은 식물 물체만 재검사하고 걷기·달리기로 중단된다. 서버는 해당 질병이 양수일 때 사용당 5씩 최소 0까지 줄인다. 별도 클라이언트 소비는 질병 수치 100 미만일 때만 실행되어 정확히 100이면 소비를 건너뛰고, 그 아래에서는 질병이 0을 지나도 요청량을 소비할 수 있다. 파리는 큐 진행 후, 흰가루병은 처리 후 큐를 진행한다. 다른 질병 치료나 원자적 동작은 아니다.')):
    QUALIFIERS[_predicate] = (_ko, _predicate)

EFFECTS[('crop_water_level', 'increase_five_per_use')] = ('사용당 작물 물 수치를 5씩 최대 100까지 높인다.', 'Each use adds five to crop water level, capped at 100.')

EFFECTS[('crop_mildew_level', 'decrease')] = ('사용당 흰가루병 수치를 5씩 최소 0까지 낮춘다.', 'Each use removes five mildew points, floored at zero.')

EFFECTS[('crop_flies_level', 'decrease')] = ('사용당 파리 피해 수치를 5씩 최소 0까지 낮춘다.', 'Each use removes five flies points, floored at zero.')

KEY_ITEMS = {'Base.Key' + str(n) for n in range(1, 6)} | {'Base.KeyPadlock', 'Base.CarKey'}

VEHICLE_KEY_USE = 'Native haveThisKeyId must recognize the carried key as matching the vehicle; the item name is not a compatibility test. The driver radial menu requires a working, nonrunning, nonstarted engine and offers the nonhotwired key/ignition route alongside separate easy-use and hotwired alternatives. ISStartVehicleEngine rechecks driver/nonrunning/nonstarted state, not key possession or engine working, and force-completes on update. Completion sends its fresh haveKey boolean; the server rechecks vehicle and driver and calls tryStartEngine without an effective engine-working guard. Native start success remains separate. The driver dashboard key control ignores paused input, normalizes fast time, requests shutdown if running, otherwise toggles setKeysInIgnition when not started; it does not itself recheck a key. Ignition commands require the driver; door-key commands require the addressed vehicle. Their native methods own item transfer and compatibility.'

KEY_ALARM = 'ISOpenVehicleDoor requires a stopped vehicle and an existing closed door, plays opening animations and completes through the actor animation. After requesting and locally setting the door open, its first-entry branch, including the hood, skips triggerAlarm when a matching carried key or ignition key exists. Otherwise an alarmed vehicle triggers without a random roll. It sets PreviouslyEntered true in that first-entry branch. This conditional omission does not silence an already active alarm or prove general alarm immunity.'

KEY_MECHANICS = 'RequiredKeyNotFound first exempts parts without MechanicRequireKey, easy-use mode, mechanics cheat and a vehicle with an accessible unlocked/open/missing nonhood door or open/destroyed/missing window. Otherwise a matching carried key makes this key check succeed. Engine, cover and installation/removal consumers keep their remaining skill, tool, part and access checks; the key does not make every repair eligible.'

DOOR_KEY_USE = 'For a closed door with a known key ID, the menu offers locking or unlocking when haveThisKeyId finds a matching carried key, or from indoors. Walking adjacent precedes the zero-time action; walking/running interrupts. The action accepts a matching key before forceLocked/CustomLock checks; without a key those locks reject it and otherwise being indoors is required. Completion sets LockedByKey on the door and its double/garage-door group without consuming the key. Native key-ID matching and lock enforcement remain separate.'

PADLOCK_USE = 'Select a non-door IsoThumpable that allows padlocks, has neither a padlock nor a nonzero code, with a found Padlock whose NumberOfKey is positive. Walk adjacent before the zero-time action; walking/running interrupts but isValid always returns true. Completion sets the lock and key ID, creates NumberOfKey Base.KeyPadlock items with that ID and removes the padlock. There is no continuing inventory or target-eligibility recheck.'

PADLOCK_KEY_USE = 'The non-door thumpable must be padlocked and haveThisKeyId must find a matching key for the menu. Walk adjacent before the zero-time action, which always reports valid and stops on walking/running. Completion unlocks it, creates a new Base.Padlock with NumberOfKey one, copies the currently found key ID, consumes that one key and resets the structure key ID to minus one. Other matching keys remain. It neither restores the original padlock condition nor rechecks key availability before dereferencing the fresh lookup.'

CODE_LOCK_USE = 'Select a non-door padlock-capable IsoThumpable without a padlock or code and a found CombinationPadlock. Clear the action queue and reach an adjacent tile before opening the dialog. Any change in player X or Y closes it. Confirming OK with a nonzero numeric code removes the item and sets LockedByCode without another possession/target check. Three editable entries feed tonumber with weights 100, 10 and one; arrow controls clamp their own changes, but arbitrary text is not validated by getCode. Joypad B invokes OK rather than cancellation. Native code enforcement remains separate.'

CODE_UNLOCK = 'For a non-door structure with positive LockedByCode, reach an adjacent tile after clearing the queue and enter the matching code. Movement closes the dialog. OK, including joypad B, compares its computed code with the current structure code; a match clears the code and creates a new Base.CombinationPadlock. It does not restore the installed item identity or condition, and typed text has no getCode validation. No carried padlock or key is required for removal.'

for _name, _ko, _en in (
        ('operate_door_lock', '열쇠가 맞는 문의 잠금과 해제를 조작할 수 있다.', 'A matching key can operate a door lock.'),
        ('request_matching_vehicle_start', '맞는 차량의 시동 요청과 점화장치 조작에 사용할 수 있다.', 'A matching key can participate in vehicle start requests and ignition controls.'),
        ('avoid_first_door_alarm_trigger', '맞는 차량의 최초 문 개방 경보 호출을 피할 수 있다.', 'A matching key can avoid the first door-opening alarm call.'),
        ('satisfy_vehicle_mechanics_key', '맞는 차량 정비의 열쇠 요구를 충족할 수 있다.', 'A matching key can satisfy a vehicle mechanics key requirement.'),
        ('install_padlock', '자물쇠를 지원하는 구조물을 잠글 수 있다.', 'It can lock a structure that supports padlocks.'),
        ('remove_matching_padlock', '열쇠가 맞는 구조물의 자물쇠를 제거할 수 있다.', 'A matching key can remove a structure padlock.'),
        ('install_combination_padlock', '지원 구조물에 번호 자물쇠를 달 수 있다.', 'It can install a combination lock on a supported structure.'),
        ('remove_combination_padlock', '맞는 번호로 설치된 번호 자물쇠를 제거할 수 있다.', 'The matching code can remove an installed combination lock.')):
    FUNCTIONS[_name] = (_name.replace('_', ' '), _ko, _en)

for _predicate, _ko in (
        (VEHICLE_KEY_USE, '엔진의 ID 조회가 차량과 이 열쇠를 일치시켜야 한다. 운전석 메뉴는 정상 엔진과 시동 상태를 검사하지만 시동 동작은 운전자·미시동 상태만 재검사하고 현재 열쇠 보유 여부를 서버에 보낸다. 서버는 운전자를 확인한 뒤 실효적인 엔진 정상 검사 없이 시동을 요청한다. 성공은 엔진에 달려 있다. 운전석 계기판은 일시정지 입력을 무시하고 배속을 정상화하며, 운전 중에는 종료를 요청하고 미시동 상태에는 보유 재검사 없이 점화 열쇠 상태 변경을 요청한다. 열쇠 이동·호환성은 엔진 메서드가 처리한다.'),
        (KEY_ALARM, '정지 차량의 닫힌 문을 애니메이션으로 열고 개방 상태를 적용한 뒤 최초 진입 분기를 처리한다. 후드도 포함하며, 맞는 소지 열쇠나 점화 열쇠가 있으면 경보 호출을 건너뛴다. 없으면 경보 차량은 무작위 추첨 없이 경보를 호출한다. 그 분기에서 최초 진입 상태를 기록한다. 이미 울리는 경보를 끄거나 일반 면역을 주는 효과는 아니다.'),
        (KEY_MECHANICS, '정비 열쇠 요구는 해당 부품의 요구 설정이 없거나 간편 사용·정비 치트·열린 차량 접근 경로가 있으면 면제된다. 그 외에는 차량과 맞는 소지 열쇠가 이 검사만 통과시킨다. 엔진·덮개·부품 장착 및 제거의 다른 기술·도구·상태·접근 조건은 그대로 적용된다.'),
        (DOOR_KEY_USE, '닫힌 문의 열쇠 ID와 소지 열쇠가 맞거나 실내에 있어야 메뉴를 쓸 수 있다. 인접 이동 뒤 동작하며 걷기·달리기로 중단된다. 동작은 일치 열쇠를 먼저 허용하고, 열쇠가 없으면 강제·사용자 잠금을 거부한 뒤 실내 여부를 검사한다. 문과 연결된 양문·차고문 잠금을 바꾸며 열쇠를 소비하지 않는다. ID 일치와 실제 잠금 효력은 엔진에 달려 있다.'),
        (PADLOCK_USE, '문이 아닌 자물쇠 지원 구조물에 기존 자물쇠나 번호가 없어야 하며, 열쇠 수가 양수인 자물쇠가 필요하다. 인접 이동 뒤 시간 0의 동작이 잠금·ID를 설정하고 지정 수의 열쇠를 만들어 ID를 복사한 뒤 자물쇠를 없앤다. 걷기·달리기로 중단되지만 보유나 대상 조건을 계속 재검사하지 않는다.'),
        (PADLOCK_KEY_USE, '잠긴 구조물과 ID가 맞는 열쇠가 메뉴 조건이다. 인접 이동 뒤 해제하고 새 자물쇠를 열쇠 수 1로 만든 다음 현재 찾은 열쇠 하나를 소비하고 구조물 ID를 -1로 바꾼다. 다른 같은 열쇠는 남는다. 원래 자물쇠 상태를 복원하지 않으며 동작 유효성에서 열쇠를 재검사하지 않아 완료 시 조회 실패는 별도 경계로 남는다.'),
        (CODE_LOCK_USE, '문이 아닌 지원 구조물에 잠금·번호가 없어야 하며 번호 자물쇠가 필요하다. 작업 대기열을 비우고 인접해 창을 연다. X·Y가 바뀌면 닫히지만 OK에서 보유나 대상 조건을 다시 검사하지 않는다. 0 아닌 번호로 물품을 소비하고 잠근다. 화살표는 숫자 변경을 제한하지만 직접 입력 문자열은 번호 계산에서 검증하지 않는다. 조이패드 B도 취소가 아니라 OK로 처리한다.'),
        (CODE_UNLOCK, '번호가 양수인 문 아닌 구조물에 인접해 맞는 번호를 확인하면 번호를 지우고 새 번호 자물쇠를 만든다. 물품 보유는 필요하지 않으며 원래 상태·동일 물품을 돌려주지 않는다. 이동하면 창이 닫히고 조이패드 B도 OK로 처리한다. 직접 입력 문자열은 번호 계산에서 검증하지 않는다.')):
    QUALIFIERS[_predicate] = (_ko, _predicate)

CAMP_PLACEMENT_SOURCES = (
    'lua/server/Camping/BuildingObjects/campingTent.lua',
    'lua/server/Camping/BuildingObjects/campingCampfire.lua',
    'lua/client/Camping/TimedActions/ISAddTentAction.lua',
    'lua/client/Camping/TimedActions/ISPlaceCampfireAction.lua',
    'lua/client/Camping/TimedActions/ISRemoveTentAction.lua',
    'lua/client/Camping/TimedActions/ISRemoveCampfireAction.lua',
    'lua/server/Camping/camping_tent.lua', 'lua/client/TimedActions/ISRestAction.lua')

CAMP_PLACEMENT = 'Select the exact carried CampfireKit or CampingTentKit through the camping menu when no existing campfire/tent occupies the selected context. Transfer the kit and place its cursor; the outdoor restriction is commented out and no separate hammer is required. The campfire cursor checks one square; the tent checks two adjacent squares, their connecting obstruction and vehicle intersection. Both reject moving/static-moving occupants, but their first non-floor object branch can return before examining later objects. Build walking is bypassed by build cheat; action time is 200 minus five per Woodwork, then Handy subtracts fifty, with instant-action handling and no final floor. The queued cursor is copied. Build validity checks floor/reachability, not all cursor placement predicates or continuing kit possession. Walking/running interrupts. The shared completion can wear a held HammerStone even though these cursors do not require a hammer. Completion assigns the actual character before invoking kit creation. These are local guards and mutations, not a guarantee of native reachability, object creation or synchronized inventory.'

CAMPFIRE_PLACEMENT = 'After the shared build completes, find CampfireKit and queue a zero-time place action. It requires possession of that exact item, removes it from hands, removes inventory by the CampfireKit type string and sends addCampfire coordinates. The server requires a grid square without its existing campfire object, but does not recheck client inventory or all cursor predicates. It creates an unlit campfire with zero fuel and a campfire item container. Installation does not ignite or fuel it. Removing even a lit campfire walks to a safe adjacent square and uses a sixty-time action requiring a refreshed world object; the server drops existing contents, removes the fire/object and requests a new camping.CampfireKit. This does not preserve original kit condition or fuel.'

TENT_PLACEMENT = 'After shared building, find CampingTentKit and queue a zero-time add action whose validity always returns true. It removes inventory by the CampingTentKit type string and sends coordinates/front sprite without continuing exact-item validation. The server checks the first square, absence of a tent there and recognized sprites, then creates the two pieces sequentially; a missing second square can leave the first piece. Tent objects have health/max-health ten and block the square. Front destruction hints request one Base.Tarp, four camping.TentPeg and two Base.WoodenStick even for a kit made with Stakes; these are not extra placement inputs. Each hinted item has a fifty-percent destruction loss. Normal removal walks adjacent and uses a sixty-time action checking object index; the server removes the recognized pair and requests a new camping.CampingTentKit, without preserving original condition. Walking/running interrupts timed actions. Native object/factory delivery and two-cell persistence are separate; no atomic placement guarantee is made.'

TENT_REST = 'Only a recognized placed tent offers these actions, and the camping menu gates both by single-player or server SleepAllowed. Rest requires endurance below 0.75 at selection, walks adjacent and queues ISRestAction; validity requires endurance below one. Start resets exercise state and update invokes native updateEnduranceWhileSitting, not the commented-out regeneration formula; walking/running stops. Time is (1-endurance)*16000. Sleep uses the active world sleep dialog/callback, not the unused ISSleepInTentAction. When sleep is needed, selection rejects fatigue at most 0.3, nearby zombies or at most one hour since sleep; below tablet effect 2000 pain at least two with fatigue at most 0.85 or panic at least one can reject it. Confirmation clears actions and approaches the bed, then always rechecks nearby zombies, pain/panic and exercise-ended state. Client SleepAllowed sets asleep/time-zero and fades before assigning bed/type. Single-player assigns bed/type, computes trait/bed-adjusted random wake time clamped three to sixteen hours and invokes the native sleeping event. Sleep effects, actual endurance recovery, comfort and weather shelter are not inferred from the kit name.'

CAMP_KIT_PREPARATION = 'Use either the complete Plank = 3 or Log = 2 campfire-kit recipe, each with one alternative among RippedSheets, RippedSheetsDirty, Sheet, Book, Magazine, Newspaper or Twigs. The explicit camping import binds absent-local names to unique Base declarations. Time is 50 and Category Survivalist, with no kept tool or callback. The spaced numeric operands are retained verbatim rather than rewritten into consumption semantics. Satisfy native recipe eligibility and do not drive; actual selection, consumption and kit delivery remain native.'

TENT_KIT_PREPARATION = 'Use the complete tent-kit recipe with Tarp, WoodenStick = 2 and either TentPeg = 4 or Stake = 4, Time 120 and Category Survivalist. Explicit camping imports bind the absent-local Base materials while TentPeg remains camping.TentPeg. Each same-named recipe variant retains its own complete clauses; neither is chosen as a declaration winner. No kept tool, skill or callback is specified. Satisfy native recipe eligibility and do not drive. Raw spaced counts and native consumption/result delivery remain separate; destruction return hints do not change these recipe inputs.'

SHOVEL_SMITHING = 'The learned farming-module shovel smithing recipes require Blacksmith 6, NearItem Anvil, the Hammer group and kept Tongs, Time 200 and native eligibility; do not drive. The full shovel requires IronIngot=90 and Handle, while the hand shovel requires IronIngot=50 without Handle. Explicit imports bind unique absent-local Base materials/results. Blacksmith25 or Blacksmith20 requests the corresponding XP amount. Neither recipe declares an OnCreate callback; the unrelated BSItem_OnCreate random condition function does not apply. Keep roles are bound to these exact recipes only. Native anvil recognition, participant selection/consumption, XP delivery and result identity remain separate.'

for _predicate, _ko in (
    (CAMP_PLACEMENT, '캠핑 메뉴에서 정확한 키트를 옮겨 설치 위치를 고른다. 야외 제한과 별도 망치 요구는 없다. 모닥불은 한 칸, 텐트는 인접 두 칸과 사이 장애물·차량 겹침을 검사하지만 첫 바닥 외 물체에서 검사를 끝낼 수 있다. 치트 외에는 이동하며 공통 건축 시간과 목공·Handy 보정을 쓴다. 큐에는 커서 사본을 넣고 층·접근 가능성을 검사하지만 위치 조건과 키트 보유를 모두 다시 검사하지는 않는다. 창문 접근 보조 함수에는 self 참조 문제가 있다. 걷기·달리기로 중단하며 완료 시 손에 든 돌망치가 있다면 공통 내구도 감소가 적용될 수 있다. 물체 생성·동기화 성공은 엔진 처리에 달려 있다.'),
    (CAMPFIRE_PLACEMENT, '건축 완료 뒤 정확한 모닥불 키트를 소지했는지 검사하는 즉시 설치 동작을 넣고 손에서 해제한 후 종류 이름으로 소비한다. 서버는 칸과 기존 모닥불 유무를 검사하고 연료 0·불이 꺼진 모닥불을 만든다. 설치만으로 점화되지 않는다. 제거는 안전한 인접 칸으로 이동하는 시간 60 동작이며 불이 켜져 있어도 가능하다. 서버는 내용물을 바닥에 놓고 불과 물체를 없앤 뒤 새 키트를 요청한다. 원래 키트 상태나 연료는 보존하지 않는다.'),
    (TENT_PLACEMENT, '건축 완료 뒤 키트를 종류 이름으로 소비하는 즉시 동작을 넣으며 해당 동작은 보유를 다시 검사하지 않는다. 서버는 첫 칸과 텐트·스프라이트를 검사한 뒤 두 부분을 차례로 만들므로 둘째 칸이 없으면 첫 부분만 남을 수 있다. 체력 10의 물체가 칸을 막는다. 파괴 시 타프 1·텐트 말뚝 4·나무 막대 2를 각각 절반 확률로 잃으며 이 목록은 추가 설치 재료가 아니다. 정상 제거는 인접 이동·시간 60·물체 인덱스 확인 뒤 두 부분을 제거하고 새 키트를 요청한다. 원래 상태 보존이나 두 칸의 원자적 생성을 보장하지 않는다.'),
    (TENT_REST, '설치된 텐트를 인식하고 싱글플레이이거나 서버가 수면을 허용해야 휴식·수면 메뉴가 나온다. 휴식은 지구력 0.75 미만에서 선택하고 인접해 지구력 1 미만 동안 엔진의 앉은 지구력 갱신을 호출한다. 걷기·달리기로 멈춘다. 수면은 활성 월드 수면 확인창을 통해 피로·좀비·통증·공황·최근 수면과 운동 상태 조건을 적용하며 접근 후 좀비·통증·공황 등을 다시 검사한다. 멀티플레이 수면 분기는 침대 속성 설정 전에 잠듦을 적용하며 싱글플레이는 침대·특성에 따른 임의 기상 시간을 3~16시간으로 제한한다. 비바람 차단·편안함·실제 회복 효과는 키트 이름에서 추론하지 않는다.'),
    (CAMP_KIT_PREPARATION, '널빤지 = 3 또는 통나무 = 2 제조법 중 하나에서 찢어진 천·더러운 천·시트·책·잡지·신문·잔가지 중 하나를 함께 제공한다. 캠핑 모듈의 명시적 import로 재료를 연결하며 시간 50·생존 분류이고 도구나 콜백은 없다. 운전 중에는 제작할 수 없고 엔진의 제작 조건을 만족해야 한다. 원문의 공백 포함 수량 표기는 그대로 보존하며 실제 소비·결과 전달을 확정하지 않는다.'),
    (TENT_KIT_PREPARATION, '타프·나무 막대 = 2에 텐트 말뚝 = 4 또는 일반 말뚝 = 4를 더하는 각 제조법을 구분한다. 시간 120·생존 분류이며 도구·기술·콜백 요구는 없다. 명시적 import와 로컬 텐트 말뚝을 구분하고 운전 중에는 제작할 수 없다. 엔진의 제작 조건·수량 처리·결과 전달은 별도이며 파괴 시 반환 목록을 제조법 입력으로 바꾸지 않는다.'),
    (SHOVEL_SMITHING, '학습한 농사 모듈 단조법은 대장장이 6·모루 근처·망치 그룹·보존하는 집게와 시간 200을 요구한다. 삽은 철괴 90·손잡이, 손삽은 철괴 50을 요구하며 각각 대장장이 경험치 25·20을 요청한다. 운전 중에는 만들 수 없고 엔진의 제작 조건을 만족해야 한다. 이 두 제조법에는 생성 콜백이 없으므로 별도 무작위 내구도 콜백을 붙이지 않는다. 모루 인식·선택·소비·경험치와 결과 전달은 엔진 처리에 달려 있다.')):
    QUALIFIERS[_predicate] = (_ko, _predicate)

for _name, _ko, _en in (
    ('place_campfire', '모닥불을 설치할 수 있다.', 'It can place a campfire.'),
    ('pitch_tent', '텐트를 설치할 수 있다.', 'It can pitch a tent.'),
    ('rest_at_placed_tent', '설치한 텐트에서 휴식·수면 동작을 선택할 수 있다.', 'The placed tent offers rest and sleep actions.')):
    FUNCTIONS[_name] = (_name.replace('_', ' '), _ko, _en)

RADIO_PRESET_EDITOR = 'lua/client/RadioCom/RadioWindowModules/RWMSubEditPreset.lua'

RADIO_GENERAL = 'lua/client/RadioCom/RadioWindowModules/RWMGeneral.lua'

RADIO_FIELDS = {'AcceptMediaType', 'AttachmentType', 'BaseVolumeRange', 'ConditionMax', 'DisappearOnUse',
    'DisplayCategory', 'DisplayName', 'Icon', 'IsHighTier', 'IsPortable', 'IsTelevision', 'MaxChannel',
    'MicRange', 'MinChannel', 'NoTransmit', 'StaticModel', 'Tooltip', 'TransmitRange', 'TwoWay', 'Type',
    'UseDelta', 'UseWhileEquipped', 'UsesBattery', 'Weight', 'WorldObjectSprite', 'WorldStaticModel'}

RADIO_PRESETS = 'The nontelevision, non-NoTransmit channel panel edits its device preset list. Mouse buttons are enabled while turned on; add checks list size below the device maximum, edit/delete require a valid selected index. The editor uses device min/max frequency divided by 1000 and a slider; save replaces an empty/nil name with Unnamed and multiplies frequency by 1000. The default add frequency is half the range width, not the range midpoint. Add/edit/delete mutate the preset objects/list and request transmitPresets without a timed action or walk-to call. Save does not recheck power, maximum size, name whitespace or continued device possession; the joypad edit/add/delete callbacks do not independently check power. This changes stored presets, not the current channel until Tune is separately invoked. Native preset storage/transmission and slider limits remain separate.'

RADIO_MEDIA_CONTROL = 'A device with a nonnegative media type exposes the media panel. Insert accepts recorded media of the matching type into an empty slot; the non-joypad path selects the first dropped item and joypad offers a selection. Remove requires only hasMedia, then requests removeMediaItem into the character inventory. Play/stop requires an on device with media, without a separate positive-power check; it calls StartPlayMedia or StopPlayMedia. Panel update also stops playing when off. These thirty-time actions allow walking, stop on running, and first require adjacent world access or occupancy of the same vehicle; the action does not continuously recheck access or donor inventory membership. Exact media identity returned, recording execution and delivered lines/effects are native; controls do not guarantee playback.'

RADIO_HEADPHONE_CONTROL = 'A portable nontelevision volume panel accepts exact Base.Headphones or Base.Earbuds when its slot is empty; removal requires headphone type at least zero. The thirty-time action passes the selected item to addHeadphones or requests getHeadphones into the player inventory. It allows walking and stops on running. World adjacency or same-vehicle occupancy is required when queued, without a continuing access/possession or power check. The native device owns item consumption/return and audible routing; a selected headphone is not guaranteed to be the identical returned instance.'

RADIO_WINDOW_LIFETIME = 'The inventory device window remains open while the exact radio is held in either hand. World/vehicle windows require x/y distance strictly below ten; this window check has no z comparison. A vehicle part with declared item types but no installed inventory item closes. Otherwise closing or losing the inventory window state turns its device off. Timed radio actions check their operation-specific device-data guards, not the full continuing window/hand/access conditions. The general panel only displays native device/channel/range properties; it does not implement signal propagation.'

RADIO_WORLD_FORM = 'The registered Moveable context accepts a main-inventory radio not held in either hand only when its native world-static-item getter does not select the ordinary 3D placement route. A declared WorldObjectSprite supplies a candidate sprite, whose actual Moveable/type/grid properties remain native. The cursor and move action require valid placement, available parts, same floor, distance at most 1.6 per axis, reachability and multiplayer safehouse permission; walking/running stops the action. Completion re-finds the item and rechecks placement. For an IsoRadio/IsoTelevision sprite with a Radio item, placement creates the corresponding object, re-applies its current turned-on value through device data, assigns that data and removes the inventory item. Pickup of an IsoWaveSignal copies its device data to the created item before removing the world object. Factories, sprite identity, radio placement permission and persistent delivery remain native; no original inventory-instance preservation or unconditional powered placement is inferred.'

RADIO_CODE_EFFECTS = 'Only a native-delivered OnDeviceText line associated with this device or assigned recording reaches the shared Lua decoder; this source does not establish that association or delivery. It considers up to four local living players, on the same floored z and within five in x/y unless coordinates are all minus one. A present source square must agree with the player indoor/outdoor state, and sleeping players are excluded. A nonempty GUID already known is skipped; a new one is marked known before checking line/codes, so an empty line can still mark it. Comma codes use a three-character registry key, an operator and numeric suffix: minus negates, equals selects absolute setting, otherwise adjustment. Boredom/unhappiness adjust by five times the amount and clamp 0..100; panic also uses five and 0..100; other registered stats adjust by 0.05 and clamp 0..1. Positive skill amounts request fifty times the amount as XP; nonpositive amounts do not grant XP. Numeric codes have per-player/per-code cooldown 30, reduced by game multiplier each tick; GUID marking precedes cooldown and may prevent a skipped code being retried. RCP codes request learning the named recipe without that cooldown, regardless of operator. The generic stat helper checks the getter twice rather than validating a setter, so a missing native setter can fail. Native getter/setter availability, XP/recipe delivery, known-line state and actual recording/broadcast assignment are not guaranteed by the item name or controls.'

PAINT_ACTIONS = 'The active callbacks always use the paint cursor. Outside build cheat it requires a recursively carried Paintbrush and the exact paint type, without a remaining-use check, and transfers both before queuing. The cursor requires a visible square and compatible Painting/OtherPainting mapping; signs require WallN or WallW. The mouse surface menu leaves its local modData nil, so it may omit a thumpable option that the joypad cursor can select. The cursor skips the shared build action but still calls its walk-to path; paint/sign actions take 100, or one in build cheat, and stop on walking/running. Their validity always returns true: they do not continuously recheck brush, paint, target or mapping. Surface completion clears wall blood, applies the mapped sprite or custom color and transmits that update, then uses paint once unless cheat. Sign completion applies the requested overlay and color, adding eight for WallW, and uses paint once unless cheat. A missing mapping may fail after blood clearing. No color durability, protective effect, continued possession guarantee or native depleted-bucket identity is inferred.'

for _predicate, _ko in (
    (RADIO_PRESETS, 'TV가 아니고 NoTransmit이 아닌 기기의 채널 목록에 프리셋을 추가·편집·삭제한다. 마우스 버튼은 전원이 켜져 있을 때 활성화되며 추가는 최대 개수, 편집·삭제는 선택 인덱스를 검사한다. 빈 이름은 Unnamed로 바꾸고 표시 주파수에 1000을 곱해 저장·전송 요청한다. 별도 이동·시간 동작은 없으며 저장 시 전원·최대 개수·계속 소지를 재검사하지 않고 조이패드 콜백에도 자체 전원 검사가 없다. 현재 채널은 별도 맞추기 동작 전에는 바뀌지 않는다. 실제 목록 저장·전송은 엔진 처리다.'),
    (RADIO_MEDIA_CONTROL, '미디어 유형이 있는 기기의 빈 슬롯에 같은 유형의 기록 매체를 넣는다. 제거는 매체 존재만 확인하고 인벤토리 반환을 요청한다. 재생·정지는 켜진 기기와 매체를 요구하지만 양의 전력을 별도로 검사하지 않는다. 꺼지면 패널 갱신도 재생을 멈춘다. 시간 30이며 걷기는 허용하고 달리면 중단한다. 큐에 넣을 때 월드 인접·동일 차량 탑승을 요구하지만 동작은 접근·매체 보유를 계속 검사하지 않는다. 실제 반환품·재생·내용 효과는 엔진 전달에 달려 있다.'),
    (RADIO_HEADPHONE_CONTROL, '휴대 가능한 TV 외 기기는 빈 슬롯에 정확한 헤드폰·이어버드를 받고, 헤드폰 유형 값이 0 이상이면 제거해 인벤토리로 반환하도록 요청한다. 시간 30이며 걷기는 허용하고 달리면 중단한다. 큐에 넣기 전 월드 인접·동일 차량 접근을 요구하지만 동작은 계속 보유·접근·전원을 검사하지 않는다. 실제 소비·반환품 동일성·소리 전달은 기기 데이터에 달려 있다.'),
    (RADIO_WINDOW_LIFETIME, '소지 기기는 같은 물품을 한 손에 들고 있어야 창이 유지된다. 월드·차량 창은 x·y 거리가 각각 10 미만이어야 하며 이 검사는 층을 비교하지 않는다. 장착 물품이 사라진 차량 부품은 창을 닫는다. 소지 기기의 창 상태를 잃으면 전원을 끈다. 시간 동작은 각 기기 데이터 조건을 검사하며 창·손·접근 조건 전체를 계속 검사하지 않는다. 일반 정보 패널은 속성을 표시할 뿐 신호를 전파하지 않는다.'),
    (RADIO_WORLD_FORM, '주 소지품에 있고 손에 들지 않았으며 일반 3D 배치로 선택되지 않는 라디오가 이동 물체 배치 경로를 사용할 수 있다. 스프라이트의 실제 속성·필수 조각·공간 조건을 만족해야 한다. 동작은 같은 층·축별 거리 1.6 이내·접근·멀티플레이 안전가옥 권한을 검사하며 걷기·달리기로 중단한다. 완료 시 물품과 배치 조건을 다시 찾고 대응 라디오·TV 물체에 기기 데이터를 넘긴 후 소지품에서 제거한다. 회수 시 월드 기기 데이터도 새 물품에 복사한다. 원래 인벤토리 인스턴스나 전원 상태가 무조건 보존되는 것은 아니다.'),
    (RADIO_CODE_EFFECTS, '이 기기나 배정된 매체에서 실제 전달된 문장 코드에만 공통 처리기가 적용된다. 깨어 있는 살아 있는 로컬 플레이어 중 같은 층·좌우 앞뒤 5 범위와 실내외 일치 조건을 검사하며 좌표가 모두 -1이면 거리 제한을 생략한다. 이미 안 GUID는 제외하고 새 GUID는 내용 검사보다 먼저 기록한다. 숫자 코드는 기분·공황에 사용량의 5배, 다른 통계에 0.05배를 더하거나 지정값을 설정해 범위를 제한한다. 양의 기술 코드는 50배 경험치를 요청하고 제조법 코드는 학습을 요청한다. 숫자 코드별 재사용 대기 30은 게임 배율로 감소하며 GUID가 먼저 기록돼 대기 중 놓친 코드가 재시도되지 않을 수 있다. 일반 통계 보조 함수는 setter 대신 getter를 두 번 검사한다. 실제 방송·녹화물 연결, 통계 함수, 경험치·학습 전달은 엔진 경계다.'),
    (PAINT_ACTIONS, '활성 경로는 도색 커서를 사용한다. 치트 외에는 정확한 붓·페인트를 재귀 소지품에서 찾아 옮기지만 잔량은 검사하지 않는다. 보이는 칸과 대응 도색 매핑이 필요하며 표식은 북·서 벽에 쓴다. 마우스 메뉴의 modData 누락으로 조이패드에서 가능한 일부 면이 빠질 수 있다. 공통 건축 동작은 생략하지만 접근 이동은 수행하고 시간 100·치트 1이며 걷기·달리기로 중단한다. 동작은 도구·대상·매핑을 계속 재검사하지 않는다. 도색은 벽 혈흔을 지운 뒤 스프라이트나 색을 설정·전송하고 표식은 방향 보정한 오버레이를 설정한다. 치트 외에는 페인트를 한 번 사용한다. 매핑 오류는 혈흔 제거 후 실패할 수도 있으며 내구성·보호 효과·빈 통 반환을 보장하지 않는다.')):
    QUALIFIERS[_predicate] = (_ko, _predicate)

for _name, _ko, _en in (
    ('edit_radio_presets', '라디오 채널 프리셋을 추가·편집·삭제할 수 있다.', 'Its radio presets can be added, edited or removed.'),
    ('control_device_media', '기기의 매체 삽입·제거·재생·정지를 조작할 수 있다.', 'Its media insertion, removal and play/stop controls can be used.'),
    ('control_device_headphones', '기기에 헤드폰을 연결하거나 제거할 수 있다.', 'Headphones can be connected to or removed from the device.'),
    ('place_radio_world_form', '배치 조건을 만족하면 라디오·TV를 월드 기기 형태로 놓을 수 있다.', 'It can be placed as a world radio or television when placement conditions hold.')):
    FUNCTIONS[_name] = (_name.replace('_', ' '), _ko, _en)

EFFECTS['delivered_media_code_outcome', 'apply_configured_code'] = ('전달된 매체 코드에 따라 통계·경험치·제조법 학습 처리가 적용될 수 있다.', 'Delivered media codes can apply their configured stat, XP or recipe-learning operations.')

HAIR_CUT = 'lua/client/TimedActions/ISCutHair.lua'

CRAFT_UI = 'lua/client/ISUI/ISCraftingUI.lua'

_splint_ko = QUALIFIERS[SPLINTING][0]

SPLINTING += ' Time is 140 minus four per actual Doctor level, or one for instant actions; the non-None access level override is applied after timing.'

QUALIFIERS[SPLINTING] = (_splint_ko + ' 시간은 실제 시술 기술별 4를 140에서 빼며 즉시 동작은 1이다. 관리 권한의 기술 덮어쓰기는 시간 계산 후 적용된다.', SPLINTING)

BLOOD_CLEANING = 'The nonvehicle world menu opens the blood-cleaning cursor. Its square must exist and have blood, with recursive Bleach plus Mop, unbroken Broom, DishCloth or BathTowel. Walk adjacent, select the tool in that priority, transfer supplies and equip mop/broom in both hands or towel/cloth with bleach. Time is 150, or one when instant. The action requires some named cleaning tool and Bleach in inventory, not necessarily the originally selected instance, and does not recheck blood or broom brokenness. Walking/running stops. Completion finds Bleach, increases its ThirstChange by 0.05 and calls Use only if the new value exceeds -0.05, then removes square blood with both flags false. It never uses the cleaning tool. No clothing/body/wound cleaning, complete bleach-bottle consumption or native blood synchronization guarantee is inferred.'

QUALIFIERS[BLOOD_CLEANING] = ('차량 밖에서 혈흔 청소 커서를 열고 혈흔이 있는 칸과 재귀 소지품의 표백제·대걸레·파손되지 않은 빗자루·행주·목욕 수건 중 하나가 필요하다. 가까이 이동해 순서대로 도구를 고르고 옮겨 장비한다. 시간 150·즉시 1이며 걷기·달리기로 중단한다. 계속 표백제와 해당 종류 도구가 필요하지만 원래 물품·혈흔·빗자루 파손 여부는 다시 검사하지 않는다. 완료 시 표백제 ThirstChange에 0.05를 더하고 새 값이 -0.05보다 클 때만 Use를 호출한 뒤 칸의 혈흔을 제거한다. 청소 도구는 소비하지 않으며 의류·몸·상처 청소가 아니다.', BLOOD_CLEANING)

FORGE_PREPARATION = 'Use the selected learned anvil recipe with its exact supplied material and kept hammer/tongs or ammunition mold, and its declared Blacksmith threshold. The reviewed variants require levels two through ten and time 120 through 300; these are alternatives, not combined prerequisites. The action must remain RecipeManager-valid and the character must not drive. Completion delegates creation/consumption to PerformMakeItem; the selected XP callback requests ten, fifteen, twenty or twenty-five Blacksmith XP. Only variants explicitly naming BSItem_OnCreate run its HandWeapon-only condition calculation: choose ZombRand(5+skill*5,10+skill*10), subtract twenty without a BallPeenHammer currently in inventory, clamp five through one hundred and round conditionMax times that percentage. Other variants have no such callback. Make Roasting Pan actually declares Pot, not RoastingPan. Native eligibility, numeric ingredient units, output count/delivery and condition binding remain separate; no assumed tool consumption or guaranteed perfect weapon is inferred.'

WELDED_PARTS = 'Use the selected learned metal-part recipe, its exact metal inputs, BlowTorch=2 and a kept WeldingMask-group item. Pipe creation has no declared skill threshold; the bar needs MetalWelding two and sheet conversions need four. Times are 150 for pipe/bar or 250 for sheets; the actual callbacks request ten or twenty-five MetalWelding XP. SmallSheetMetal=4 produces the declared SheetMetal form while SheetMetal declares SmallSheetMetal=3, so they are not lossless reverses. RecipeManager validity and not driving apply; native ingredient-use units, result creation/count and delivery remain separate. No protective property, full blowtorch consumption or perfect reversibility is inferred.'

LOG_BINDING = 'Select the exact two-, three- or four-log recipe with Log=count and two CraftLogStack-group supplies selected by the Rope tag. The recipe allows floor input, takes sixty and requests no XP. CreateLogStack records every supplied non-Base.Log FullType in result modData.ropeItems without assuming it was Base.Rope. The reverse recipe takes its exact LogStacks form, allows floor input and declares the corresponding Log count. SplitLogStack reads items:get(0) ropeItems: missing data requests two Base.Rope; otherwise it requests each stored FullType. The actual ItemManager result creation/count, supplied-item ordering and modData persistence remain native. Neither arbitrary stack splitting nor preservation of rope condition or guaranteed return delivery is inferred. RecipeManager validity, not driving and interruption still apply.'

MATTRESS_PREPARATION = 'The exact mattress recipe keeps a SewingNeedle-group tool and declares Thread=5, Sheet=5 and Pillow=5, result Mattress, time 180 and category Carpentry. RecipeManager validity and not driving apply. These supplies serve assembly, not a direct pillow sleep or bedding-comfort action. Numeric drainable units, inventory consumption and native result delivery remain separate; no additional skill, learned-recipe requirement or callback is declared.'

FROG_PREPARATION = 'The exact Slice Frog recipe supplies the Normal Base.Frog and keeps a SharpKnife-group item or MeatCleaver, declares FrogMeat, time fifty and SliceMeat sound, and its callback requests ten Cooking XP. RecipeManager validity and not driving apply. This is preparation of a distinct Food result, not eating the Normal frog; native creation and delivery remain separate and no unlisted cooking, freshness or disease effect is inferred.'

WIRE_RECOVERY = 'The exact learned Get Wire Back recipe supplies BrokenFishingNet, takes one hundred and declares the raw Result:Wire;3. That semicolon spelling is retained without converting it to equals or inventing a native result interpretation. RecipeManager validity and not driving apply. The broken net is a transformation input; actual eligibility, consumption, Wire identity and count require the native Result parser/executor. No positive three-wire yield or intact net reuse is asserted.'

for _predicate, _ko in (
    (FORGE_PREPARATION, '선택한 학습된 모루 제조법의 정확한 금속 재료와 보존하는 망치·집게 또는 탄약 틀을 제공한다. 제조법별 단조 기술 2~10과 시간 120~300은 서로 다른 선택지 조건이다. 제작 유효성과 운전하지 않음이 필요하고 해당 콜백은 단조 경험치 10·15·20·25를 요청한다. BSItem_OnCreate를 명시한 무기 결과만 기술별 임의 내구도를 계산하며 현재 볼핀 해머가 없으면 20을 빼고 5~100%로 제한한다. 다른 제조법에 이 콜백을 붙이지 않는다. 로스팅 팬이라는 제조법도 실제 결과는 Pot이다. 소비 단위·결과 전달·내구도 결속은 엔진 경계다.'),
    (WELDED_PARTS, '학습한 금속 부품 제조법의 재료와 토치 사용량 2, 보존하는 용접 마스크 그룹 도구를 제공한다. 파이프는 기술 조건이 선언되지 않고 금속 막대는 용접 2, 판 변환은 4가 필요하다. 시간은 150 또는 250이며 용접 경험치 10 또는 25를 요청한다. 작은 판 넷으로 판 하나, 판 하나로 작은 판 셋을 선언하므로 무손실 역변환이 아니다. 제작 유효성·운전 금지 및 실제 소비 단위·결과 전달의 엔진 경계를 유지한다.'),
    (LOG_BINDING, '정확한 통나무 2·3·4개와 로프 태그 공급 두 개로 묶음을 만들며 바닥 재료 허용·시간 60·경험치 없음이다. 생성 콜백은 통나무 외 제공 물품의 정확한 형식 목록을 묶음에 저장한다. 대응 묶음을 풀면 선언된 통나무 수와 함께 저장한 형식을 돌려주도록 요청하고 저장 데이터가 없으면 Base.Rope 둘을 요청한다. 공급 순서·데이터 지속·결과 수량과 전달은 엔진 경계이며 밧줄의 원래 상태나 반환 성공을 보장하지 않는다.'),
    (MATTRESS_PREPARATION, '보존하는 재봉 바늘 그룹 도구와 실·시트·베개 각각 선언량 5로 시간 180의 매트리스 제조법에 참여한다. 직접 수면이나 안락함 효과가 아니며 별도 기술·학습·콜백은 선언되지 않는다. 제작 유효성·운전 금지와 실제 소비·결과 전달의 엔진 경계를 유지한다.'),
    (FROG_PREPARATION, '일반형 Base.Frog를 제공하고 날카로운 칼 그룹 또는 식칼을 보존하여 시간 50의 손질 제조법으로 FrogMeat를 선언하며 요리 경험치 10을 요청한다. 일반형 개구리를 먹는 동작이 아니고 실제 결과 전달·신선도는 별도다. 제작 유효성과 운전하지 않음이 필요하다.'),
    (WIRE_RECOVERY, '학습한 철사 회수 제조법은 부서진 통발을 제공하고 시간 100 및 원문 Result:Wire;3을 선언한다. 세미콜론을 등호로 고치거나 철사 세 개 반환으로 해석하지 않는다. 제작 유효성·운전 금지가 필요하며 실제 결과 이름·수량·소비는 엔진의 해당 구문 처리에 달려 있다. 통발을 그대로 재사용하는 동작은 아니다.')):
    QUALIFIERS[_predicate] = (_ko, _predicate)

for _name, _ko, _en in (
    ('unbundle_logs', '대응하는 통나무 묶음 풀기 제조법에 제공할 수 있다.', 'It can be supplied to its corresponding log-unstacking recipe.'),
    ('prepare_frog_meat', '칼을 사용하는 개구리 고기 손질 제조법에 제공할 수 있다.', 'It can be supplied to the knife-based frog-meat preparation recipe.'),
    ('process_broken_fish_net', '부서진 통발의 철사 회수 제조법에 제공할 수 있다.', 'It can be supplied to the broken-net wire-recovery recipe.')):
    FUNCTIONS[_name] = (_name.replace('_', ' '), _ko, _en)

FOOD_ASSEMBLY = 'Supply the exact accepted ingredients, vessels and kept utensils of the selected reviewed preparation. RecipeManager eligibility and not driving apply; learning is required only where declared. Raw semicolon/equal quantities, Water pseudo-operand selection, consumption, result identity/count and native food defaults remain separate. No automatic cooking or preservation is inferred from a Cooking category. The callback-free assembly recipes declare no additional local test or result mutation; category, time and any Cooking XP request remain source metadata.'

QUALIFIERS[FOOD_ASSEMBLY] = ('선택한 음식 준비법에서 허용하는 재료와 용기·도구가 필요하다. 학습을 요구하는 준비법은 먼저 익혀야 하며 운전 중에는 제작할 수 없다.', FOOD_ASSEMBLY)

FOOD_SLICING = 'Supply the exact accepted ingredients, vessels and kept utensils of the selected reviewed preparation. RecipeManager eligibility and not driving apply; learning is required only where declared. Raw semicolon/equal quantities, Water pseudo-operand selection, consumption, result identity/count and native food defaults remain separate. No automatic cooking or preservation is inferred from a Cooking category. SliceWatermelon divides hunger, boredom, unhappiness and nutrition by ten; SliceBread divides those by three; SliceHam handles Ham/Baloney and divides them by six; SliceSalami divides them by five although the declaration yields four. These callbacks do not copy thirst or freshness. No corrected five-slice Salami yield is invented.'

QUALIFIERS[FOOD_SLICING] = ('선택한 손질법에 맞는 음식과 보존 도구가 필요하며 운전 중에는 할 수 없다.', FOOD_SLICING)

COOKED_SLICING = 'Supply the exact accepted ingredients, vessels and kept utensils of the selected reviewed preparation. RecipeManager eligibility and not driving apply; learning is required only where declared. Raw semicolon/equal quantities, Water pseudo-operand selection, consumption, result identity/count and native food defaults remain separate. No automatic cooking or preservation is inferred from a Cooking category. SliceCooked accepts non-Food arguments and requires a present cooked or burnt Food argument. SlicePie divides hunger, thirst, mood and nutrition by five and requests a BakingPan return. It does not independently copy cooked/burnt/freshness state; native result delivery remains separate.'

QUALIFIERS[COOKED_SLICING] = ('선택한 파이·케이크 손질법의 도구가 필요하며 음식은 익었거나 탄 상태여야 한다. 운전 중에는 할 수 없다.', COOKED_SLICING)

DOUGH_SLICING = 'Supply the exact accepted ingredients, vessels and kept utensils of the selected reviewed preparation. RecipeManager eligibility and not driving apply; learning is required only where declared. Raw semicolon/equal quantities, Water pseudo-operand selection, consumption, result identity/count and native food defaults remain separate. No automatic cooking or preservation is inferred from a Cooking category. SliceBreadDough tests cooked state only for exact Base.BreadDough. Its callback copies burnt=true when applicable, divides base hunger by three into both base and current hunger, and divides thirst, mood and nutrition by three. Freshness is not set here.'

QUALIFIERS[DOUGH_SLICING] = ('빵 반죽을 자를 때는 익힌 반죽과 지정된 칼이 필요하며 운전 중에는 할 수 없다.', DOUGH_SLICING)

PIZZA_SLICING = 'Supply the exact accepted ingredients, vessels and kept utensils of the selected reviewed preparation. RecipeManager eligibility and not driving apply; learning is required only where declared. Raw semicolon/equal quantities, Water pseudo-operand selection, consumption, result identity/count and native food defaults remain separate. No automatic cooking or preservation is inferred from a Cooking category. SlicePizza accepts exact type PizzaWhole directly; other selected items require cooked or burnt state. Completion uses the selected item, copies true burnt/cooked flags, divides hunger and nutrients by six, copies the full unmodified-by-division boredom/unhappiness getters, assigns a slice name and removes the selected item. No six-way mood division is inferred.'

QUALIFIERS[PIZZA_SLICING] = ('피자 손질 도구가 필요하다. 완성 피자 형식 이외에는 익었거나 탄 피자를 선택해야 하며 운전 중에는 할 수 없다.', PIZZA_SLICING)

FISH_PREPARATION = 'Supply the exact accepted ingredients, vessels and kept utensils of the selected reviewed preparation. RecipeManager eligibility and not driving apply; learning is required only where declared. Raw semicolon/equal quantities, Water pseudo-operand selection, consumption, result identity/count and native food defaults remain separate. No automatic cooking or preservation is inferred from a Cooking category. CutFish tests every Food argument for ActualWeight > 0.6. It selects the first Food, halves the larger of base/current hunger, sets custom weight to 0.9 of source weight divided by two, halves nutrition and copies cooked state. Neither freshness nor guaranteed fillet delivery is assigned by this callback.'

QUALIFIERS[FISH_PREPARATION] = ('생선 손질 도구가 필요하고 생선의 실제 무게가 0.6보다 커야 하며 운전 중에는 할 수 없다.', FISH_PREPARATION)

ANIMAL_PREPARATION = 'Supply the exact accepted ingredients, vessels and kept utensils of the selected reviewed preparation. RecipeManager eligibility and not driving apply; learning is required only where declared. Raw semicolon/equal quantities, Water pseudo-operand selection, consumption, result identity/count and native food defaults remain separate. No automatic cooking or preservation is inferred from a Cooking category. CutAnimal selects the first Food, sets hunger to current hunger times 1.05 with a lower bound of -100, weight to source weight times 0.7 and nutrition to source times 0.75. It does not assign freshness or cooked state. The recipe requests Cooking10 XP.'

QUALIFIERS[ANIMAL_PREPARATION] = ('선택한 작은 동물 손질법에서 허용하는 사체와 칼이 필요하며 운전 중에는 할 수 없다.', ANIMAL_PREPARATION)

SANDWICH_PREPARATION = 'Supply the exact accepted ingredients, vessels and kept utensils of the selected reviewed preparation. RecipeManager eligibility and not driving apply; learning is required only where declared. Raw semicolon/equal quantities, Water pseudo-operand selection, consumption, result identity/count and native food defaults remain separate. No automatic cooking or preservation is inferred from a Cooking category. WholeBreadSlices returns true for items without BreadSlices tag. Tagged fresh slices require absolute hunger change >= absolute base hunger; other tagged slices require >= 0.75 of absolute base hunger. Equality passes. There is no local result callback.'

QUALIFIERS[SANDWICH_PREPARATION] = ('치즈 샌드위치를 만들 때는 허용하는 빵과 치즈가 필요하며 빵 조각은 신선도에 따른 남은 양 조건을 만족해야 한다. 운전 중에는 할 수 없다.', SANDWICH_PREPARATION)

GRAIN_VESSEL_PREPARATION = 'Supply the exact accepted ingredients, vessels and kept utensils of the selected reviewed preparation. RecipeManager eligibility and not driving apply; learning is required only where declared. Raw semicolon/equal quantities, Water pseudo-operand selection, consumption, result identity/count and native food defaults remain separate. No automatic cooking or preservation is inferred from a Cooking category. AddBaseIngredientToCookingVessel copies condition from each WaterPot or WaterSaucepan to the result; it does not locally set cooked state, water safety or nutritional outcome. The original vessel is a destroy participant, not a kept tool.'

QUALIFIERS[GRAIN_VESSEL_PREPARATION] = ('허용하는 쌀 또는 파스타와 물이 든 냄비·소스팬이 필요하며 운전 중에는 할 수 없다.', GRAIN_VESSEL_PREPARATION)

OATMEAL_PREPARATION = 'Supply the exact accepted ingredients, vessels and kept utensils of the selected reviewed preparation. RecipeManager eligibility and not driving apply; learning is required only where declared. Raw semicolon/equal quantities, Water pseudo-operand selection, consumption, result identity/count and native food defaults remain separate. No automatic cooking or preservation is inferred from a Cooking category. MakeOatmeal sets result heat to 2.5 and cooked=true, despite no active Heat requirement; the nearby CanBeDoneFromFloor/Heat lines are commented out. Water safety and engine delivery are not guaranteed.'

QUALIFIERS[OATMEAL_PREPARATION] = ('그릇과 귀리·물이 필요하며 운전 중에는 준비할 수 없다.', OATMEAL_PREPARATION)

WOOD_SHAPING = 'The complete Make Stake and Drill Plank recipes require their declared branch or plank/log and kept sharp/dull knife, screwdriver or chipped-stone alternatives respectively. RecipeManager eligibility and not driving apply. Make Stake requests WoodWork5 XP. Drill Plank has no callback and its Prop source slots are animation metadata. Result construction and delivered identity remain native; no spark generation is inferred from making drilled wood.'

QUALIFIERS[WOOD_SHAPING] = ('선택한 목재 가공법에서 허용하는 목재와 보존 도구가 필요하며 운전 중에는 할 수 없다.', WOOD_SHAPING)

FOOD_PREPARATION_RECIPES = (
    ('Base', 'Make Meat Patty', ['MincedMeat;40', 'Result:MeatPatty', 'Time:30.0', 'Category:Cooking'], 'food_preparation', FOOD_ASSEMBLY),
    ('Base', 'Make Cheese Sandwich', ['BreadSlices', '[Recipe.GetItemTypes.Cheese];5', 'Result:CheeseSandwich', 'OnTest:Recipe.OnTest.WholeBreadSlices', 'Time:50.0', 'Category:Cooking'], 'food_preparation', SANDWICH_PREPARATION),
    ('Base', 'Butcher Small Animal', ['keep [Recipe.GetItemTypes.SharpKnife]/MeatCleaver', 'DeadMouse/DeadSquirrel/DeadRat', 'Result:Smallanimalmeat', 'Sound:PZ_FoodSwoosh', 'Time:50.0', 'OnCreate:Recipe.OnCreate.CutAnimal', 'Category:Cooking', 'OnGiveXP:Recipe.OnGiveXP.Cooking10'], 'animal_butchery', ANIMAL_PREPARATION),
    ('Base', 'Slice Watermelon', ['Watermelon', 'keep [Recipe.GetItemTypes.SharpKnife]/[Recipe.GetItemTypes.Saw]/Axe/HandAxe/AxeStone/WoodAxe/MeatCleaver', 'Result:WatermelonSliced=10', 'OnCreate:Recipe.OnCreate.SliceWatermelon', 'Time:70.0', 'Category:Cooking', 'OnGiveXP:Recipe.OnGiveXP.Cooking3', 'AllowRottenItem:true'], 'food_portioning', FOOD_SLICING),
    ('Base', 'Place Pasta in Cooking Pot', ['Pasta;10', 'destroy WaterPot', 'Result:WaterPotPasta', 'Time:50.0', 'OnCreate:Recipe.OnCreate.AddBaseIngredientToCookingVessel', 'Category:Cooking', 'OnGiveXP:Recipe.OnGiveXP.None'], 'grain_preparation', GRAIN_VESSEL_PREPARATION),
    ('Base', 'Slice Ham', ['keep [Recipe.GetItemTypes.SharpKnife]/MeatCleaver', 'Ham', 'Result:HamSlice=6', 'OnCreate:Recipe.OnCreate.SliceHam', 'Sound:SliceMeat', 'Time:50.0', 'Category:Cooking', 'OnGiveXP:Recipe.OnGiveXP.Cooking3'], 'food_portioning', FOOD_SLICING),
    ('Base', 'Slice Salami', ['keep [Recipe.GetItemTypes.SharpKnife]/MeatCleaver', 'Salami', 'Result:SalamiSlice=4', 'OnCreate:Recipe.OnCreate.SliceSalami', 'Sound:SliceMeat', 'Time:50.0', 'Category:Cooking', 'OnGiveXP:Recipe.OnGiveXP.Cooking3'], 'food_portioning', FOOD_SLICING),
    ('Base', 'Make Bowl of Oatmeal', ['Bowl', 'OatsRaw;10', 'Water=1', 'Result:Oatmeal', 'Time:20.0', 'Category:Cooking', 'OnCreate:Recipe.OnCreate.MakeOatmeal', 'OnGiveXP:Recipe.OnGiveXP.Cooking3'], 'food_preparation', OATMEAL_PREPARATION),
    ('Base', 'Make Squid Calamari', ['keep [Recipe.GetItemTypes.SharpKnife]/MeatCleaver', 'destroy Squid', 'Result:SquidCalamari=2', 'Category:Cooking', 'Time:30'], 'food_portioning', FOOD_ASSEMBLY),
    ('Base', 'Slice Cake', ['keep [Recipe.GetItemTypes.DullKnife]/[Recipe.GetItemTypes.SharpKnife]/MeatCleaver', 'CakeRaw', 'Result:CakeSlice=5', 'Time:20.0', 'OnCreate:Recipe.OnCreate.SlicePie', 'Category:Cooking', 'OnGiveXP:Recipe.OnGiveXP.Cooking3', 'OnCanPerform:Recipe.OnCanPerform.SliceCooked'], 'food_portioning', COOKED_SLICING),
    ('Base', 'Make Bowl of Cereal', ['Bowl', 'Cereal;5', '[Recipe.GetItemTypes.Milk];2', 'Result:CerealBowl', 'Time:20.0', 'Category:Cooking', 'OnGiveXP:Recipe.OnGiveXP.Cooking3'], 'food_preparation', FOOD_ASSEMBLY),
    ('Base', 'Place Rice in Cooking Pot', ['Rice;10', 'destroy WaterPot', 'Result:WaterPotRice', 'Time:50.0', 'OnCreate:Recipe.OnCreate.AddBaseIngredientToCookingVessel', 'Category:Cooking', 'OnGiveXP:Recipe.OnGiveXP.None'], 'grain_preparation', GRAIN_VESSEL_PREPARATION),
    ('Base', 'Make Shortbread Cookie Dough', ['keep Spatula/[Recipe.GetItemTypes.Spoon]/[Recipe.GetItemTypes.Fork]', 'keep Bowl', 'destroy BakingTray', 'keep RollingPin', 'Butter;4', '[Recipe.GetItemTypes.Sugar];10', 'Water=1', 'Flour=1', 'Result:CookiesShortbreadDough', 'NeedToBeLearn:true', 'Category:Cooking', 'Time:50'], 'cookie_preparation', FOOD_ASSEMBLY),
    ('Base', 'Scoop Ice Cream', ['keep [Recipe.GetItemTypes.Spoon]', 'Cone', 'Icecream;10', 'Result:ConeIcecream', 'Time:30.0', 'Category:Cooking'], 'food_preparation', FOOD_ASSEMBLY),
    ('Base', 'Make Stake', ['TreeBranch', 'keep [Recipe.GetItemTypes.SharpKnife]/MeatCleaver', 'Result:Stake', 'Time:80.0', 'Category:Survivalist', 'OnGiveXP:Recipe.OnGiveXP.WoodWork5'], 'woodworking', WOOD_SHAPING),
    ('Base', 'Slice Pie', ['keep [Recipe.GetItemTypes.DullKnife]/[Recipe.GetItemTypes.SharpKnife]/MeatCleaver', 'PieWholeRaw/PieWholeRawSweet', 'Result:Pie=5', 'Time:20.0', 'OnCreate:Recipe.OnCreate.SlicePie', 'Category:Cooking', 'OnGiveXP:Recipe.OnGiveXP.Cooking3', 'OnCanPerform:Recipe.OnCanPerform.SliceCooked'], 'food_portioning', COOKED_SLICING),
    ('Base', 'Butcher Rabbit', ['keep [Recipe.GetItemTypes.SharpKnife]/MeatCleaver', 'DeadRabbit', 'Result:Rabbitmeat', 'Sound:PZ_FoodSwoosh', 'Time:50.0', 'OnCreate:Recipe.OnCreate.CutAnimal', 'Category:Cooking', 'OnGiveXP:Recipe.OnGiveXP.Cooking10'], 'animal_butchery', ANIMAL_PREPARATION),
    ('Base', 'Make Sugar Cookie Dough', ['keep Spatula/[Recipe.GetItemTypes.Spoon]/[Recipe.GetItemTypes.Fork]', 'keep Bowl', 'destroy BakingTray', 'keep RollingPin', '[Recipe.GetItemTypes.BakingFat];2', '[Recipe.GetItemTypes.Sugar];10', '[Recipe.GetItemTypes.Egg]=2', 'BakingSoda=1', 'Water=1', 'Flour=1', 'Result:CookiesSugarDough', 'NeedToBeLearn:true', 'Category:Cooking', 'Time:50'], 'cookie_preparation', FOOD_ASSEMBLY),
    ('Base', 'Slice Pizza', ['keep [Recipe.GetItemTypes.SharpKnife]/MeatCleaver', 'PizzaWhole/PizzaRecipe', 'Result:Pizza=6', 'OnCreate:Recipe.OnCreate.SlicePizza', 'Sound:SliceMeat', 'Time:50.0', 'OnCanPerform:Recipe.OnCanPerform.SlicePizza', 'Category:Cooking'], 'food_portioning', PIZZA_SLICING),
    ('Base', 'Slice Bread', ['keep [Recipe.GetItemTypes.DullKnife]/[Recipe.GetItemTypes.SharpKnife]/MeatCleaver', 'Bread', 'Result:BreadSlices=3', 'OnCreate:Recipe.OnCreate.SliceBread', 'Sound:SliceBread', 'Time:40.0', 'Category:Cooking', 'OnGiveXP:Recipe.OnGiveXP.Cooking3'], 'food_portioning', FOOD_SLICING),
    ('Base', 'Make Oatmeal Cookie Dough', ['keep Spatula/[Recipe.GetItemTypes.Spoon]/[Recipe.GetItemTypes.Fork]', 'keep Bowl', 'destroy BakingTray', 'keep RollingPin', '[Recipe.GetItemTypes.BakingFat];2', '[Recipe.GetItemTypes.Sugar];5', '[Recipe.GetItemTypes.Egg]=2', 'BakingSoda=1', 'OatsRaw;10', 'Water=1', 'Flour=1', 'Result:CookiesOatmealDough', 'NeedToBeLearn:true', 'Category:Cooking', 'Time:50'], 'cookie_preparation', FOOD_ASSEMBLY),
    ('Base', 'Slice Baloney', ['keep [Recipe.GetItemTypes.SharpKnife]/MeatCleaver', 'Baloney', 'Result:BaloneySlice=6', 'OnCreate:Recipe.OnCreate.SliceHam', 'Sound:SliceMeat', 'Time:50.0', 'Category:Cooking', 'OnGiveXP:Recipe.OnGiveXP.Cooking3'], 'food_portioning', FOOD_SLICING),
    ('farming', 'Get Bacon Bits', ['keep [Recipe.GetItemTypes.SharpKnife]', 'BaconRashers', 'Result:BaconBits=4', 'Time:10.0', 'Category:Cooking'], 'food_portioning', FOOD_ASSEMBLY),
    ('Base', 'Place Pasta in Saucepan', ['Pasta;10', 'destroy WaterSaucepan', 'Result:WaterSaucepanPasta', 'Time:50.0', 'OnCreate:Recipe.OnCreate.AddBaseIngredientToCookingVessel', 'Category:Cooking', 'OnGiveXP:Recipe.OnGiveXP.None'], 'grain_preparation', GRAIN_VESSEL_PREPARATION),
    ('Base', 'Place Rice in Saucepan', ['Rice;10', 'destroy WaterSaucepan', 'Result:WaterSaucepanRice', 'Time:50.0', 'OnCreate:Recipe.OnCreate.AddBaseIngredientToCookingVessel', 'Category:Cooking', 'OnGiveXP:Recipe.OnGiveXP.None'], 'grain_preparation', GRAIN_VESSEL_PREPARATION),
    ('Base', 'Make Halloween Pumpkin', ['Pumpkin', 'keep [Recipe.GetItemTypes.SharpKnife]/[Recipe.GetItemTypes.DullKnife]', 'Result:HalloweenPumpkin', 'Category:Cooking', 'Time:60'], 'pumpkin_carving', FOOD_ASSEMBLY),
    ('farming', 'Get Bacon Rashers', ['keep [Recipe.GetItemTypes.SharpKnife]', 'Bacon', 'Result:BaconRashers=4', 'Time:10.0', 'Category:Cooking'], 'food_portioning', FOOD_ASSEMBLY),
    ('Base', 'Make Chocolate Chip Cookie Dough', ['keep Spatula/[Recipe.GetItemTypes.Spoon]/[Recipe.GetItemTypes.Fork]', 'keep Bowl', 'destroy BakingTray', 'keep RollingPin', '[Recipe.GetItemTypes.BakingFat];2', '[Recipe.GetItemTypes.Sugar];5', '[Recipe.GetItemTypes.Egg]=2', 'BakingSoda=1', 'ChocolateChips;6', 'Water=1', 'Flour=1', 'Result:CookieChocolateChipDough', 'NeedToBeLearn:true', 'Category:Cooking', 'Time:50'], 'cookie_preparation', FOOD_ASSEMBLY),
    ('Base', 'Make Maki', ['[Recipe.GetItemTypes.FishMeat];2', '[Recipe.GetItemTypes.Rice];2', 'Seaweed', 'Avocado;2', 'Result:Maki', 'Category:Cooking', 'Time:30'], 'food_preparation', FOOD_ASSEMBLY),
    ('Base', 'Make Onigiri', ['[Recipe.GetItemTypes.FishMeat];2', '[Recipe.GetItemTypes.Rice];3', 'Seaweed', 'Avocado;2', 'Result:Onigiri', 'Category:Cooking', 'Time:30'], 'food_preparation', FOOD_ASSEMBLY),
    ('Base', 'Drill Plank', ['Plank/Log', 'keep [Recipe.GetItemTypes.Screwdriver]/[Recipe.GetItemTypes.DullKnife]/[Recipe.GetItemTypes.SharpKnife]/SharpedStone', 'Result:PercedWood', 'Time:40.0', 'Prop1:Source=2', 'Prop2:Source=1'], 'woodworking', WOOD_SHAPING),
    ('Base', 'Slice Fillet', ['keep [Recipe.GetItemTypes.SharpKnife]/MeatCleaver', 'Bass/Catfish/Perch/Crappie/Panfish/Pike/Trout', 'Result:FishFillet=2', 'Sound:SliceMeat', 'Time:50.0', 'OnTest:Recipe.OnTest.CutFish', 'OnCreate:Recipe.OnCreate.CutFish', 'Category:Cooking', 'OnGiveXP:Recipe.OnGiveXP.Cooking10'], 'fish_preparation', FISH_PREPARATION),
    ('Base', 'Slice Bread', ['keep [Recipe.GetItemTypes.DullKnife]/[Recipe.GetItemTypes.SharpKnife]/MeatCleaver', 'BreadDough', 'Result:BreadSlices=3', 'Sound:SliceBread', 'Time:40.0', 'Category:Cooking', 'OnTest:Recipe.OnTest.SliceBreadDough', 'OnCreate:Recipe.OnCreate.SliceBreadDough', 'OnGiveXP:Recipe.OnGiveXP.Cooking3'], 'food_portioning', DOUGH_SLICING),
    ('Base', 'Slice Onion', ['Onion', 'keep [Recipe.GetItemTypes.SharpKnife]/MeatCleaver', 'Result:OnionRings=2', 'Time:70.0', 'Category:Cooking', 'OnGiveXP:Recipe.OnGiveXP.Cooking3'], 'food_portioning', FOOD_SLICING),
    ('Base', 'Make Chocolate Cookie Dough', ['keep Spatula/[Recipe.GetItemTypes.Spoon]/[Recipe.GetItemTypes.Fork]', 'keep Bowl', 'destroy BakingTray', 'keep RollingPin', '[Recipe.GetItemTypes.BakingFat];2', '[Recipe.GetItemTypes.Sugar];5', '[Recipe.GetItemTypes.Egg]=2', 'BakingSoda=1', 'CocoaPowder;10', 'Water=1', 'Flour=1', 'Result:CookiesChocolateDough', 'NeedToBeLearn:true', 'Category:Cooking', 'Time:50'], 'cookie_preparation', FOOD_ASSEMBLY),
    ('Base', 'Make Sushi', ['[Recipe.GetItemTypes.FishMeat];5', '[Recipe.GetItemTypes.Rice];5', 'Result:SushiFish', 'Category:Cooking', 'Time:30'], 'food_preparation', FOOD_ASSEMBLY),
    ('Base', 'Butcher Bird', ['keep [Recipe.GetItemTypes.SharpKnife]/MeatCleaver', 'DeadBird', 'Result:Smallbirdmeat', 'Sound:PZ_FoodSwoosh', 'Time:50.0', 'OnCreate:Recipe.OnCreate.CutAnimal', 'Category:Cooking', 'OnGiveXP:Recipe.OnGiveXP.Cooking10'], 'animal_butchery', ANIMAL_PREPARATION),
)

DEVICE_ASSEMBLY = 'The exact learned electrical or explosive recipe requires its declared materials and kept tool, where present. Electricity requirements apply only to the selected recipe: timer level one, controllers/sensors levels two/four/six, trigger level two and noise maker level three. No callback is declared in these recipes. RecipeManager validity, not driving, raw consumption quantities and native result delivery remain separate; crafting a named device does not prove ignition, damage, smoke, noise, timer or sensor behavior.'

QUALIFIERS[DEVICE_ASSEMBLY] = ('선택한 장치 제작법의 재료·도구와 학습·전기 기술 조건이 필요하며 운전 중에는 제작할 수 없다.', DEVICE_ASSEMBLY)

MOLOTOV_ASSEMBLY = 'The three exact recipes separately accept liquor-group plus cloth, empty bottles plus cloth and petrol, or destroyed petrol bottles plus cloth. FullLiquor is assigned twice in the supplied Lua; its later effective definition, like FullPetrolBottle, checks UsedDelta == 1 only for Petrol-tagged arguments and accepts other arguments. Do not restore the overwritten whole-liquor hunger test. RecipeManager validity and not driving apply. Consumption, fuel interpretation and result delivery remain native; no fire or explosion outcome follows from this recipe role.'

QUALIFIERS[MOLOTOV_ASSEMBLY] = ('화염병 제작법마다 허용하는 병·천·연료가 다르다. 검사 콜백이 있는 경우 연료 태그 물품은 가득 차 있어야 하며 운전 중에는 제작할 수 없다.', MOLOTOV_ASSEMBLY)

TRAP_ASSEMBLY = 'The five exact learned recipes supply their declared planks/nails/twine/sticks/wire and keep a saw only where declared. Snare requires Trapping one, box Woodwork one and Trapping two, cage Trapping three; wooden crate and stick recipes declare no skill level. RecipeManager validity and not driving apply. No additional callback is declared; placement, bait, animal capture and native result delivery are not implied by these crafting roles.'

QUALIFIERS[TRAP_ASSEMBLY] = ('선택한 덫 제작법의 재료와 학습 조건이 필요하다. 톱과 목공·덫 기술 조건은 해당 제작법에서 요구할 때 적용되며 운전 중에는 제작할 수 없다.', TRAP_ASSEMBLY)

SAWN_WOOD = 'Saw Logs and Make Sturdy Stick supply Log or Plank and keep a Saw-group tool. Saw Logs permits floor inputs and requests Woodwork XP three at level <= 3, otherwise one. Sturdy Stick has no XP callback. Raw result clauses declare three planks or eight sticks; native material selection, consumption and result delivery remain separate. RecipeManager validity and not driving apply.'

QUALIFIERS[SAWN_WOOD] = ('통나무·판자를 해당 목재 가공법에 제공하고 허용하는 톱을 사용한다. 운전 중에는 제작할 수 없다.', SAWN_WOOD)

SIMPLE_TRANSFORMATION = 'The exact reviewed callback-free recipe supplies its declared material and declares its distinct result. RecipeManager validity and not driving apply. Raw result quantities, consumed units and native item creation/delivery remain separate. No effect of the resulting item, implicit equipped state or preservation of the original state is inferred.'

QUALIFIERS[SIMPLE_TRANSFORMATION] = ('선택한 가공법에서 지정한 재료가 필요하며 운전 중에는 제작할 수 없다.', SIMPLE_TRANSFORMATION)

PLASTER_MIXING = 'The exact Make Bucket of Plaster recipe destroys an empty or water-filled bucket, supplies Water=5 and PlasterPowder, and declares BucketPlasterFull. Both bucket alternatives still have the explicit Water operand. No callback is declared. RecipeManager validity and not driving apply; native water accounting, consumption and result delivery remain separate.'

QUALIFIERS[PLASTER_MIXING] = ('석고 혼합에는 허용하는 양동이와 석고 가루·물이 필요하며 운전 중에는 제작할 수 없다.', PLASTER_MIXING)

CAKE_PAN_PREPARATION = 'Place Cake in Baking Pan supplies CakeBatter and BakingPan and requests Cooking3 XP. Its PutCakeBatterInBakingPan callback adds a Base.Bowl; it does not locally set cooked state or copy freshness. RecipeManager validity and not driving apply; native material consumption and bowl/result delivery remain separate.'

QUALIFIERS[CAKE_PAN_PREPARATION] = ('케이크 반죽을 베이킹 팬에 옮기는 준비법에 사용하며 운전 중에는 할 수 없다.', CAKE_PAN_PREPARATION)

EGG_PACKING = 'Put Eggs in Carton supplies Egg=12, allows frozen input and uses Uncooked. That predicate accepts non-Food arguments and requires Food arguments to be neither cooked nor burnt. RecipeManager validity and not driving apply. No local result callback or freshness preservation is declared; native count and result delivery remain separate.'

QUALIFIERS[EGG_PACKING] = ('달걀 포장은 익거나 타지 않은 달걀을 받으며 냉동 달걀도 허용한다. 운전 중에는 포장할 수 없다.', EGG_PACKING)

OMELETTE_PREPARATION = 'Prepare Omelette keeps a Spatula/Spoon/Fork-group utensil, destroys Pan and supplies Egg-group quantity two. WholeEgg rejects any cooked argument; Egg-tagged arguments require absolute hunger change >= absolute base hunger when fresh, otherwise >= 0.75 of base hunger. No OnCreate cooking callback is declared. RecipeManager validity and not driving apply; selected quantities and native delivery remain separate.'

QUALIFIERS[OMELETTE_PREPARATION] = ('오믈렛 준비에는 프라이팬·허용하는 도구와 익히지 않은 달걀이 필요하며 달걀은 신선도별 남은 양 조건을 만족해야 한다. 운전 중에는 할 수 없다.', OMELETTE_PREPARATION)

TRAY_EMPTYING = 'The exact pan/tray emptying recipes destroy the specified prepared-food form and declare its corresponding empty container. AllowRottenItem is true and no result callback is declared. RecipeManager validity and not driving apply. This discards the food form; it does not recover ingredients, clean blood/dirt or guarantee native result delivery.'

QUALIFIERS[TRAY_EMPTYING] = ('해당 팬·트레이의 음식을 비울 수 있으며 상한 음식도 허용한다. 재료를 돌려받는 동작은 아니고 운전 중에는 할 수 없다.', TRAY_EMPTYING)

MUFFIN_PORTIONING = 'Get 6 Muffins requires a present cooked selected tray; burnt state alone does not pass GetMuffin. Completion divides selected hunger and nutrition by six, sets cooked true, copies the name, requests a MuffinTray and removes the selected tray. It does not copy mood or freshness. RecipeManager validity and not driving apply; native output count and delivery remain separate.'

QUALIFIERS[MUFFIN_PORTIONING] = ('머핀을 꺼내려면 익힌 머핀 트레이가 필요하며 운전 중에는 할 수 없다.', MUFFIN_PORTIONING)

BISCUIT_PORTIONING = 'Get 6 Biscuits/Get 6 Cookies use GetBiscuit, requiring cooked or burnt selected food. Their completion copies only burnt=true when applicable, requests MuffinTray for biscuits or BakingTray for cookies and removes selected input. The numerical hunger/nutrition copying code is commented out, so it supplies no effect. RecipeManager validity and not driving apply; native result count, defaults and delivery remain separate.'

QUALIFIERS[BISCUIT_PORTIONING] = ('비스킷·쿠키를 꺼내려면 익었거나 탄 해당 트레이가 필요하며 운전 중에는 할 수 없다.', BISCUIT_PORTIONING)

BEAN_PREPARATION = 'Make Bowl of Beans supplies OpenBeans and Bowl or TinnedBeans and Bowl with a kept CanOpener-group tool. BeanBowl copies age, hunger and nutrition only from an OpenBeans input; the TinnedBeans variant has no corresponding local copy. RecipeManager validity and not driving apply; native material consumption, food defaults and result delivery remain separate.'

QUALIFIERS[BEAN_PREPARATION] = ('콩을 그릇에 옮길 때 그릇과 열린 콩 통조림 또는 캔 따개가 필요한 닫힌 통조림을 사용한다. 운전 중에는 할 수 없다.', BEAN_PREPARATION)

CANDY_OPENING = 'Open Candy Package destroys CandyPackage and declares Lollipop=5. Its callback additionally requests six MintCandy. RecipeManager validity and not driving apply; native result quantity interpretation and delivery remain separate. This is package opening, not direct consumption of the package.'

QUALIFIERS[CANDY_OPENING] = ('사탕 포장을 여는 데 사용할 수 있으며 운전 중에는 개봉할 수 없다.', CANDY_OPENING)

SHOTGUN_SHORTENING = 'The exact shotgun shortening recipe supplies Shotgun or DoubleBarrelShotgun and keeps Base.Saw, not the Saw group. The respective callback copies current ammunition and all modData, copies a live chamber only when both guns have a chamber, and transfers attachments that MountOn the result FullType while returning other parts to inventory. It does not explicitly copy condition. RecipeManager validity and not driving apply; native factory, attachments and result delivery remain separate.'

QUALIFIERS[SHOTGUN_SHORTENING] = ('해당 산탄총과 지정된 톱으로 총신 단축 제작법에 참여한다. 호환 부착물은 옮기고 다른 부착물은 돌려주도록 처리하며 운전 중에는 할 수 없다.', SHOTGUN_SHORTENING)

TORCH_REFILL_RECIPE = 'Refill Blow Torch destroys BlowTorch=1 and supplies PropaneTank. Its test rejects an already full blowtorch and an empty propane tank. Completion finds both inputs, starts result delta at old torch delta plus new UseDelta times thirty, then while below one with propane remaining adds new UseDelta times ten and calls propane Use; it clamps values above one. No guaranteed full refill with insufficient propane. RecipeManager validity and not driving apply; native recipe consumption, Use units and result delivery remain separate.'

QUALIFIERS[TORCH_REFILL_RECIPE] = ('토치 재충전에는 가득 차지 않은 토치와 연료가 남은 프로판 탱크가 필요하며 운전 중에는 할 수 없다.', TORCH_REFILL_RECIPE)

BATTERY_REMOVAL_RECIPE = 'Remove Battery keeps Torch, HandTorch or Rubberducky2. TorchBatteryRemoval requires positive UsedDelta; completion creates the recipe Battery with the receiver delta and sets receiver delta to zero, without setting activation. Walking is permitted by StopOnWalk:false; RecipeManager validity and not driving apply. Native result delivery and charge interpretation remain separate.'

QUALIFIERS[BATTERY_REMOVAL_RECIPE] = ('건전지를 꺼내려면 해당 기기에 남은 전력이 있어야 한다. 이동 중에는 가능하지만 운전 중에는 할 수 없다.', BATTERY_REMOVAL_RECIPE)

CANDLE_LIGHT_RECIPE = 'Light Candle destroys Candle and supplies a StartFire-group item. Completion copies delta, condition and favorite state, clears primary if primary equals secondary, sets the result in secondary and activates it. StopOnWalk:false allows walking; RecipeManager validity and not driving apply. This recipe does not impose the inventory-menu one-lit-candle restriction on other entry routes. Native result creation and illumination remain separate.'

QUALIFIERS[CANDLE_LIGHT_RECIPE] = ('초에 불을 붙이는 제작법에는 초와 허용하는 발화 도구가 필요하다. 걸으면서는 가능하지만 운전 중에는 할 수 없다.', CANDLE_LIGHT_RECIPE)

CANDLE_EXTINGUISH_RECIPE = 'Extinguish Candle destroys CandleLit and declares Candle; completion copies delta, condition and favorite state but does not reassign hands. This differs from the immediate inventory unequip/drop helper. StopOnWalk:false allows walking; RecipeManager validity and not driving apply. Native result delivery and extinguishing remain separate.'

QUALIFIERS[CANDLE_EXTINGUISH_RECIPE] = ('켜진 초를 끄는 제작법에 사용할 수 있다. 걸으면서는 가능하지만 운전 중에는 할 수 없다.', CANDLE_EXTINGUISH_RECIPE)

ITEM_TRANSFORMATION_RECIPES = (
    ('Gather Gunpowder', ['Bullets38/Bullets44/Bullets45/Bullets9mm/556Bullets/308Bullets/223Bullets/ShotgunShells', 'Result:GunPowder', 'Time:30.0'], 'ammunition_disassembly', SIMPLE_TRANSFORMATION),
    ('Add Timer', ['Aerosolbomb', 'TimerCrafted', 'ElectronicsScrap=2', 'DuctTape=1', 'Result:AerosolbombTriggered', 'NeedToBeLearn:true', 'Time:80.0', 'Category:Electrical'], 'explosive_modification', DEVICE_ASSEMBLY),
    ('Add Motion Sensor V1', ['Aerosolbomb', 'MotionSensor', 'ElectronicsScrap=2', 'DuctTape=1', 'Result:AerosolbombSensorV1', 'NeedToBeLearn:true', 'SkillRequired:Electricity=2', 'Time:80.0', 'Category:Electrical'], 'explosive_modification', DEVICE_ASSEMBLY),
    ('Add Motion Sensor V2', ['Aerosolbomb', 'MotionSensor', 'ElectronicsScrap=3', 'DuctTape=1', 'Result:AerosolbombSensorV2', 'NeedToBeLearn:true', 'SkillRequired:Electricity=4', 'Time:80.0', 'Category:Electrical'], 'explosive_modification', DEVICE_ASSEMBLY),
    ('Add Motion Sensor V3', ['Aerosolbomb', 'MotionSensor', 'ElectronicsScrap=4', 'DuctTape=1', 'Result:AerosolbombSensorV3', 'NeedToBeLearn:true', 'SkillRequired:Electricity=6', 'Time:80.0', 'Category:Electrical'], 'explosive_modification', DEVICE_ASSEMBLY),
    ('Add Crafted Trigger', ['Aerosolbomb', 'TriggerCrafted', 'ElectronicsScrap=2', 'DuctTape=1', 'Result:AerosolbombRemote', 'NeedToBeLearn:true', 'SkillRequired:Electricity=2', 'Time:80.0', 'Category:Electrical'], 'explosive_modification', DEVICE_ASSEMBLY),
    ('Make Timer', ['Timer/AlarmClock2', 'keep [Recipe.GetItemTypes.Screwdriver]', 'ElectronicsScrap', 'Glue=1', 'Result:TimerCrafted', 'SkillRequired:Electricity=1', 'NeedToBeLearn:true', 'Time:50.0', 'Category:Electrical'], 'electronic_assembly', DEVICE_ASSEMBLY),
    ('Make Aerosol bomb', ['Hairspray', 'Sparklers', 'Aluminum', 'Result:Aerosolbomb', 'Time:80.0', 'NeedToBeLearn:true', 'Category:Engineer'], 'explosive_assembly', DEVICE_ASSEMBLY),
    ('Make Tin Foil Hat', ['Aluminum', 'Result:Hat_TinFoilHat', 'Time:20'], 'hat_crafting', SIMPLE_TRANSFORMATION),
    ('Make Noise Maker', ['ElectronicsScrap=7', 'Amplifier', 'Result:NoiseTrap', 'SkillRequired:Electricity=3', 'Time:80.0', 'NeedToBeLearn:true', 'Category:Electrical'], 'explosive_assembly', DEVICE_ASSEMBLY),
    ('Place Cake in Baking Pan', ['CakeBatter', 'BakingPan', 'Result:CakePrep', 'OnCreate:Recipe.OnCreate.PutCakeBatterInBakingPan', 'Time:30.0', 'Category:Cooking', 'OnGiveXP:Recipe.OnGiveXP.Cooking3'], 'food_preparation', CAKE_PAN_PREPARATION),
    ('Place Pie in Baking Pan', ['PieDough', 'BakingPan', 'keep RollingPin', 'Result:PiePrep', 'Time:30.0', 'Category:Cooking', 'OnGiveXP:Recipe.OnGiveXP.Cooking3'], 'food_preparation', FOOD_ASSEMBLY),
    ('Make Fried Shrimp', ['BakingSoda=1', '[Recipe.GetItemTypes.Flour]=1', 'Shrimp', 'Result:ShrimpFriedCraft', 'Category:Cooking', 'Time:10'], 'food_preparation', FOOD_ASSEMBLY),
    ('Make Fried Onion Rings', ['BakingSoda=1', '[Recipe.GetItemTypes.Flour]=1', 'OnionRings', 'Result:FriedOnionRingsCraft', 'Category:Cooking', 'Time:10'], 'food_preparation', FOOD_ASSEMBLY),
    ('Clean Tray', ['destroy BakingTray_Muffin/BakingTray_Muffin_Recipe/Muffintray_Biscuit', 'Result:MuffinTray', 'Category:Cooking', 'OnGiveXP:Recipe.OnGiveXP.None', 'Time:40.0', 'Sound:EmptyPan', 'AllowRottenItem:true'], 'food_container_emptying', TRAY_EMPTYING),
    ('Get 6 Muffins', ['BakingTray_Muffin_Recipe/BakingTray_Muffin', 'Result:MuffinGeneric=6', 'Category:Cooking', 'OnCanPerform:Recipe.OnCanPerform.GetMuffin', 'OnCreate:Recipe.OnCreate.GetMuffin', 'Time:60'], 'food_portioning', MUFFIN_PORTIONING),
    ('Smash Watermelon', ['Watermelon', 'keep [Recipe.GetItemTypes.Hammer]/[Recipe.GetItemTypes.Sledgehammer]/Log/Plank/BaseballBat/BaseballBatNails', 'Result:WatermelonSmashed=5', 'Time:50.0', 'Category:Cooking', 'OnGiveXP:Recipe.OnGiveXP.Cooking3', 'AllowRottenItem:true'], 'watermelon_breaking', FOOD_ASSEMBLY),
    ('Make Fork', ['IronIngot=18', 'keep [Recipe.GetItemTypes.Hammer]', 'NearItem:Anvil', 'Result:Fork', 'Time:100.0', 'Category:Smithing', 'OnGiveXP:Recipe.OnGiveXP.Blacksmith10', 'OnCreate:BSItem_OnCreate', 'NeedToBeLearn:true'], 'metal_forging', FORGE_PREPARATION),
    ('Make Spoon', ['IronIngot=18', 'keep [Recipe.GetItemTypes.Hammer]', 'NearItem:Anvil', 'Result:Spoon', 'Time:100.0', 'Category:Smithing', 'OnGiveXP:Recipe.OnGiveXP.Blacksmith10', 'OnCreate:BSItem_OnCreate', 'NeedToBeLearn:true'], 'metal_forging', FORGE_PREPARATION),
    ('Smash Bottle', ['WineEmpty/WineEmpty2/WhiskeyEmpty/BeerEmpty', 'Result:SmashedBottle', 'Time:20', 'Sound:BreakGlassItem'], 'bottle_breaking', SIMPLE_TRANSFORMATION),
    ('Make Molotov Cocktail', ['WineEmpty/WineEmpty2/WhiskeyEmpty/BeerEmpty', 'RippedSheets/RippedSheetsDirty/DenimStrips/DenimStripsDirty', '[Recipe.GetItemTypes.Petrol]=1', 'Result:Molotov', 'Time:50.0'], 'explosive_assembly', MOLOTOV_ASSEMBLY),
    ('Refill Blow Torch', ['destroy BlowTorch=1', 'PropaneTank', 'Result:BlowTorch', 'Time:50.0', 'Category:Welding', 'OnTest:Recipe.OnTest.RefillBlowTorch', 'OnCreate:Recipe.OnCreate.RefillBlowTorch'], 'blowtorch_refilling', TORCH_REFILL_RECIPE),
    ('Make Bowl of Beans', ['OpenBeans', 'Bowl', 'Result:BeanBowl', 'Time:80.0', 'Category:Cooking', 'OnCreate:Recipe.OnCreate.BeanBowl', 'OnGiveXP:Recipe.OnGiveXP.Cooking3'], 'food_preparation', BEAN_PREPARATION),
    ('Make Bowl of Beans', ['TinnedBeans', 'keep [Recipe.GetItemTypes.CanOpener]', 'Bowl', 'Result:BeanBowl', 'Time:130.0', 'Category:Cooking', 'OnCreate:Recipe.OnCreate.BeanBowl', 'OnGiveXP:Recipe.OnGiveXP.Cooking3', 'Sound:OpenCannedFood'], 'food_preparation', BEAN_PREPARATION),
    ('Make Gravy', ['keep Spatula/[Recipe.GetItemTypes.Spoon]/[Recipe.GetItemTypes.Fork]', 'keep Bowl', 'GravyMix', 'Water=2', 'Result:Gravy', 'Category:Cooking', 'Time:20'], 'food_preparation', FOOD_ASSEMBLY),
    ('Make Pancake', ['keep Spatula/[Recipe.GetItemTypes.Spoon]/[Recipe.GetItemTypes.Fork]', 'keep Bowl', 'PancakeMix', 'Water=2', 'Result:PancakesCraft', 'Category:Cooking', 'Time:10'], 'food_preparation', FOOD_ASSEMBLY),
    ('Make Bucket of Plaster', ['destroy BucketEmpty/BucketWaterFull', 'Water=5', 'PlasterPowder', 'Result:BucketPlasterFull', 'Time:150.0', 'Category:Carpentry', 'Sound:MakePlaster'], 'plaster_preparation', PLASTER_MIXING),
    ('Light Candle', ['destroy Candle', '[Recipe.GetItemTypes.StartFire]', 'Result:CandleLit', 'Time:30.0', 'OnCreate:LightCandle_OnCreate', 'StopOnWalk:false'], 'candle_lighting', CANDLE_LIGHT_RECIPE),
    ('Extinguish Candle', ['destroy CandleLit', 'Result:Candle', 'Time:30.0', 'OnCreate:ExtinguishCandle_OnCreate', 'StopOnWalk:false'], 'candle_extinguishing', CANDLE_EXTINGUISH_RECIPE),
    ('Open Candy Package', ['destroy CandyPackage', 'Result:Lollipop=5', 'Time:5.0', 'OnCreate:Recipe.OnCreate.OpenCandyPackage', 'OnGiveXP:Recipe.OnGiveXP.None', 'Category:Cooking'], 'package_opening', CANDY_OPENING),
    ('Make Smoke Bomb', ['Coldpack', 'RippedSheets/RippedSheetsDirty', 'Newspaper=2', 'Result:SmokeBomb', 'Time:80.0', 'NeedToBeLearn:true', 'Category:Engineer'], 'explosive_assembly', DEVICE_ASSEMBLY),
    ('Get 6 Cookies', ['CookieChocolateChipDough', 'Result:CookieChocolateChip=6', 'Category:Cooking', 'OnCanPerform:Recipe.OnCanPerform.GetBiscuit', 'OnCreate:Recipe.OnCreate.GetCookies', 'Time:60'], 'food_portioning', BISCUIT_PORTIONING),
    ('Empty Baking Tray', ['destroy CookiesChocolateDough/CookieChocolateChipDough/CookiesOatmealDough/CookiesSugarDough/CookiesShortbreadDough', 'Result:BakingTray', 'OnGiveXP:Recipe.OnGiveXP.None', 'Time:40.0', 'Category:Cooking', 'Sound:EmptyPan', 'AllowRottenItem:true'], 'food_container_emptying', TRAY_EMPTYING),
    ('Get 6 Cookies', ['CookiesChocolateDough', 'Result:CookiesChocolate=6', 'Category:Cooking', 'OnCanPerform:Recipe.OnCanPerform.GetBiscuit', 'OnCreate:Recipe.OnCreate.GetCookies', 'Time:60'], 'food_portioning', BISCUIT_PORTIONING),
    ('Get 6 Cookies', ['CookiesOatmealDough', 'Result:CookiesOatmeal=6', 'Category:Cooking', 'OnCanPerform:Recipe.OnCanPerform.GetBiscuit', 'OnCreate:Recipe.OnCreate.GetCookies', 'Time:60'], 'food_portioning', BISCUIT_PORTIONING),
    ('Get 6 Cookies', ['CookiesShortbreadDough', 'Result:CookiesShortbread=6', 'Category:Cooking', 'OnCanPerform:Recipe.OnCanPerform.GetBiscuit', 'OnCreate:Recipe.OnCreate.GetCookies', 'Time:60'], 'food_portioning', BISCUIT_PORTIONING),
    ('Get 6 Cookies', ['CookiesSugarDough', 'Result:CookiesSugar=6', 'Category:Cooking', 'OnCanPerform:Recipe.OnCanPerform.GetBiscuit', 'OnCreate:Recipe.OnCreate.GetCookies', 'Time:60'], 'food_portioning', BISCUIT_PORTIONING),
    ('Make Molotov Cocktail', ['destroy [Recipe.GetItemTypes.Liquor]', 'RippedSheets/RippedSheetsDirty/DenimStrips/DenimStripsDirty', 'Result:Molotov', 'Time:50.0', 'OnTest:Recipe.OnTest.FullLiquor'], 'explosive_assembly', MOLOTOV_ASSEMBLY),
    ('Make Molotov Cocktail', ['destroy WinePetrol/WhiskeyPetrol', 'RippedSheets/RippedSheetsDirty/DenimStrips/DenimStripsDirty', 'Result:Molotov', 'Time:50.0', 'OnTest:Recipe.OnTest.FullPetrolBottle'], 'explosive_assembly', MOLOTOV_ASSEMBLY),
    ('Make Flame bomb', ['[Recipe.GetItemTypes.Petrol]=4', 'RippedSheets/RippedSheetsDirty/DenimStrips/DenimStripsDirty', 'WaterBottleEmpty', 'Result:FlameTrap', 'Time:80.0', 'NeedToBeLearn:true', 'Category:Engineer'], 'explosive_assembly', DEVICE_ASSEMBLY),
    ('Saw Off Double Barrel Shotgun', ['DoubleBarrelShotgun', 'keep Saw', 'Result:DoubleBarrelShotgunSawnoff', 'Sound:Sawing', 'Time:200.0', 'OnCreate:DblBarrelhotgunSawnoff_OnCreate'], 'shotgun_modification', SHOTGUN_SHORTENING),
    ('Add Timer', ['FlameTrap', 'TimerCrafted', 'ElectronicsScrap=2', 'DuctTape=1', 'Result:FlameTrapTriggered', 'NeedToBeLearn:true', 'Time:80.0', 'Category:Electrical'], 'explosive_modification', DEVICE_ASSEMBLY),
    ('Add Motion Sensor V1', ['FlameTrap', 'MotionSensor', 'ElectronicsScrap=2', 'DuctTape=1', 'Result:FlameTrapSensorV1', 'NeedToBeLearn:true', 'SkillRequired:Electricity=2', 'Time:80.0', 'Category:Electrical'], 'explosive_modification', DEVICE_ASSEMBLY),
    ('Add Motion Sensor V2', ['FlameTrap', 'MotionSensor', 'ElectronicsScrap=3', 'DuctTape=1', 'Result:FlameTrapSensorV2', 'NeedToBeLearn:true', 'SkillRequired:Electricity=4', 'Time:80.0', 'Category:Electrical'], 'explosive_modification', DEVICE_ASSEMBLY),
    ('Add Motion Sensor V3', ['FlameTrap', 'MotionSensor', 'ElectronicsScrap=4', 'DuctTape=1', 'Result:FlameTrapSensorV3', 'NeedToBeLearn:true', 'SkillRequired:Electricity=6', 'Time:80.0', 'Category:Electrical'], 'explosive_modification', DEVICE_ASSEMBLY),
    ('Add Crafted Trigger', ['FlameTrap', 'TriggerCrafted', 'ElectronicsScrap=2', 'DuctTape=1', 'Result:FlameTrapRemote', 'NeedToBeLearn:true', 'SkillRequired:Electricity=2', 'Time:80.0', 'Category:Electrical'], 'explosive_modification', DEVICE_ASSEMBLY),
    ('Add Timer', ['NoiseTrap', 'TimerCrafted', 'ElectronicsScrap=2', 'DuctTape=1', 'Result:NoiseTrapTriggered', 'NeedToBeLearn:true', 'Time:80.0', 'Category:Electrical'], 'explosive_modification', DEVICE_ASSEMBLY),
    ('Add Motion Sensor V1', ['NoiseTrap', 'MotionSensor', 'ElectronicsScrap=2', 'DuctTape=1', 'Result:NoiseTrapSensorV1', 'NeedToBeLearn:true', 'SkillRequired:Electricity=2', 'Time:80.0', 'Category:Electrical'], 'explosive_modification', DEVICE_ASSEMBLY),
    ('Add Motion Sensor V2', ['NoiseTrap', 'MotionSensor', 'ElectronicsScrap=3', 'DuctTape=1', 'Result:NoiseTrapSensorV2', 'NeedToBeLearn:true', 'SkillRequired:Electricity=4', 'Time:80.0', 'Category:Electrical'], 'explosive_modification', DEVICE_ASSEMBLY),
    ('Add Motion Sensor V3', ['NoiseTrap', 'MotionSensor', 'ElectronicsScrap=4', 'DuctTape=1', 'Result:NoiseTrapSensorV3', 'NeedToBeLearn:true', 'SkillRequired:Electricity=6', 'Time:80.0', 'Category:Electrical'], 'explosive_modification', DEVICE_ASSEMBLY),
    ('Add Crafted Trigger', ['NoiseTrap', 'TriggerCrafted', 'ElectronicsScrap=2', 'DuctTape=1', 'Result:NoiseTrapRemote', 'NeedToBeLearn:true', 'SkillRequired:Electricity=2', 'Time:80.0', 'Category:Electrical'], 'explosive_modification', DEVICE_ASSEMBLY),
    ('Add Timer', ['SmokeBomb', 'TimerCrafted', 'ElectronicsScrap=2', 'DuctTape=1', 'Result:SmokeBombTriggered', 'NeedToBeLearn:true', 'Time:80.0', 'Category:Electrical'], 'explosive_modification', DEVICE_ASSEMBLY),
    ('Add Motion Sensor V1', ['SmokeBomb', 'MotionSensor', 'ElectronicsScrap=2', 'DuctTape=1', 'Result:SmokeBombSensorV1', 'NeedToBeLearn:true', 'SkillRequired:Electricity=2', 'Time:80.0', 'Category:Electrical'], 'explosive_modification', DEVICE_ASSEMBLY),
    ('Add Motion Sensor V2', ['SmokeBomb', 'MotionSensor', 'ElectronicsScrap=3', 'DuctTape=1', 'Result:SmokeBombSensorV2', 'NeedToBeLearn:true', 'SkillRequired:Electricity=4', 'Time:80.0', 'Category:Electrical'], 'explosive_modification', DEVICE_ASSEMBLY),
    ('Add Motion Sensor V3', ['SmokeBomb', 'MotionSensor', 'ElectronicsScrap=4', 'DuctTape=1', 'Result:SmokeBombSensorV3', 'NeedToBeLearn:true', 'SkillRequired:Electricity=6', 'Time:80.0', 'Category:Electrical'], 'explosive_modification', DEVICE_ASSEMBLY),
    ('Add Crafted Trigger', ['SmokeBomb', 'TriggerCrafted', 'ElectronicsScrap=2', 'DuctTape=1', 'Result:SmokeBombRemote', 'NeedToBeLearn:true', 'SkillRequired:Electricity=2', 'Time:80.0', 'Category:Electrical'], 'explosive_modification', DEVICE_ASSEMBLY),
    ('Add Timer', ['PipeBomb', 'TimerCrafted', 'ElectronicsScrap=2', 'DuctTape=1', 'Result:PipeBombTriggered', 'NeedToBeLearn:true', 'Time:80.0', 'Category:Electrical'], 'explosive_modification', DEVICE_ASSEMBLY),
    ('Add Motion Sensor V1', ['PipeBomb', 'MotionSensor', 'ElectronicsScrap=2', 'DuctTape=1', 'Result:PipeBombSensorV1', 'NeedToBeLearn:true', 'SkillRequired:Electricity=2', 'Time:80.0', 'Category:Electrical'], 'explosive_modification', DEVICE_ASSEMBLY),
    ('Add Motion Sensor V2', ['PipeBomb', 'MotionSensor', 'ElectronicsScrap=3', 'DuctTape=1', 'Result:PipeBombSensorV2', 'NeedToBeLearn:true', 'SkillRequired:Electricity=4', 'Time:80.0', 'Category:Electrical'], 'explosive_modification', DEVICE_ASSEMBLY),
    ('Add Motion Sensor V3', ['PipeBomb', 'MotionSensor', 'ElectronicsScrap=4', 'DuctTape=1', 'Result:PipeBombSensorV3', 'NeedToBeLearn:true', 'SkillRequired:Electricity=6', 'Time:80.0', 'Category:Electrical'], 'explosive_modification', DEVICE_ASSEMBLY),
    ('Add Crafted Trigger', ['PipeBomb', 'TriggerCrafted', 'ElectronicsScrap=2', 'DuctTape=1', 'Result:PipeBombRemote', 'NeedToBeLearn:true', 'SkillRequired:Electricity=2', 'Time:80.0', 'Category:Electrical'], 'explosive_modification', DEVICE_ASSEMBLY),
    ('Put Eggs in Carton', ['Egg=12', 'Result:EggCarton', 'AllowFrozenItem:true', 'OnGiveXP:Recipe.OnGiveXP.None', 'Time:5.0', 'Category:Cooking', 'OnCanPerform:Recipe.OnCanPerform.Uncooked'], 'item_packaging', EGG_PACKING),
    ('Prepare Omelette', ['keep Spatula/[Recipe.GetItemTypes.Spoon]/[Recipe.GetItemTypes.Fork]', 'destroy Pan', '[Recipe.GetItemTypes.Egg]=2', 'Result:OmeletteRecipe', 'Category:Cooking', 'Time:20', 'OnTest:Recipe.OnTest.WholeEgg'], 'food_preparation', OMELETTE_PREPARATION),
    ('Make Remote Controller V1', ['Remote', 'keep [Recipe.GetItemTypes.Screwdriver]', 'ElectronicsScrap=2', 'Glue=2', 'Result:RemoteCraftedV1', 'SkillRequired:Electricity=2', 'NeedToBeLearn:true', 'Time:50.0', 'Category:Electrical'], 'electronic_assembly', DEVICE_ASSEMBLY),
    ('Make Remote Controller V2', ['Remote', 'keep [Recipe.GetItemTypes.Screwdriver]', 'ElectronicsScrap=3', 'Glue=2', 'Result:RemoteCraftedV2', 'SkillRequired:Electricity=4', 'NeedToBeLearn:true', 'Time:50.0', 'Category:Electrical'], 'electronic_assembly', DEVICE_ASSEMBLY),
    ('Make Remote Controller V3', ['Remote', 'keep [Recipe.GetItemTypes.Screwdriver]', 'ElectronicsScrap=4', 'Glue=2', 'Result:RemoteCraftedV3', 'SkillRequired:Electricity=6', 'NeedToBeLearn:true', 'Time:50.0', 'Category:Electrical'], 'electronic_assembly', DEVICE_ASSEMBLY),
    ('Make Remote Trigger', ['Receiver/Radio.RadioReceiver', 'keep [Recipe.GetItemTypes.Screwdriver]', 'ElectronicsScrap=2', 'Glue=2', 'Result:TriggerCrafted', 'SkillRequired:Electricity=2', 'NeedToBeLearn:true', 'Time:50.0', 'Category:Electrical'], 'electronic_assembly', DEVICE_ASSEMBLY),
    ('Make Pipe bomb', ['ElectronicsScrap=3', 'MetalPipe', 'GunPowder=20', 'Twine=1', 'keep [Recipe.GetItemTypes.Saw]', 'Result:PipeBomb', 'Time:100.0', 'NeedToBeLearn:true', 'Category:Engineer'], 'explosive_assembly', DEVICE_ASSEMBLY),
    ('Saw Logs', ['Log', 'keep [Recipe.GetItemTypes.Saw]', 'CanBeDoneFromFloor:true', 'Result:Plank=3', 'Sound:Sawing', 'Time:230.0', 'Category:Carpentry', 'OnGiveXP:Recipe.OnGiveXP.SawLogs', 'AnimNode:SawLog', 'Prop1:Source=2', 'Prop2:Log'], 'woodworking', SAWN_WOOD),
    ('Make Sturdy Stick', ['Plank', 'keep [Recipe.GetItemTypes.Saw]', 'Result:WoodenStick=8', 'Sound:Sawing', 'Time:50.0'], 'woodworking', SAWN_WOOD),
    ('Make Wooden Box Trap', ['keep [Recipe.GetItemTypes.Saw]', 'Plank=3', 'Nails=5', 'Result:TrapCrate', 'Sound:Sawing', 'Time:120.0', 'Category:Trapper', 'NeedToBeLearn:true'], 'trap_crafting', TRAP_ASSEMBLY),
    ('Make Snare Trap', ['keep [Recipe.GetItemTypes.Saw]', 'Plank=1', 'Twine=2', 'SkillRequired:Trapping=1', 'Result:TrapSnare', 'Sound:Sawing', 'Time:130.0', 'Category:Trapper', 'NeedToBeLearn:true'], 'trap_crafting', TRAP_ASSEMBLY),
    ('Make Trap Box', ['keep [Recipe.GetItemTypes.Saw]', 'Plank=4', 'Nails=7', 'SkillRequired:Woodwork=1;Trapping=2;', 'Result:TrapBox', 'Sound:Sawing', 'Time:150.0', 'Category:Trapper', 'NeedToBeLearn:true'], 'trap_crafting', TRAP_ASSEMBLY),
    ('Empty Griddle Pan', ['destroy GriddlePanFriedVegetables', 'Result:GridlePan', 'OnGiveXP:Recipe.OnGiveXP.None', 'Time:40.0', 'Category:Cooking', 'Sound:EmptyPan', 'AllowRottenItem:true'], 'food_container_emptying', TRAY_EMPTYING),
    ('Remove Battery', ['keep Torch/HandTorch/Rubberducky2', 'Result:Battery', 'Time:30', 'OnTest:Recipe.OnTest.TorchBatteryRemoval', 'OnCreate:Recipe.OnCreate.TorchBatteryRemoval', 'StopOnWalk:false'], 'battery_removal', BATTERY_REMOVAL_RECIPE),
    ('Get 6 Biscuits', ['Muffintray_Biscuit', 'Result:Biscuit=6', 'Category:Cooking', 'OnCanPerform:Recipe.OnCanPerform.GetBiscuit', 'OnCreate:Recipe.OnCreate.GetBiscuit', 'Time:60'], 'food_portioning', BISCUIT_PORTIONING),
    ('Make Newspaper Hat', ['Newspaper', 'Result:Hat_NewspaperHat', 'Time:20'], 'hat_crafting', SIMPLE_TRANSFORMATION),
    ('Empty Frying Pan', ['destroy OmeletteRecipe', 'Result:Pan', 'OnGiveXP:Recipe.OnGiveXP.None', 'Time:40.0', 'Category:Cooking', 'AllowRottenItem:true'], 'food_container_emptying', TRAY_EMPTYING),
    ('Empty Frying Pan', ['destroy PanFriedVegetables', 'Result:Pan', 'OnGiveXP:Recipe.OnGiveXP.None', 'Time:40.0', 'Category:Cooking', 'Sound:EmptyPan', 'AllowRottenItem:true'], 'food_container_emptying', TRAY_EMPTYING),
    ('Empty Roasting Pan', ['destroy PanFriedVegetables2', 'Result:RoastingPan', 'OnGiveXP:Recipe.OnGiveXP.None', 'Time:40.0', 'Category:Cooking', 'Sound:EmptyPan', 'AllowRottenItem:true'], 'food_container_emptying', TRAY_EMPTYING),
    ('Saw Off Shotgun', ['Shotgun', 'keep Saw', 'Result:ShotgunSawnoff', 'Sound:Sawing', 'Time:200.0', 'OnCreate:ShotgunSawnoff_OnCreate'], 'shotgun_modification', SHOTGUN_SHORTENING),
    ('Make Stick Trap', ['WoodenStick=4', 'Twine=1', 'Result:TrapStick', 'Time:120.0', 'Category:Trapper', 'NeedToBeLearn:true'], 'trap_crafting', TRAP_ASSEMBLY),
    ('Make Cage Trap', ['Wire=5', 'SkillRequired:Trapping=3;', 'Result:TrapCage', 'Time:180.0', 'Category:Trapper', 'NeedToBeLearn:true'], 'trap_crafting', TRAP_ASSEMBLY),
)

AMMUNITION_ITEMS = {'Base.' + n for n in ('223Bullets', '308Bullets', '556Bullets', 'Bullets38', 'Bullets44', 'Bullets45', 'Bullets9mm', 'ShotgunShells')}

AMMUNITION_FIELDS = {'DisplayCategory', 'Count', 'Weight', 'AlwaysWelcomeGift', 'Type', 'DisplayName', 'Icon', 'MetalValue', 'WorldStaticModel'}

THROWN_DEVICE_ITEMS = {'Base.' + n + suffix for n in ('Aerosolbomb', 'FlameTrap', 'NoiseTrap', 'PipeBomb', 'SmokeBomb')
                       for suffix in ('', 'Remote', 'SensorV1', 'SensorV2', 'SensorV3', 'Triggered')} | {'Base.Molotov', 'Base.Football2'}

THROWN_DEVICE_FIELDS = {'DisplayCategory', 'MaxRange', 'KnockdownMod', 'Type', 'MinimumSwingTime', 'SwingAnim', 'WeaponSprite', 'UseSelf', 'DisplayName', 'SwingTime', 'SwingAmountBeforeImpact', 'PhysicsObject', 'MinDamage', 'Weight', 'MaxDamage', 'MaxHitCount', 'Icon', 'ExplosionPower', 'ExplosionRange', 'ExplosionTimer', 'SensorRange', 'CanBePlaced', 'CanBeRemote', 'CanBeReused', 'ExplosionSound', 'SwingSound', 'PlacedSprite', 'WorldStaticModel', 'TriggerExplosionTimer', 'triggerExplosionTimer', 'Tooltip', 'FirePower', 'FireRange', 'NoiseRange', 'NoiseDuration', 'SmokeRange', 'OtherHandUse', 'OtherHandRequire', 'EquipSound', 'ExtraDamage'}

REMOTE_CONTROLLER_ITEMS = {'Base.RemoteCraftedV1', 'Base.RemoteCraftedV2', 'Base.RemoteCraftedV3'}

REMOTE_CONTROLLER_FIELDS = {'DisplayCategory', 'Weight', 'Type', 'DisplayName', 'Icon', 'RemoteController', 'RemoteRange', 'MetalValue', 'Tooltip', 'WorldStaticModel'}

AMMUNITION_LOADING_PATHS = 'The ammunition-item menu selects DisplayCategory Ammo from player inventory, then examines top-level receivers with the same FullType AmmoType: non-HandWeapon magazines with free capacity, or guns without MagazineType. Magazine count uses recursive ammunition and free capacity, then transfers selected rounds and receiver. InsertBullet rechecks full/exhausted state, removes one matching round and increments magazine count; running stops while walking and aiming are allowed. XP is conditional. The optional sound branch references an unset self.gun. The bullet-menu tooltip creates the receiver GunType and dereferences it without a nil guard; the .223 magazine declares none. doBulletMenu additionally reads an unbound global bullets, with zero disabling its requested amount. Gun load and legacy difficulty-specific paths are independently represented on actual receivers. Native getter defaults, these unbound references, selected item delivery and animation dispatch remain specific unresolved execution boundaries; Count is not converted into a guaranteed available stack.'

PHYSICS_ATTACK = 'The supplied non-ranged attack hook clears queued actions, rejects an already started attack or unauthorized player action, and permits DoAttack outside a vehicle or during a shove. It forwards zero or chargeDelta. These exact declarations use SwingAnim Throw and PhysicsObject, so this is an attack request rather than an admitted melee hit. DoAttack owns projectile creation, throwing, collision, damage, UseSelf/OtherHandRequire interpretation and device activation. No guaranteed thrown object, fire, explosion, noise, smoke or companion-item consumption is inferred.'

DEVICE_TIMER_CONTROL = 'The selected HandWeapon must have ExplosionTimer > 0 to offer the dialog. Confirming OK with a positive numeric value sets ExplosionTimer; cancel or nonpositive/non-numeric input does not. SensorRange changes only the activation/explosion label here. There is no continued inventory or original timer guard in the callback. Native countdown, sensor activation and resulting effect remain separate.'

DEVICE_WORLD_PLACEMENT = 'The selected HandWeapon must allow placement; the timed action requires it to remain in inventory and uses the character square captured at construction. Walking or running interrupts. Completion constructs IsoTrap, adds it to that square, syncs on clients, clears hands and removes the inventory item. No transfer from another container is queued by this entry and no additional empty-square test is present. Native object construction, physics behavior, activation and post-use retention remain separate.'

for _name, _ko, _en in (
    ('request_physics_attack', '던지기형 무기의 공격 동작을 요청할 수 있다.', 'It can initiate the attack action for a throwing weapon.'),
    ('place_trigger_device', '설치가 허용된 장치를 현재 칸에 놓을 수 있다.', 'A placement-enabled device can be placed on the current square.')):
    FUNCTIONS[_name] = (_name.replace('_', ' '), _ko, _en)

for _predicate, _ko in (
    (AMMUNITION_LOADING_PATHS, '해당 탄종을 받는 총기나 탄창과 남은 장전 공간이 필요하다. 달리면 장전이 중단된다.'),
    (PHYSICS_ATTACK, '공격을 시작할 수 있는 상태에서 차량 밖에 있어야 하며 밀치기에는 차량 예외가 있다. 실제 투척과 효과는 별개다.'),
    (DEVICE_TIMER_CONTROL, '타이머 설정을 지원하는 장치에서 양수의 지연 값을 확인하면 설정을 바꿀 수 있다.'),
    (DEVICE_WORLD_PLACEMENT, '설치를 허용하는 장치를 소지한 채 현재 칸에 놓으며 걷거나 달리면 중단된다.')):
    QUALIFIERS[_predicate] = (_ko, _predicate)

LIGHT_RADIAL = 'lua/client/ISUI/ISLightSourceRadialMenu.lua'

LIGHT_BINDING = 'lua/server/Items/ItemBindingHandler.lua'

CAMP_PETROL_LIGHT = 'lua/client/Camping/TimedActions/ISLightFromPetrol.lua'

CAMP_KINDLE_LIGHT = 'lua/client/Camping/TimedActions/ISLightFromKindle.lua'

LIGHT_ITEMS = {'Base.Torch', 'Base.HandTorch', 'Base.Lighter', 'Base.Matches', 'Base.Candle', 'Base.CandleLit', 'Base.Rubberducky2'}

LIGHT_FIELDS = {'DisplayCategory', 'LightDistance', 'Weight', 'Type', 'UseWhileEquipped', 'UseWhileUnequipped', 'UseDelta', 'TorchCone', 'LightStrength', 'DisplayName', 'ActivatedItem', 'Icon', 'MetalValue', 'cantBeConsolided', 'ConsolidateOption', 'StaticModel', 'WorldStaticModel', 'ticksPerEquipUse', 'Tags', 'DisappearOnUse', 'TorchDot', 'primaryAnimMask', 'secondaryAnimMask'}

LIGHT_CONTROL = 'The radial menu includes positive-light-strength items and exact Candle, but exposes action choices only for held primary/secondary items; toggle additionally requires canBeActivated and canEmitLight, and its callback rechecks only canBeActivated. Equip/unequip selection queues that action then immediately activates an inactive item, including the unequip route. The active short-key release calls ItemBindingHandler: secondary, primary then attached canEmitLight items except CandleLit take priority and stop search even if not activatable. Otherwise it equips the best emitting positive-strength inventory item into secondary and activates immediately; that fallback does not exclude CandleLit. Key entry requires a live player, unpaused game, no queue and no drag. The ordinary inventory toggle requires held/attached, recognized Drainable positive delta and not CandleLit, then toggles without continued guard. Positive strength alone does not establish available charge, light emission or native equipped-drain behavior.'

CANDLE_UNEQUIP = 'The specific CandleLit unequip/hand replacement and equipped-drop callers use litCandleExtinguish: request a new Base.Candle, copy delta, condition and favorite, replace primary if it held the lit candle else secondary, then remove the old item. This is an immediate form change before the ordinary queued action, distinct from the extinguishing recipe that does not reassign hands. Native creation and hand/inventory delivery remain separate.'

CAMP_IGNITER = 'The campfire menu selects a StartFire-tag item or exact Lighter/Matches from available containers. Tinder lighting requires an unlit campfire and an accepted tinder; it transfers both items and approaches the campfire. Timed validity rechecks campfire existence/unlit state and possession of both, but not igniter remaining delta. Completion removes the tinder, calls igniter Use and sends its fuel amount. Petrol lighting instead requires existing campfire fuel, accepted Petrol-tag/PetrolCan with more than one drainable use at menu time, and positive petrol/igniter delta during the action; completion calls Use on each without adding fuel. Walking/running interrupts both. The server adds any supplied fuel and lights only an unlit fire with positive fuel. The supplied menu assigns startFireTypes[types] although types is not locally bound; entry completion depends on that global environment. Tinder sorting also does not reorder the parallel fuel amount list. These execution and fuel-binding limits are not replaced by a guaranteed ignition or fixed consumption result.'

CAMP_FRICTION = 'The campfire menu selects exact PercedWood plus WoodenStick preferentially, otherwise TreeBranch, for an unlit fueled campfire with positive endurance. Transfer and adjacent approach precede the action. Validity rechecks both wood items, unlit campfire existence and positive endurance, but not fuel. Each update lowers endurance by 0.0001 times game multiplier; after progress 0.2 it rolls ignition at one in 300, or one in 150 for Outdoorsman. On failure a separate one in 300 break roll, or one in 450 for Outdoorsman, removes the stick/branch, not PercedWood. The action lasts 1500 and stops on walking/running; its perform does not guarantee ignition or consume the drilled board. The server only lights with positive fuel. Native command delivery and game-time/random execution remain separate.'

for _predicate, _ko in (
    (LIGHT_CONTROL, '지원하는 손·장착 조명을 조작한다. 실제 발광 가능 상태가 필요하며 메뉴와 단축키의 선택 순서는 서로 다르다.'),
    (CANDLE_UNEQUIP, '켜진 초를 손에서 빼거나 장착한 채 버릴 때 꺼진 초로 바꾸며 남은 양과 상태를 넘긴다.'),
    (CAMP_IGNITER, '꺼진 모닥불에 불쏘시개를 함께 쓰거나, 연료가 든 모닥불에 휘발유를 함께 써 점화를 시도한다. 걷거나 달리면 중단된다.'),
    (CAMP_FRICTION, '꺼진 모닥불에 연료가 있고 지구력이 남아 있어야 한다. 구멍 낸 나무와 나뭇가지 또는 막대가 필요하며 지구력이 줄고 막대가 부러질 수 있다. 점화는 확률적이며 이동하면 중단된다.')):
    QUALIFIERS[_predicate] = (_ko, _predicate)

for _name, _ko, _en in (
    ('control_portable_light', '휴대 조명의 장착·활성 상태를 조작할 수 있다.', 'Its portable-light equipment and activation controls can be used.'),
    ('extinguish_on_unequip', '켜진 초를 손에서 빼거나 버리며 끌 수 있다.', 'A lit candle can be extinguished when unequipped or dropped.'),
    ('light_candle', '발화 도구로 초에 불을 붙이는 제작법에 사용할 수 있다.', 'It can be used in the candle-lighting recipe with a fire-starting item.'),
    ('extinguish_candle', '켜진 초를 끄는 제작법에 사용할 수 있다.', 'It can be used in the lit-candle extinguishing recipe.'),
    ('remove_device_battery', '해당 기기에서 건전지를 꺼낼 수 있다.', 'A battery can be removed from the supported device.'),
    ('light_campfire_by_friction', '나무를 마찰시켜 모닥불 점화를 시도할 수 있다.', 'It can be used to attempt lighting a campfire by wood friction.')):
    FUNCTIONS[_name] = (_name.replace('_', ' '), _ko, _en)

FIREARM_RADIAL = 'lua/client/ISUI/ISFirearmRadialMenu.lua'

GUN_ROUND_LOADING = 'Hold the firearm in the primary hand and supply its matching ammunition with free capacity. Automatic reload refuses a jammed non-magazine gun; the explicit radial/menu load route has no equivalent jam guard. Menu transfer precedes the action. Validity checks primary-hand identity only. Each load animation removes one captured ammunition item and increments current count; InsertAllBulletsReload repeats the same operation. Exhausted bullets or full capacity finishes loading and queues rack for an empty chamber. Walking/aiming are allowed, running stops. Native ammunition construction, animation-event delivery and state binding remain separate.'

QUALIFIERS[GUN_ROUND_LOADING] = ('총을 주 손에 들고 호환 탄약과 남은 장전 공간이 있어야 한다. 자동 재장전은 걸린 총에 탄을 넣지 않으며 달리면 중단된다.', GUN_ROUND_LOADING)

GUN_ROUND_UNLOADING = 'The radial/menu unload route selects a firearm without MagazineType and with current ammunition. The timed action validity always returns true, so primary-hand/possession and nonempty state are not continuous guards. Each unload sound event creates one AmmoType item and decrements current count, or handles all current rounds for InsertAllBulletsReload. The action does not unload a chambered round. Running stops; walking/aiming do not. Item creation, animation delivery and native ammo getters remain separate.'

QUALIFIERS[GUN_ROUND_UNLOADING] = ('탄창을 쓰지 않는 총에 남은 탄약이 있을 때 탄약을 꺼낼 수 있다. 달리면 중단되며 약실의 탄은 별도로 다룬다.', GUN_ROUND_UNLOADING)

GUN_MAGAZINE_EJECTION = 'The menu/radial ejection route selects an installed magazine. The action requires the primary-hand gun and checks containsClip at start and unload completion. It creates a new declared MagazineType, copies current gun ammunition into it, adds it to inventory, clears containsClip and sets current ammunition to zero. The chamber is unchanged; the original magazine identity/condition is not returned. Running stops, walking/aiming do not. Factory and animation-event execution remain native dependencies.'

QUALIFIERS[GUN_MAGAZINE_EJECTION] = ('총을 주 손에 들고 탄창이 끼워져 있어야 한다. 달리면 중단되며 약실의 탄은 남는다.', GUN_MAGAZINE_EJECTION)

GUN_RACKING = 'canRack requires a MagazineType or AmmoType and accepts jammed, live/spent chamber, a magazine gun with empty chamber and current rounds, a no-chamber gun with current/spent rounds, or a gun without MagazineType whose current ammunition is at least AmmoPerShoot. Start checks canRack; subsequent validity always returns true. Live unjammed chamber ejects one newly constructed AmmoType item, then chamber/jam clear and current ammunition feeds the chamber when >= AmmoPerShoot. No-chamber unjammed count>0 ejects one item and subtracts AmmoPerShoot, without an added nonnegative clamp. Jam clearing returns no live round. Spent count clears before the else-if spent-chamber branch. Running stops; walking/aiming do not. Native item creation and event/state persistence remain separate.'

QUALIFIERS[GUN_RACKING] = ('총의 탄 걸림·약실·잔탄 상태가 조작을 허용해야 한다. 걸림을 풀거나 약실에 탄을 넣고 뺄 수 있으며 달리면 중단된다.', GUN_RACKING)

GUN_FIRING_CYCLE = 'The normal firing hook clears timed actions, requires no attack already started and player melee authorization, and calls canShoot for a ranged non-shove attack. canShoot requires not jammed and a live chamber or current count>0 for no-chamber guns, not count>=AmmoPerShoot; debug unlimited ammunition bypasses those checks. The hit-point hook clears the chamber; RackAfterShoot leaves a spent chamber and attack-finished queues rack. Otherwise count>=AmmoPerShoot feeds a chamber and subtracts AmmoPerShoot; manual-spent handling increments spent count. Condition below maximum, positive JamGunChance and current ammunition permit a random jam with loss-adjusted chance capped at seven. No hit, damage or guaranteed post-shot recovery is inferred. Reload speed uses skill, panic, ammo strap, driver and animation-speed factors; animation events drive completion rather than a fixed duration.'

QUALIFIERS[GUN_FIRING_CYCLE] = ('사격하면 총의 방식에 따라 탄약·약실·탄피 상태가 바뀐다. 상태가 나쁜 총은 남은 탄약이 있을 때 걸릴 수 있다.', GUN_FIRING_CYCLE)

GUN_FIRE_MODES = 'The selected HandWeapon menu offers its FireModePossibilities only when there is more than one, excluding current mode. Selection immediately sets the weapon mode and character FireMode variable without transfer, continuous possession or timed interruption checks. The reviewed AssaultRifle declares Auto/Single. Generic Burst handling sets AmmoPerShoot to three but is not an offered mode for this declaration; switching away does not locally reset that field. Native mode execution remains separate.'

QUALIFIERS[GUN_FIRE_MODES] = ('이 총에 제공되는 현재 모드 이외의 발사 모드를 선택할 수 있다.', GUN_FIRE_MODES)

FUNCTIONS['load_firearm_rounds'] = ("firearm controls", '총에 호환 탄약을 장전할 수 있다.', 'Matching rounds can be loaded into the firearm.')

FUNCTIONS['unload_firearm_rounds'] = ("firearm controls", '총에 남은 탄약을 꺼낼 수 있다.', 'Remaining rounds can be unloaded from the firearm.')

FUNCTIONS['receive_firearm_magazine'] = ("firearm controls", '총에 호환 탄창을 끼울 수 있다.', 'A compatible magazine can be inserted into the firearm.')

FUNCTIONS['eject_firearm_magazine'] = ("firearm controls", '총에서 탄창을 빼낼 수 있다.', 'The magazine can be ejected from the firearm.')

FUNCTIONS['rack_firearm'] = ("firearm controls", '총의 탄 걸림을 풀거나 약실·탄약을 조작할 수 있다.', 'The firearm can be cycled to clear a jam or handle its chamber and ammunition.')

FUNCTIONS['change_firearm_mode'] = ("firearm controls", '제공되는 발사 모드를 바꿀 수 있다.', 'The firearm can switch between its offered firing modes.')

FUNCTIONS['receive_weapon_upgrade'] = ("firearm controls", '총에 호환 개조 부품을 장착할 수 있다.', 'Compatible upgrade parts can be installed on the firearm.')

FUNCTIONS['detach_weapon_upgrade'] = ("firearm controls", '총에 장착한 개조 부품을 떼어낼 수 있다.', 'Installed upgrade parts can be removed from the firearm.')

FIREARM_ITEMS = {'Base.VarmintRifle', 'Base.Revolver', 'Base.ShotgunSawnoff', 'Base.AssaultRifle2', 'Base.Revolver_Long', 'Base.Pistol3', 'Base.Pistol', 'Base.Pistol2', 'Base.AssaultRifle', 'Base.Shotgun', 'Base.DoubleBarrelShotgun', 'Base.Revolver_Short', 'Base.DoubleBarrelShotgunSawnoff', 'Base.HuntingRifle'}

FIREARM_FIELDS = {'RangeFalloff', 'MagazineType', 'ToHitModifier', 'IsAimedFirearm', 'EquipSound', 'MinRange', 'EjectAmmoStopSound', 'EjectAmmoStartSound', 'DisplayName', 'ImpactSound', 'InsertAllBulletsReload', 'CriticalChance', 'EjectAmmoSound', 'ReloadTime', 'Icon', 'AmmoBox', 'InsertAmmoStopSound', 'WeaponSprite', 'SplatNumber', 'SwingAmountBeforeImpact', 'RackSound', 'AimingMod', 'HitChance', 'ProjectileCount', 'HitSound', 'ConditionMax', 'SplatBloodOnNoDeath', 'SoundRadius', 'BreakSound', 'SwingAnim', 'MaxHitCount', 'NPCSoundBoost', 'IsAimedHandWeapon', 'PiercingBullets', 'RecoilDelay', 'ConditionLowerChanceOneIn', 'SubCategory', 'KnockBackOnNoDeath', 'AimingPerkMinAngleModifier', 'DisplayCategory', 'SoundGain', 'FireMode', 'PushBackMod', 'ManuallyRemoveSpentRounds', 'JamGunChance', 'UnequipSound', 'ShellFallSound', 'AimingPerkRangeModifier', 'Ranged', 'MinDamage', 'InsertAmmoStartSound', 'WeaponReloadType', 'ClipSize', 'SwingSound', 'SplatSize', 'CritDmgMultiplier', 'AimingPerkHitChanceModifier', 'ShareDamage', 'AimingPerkCritModifier', 'MinimumSwingTime', 'TwoHandWeapon', 'UseEndurance', 'RequiresEquippedBothHands', 'MetalValue', 'StopPower', 'MaxRange', 'RunAnim', 'RackAfterShoot', 'ClickSound', 'AimingTime', 'IdleAnim', 'SoundVolume', 'AmmoType', 'AttachmentType', 'MultipleHitConditionAffected', 'MaxDamage', 'Weight', 'KnockdownMod', 'AngleFalloff', 'haveChamber', 'ModelWeaponPart', 'BringToBearSound', 'Type', 'SwingTime', 'InsertAmmoSound', 'MaxAmmo', 'DoorDamage', 'MinAngle', 'FireModePossibilities'}

LEGACY_GUN_ITEMS = {'Base.Pistol', 'Base.Shotgun', 'Base.ShotgunSawnoff', 'Base.HuntingRifle', 'Base.VarmintRifle', 'Base.AssaultRifle'}

LEGACY_RELOAD_SOURCES = tuple('lua/shared/Reloading/' + name + '.lua' for name in (
    'stormysReload', 'ISReloadManager', 'ISReloadUtil', 'ISReloadable', 'ISReloadableWeapon',
    'ISShotgunWeapon', 'ISSemiAutoWeapon', 'ISReloadableMagazine', 'ISReloadAction', 'ISRackAction'))

LEGACY_GUN_CONTROLS = 'When isNewReloading is false, the supplied registry initializes six gun types and BerettaClip entries and registers legacy update/fire/attack hooks alongside the supplied modern hook. Shotgun, ShotgunSawnoff, HuntingRifle and VarmintRifle use ISShotgunWeapon; Pistol and AssaultRifle use ISSemiAutoWeapon. Setup stores ammo in modData, sets native AmmoType nil and initializes capacity/chamber to zero; base capacity defaults to ClipSize, not MaxAmmo. Shotgun-class reload rechecks free capacity and a found round, adds one count, removes one ammo and requests one Reloading XP; it chains while permitted. Its shot clears the chamber and sets spent-shell state; racking can eject a live round onto the current square then feed one from capacity. Semi-auto firing feeds the next round from capacity. Easy semi-auto completion consumes rounds up to free capacity; normal/hard toggles a newly created magazine out or picks the fullest matching top-level clip. The canReload method reads an unbound global difficulty, not the manager argument, while timed validity uses the supplied difficulty: easy checks capacity/ammo, normal clip possession, hard always true. ReloadManager[1] is used by some difficulty branches even for another player. Easy synchronization forces containsClip. Auto rack applies below hardcore or with a joypad; hardcore keyboard can rack even without a live round, while spent shells always allow it. Reload actions stop on running, not walking/aiming, and recheck the class rather than primary-hand identity; rack actions always validate and do not stop on movement. Reload timing uses the actual HandWeapon ReloadTime times character reload modifier plus panic*30, overriding the passed class duration; rack uses class rackTime plus panic*5. Rack completion requests a native ammo lookup and weight debit after setup has cleared AmmoType. Native lookup-on-nil behavior, global difficulty environment, conflicting modern/legacy hook dispatch, modData persistence and result creation remain unresolved; no guaranteed alternate-engine compatibility or successful racking after that lookup is asserted.'

QUALIFIERS[LEGACY_GUN_CONTROLS] = ('구형 장전 방식을 사용하는 설정에서는 해당 총의 등록된 탄약·탄창과 난이도별 장전·약실 규칙을 따른다. 장전은 달리면 중단되지만 약실 조작은 이동으로 중단되지 않는다. 이 경로와 현재 장전 동작의 동시 실행 및 반환 결과는 보장하지 않는다.', LEGACY_GUN_CONTROLS)

FUNCTIONS['use_alternate_reload_controls'] = ('firearm controls', '장전 방식 설정에 따라 탄약·탄창을 넣고 약실을 조작할 수 있다.', 'The selected reloading system provides ammunition, magazine and chamber controls.')

BEARD_TRIM = 'lua/client/TimedActions/ISTrimBeard.lua'

DYE_APPLICATION = 'The selected HairDye item exposes hair dyeing when the hair model exists and is not exactly Bald, or beard dyeing when the beard model is nonempty. Transfer the selected dye and retain it; the 120-time action, or one when instant, stops on walking/running and rechecks only possession, not remaining dye or continuing hair/beard style. Completion sets the chosen visual color from the dye native R/G/B getters, calls Use once, resets the model, sends visuals and updates clothing. Declared ColorRed/Green/Blue binding and Use depletion remain native; this does not grow hair or establish color durability.'

HAIR_GROOMING = 'The character screen uses the sex-specific native hair style registry and a current style above level zero. It offers lower nonattached selectable styles plus exact trim choices, with independent tie/untie routes. Bald requires an unbroken Razor/type-tag or Scissors/type-tag. Nonflat Mohawk and GreasedBack choices require carried Hairgel instead of the ordinary scissors guard; other cuts require an unbroken Scissors tag. Selection removes headwear first. The callback prefers scissors then razor for hair, equips for actual cutting and queues 300 time, with tie/untie 100 and instant one. ISCutHair validity always returns true: it does not recheck tool, gel, style eligibility or remaining supply. It sets the selected hair model, updates attached/nonattached references and resets model/growth time; a name containing Bald also restores natural hair color. Only a nonflat Mohawk consumes a found Hairgel once at completion. GreasedBack does not consume gel, and missing gel at completion does not prevent the model change. Tools are not consumed. Walking/running interrupts. Native style lookup and visual effects remain separate.'

BEARD_GROOMING = 'The character screen requires a current beard style above level zero and an unbroken Razor/type-tag or Scissors/type-tag. Choose clean shave, a lower style or a listed trim choice. The callback prefers a razor to scissors, equips it and queues 300 time, or one when instant. The action rechecks possession of the selected tool only, stops on walking/running and does not consume it. Completion sets the requested beard model, resets model and beard growth time and updates clothing; an empty style restores natural beard color. Native style/model binding and visual synchronization remain separate; no continued brokenness/style-eligibility check is added.'

MAKEUP_LIFECYCLE = 'Opening requires a selected MakeUpType cosmetic and either an inventory Mirror, a vehicle, an inventory Base.MakeupFoundation, that exact selected foundation, or a same-z world mirror in the x/y range minus one through plus two without a wall between. Main and attached mirror sprites are checked. The UI does not transfer or continuously check possession of the cosmetic/mirror, remaining uses, reach or movement. Its category and type registry select candidate cosmetic items. Preview creates a candidate and temporarily replaces the actual worn slot, keeping the previous item for restoration on reselection/close. Apply adds the preview item to inventory, removes the old cosmetic from inventory and clears the preview references; it never calls Use on the cosmetic supply. Removal can select any worn MakeUp-prefixed item found in the registry, removes worn/inventory state and consumes no supply. These are immediate UI operations, not timed actions; closing cancels an uncommitted preview and restores the previous item. Native factory, body-location and visual synchronization remain separate. Foundation is a selector for its supported designs and mirror exemption, not proof of a real-world base-layer effect.'

STITCHING = 'Select an injured/stitched/splinted but unbandaged deep wound without glass. Use Base.SutureNeedle or Base.Needle/SewingNeedle-tag plus Base.Thread; thread is selected even at UsedDelta zero. The queued health handler rechecks the complete option before transfers. The timed action retains only the consumed suture/thread item and patient movement, not the separate needle, deep-wound or glass state. Walking/running stops; self-treatment and same-position patients pass, and moved vehicle passengers pass whereas moved drivers or patients outside vehicles fail. Completion calls Use on the suture/thread, conditionally grants fifteen Doctor XP, sets stitched and stitch time to (Doctor+1)/2 times a random value in [2,5). Infection is set when ZombRand(5+Doctor*2.5)==0. Hemophobic adds fifty panic regardless of bleeding. Base pain is twenty, or ten with a current SutureNeedleHolder or a SutureNeedle, minus Doctor with floor zero; this source adds that pain only when access level is not None. Base time is 200 or 150 with the holder/needle, minus four per actual Doctor level; instant time is one, and non-None access changes effective Doctor to ten after timing. No healing guarantee or continued ordinary-needle possession is inferred.'

GLASS_REMOVAL = 'Select an injured/stitched/splinted but unbandaged part with glass and a RemoveGlass-tag item, Tweezers or SutureNeedleHolder; bare hands are a separate option. Transfer the selected tool before queuing, but the action receives no tool argument and checks only patient movement, not continuing glass/tool state. Walking/running stops; self-treatment and same-position patients pass, and moved passengers pass while moved drivers/out-of-vehicle patients fail. Completion grants fifteen Doctor XP, clears haveGlass and gives Hemophobic fifty panic. Pain 30 minus effective Doctor is added only for non-None access; the bare-hand branch adds thirty independently. The later four-argument constructor overrides the earlier constructor: ordinary time is 150 minus four per Doctor, instant one; access then sets effective Doctor ten. Bare hands override time to 300 minus four per effective Doctor even after instant timing. The selected tool is not consumed and extracted glass is not created as inventory loot. Native wound evolution and multiplayer delivery remain separate.'

BULLET_REMOVAL = 'Select an injured/stitched/splinted but unbandaged part with a bullet and a RemoveBullet-tag item, Tweezers or SutureNeedleHolder. Transfer the tool before queuing; the action receives no tool argument and only checks patient movement, not continuing bullet/tool state. Walking/running stops, with self/same-position and moved passenger exceptions to the movement guard. Completion grants twenty Doctor XP, adds pain 80 minus effective Doctor, calls setHaveBullet(false, Doctor) and adds fifty panic for Hemophobic. Time is 250 minus six per actual Doctor, instant one; non-None access sets effective Doctor ten after timing. The tool is not consumed and no recovered bullet item is created. Native wound response and multiplayer delivery remain separate.'

POULTICE_USE = 'Select an injured/stitched/splinted but unbandaged body part with all three plantain/comfrey/garlic factors exactly zero. The queued health handler rechecks the exact poultice and those conditions before transfer. The action retains the poultice and checks patient movement only, not continuing injury/factors; walking/running stops with the same self/same-position and vehicle-passenger exceptions. Completion sets only its corresponding factor to ten plus a random value between (Doctor+1)*0.5 and Doctor+1, removes the poultice and sends that factor in the corresponding client message slot. Hemophobic adds fifty panic only while the part is bleeding. Time is 120 minus four per actual Doctor, instant one; non-None access sets effective Doctor ten after timing. No Doctor XP is granted here. Native factor decay, wound healing and client/server delivery remain separate.'

SUTURE_ASSISTANCE = 'A SutureNeedleHolder present in doctor inventory at ISStitch construction reduces its base time from 200 to 150 before actual Doctor skill subtraction, including the no-item stitch-removal action. At stitching completion, current holder possession or a SutureNeedle changes base pain from twenty to ten, but the source adds final pain only for non-None access. The holder is neither transferred nor consumed by these presence checks, and alone does not satisfy needle/thread selection. Stitch removal itself needs only an already stitched body part and no tool: it sets stitched false, uses base pain five, can grant the conditional fifteen XP and uses the same random infection branch. The holder does not establish healed wounds, universal pain relief or a mandatory removal tool.'

MEDICAL_PANIC = 'During the represented stitching or embedded-glass/bullet extraction action, a Hemophobic treating character gains fifty panic regardless of bleeding. For the represented poultice application only, the same increase additionally requires positive bleeding time.'

POULTICE_PREPARATION = 'The exact plantain, comfrey or wild-garlic preparation declares five of its named plant and a kept MortarPestle-group tool, time sixty and its corresponding poultice result. Both same-name wild-garlic declarations remain separate: one names WildGarlic and the other WildGarlic2, with their respective IsHidden/isHidden true fields. The ordinary crafting UI excludes native isHidden recipes; another native RecipeManager entry is not established here. No duplicate winner, implicit plant substitution, visible recipe guarantee, ingredient healing effect or unconditional output delivery is inferred.'

QUALIFIERS[POULTICE_PREPARATION] = ('정확한 약초 다섯 개와 보존하는 절구·공이 그룹 도구로 대응하는 찜질제를 만드는 시간 60의 제조법이다. 야생 마늘의 같은 이름 두 선언은 WildGarlic과 WildGarlic2 및 숨김 필드를 각각 유지한다. 일반 제작 창은 숨김 제조법을 제외하며 다른 엔진 진입 경로의 실행 가능성은 별도다. 약초 대체·숨김 제조법 노출·원재료의 치료 효과나 결과 전달을 보장하지 않는다.', POULTICE_PREPARATION)

BODY_DRYING = 'Select an exact BathTowel or DishCloth with positive body wetness; the callback uses the first selected item and transfers it. Time is ceil(UsedDelta*10)*20+20. Validity retains inventory possession, positive body wetness and positive used delta. Every original-time/20 update ticks, call decreaseBodyWetness(current wetness/20) and Use; completion calls Use again. Instant maxTime one does not change that original tick interval. Walking/running interrupts and already spent uses or wetness changes remain. The exact declarations prohibit consolidation; native Use and ReplaceOnDeplete produce any wet form, whose Wet/WetCooldown/ItemWhenDry processing is separately native. No complete dryness or immediate reusable replacement is guaranteed.'

QUALIFIERS[BODY_DRYING] = ('정확한 마른 목욕 수건·행주와 몸의 젖음이 필요하며 첫 선택 물품을 옮긴다. 시간은 ceil(잔량×10)×20+20이고 계속 소지·양의 잔량·젖음이 필요하다. 원래 시간/20 업데이트마다 현재 젖음의 1/20만큼 감소를 호출하고 수건을 사용하며 완료 때도 한 번 사용한다. 즉시 동작도 원래 주기를 바꾸지 않고 걷기·달리기로 중단된다. 이 선언은 합치기를 금지한다. 소모 후 젖은 형태와 재건조는 엔진 처리이며 완전 건조나 즉시 재사용은 보장하지 않는다.', BODY_DRYING)

for _predicate, _ko in (
    (DYE_APPLICATION, '머리 모델이 있고 정확히 Bald가 아니면 머리, 비어 있지 않은 수염 모델이면 수염 염색을 선택한다. 염색약을 옮겨 계속 소지하며 시간 120·즉시 1이고 걷기·달리기로 중단된다. 잔량이나 계속 같은 모양인지는 재검사하지 않는다. 완료 시 염색약의 RGB getter 값으로 색을 바꾸고 한 번 소비한 뒤 모델·시각 정보를 갱신한다. 색 속성 결속·소모·지속성은 엔진 경계이며 머리를 자라게 하지 않는다.'),
    (HAIR_GROOMING, '현재 머리 길이와 성별별 스타일 목록·정해진 자르기 선택지를 사용한다. 삭발은 파손되지 않은 면도기나 가위가, 일반 자르기는 가위 태그가 필요하며 모호크·기름칠한 스타일은 헤어젤 조건으로 갈린다. 모자를 벗고 자르기는 시간 300, 묶기·풀기는 100이며 즉시는 1이다. 동작은 도구·젤·스타일 자격을 다시 검사하지 않고 걷기·달리기로 중단된다. 완료 때 머리 모델·묶임·성장 시간을 바꾸고 Bald를 포함하면 자연색으로 되돌린다. 평평하지 않은 모호크만 발견한 젤을 한 번 소비하며 기름칠 스타일은 소비하지 않는다. 도구는 소비하지 않는다.'),
    (BEARD_GROOMING, '수염 길이가 있고 지원하는 면도·낮은 길이·다듬기 선택지가 있어야 하며 파손되지 않은 면도기나 가위가 필요하다. 면도기를 우선 장비하고 시간 300·즉시 1로 처리한다. 계속 도구를 소지해야 하지만 파손 여부·스타일 자격은 다시 검사하지 않는다. 걷기·달리기로 중단되며 도구는 소비하지 않는다. 완료 시 수염 모델·성장 시간을 바꾸고 완전히 깎으면 자연색으로 되돌린다.'),
    (MAKEUP_LIFECYCLE, '선택한 화장품과 소지 거울·차량·소지 또는 선택한 파운데이션·주변의 벽에 가리지 않는 월드 거울 중 하나로 메뉴를 연다. 같은 층의 x·y -1~+2 칸을 검사한다. 창에서는 소지·잔량·거리·이동을 계속 검사하지 않는다. 등록된 종류의 후보를 만들고 실제 착용 슬롯에서 미리보기하며 닫으면 이전 분장으로 되돌린다. 적용은 후보를 인벤토리에 넣고 이전 분장을 제거하며 화장품을 소비하지 않는다. 등록된 착용 분장은 종류와 관계없이 제거할 수 있고 별도 소모나 시간 동작은 없다. 파운데이션은 지원 분장과 거울 조건을 선택할 뿐 현실의 기초 화장 효과를 보장하지 않는다.'),
    (STITCHING, '붕대 없는 깊은 상처에 유리가 없어야 하며 봉합침 또는 바늘·재봉바늘 태그와 실이 필요하다. 실은 잔량 0도 선택된다. 큐의 건강 처리기는 재료 조합을 다시 검사하지만 시술은 소비할 실·봉합침과 환자 이동만 검사한다. 걷기·달리기로 중단되고 자기 자신·좌표가 같은 환자·이동 중 차량 승객에는 이동 예외가 있다. 완료 시 소비·조건부 의사 경험치 15·봉합 상태와 기술별 임의 봉합 시간을 설정하고 확률적으로 상처 감염을 설정한다. 혈액공포증은 출혈과 무관하게 공황 50을 더한다. 지침기나 봉합침은 기본 시간·통증을 낮추지만 이 소스의 추가 통증은 일반 사용자가 아닌 access level에만 적용된다. 일반 바늘의 계속 보유나 회복을 보장하지 않는다.'),
    (GLASS_REMOVAL, '붕대 없는 다친 부위의 유리와 지원 태그·핀셋·봉합침 지침기를 선택한다. 맨손은 별도 선택지다. 도구를 옮기지만 동작은 도구 인수를 받지 않고 환자 이동만 검사하며 걷기·달리기로 중단된다. 완료 시 의사 경험치 15·유리 상태 해제·혈액공포증 공황 50을 적용한다. 기본 추가 통증은 비일반 access level에만, 맨손 통증 30은 별도로 적용된다. 뒤의 생성자가 앞의 생성자를 덮어쓰며 맨손 시간은 즉시 설정 뒤에도 별도로 계산된다. 도구를 소비하거나 유리 아이템을 반환하지 않는다. 회복·동기화는 엔진 경계다.'),
    (BULLET_REMOVAL, '붕대 없는 다친 부위의 탄환과 지원 태그·핀셋·봉합침 지침기를 선택한다. 도구를 옮기지만 동작은 도구 인수를 받지 않고 환자 이동만 검사하며 걷기·달리기로 중단된다. 완료 시 의사 경험치 20·80에서 유효 의사 기술을 뺀 통증·탄환 상태 해제와 혈액공포증 공황 50을 적용한다. 시간은 250에서 실제 기술당 6을 빼고 즉시는 1이다. 비일반 access level의 유효 기술 10은 시간 계산 후 적용된다. 도구 소비나 회수 탄환 생성은 없으며 실제 회복·동기화는 별도다.'),
    (POULTICE_USE, '붕대 없는 다친 부위에서 세 약초 계수가 모두 0이고 정확한 찜질제가 있어야 한다. 큐 처리기는 조건을 다시 검사하지만 시술은 소지와 환자 이동만 검사한다. 걷기·달리기로 중단되며 자기 자신·같은 좌표·차량 승객 예외가 있다. 완료 시 해당 계수만 10과 기술별 임의값의 합으로 설정하고 찜질제를 제거한다. 혈액공포증 공황 50은 출혈이 있을 때만 적용하고 경험치는 주지 않는다. 실제 계수 경과·회복·동기화는 엔진 경계다.'),
    (SUTURE_ASSISTANCE, '의사 인벤토리의 봉합침 지침기는 봉합 또는 도구 없는 실밥 제거 동작을 만들 때 기본 시간을 200에서 150으로 낮춘다. 봉합 완료 시 현재 지침기 소지나 봉합침 사용은 기본 통증을 20에서 10으로 낮추지만 추가 통증 설정은 비일반 access level에만 실행된다. 이 보유 검사는 지침기를 옮기거나 소비하지 않으며 지침기만으로 바늘·실 조건을 만족하지 않는다. 실밥 제거에는 원래 도구가 필요 없고 봉합 상태를 해제하며 별도 통증·경험치·감염 분기를 사용한다. 회복이나 보편적 통증 감소를 보장하지 않는다.'),
    (MEDICAL_PANIC, '봉합·유리 또는 탄환 제거 때 시술자의 혈액공포증은 출혈과 무관하게 공황을 50 높인다. 약초 찜질제 적용 때는 추가로 해당 부위에 출혈이 있어야 한다.')):
    QUALIFIERS[_predicate] = (_ko, _predicate)

for _name, _ko, _en in (
    ('groom_hair', '지원하는 머리 자르기·모양 변경에 쓸 수 있다.', 'It can support the permitted hair cutting or styling operation.'),
    ('groom_beard', '수염을 다듬거나 면도하는 데 쓸 수 있다.', 'It can trim or shave a beard.'),
    ('support_makeup_mirror', '화장 메뉴의 거울 조건을 충족하는 데 쓸 수 있다.', 'It can satisfy the makeup-menu mirror requirement.'),
    ('remove_registered_makeup', '등록된 착용 분장을 제거하는 창을 사용할 수 있다.', 'Its makeup window can remove registered worn makeup.'),
    ('assist_stitching', '봉합 동작의 기본 시간·통증 계산에 영향을 준다.', 'Its presence changes the stitching action base time and pain calculation.')):
    FUNCTIONS[_name] = (_name.replace('_', ' '), _ko, _en)

FUNCTIONS['dye_hair_or_beard'] = ('hair dye', '머리카락이나 수염의 색을 바꿀 수 있다.', 'It can change hair or beard color.')

for _property, _direction, _ko, _en in (
    ('hair_or_beard_color', 'set_dye_color', '머리카락 또는 수염 색을 염색약 색으로 설정한다.', 'It sets hair or beard color to the dye color.'),
    ('poultice_factor', 'set_doctor_random', '해당 약초 찜질제 계수를 시술 기술별 임의값으로 설정한다.', 'It sets the corresponding poultice factor using the doctor-dependent random value.'),
    ('stitched_state', 'set_true', '상처의 봉합 상태를 설정한다.', 'It sets the wound stitched state.'),
    ('embedded_glass', 'remove', '상처에 박힌 유리 상태를 해제한다.', 'It clears the embedded-glass state.'),
    ('embedded_bullet', 'remove', '상처에 박힌 탄환 상태를 해제한다.', 'It clears the embedded-bullet state.')):
    EFFECTS[_property, _direction] = (_ko, _en)

CHOP_CURSOR = 'lua/server/BuildingObjects/ISChopTreeCursor.lua'

PLANT_CURSOR = 'lua/server/BuildingObjects/ISRemovePlantCursor.lua'

REMOVE_BUSH = 'lua/client/TimedActions/ISRemoveBush.lua'

BARRICADE = 'lua/client/TimedActions/ISBarricadeAction.lua'

UNBARRICADE = 'lua/client/TimedActions/ISUnbarricadeAction.lua'

DESTROY_CURSOR = 'lua/server/BuildingObjects/ISDestroyCursor.lua'

DESTROY_ACTION = 'lua/client/TimedActions/ISDestroyStuffAction.lua'

CHOPPING = 'The world menu selects an unbroken ChopTree-tag item and an existing tree; the cursor requires HasTree and approaches the square. doChopTree prefers the held accepted tool or the greatest TreeDamage among recursive accepted tools, transferring/equipping it. The action continuously requires an existing tree, CanAttack and a primary-hand Axe-category item, not necessarily the original instance or an explicit unbroken recheck. Start captures the axe. Each ChopTree animation calls native WeaponHit, consumes endurance when enabled, then either reduces condition on its maintenance-adjusted random roll and checks replacement equipment, or grants Maintenance XP one. A missing tree forces completion; perform alone does not cut it. Walking/running stops and normal maxTime is -1; instant start sets tree health one. Native animation delivery, tree damage, drops and complete felling remain separate.'

PLANT_CUTTING = 'The world menu and bush/vine cursor require an unbroken CutPlant-tag item in recursive inventory and a canBeCut bush or attached f_wallvines_ sprite. Walk adjacent to a bush or queue a walk to a vine square, then equip an accepted tool. Start captures the primary-hand weapon; ongoing validity checks the target and captured weapon condition when present, not the tag or continued hand/inventory identity. Walking/running stops; time is 100 or instant one. Chop events request sound, conditional endurance use and random weapon wear with equipment replacement. Completion requests object.removeBush. The server removes matching bush objects with possible branch and twig drops, or the vine and one above it. The forward bush loop mutates its index and collection; native removal/order and delivery are not guaranteed. Grass removal is a separate tool-free action, and no guaranteed loot or whole-area clearing follows.'

WOOD_BARRICADE = 'Use an eligible door/window/thumpable, a character-side barricade that can accept another plank, an unbroken Hammer-tag tool, a plank and two nails. Window/thumpable entry excludes sheet ropes and protected windows; doors use their own barricade permission. The caller approaches, equips hammer and plank, and queues time 100 minus five per Woodwork level, less twenty for Handy or instant one. Ongoing validity requires the existing BarricadeAble, equipped Hammer tag and Plank, two nails and available plank capacity; after start a door must remain closed. It does not recheck hammer brokenness. Completion sends the secondary-hand material ID/condition; the server creates a plank at that condition, adds it, requests removal of the input and two nails and Woodwork XP three. Walking/running stops. Native barricade capacity, strength, successful insertion and non-atomic inventory/server delivery remain separate. CanBarricade alone is not this menu predicate.'

WOOD_UNBARRICADE = 'Select a character-side barricade with planks and an unbroken RemoveBarricade-tag tool, approach the window/door and equip that tool. Time is 200 minus five per Woodwork level, less twenty for Handy or instant one; walking/running stops. Ongoing validity checks BarricadeAble, an existing nonmetal barricade with planks and an equipped RemoveBarricade tag, not continued tool brokenness. Completion sends an unbarricade command. The server removes one plank, transmits remaining state and, if a plank is returned, delivers it and requests Woodwork XP two and Strength XP two. It does not return nails or consume the removal tool. Native material condition, object mutation and delivery remain separate; this is not arbitrary structure dismantling.'

METAL_BARRICADE = 'Use a compatible door/window/thumpable without an existing character-side barricade, a BlowTorch with at least one drainable use and SheetMetal or three MetalBars. Window/thumpable entry additionally excludes sheet ropes. The caller approaches and equips torch/material; time is 170 minus five per MetalWelding level, less twenty for Handy or instant one. Ongoing validity checks an existing BarricadeAble, absent barricade and equipped torch/material, and three bars for the bar route, but not torch uses or a welding mask. Started doors must remain closed; walking/running stops. Completion sends secondary-hand material ID/condition and uses the primary item once. The server adds the matching metal barricade, requests one sheet or three bar removals and MetalWelding XP six. Native barricade creation/strength and non-atomic delivery remain separate. Neither a mask nor a learned recipe is required by this path.'

METAL_UNBARRICADE = 'Select an existing metal or bar barricade with a BlowTorch having at least one use, approach and equip it. Time is 120, less twenty for Handy or instant one; walking/running stops. The action rechecks the barricade and equipped BlowTorch but not remaining uses or a mask. Completion requests removal and uses the primary item once. The server returns the removed sheet, or the removed bar plus two created bars copying its condition. No removal XP is requested for metal. Native material state, removal and delivery remain separate; the path does not require a welding mask or guarantee full-condition salvage.'

MEAL_UTENSIL = 'At the start of eating, top-level inventory Spoon-tag/Base.Spoon and Fork-tag/Base.Fork items may supply the hand-model prop. For can, candrink, 2hand and plate food types, spoon takes priority over fork. A 2handbowl accepts only spoon and otherwise uses a drink animation, even if a fork is present. Other food types do not select these props. This selection does not equip, consume, require an unbroken utensil or make it necessary for eating; food possession, any separately declared companion and the usual eating action remain independent. It establishes an optional eating prop, not better nutrition or faster eating.'

STRUCTURE_DESTRUCTION = 'Outside LastStand and a vehicle, use the construction Destroy menu with an unbroken Sledgehammer tag/type, subject to AllowDestructionBySledgehammer on clients. The cursor enforces its eligible visible object list and client safehouse policy, excluding trees, loose inventory, vegetation, sheet ropes, ground floors, stair-top floors, specified scenery and occupied door walls. Select an object/corner side, approach and equip the selected type. Ongoing validity requires some recursive unbroken sledge and an existing target within 1.6 in each horizontal axis, not an explicit held-tool or Z recheck. Time is 300 minus ten per Strength level or instant one; walking/running stops. Completion drops container contents, applies conditional attached-window/light/barricade/curtain/rope/generator handling and removes grouped stairs/doors/graves or the target, with client sledgeDestroy versus local removal. Native linked-object lookup and command delivery remain separate. The source retains not-before-comparison corner expressions, an unbound square in lit-campfire cleanup, and an unchecked second grave square; complete teardown and salvage are not guaranteed. Normal completion can randomly wear the primary-hand item. Cheat bypasses normal tool/validity rules.'

for _predicate, _ko in (
    (CHOPPING, '접근 가능한 나무에 사용 가능한 벌목 도구를 장착하고 공격 가능한 상태여야 한다. 베는 동작에서 지구력과 도구 상태가 줄 수 있으며 걷거나 달리면 중단된다.'),
    (PLANT_CUTTING, '자르기 도구와 대상 덤불·벽 덩굴이 필요하다. 접근해 도구를 장착하며 걷기·달리기로 중단한다. 도구 마모와 지구력 소비가 있을 수 있고 잔가지 회수를 보장하지 않는다.'),
    (WOOD_BARRICADE, '판자를 추가할 수 있는 문·창문에 허용하는 망치와 판자·못 두 개가 필요하다. 접근해 도구와 판자를 장착하며 문은 작업 중 닫혀 있어야 한다. 걷거나 달리면 중단된다.'),
    (WOOD_UNBARRICADE, '판자 바리케이드와 허용하는 철거 도구가 필요하다. 가까이 접근해 도구를 장착하며 걷기·달리기로 중단한다. 판자 하나의 제거·반환을 요청하지만 못은 돌려주지 않는다.'),
    (METAL_BARRICADE, '호환 문·창문에 기존 바리케이드가 없고 토치 사용량 한 번과 금속판 한 장 또는 금속 막대 세 개가 필요하다. 접근해 장착하며 문은 작업 중 닫혀 있어야 한다. 걷기·달리기로 중단하고 이 경로에는 용접 마스크나 학습 제작법이 필요하지 않다.'),
    (METAL_UNBARRICADE, '금속 바리케이드에 사용량이 남은 토치를 장착하고 접근한다. 걷기·달리기로 중단하며 토치를 한 번 사용한다. 제거한 판 또는 같은 상태의 막대 세 개를 반환하도록 요청하지만 무손상 회수를 보장하지 않는다.'),
    (MEAL_UTENSIL, '지원하는 음식의 식사 동작에서 소지한 숟가락이 포크보다 우선 선택된다. 그릇을 든 식사 유형에는 숟가락만 선택되며 도구가 없어도 식사할 수 있다. 식사 소품으로 사용할 때 도구를 소비하지 않는다.'),
    (STRUCTURE_DESTRUCTION, '서버의 파괴·보호 구역 규칙이 허용하는 대상에 사용 가능한 슬레지해머를 장착하고 접근한다. 걷기·달리기로 중단하며 도구가 마모될 수 있다. 모든 구조물의 제거·재료 회수를 보장하지 않는다.'),
):
    QUALIFIERS[_predicate] = (_ko, _predicate)

for _name, _context, _ko, _en in (
    ('cut_bushes_and_vines', 'vegetation_removal', '덤불과 벽 덩굴을 제거하는 데 쓸 수 있다.', 'It can be used to remove bushes and wall vines.'),
    ('build_wooden_barricade', 'barricading', '문·창문에 판자 바리케이드를 추가하는 데 쓸 수 있다.', 'It can be used to add a plank barricade to a door or window.'),
    ('remove_barricade', 'barricading', '판자 바리케이드를 제거하는 데 쓸 수 있다.', 'It can be used to remove a plank barricade.'),
    ('build_metal_barricade', 'barricading', '문·창문에 금속 바리케이드를 설치하는 데 쓸 수 있다.', 'It can be used to install a metal barricade on a door or window.'),
    ('remove_metal_barricade', 'barricading', '금속 바리케이드를 제거하는 데 쓸 수 있다.', 'It can be used to remove a metal barricade.'),
    ('serve_as_eating_utensil', 'eating', '식사할 때 선택되는 도구로 쓸 수 있다.', 'It can serve as an optional eating utensil.'),
    ('destroy_structure', 'demolition', '허용하는 월드 구조물을 철거하는 데 쓸 수 있다.', 'It can be used to demolish eligible world structures.'),
):
    FUNCTIONS[_name] = (_context, _ko, _en)

LAMP_ACTION = 'lua/client/TimedActions/ISLightActions.lua'

PILLAR_INSERT = 'lua/client/BuildingObjects/TimedActions/ISInsertLightSourceFuelAction.lua'

PILLAR_REMOVE = 'lua/client/BuildingObjects/TimedActions/ISRemoveLightSourceFuelAction.lua'

PILLAR_LIGHT = 'lua/server/BuildingObjects/ISLightSource.lua'

BATTERY_TEMPLATE = 'scripts/vehicles/template_battery.txt'

HEADLIGHT_TEMPLATE = 'scripts/vehicles/template_headlight.txt'

CHARGER_ACTIONS = tuple('lua/client/TimedActions/' + n + '.lua' for n in (
    'ISPlaceCarBatteryChargerAction', 'ISTakeCarBatteryChargerAction', 'ISActivateCarBatteryChargerAction',
    'ISConnectCarBatteryToChargerAction', 'ISRemoveCarBatteryFromChargerAction'))

OLD_BATTERY_RECHARGE = 'lua/client/Vehicles/TimedActions/ISRechargeCarBattery.lua'

GENERATOR_ACTIONS = tuple('lua/client/TimedActions/' + n + '.lua' for n in (
    'ISActivateGenerator', 'ISPlugGenerator', 'ISTakeGenerator', 'ISFixGenerator', 'ISAddFuel', 'ISGeneratorInfoAction'))

GENERATOR_INFO = 'lua/client/ISUI/ISGeneratorInfoWindow.lua'

GENERATOR_MAP = 'lua/server/Map/MapObjects/MOGenerator.lua'

HEAVY_EQUIP = 'lua/client/TimedActions/ISEquipHeavyItem.lua'

WEAPON_EQUIP = 'lua/client/TimedActions/ISEquipWeaponAction.lua'

LIGHT_BULBS = {'Base.LightBulb' + suffix for suffix in ('', 'Blue', 'Cyan', 'Green', 'Magenta', 'Orange', 'Pink', 'Purple', 'Red', 'Yellow')}

ELECTRICAL_FIELDS = PLAIN_OBJECT_FIELDS | {'MetalValue', 'ConditionMax', 'VehicleType', 'MechanicsItem', 'ChanceToSpawnDamaged',
    'UseDelta', 'UseWhileEquipped', 'cantBeConsolided', 'RequiresEquippedBothHands', 'Tags', 'Tooltip',
    'ColorRed', 'ColorGreen', 'ColorBlue'}

LAMP_BULB = 'Use a modifiable light switch with no installed bulb. The menu selects recursive inventory types beginning LightBulb and deduplicates by type, without a condition/brokenness filter. Walk adjacent and transfer the selected bulb; the action takes 120 and stops on walking/running. Ongoing and completion validity require the item argument, modifiable lamp and empty bulb slot, not continued inventory ownership or remaining lamp object index. Completion calls native addLightBulb(character,item). Removal instead requires an installed bulb and calls removeLightBulb. Native acceptance, consumption, color, brightness, durability and actual illumination remain separate; replacing a bulb does not by itself power the lamp.'

LAMP_BATTERY = 'Use a modifiable lamp already configured for battery power with an empty battery slot. The menu requires a carried positive-delta Drainable Battery, then walks adjacent and transfers it. The 60-time action stops on walking/running and rechecks the item argument, modifiable battery lamp and empty slot, but not inventory ownership or positive charge. Completion repeats those guards then calls native addBattery. Removal requires a present lamp battery and delegates removeBattery. Native charge transfer, inventory consumption, battery drain and light emission remain separate.'

LAMP_CONVERSION = 'The modifiable, not-yet-battery-powered lamp menu requires Electricity five, an unbroken Screwdriver-tag tool and ElectronicsScrap in recursive inventory. Approach and equip the screwdriver and scrap; time is 300 and walking/running stops. Action validity requires its item argument, modifiable nonbattery lamp and Electricity five, not continued screwdriver possession. Completion also checks that exact Base.ElectronicsScrap is in inventory, clears it from hands, removes it and sets UseBattery true. This configures a battery connector; it does not supply a battery or establish illumination.'

PILLAR_BATTERY = 'The active pillar-lamp factory declares Base.Battery as fuel. Its world menu accepts matching positive-delta Drainable fuel, approaches and queues a 50-time insertion; the caller does not transfer a nested item. Start requires positive delta and ongoing validity requires inventory possession only. Completion sends item ID/type/delta. The server selects the first matching thumpable light on the square, creates the fuel with that delta, inserts it and requests removal of the input and return of any previous fuel. Removal requires current fuel and returns the native removed item. Walking/running stops. Native light binding, charge/illumination and non-atomic server/inventory delivery remain separate.'

CHARGER_PLACEMENT = 'The exact CarBatteryCharger inventory selection transfers it and queues placement for 100 time on the character current square. Possession must remain valid; walking/running stops. The server rejects a second charger on the square, requests input removal and creates/transmits IsoCarBatteryCharger from that item. It does not check electricity for placement and assumes the supplied square exists. Taking approaches an existing charger with no battery, takes 50 time and rechecks those conditions; the server returns its item when present and removes the world object. Native object creation and non-atomic delivery remain separate.'

CHARGER_CONTROLS = 'Use an existing placed charger and approach it. With no battery, the menu accepts recursive CarBattery1/2/3 or other CarBattery-tag items below full charge; connecting transfers the battery and takes 100 time. Ongoing checks charger existence and battery possession, not empty slot or charge; the server rejects an occupied charger, removes the input by ID and sets/syncs the battery. With a battery, activation is offered only with square electricity or an indoor square before electricity shutoff. The 50-time toggle rechecks charger existence and changed activation state, not power or battery. Server activation sets/syncs the flag. Battery removal takes 100 and rechecks charger/battery, then the server clears/syncs and returns it. Walking/running stops all these actions. Actual charging rate and charge change are native IsoCarBatteryCharger behavior; the unused ISRechargeCarBattery class is not a live entry point or proof of guaranteed full charging.'

VEHICLE_BATTERY_EXCHANGE = 'The Battery vehicle template names Base.CarBattery, with the exact CarBattery1/2/3 VehicleType mapping remaining a runtime compatibility condition. Both install and uninstall require a kept primary-hand Screwdriver and base time 100 with the existing mechanics action adjustment. Installation uses the Engine area/EngineDoor and key-access tests; neither table declares a skill, recipe, profession or trait threshold. Uninstall additionally rejects an engine that is started or running, despite the contrary comment. Existing mechanics eligibility, transfer, native exact-part acceptance, server roll and non-atomic return/install conditions remain attached. A positive-charge requirement is not added to installing a battery.'

VEHICLE_BATTERY_CYCLE = 'After this exact item binds to the installed Battery part, its update subtracts 0.025 when isEngineRunning changes from a false/nil stored flag to true. Positive elapsedMinutes with a running engine adds elapsedMinutes*0.001 capped at one. Changes update UsedDelta and may transmit at two-decimal comparison. Headlights, lightbar and siren use positive native battery charge; active lights/siren/radio while the engine is off and active heater while running call chargeBattery. That helper applies delta twice, first with a lower clamp and then an upper clamp, as written. It must not be normalized to a single delta. These local charge adjustments do not prove native starting power, illumination, sound, actual battery capacity or successful engine start; startEngine delegates tryStartEngine after driver checks.'

VEHICLE_BULB_EXCHANGE = 'The Headlight wildcard vehicle template explicitly accepts Base.LightBulb with specificItem false; colored LightBulb forms are not listed and are not generalized into that slot. Installation and removal require a kept primary-hand Screwdriver and base time 100, key-access and existing mechanics eligibility/transfer/server conditions. Front positions use Engine and rear positions TruckBed. Create.Headlight constructs spotlights only for the two front IDs. Update requires a light object and disables activation when the part item is absent or native battery charge is nonpositive; active lights with stopped engine consume battery through the actual double-delta helper. Native item compatibility, emitted light, condition-dependent range/intensity and delivery remain separate.'

GENERATOR_CONTROL = 'This exact Base.Generator must become an installed IsoGenerator; map replacement and moveable construction explicitly create that type, while ordinary inventory dropping delegates native world insertion. The world menu approaches the object. Connecting requires known Generator at menu entry and takes 300; disconnecting is offered while connected and inactive. The action only rechecks object existence and changed connection state before setConnected. Toggle takes 30 and requires changed activation, object existence, positive fuel and positive condition; connection is additionally required for activation. As written, the fuel/condition checks also apply to deactivation. Starting at condition <= 50 can fail on a one-in-two roll; otherwise setActivated is called. Walking/running stops, with instant-time exceptions. Native supply range, electricity, exhaust toxicity and fuel/condition evolution are not inferred from these controls or the information tooltip.'

GENERATOR_REPAIR = 'Repair an inactive installed generator below condition 100. The menu requires known Generator and recursive ElectronicsScrap; approach and transfer a scrap. The action checks object existence, inactive/below-full state and some recursive scrap, not knowledge again. Time is 150 minus Electricity*3 or instant one; walking/running stops. Completion removes one selected scrap, adds 4 + Electricity/2 to generator condition and grants Electricity XP five. While still below full it queues another scrap transfer/repair if available. Native setter clamping and nested inventory removal remain separate; one scrap is not a guaranteed full repair.'

GENERATOR_REFUEL = 'The menu requires an inactive installed generator below fuel 100 and a Petrol-tag/PetrolCan with a positive integer use. The submenu selects unbroken Petrol-tag Drainable items with positive delta, groups them and requires an adjacent tile. Approach, equip and queue each selected container for 70 + delta*40 time, or instant one. The action validity is (generator exists AND primary item matches) OR secondary item matches, not a conjunction over both hands; it does not recheck inactivity or capacity. Walking/running stops. Completion loops while container delta is positive and generator fuel plus added amount is below 100, calls Use and adds ten fuel per iteration, then sets the sum. Partial units can add ten and the sum can exceed 100 before the native setter; native Use termination/clamping and installed generator binding remain separate.'

GENERATOR_HANDLING = 'The inventory Generator take action approaches its container, clears hands and queues a 100-time heavy-item transfer. It requires the item in its source container, not already in the player inventory or both hands, and any vehicle-container access. Completion force-drops held heavy items, transfers the generator and sets both hands. Taking an installed generator instead requires an existing disconnected object, approaches/clears hands and takes 100 or instant one. Completion creates Base.Generator, copies condition and positive fuel metadata, sets both hands and removes the world object. Walking/running stops. Ordinary drops and forced heavy-item drops call native AddWorldInventoryItem; installed-object creation and non-atomic delivery remain native. No independent placement permission or guaranteed preservation of arbitrary metadata is inferred.'

GENERATOR_INSPECTION = 'Approach an existing generator and open its zero-time information action. The window reads rounded-up fuel, condition, activated powered-item list and rounded total consumption. It shows an indoor toxicity warning when the square is not outside and has a building. These are getter-based information and a warning, not local implementations of electricity, fuel consumption or toxic injury. Native generator state and UI object lifetime remain separate; update requests text before its later missing-object removal guard.'

for _predicate, _ko in (
    (LAMP_BULB, '교체 가능한 조명에 전구가 없어야 한다. 접근해 전구를 옮기며 걷기·달리기로 중단한다. 삽입은 조명의 메서드에 맡기며 전구 설치만으로 전력·색·밝기를 보장하지 않는다.'),
    (LAMP_BATTERY, '건전지용으로 개조한 조명의 빈 칸에 남은 충전량이 있는 건전지를 넣는다. 접근해 옮기며 걷기·달리기로 중단한다. 실제 전력 전달과 발광은 조명 구현에 달려 있다.'),
    (LAMP_CONVERSION, '전기 기술 5와 사용 가능한 드라이버·전자 스크랩이 필요하다. 개조 가능한 조명에 접근하고 작업하면 스크랩 하나를 소비해 건전지 사용 상태를 설정한다. 건전지를 함께 넣지는 않는다.'),
    (PILLAR_BATTERY, '건전지를 연료로 받는 기둥 조명에 남은 충전량이 있는 건전지를 사용한다. 접근·소지 조건이 필요하고 걷기·달리기로 중단하며 이전 건전지의 반환은 설치 처리에 달려 있다.'),
    (CHARGER_PLACEMENT, '소지한 충전기를 현재 칸에 설치한다. 한 칸에 충전기를 두 개 놓을 수 없으며 건전지가 없는 충전기만 회수할 수 있다. 걷거나 달리면 중단된다.'),
    (CHARGER_CONTROLS, '설치한 충전기에 완충되지 않은 차량 배터리를 연결한다. 켜기 메뉴에는 전력 조건이 필요하고 배터리를 꺼낼 수도 있다. 접근·행동 유효성 조건을 만족해야 하며 실제 충전은 충전기의 엔진 구현에 달려 있다.'),
    (VEHICLE_BATTERY_EXCHANGE, '해당 차량 배터리 자리에 맞아야 하며 드라이버와 차량 정비 접근·열쇠 조건이 필요하다. 제거할 때는 엔진이 시동 중이거나 운전 중이면 안 된다.'),
    (VEHICLE_BATTERY_CYCLE, '호환 차량에 장착되면 엔진 운전 상태 변경과 경과 시간에 따라 충전량을 조정한다. 전기 장치 소비는 별도 조건과 계산을 사용하며 시동 성공이나 조명 효과를 보장하지 않는다.'),
    (VEHICLE_BULB_EXCHANGE, '해당 차량 전조등 자리에 맞는 기본 전구와 드라이버가 필요하다. 차량 정비의 접근·열쇠 조건과 장착 판정을 따르며 색 전구까지 호환된다고 일반화하지 않는다.'),
    (GENERATOR_CONTROL, '설치한 발전기에 접근해 연결·활성 상태를 조작한다. 연결에는 발전기 지식이 필요하며 켜려면 연결·연료·상태 조건을 만족해야 한다. 상태가 낮으면 시동에 실패할 수 있다.'),
    (GENERATOR_REPAIR, '작동하지 않는 손상 발전기에 발전기 지식과 전자 스크랩이 필요하다. 한 번에 스크랩 하나를 사용해 상태를 늘리고 재료가 남으면 수리를 이어갈 수 있다. 한 번으로 완전 수리를 보장하지 않는다.'),
    (GENERATOR_REFUEL, '꺼져 있고 가득 차지 않은 발전기에 사용 가능한 휘발유 용기를 장착하고 접근한다. 소모 단위마다 연료를 더하며 부분 단위 처리와 최종 상한은 실제 소비·설정 처리에 달려 있다.'),
    (GENERATOR_HANDLING, '발전기를 양손으로 들거나 연결을 해제한 설치 발전기를 회수할 수 있다. 접근·원래 용기 소지 조건을 따르며 걷기·달리기로 중단한다. 회수 시 상태와 양수인 연료량을 복사한다.'),
    (GENERATOR_INSPECTION, '접근 가능한 설치 발전기의 연료·상태·전력 사용 정보를 확인한다. 실내 독성 경고를 표시하지만 정보 창이 실제 공급이나 독성 효과를 구현하지는 않는다.'),
):
    QUALIFIERS[_predicate] = (_ko, _predicate)

for _name, _ko, _en in (
    ('install_light_bulb', '교체 가능한 조명에 전구를 넣을 수 있다.', 'It can be inserted into a lamp with a replaceable bulb.'),
    ('supply_lamp_battery', '건전지용 조명에 건전지를 넣는 데 쓸 수 있다.', 'It can be inserted into a battery-powered lamp.'),
    ('supply_pillar_light_battery', '기둥 조명에 건전지를 공급할 수 있다.', 'It can supply a battery to a pillar lamp.'),
    ('convert_lamp_to_battery', '조명을 건전지용으로 개조하는 데 쓸 수 있다.', 'It can be used to convert a lamp to battery power.'),
    ('place_vehicle_battery_charger', '차량 배터리 충전기를 설치하거나 회수할 수 있다.', 'The vehicle battery charger can be placed or retrieved.'),
    ('operate_vehicle_battery_charger', '설치한 충전기에 배터리를 연결·분리하고 활성 상태를 조작할 수 있다.', 'A battery can be connected to or removed from the placed charger, and its activation can be controlled.'),
    ('connect_to_vehicle_battery_charger', '차량 배터리 충전기에 연결할 수 있다.', 'It can be connected to a vehicle battery charger.'),
    ('install_vehicle_battery', '호환 차량에 배터리를 장착할 수 있다.', 'It can be installed as a battery in a compatible vehicle.'),
    ('remove_vehicle_battery', '차량에 장착한 배터리를 제거할 수 있다.', 'The installed vehicle battery can be removed.'),
    ('install_vehicle_bulb', '호환 차량의 전조등 자리에 장착할 수 있다.', 'It can be installed in a compatible vehicle light slot.'),
    ('remove_vehicle_bulb', '차량에 장착한 전구를 제거할 수 있다.', 'The installed vehicle bulb can be removed.'),
    ('control_installed_generator', '설치한 발전기의 연결·활성 상태를 조작할 수 있다.', 'The installed generator connection and activation can be controlled.'),
    ('repair_generator', '설치한 발전기를 수리하는 데 쓸 수 있다.', 'It can be used to repair an installed generator.'),
    ('refuel_generator', '설치한 발전기에 연료를 넣는 데 쓸 수 있다.', 'It can be used to refuel an installed generator.'),
    ('handle_generator', '발전기를 양손으로 들거나 설치된 발전기를 회수할 수 있다.', 'The generator can be held in both hands or retrieved from the world.'),
    ('inspect_generator', '발전기의 연료·상태와 전력 사용 정보를 확인할 수 있다.', 'The generator fuel, condition and power-use information can be inspected.'),
    ('supply_portable_device_charge', '휴대 기기에 넣어 남은 충전량을 공급할 수 있다.', 'It can be inserted into a portable device to supply its remaining charge.'),
):
    FUNCTIONS[_name] = ('electrical_controls', _ko, _en)

EFFECTS['installed_vehicle_battery_charge', 'adjust_on_engine_state'] = (
    '장착한 차량 배터리의 충전량은 엔진 운전 상태에 따라 조정된다.',
    'The installed vehicle battery charge is adjusted according to engine running state.')

ELECTRICAL_SOURCES = (LAMP_ACTION, PILLAR_INSERT, PILLAR_REMOVE, PILLAR_LIGHT, BATTERY_TEMPLATE,
    HEADLIGHT_TEMPLATE, *CHARGER_ACTIONS, OLD_BATTERY_RECHARGE, *GENERATOR_ACTIONS, GENERATOR_INFO,
    GENERATOR_MAP, HEAVY_EQUIP, WEAPON_EQUIP)

PLOW_CURSOR = 'lua/server/Farming/BuildingObjects/farmingPlot.lua'

PLOW_ACTION = 'lua/client/Farming/TimedActions/ISPlowAction.lua'

SHOVEL_PLANT = 'lua/client/Farming/TimedActions/ISShovelAction.lua'

GRAVE_CURSOR = 'lua/server/BuildingObjects/ISEmptyGraves.lua'

GRAVE_FILL = 'lua/client/TimedActions/ISFillGrave.lua'

NET_OBJECT = 'lua/server/Fishing/BuildingObjects/FishingNet.lua'

NET_CHECK = 'lua/client/Fishing/TimedActions/ISCheckFishingNetAction.lua'

BASE_OBJECT = 'lua/shared/ISBaseObject.lua'

GROUND_TOOLS = {'Base.' + n for n in ('HandFork', 'GardenHoe', 'GardenFork', 'PickAxe', 'Shovel', 'Shovel2', 'SnowShovel')} | {'farming.HandShovel'}

DRAINABLE_MATERIALS = {'Base.' + n for n in ('BakingSoda', 'Cornflour', 'Cornmeal', 'Flour', 'GravyMix', 'PancakeMix',
    'Yeast', 'Vinegar', 'DuctTape', 'Glue', 'Woodglue', 'Twine', 'Wire', 'GunPowder', 'IronIngot', 'WeldingRods', 'FishingLine')}

DRAINABLE_MATERIAL_FIELDS = MATERIAL_OBJECT_FIELDS | {'UseDelta', 'UseWhileEquipped', 'ConsolidateOption', 'WeightEmpty', 'Tags'}

FURROW_DIGGING = 'The farming menu selects an unbroken DigPlow tool, preferring the primary hand then recursive inventory. Mouse entry excludes vehicles; joypad has a separate branch. The cursor requires no farm object, a free-or-midair square and a natural floor texture. Approach through the building cursor and equip the tool. The 110 action stops on walking/running, but isValid always returns true: possession, condition and plot eligibility are not rechecked. Completion sends plow, raises fatigue .006, lowers endurance .0013 and independently rolls a one-in-five worm return. The server accepts an existing square, removes any current plant, clears removable vegetation and creates a plowed object. The bare-hand scratch roll is not applied with a tool. Native placement, inventory and command delivery remain separate; digging does not sow or guarantee growth.'

PLANT_REMOVAL = 'With a farm object, select an unbroken DigPlow tool, approach and equip it. The 40 removal action stops on walking/running. Validity updates the plant and checks its world object only, not tool condition, possession or equipment. Completion uses the captured tool container then sends removePlant; the server removes the current plant if present. This clears the farm object rather than harvesting. Missing tool/container and native command delivery remain separate.'

GRAVE_DIGGING = 'Outside a vehicle, select a recursive unbroken DigGrave tool and natural ground; joypad can open the cursor separately. Two available natural-floor squares at Z no greater than zero are required. Actual validation combines their shovelled-ground history checks with OR, unlike the separate previews. Approach the closer square, transfer and equip both hands. Build time is 150 with instant/Handy handling; walking/running stops. Shared validity checks same floor and window reachability, not continuing tool ownership or all placement conditions. Completion creates two EmptyGraves objects with zero corpses and filled=false, removes a removable object and disables erosion on each square. Native placement, unchecked floor references and partial two-square creation remain bounded. No automatic burial is implied.'

GRAVE_FILLING = 'Select an unbroken DigGrave tool for an unfilled EmptyGraves object; no corpse count is required. Approach and equip both hands, then run the 150 action or instant one, interrupted by walking/running. isValid always returns true. Completion derives the paired square from orientation/spriteType, marks its EmptyGraves objects filled and shifts sprite indices by eight on both squares. The second square is not nil-guarded. Burying a fifth corpse can queue this same fill action if a shovel was selected; burial itself needs no shovel. Native object/sprite delivery and partial paired-square update remain separate.'

THUMPABLE_SCRAP = 'The movable fallback selects a dismantlable IsoThumpable with a sprite when ordinary movable properties do not permit scrap. Visibility permits unseen adjacent doors/windows only. Walk adjacent, find recursive unbroken Saw and Screwdriver tools and equip their selected types in primary/secondary hands. Time is 200 minus Strength*10 or movable-cheat ten. The action checks same Z, target presence, distance at most 1.6 on each axis, barrier reachability and safehouse membership, stopping on walking/running; tools are not continuously rechecked. Completion returns a random one-to-count for each need: entry, except a pillar-light Torch returns empty plus current fuel. Clients send OnDestroyIsoThumpable; grouped stairs or the target are removed. Displayed Woodwork chance is not used by this fallback. Native factories/removal remain separate; the commented legacy menu is not live.'

NET_PLACEMENT = 'The water menu selects recursive FishingNet, but the placement-distance line dereferences storeWater instead of the selected net water object. The cursor requires a top-level net and water within distance five. Inherited Type=fishingNet permits the water-distance branch when adjacency walking fails; skipWalk differs from parent skipWalk2. No build action is queued. Creation adds/transmits an object before removing a held or top-level net, then timestamps the square, not the individual net. No duplicate-net guard is present. Native inventory/object delivery and the storeWater menu binding remain separate; placement is not atomic.'

NET_CHECKING = 'Select a placed net within distance five after one whole elapsed hour from its square timestamp. Checking takes hours*13 capped at 150 and stops on walking/running. Validity requires trap/square and elapsed hours within two of the captured hours, not continued distance or object-index membership. After more than 15 hours a one-in-five roll removes the net and returns BrokenFishingNet first. Otherwise hours are capped at 20, each with a one-in-four BaitFish return. Any catch adds one Fishing XP; the action adds another even after breakage. Nonbreak checking resets the shared square timestamp. Native item returns and random rolls remain separate; neither catch nor preserved net is guaranteed.'

NET_REMOVAL = 'The menu offers removal within distance five without walking or a timed action. It requests object removal then adds a new Base.FishingNet. Original item state is not preserved and the square timestamp is not cleared. Native removal and item return are not atomic.'

STONE_TOOL_WEAR = 'Shared ISBuildAction completion checks the current primary-hand item for exact HammerStone, even if its cursor needs no hammer. A zero roll in native ConditionLowerChance subtracts one condition and invokes checkWeapon before creation. The current tool, not a captured participant, is used; native wear probability and subsequent object creation remain separate.'

for name, predicate, ko, en in (
    ('dig_furrow', FURROW_DIGGING, '농사를 지을 고랑을 팔 수 있다.', 'It can dig a farming furrow.'),
    ('remove_farm_plant', PLANT_REMOVAL, '재배 중인 작물이나 고랑을 제거할 수 있다.', 'It can remove a farm plant or furrow.'),
    ('dig_grave', GRAVE_DIGGING, '무덤 자리를 팔 수 있다.', 'It can dig a grave.'),
    ('fill_grave', GRAVE_FILLING, '파 놓은 무덤을 흙으로 메울 수 있다.', 'It can fill a dug grave.'),
    ('dismantle_built_object', THUMPABLE_SCRAP, '분해 가능한 건축물을 해체하는 데 쓸 수 있다.', 'It can help dismantle eligible built objects.'),
    ('place_fishing_net', NET_PLACEMENT, '물에 어망을 설치할 수 있다.', 'It can be placed as a fishing net in water.'),
    ('check_fishing_net', NET_CHECKING, '설치한 어망을 확인해 미끼용 물고기를 얻을 수 있다.', 'Checking the placed net can return bait fish.'),
    ('remove_fishing_net', NET_REMOVAL, '설치한 어망을 회수할 수 있다.', 'The placed fishing net can be retrieved.'),
):
    FUNCTIONS[name] = ('ground and object controls', ko, en)
    QUALIFIERS[predicate] = (ko, en)

QUALIFIERS[STONE_TOOL_WEAR] = ('건축 행동을 마칠 때 주 손에 든 돌망치가 확률적으로 마모될 수 있다.', 'A stone hammer in the primary hand may wear when a build action completes.')

EFFECTS[('held_stone_hammer_condition', 'may_decrease_on_build')] = QUALIFIERS[STONE_TOOL_WEAR]

FUNCTIONS['collect_ground_into_bag'] = ('ground collection', '대응하는 지면의 흙·모래·자갈을 포대에 담는 데 쓸 수 있다.', 'It can collect dirt, sand or gravel from matching ground into a bag.')

BBQ_MENU = 'lua/client/ISUI/ISBBQMenu.lua'

FIREPLACE_MENU = 'lua/client/ISUI/ISFireplaceMenu.lua'

BLACKSMITH_MENU = 'lua/client/Blacksmith/ISUI/ISBlacksmithMenu.lua'

TAKE_FUEL = 'lua/client/TimedActions/ISTakeFuel.lua'

BURN_CORPSE = 'lua/client/TimedActions/ISBurnCorpseAction.lua'

HEAT_ACTIONS = tuple('lua/client/TimedActions/IS' + family + name + '.lua'
    for family in ('BBQ', 'Fireplace') for name in ('AddFuel', 'LightFromLiterature', 'LightFromPetrol', 'LightFromKindle'))

PROPANE_ACTIONS = tuple('lua/client/TimedActions/ISBBQ' + name + '.lua'
    for name in ('InsertPropaneTank', 'RemovePropaneTank', 'Toggle'))

INDUSTRIAL_ACTIONS = tuple('lua/client/Blacksmith/TimedActions/IS' + name + '.lua' for name in (
    'UseBellows', 'AddCoalInFurnace', 'FurnaceLightFromPetrol', 'FurnaceLightFromLiterature', 'FurnaceLightFromKindle',
    'DrumLightFromPetrol', 'DrumLightFromLiterature', 'DrumLightFromKindle', 'AddLogsInDrum', 'RemoveCharcoal', 'EmptyDrum', 'PutOutFireDrum'))

DRUM_SOURCES = ('lua/client/MetalDrum/CMetalDrumSystem.lua', 'lua/client/MetalDrum/CMetalDrumGlobalObject.lua',
    'lua/server/MetalDrum/SMetalDrumSystem.lua', 'lua/server/MetalDrum/SMetalDrumGlobalObject.lua',
    'lua/server/MetalDrum/BuildingObjects/ISMetalDrum.lua', 'lua/server/Map/MapObjects/MOMetalDrum.lua')

HEAT_SOURCES = (BBQ_MENU, FIREPLACE_MENU, BLACKSMITH_MENU, TAKE_FUEL, BURN_CORPSE,
    *HEAT_ACTIONS, *PROPANE_ACTIONS, *INDUSTRIAL_ACTIONS, *DRUM_SOURCES)

PETROL_ITEMS = {'Base.' + n for n in ('PetrolCan', 'WaterBottlePetrol', 'PetrolPopBottle', 'WhiskeyPetrol', 'WinePetrol', 'PetrolBleachBottle')}

EMPTY_PETROL_ITEMS = {'Base.' + n for n in ('EmptyPetrolCan', 'WaterBottleEmpty', 'PopBottleEmpty', 'BleachEmpty', 'WhiskeyEmpty', 'WineEmpty', 'WineEmpty2')}

FUEL_FIELDS = MATERIAL_OBJECT_FIELDS | {'Tags', 'UseDelta', 'UseWhileEquipped', 'ReplaceOnDeplete', 'ReplaceTypes',
    'ReplaceOnUseOn', 'CanStoreWater', 'StaticModel', 'ReplaceInPrimaryHand', 'ReplaceInSecondHand', 'ToolTip', 'WeightEmpty',
    'FillFromDispenserSound', 'FillFromTapSound', 'UseWorldItem', 'ScaleWorldIcon', 'cantBeConsolided', 'ConsolidateOption'}

PUMP_CONTAINER = 'At a fueled piped pump with menu electricity, the same building and an accessible adjacent tile, choose an unbroken EmptyPetrol-tag or nonfull Drainable Petrol-tag container. Transfer and equip secondary, then queue the action. Ongoing validity checks only pump fuel, not electricity, possession or position. Start replaces an empty container by its PetrolSource replacement or Base.PetrolCan fallback and updates held hands. The actual replacement is distinct from the menu temporary item that copies condition/favorite and may be queued for return to a nested container. Duration is fifty per requested use. Updates subtract newly transferred integer uses from the pump and set item charge; completion instead adds the remaining difference to pump fuel. Walking/running stops and partial transfers persist. Native creation, piped-fuel accounting and delivery remain separate; neither full filling, state preservation nor atomic conservation is guaranteed.'

VEHICLE_CONTAINER = 'Vehicle entry selects a Gasoline container part with the engine not started. Adding needs a positive Petrol container and free tank space; siphoning needs fuel and an empty or nonfull compatible container. Select, transfer, exit the vehicle, path to the part area and equip primary for adding or secondary for siphoning. Adding prefers the held eligible can, otherwise the most integer uses; siphoning first prefers exact EmptyPetrolCan or BleachEmpty before the general selector. Both actions return true from ongoing validity. Empty siphon containers are replaced using PetrolSource or the PetrolCan fallback. Can capacity is JerryCanLitres times floor(1/UseDelta)/8; duration is fifty per transferred litre. Addition floors intermediate tank quantities, siphoning ceils them, and completion requests the exact target through setContainerContentAmount. Donor charge follows progress and depleted addition calls Use; cancellation retains changes. These constructors do not explicitly set walking/running interruption. Native capacity, inventory creation and client/server delivery remain independent; a selected container is not itself a vehicle tank.'

HEARTH_FUEL = 'A nonpropane barbecue or fireplace accepts items through the camping fuel type/category tables and ISCampingMenu fuel eligibility. The menus deduplicate display names; multiple-use requests transfer eligible supplies, approach and unequip them before queuing time 100 per use. Ongoing validity checks the object index and inventory item, not continued category eligibility or barbecue propane state. Completion uses a Drainable once or clears hands and removes the whole other item, then requests the table duration in minutes as fuel. Fireplace instant actions take one. The server selects the first matching object on the square and adds/synchronizes fuel. Native combustion, heat and non-atomic inventory/server delivery are not established by this supply operation.'

HEARTH_TINDER = 'For an unlit nonpropane barbecue or fireplace, choose camping-valid tinder and a selected lighter, matches or StartFire item, approach and transfer both. The 100-time action checks the object index, both inventory items and unlit state, not igniter charge. It removes the whole tinder even if Drainable, uses the igniter and requests lighting with tinder fuel minutes. The barbecue computes duration from its tinder table entry; the fireplace passes a parallel amount list that is not reordered when tinder is sorted. Fireplace menu selection also retains an unbound types lookup in startFireTypes. The server adds the passed fuel then lights only when fuel exists and it is not already lit. Walking/running stops; native fire state and command delivery remain separate.'

HEARTH_PETROL = 'For an unlit fueled nonpropane barbecue or fireplace, select a Petrol container and lighter/matches/StartFire implement, approach and transfer both. Barbecue menu selection requires positive petrol delta; fireplace entry does not, but both 20-time actions require positive delta in both items, possession, an existing object, fuel and unlit state. Completion uses both items once and requests lighting; walking/running stops. Server lighting requires fuel and unlit state. Fireplace retains its unbound types ignition lookup. Native lighting and inventory/server delivery are not guaranteed by menu availability.'

INDUSTRIAL_PETROL = 'Outside LastStand and a vehicle, the live existing-furnace/drum menu selects positive petrol and an igniter. Furnace entry requires fuel and no fire; drum entry requires logs, no fire and no charcoal. Approach and transfer both for time 20, with walking/running interruption. Furnace ongoing validity requires both positive-delta inventory items, a furnace, fuel and no fire. Drum ongoing validity checks its current object and both positive-delta inventory items but does not recheck logs, charcoal or fire. Neither completion consumes petrol or the igniter. Furnace completion sets fire started without an explicit sync; drum completion sends lightFire, whose server requires logs and unlit state. Native fire/heat and delivery remain separate.'

INDUSTRIAL_TINDER = 'The live existing-furnace/drum menu outside LastStand and a vehicle uses raw camping tinder type/category tables, without the camping favorite, worn or fabric filters. Entry requires an igniter and respectively fueled unlit furnace or logged unlit noncharcoal drum. Approach, transfer and unequip tinder for time 100. Furnace ongoing validity requires a furnace, inventory tinder/igniter and unlit state, not fuel or igniter charge; drum validity only rechecks its object and the two items. Completion removes the whole tinder and uses the igniter. Furnace client lighting is commented out and only the nonclient branch sets fire started. Drum sends lightFire; its server requires logs and no fire. The passed coal-valued fuelAmt is unused for furnace fuel and ignored by the drum server. Walking/running stops; no guaranteed client furnace ignition is inferred.'

HEAT_FRICTION = 'Select PercedWood and WoodenStick, preferring it over TreeBranch, with positive endurance. Hearth entry needs an unlit fueled object; industrial entry needs an unlit fueled furnace or an unlit logged noncharcoal drum outside LastStand/vehicle. Approach for a 1500-time action; fireplace and industrial callers transfer the inputs, barbecue does not. Ongoing checks require the target, both inventory items, unlit state and positive endurance, but do not recheck fuel or drum logs/charcoal. Each update costs .0001 endurance times game multiplier. After twenty percent, random ignition is one in 300 and a failed roll permits one-in-300 stick breakage; Outdoorsman changes these to one in 150 and one in 450. Broken sticks/branches are removed, not PercedWood. Successful barbecue/fireplace/drum attempts send their server lighting request. Furnace client lighting is commented out; nonclient success sets fire. Normal timed completion alone does not ignite. Walking/running stops; native random outcomes and delivery remain separate.'

PROPANE_BARBECUE = 'A propane barbecue selects a positive-delta Base.PropaneTank from recursive inventory, otherwise nearby unblocked world squares. Approach the world tank or barbecue and transfer an inventory tank for insertion time 100. Ongoing validity requires the barbecue object and inventory/world tank, not charge or an empty installed slot. Completion removes the input and sends its delta. Server insertion drops an existing tank on the player square, creates a new tank with the sent delta and installs it. Removal time 100 requires an installed tank and returns it to the player square. Toggle time 50 requires propane mode and fuel, not an object-index check; server toggling requires fuel. Walking/running stops. Native fuel burn, heat and non-atomic replacement are separate; empty-slot-only insertion and preserved original item identity are not inferred.'

FURNACE_FUEL = 'Outside LastStand and a vehicle, the live furnace menu selects Coal or Charcoal and a furnace below fuel 100, then approaches for time 100. Start checks the supply and fuel below 100; ongoing validity only requires the supply in inventory. Completion loops inclusively from zero through floor(delta/UseDelta), adds ten fuel and calls Use each iteration, and breaks only when fuel equals 100. Walking/running stops and fuel is synchronized after completion. Native clamping/depletion remain separate: the inclusive loop is not a safe exact-use count and Coal remains declared obsolete rather than assumed spawnable.'

BELLOWS_USE = 'The live furnace menu outside LastStand and a vehicle selects Bellows when fire is started and heat is below 100. Approach for time 300. Ongoing validity only requires inventory bellows, not fire, heat or endurance. Each update adds .3 furnace heat and removes .0002 endurance without applying the game-time multiplier; stop and completion synchronize the furnace. Walking/running stops and the bellows is not used up. Native heat clamping, persistence and actual smelting remain separate.'

DRUM_LOGS = 'The live metal-drum menu requires a nearby existing empty nonburning drum without water or charcoal and five Base.Log in inventory. Approach and queue time 30. Start excludes fire and charcoal; ongoing validity refreshes the drum object and requires the add/remove request to differ from haveLogs, not continued inventory count. The server addLogs requests five removals then marks logs present without rechecking the count or state. RemoveLogs returns five logs and clears state without a haveLogs guard. Lighting separately requires logs and an unlit drum. Ten-minute updates advance a lit logged drum to charcoal at tick twelve, clear logs/fire and set charcoal; conditional removal returns two Charcoal. Walking/running stops. Native delivery is non-atomic and a carried Log does not guarantee charcoal production.'

CORPSE_IGNITION = 'The corpse menu requires a selected corpse, positive integer-use Petrol and a StartFire item or lighter/matches. Approach, equip the preferred igniter primary and petrol secondary, and queue time 110 or instant one. Ongoing validity checks the corpse index and the inventory items lazily captured from the current hands, not their type, charge or continued equipment. Completion calls native character.burnCorpse, then uses both captured items. Walking/running stops. Native fire/corpse effects and successful consumption are separate; the Lua request does not guarantee destruction.'

for _name, _context, _ko, _en in (
    ('fill_petrol_container', 'fuel_handling', '주유소에서 연료 용기를 채우는 데 쓸 수 있다.', 'It can be used as a container when drawing fuel from a pump.'),
    ('transfer_vehicle_fuel', 'fuel_handling', '차량과 용기 사이에서 연료를 옮기는 데 쓸 수 있다.', 'It can be used to transfer fuel between a vehicle and a container.'),
    ('supply_hearth_fuel', 'fire_starting', '비프로판 바비큐·벽난로의 연료로 쓸 수 있다.', 'It can supply fuel to a nonpropane barbecue or fireplace.'),
    ('provide_hearth_tinder', 'fire_starting', '바비큐·벽난로의 불쏘시개로 쓸 수 있다.', 'It can serve as tinder for a barbecue or fireplace.'),
    ('ignite_hearth_with_tinder', 'fire_starting', '불쏘시개를 쓰는 바비큐·벽난로 점화에 쓸 수 있다.', 'It can ignite tinder for a barbecue or fireplace.'),
    ('ignite_hearth_with_petrol', 'fire_starting', '휘발유를 쓰는 바비큐·벽난로 점화에 쓸 수 있다.', 'It can participate in petrol ignition of a barbecue or fireplace.'),
    ('ignite_industrial_fire_with_petrol', 'fire_starting', '기존 화로·금속 드럼의 휘발유 점화 동작에 쓸 수 있다.', 'It can participate in petrol ignition of an existing furnace or metal drum.'),
    ('provide_industrial_tinder', 'fire_starting', '기존 화로·금속 드럼의 불쏘시개 점화 동작에 쓸 수 있다.', 'It can participate in tinder ignition of an existing furnace or metal drum.'),
    ('ignite_industrial_tinder', 'fire_starting', '기존 화로·금속 드럼의 불쏘시개에 불을 붙이는 동작에 쓸 수 있다.', 'It can ignite tinder for an existing furnace or metal drum.'),
    ('kindle_heat_sources', 'fire_starting', '바비큐·벽난로·화로·금속 드럼의 마찰 점화에 쓸 수 있다.', 'It can participate in friction ignition of barbecues, fireplaces, furnaces and metal drums.'),
    ('supply_propane_barbecue', 'fuel_handling', '프로판 바비큐에 탱크를 설치해 연료를 공급할 수 있다.', 'It can be installed as the fuel tank of a propane barbecue.'),
    ('supply_furnace_fuel', 'fuel_handling', '기존 화로에 연료를 보충하는 데 쓸 수 있다.', 'It can supply fuel to an existing furnace.'),
    ('use_furnace_bellows', 'metalworking', '화로의 풀무 동작에 쓸 수 있다.', 'It can be used in the furnace bellows action.'),
    ('supply_drum_logs', 'charcoal_preparation', '금속 드럼에 통나무를 넣는 데 쓸 수 있다.', 'It can be supplied as logs to a metal drum.'),
    ('request_corpse_burning', 'fire_starting', '시신에 불을 붙이는 동작에 쓸 수 있다.', 'It can participate in the corpse-burning action.'),
):
    FUNCTIONS[_name] = (_context, _ko, _en)

for _predicate in (PUMP_CONTAINER, VEHICLE_CONTAINER, HEARTH_FUEL, HEARTH_TINDER, HEARTH_PETROL,
    INDUSTRIAL_PETROL, INDUSTRIAL_TINDER, HEAT_FRICTION, PROPANE_BARBECUE, FURNACE_FUEL, BELLOWS_USE, DRUM_LOGS, CORPSE_IGNITION):
    QUALIFIERS[_predicate] = ('대상·재료·접근 조건과 해당 동작의 중단·소모 규칙을 따른다. 실제 결과는 실행 상태에 달려 있다.', _predicate)

HEAT_PATHS = {
    PUMP_CONTAINER: (WORLD_MENU, TAKE_FUEL),
    VEHICLE_CONTAINER: (VEHICLE_USE_MENU, VEHICLE_MENU, VEHICLE_COMMANDS, *VEHICLE_FUEL_ACTIONS),
    GENERATOR_REFUEL: (WORLD_MENU, OBJECT_COMMANDS, *GENERATOR_ACTIONS),
    PROPANE_BARBECUE: (BBQ_MENU, OBJECT_COMMANDS, *PROPANE_ACTIONS),
    FURNACE_FUEL: (BLACKSMITH_MENU, INDUSTRIAL_ACTIONS[1]),
    BELLOWS_USE: (BLACKSMITH_MENU, INDUSTRIAL_ACTIONS[0]),
    DRUM_LOGS: (BLACKSMITH_MENU, *DRUM_SOURCES, *INDUSTRIAL_ACTIONS[-4:]),
    CORPSE_IGNITION: (WORLD_MENU, BURN_CORPSE),
}

for _predicate, _suffix in ((HEARTH_FUEL, 'AddFuel'), (HEARTH_TINDER, 'LightFromLiterature'), (HEARTH_PETROL, 'LightFromPetrol')):
    HEAT_PATHS[_predicate] = (BBQ_MENU, FIREPLACE_MENU, CAMP_MENU, CAMP_FUEL, OBJECT_COMMANDS,
                            *(p for p in HEAT_ACTIONS if p.endswith(_suffix + '.lua')))

for _predicate, _suffix in ((INDUSTRIAL_PETROL, 'LightFromPetrol'), (INDUSTRIAL_TINDER, 'LightFromLiterature')):
    HEAT_PATHS[_predicate] = (BLACKSMITH_MENU, CAMP_FUEL, *DRUM_SOURCES,
                            *(p for p in INDUSTRIAL_ACTIONS if p.endswith(_suffix + '.lua')))

HEAT_PATHS[HEAT_FRICTION] = (BBQ_MENU, FIREPLACE_MENU, BLACKSMITH_MENU, OBJECT_COMMANDS, *DRUM_SOURCES,
    *(p for p in (*HEAT_ACTIONS, *INDUSTRIAL_ACTIONS) if p.endswith('LightFromKindle.lua')))

EFFECTS['forge_temperature', 'increase'] = ('풀무 동작의 갱신마다 화로 열을 0.3씩 높이는 처리를 한다.', 'Each bellows-action update requests a 0.3 increase in furnace heat.')

CAMP_PETROL_USE = 'Use an unlit fueled campfire, a Petrol-tag/PetrolCan supply with more than one drainable use at menu time, and a StartFire item or lighter/matches. Transfer both and approach; ongoing validity requires the campfire, fuel, unlit state, both inventory items and positive delta in both. Completion uses petrol and igniter once and sends lightFire without adding fuel. The server only lights with positive fuel and no existing fire. Walking/running interrupts. The menu retains its unbound types ignition lookup; native delivery remains separate. Petrol is the ignition supply, not a tinder item or the ignition implement.'

TRAP_ACTIONS = tuple('lua/client/Traps/TimedActions/IS' + n + 'Action.lua' for n in ('RemoveTrap', 'RemoveBait', 'CheckTrap'))

ENGINE_ACTIONS = ('lua/client/Vehicles/TimedActions/ISRepairEngine.lua', 'lua/client/Vehicles/TimedActions/ISTakeEngineParts.lua')

BURNT_VEHICLE = 'lua/client/Vehicles/TimedActions/ISRemoveBurntVehicle.lua'

PLASTER_ACTION = 'lua/client/BuildingObjects/TimedActions/ISPlasterAction.lua'

PAINTING_REFERENCE = 'lua/server/BuildingObjects/PaintingReference.lua'

CURTAIN_ACTIONS = ('lua/client/TimedActions/ISAddSheetAction.lua', 'lua/client/TimedActions/ISRemoveSheetAction.lua', 'lua/client/TimedActions/ISOpenCloseCurtain.lua')

CURTAIN_USE = 'A carried Sheet enables adding a curtain to an eligible window, window frame or transparent nongarage door without curtains. Transfer the recursively selected sheet and walk to the native add-sheet square or eligible adjacent window; the blocked door fallback does not add. Time 50, interrupted by walking/running, rechecks absent curtains and inventory Sheet rather than the selected item or current position. Completion requests object addSheet and marks construction. The server accepts the indexed door/window/thumpable/frame and delegates native addSheet(player). Installed curtain removal takes 50 with object validity and curtain presence, then the server delegates native removeSheet for IsoCurtain or IsoDoor. Opening/closing uses the placed curtain, approach and a time-zero action with unconditional validity, calling native toggleCurtain or ToggleDoor directly. These placed-object controls do not require retaining the original Sheet. Native material consumption, returned item identity and visibility/weather effects are not implemented by these Lua calls.'

COMPOST_ACTIONS = ('lua/client/TimedActions/ISGetCompost.lua', 'lua/client/TimedActions/ISAddCompost.lua')

VEHICLE_TOOL_TEMPLATES = tuple('scripts/vehicles/template_' + n + '.txt' for n in (
    'tire', 'brake', 'suspension', 'battery', 'gastank', 'headlight', 'radio', 'radio_HAM', 'seat', 'windshield', 'window'))

TRAP_CONTROLS = 'Use the registered placed trap through its world menu and approach its square. Bait addition needs an unbaited trap without an animal and top-level uncooked Food with hunger change at most -.05 or Worm, no extra ingredients or Drink menu; no freshness check occurs at entry. Its time-20 action only rechecks the trap object. Completion scales food values by the requested .05 portion, may Use the remainder, and sends the type, age and consumed amount. The server does not repeat bait/animal eligibility and records the baiting player as owner. Bait removal time 20 rechecks object and bait, sends removeBait, then may create a returned portion using the client cached negative amount and adjusted age; the server clears bait without returning it. Trap removal time 40 is offered without an animal but ongoing validity only checks the object; the server returns a newly created trap type, clears bait and removes the object without repeating the animal guard. Capture retrieval time 40 requires a current animal; the server creates its randomized-size item, scales hunger/weight/nutrients and gives at least three Trapping XP only to the recorded owner before clearing the animal. These constructors do not explicitly set walking/running interruption. Native object lookup, item creation and non-atomic client/server delivery remain separate.'

TRAP_LIFECYCLE = 'The placement callback captures the player name, Trapping level and zone and sets the trap undestroyed. Hourly checks skip catches on loaded squares and clear bait/animals when the adjacent hoppable/window check fails. Unloaded undestroyed traps need accepted fresh bait and time/zone matches, pass trap-plus-bait-plus-skill and zone-plus-skill rolls, then randomly select an eligible animal. Capturing clears bait. When no animal remains, bait can be lost on a one-in-(strength+10) roll, and an unloaded trap can be marked destroyed on separate one-in-40 and one-in-strength rolls. Loaded destruction creates the exact registered debris, with returned Twine set to one use. Ten-minute sound processing for a captured animal can request radius-40 sound on a one-in-four roll, plus trap/animal-specific sound. Native randomness, freshness, streaming, sound and delivery remain separate; no guaranteed capture or recovery is inferred.'

ROD_LINE_BREAK = 'For a named fish, the break threshold is 8, 12 or 22 by small/medium/big size minus Fishing level, minus two when the exact rod type does not contain TwineLine, floored at zero, then plus three only for exact CraftedFishingRod. A random 0..99 value at or below the threshold breaks the line, so threshold zero is not immunity. Crafted rod forms return WoodenStick; modern rod forms return FishingRodBreak. The old rod and its lure are removed, hands cleared and fishing force-stopped. A fish is not created on this branch. Native replacement creation and removal are non-atomic; crafted twine rods do not receive the exact CraftedFishingRod-only plus-three adjustment.'

FISHING_EXECUTION = 'The water menu selects an unbroken FishingRod/FishingSpear tag with a native FishingLure or the spear classifier. The UI searches water within four horizontal tiles for rods or one for spears at player Z at most one, equips by type and starts within distance ten. Ongoing checks keep the same rod and lure hands and reject a different final queued action, not continued water/rod condition. Walking/running stops. Action time is 700 plus random 0..299 minus five per Fishing level for plastic bait, 500 plus random minus skill for living bait, or 300 plus random minus skill for spears. Low Fishing level updates boredom through the configured global value. Zone stock can refresh after timestamp difference 20000, and a successful attraction decrements stock even when line break prevents delivery. Dawn/dusk, winter, skill, abundance and plastic status alter attraction. The fish/trash selector recursively retries unmatched lure rows with no retry bound. Size-based XP is given before line break/item delivery; fish size determines native-created item nutrition/weight. A selected bag is used only if it has capacity, otherwise player inventory. The action can queue another cast while a lure remains. Native registries, classification, random selection, stock and delivery are not guaranteed by the nominal rod/lure declaration.'

ENGINE_REPAIR = 'The Engine mechanics menu requires key/access permission, condition below 100, EngineParts in inventory, Mechanics at least the script engine-repair level and a Wrench. The caller leaves the vehicle, selects a positive-condition Base.Wrench from mechanics containers, transfers it, paths to the engine area and opens/closes an installed hood as needed; it does not explicitly equip the wrench. The 300-time action returns true from ongoing validity and does not explicitly set walking/running interruption. Completion sends current part count and skill excess. The server adds min(1+skillExcess/2,5) condition per requested part until 100, requests removal of that many Base.EngineParts and optional XP equal to parts used, and synchronizes condition. Client mechanics history controls repeat XP. It does not recheck inventory, wrench, skill or access on the server. Native delivery, actual engine performance and non-atomic part consumption remain separate.'

ENGINE_SALVAGE = 'With Engine condition above ten, required Mechanics level, Wrench and key/access, leave the vehicle, transfer the positive-condition wrench, path to the engine and open/close the hood as needed for time 300. The action has unconditional ongoing validity and no explicit walking/running interruption. Server salvage chooses a random condition cost between one-third and all of max(20-skillExcess,5), returns floor(currentCondition/cost) EngineParts and sets engine condition zero. Client XP instead uses the nonrandom denominator and a separate mechanics-history key. Inventory EngineParts are an output, not an input to this action; wrench use is not consumption. Native random, condition and delivery remain separate.'

VEHICLE_TOOL_USE = 'The exact template lists the carried tool with count one and keep=true for installation/removal. Jack is not explicitly equipped; LugWrench and Screwdriver are primary-hand tools. Required items are selected by positive condition from mechanics containers, transferred and equipped as declared, then the caller exits and paths to the work area. Default tests require the appropriate empty/installed slot, profession/recipe/trait and key/access/prerequisite parts; skill shortfall changes success/damage rather than gating entry, and the item-count test body is empty. Ongoing actions delegate canInstallPart/canUninstallPart, without an explicit position or held-tool recheck. Time is the selected install-table time minus Mechanics times time/15; even uninstall caller/server use install-table time/skills. Success changes the installed part and runs its callback; failures can damage or return it, with the asymmetric uninstall failure roll retained. The listed tools are kept. Native compatibility, stats, command delivery and resulting vehicle operation remain separate.'

WEAPON_ATTACHMENT_TOOL = 'An unbroken recursive Screwdriver tag enables attachment controls on a HandWeapon, including a broken weapon. Addition needs an accepted MountOn FullType and empty supported part slot; the caller transfers weapon/part and equips part secondary and screwdriver primary for time 50 or instant one. Ongoing addition checks a top-level unbroken screwdriver tag, the empty slot and part possession, not weapon possession or repeated MountOn. Removal time 50 checks the top-level unbroken screwdriver, weapon possession and exact installed part. Walking/running stops. Addition calls attachWeaponPart, removes the part and clears secondary; removal detaches, returns the same part and resets hand models. Neither action consumes the screwdriver; native compatibility and stat effects remain separate.'

PLASTER_USE = 'The paint menu requires Woodwork four and a recursive BucketPlasterFull, with a plasterable thumpable unless using the joypad; cheat bypasses this. The active callback always selects the plaster cursor, whose object list accepts plasterable IsoThumpable and whose shared wall-aware walk precedes creation. skipWalk is not the parent skipWalk2 flag. Transfer a plaster bucket and queue time 100, or cheat one. Ongoing validity checks only a BucketPlasterFull in inventory, not the selected bucket, skill, charge or target. Completion indexes Painting by wallType/orientation without a missing-entry guard, requests a sprite change and paintable=true, then uses the selected bucket once. The server checks the indexed object is an IsoThumpable but does not repeat plasterability/skill. Walking/running stops. Native sprite/state/delivery remain separate; this does not paint a chosen color or strengthen every wooden structure.'

COMPOST_TRANSFER = 'At a selected IsoCompost, get-compost entry uses rounded compost amount and requires at least one use, plus a nonfull CompostBag or empty EmptySandbag; adding requires space for a use and a CompostBag. Approach, transfer and equip primary. Ten compost units correspond to a full bag, with uses derived from the CompostBag script UseDelta. Get time 100 checks compost amount and item possession, not current capacity; completion fills an existing bag by available uses or replaces the empty sack with Base.CompostBag, equips primary and subtracts the corresponding compost. Add time 150 checks room, possession and positive integer uses; completion consumes as many uses as fit and adds compost. Both update sprite and client-sync, stop on walking/running and use instant time one. Native compost state and replacement/delivery are separate; this does not establish compost production from food.'

BURNT_VEHICLE_USE = 'The vehicle menu recognizes script names containing Burnt or Smashed and requires a recursive WeldingMask tag/type and a Base.BlowTorch with at least ten uses. Approach, equip a torch tag/type with ten uses and wear the selected mask. Time is 800 minus twenty per MetalWelding level or instant ten. Ongoing validity only checks a primary eligible torch and nonremoved vehicle, not mask, distance or script name; the constructor sets no walking/running flags. Completion makes skill-dependent random world drops of bars, pipes, sheets, small sheets and scrap over max(5,skill) iterations, uses the captured torch ten times, awards five plus two XP per successful drop, and requests vehicle removal. The server removes the identified vehicle without repeating those eligibility checks. Native random drops and removal are non-atomic; guaranteed salvage or protection is not inferred.'

for _name, _context, _ko, _en in (
    ('light_campfire_with_petrol', 'campfire_lighting', '휘발유를 쓰는 모닥불 점화에 쓸 수 있다.', 'It can participate in petrol ignition of a campfire.'),
    ('manage_animal_trap', 'trapping', '설치한 덫에 미끼를 넣거나 미끼·포획물·덫을 회수할 수 있다.', 'Its placed trap supports baiting and retrieval of bait, a catch or the trap.'),
    ('repair_vehicle_engine', 'vehicle_maintenance', '차량 엔진 수리에 쓸 수 있다.', 'It can be used in vehicle engine repair.'),
    ('salvage_vehicle_engine', 'vehicle_maintenance', '차량 엔진에서 예비 부품을 회수하는 데 쓸 수 있다.', 'It can be used to salvage spare parts from a vehicle engine.'),
    ('service_vehicle_parts', 'vehicle_maintenance', '지원하는 차량 부품의 설치·분리 도구로 쓸 수 있다.', 'It can serve as a tool for supported vehicle part installation and removal.'),
    ('manage_weapon_attachments', 'weapon_modification', '무기 부착물의 설치·분리 도구로 쓸 수 있다.', 'It can serve as a tool for attaching and removing weapon parts.'),
    ('plaster_supported_structure', 'surface_preparation', '지원하는 구조물에 석고를 바르는 데 쓸 수 있다.', 'It can be used to plaster an eligible structure.'),
    ('transfer_compost', 'compost_handling', '퇴비통과 포대 사이에서 퇴비를 옮길 수 있다.', 'It can transfer compost between a compost bin and a bag.'),
    ('install_sheet_curtain', 'curtain_handling', '대응하는 창문·문에 커튼을 설치하는 데 쓸 수 있다.', 'It can supply a curtain for an eligible window or door.'),
    ('control_sheet_curtain', 'curtain_handling', '설치한 커튼을 열고 닫거나 떼어낼 수 있다.', 'Its installed curtain can be opened, closed or removed.'),
    ('receive_compost', 'compost_handling', '퇴비통의 퇴비를 담는 데 쓸 수 있다.', 'It can receive compost from a compost bin.'),
    ('dismantle_burnt_vehicle', 'vehicle_maintenance', '불타거나 파손된 차량의 분해에 쓸 수 있다.', 'It can be used to dismantle a burnt or smashed vehicle.'),
):
    FUNCTIONS[_name] = (_context, _ko, _en)

for _predicate in (CAMP_PETROL_USE, TRAP_CONTROLS, TRAP_LIFECYCLE, ROD_LINE_BREAK, FISHING_EXECUTION,
    ENGINE_REPAIR, ENGINE_SALVAGE, VEHICLE_TOOL_USE, WEAPON_ATTACHMENT_TOOL, PLASTER_USE, COMPOST_TRANSFER, BURNT_VEHICLE_USE, CURTAIN_USE):
    QUALIFIERS[_predicate] = ('해당 대상·도구·재료 조건을 충족해야 하며 실제 결과는 실행 상태에 달려 있다.', _predicate)

EFFECTS['fishing_rod_form', 'replace_on_line_break'] = ('낚싯줄이 끊어지면 낚싯대가 제거되고 종류에 맞는 잔여 물품을 반환하도록 한다.', 'A broken line removes the rod and requests its type-specific remnant.')

CONTROL_SOURCES = (*TRAP_ACTIONS, *ENGINE_ACTIONS, BURNT_VEHICLE, PLASTER_ACTION, PAINTING_REFERENCE,
                   *COMPOST_ACTIONS, *CURTAIN_ACTIONS, *VEHICLE_TOOL_TEMPLATES)

EQUIPPED_RAIN_USE = 'The item declares equipped rain protection and is held in either hand. Outdoor foraging reduces the precipitation contribution when the held item reports rain protection; fog, snow and cloud effects remain separate.'

MEDICINE_PURPOSES = {
    'Tooltip_Painkillers': ('Reduce feelings of pain', 'use_pain_relief_medicine',
        '통증 완화에 쓰는 약이다', 'It is medicine for pain relief'),
    'Tooltip_PillsAntidepressant': ('Reduces unhappiness over sustained periods', 'use_unhappiness_medicine',
        '시간을 두고 불행을 줄이는 데 쓰는 약이다', 'It is medicine for reducing unhappiness over time'),
    'Tooltip_PillsBetablocker': ('Reduces panic', 'use_panic_relief_medicine',
        '공포를 줄이는 데 쓰는 약이다', 'It is medicine for reducing panic'),
    'Tooltip_PillsSleeping': ('Helps in getting to sleep. Useful when anxious or in pain.', 'use_sleep_aid_medicine',
        '불안하거나 아플 때 잠드는 데 도움을 주는 약이다', 'It is medicine that helps with getting to sleep when anxious or in pain'),
    'Tooltip_Vitamins': ('Provides a burst of energy when taken. Reduces fatigue.', 'use_fatigue_relief_medicine',
        '피로를 줄이는 데 쓰는 약이다', 'It is medicine for reducing fatigue'),
    'Tooltip_Antibiotics': ('Fights wound infections. Cannot prevent zombification.', 'use_wound_infection_medicine',
        '상처 감염에 대응하는 약이다. 좀비화는 막지 못한다', 'It is medicine for fighting wound infections. It cannot prevent zombification'),
}

FUNCTIONS.update({function: ('medicine', ko, en) for _, function, ko, en in MEDICINE_PURPOSES.values()})

GENERATOR_EXTERIOR_USE = 'The sandbox option allowing generators to work on exterior tiles must be enabled for the represented exterior fuel-pump power use. This admits the authored exterior/pump purpose only, not a supply radius or unconditional power to every device.'

FUNCTIONS['power_exterior_fuel_pumps'] = ('power supply', '가동해 야외 주유기에 전원을 공급하는 데 쓸 수 있다', 'It can be operated to supply power to exterior fuel pumps')

LEARNING_PURPOSES = {
    'Cooking': ('요리법', 'cooking recipes'),
    'Farming': ('작물 치료제를 만드는 방법', 'how to make crop treatments'),
    'Fishing': ('낚시 장비 관련 제작법', 'fishing-equipment recipes'),
    'Trapper': ('덫을 만드는 방법', 'how to make traps'),
    'Welding': ('금속 가공 방법', 'metalworking techniques'),
    'MetalConstruction': ('금속 구조물을 만드는 방법', 'how to build metal structures'),
    'Smithing': ('금속을 단조해 물품을 만드는 방법', 'how to forge metal items'),
    'Electrical': ('전자 장치 관련 제작법', 'electronic-device recipes'),
    'Engineer': ('장치를 만드는 방법', 'how to make devices'),
    'Mechanics': ('차량 정비 지식', 'vehicle maintenance'),
    'Herbalist': ('야생 열매와 버섯의 독성을 식별하는 방법', 'how to identify poisonous wild berries and mushrooms'),
    'Generator': ('발전기를 연결하고 사용하는 방법', 'how to connect and use generators'),
}

for _topic, (_ko, _en) in LEARNING_PURPOSES.items():
    FUNCTIONS['learn_literature_' + _topic.lower()] = ('literature learning',
        '읽어서 ' + _ko + '을 배울 수 있다', 'It can be read to learn ' + _en)

for _name, _ko, _en in (
    ('boredom', '일부 내용은 지루함을 덜어주는 데 쓸 수 있다', 'Some recordings can help relieve boredom'),
    ('skills', '일부 내용은 기술을 익히는 데 쓸 수 있다', 'Some recordings can help develop skills'),
    ('recipes', '일부 내용은 제작법을 배우는 데 쓸 수 있다', 'Some recordings can teach recipes'),
    ('stress', '일부 내용은 스트레스를 줄 수 있다', 'Some recordings can cause stress'),
    ('panic', '일부 내용은 공포를 느끼게 할 수 있다', 'Some recordings can cause panic')):
    FUNCTIONS['recorded_content_' + _name] = ('recorded content', _ko, _en)

FUNCTIONS['supply_vehicle_electrical_power'] = ('차량의 시동과 전기 장치에 전력을 공급할 수 있다', 'It can supply power for starting a vehicle and operating its electrical equipment')

FUNCTIONS['provide_vehicle_headlight'] = ('호환 차량의 전조등에 달아 빛을 낼 수 있다', 'It can provide light in a compatible vehicle headlight')

FUNCTIONS['read_for_morale'] = ('leisure reading', '기분 전환을 위한 읽을거리로 쓸 수 있다', 'It can be read for a change of mood')

ATTACHMENT_PURPOSES = {
    'Tooltip_AmmoStrap': ('Reduces firearm reload time.', 'reload',
        (('ReloadTimeModifier', -1),),
        '호환 총기의 장전 시간을 줄이는 부착물로 쓸 수 있다',
        'It can serve as an attachment to reduce reload time on a compatible firearm'),
    'Tooltip_Scope': ("Weapon attachment. Increases firearm's maximum range.<br>Decreases short-range accuracy.", 'scope',
        (('MaxRangeModifier', 1), ('MinRangeModifier', 1)),
        '호환 총기의 최대 사거리를 늘리는 부착물로 쓸 수 있다. 근거리 정확도는 낮아진다',
        'It can extend the maximum range of a compatible firearm, at the cost of short-range accuracy'),
    'Tooltip_IronSight': ("Weapon attachment. Increases firearm's maximum range.", 'range',
        (('MaxRangeModifier', 1),),
        '호환 총기의 최대 사거리를 늘리는 부착물로 쓸 수 있다',
        'It can serve as an attachment to extend the maximum range of a compatible firearm'),
    'Tooltip_Sling': ('Weapon attachment. Reduces firearm carry-encumbrance.', 'carry',
        (('WeightModifier', -1),),
        '호환 총기를 휴대할 때 무게 부담을 줄이는 부착물로 쓸 수 있다',
        'It can reduce the carrying burden of a compatible firearm'),
    'Tooltip_FiberglassStock': ('Weapon attachment. Decreases firearm encumbrance and increases accuracy.', 'stock',
        (('WeightModifier', -1), ('HitChanceModifier', 1)),
        '호환 총기의 휴대 무게 부담을 줄이고 정확도를 높이는 부착물로 쓸 수 있다',
        'It can reduce carrying burden and improve accuracy on a compatible firearm'),
    'Tooltip_RecoilPad': ('Weapon attachment. Reduces firearm recoil and delay to next shot.', 'recoil',
        (('RecoilDelayModifier', -1),),
        '호환 총기의 반동과 다음 발사까지의 지연을 줄이는 부착물로 쓸 수 있다',
        'It can reduce recoil and delay before the next shot on a compatible firearm'),
    'Tooltip_Laser': ('Weapon attachment. Increases firearm accuracy.', 'accuracy',
        (('HitChanceModifier', 1),),
        '호환 총기의 정확도를 높이는 부착물로 쓸 수 있다',
        'It can serve as an attachment to improve accuracy on a compatible firearm'),
    'Tooltip_RedDot': ("Weapon attachment. Increases firearm's aiming speed.", 'aiming',
        (('AimingTimeModifier', 1),),
        '호환 총기의 조준 속도를 높이는 부착물로 쓸 수 있다',
        'It can serve as an attachment to increase aiming speed on a compatible firearm'),
    'Tooltip_ChokeTubeFull': ('Shotgun attachment. Provides a narrower blast and increased damage.', 'narrow_spread',
        (('AngleModifier', 1), ('DamageModifier', 1)),
        '호환 산탄총의 산탄 퍼짐을 좁히고 피해를 높이는 부착물로 쓸 수 있다',
        'It can narrow pellet spread and increase damage on a compatible shotgun'),
    'Tooltip_ChokeTubeImproved': ('Shotgun attachment. Provides a wider blast but decreased damage.', 'wide_spread',
        (('AngleModifier', -1), ('DamageModifier', -1)),
        '호환 산탄총의 산탄 퍼짐을 넓히는 부착물로 쓸 수 있다. 피해는 줄어든다',
        'It can widen pellet spread on a compatible shotgun, at the cost of damage'),
}

for _expected, _name, _checks, _ko, _en in ATTACHMENT_PURPOSES.values():
    FUNCTIONS['attachment_purpose_' + _name] = ('weapon attachment purpose', _ko, _en)

PLACED_PURPOSES = {
    'hearth': ('설치하고 연료를 넣어 난방이나 조리에 쓸 수 있다', 'Once installed and fueled, it can provide heat or cook food'),
    'barbecue': ('설치하고 맞는 연료를 넣어 음식을 조리할 수 있다', 'Once installed and supplied with suitable fuel, it can cook food'),
    'mannequin': ('배치해 의류를 입혀둘 수 있다', 'It can be placed and dressed in clothing'),
    'salvage_welding': ('설치된 상태에서 용접용 마스크와 프로판 토치를 써서 분해해 재료를 회수할 수 있다', 'Once placed, it can be dismantled with a welding mask and propane torch to recover materials'),
    'salvage_wood': ('설치된 상태에서 망치와 톱을 써서 분해해 재료를 회수할 수 있다', 'Once placed, it can be dismantled with a hammer and saw to recover materials'),
    'salvage_screwdriver': ('설치된 상태에서 드라이버로 분해해 재료를 회수할 수 있다', 'Once placed, it can be dismantled with a screwdriver to recover materials'),
    'salvage_hammer': ('설치된 상태에서 망치로 분해해 재료를 회수할 수 있다', 'Once placed, it can be dismantled with a hammer to recover materials'),
    'sleep': ('놓아서 잠을 자거나 쉬는 데 쓸 수 있다', 'When set down, it provides a place to sleep or rest'),
    'storage': ('수납용으로 놓아 사용할 수 있다', 'It can serve as storage once set down'),
    'cold_storage': ('설치하고 전원을 공급하면 음식 등을 차갑게 보관할 수 있다', 'Once installed and powered, it can keep food and other contents cold'),
    'surface': ('물건을 올려두는 용도로 놓아 쓸 수 있다', 'Its surface can hold items when it is set down'),
    'water_piped': ('설치하고 급수를 연결해 물을 받거나 씻는 데 쓸 수 있다', 'Once installed and connected to a water supply, it can provide water for filling containers or washing'),
    'water_storage': ('배치해 담긴 물을 받거나 마시는 데 쓸 수 있다', 'Once placed, it can dispense its stored water for filling containers or drinking'),
    'light': ('설치하고 전원을 공급해 조명으로 쓸 수 있다', 'Once installed and powered, it can provide light'),
    'mirror': ('설치해 화장할 때 필요한 거울로 쓸 수 있다', 'Once installed, it can serve as the mirror needed for applying makeup'),
    'cooking': ('설치하고 전원을 공급해 음식을 데우거나 조리하는 데 쓸 수 있다', 'Once installed and powered, it can heat or cook food'),
    'washing': ('설치하고 전기와 물을 공급해 의류를 세탁할 수 있다', 'Once installed and supplied with electricity and water, it can wash clothing'),
    'drying': ('설치하고 전원을 공급해 젖은 의류를 말릴 수 있다', 'Once installed and powered, it can dry wet clothing'),
}

FUNCTIONS['attachment_purpose_movement_aim'] = ('weapon attachment purpose',
    '호환 총기에 장착해 이동으로 인한 명중률 감소를 줄일 수 있다',
    'On a compatible firearm, it can reduce the movement-related hit-chance penalty')

for _name, (_ko, _en) in PLACED_PURPOSES.items():
    FUNCTIONS['placed_purpose_' + _name] = ('placed object purpose', _ko, _en)

FUNCTIONS['emit_attracting_noise'] = ('noise', '소음을 내 좀비의 주의를 끄는 데 쓸 수 있다', 'It can produce noise to attract zombies')

FUNCTIONS['supply_nearby_electricity'] = ('power supply', '가동해 주변 전기 설비에 전원을 공급할 수 있다', 'It can be operated to power nearby electrical equipment')

FUNCTIONS['device_explosion_damage'] = ('explosion', '폭발로 주변에 피해를 줄 수 있다', 'It can cause blast damage nearby')

FUNCTIONS['device_start_fire'] = ('fire', '주변에 불을 붙이는 데 쓸 수 있다', 'It can be used to start fires nearby')

FUNCTIONS['device_smoke_distraction'] = ('smoke', '연막을 퍼뜨려 좀비가 쫓던 대상을 놓치게 할 수 있다', 'It can release smoke that makes zombies lose their current target')

from .purpose_evidence import REVIEW_FUNCTIONS

FUNCTIONS.update(REVIEW_FUNCTIONS)

from .purpose_participant_relations import FUNCTIONS as PARTICIPANT_FUNCTIONS

FUNCTIONS.update(PARTICIPANT_FUNCTIONS)
