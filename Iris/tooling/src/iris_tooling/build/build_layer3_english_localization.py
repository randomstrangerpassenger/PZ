from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import shutil

from .dvf_3_3_generation_contract import (
    CANONICAL_INPUTS,
    canonical_input_identity,
    repository_path,
)
from .repository_context import require_repository_context


CURRENT_POINTER_RELATIVE_PATH = "Iris/media/lua/client/Iris/Data/IrisLayer3DataCurrent.lua"
CURRENT_GENERATION_ROOT_RELATIVE_PATH = (
    "Iris/media/lua/client/Iris/Data/IrisLayer3Generations"
)
TOOLTIP_T1_OWNER_OUTPUT_RELATIVE_PATH = (
    "Iris/build/description/v2/data/tooltip_t1_layer3_owner_input.json"
)
TOOLTIP_T1_D3_REGISTRY_RELATIVE_PATH = (
    "Iris/_docs/authority/dvf/tooltip_t1_d3_disposition_registry.json"
)


PRIMARY_USE_SOURCE_SHA256 = "6d9e5d73cf8425ea0113fab960b993e9668777958b9452273407d739540e0503"

# This list is aligned with the sorted, distinct primary_use values in the
# current Layer 3 facts. The source hash prevents a changed fact set from being
# paired with stale localization.
PRIMARY_USE_EN = [
    "Junk with no specific crafting use in Build 41.",
    "A chew toy for dogs.",
    "A medical consumable used to manage or treat health conditions.",
    "Used to shape or fit material into other tool parts during construction or crafting preparation.",
    "A rubber duck whose battery can be inserted or removed.",
    "Used to shape or fit materials while preparing construction work.",
    "A nail used in construction or crafting.",
    "Sporting equipment used according to the rules of a game or activity.",
    "A toy shaped like a rubber duck.",
    "Handled when arranging a space by placing or removing decorations, exhibits, signs, or area markers.",
    "Food eaten as fruit.",
    "Handled when placing or throwing a noise-making device as a distraction.",
    "Used to thrust or push from a distance in close combat.",
    "Used to swing, strike, or push in close combat.",
    "A tool used both in close combat and for practical work.",
    "A weapon used in close combat.",
    "A metal pipe used as material in metalworking.",
    "A small metal sheet used as material for producing metal sheets.",
    "A metal sheet used as material for producing smaller metal sheets.",
    "Used as material for metal structures and certain metal items.",
    "A tool used for metal forging.",
    "A tool used for joining metal.",
    "Used in metal crafting to melt or hammer material into other parts.",
    "Scrap left by metal dismantling that cannot be used as material.",
    "Cosmetics used as a base layer of makeup.",
    "Consumed recreationally to improve mood.",
    "A medical tool used with a suture needle to close deep wounds.",
    "Broken glass that requires care when approached or cleared.",
    "A cord-like material.",
    "Fishing line used to make or repair fishing rods.",
    "Handled during play with boards, cards, pieces, or small toys.",
    "Used to remove or divide seeds while preparing to farm.",
    "Cosmetics used around the eyes.",
    "Face paint used to add a pattern around the eyes.",
    "Eye shadow used to add color around the eyes.",
    "Material used to make traps and fishing nets.",
    "A tool used to place or retrieve traps.",
    "A portable container for carrying tools or other items.",
    "A tool.",
    "Read or skimmed to examine its contents.",
    "A stone used to make a stone hammer.",
    "Hair gel used to style hair.",
    "A comb used to arrange and groom hair.",
    "Hair dye used to change hair color.",
    "A tool used for shaving.",
    "A piece of wood usable as campfire fuel.",
    "A twig used to prepare campfire material.",
    "A drawer part made through carpentry.",
    "Plank material used in carpentry and other crafting.",
    "A mirror used to check grooming.",
    "Worn on the body as part of an outfit or for a specific function.",
    "An accessory worn on the body.",
    "A medical tool used to remove embedded glass or bullets.",
    "Clothing worn on or around the body.",
    "Perfume used to add fragrance to the body.",
    "Rope material used in crafting that requires tying or connecting.",
    "Stationery used to write or revise documents or organize paper.",
    "Used to build structures that require hinges, such as doors or gates.",
    "A bag used to hold and carry items.",
    "A vessel used to hold water.",
    "An empty container that can be reused to carry water.",
    "A metal drum used to collect water or burn wood into charcoal.",
    "A collar worn by a pet dog.",
    "Used to chop or cut trees while logging.",
    "Handled to store, carry, or divide possessions and contents.",
    "Handled to lock or unlock padlocks, vehicles, or doors.",
    "Flint used to make a spark.",
    "Handled when emptying, sorting, reusing, or disposing of leftover cans and containers.",
    "A double-barrel shotgun used for shooting.",
    "A shotgun used for shooting.",
    "A firearm used for shooting.",
    "Used as a rifle or as equipment that stores one.",
    "A frame used to hold a photograph or picture.",
    "Can be opened to remove screws.",
    "Can be opened to remove nails.",
    "Can be opened to remove several empty bottles.",
    "Medical supplies used to treat wounds.",
    "Handled while cleaning the body or surroundings and gathering household consumables.",
    "Handled when removing or reinstalling devices and fixed fixtures.",
    "An explosive used in combat by placing or throwing it before detonation.",
    "A reusable device that makes a sound after a set delay.",
    "A pine cone produced by a pine tree.",
    "A small bell that makes sound.",
    "Handled when carrying cash, cards, and a wallet.",
    "Metal bar material used to make crowbars and golf clubs.",
    "Used to reconnect or repair damaged equipment.",
    "Used to open or divide sacks while organizing harvested goods.",
    "A device used to check the time or set an alarm.",
    "Food used in meal preparation or consumption.",
    "Soup eaten as food.",
    "An electronic device used to check signals or operate equipment.",
    "Handled when moving chairs, tables, or resting furniture into position indoors.",
    "Handled when moving storage furniture or containers into position indoors.",
    "Used to set up temporary shelter while preparing a campsite.",
    "Opened for rain protection or folded for carrying outdoors.",
    "Face paint used to add a pattern across the face.",
    "Material used to make an aerosol bomb.",
    "Handled during leisure when viewing or collecting photos, recordings, souvenirs, or toys.",
    "Denim-strip material used in several crafting processes.",
    "Torn-cloth material used in several crafting processes.",
    "Used to transfer or add fuel.",
    "Material used to make a smoke bomb.",
    "A musical instrument used for performance.",
    "A button attached to clothing or fabric goods.",
    "Coal used as furnace fuel.",
    "A container.",
    "A propane tank used to refill a welding torch.",
    "Used to shape stone tools or improvised weapons in primitive crafting.",
    "A map referenced for navigation and route planning.",
    "Used to drink or share a beverage.",
    "Used to prepare or consume food while it is held in a container.",
    "Kitchenware used to prepare or hold food and drinks.",
    "Used to disinfect or medicate wounds during treatment.",
    "An item used in medical treatment.",
    "Used to mend clothing or reinforce it with leather patches.",
    "Opened and referenced to check a location while planning travel.",
    "Toothpaste used to brush teeth.",
    "A toothbrush used to brush teeth.",
    "A household consumable used in ordinary consumption.",
    "Used to repair certain damaged weapons or tools.",
    "Cosmetics used to add color to the lips.",
    "Used to store or remove harvested goods kept in a sack.",
    "Handled when putting ammunition into or taking it out of boxes and clips.",
    "A material.",
    "Used to remove and plant seeds while preparing cultivation.",
    "Gardening supplies used in cultivation and maintenance.",
    "A tool used for cultivation and soil work.",
    "A needle used for sewing.",
    "Installed to supply electricity to nearby devices.",
    "Handled when dismantling electronics or fitting circuits.",
    "An electronic device intended for dismantling.",
    "Handled while assembling, maintaining, or dismantling electronic equipment.",
    "Consumable material used in crafting or repair.",
    "Cookware used to hold or mix ingredients before cooking.",
    "Handled during food preparation or cooking.",
    "Food used while preparing or eating a meal.",
    "An ingredient used in cooking.",
    "Food that is cooked before eating.",
    "A screw used in assembly or repair.",
    "Handled with tableware and place-setting items during kitchen work or meal preparation.",
    "Used to reinforce the tip of a spear while making an improvised weapon.",
    "Used to fit a rod or branch into the handle or body of an improvised item.",
    "Used to hold contents or combine spray materials while making an improvised explosive.",
    "Used to complete an improvised explosive by attaching its trigger.",
    "Handled when connecting or replacing a vehicle battery to restore the electrical system.",
    "Handled when removing or replacing a vehicle fuel tank.",
    "Handled when removing or reinstalling a vehicle seat or cargo module.",
    "Handled when removing or replacing running gear to restore a vehicle's operation.",
    "Handled when removing or reinstalling a vehicle body panel or window.",
    "Used to install or remove vehicle tires.",
    "Used to adjust the air pressure in vehicle tires.",
    "Used to recharge a battery removed from a vehicle.",
    "Material used to brew tea.",
    "Worn over the head or face for covering or protection.",
    "Worn on the body as active clothing.",
    "Worn on the wrist to check the time or set an alarm.",
    "A broken fish trap from which wire can be recovered.",
    "Used in carpentry work to build barbed-wire fences.",
    "Handled when tuning a portable radio to listen to broadcasts.",
    "A part used to modify firearms.",
    "A magazine used to load a firearm.",
    "Paint used for coating or leaving marks.",
    "Used to fit or sew stuffing while making bedding.",
    "Used to install or remove certain vehicle parts, such as tires and brakes.",
    "A mold used to cast ammunition.",
    "Equipment used to carry ammunition.",
    "Gunpowder material used to make ammunition and explosives.",
    "A sawing tool also used to shorten shotgun barrels.",
    "Used with paint to color plastered walls or other paintable surfaces.",
    "Handled when placing an explosive fitted with a detonator.",
    "Read or referenced to learn a skill or crafting recipe.",
    "A belt worn around the waist.",
    "Bellows used to raise a forge's temperature by forcing in air.",
    "Sporting equipment used for training or recreation.",
    "Used to carry items by wearing or holding it.",
]

