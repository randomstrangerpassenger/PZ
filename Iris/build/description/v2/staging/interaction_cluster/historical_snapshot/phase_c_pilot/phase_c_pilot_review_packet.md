# Phase C Pilot Review Packet

- total rows: 52
- review sources: {'historical_snapshot': 50, 'seed_supplement': 2}
- pilot groups: {'role_fallback_excess': 25, 'layer4_rich_layer3_sparse': 26, 'high_abstraction': 1}

## Rows

### Base.CanOpener
- source: seed_supplement
- focus: group:high_abstraction, direct_use_preservation
- suggested: misaligned=false, too_generic=false, direct_use_preserved=true
- suggestion basis: expected_selected_cluster, use_source:direct_use
- cluster: expected=cooking_prep actual=cooking_prep
- merge/use: direct_use_keep / direct_use
- primary use: 통조림 개봉에 쓰는 도구다
- rendered: 도구. 통조림 개봉에 쓰는 도구다. 주방과 조리 도구 보관 장소에서 발견된다.
- acquisition: 주방과 조리 도구 보관 장소에서 발견된다

### Base.ModKit
- source: seed_supplement
- focus: group:layer4_rich_layer3_sparse, tie_break_validation, direct_use_replacement
- suggested: misaligned=false, too_generic=false
- suggestion basis: expected_selected_cluster
- cluster: expected=gun_modding actual=gun_modding
- merge/use: direct_use_replaced_by_cluster / cluster_summary
- primary use: 총기 개조 작업에 들어가는 부품이다
- rendered: 도구. 총기 개조 작업에 들어가는 부품이다. 총포상과 작업대 주변에서 발견된다.
- acquisition: 총포상과 작업대 주변에서 발견된다

### Base.Apron_Black
- source: historical_snapshot
- focus: group:layer4_rich_layer3_sparse, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 조리 도구 보관 장소에서 발견된다

### Base.Apron_IceCream
- source: historical_snapshot
- focus: group:layer4_rich_layer3_sparse, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 시가지와 트레일러파크, 초목 지대 채집으로 구할 수 있다

### Base.Apron_Jay
- source: historical_snapshot
- focus: group:layer4_rich_layer3_sparse, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 시가지와 트레일러파크, 초목 지대 채집으로 구할 수 있다

### Base.Apron_Spiffos
- source: historical_snapshot
- focus: group:layer4_rich_layer3_sparse, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 스피포 주방과 스피포 상품 진열대, 스피포 차량에서 발견된다

### Base.Apron_White
- source: historical_snapshot
- focus: group:layer4_rich_layer3_sparse, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 주방과 조리 작업 장소에서 발견된다

### Base.Apron_WhiteTEXTURE
- source: historical_snapshot
- focus: group:layer4_rich_layer3_sparse, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 시가지와 트레일러파크, 초목 지대 채집으로 구할 수 있다

### Base.BadmintonRacket
- source: historical_snapshot
- focus: group:layer4_rich_layer3_sparse, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 스포츠 상자와 라켓 보관함에서 발견된다

### Base.Bag_ALICEpack
- source: historical_snapshot
- focus: group:layer4_rich_layer3_sparse, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 군용품점과 캠핑, 사냥 장비 보관 장소, 생존 차량에서 발견된다

### Base.Bag_ALICEpack_Army
- source: historical_snapshot
- focus: group:layer4_rich_layer3_sparse, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 군용 보관 장소와 군용품점에서 발견된다

### Base.Bag_BigHikingBag
- source: historical_snapshot
- focus: group:layer4_rich_layer3_sparse, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 캠핑과 사냥 장비 보관 장소, 의류 보관 장소와 생존 차량에서 발견된다

### Base.Bag_DuffelBag
- source: historical_snapshot
- focus: group:layer4_rich_layer3_sparse, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 군용품점과 캠핑 장비 보관 장소에서 발견된다

### Base.Bag_DuffelBagTINT
- source: historical_snapshot
- focus: group:layer4_rich_layer3_sparse, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 사물함과 의류 보관 장소, 생존 차량에서 발견된다

### Base.Bag_FannyPackFront
- source: historical_snapshot
- focus: group:layer4_rich_layer3_sparse, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 사물함과 의류 보관 장소, 체육관과 경찰 보관 장소에서 발견된다

### Base.Bag_FoodCanned
- source: historical_snapshot
- focus: group:layer4_rich_layer3_sparse, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 생존 차량에서 발견된다

### Base.Bag_FoodSnacks
- source: historical_snapshot
- focus: group:layer4_rich_layer3_sparse, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 생존 차량에서 발견된다

### Base.Bag_GolfBag
- source: historical_snapshot
- focus: group:layer4_rich_layer3_sparse, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 골프 보관함과 골프 차량에서 발견된다

### Base.Bag_MedicalBag
- source: historical_snapshot
- focus: group:layer4_rich_layer3_sparse, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 구급차와 의사 차량, 생존 차량에서 발견된다

### Base.Bag_Military
- source: historical_snapshot
- focus: group:layer4_rich_layer3_sparse, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 군용 보관 장소와 군용품점에서 발견된다

