# Iris Evidence Allowlist (v0.2)

이 문서는 Iris 자동 분류 시스템에서 **허용되는 증거(Evidence)**를 정의한다.  
여기에 명시되지 않은 증거는 분류 규칙에서 사용할 수 없다.

> ⚠️ **v0.2 주요 변경**: 바닐라 스크립트 실데이터 분석 결과 반영. Medical 필드 추가, 존재하지 않는 Tags/CustomContextMenu 값 제거, Recipe Category 수정.

---

## 핵심 원칙

1. **추론 금지** — 아이템 이름, DisplayName, 설명 문자열에서 의미를 추론하지 않는다
2. **판단 금지** — 수치의 크기, 수준, 효율을 비교하지 않는다
3. **누적만 허용** — 태그는 추가만, 제거/선택/우선순위 없음
4. **목록 외 금지** — 이 문서에 없는 증거 소스는 사용 불가

---

## 1. 허용 증거 소스

### 1-1. Item Script 필드

아이템 스크립트(`.txt`)에서 직접 참조 가능한 필드 목록.

#### 분류용 필드 (Classification)

| 필드명 | 타입 | 용도 | 허용값 |
|--------|------|------|--------|
| `Type` | enum | 아이템 기본 타입 | `Weapon`, `Food`, `Literature`, `Clothing`, `Drainable`, `Radio`, `Map`, `Normal`, `Container`, `WeaponPart` |
| `Categories` | string[] | 무기 카테고리 | 섹션 2 참조 |
| `SubCategory` | string | 무기 세부 카테고리 | `Swinging`, `Stab`, `Spear`, `Firearm` |
| `BodyLocation` | string | 착용 부위 | 섹션 3 참조 |
| `AmmoType` | string | 탄약 타입 | 섹션 4 참조 |
| `Tags` | string[] | 아이템 태그 | 섹션 5 참조 |

> ⚠️ **Tags 정의**: `Tags`는 **Item Script에 명시적으로 선언된 태그 문자열만**을 의미한다.  
> 런타임에서 파생/추론된 태그는 사용 불가.

#### 무기 세부 분류 필드 (Weapon Detail)

| 필드명 | 타입 | 용도 | 분류 연결 |
|--------|------|------|-----------|
| `TwoHandWeapon` | boolean | 양손 무기 여부 | 장/단 무기 구분 — exists=장, not exists=단 |
| `IsAimedFirearm` | boolean | 조준 총기 여부 | 총기 확인 (보조) |
| `MountOn` | string | 장착 가능 총기 | 2-L(총기부품) — exists가 핵심 증거 |

> ⚠️ **TwoHandWeapon 특이사항**: 바닐라에서 `TRUE`만 존재하고, 한손 무기는 필드 자체가 없음.  
> 따라서 `exists` = 양손(장무기), `not exists` = 한손(단무기)로 구분.

#### 의료 관련 필드 (Medical) — v0.2 신규

| 필드명 | 타입 | 용도 | 분류 연결 |
|--------|------|------|-----------|
| `Medical` | boolean | 의료 아이템 여부 | 3-C(의약품) |
| `CanBandage` | boolean | 붕대 기능 여부 | 3-C(의약품) |
| `AlcoholPower` | number | 소독 효과 | 3-C(의약품) — exists만 허용, 수치 비교 금지 |
| `BandagePower` | number | 붕대 효과 | 표시 정보 (분류 증거 아님) |

> ⚠️ **Medical 필드**: `Medical = TRUE`는 Tags가 아닌 **독립 필드**다.  
> `Tags contains "Medical"`이 아닌 `Medical = TRUE`로 체크한다.

#### 광원/점화 필드 (Light/Fire)

| 필드명 | 타입 | 용도 | 분류 연결 |
|--------|------|------|-----------|
| `LightStrength` | number | 광원 강도 | 1-H(광원) — exists만 허용, 수치 비교 금지 |
| `TorchCone` | boolean | 손전등형 광원 | 1-H(광원) |
| `ActivatedItem` | boolean | 활성화/토글 가능 | 1-H(광원/점화) 가드 |

> ⚠️ **광원 필드 제한**: `LightStrength`는 **exists 여부만** 분류 증거로 사용.  
> 수치 비교(`> 0.5` 등)는 금지.

#### 행동 연결 필드 (Action-Indicating)