SPECIAL_CONTEXT_SOURCE_SHA256 = "b2ebc665a88e252b1207bc39962b0b06181b9e187191745307b86a8cecbd33bb"
SPECIAL_CONTEXT_EN = [
    "Junk with no specific crafting use in Build 41.",
    "Used as material for metal structures and certain metal items.",
    "A portable container for carrying tools or other items.",
    "Used to build structures that require hinges, such as doors or gates.",
    "Used to mend clothing or reinforce it with leather patches.",
    "Used to repair certain damaged weapons or tools.",
    "Used to install or remove vehicle tires.",
    "Used to adjust the air pressure in vehicle tires.",
    "Used to recharge a battery removed from a vehicle.",
    "Used in carpentry work to build barbed-wire fences.",
    "Used to install or remove certain vehicle parts, such as tires and brakes.",
    "Used with paint to color plastered walls or other paintable surfaces.",
]

IDENTITY_ONLY_EN = {
    "수원": "A water source.",
    "물통": "A water container.",
    "잡동사니": "A miscellaneous item.",
    "조명 기구": "A light source.",
    "원예 소모품": "A gardening consumable.",
    "낚싯대": "A fishing rod.",
    "차량 정비 용품": "A vehicle-maintenance item.",
    "캠핑 용품": "Camping equipment.",
    "낚시 용품": "Fishing equipment.",
    "제작 무기": "A crafted weapon.",
    "통자물쇠": "A padlock.",
    "무전기": "A radio.",
    "기술 서적": "A skill book.",
    "음료": "A drink.",
}

