# Right-click Capability Allowlist v1

> **원칙**: 이 목록 밖의 Capability 생성 시도 = **Fail**  
> Iris는 "의미 시스템"이 아닌 "결정적 Capability Evidence 시스템"

---

## Phase 0-1: Capability 대상 범위 확정

### Allowlist (7개)

| ID | Capability ID | 설명 | 
|---|---|---|
| 1 | `can_extinguish_fire` | 불 끄기 (소화기/물/모래주머니) |
| 2 | `can_add_generator_fuel` | 발전기 연료 추가 |
| 3 | `can_scrap_moveables` | Moveable 해체 |
| 4 | `can_open_canned_food` | 캔 음식 열기 (Recipe 연동) |
| 5 | `can_stitch_wound` | 상처 봉합 |
| 6 | `can_remove_embedded_object` | 박힌 물체 제거 (유리/총알) |
| 7 | `can_attach_weapon_mod` | 무기 부착물 장착 |

---

## Phase 0-2: Capability 정의 형식 고정

```typescript
interface Capability {
  id: string;           // can_xxx 형식
  type: "capability";   // 고정
  source: "right-click"; // 고정
}
```

### 금지 필드
- ❌ description (설명)
- ❌ meaning (의미)
- ❌ action_name (행동명)
- ❌ menu_label (메뉴명)

---

## 버전 정보

- **Version**: v1
- **Created**: 2026-02-08
- **Status**: Active
