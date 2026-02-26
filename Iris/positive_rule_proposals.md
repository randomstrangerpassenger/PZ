# positive_rule_proposals.md (from scope-outside clusters)

규칙은 extract / prove / exclusions로 분리. prove는 가능한 경우만 true, 불명확은 unknown→REVIEW.

## outside.cluster01.moveable_furniture.candidate_only
- source_type: rc.worldobject.moveable
- anchor: kind=UNKNOWN, ref=TBD, span=TBD
- extract.matchers:
  - Type: ['Moveable']
  - DisplayCategory: ['Furniture']
- prove: {'A': 'unknown', 'B': 'unknown', 'C': 'unknown'}
- exclusions: {'Recipe': 'unknown', 'Consumption': 'unknown', 'Equip': 'unknown', 'Passive': 'unknown', 'Auto': 'unknown', 'property_based': 'unknown'}
- expected_impact: {'candidate_count_estimate': 136, 'pass_possible': 'unknown', 'review_likely': 'high', 'representatives': ['Base.Mattress', 'Base.Mov_AirConditioner', 'Base.Mov_AntiqueStove', 'Base.Mov_ArcadeMachine1', 'Base.Mov_ArcadeMachine2', 'Base.Mov_BeachChair', 'Base.Mov_BinRound', 'Base.Mov_Birdbath', 'Base.Mov_BlueComfyChair', 'Base.Mov_BluePlasticChair']}

## outside.cluster02.normal_junk.candidate_only
- source_type: rc.none
- anchor: kind=UNKNOWN, ref=TBD, span=TBD
- extract.matchers:
  - Type: ['Normal']
  - DisplayCategory: ['Junk']
- prove: {'A': 'unknown', 'B': 'unknown', 'C': 'unknown'}
- exclusions: {'Recipe': 'unknown', 'Consumption': 'unknown', 'Equip': 'unknown', 'Passive': 'unknown', 'Auto': 'unknown', 'property_based': 'unknown'}
- expected_impact: {'candidate_count_estimate': 73, 'pass_possible': 'unknown', 'review_likely': 'high', 'representatives': ['Base.BackgammonBoard', 'Base.BeerCanEmpty', 'Base.Bell', 'Base.Belt', 'Base.BobPic', 'Base.Bricktoys', 'Base.Button', 'Base.Camera', 'Base.CameraDisposable', 'Base.CameraExpensive']}

## outside.cluster03.vehiclemaintenance_parts.candidate_only
- source_type: rc.vehicle.maintenance
- anchor: kind=UNKNOWN, ref=TBD, span=TBD
- extract.matchers:
  - DisplayCategory: ['VehicleMaintenance']
  - HasKeys_all_of: ['MechanicsItem', 'VehicleType']
- prove: {'A': 'unknown', 'B': 'unknown', 'C': 'unknown'}
- exclusions: {'Recipe': 'unknown', 'Consumption': 'unknown', 'Equip': 'unknown', 'Passive': 'unknown', 'Auto': 'unknown', 'property_based': 'unknown'}
- expected_impact: {'candidate_count_estimate': 55, 'pass_possible': 'unknown', 'review_likely': 'high', 'representatives': ['Base.BigGasTank1', 'Base.BigGasTank2', 'Base.BigGasTank3', 'Base.BigTrunk1', 'Base.BigTrunk2', 'Base.BigTrunk3', 'Base.EngineDoor1', 'Base.EngineDoor2', 'Base.EngineDoor3', 'Base.FrontCarDoor1']}

## outside.cluster04.material.input_material_exclusion
- source_type: rc.exclusion.input_material
- anchor: kind=STATIC, ref=items_itemscript.json, span=DisplayCategory=Material
- extract.matchers:
  - DisplayCategory: ['Material']
- prove: {'A': 'unknown', 'B': 'unknown', 'C': 'unknown'}
- exclusions: {'input_material': True, 'Decision': 'NO', 'Reason': 'DisplayCategory=Material (static)'}
- expected_impact: {'candidate_count_estimate': 43, 'pass_possible': 'no', 'review_likely': 'low', 'representatives': ['Base.Aluminum', 'Base.BarbedWire', 'Base.BoxOfJars', 'Base.ConcretePowder', 'Base.Doorknob', 'Base.Drawer', 'Base.Handle', 'Base.Hinge', 'Base.Log', 'Base.LogStacks2']}

## outside.cluster05.container_container.candidate_only
- source_type: rc.inventory.container
- anchor: kind=UNKNOWN, ref=TBD, span=TBD
- extract.matchers:
  - Type: ['Container']
  - DisplayCategory: ['Container']
- prove: {'A': 'unknown', 'B': 'unknown', 'C': 'unknown'}
- exclusions: {'Recipe': 'unknown', 'Consumption': 'unknown', 'Equip': 'unknown', 'Passive': 'unknown', 'Auto': 'unknown', 'property_based': 'unknown'}
- expected_impact: {'candidate_count_estimate': 41, 'pass_possible': 'unknown', 'review_likely': 'high', 'representatives': ['Base.Briefcase', 'Base.Cooler', 'Base.EmptySandbag', 'Base.Flightcase', 'Base.Garbagebag', 'Base.GroceryBag1', 'Base.GroceryBag2', 'Base.GroceryBag3', 'Base.GroceryBag4', 'Base.GroceryBag5']}

