TSD(Template Style Drawing) 직접 수정 기술 분석 보고서
본 보고서는 애플 Numbers 파일 내의 객체 레이아웃을 결정하는 TSD(Template Style Drawing) 프레임워크를 직접 수정하여, 이미지의 위치($x, y$)와 크기($w, h$)를 동적으로 조절하는 기술의 구현 가능성을 검토합니다.

1. 개요 및 기술적 배경
Apple의 iWork(Numbers, Pages, Keynote)는 화면에 그려지는 모든 객체(이미지, 도형, 표 등)를 관리하기 위해 TSD라는 내부 프레임워크를 사용합니다. 각 객체는 다음 세 가지 핵심 정보를 가집니다.

Info (TSD.InfoArchive): 객체의 성격 (예: 이것은 이미지다).
Drawable (TSD.DrawableArchive): 화면에 그려질 수 있는 속성 (레이어 순서 등).
Geometry (TSD.GeometryArchive): 가장 중요한 부분으로, 객체의 위치, 크기, 회전 각도 등을 결정합니다.
2. TSD.GeometryArchive 내부 구조 분석
.iwa 파일 내부의 Protobuf 스키마 분석 결과, TSD.GeometryArchive는 다음과 같은 필드를 통해 객체의 기하학적 속성을 정의합니다.

origin (TSP.Point): 객체의 좌상단 기준 좌표 ($x, y$). 단위는 포인트(pt)입니다.
size (TSP.Size): 객체의 너비($w$)와 높이($h$).
angle (double): 객체의 회전 각도 (라디안 단위).
flags (uint32): 가로/세로 뒤집기, 비율 고정 여부 등의 속성 비트마스크.
3. 구현 가능성 및 기술적 난관 (Feasibility)
[구현 가능성: YES]
기술적으로 직접 수정은 충분히 가능합니다. 실제로 오픈 소스 커뮤니티에서 역공학을 통해 해당 스키마를 파악해 두었으며, 바이너리 수준에서 이를 수정하면 Numbers 앱을 실행하지 않고도 레이아웃을 바꿀 수 있습니다.

[기술적 난관 및 프로세스]
하지만 구현 과정에는 다음과 같은 5단계의 복잡한 파이프라인이 필수적입니다.

압축 해제 (ZIP -> Snappy): 
.numbers
 압축을 풀고, Index/*.iwa 파일의 Snappy 압축을 해제해야 합니다.
역직렬화 (Protobuf Deserialization): 바이너리 데이터를 객체 형태로 변환해야 합니다. 이때 Apple의 비공개 스키마(TSDArchives.proto)가 필요합니다.
객체 매핑 (Identity Mapping): 수정하려는 이미지가 어떤 GeometryArchive를 참조하고 있는지 ID(TSP.Reference)를 추적해야 합니다. (이미지 파일명 -> ImageArchive -> GeometryArchive 순서)
값 수정 및 재직렬화: 좌표와 크기 값을 수정하고 다시 바이너리 형태로 변환합니다.
재압축 (Snappy -> ZIP): Apple의 특수한 Snappy 포맷 규칙에 맞춰 압축한 뒤 최종적으로 ZIP으로 패키징합니다.
4. 최종 평가 및 추천
장점
애플 스크립트 없이 완벽한 백그라운드 자동화가 가능합니다.
Linux 서버 등 macOS가 없는 환경에서도 Numbers 파일을 동적으로 생성할 수 있습니다.
단점 및 리스크
개발 공수: 단순 이미지 교체(전략 1)에 비해 구현 난이도가 10배 이상 높습니다.
스키마 변화: Apple이 Numbers 업데이트를 통해 내부 Protobuf 스키마를 변경하면 코드가 깨질 위험이 있습니다.
결론
"구현 가능한 기술입니다." 다만, 이를 바닥부터 개발하기보다는 기존의 numbers-parser (Python) 라이브러리의 내부 엔진을 확장하여 사용하거나, 전문적인 상업 라이브러리인 Aspose.Cells를 도입하는 것이 비즈니스 측면에서 가장 합리적인 선택입니다.

직접 구현을 원하실 경우, m-tymchyk/apple-iwork-protos와 같은 오픈소스 스키마를 기반으로 한 IWA 편집 도구 개발이 선행되어야 합니다