# Acquisition prose is assembled from a limited product vocabulary. Longest
# phrases are replaced first, then the remaining Korean grammar is normalized.
TERMS_EN = {
    "공사 자재 보관 장소": "construction-material storage",
    "건축 자재 보관 장소": "building-material storage",
    "사냥 장비 보관 장소": "hunting-equipment storage",
    "가정 총기 보관 장소": "home firearm storage",
    "차고 총기 보관 장소": "garage firearm storage",
    "군용 무기 보관 장소": "military weapon storage",
    "경찰 무기 보관 장소": "police weapon storage",
    "경찰 총기 보관 장소": "police firearm storage",
    "총기 보관 장소": "firearm storage",
    "총기 취급 장소": "firearm areas",
    "특수 총기 진열대": "special-firearm displays",
    "무장 은신처 보관 장소": "armed safehouse storage",
    "전자 부품 보관 장소": "electronic-parts storage",
    "전기 부품 보관 장소": "electrical-parts storage",
    "전자 공구 보관 장소": "electronics-tool storage",
    "전기 공구 보관 장소": "power-tool storage",
    "전자용품 보관 장소": "electronics storage",
    "의료 물품 보관 장소": "medical-supply storage",
    "의료 보관 장소": "medical storage",
    "병원 보관 장소": "hospital storage",
    "군 의료 보관 장소": "military medical storage",
    "캠핑 장비 보관 장소": "camping-equipment storage",
    "생존 장비 보관 장소": "survival-equipment storage",
    "군용 장비 보관 장소": "military-equipment storage",
    "의류 보관 장소": "clothing storage",
    "겨울 의류 보관 장소": "winter-clothing storage",
    "스포츠 의류 장소": "sportswear areas",
    "코스튬 보관 장소": "costume storage",
    "의상 보관 장소": "outfit storage",
    "연습실 의상 보관 장소": "rehearsal-room costume storage",
    "식기 보관 장소": "tableware storage",
    "조리 도구 보관 장소": "cookware storage",
    "냉동 식품 보관 장소": "frozen-food storage",
    "침구 보관 장소": "bedding storage",
    "재봉 자재 보관 장소": "sewing-material storage",
    "재봉 도구 보관 장소": "sewing-tool storage",
    "공구 보관 장소": "tool storage",
    "공장 보관 장소": "factory storage",
    "학교 보관 장소": "school storage",
    "체육관 보관 장소": "gym storage",
    "소방 보관 장소": "fire-department storage",
    "경찰 보관 장소": "police storage",
    "군용 보관 장소": "military storage",
    "교도관 보관 장소": "corrections-officer storage",
    "농업 물품 상자": "farming-supply crates",
    "목공 공구 상자": "carpentry-tool crates",
    "공구 상자": "toolboxes",
    "스포츠 상자": "sports crates",
    "식기 상자": "tableware crates",
    "악기 상자": "instrument cases",
    "낚시 장비 상자": "fishing-equipment crates",
    "운동 장비 상자": "exercise-equipment crates",
    "당구 용품 상자": "billiards-supply crates",
    "바비큐 용품 상자": "barbecue-supply crates",
    "스피포 상품 상자": "Spiffo merchandise crates",
    "스피포 상품 진열대": "Spiffo merchandise displays",
    "스피포 상품 보관 장소": "Spiffo merchandise storage",
    "스피포 주방": "Spiffo kitchens",
    "스피포 차량": "Spiffo vehicles",
    "스피포 매장": "Spiffo restaurants",
    "총기 매장 진열대": "gun-store displays",
    "전당포 칼 진열대": "pawnshop knife displays",
    "밴드 굿즈 진열대": "band-merchandise displays",
    "지도 진열대": "map displays",
    "속옷 진열대": "underwear displays",
    "수영복 진열대": "swimwear displays",
    "조리 도구 진열대": "cookware displays",
    "무기 진열 장소": "weapon displays",
    "장신구 취급 장소": "jewelry retailers",
    "장신구 보관 장소": "jewelry storage",
    "캠핑 장비 취급 장소": "camping-supply retailers",
    "낚시 장비 취급 장소": "fishing-supply retailers",
    "원예 용품 취급 장소": "gardening-supply retailers",
    "무전 장비 취급 장소": "radio-equipment retailers",
    "야외 조리 장비 취급 장소": "outdoor-cooking retailers",
    "농사용품 판매 장소": "farming-supply stores",
    "재봉용품 판매 장소": "sewing-supply stores",
    "공구 판매 장소": "tool retailers",
    "휴가용품 판매 장소": "vacation-supply stores",
    "전자제품 매장": "electronics stores",
    "전자제품 매대": "electronics counters",
    "전자용품점": "electronics stores",
    "음향 기기 판매점": "audio-equipment stores",
    "주방용품 매장": "kitchenware stores",
    "생활용품 매장": "household-goods stores",
    "군용품점": "military-surplus stores",
    "총기 매장": "gun stores",
    "총기점": "gun stores",
    "스포츠 상점": "sporting-goods stores",
    "스포츠 매장": "sporting-goods stores",
    "원예 상점": "gardening stores",
    "공구점": "tool stores",
    "철물점": "hardware stores",
    "전당포": "pawnshops",
    "골동품점": "antique stores",
    "악기 상점": "music stores",
    "음악 상점": "music stores",
    "낚시용품점": "fishing-supply stores",
    "애완용품 판매점": "pet-supply stores",
    "장난감 판매점": "toy stores",
    "카메라 매장": "camera stores",
    "식료품점": "grocery stores",
    "제과점": "bakeries",
    "카페": "cafes",
    "약국": "pharmacies",
    "병원": "hospitals",
    "가정집": "homes",
    "주거지": "residences",
    "주거지 주방": "residential kitchens",
    "주방": "kitchens",
    "욕실": "bathrooms",
    "휴게 공간": "break areas",
    "사무 공간": "offices",
    "우편 업무 장소": "postal workplaces",
    "작업장": "workshops",
    "작업 현장": "work sites",
    "작업 장소": "work areas",
    "정비 작업장": "maintenance workshops",
    "목공 작업 장소": "carpentry areas",
    "금속 작업 장소": "metalworking areas",
    "금속 작업장": "metalworking workshops",
    "조리 작업 장소": "cooking areas",
    "청소 작업 장소": "cleaning areas",
    "세탁 작업 장소": "laundry areas",
    "도축 작업 장소": "butchering areas",
    "검시 작업 장소": "autopsy areas",
    "의료 작업 장소": "medical work areas",
    "전기공 작업 구역": "electrician work areas",
    "사진 자재 보관 장소": "photography-supply storage",
    "연료 보관 장소": "fuel storage",
    "안전 장비 보관 장소": "safety-equipment storage",
    "보안 장비 보관 장소": "security-equipment storage",
    "정비 보관 장소": "maintenance storage",
    "차량 정비 장소": "vehicle-maintenance areas",
    "차량 보관 장소": "vehicle storage",
    "차량 정비소 선반": "vehicle-shop shelves",
    "군 항공 보관 장소": "military-aviation storage",
    "은닉 보관 장소": "hidden stashes",
    "생존자 은닉처": "survivor safehouses",
    "무장 은신처": "armed safehouses",
    "실험 시설": "laboratories",
    "실험실": "laboratories",
    "약품 제조 시설": "pharmaceutical facilities",
    "의료 시설": "medical facilities",
    "경찰 시설": "police facilities",
    "숙박 시설": "lodging",
    "발전기실": "generator rooms",
    "교도소 수감자 구역": "prisoner areas",
    "학교 물품 장소": "school-supply areas",
    "사물함": "lockers",
    "학교 선반": "school shelves",
    "책상": "desks",
    "체육관": "gyms",
    "학교": "schools",
    "골프 보관함": "golf lockers",
    "골프 보관 장소": "golf storage",
    "볼링장 보관 장소": "bowling-alley storage",
    "볼링장 신발 보관 장소": "bowling-shoe storage",
    "패들 보관함": "paddle lockers",
    "라켓 보관함": "racket lockers",
    "스틱 보관함": "stick lockers",
    "연습실 보관함": "rehearsal-room storage",
    "폐기물 처리 장소": "waste-disposal areas",
    "의료 관련 장소": "medical areas",
    "시계 취급 장소": "watch retailers",
    "안경 취급 장소": "eyewear retailers",
    "잡화 보관 장소": "general-goods storage",
    "문구 보관 장소": "stationery storage",
    "사무용품 보관 장소": "office-supply storage",
    "사무용품 보관함": "office-supply cabinets",
    "학용품 보관 장소": "school-supply storage",
    "침구 취급 장소": "bedding retailers",
    "침구 보관 장소": "bedding storage",
    "세탁물 보관 장소": "laundry storage",
    "식음료 판매대": "food-and-drink counters",
    "담배 판매대": "tobacco counters",
    "문구 매대": "stationery counters",
    "의상 액세서리 매장": "fashion-accessory stores",
    "란제리 액세서리 매장": "lingerie-accessory stores",
    "란제리 매장": "lingerie stores",
    "장갑 매장": "glove stores",
    "가죽 장갑 매장": "leather-glove stores",
    "신발 매장": "shoe stores",
    "가죽 신발 매장": "leather-shoe stores",
    "운동화 매장": "sneaker stores",
    "부츠 매장": "boot stores",
    "양말 매장": "sock stores",
    "모자 매장": "hat stores",
    "셔츠 매장": "shirt stores",
    "정장 셔츠 매장": "dress-shirt stores",
    "바지 매장": "pants stores",
    "정장 바지 매장": "dress-pants stores",
    "청바지 매장": "jeans stores",
    "가죽 바지 매장": "leather-pants stores",
    "재킷 매장": "jacket stores",
    "정장 재킷 매장": "dress-jacket stores",
    "점퍼 매장": "jumper stores",
    "드레스 매장": "dress stores",
    "여름 의류 매장": "summer-clothing stores",
    "격식 의류 보관 장소": "formalwear storage",
    "수영장 보관 장소": "pool storage",
    "스트립 클럽 탈의실": "strip-club dressing rooms",
    "겨울 의류": "winter-clothing areas",
    "축제 물품 보관 장소": "festival-supply storage",
    "축제 물품": "festival-supply areas",
    "군용 전자 보관 장소": "military-electronics storage",
    "경비 보관 장소": "security-guard storage",
    "정비 차량": "maintenance vehicles",
    "작업 차량": "work vehicles",
    "생존 차량": "survival vehicles",
    "사냥 차량": "hunting vehicles",
    "경찰 차량": "police vehicles",
    "소방 차량": "fire-department vehicles",
    "구급 차량": "ambulances",
    "구급차": "ambulances",
    "의사 차량": "doctor vehicles",
    "골프 차량": "golf carts",
    "차량": "vehicles",
    "차고": "garages",
    "캠핑": "camping areas",
    "사냥 장비 장소": "hunting-equipment areas",
    "군용": "military areas",
    "군": "military areas",
    "경찰": "police areas",
    "시가지": "urban areas",
    "트레일러파크": "trailer parks",
    "초목 지대 채집": "foraging in vegetation zones",
    "채집": "foraging",
}