| 필드명 | 타입 | 나타내는 행동 | 분류 연결 |
|--------|------|---------------|-----------|
| `CustomContextMenu` | string[] | 컨텍스트 메뉴 액션 | 섹션 6 참조 |
| `TeachedRecipes` | string[] | 레시피 해금 | 5-B(레시피잡지) |
| `SkillTrained` | string | 스킬 훈련 | 5-A(스킬북) |
| `CanStoreWater` | boolean | 물 저장 가능 | 1-D(조리) 보조 |
| `Alcoholic` | boolean | 알코올 여부 | 3-D(기호품) |
| `TwoWay` | boolean | 양방향 송수신 | 1-I(통신) — 워키토키 구분 |

> ⚠️ **Literature 분류 우선순위**:  
> - 1순위: `Type = Literature`  
> - 2순위: `Type = Map`

#### 상태/수치 필드 (exists로 분류 증거 사용 가능)

| 필드명 | 용도 | 분류 연결 |
|--------|------|-----------|
| `HungerChange` | 배고픔 변화 | 3-A(식품) — `Type = Food` AND `HungerChange exists` |
| `ThirstChange` | 갈증 변화 | 3-B(음료) — `Type = Food/Drainable` AND `ThirstChange exists` |
| `StressChange` | 스트레스 변화 | 3-D(기호품) — `Type = Food` AND `StressChange exists` |

> ⚠️ **exists 단독 금지**: 위 필드들은 반드시 Type 가드와 함께 사용해야 한다.

#### 상태/수치 필드 (Display Only)

이 필드들은 **분류 증거로 사용 불가**. UI 표시 정보로만 사용.

| 필드명 | 용도 |
|--------|------|
| `MaxDamage`, `MinDamage` | 전투 상세 패널 표시 |
| `Weight` | 일반 정보 표시 |
| `UseDelta` | 소모품 잔량 표시 |
| `BandagePower` | 붕대 효과 수치 표시 |

---

### 1-2. Recipe 관계

아이템이 레시피에서 어떤 역할로 참조되는지.

#### 허용 Role

| Role | 설명 | 분류 연결 예시 |
|------|------|----------------|
| `input` | 재료로 소모됨 | 4(Resource) |
| `output` | 결과물로 생성됨 | (분류 아닌 역참조용) |
| `keep` | 도구로 사용, 소모 안 됨 | 1(Tool) |
| `require` | 필수 도구 | 1(Tool) |

> ⚠️ **output role 제한**: `output` role은 **분류 태그를 추가하는 증거로 사용하지 않는다.**

#### Recipe Category 허용값 (v0.2 수정)

| Category | 용도 | 분류 연결 |
|----------|------|-----------|
| `Carpentry` | 목공 | Tool.1-A, Resource.4-A |
| `Cooking` | 조리 | Tool.1-D, Resource.4-B |
| `Electrical` | 전자 | Resource.4-E |
| `Smithing` | 대장 | Tool.1-A |
| `Welding` | 용접 | Tool.1-A, Resource.4-A |
| `Survivalist` | 생존 | 다용도 |
| `Farming` | 농업 | Tool.1-E |
| `Fishing` | 낚시 | Tool.1-G |
| `Trapper` | 덫 | Tool.1-G |
| `Health` | 의료 | Resource.4-C |
| `Engineer` | 공학 | Resource.4-E |

> ⚠️ **폐기된 Category** (v0.2): `MetalWelding`(→ `Welding` 사용), `Masonry`(바닐라 없음), `Mechanics`(바닐라 없음), `Electronics`(→ `Electrical` 사용)

---

### 1-3. Fixing 관계

| Role | 설명 | 분류 연결 |
|------|------|-----------|
| `Fixer` | 수리 도구 | 1-C(정비) |

---

### 1-4. Moveables 관계 (Lua)

소스 파일: `ISMoveableDefinitions.lua`

#### Moveables ItemId 허용값 (v0.2 확정)

| 허용값 | 도구 정의 | 분류 연결 |
|--------|-----------|-----------|
| `Base.Hammer` | Hammer | 1-A, 1-B |
| `Base.Screwdriver` | Electrician, Metal | 1-B |
| `Base.Shovel` | Shovel | 1-E |
| `Base.Wrench` | Wrench | 1-C |
| `Base.PipeWrench` | Wrench | 1-C |

#### Moveables Tag 허용값 (v0.2 확정)

