# review_queue_breakdown.md

- total: 8
- item_review: 6
- excluded_matcher: 1
- rule_blocked: 1

## By-kind details

### excluded_matcher (1)

- rule_id: rule_firefighting_isextinguisher, match_type: property, value: isWaterSource()

### item_review (6)

- fulltype: Base.PetrolBleachBottle, rule_ids: ['rule_worldobject_predicatepetrol'], reason: property_based exclusion (auto conclusion forbidden)
- fulltype: Base.PetrolCan, rule_ids: ['rule_worldobject_predicatepetrol'], reason: property_based exclusion (auto conclusion forbidden)
- fulltype: Base.PetrolPopBottle, rule_ids: ['rule_worldobject_predicatepetrol'], reason: property_based exclusion (auto conclusion forbidden)
- fulltype: Base.WaterBottlePetrol, rule_ids: ['rule_worldobject_predicatepetrol'], reason: property_based exclusion (auto conclusion forbidden)
- fulltype: Base.WhiskeyPetrol, rule_ids: ['rule_worldobject_predicatepetrol'], reason: property_based exclusion (auto conclusion forbidden)
- fulltype: Base.WinePetrol, rule_ids: ['rule_worldobject_predicatepetrol'], reason: property_based exclusion (auto conclusion forbidden)

### rule_blocked (1)

- rule_id: rule_moveabledefinitions_scrapdefinitions, reason: scrapDefinitions 테이블은 material 기반 정의이며, items_itemscript.json의 FullType에 결정적으로 매칭할 criteria가 부재. 후보 집합을 결정적으로 산출 불가.

## 처리 방침 (허용 근거 타입 기반)

- excluded_matcher(property): 정적 필드로 대체 가능한 경우에만 matcher 교체 → PASS/NO는 그대로, 불명확은 REVIEW 유지.
- item_review(property_based): 자동 NO 금지이므로 축소 대상 아님. 정적 tag/field로 'property_based' 라우팅만 유지.
- rule_blocked(비결정적 후보집합): criteria(정적 매처) 확보 전까지 자동 산출 불가 → 유지.