ACQUISITION_EXACT_EN = {
    "TV 리모컨을 분해해 구한다": "Obtained by dismantling a TV remote.",
    "가죽 의류를 찢어 얻는다": "Obtained by tearing leather clothing.",
    "고기를 잘라 얻는다": "Obtained by cutting meat.",
    "권투 장비 보관 장소와 골동품점에서 발견된다": "Found in boxing-equipment storage and antique stores.",
    "권투 장비 보관 장소와 스포츠 상점에서 발견된다": "Found in boxing-equipment storage and sporting-goods stores.",
    "그릇이나 냄비에 음식 또는 재료를 담아 준비한다": "Prepared by placing food or ingredients in a bowl or pot.",
    "금속 가공으로 만든다": "Made through metalworking.",
    "금속 작업 장소와 공구점, 정비 장소에서 발견된다": "Found in metalworking areas, tool stores, and maintenance areas.",
    "나무 판재를 가공해 얻는다": "Obtained by processing lumber.",
    "나무막대와 끈, 종이클립이나 못으로 제작한다": "Crafted from a wooden stick, cord, and a paperclip or nail.",
    "나무막대와 낚싯줄, 종이클립이나 못으로 제작한다": "Crafted from a wooden stick, fishing line, and a paperclip or nail.",
    "나뭇가지를 칼날 도구로 깎아 만든다": "Made by shaping a branch with a bladed tool.",
    "나뭇가지와 깎인 돌, 천 조각으로 제작한다": "Crafted from a branch, chipped stone, and a ripped sheet.",
    "나뭇가지와 깎인 돌, 천 조각이나 끈으로 제작한다": "Crafted from a branch, chipped stone, and a ripped sheet or cord.",
    "나뭇가지와 돌, 천 조각으로 제작한다": "Crafted from a branch, stone, and a ripped sheet.",
    "냉찜질팩과 천 조각, 신문으로 제작한다": "Crafted from a cold pack, ripped sheets, and newspaper.",
    "데님 의류를 찢어 얻는다": "Obtained by tearing denim clothing.",
    "도축 작업 장소와 식기 보관 장소, 칼 제작 장소에서 발견된다": "Found in butchering areas, tableware storage, and knife-production areas.",
    "동물 사체를 손질해 얻는다": "Obtained by butchering an animal carcass.",
    "맥주를 따라 얻는다": "Obtained by pouring beer.",
    "모래를 담아 얻는다": "Obtained by filling it with sand.",
    "모루 근처에서 철괴와 망치, 집게로 제작한다": "Crafted near an anvil from an iron ingot with a hammer and tongs.",
    "모루 근처에서 철괴와 망치로 제작한다": "Crafted near an anvil from an iron ingot with a hammer.",
    "못 상자를 열어 구한다": "Obtained by opening a box of nails.",
    "물 양동이를 비워 구한다": "Obtained by emptying a bucket of water.",
    "물고기를 손질해 얻는다": "Obtained by preparing a fish.",
    "반죽이나 재료를 조리해 만든다": "Made by cooking dough or ingredients.",
    "배관 자재 장소와 차량에서 발견된다": "Found in plumbing-supply areas and vehicles.",
    "밴드 굿즈 진열대와 의류 매장에서 발견된다": "Found at band-merchandise displays and clothing stores.",
    "베이컨을 손질해 얻는다": "Obtained by preparing bacon.",
    "베이컨을 잘게 손질해 얻는다": "Obtained by cutting bacon into pieces.",
    "부러진 낚싯대를 끈과 종이클립이나 못으로 수리한다": "Made by repairing a broken fishing rod with cord and a paperclip or nail.",
    "분무기를 조합해 얻는다": "Obtained by assembling a gardening spray can.",
    "분무기에 약품을 채워 얻는다": "Obtained by filling a spray can with chemicals.",
    "붕대를 소독하거나 끓여서 만든다": "Made by disinfecting or boiling a bandage.",
    "빈 물병에 휘발유를 담아 만든다": "Made by filling an empty water bottle with gasoline.",
    "빈 술병이나 빈 맥주병을 깨뜨려 만든다": "Made by breaking an empty liquor or beer bottle.",
    "빈 연료통에 휘발유를 담아 만든다": "Made by filling an empty gas can with gasoline.",
    "빈 와인 병에 휘발유를 담아 만든다": "Made by filling an empty wine bottle with gasoline.",
    "빈 용기에 물을 담아 얻는다": "Obtained by filling an empty container with water.",
    "빈 용기에 물을 채워 얻는다": "Obtained by filling an empty container with water.",
    "빈 위스키 병에 휘발유를 담아 만든다": "Made by filling an empty whiskey bottle with gasoline.",
    "빈 음료수 병에 휘발유를 담아 만든다": "Made by filling an empty pop bottle with gasoline.",
    "빈 표백제 병에 휘발유를 담아 만든다": "Made by filling an empty bleach bottle with gasoline.",
    "빵을 잘라 얻는다": "Obtained by slicing bread.",
    "사무용품과 학용품 보관 장소, 의료 작업 장소에서 발견된다": "Found with office supplies, school-supply storage, and medical work areas.",
    "산탄총과 톱으로 절단해 만든다": "Made by cutting down a shotgun with a saw.",
    "서점 가방 진열대와 학교 물품 장소, 사물함에서 발견된다": "Found at bookstore bag displays, school-supply areas, and lockers.",
    "서점 가방 진열대와 학교 물품 장소, 학교 보관 장소에서 발견된다": "Found at bookstore bag displays, school-supply areas, and school storage.",
    "솜에 알코올을 묻혀 만든다": "Made by soaking cotton balls in alcohol.",
    "수박을 으깨 얻는다": "Obtained by crushing a watermelon.",
    "수박을 잘라 얻는다": "Obtained by slicing a watermelon.",
    "수신기와 전자 부품으로 만든다": "Made from a receiver and electronic parts.",
    "수확물을 포대에 담아 얻는다": "Obtained by placing harvested produce in a sack.",
    "술병이나 빈 병, 천 조각과 휘발유로 제작한다": "Crafted from a liquor or empty bottle, a ripped sheet, and gasoline.",
    "스포츠 매장과 야구 장비 보관 장소, 차량에서 발견된다": "Found in sporting-goods stores, baseball-equipment storage, and vehicles.",
    "스포츠 장비 장소에서 발견된다": "Found in sports-equipment areas.",
    "스포츠 장비 장소와 잡화 보관 장소, 골동품점에서 발견된다": "Found in sports-equipment areas, general-goods storage, and antique stores.",
    "스포츠 장비 장소와 코스튬 보관 장소, 골동품점에서 발견된다": "Found in sports-equipment areas, costume storage, and antique stores.",
    "스피커를 분해해 구한다": "Obtained by dismantling a speaker.",
    "스피포 상품 진열대와 의류 매장에서 발견된다": "Found at Spiffo merchandise displays and clothing stores.",
    "시계 판매점에서 발견된다": "Found in watch stores.",
    "시트나 면 의류를 찢어 만든다": "Made by tearing sheets or cotton clothing.",
    "식기 보관 장소와 생활용품 매장, 칼 제작 장소에서 발견된다": "Found in tableware storage, household-goods stores, and knife-production areas.",
    "식료품점이나 극장에서 발견된다": "Found in grocery stores or theaters.",
    "신문으로 제작한다": "Crafted from newspaper.",
    "쌀을 끓여 만든다": "Made by boiling rice.",
    "쌍열 산탄총과 톱으로 절단해 만든다": "Made by cutting down a double-barrel shotgun with a saw.",
    "씨앗 봉투를 열어 얻는다": "Obtained by opening a seed packet.",
    "씨앗을 봉투에 담아 얻는다": "Obtained by placing seeds in a packet.",
    "알루미늄으로 제작한다": "Crafted from aluminum.",
    "야구 방망이와 못, 망치로 제작한다": "Crafted from a baseball bat and nails with a hammer.",
    "야구 장비 보관 장소와 스포츠 상점, 골동품점에서 발견된다": "Found in baseball-equipment storage, sporting-goods stores, and antique stores.",
    "야구 장비 보관 장소와 스포츠 상점, 학교 보관 장소에서 발견된다": "Found in baseball-equipment storage, sporting-goods stores, and school storage.",
    "약초를 가공해 얻는다": "Obtained by processing herbs.",
    "양동이에 물을 담아 만든다": "Made by filling a bucket with water.",
    "양초에 불을 붙여 얻는다": "Obtained by lighting a candle.",
    "와인잔에 와인을 따라 만든다": "Made by pouring wine into a wine glass.",
    "욕실과 배관 자재 장소, 차고와 공구 상자에서 발견된다": "Found in bathrooms, plumbing-supply areas, garages, and toolboxes.",
    "욕실과 배관 자재 장소, 청소 작업 장소에서 발견된다": "Found in bathrooms, plumbing-supply areas, and cleaning areas.",
    "유리컵에 음료를 따라 만든다": "Made by pouring a drink into a glass.",
    "자갈을 담아 얻는다": "Obtained by filling it with gravel.",
    "재료를 그릇에 담아 만든다": "Made by placing ingredients in a bowl.",
    "재료를 병조림해 만든다": "Made by canning ingredients in a jar.",
    "재료를 섞어 얻는다": "Obtained by mixing ingredients.",
    "재료를 섞어 준비한다": "Prepared by mixing ingredients.",
    "재료를 조리해 만든다": "Made by cooking ingredients.",
    "재료를 조합해 만든다": "Made by combining ingredients.",
    "재봉 관련 장소나 의료 시설에서 발견된다": "Found in sewing-related areas or medical facilities.",
    "재봉 용품점이나 재봉 자재 보관 장소에서 발견된다": "Found in sewing-supply stores or sewing-material storage.",
    "전당포 칼 진열대와 무기 진열 장소, 취미품 진열대에서 발견된다": "Found at pawnshop knife displays, weapon displays, and hobby displays.",
    "전자 부품과 금속 파이프, 화약과 끈으로 제작한다": "Crafted from electronic parts, a metal pipe, gunpowder, and cord.",
    "전자 부품과 증폭기를 조합해 만든다": "Made by combining electronic parts and an amplifier.",
    "전자 부품을 가공해 얻는다": "Obtained by processing electronic parts.",
    "전자 스크랩과 무선 부품, 전선과 알루미늄으로 제작한다": "Crafted from electronic scrap, radio parts, wire, and aluminum.",
    "전자기기를 분해해 구한다": "Obtained by dismantling electronic devices.",
    "제과 작업 장소와 식기 보관 장소, 칼 제작 장소에서 발견된다": "Found in baking areas, tableware storage, and knife-production areas.",
    "제작으로 얻는다": "Obtained through crafting.",
    "제작한 창과 가위, 덕트 테이프로 제작한다": "Crafted from a crafted spear, scissors, and duct tape.",
    "제작한 창과 드라이버, 덕트 테이프로 제작한다": "Crafted from a crafted spear, screwdriver, and duct tape.",
    "제작한 창과 마체테, 덕트 테이프로 제작한다": "Crafted from a crafted spear, machete, and duct tape.",
    "제작한 창과 메스, 덕트 테이프로 제작한다": "Crafted from a crafted spear, scalpel, and duct tape.",
    "제작한 창과 버터칼, 덕트 테이프로 제작한다": "Crafted from a crafted spear, butter knife, and duct tape.",
    "제작한 창과 사냥칼, 덕트 테이프로 제작한다": "Crafted from a crafted spear, hunting knife, and duct tape.",
    "제작한 창과 손갈퀴, 덕트 테이프로 제작한다": "Crafted from a crafted spear, hand fork, and duct tape.",
    "제작한 창과 숟가락, 덕트 테이프로 제작한다": "Crafted from a crafted spear, spoon, and duct tape.",
    "제작한 창과 식빵칼, 덕트 테이프로 제작한다": "Crafted from a crafted spear, bread knife, and duct tape.",
    "제작한 창과 식칼, 덕트 테이프로 제작한다": "Crafted from a crafted spear, kitchen knife, and duct tape.",
    "제작한 창과 얼음송곳, 덕트 테이프로 제작한다": "Crafted from a crafted spear, ice pick, and duct tape.",
    "제작한 창과 편지칼, 덕트 테이프로 제작한다": "Crafted from a crafted spear, letter opener, and duct tape.",
    "제작한 창과 포크, 덕트 테이프로 제작한다": "Crafted from a crafted spear, fork, and duct tape.",
    "지도 진열대와 지도 상자, 차량 정비소 선반과 차량에서 발견된다": "Found at map displays, in map crates, on vehicle-shop shelves, and in vehicles.",
    "천 조각과 막대 재료로 제작한다": "Crafted from ripped sheets and stick material.",
    "천이나 의류를 찢어 얻는다": "Obtained by tearing fabric or clothing.",
    "컵에 물과 재료를 담아 끓여 만든다": "Made by boiling water and ingredients in a cup.",
    "컵에 음료를 담아 만든다": "Made by pouring a drink into a cup.",
    "타이머나 알람시계를 개조해 만든다": "Made by modifying a timer or alarm clock.",
    "탄약 상자를 열거나 모루 근처에서 주조해 얻는다": "Obtained by opening an ammunition box or casting near an anvil.",
    "탄약 상자를 열어 얻는다": "Obtained by opening an ammunition box.",
    "탄약을 분해해 구한다": "Obtained by dismantling ammunition.",
    "탄약을 상자에 담아 얻는다": "Obtained by placing ammunition in a box.",
    "통나무를 묶어 만든다": "Made by tying logs together.",
    "통나무를 톱으로 가공해 얻는다": "Obtained by sawing a log.",
    "퇴비를 담아 얻는다": "Obtained by filling it with compost.",
    "파스타를 끓여 만든다": "Made by boiling pasta.",
    "판자나 나뭇가지와 칼날 도구로 제작한다": "Crafted from a plank or branch with a bladed tool.",
    "판자를 톱질해 만든다": "Made by sawing planks.",
    "판자와 못, 망치로 제작한다": "Crafted from planks and nails with a hammer.",
    "폭발물을 개조해 얻는다": "Obtained by modifying an explosive.",
    "플라스틱 컵에 음료를 따라 만든다": "Made by pouring a drink into a plastic cup.",
    "헝겊을 소독하거나 끓여서 만든다": "Made by disinfecting or boiling a rag.",
    "헤어스프레이와 불꽃놀이 재료를 조합해 만든다": "Made by combining hairspray and fireworks material.",
    "호박을 가공해 만든다": "Made by processing a pumpkin.",
    "휘발유와 천 조각과 빈 병을 조합해 만든다": "Made by combining gasoline, a ripped sheet, and an empty bottle.",
    "흙을 담아 얻는다": "Obtained by filling it with soil.",
}