## outside.cluster06.food.consumption_exclusion
- source_type: rc.exclusion.consumption
- anchor: kind=STATIC, ref=items_itemscript.json, span=Type=Food OR DisplayCategory=Food
- extract.matchers:
  - Type: ['Food']
  - DisplayCategory: ['Food']
- prove: {'A': 'unknown', 'B': 'unknown', 'C': 'unknown'}
- exclusions: {'consumption': True, 'Decision': 'NO', 'Reason': 'Type/DisplayCategory indicates consumption domain (static)'}
- expected_impact: {'candidate_count_estimate': 39, 'pass_possible': 'no', 'review_likely': 'low', 'representatives': ['Base.CandyPackage', 'Base.CannedBolognese', 'Base.CannedCarrots2', 'Base.CannedChili', 'Base.CannedCorn', 'Base.CannedCornedBeef', 'Base.CannedFruitBeverage', 'Base.CannedFruitCocktail', 'Base.CannedMilk', 'Base.CannedMushroomSoup']}

## outside.cluster07.normal_electronics.candidate_only
- source_type: rc.inventory.item
- anchor: kind=UNKNOWN, ref=TBD, span=TBD
- extract.matchers:
  - Type: ['Normal']
  - DisplayCategory: ['Electronics']
- prove: {'A': 'unknown', 'B': 'unknown', 'C': 'unknown'}
- exclusions: {'Recipe': 'unknown', 'Consumption': 'unknown', 'Equip': 'unknown', 'Passive': 'unknown', 'Auto': 'unknown', 'property_based': 'unknown'}
- expected_impact: {'candidate_count_estimate': 32, 'pass_possible': 'unknown', 'review_likely': 'high', 'representatives': ['Base.Amplifier', 'Base.CordlessPhone', 'Base.Earbuds', 'Base.ElectronicsScrap', 'Base.Generator', 'Base.Headphones', 'Base.HomeAlarm', 'Base.LightBulb', 'Base.LightBulbBlue', 'Base.LightBulbCyan']}

## outside.cluster08.weapon_explosives.candidate_only
- source_type: rc.weapon.explosive
- anchor: kind=UNKNOWN, ref=TBD, span=TBD
- extract.matchers:
  - Type: ['Weapon']
  - DisplayCategory: ['Explosives']
- prove: {'A': 'unknown', 'B': 'unknown', 'C': 'unknown'}
- exclusions: {'Recipe': 'unknown', 'Consumption': 'unknown', 'Equip': 'unknown', 'Passive': 'unknown', 'Auto': 'unknown', 'property_based': 'unknown'}
- expected_impact: {'candidate_count_estimate': 31, 'pass_possible': 'unknown', 'review_likely': 'high', 'representatives': ['Base.Aerosolbomb', 'Base.AerosolbombRemote', 'Base.AerosolbombSensorV1', 'Base.AerosolbombSensorV2', 'Base.AerosolbombSensorV3', 'Base.AerosolbombTriggered', 'Base.FlameTrap', 'Base.FlameTrapRemote', 'Base.FlameTrapSensorV1', 'Base.FlameTrapSensorV2']}

## outside.cluster09.container_bag.candidate_only
- source_type: rc.inventory.bag
- anchor: kind=UNKNOWN, ref=TBD, span=TBD
- extract.matchers:
  - Type: ['Container']
  - DisplayCategory: ['Bag']
- prove: {'A': 'unknown', 'B': 'unknown', 'C': 'unknown'}
- exclusions: {'Recipe': 'unknown', 'Consumption': 'unknown', 'Equip': 'unknown', 'Passive': 'unknown', 'Auto': 'unknown', 'property_based': 'unknown'}
- expected_impact: {'candidate_count_estimate': 26, 'pass_possible': 'unknown', 'review_likely': 'high', 'representatives': ['Base.Bag_ALICEpack', 'Base.Bag_ALICEpack_Army', 'Base.Bag_BigHikingBag', 'Base.Bag_BowlingBallBag', 'Base.Bag_DoctorBag', 'Base.Bag_DuffelBag', 'Base.Bag_DuffelBagTINT', 'Base.Bag_FoodCanned', 'Base.Bag_FoodSnacks', 'Base.Bag_GolfBag']}

## outside.cluster10.ammo.input_material_exclusion
- source_type: rc.exclusion.input_material
- anchor: kind=STATIC, ref=items_itemscript.json, span=DisplayCategory=Ammo
- extract.matchers:
  - DisplayCategory: ['Ammo']
- prove: {'A': 'unknown', 'B': 'unknown', 'C': 'unknown'}
- exclusions: {'input_material': True, 'Decision': 'NO', 'Reason': 'DisplayCategory=Ammo (static)'}
- expected_impact: {'candidate_count_estimate': 20, 'pass_possible': 'no', 'review_likely': 'low', 'representatives': ['Base.223Box', 'Base.223Bullets', 'Base.223BulletsMold', 'Base.308Box', 'Base.308Bullets', 'Base.308BulletsMold', 'Base.556Box', 'Base.556Bullets', 'Base.9mmBulletsMold', 'Base.Bullets38']}
