"""Question-local source attribution, retaining separate unfinished work.

Route observations are evidence inputs, never the blocker decision. Each rule
states which part of an exact axis/scope those observations answer and which
consumer boundary still owns its residual. Attribution does not mean recovery
is complete; available but unimplemented interpretations stay in remaining_work.
"""
from collections import defaultdict
from copy import deepcopy
import re

from . import semantic_model as model
from . import semantic_results as semantic
from . import recovery_sources as sources


NATIVE_FIELDS = {
    'activity:ingestion': ('Type', 'CantEat', 'CustomContextMenu', 'CustomMenuOption', 'HungerChange', 'ThirstChange',
                           'BoredomChange', 'UnhappyChange', 'StressChange', 'Poison', 'PoisonDetectionLevel',
                           'OnEat', 'RequireInHandOrInventory', 'DangerousUncooked'),
    'activity:reading': ('Type', 'CanBeWrite', 'SkillTrained', 'LvlSkillTrained', 'NumLevelsTrained',
                         'NumberOfPages', 'TeachedRecipes', 'BoredomChange', 'UnhappyChange', 'StressChange'),
    'activity:wearing': ('Type', 'BodyLocation', 'CanBeEquipped', 'ClothingItemExtra', 'ClothingItemExtraOption'),
    'activity:combat': ('Type', 'Ranged', 'AmmoType', 'MagazineType', 'Categories', 'CanBePlaced',
                        'ExplosionPower', 'FirePower', 'SmokeRange', 'NoiseRange', 'OnWeaponSwing', 'OnWeaponHit'),
    'activity:storage': ('Type', 'Capacity', 'AcceptItemFunction', 'CanBeEquipped', 'OnlyAcceptCategory'),
    'activity:expenditure': ('Type', 'UseDelta', 'IsWaterSource', 'ReplaceOnDeplete', 'OnCreate', 'OnEat'),
    'activity:cooking': ('Type', 'EvolvedRecipe'),
}
CONSUMERS = {
    'activity:ingestion': semantic.EAT, 'activity:reading': semantic.READ,
    'activity:wearing': semantic.WEAR, 'activity:combat': sources.FIREARM,
    'activity:storage': semantic.TRANSFER, 'activity:expenditure': semantic.DRINK,
    'activity:crafting': semantic.CRAFT, 'activity:cooking': semantic.COOK,
    'activity:world_work': semantic.PROPS, 'item:direct': semantic.MENU,
}

# Exact untagged melee declarations examined against the selected inventory,
# hotbar, campfire and registered context dispatch. Capability-bearing tools
# (fitness weights, barricading tools, plumbing wrench) are separate families.
PLAIN_MELEE_ITEMS = {'Base.' + name for name in (
    'LeadPipe', 'Nightstick', 'MetalBar', 'MetalPipe', 'MeatCleaver', 'HandScythe', 'PipeWrench',
    'Saxophone', 'Trumpet', 'Violin', 'Drumstick', 'Plunger', 'Flute', 'ChairLeg',
    'PickAxeHandle', 'PickAxeHandleSpiked', 'TableLeg', 'BadmintonRacket', 'TennisRacket',
    'Wrench', 'RollingPin', 'Pan', 'GridlePan', 'Chainsaw', 'Golfclub', 'Katana',
    'Banjo', 'GuitarAcoustic', 'Plank', 'PlankNail', 'Poolcue', 'HockeyStick',
    'IceHockeyStick', 'LaCrosseStick', 'CanoePadel', 'CanoePadelX2', 'BaseballBat',
    'BaseballBatNails', 'FishingRodBreak', 'LeafRake', 'Rake', 'GuitarElectricBassBlack',
    'GuitarElectricBassBlue', 'GuitarElectricBassRed', 'Keytar', 'GuitarElectricBlack',
    'GuitarElectricBlue', 'GuitarElectricRed', 'IcePick', 'LetterOpener', 'Scalpel',
    'Stake', 'ClosedUmbrellaBlue', 'ClosedUmbrellaRed', 'ClosedUmbrellaBlack',
    'ClosedUmbrellaWhite', 'WoodenLance')}
PLAIN_MELEE_FIELDS = {
    'AimingMod', 'AlwaysKnockdown', 'AttachmentType', 'BaseSpeed', 'BreakSound', 'Categories',
    'CloseKillMove', 'ConditionLowerChanceOneIn', 'ConditionMax', 'CritDmgMultiplier', 'CriticalChance',
    'DamageCategory', 'DamageMakeHole', 'DisplayCategory', 'DisplayName', 'DoorDamage', 'DoorHitSound',
    'EnduranceMod', 'HitAngleMod', 'HitFloorSound', 'HitSound', 'Icon', 'IdleAnim', 'ImpactSound',
    'IsAimedHandWeapon', 'KnockBackOnNoDeath', 'KnockdownMod', 'MaxDamage', 'MaxHitCount', 'MaxRange',
    'MetalValue', 'MinAngle', 'MinDamage', 'MinRange', 'MinimumSwingTime', 'PushBackMod',
    'RequiresEquippedBothHands', 'RunAnim', 'SoundMap', 'SplatBloodOnNoDeath', 'SplatNumber', 'SplatSize',
    'SubCategory', 'SwingAmountBeforeImpact', 'SwingAnim', 'SwingSound', 'SwingTime', 'Tooltip',
    'TreeDamage', 'TwoHandWeapon', 'Type', 'WeaponLength', 'WeaponSprite', 'Weight', 'critDmgMultiplier'}