def _source_values(rows: list[dict[str, object]], field: str) -> list[str]:
    return sorted({str(row[field]) for row in rows if row.get(field)})


def _sha(values: list[str]) -> str:
    return hashlib.sha256("\n".join(values).encode("utf-8")).hexdigest()


def primary_use_translations(rows: list[dict[str, object]]) -> dict[str, str]:
    values = _source_values(rows, "primary_use")
    if _sha(values) != PRIMARY_USE_SOURCE_SHA256 or len(values) != len(PRIMARY_USE_EN):
        raise RuntimeError("LAYER3_EN_PRIMARY_USE_SOURCE_MISMATCH")
    return dict(zip(values, PRIMARY_USE_EN, strict=True))


def special_context_translations(rows: list[dict[str, object]]) -> dict[str, str]:
    values = _source_values(rows, "special_context")
    if _sha(values) != SPECIAL_CONTEXT_SOURCE_SHA256 or len(values) != len(SPECIAL_CONTEXT_EN):
        raise RuntimeError("LAYER3_EN_SPECIAL_CONTEXT_SOURCE_MISMATCH")
    return dict(zip(values, SPECIAL_CONTEXT_EN, strict=True))


def _translate_terms(value: str) -> str:
    translated = value
    for korean, english in sorted(TERMS_EN.items(), key=lambda pair: len(pair[0]), reverse=True):
        translated = translated.replace(korean, english)
    translated = translated.replace("이나 ", " or ").replace("나 ", " or ")
    translated = translated.replace(" 또는 ", " or ")
    translated = translated.replace("과 ", ", ").replace("와 ", ", ")
    return translated