| 허용값 | 도구 정의 | 분류 연결 |
|--------|-----------|-----------|
| `Tag.Crowbar` | Crowbar | 1-B |
| `Tag.SharpKnife` | Cutter | 1-B, 1-D |
| `Tag.Scissors` | Cutter | 1-B |
| `Tag.WeldingMask` | MetalBars (보조) | 1-A |

---

## 2. Categories 허용값 (v0.2 확정)

바닐라 무기 스크립트에서 실제 확인된 값.

| 허용값 | 개수 | 분류 연결 |
|--------|------|-----------|
| `Axe` | 5 | Combat.2-A |
| `Blunt` | 40 | Combat.2-B/2-C (TwoHandWeapon으로 구분) |
| `SmallBlunt` | 25 | Combat.2-C (단둔기) |
| `LongBlade` | 2 | Combat.2-D |
| `SmallBlade` | 18 | Combat.2-E |
| `Spear` | 20 | Combat.2-F |
| `Improvised` | 56 | 보조 태그 (단독 분류 기준 아님) |

> ⚠️ **폐기된 값** (v0.2): `Blade`(→ `SmallBlade`, `LongBlade` 사용), `Thrown`(바닐라에 없음)

---

## 3. BodyLocation 매핑 테이블 (v0.2 신규)

### 6-A. 모자/헬멧 (Headwear)

`Hat`, `FullHat`, `FullHelmet`, `Mask`, `MaskEyes`, `MaskFull`

### 6-B. 상의 (Upperwear)

`Shirt`, `ShortSleeveShirt`, `Tshirt`, `TankTop`, `Sweater`, `SweaterHat`, `Jacket`, `JacketHat`, `JacketHat_Bulky`, `JacketSuit`, `Jacket_Bulky`, `Jacket_Down`, `TorsoExtra`, `TorsoExtraVest`

### 6-C. 하의 (Lowerwear)

`Pants`, `Skirt`, `Legs1`

### 6-D. 장갑 (Handwear)

`Hands`

### 6-E. 신발 (Footwear)

`Shoes`, `Socks`

### 6-G. 힙색 (Fanny Pack)

`FannyPackFront`, `FannyPackBack`

### 6-H. 액세서리 (Accessory)

`Belt`, `BeltExtra`, `Neck`, `Necklace`, `Necklace_Long`, `Eyes`, `LeftEye`, `RightEye`, `Ears`, `EarTop`, `Scarf`, `LeftWrist`, `RightWrist`, `Left_MiddleFinger`, `Left_RingFinger`, `Right_MiddleFinger`, `Right_RingFinger`, `Nose`, `BellyButton`, `AmmoStrap`

### 다중 태그 (전신복)

| BodyLocation 값 | 분류 |
|-----------------|------|
| `Boilersuit` | 6-B + 6-C |
| `Dress` | 6-B + 6-C |
| `FullSuit` | 6-B + 6-C |
| `FullSuitHead` | 6-A + 6-B + 6-C |

### 분류 제외

`ZedDmg`, `Wound`, `Bandage`, `MakeUp_*`, `Underwear*`, `Tail`

---

## 4. AmmoType 허용값 (확정)

### 권총 (2-G)

`Base.Bullets9mm`, `Base.Bullets45`, `Base.Bullets44`, `Base.Bullets38`

### 소총 (2-H)

`Base.223Bullets`, `Base.308Bullets`, `Base.556Bullets`

### 산탄총 (2-I)

`Base.ShotgunShells`

---

## 5. Tags 허용값 (v0.2 전면 개정)

바닐라 스크립트에서 실제 확인된 Tags만 허용.

### 도구 관련

| 태그 | 분류 연결 |
|------|-----------|
| `Hammer` | 1-A, 1-B |
| `Saw` | 1-A, 1-B |
| `Screwdriver` | 1-B, 1-C |
| `Crowbar` | 1-B |
| `Scissors` | 1-B |
| `CanOpener` | 1-B |
| `RemoveBarricade` | 1-B |
| `FishingRod` | 1-G |
| `FishingSpear` | 1-G |
| `Lighter` | 1-H |
| `StartFire` | 1-H |
| `ChopTree` | 1-E |
| `DigPlow` | 1-E |
| `DigGrave` | 1-E |
| `ClearAshes` | 1-E |
| `TakeDirt` | 1-E |
| `Sledgehammer` | 1-A |
| `WeldingMask` | 1-A 보조 |

### 의료 관련

| 태그 | 분류 연결 |
|------|-----------|
| `RemoveBullet` | 1-F |
| `RemoveGlass` | 1-F |
| `SewingNeedle` | 1-F |
| `Disinfectant` | 3-C |

