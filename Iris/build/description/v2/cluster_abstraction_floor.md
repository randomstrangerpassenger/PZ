# Cluster Abstraction Floor

> 목적: interaction cluster summary가 지나치게 추상적이거나 3-4 목록형으로 붕괴하는 것을 막는다.

---

## 1. 하한선 원칙

- cluster summary는 대표 작업 맥락을 포함해야 한다.
- role만 있고 작업이 없으면 `too_generic_use`다.
- 작업은 있는데 목록 구조가 섞이면 `borrowed_list_structure`다.
- summary는 한 아이템의 대표 이해를 돕는 문장이어야 한다.

## 2. 허용 골격

아래 세 골격만 최소 허용 골격으로 사용한다.

1. `~작업에서 ~할 때 쓴다`
2. `~에 쓰는 도구/부품/재료다`
3. `~작업에 들어가는 ~다`

## 3. 필수 조건

세 골격 중 어느 것을 쓰더라도 아래 조건이 필수다.

- 게임 내 작업 맥락이 직접 드러나야 한다.
- 아이템의 역할이 작업 맥락 안에서 읽혀야 한다.
- 문장은 단일 대표 맥락으로 닫혀야 한다.

### 허용 예시

- 금속 단조 작업에 들어가는 도구다
- 전자 조립에 쓰는 부품이다
- 조리 작업에서 재료를 익힐 때 쓴다

### 금지 예시

- 다양한 작업에 쓰인다
- 아이템을 제작할 때 쓴다
- 도구다
- 재료다

## 4. FAIL 패턴

### `too_generic_use`

다음은 HARD FAIL이다.

- 작업 맥락 없이 역할만 남는 문장
- `다양한`, `여러`, `일반적인`, `기본적인`처럼 범용성을 말하고 끝나는 문장
- `제작에 쓰인다`처럼 구체 작업이 없는 문장

### `borrowed_list_structure`

다음은 HARD FAIL이다.

- `:`, `·`, `1.`, `/`를 이용한 항목 나열
- `A, B, C` 식의 용도/대상 열거
- recipe/requirement/action label의 목록화

### `cluster_misaligned`

다음은 HARD FAIL이다.

- 선택된 cluster와 summary의 작업 맥락이 다를 때
- `metalwork_anvil`로 선택했는데 summary가 용접 작업을 말할 때
- `gun_modding`으로 선택했는데 summary가 탄약 제작을 말할 때

## 5. 판정 절차

- summary 초안은 `3_3_vs_4_boundary_examples.md`의 허용/금지 예시와 대조한다.
- 허용 골격을 썼더라도 작업 맥락이 없으면 FAIL이다.
- V9 맥락어 검사는 WARN으로만 사용하며, 구조 FAIL은 여기 정의된 패턴이 우선한다.