### Base.Bag_NormalHikingBag
- source: historical_snapshot
- focus: group:layer4_rich_layer3_sparse, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 캠핑과 사냥 장비 보관 장소, 의류 보관 장소와 생존 차량에서 발견된다

### Base.Bag_Satchel
- source: historical_snapshot
- focus: group:layer4_rich_layer3_sparse, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 서점 가방 진열대와 학교 물품 장소, 사물함에서 발견된다

### Base.Bag_Schoolbag
- source: historical_snapshot
- focus: group:layer4_rich_layer3_sparse, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 서점 가방 진열대와 학교 물품 장소, 학교 보관 장소에서 발견된다

### Base.Bag_ShotgunBag
- source: historical_snapshot
- focus: group:layer4_rich_layer3_sparse, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 생존 차량과 생존자 은닉처에서 발견된다

### Base.Bag_ShotgunDblBag
- source: historical_snapshot
- focus: group:layer4_rich_layer3_sparse, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 생존 차량과 생존자 은닉처에서 발견된다

### Base.Bag_ShotgunDblSawnoffBag
- source: historical_snapshot
- focus: group:layer4_rich_layer3_sparse, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 생존 차량과 생존자 은닉처에서 발견된다

### Base.Bag_ShotgunSawnoffBag
- source: historical_snapshot
- focus: group:layer4_rich_layer3_sparse, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 생존 차량과 생존자 은닉처에서 발견된다

### Base.BakingTray_Muffin
- source: historical_snapshot
- focus: group:role_fallback_excess, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 반죽이나 재료를 조리해 만든다

### Base.BakingTray_Muffin_Recipe
- source: historical_snapshot
- focus: group:role_fallback_excess, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 재료를 섞어 준비한다

### Base.BreadSlices
- source: historical_snapshot
- focus: group:role_fallback_excess, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 빵을 잘라 얻는다

### Base.CakeRaw
- source: historical_snapshot
- focus: group:role_fallback_excess, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 재료를 섞어 준비한다

### Base.CannedBellPepper
- source: historical_snapshot
- focus: group:role_fallback_excess, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 재료를 병조림해 만든다

### Base.CannedBroccoli
- source: historical_snapshot
- focus: group:role_fallback_excess, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 재료를 병조림해 만든다

### Base.CannedCarrots
- source: historical_snapshot
- focus: group:role_fallback_excess, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 재료를 병조림해 만든다

### Base.CannedEggplant
- source: historical_snapshot
- focus: group:role_fallback_excess, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 재료를 병조림해 만든다

### Base.CannedLeek
- source: historical_snapshot
- focus: group:role_fallback_excess, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 재료를 병조림해 만든다

### Base.CannedPotato
- source: historical_snapshot
- focus: group:role_fallback_excess, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 재료를 병조림해 만든다

### Base.CannedRedRadish
- source: historical_snapshot
- focus: group:role_fallback_excess, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 재료를 병조림해 만든다

### Base.CannedTomato
- source: historical_snapshot
- focus: group:role_fallback_excess, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 재료를 병조림해 만든다

### Base.CookieChocolateChipDough
- source: historical_snapshot
- focus: group:role_fallback_excess, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 재료를 섞어 준비한다

### Base.CookiesChocolateDough
- source: historical_snapshot
- focus: group:role_fallback_excess, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 재료를 섞어 준비한다

### Base.CookiesOatmealDough
- source: historical_snapshot
- focus: group:role_fallback_excess, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 재료를 섞어 준비한다

### Base.CookiesShortbreadDough
- source: historical_snapshot
- focus: group:role_fallback_excess, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 재료를 섞어 준비한다

### Base.CookiesSugarDough
- source: historical_snapshot
- focus: group:role_fallback_excess, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 재료를 섞어 준비한다

### Base.Dogfood
- source: historical_snapshot
- focus: group:role_fallback_excess, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 가정집이나 애완용품 판매점에서 발견된다

### Base.Glue
- source: historical_snapshot
- focus: group:role_fallback_excess, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 문구 보관 장소나 사무용품 보관 장소에서 발견된다

### Base.GriddlePanFriedVegetables
- source: historical_snapshot
- focus: group:role_fallback_excess, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 재료를 조리해 만든다

### Base.MuffinTray
- source: historical_snapshot
- focus: group:role_fallback_excess, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 가정집이나 제과점에서 발견된다

### Base.Muffintray_Biscuit
- source: historical_snapshot
- focus: group:role_fallback_excess, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 반죽이나 재료를 조리해 만든다

### Base.OmeletteRecipe
- source: historical_snapshot
- focus: group:role_fallback_excess, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 재료를 섞어 준비한다

### Base.OnionRings
- source: historical_snapshot
- focus: group:role_fallback_excess, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 재료를 조리해 만든다

### Base.Pan
- source: historical_snapshot
- focus: group:role_fallback_excess, cluster_absent_validation, role_fallback_residual, primary_use_gap
- suggested: no auto-suggestion
- suggestion basis: none
- cluster: expected=None actual=None
- merge/use: cluster_absent_keep_existing / role_fallback
- primary use: <null>
- rendered: <null>
- acquisition: 주방용품 매장과 조리 도구 보관 장소에서 발견된다