### 조리 관련

| 태그 | 분류 연결 |
|------|-----------|
| `CoffeeMaker` | 1-D |
| `SharpKnife` | 1-B, 1-D |
| `DullKnife` | 1-D |
| `Fork` | 1-D |
| `Spoon` | 1-D |

### 식품/음료 관련

| 태그 | 분류 연결 |
|------|-----------|
| `AlcoholicBeverage` | 3-D 보조 |
| `LowAlcohol` | 3-D 보조 |
| `HerbalTea` | 3-E |

### 기타

| 태그 | 분류 연결 |
|------|-----------|
| `Petrol` | 4-D |
| `Rope` | 4-F |
| `GasMask` | 6-A 보조 |

### 폐기된 Tags (v0.2) — 바닐라에 없음

| 폐기 태그 | 대체 방안 |
|-----------|-----------|
| `Cookware` | `CoffeeMaker` 또는 Recipe Cooking+keep |
| `Medical` | `Medical = TRUE` 필드 사용 |
| `Tool` | 개별 도구 태그 사용 |
| `Weapon` | `Type = Weapon` 사용 |
| `Clothing` | `Type = Clothing` 사용 |
| `Food` | `Type = Food` 사용 |
| `Literature` | `Type = Literature` 사용 |

---

## 6. CustomContextMenu 허용값 (v0.2 수정)

바닐라 Item Script에서 실제 확인된 값만 허용.

| 허용값 | 분류 연결 |
|--------|-----------|
| `Drink` | 3-B 보조 |
| `Smoke` | 3-D |
| `Take` | 3-C 보조 |

### 폐기된 CustomContextMenu 값 (v0.2) — Item Script에 없음

| 폐기 값 | 대체 방안 |
|---------|-----------|
| `Disinfect` | `AlcoholPower exists` 또는 `Tags = Disinfectant` |
| `Bandage` | `CanBandage = TRUE` |
| `Splint` | 수동 오버라이드 |
| `Stitch` | `Tags = SewingNeedle` |
| `RemoveBullet` | `Tags = RemoveBullet` |
| `RemoveGlass` | `Tags = RemoveGlass` |
| `CleanWound` | 수동 오버라이드 |

---

## 7. 필드 연산 규칙

### 7-1. `exists` 연산

**규칙: 단독 사용 금지, 반드시 Type 가드와 함께**

**예외: 다음 필드는 단독 exists 허용**

- `Medical` — 의료 아이템 전용 필드
- `CanBandage` — 붕대 아이템 전용 필드
- `MountOn` — 총기부품 전용 필드
- `TorchCone` — 손전등 전용 필드
- `TeachedRecipes` — 레시피잡지 전용 필드
- `SkillTrained` — 스킬북 전용 필드

### 7-2. `equals` 연산

**규칙: boolean/enum만 허용, 수치 비교 금지**

### 7-3. `contains` 연산

**규칙: 허용 필드 + 허용값 목록만**

허용 필드: `Tags`, `Categories`, `CustomContextMenu`

---

## 8. 금지 목록

### 절대 금지

| 항목 | 이유 |
|------|------|
| `DisplayName` | 이름 추론 금지 |
| `DisplayCategory` | 표시용 카테고리, 분류 증거 아님 |
| 아이템 설명(Description) | 텍스트 추론 금지 |
| 수치 비교 (`>`, `<`, `>=`, `<=`) | 판단/평가로 이어짐 |
| 허용 목록 외 문자열 매칭 | 분류 기준 오염 방지 |

### 조건부 금지

| 항목 | 조건 |
|------|------|
| `exists` 단독 사용 | 예외 필드 외에는 Type 가드 필수 |
| Recipe `category` | role과 조합 필수 |

---

## 9. 수동 오버라이드 필수 항목 (v0.2)

| 소분류 | 대상 | 사유 |
|--------|------|------|
| Tool.1-J | `Base.Generator` | 전용 필드 없음 |
| Combat.2-J | 투척/폭발물 | Categories=Thrown 없음 |
| Combat.2-K | 탄약류 | Type=Ammo 없음 |
| Resource.4-D | 연료류 | 연료 전용 필드 없음 |
| Consumable.3-E | 약초류 | 전용 필드 없음 |

---

## 변경 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| 0.1 | - | 초안 작성 |
| 0.2 | - | 바닐라 데이터 기반 전면 개정 |