def translate_acquisition_hint(value: str) -> str | None:
    exact = ACQUISITION_EXACT_EN.get(value)
    if exact is not None:
        return exact
    for suffix, prefix in (
        ("에서 발견된다", "Found in "),
        ("에서 구할 수 있다", "Can be obtained from "),
        ("으로 구할 수 있다", "Can be obtained from "),
        ("로 구할 수 있다", "Can be obtained from "),
    ):
        if value.endswith(suffix):
            result = prefix + _translate_terms(value[: -len(suffix)]) + "."
            return result if re.search("[가-힣]", result) is None else None
    return None


def _lua_string(value: str) -> str:
    parts = ['"']
    for byte in value.encode("utf-8"):
        if byte == 34:
            parts.append('\\"')
        elif byte == 92:
            parts.append('\\\\')
        elif byte == 10:
            parts.append("\\n")
        elif byte == 13:
            parts.append("\\r")
        elif byte == 9:
            parts.append("\\t")
        elif 32 <= byte <= 126:
            parts.append(chr(byte))
        else:
            parts.append(f"\\{byte:03d}")
    parts.append('"')
    return "".join(parts)


def _write_runtime(entries: dict[str, str], output_root: Path, chunk_size: int = 200) -> None:
    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True)
    ordered = sorted(entries.items())
    chunks: list[dict[str, object]] = []
    for offset in range(0, len(ordered), chunk_size):
        rows = ordered[offset : offset + chunk_size]
        ordinal = len(chunks) + 1
        name = f"Chunk{ordinal:03d}"
        lines = ["-- Generated Layer 3 English localization payload.", "return {"]
        lines.extend(f"    [{_lua_string(full_type)}] = {_lua_string(text)}," for full_type, text in rows)
        lines.extend(["}", ""])
        (output_root / f"{name}.lua").write_text("\n".join(lines), encoding="utf-8", newline="\n")
        chunks.append({"first": rows[0][0], "last": rows[-1][0], "module": f"Iris/Data/Layer3English/{name}"})
    lines = ["-- Generated Layer 3 English localization range index.", "return {", "    chunks = {"]
    lines.extend(
        "        { first = %s, last = %s, module = %s },"
        % (_lua_string(str(row["first"])), _lua_string(str(row["last"])), _lua_string(str(row["module"])))
        for row in chunks
    )
    lines.extend(["    },", "}", ""])
    (output_root / "Index.lua").write_text("\n".join(lines), encoding="utf-8", newline="\n")


