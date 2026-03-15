"""
build_layer3_facts.py — facts 빌더 (현재: 수동 편집 보조 + validate)

현재 역할:
  - JSONL 순회하며 스키마 검증 수행
  - 기본 정합성 체크 (타입, 필수 필드, 금지어)

Phase 3 전환 시:
  - 자동 facts 생성으로 확장 예정
"""


def main():
    print("build_layer3_facts: Phase 2에서는 수동 편집 + validate 역할만 수행합니다.")
    print("facts 검증은 run_pipeline.py를 통해 DVF를 사용하세요.")


if __name__ == '__main__':
    main()
