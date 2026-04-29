# Scope-outside Top 10 Clusters (static-only) — Gate-0 v2 후

- total_fulltypes: 2281
- in_pipeline_fulltypes: 1462
- scope_outside_fulltypes: 819
- cluster_count: 67
- 이전 대비 변화: scope outside 1004 → 819 (185개 pipeline 진입)

## Cluster 1
- count: 136
- signature: Type=Moveable, DisplayCategory=Furniture
- representatives (10):
  - Base.Mattress
  - Base.Mov_AirConditioner
  - Base.Mov_AntiqueStove
  - Base.Mov_ArcadeMachine1
  - Base.Mov_ArcadeMachine2
  - Base.Mov_BeachChair
  - Base.Mov_BinRound
  - Base.Mov_Birdbath
  - Base.Mov_BlueComfyChair
  - Base.Mov_BluePlasticChair
- exclusion_feasibility: ['unknown']

## Cluster 2
- count: 88
- signature: Type=Normal, DisplayCategory=VehicleMaintenance, HasKeys=['MechanicsItem', 'VehicleType']
- representatives (10):
  - Base.BigGasTank1
  - Base.BigGasTank2
  - Base.BigGasTank3
  - Base.BigTrunk1
  - Base.BigTrunk2
  - Base.BigTrunk3
  - Base.EngineDoor1
  - Base.EngineDoor2
  - Base.EngineDoor3
  - Base.FrontCarDoor1
- exclusion_feasibility: ['unknown']

## Cluster 3
- count: 73
- signature: Type=Normal, DisplayCategory=Junk
- representatives (10):
  - Base.BackgammonBoard
  - Base.BeerCanEmpty
  - Base.Bell
  - Base.Belt
  - Base.BobPic
  - Base.Bricktoys
  - Base.Button
  - Base.Camera
  - Base.CameraDisposable
  - Base.CameraExpensive
- exclusion_feasibility: ['unknown']

## Cluster 4
- count: 42
- signature: Type=Container, DisplayCategory=Container
- representatives (10):
  - Base.Briefcase
  - Base.Cooler
  - Base.EmptySandbag
  - Base.FirstAidKit
  - Base.Flightcase
  - Base.Garbagebag
  - Base.GroceryBag1
  - Base.GroceryBag2
  - Base.GroceryBag3
  - Base.GroceryBag4
- exclusion_feasibility: ['unknown']

## Cluster 5
- count: 32
- signature: Type=Normal, DisplayCategory=Electronics
- representatives (10):
  - Base.Amplifier
  - Base.CordlessPhone
  - Base.Earbuds
  - Base.ElectronicsScrap
  - Base.Generator
  - Base.Headphones
  - Base.HomeAlarm
  - Base.LightBulb
  - Base.LightBulbBlue
  - Base.LightBulbCyan
- exclusion_feasibility: ['unknown']

## Cluster 6
- count: 31
- signature: Type=Weapon, DisplayCategory=Explosives
- representatives (10):
  - Base.Aerosolbomb
  - Base.AerosolbombRemote
  - Base.AerosolbombSensorV1
  - Base.AerosolbombSensorV2
  - Base.AerosolbombSensorV3
  - Base.AerosolbombTriggered
  - Base.FlameTrap
  - Base.FlameTrapRemote
  - Base.FlameTrapSensorV1
  - Base.FlameTrapSensorV2
- exclusion_feasibility: ['unknown']

## Cluster 7
- count: 26
- signature: Type=Container, DisplayCategory=Bag
- representatives (10):
  - Base.Bag_ALICEpack
  - Base.Bag_ALICEpack_Army
  - Base.Bag_BigHikingBag
  - Base.Bag_BowlingBallBag
  - Base.Bag_DoctorBag
  - Base.Bag_DuffelBag
  - Base.Bag_DuffelBagTINT
  - Base.Bag_FoodCanned
  - Base.Bag_FoodSnacks
  - Base.Bag_GolfBag
- exclusion_feasibility: ['unknown']

## Cluster 8
- count: 23
- signature: Type=Weapon, DisplayCategory=Weapon
- representatives (10):
  - Base.AssaultRifle
  - Base.AssaultRifle2
  - Base.BareHands
  - Base.Chainsaw
  - Base.DoubleBarrelShotgun
  - Base.DoubleBarrelShotgunSawnoff
  - Base.HuntingKnife
  - Base.HuntingRifle
  - Base.Katana
  - Base.LeadPipe
- exclusion_feasibility: ['unknown']

## Cluster 9
- count: 22
- signature: Type=Weapon, DisplayCategory=WeaponCrafted
- representatives (10):
  - Base.BaseballBatNails
  - Base.FlintKnife
  - Base.PickAxeHandleSpiked
  - Base.PlankNail
  - Base.SmashedBottle
  - Base.SpearBreadKnife
  - Base.SpearButterKnife
  - Base.SpearCrafted
  - Base.SpearFork
  - Base.SpearHandFork
- exclusion_feasibility: ['unknown']

## Cluster 10
- count: 20
- signature: Type=Weapon, DisplayCategory=ToolWeapon
- representatives (10):
  - Base.Axe
  - Base.AxeStone
  - Base.BallPeenHammer
  - Base.ClubHammer
  - Base.Crowbar
  - Base.Hammer
  - Base.HammerStone
  - Base.HandAxe
  - Base.HandFork
  - Base.HandScythe
- exclusion_feasibility: ['unknown']

## Summary: 이전 대비 변화

| 이전 Cluster | 변화 |
|---|---|
| Cluster 4 (Material, 43) | Type=Normal 48개 pipeline 진입 (input_material NO) |
| Cluster 6 (Food, 39) | 479개 전체 pipeline 진입 (consumption NO) |
| Cluster 10 (Ammo, 20) | 27개 전체 pipeline 진입 (input_material NO) |

## Scope-outside DisplayCategory 분포

| DisplayCategory | Count |
|---|---|
| Furniture | 136 |
| VehicleMaintenance | 93 |
| Junk | 79 |
| Container | 42 |
| Household | 36 |
| Electronics | 34 |
| Explosives | 31 |
| Bag | 28 |
| FirstAid | 26 |
| Gardening | 26 |
| Cooking | 24 |
| Weapon | 23 |
| WeaponCrafted | 22 |
| Sports | 21 |
| Accessory | 21 |
| ToolWeapon | 20 |
| Appearance | 16 |
| Communications | 16 |
| Cartography | 15 |
| Paint | 15 |
| Instrument | 14 |
| Material | 14 |
| Tool | 11 |
| Fishing | 10 |
| Security | 9 |
| LightSource | 6 |
| Trapping | 6 |
| Entertainment | 5 |
| Camping | 5 |
| Hidden | 4 |
| Corpse | 2 |
| Raccoon | 2 |
| Badger | 1 |
| Bunny | 1 |
| Fox | 1 |
| Squirrel | 1 |
| Beaver | 1 |
| Mole | 1 |
| Hedgehog | 1 |