def _current_projection(repository_root: Path) -> tuple[dict[str, dict[str, object]], str]:
    pointer_path = repository_path(repository_root, CURRENT_POINTER_RELATIVE_PATH)
    pointer_text = pointer_path.read_text(encoding="utf-8")
    generation_matches = re.findall(
        r'^\s*generation_id\s*=\s*"(dvf33-[0-9a-f]{64})",?\s*$',
        pointer_text,
        re.MULTILINE,
    )
    if len(generation_matches) != 1:
        raise RuntimeError("LAYER3_EN_CURRENT_GENERATION_POINTER_INVALID")

    current_generation_id = generation_matches[0]
    descriptor_path = repository_path(
        repository_root,
        f"{CURRENT_GENERATION_ROOT_RELATIVE_PATH}/{current_generation_id}/generation_descriptor.json",
    )
    descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
    if descriptor.get("generation_id") != current_generation_id:
        raise RuntimeError("LAYER3_EN_CURRENT_GENERATION_DESCRIPTOR_MISMATCH")
    required_input_paths = {CANONICAL_INPUTS[0], CANONICAL_INPUTS[6]}
    descriptor_inputs = {
        row.get("path"): row
        for row in descriptor.get("canonical_inputs", [])
        if row.get("path") in required_input_paths
    }
    current_inputs = {
        row["path"]: row
        for row in canonical_input_identity(repository_root)
        if row["path"] in required_input_paths
    }
    if descriptor_inputs != current_inputs:
        raise RuntimeError("LAYER3_EN_CURRENT_GENERATION_INPUT_MISMATCH")

    projection_path = repository_path(repository_root, CANONICAL_INPUTS[6])
    projection = json.loads(projection_path.read_text(encoding="utf-8"))
    entries = projection.get("entries")
    if not isinstance(entries, dict):
        raise RuntimeError("LAYER3_EN_CURRENT_PROJECTION_INVALID")
    return entries, current_generation_id


def approved_general_descriptions(
    repository_root: Path,
    facts_by_item: dict[str, dict[str, object]],
    rendered: dict[str, dict[str, object]],
) -> dict[str, dict[str, str]]:
    """Read bilingual edits from the already generation-bound approved input.

    The source fields retain their historical provenance. User adoption of
    these existing details is not an independent game-source verification.
    """
    projection = json.loads(repository_path(repository_root, CANONICAL_INPUTS[6]).read_text(encoding="utf-8"))
    adoption = projection.get("meta", {}).get("general_description_integration")
    if adoption is None:
        return {}
    if (not isinstance(adoption, dict)
            or adoption.get("decision") not in {
                "user_adopted_primary_use_with_context_detail_refinement",
                "user_adopted_build41_description_correction",
            }
            or adoption.get("source_slot") != "special_context"
            or not adoption.get("authority_ref")):
        raise RuntimeError("LAYER3_GENERAL_DESCRIPTION_ADOPTION_INVALID")
    facts_path = repository_path(repository_root, CANONICAL_INPUTS[0])
    if adoption.get("facts_sha256") != hashlib.sha256(facts_path.read_bytes()).hexdigest():
        raise RuntimeError("LAYER3_GENERAL_DESCRIPTION_INPUT_STALE")
    entries = adoption.get("entries")
    if not isinstance(entries, dict) or not entries:
        raise RuntimeError("LAYER3_GENERAL_DESCRIPTION_ENTRIES_INVALID")
    result = {}
    for key, entry in entries.items():
        facts = facts_by_item.get(key, {})
        current = rendered.get(key, {})
        if not isinstance(entry, dict):
            raise RuntimeError(f"LAYER3_GENERAL_DESCRIPTION_ENTRY_INVALID:{key}")
        for field, hash_field in (("primary_use", "primary_use_source_sha256"), ("special_context", "context_source_sha256")):
            value = facts.get(field)
            if not isinstance(value, str) or not value or hashlib.sha256(value.encode("utf-8")).hexdigest() != entry.get(hash_field):
                raise RuntimeError(f"LAYER3_GENERAL_DESCRIPTION_SOURCE_MISMATCH:{key}:{field}")
        context_identity = {
            "item_id": key, "source_slot": "special_context",
            "fact_origin": entry.get("original_origin"),
            "source_value_hash": entry["context_source_sha256"],
        }
        context_id = "l3rf-" + hashlib.sha256(json.dumps(
            context_identity, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        ).encode("utf-8")).hexdigest()
        if entry.get("original_origin") != "origin_missing" or entry.get("context_fact_id") != context_id:
            raise RuntimeError(f"LAYER3_GENERAL_DESCRIPTION_CONTEXT_ID_MISMATCH:{key}")
        if current.get("role_material", {}).get("core_source_fact_ids") != [entry.get("primary_use_fact_id")]:
            raise RuntimeError(f"LAYER3_GENERAL_DESCRIPTION_CORE_MISMATCH:{key}")
        localized = entry.get("localized_general_description")
        if (not isinstance(localized, dict) or set(localized) != {"ko", "en"}
                or any(not isinstance(value, str) or not value.strip() or "\n" in value or "\r" in value for value in localized.values())
                or (current.get("text_ko") or "").split("\n\n", 1)[0] != localized["ko"]):
            raise RuntimeError(f"LAYER3_GENERAL_DESCRIPTION_LOCALE_MISMATCH:{key}")
        result[key] = localized
    return result


def build_english_entries(
    repository_root: Path,
) -> tuple[dict[str, str], str, dict[str, int]]:
    facts_path = repository_root / "Iris/build/description/v2/data/dvf_3_3_facts.jsonl"
    rows = [json.loads(line) for line in facts_path.read_text(encoding="utf-8").splitlines() if line]
    translations = primary_use_translations(rows)
    special = special_context_translations(rows)
    acquisition_values = _source_values(rows, "acquisition_hint")
    localized_acquisition = {
        value: translated
        for value in acquisition_values
        if (translated := translate_acquisition_hint(value)) is not None
    }
    unresolved = [value for value in acquisition_values if value not in localized_acquisition]
    if unresolved:
        raise RuntimeError(f"LAYER3_EN_ACQUISITION_UNRESOLVED:{len(unresolved)}")

    facts_by_item = {str(row["item_id"]): row for row in rows}
    rendered, generation_id = _current_projection(repository_root)
    general_descriptions = approved_general_descriptions(repository_root, facts_by_item, rendered)
    english_entries: dict[str, str] = {}
    for item_id, rendered_entry in rendered.items():
        if not isinstance(rendered_entry, dict):
            raise RuntimeError(f"LAYER3_EN_CURRENT_PROJECTION_ENTRY_INVALID:{item_id}")
        if not rendered_entry.get("text_ko"):
            continue
        facts = facts_by_item.get(item_id)
        if facts is None:
            raise RuntimeError(f"LAYER3_EN_CURRENT_PUBLIC_FACT_MISSING:{item_id}")
        primary_use = facts.get("primary_use")
        body = ""
        general_description = general_descriptions.get(item_id)
        if general_description:
            body = general_description["en"]
        elif primary_use:
            body = translations[str(primary_use)]
        else:
            body = IDENTITY_ONLY_EN[str(facts["identity_hint"])]
        if not general_description and facts.get("special_context"):
            body += " " + special[str(facts["special_context"])]
        if facts.get("acquisition_hint"):
            body += "\n\n" + localized_acquisition[str(facts["acquisition_hint"])]
        english_entries[item_id] = body
    return english_entries, generation_id, {
        "primary_use": len(translations),
        "special_context": len(special),
        "acquisition": len(localized_acquisition),
    }


def build_tooltip_t1_owner_entries(
    repository_root: Path,
) -> tuple[dict[str, dict[str, object]], str]:
    """Publish existing single-core DVF facts for the Tooltip T1 contract.

    The output is a projection of already-owned fact identities and localized
    primary-use surfaces.  It does not split rendered bodies, synthesize facts,
    or turn acquisition material into a core description.
    """

    facts_path = repository_root / "Iris/build/description/v2/data/dvf_3_3_facts.jsonl"
    rows = [json.loads(line) for line in facts_path.read_text(encoding="utf-8").splitlines() if line]
    translations = primary_use_translations(rows)
    facts_by_item = {str(row["item_id"]): row for row in rows}
    rendered, generation_id = _current_projection(repository_root)
    entries: dict[str, dict[str, object]] = {}
    for item_id, rendered_entry in sorted(rendered.items()):
        if not isinstance(rendered_entry, dict):
            raise RuntimeError(f"TOOLTIP_T1_DVF_RENDERED_ENTRY_INVALID:{item_id}")
        role_material = rendered_entry.get("role_material")
        if not isinstance(role_material, dict):
            continue
        core_ids = role_material.get("core_source_fact_ids")
        if not isinstance(core_ids, list) or not all(isinstance(value, str) and value for value in core_ids):
            raise RuntimeError(f"TOOLTIP_T1_DVF_CORE_IDENTITY_INVALID:{item_id}")
        if not core_ids:
            continue
        if len(core_ids) != 1:
            raise RuntimeError(f"TOOLTIP_T1_DVF_MULTIPLE_CORE_FACTS_FORBIDDEN:{item_id}")
        facts = facts_by_item.get(item_id)
        if not isinstance(facts, dict) or not facts.get("primary_use"):
            raise RuntimeError(f"TOOLTIP_T1_DVF_CORE_SOURCE_MISSING:{item_id}")
        fact_id = core_ids[0]
        primary_use = str(facts["primary_use"])
        entries[item_id] = {
            "fact_id": fact_id,
            "fact_kind": "core_description",
            "source_fact_ids": [fact_id],
            "source_ref": f"Iris/build/description/v2/data/dvf_3_3_facts.jsonl#item_id={item_id};field=primary_use",
            "authority_ref": (
                f"{CURRENT_GENERATION_ROOT_RELATIVE_PATH}/{generation_id}/"
                f"dvf_3_3_rendered.json#entries/{item_id}/role_material/core_source_fact_ids"
            ),
            "upstream_readiness": "owner_approved",
            "tooltip_eligibility": "eligible",
            "localized_surfaces": {
                "ko": primary_use,
                "en": translations[primary_use],
            },
        }
    return entries, generation_id


def _write_tooltip_t1_owner_output(
    repository_root: Path,
    entries: dict[str, dict[str, object]],
    generation_id: str,
) -> Path:
    registry_path = repository_root / TOOLTIP_T1_D3_REGISTRY_RELATIVE_PATH
    absence_entries: dict[str, dict[str, object]] = {}
    if registry_path.is_file():
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        if registry.get("schema_version") != "iris-tooltip-t1-d3-disposition-registry-v1":
            raise RuntimeError("TOOLTIP_T1_D3_REGISTRY_SCHEMA_INVALID")
        registry_entries = registry.get("entries")
        if not isinstance(registry_entries, dict):
            raise RuntimeError("TOOLTIP_T1_D3_REGISTRY_ENTRIES_INVALID")
        if registry.get("target_count") != len(registry_entries) or registry.get("terminal_distribution") != {"A": 0, "B": len(registry_entries), "blocked": 0}:
            raise RuntimeError("TOOLTIP_T1_D3_REGISTRY_DISTRIBUTION_INVALID")
        for full_type, row in sorted(registry_entries.items()):
            if not isinstance(row, dict) or row.get("exact_full_type") != full_type:
                raise RuntimeError(f"TOOLTIP_T1_D3_REGISTRY_IDENTITY_INVALID:{full_type}")
            if row.get("intended_disposition") != "approved_legitimate_absence":
                continue
            absence_entries[full_type] = {
                "exact_full_type": full_type,
                "disposition": "approved_legitimate_absence",
                "absence_reason_code": row["absence_reason_code"],
                "owner": row["owner"],
                "acceptance_evidence": row["acceptance_evidence"],
                "applicable_scope": row["applicable_scope"],
                "reaudit_condition": row["reaudit_condition"],
                "authority_decision_ref": row["authority_decision_ref"],
            }
    from iris_tooling.domains.tooltip_t1.contract import canonical_bytes, sha256_bytes

    output_path = repository_root / TOOLTIP_T1_OWNER_OUTPUT_RELATIVE_PATH
    payload = {
        "schema_version": "iris-tooltip-t1-layer3-owner-input-v2",
        "producer": "iris_tooling.build.build_layer3_english_localization",
        "generation_id": generation_id,
        "absence_entries": absence_entries,
        "manifest": {
            "fact_entry_count": len(entries),
            "absence_entry_count": len(absence_entries),
            "total_owner_row_count": len(entries) + len(absence_entries),
            "fact_entries_sha256": sha256_bytes(canonical_bytes(entries)),
            "absence_entries_sha256": sha256_bytes(canonical_bytes(absence_entries)),
        },
        "entries": entries,
    }
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return output_path


def publish_tooltip_t1_owner_only(repository_root: Path) -> dict[str, object]:
    """Regenerate only the metadata owner projection, never locale runtime bytes."""

    tooltip_entries, generation_id = build_tooltip_t1_owner_entries(repository_root)
    output = _write_tooltip_t1_owner_output(repository_root, tooltip_entries, generation_id)
    payload = json.loads(output.read_text(encoding="utf-8"))
    return {
        "status": "BUILT",
        "generation_id": generation_id,
        "fact_entries": len(payload["entries"]),
        "absence_entries": len(payload["absence_entries"]),
        "tooltip_t1_owner_output": str(output),
        "runtime_locale_write_set": [],
    }


def main() -> int:
    repository_root = require_repository_context().repository_root
    english_entries, generation_id, metrics = build_english_entries(repository_root)
    tooltip_entries, tooltip_generation_id = build_tooltip_t1_owner_entries(repository_root)
    if tooltip_generation_id != generation_id:
        raise RuntimeError("TOOLTIP_T1_DVF_GENERATION_MISMATCH")

    output_root = repository_root / "Iris/media/lua/client/Iris/Data/Layer3English"
    _write_runtime(english_entries, output_root)
    tooltip_output = _write_tooltip_t1_owner_output(
        repository_root,
        tooltip_entries,
        generation_id,
    )
    print(json.dumps({
        "status": "BUILT",
        **metrics,
        "runtime_entries": len(english_entries),
        "tooltip_t1_owner_entries": len(tooltip_entries),
        "tooltip_t1_owner_output": str(tooltip_output),
        "generation_id": generation_id,
        "output_root": str(output_root),
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
