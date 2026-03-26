# TSD(Template Style Drawing) 직접 수정을 통한 넘버스 파일 생성 구현 계획

## 1. 개요
Apple Numbers 파일 내부의 `Index/*.iwa` (Snappy 압축 + Protobuf 직렬화) 파일을 직접 파싱하고 TSD 프레임워크의 Geometry 데이터를 수정하여, 애플 스크립트 없이 넘버스 파일을 백그라운드에서 동적으로 생성하는 기술을 구현합니다.
기존의 `numbers-parser` (Python) 라이브러리를 확장 또는 참고하여 파이프라인을 구축합니다.

## 2. 개발 환경 및 기술 스택
- **언어**: Python 3.10+
- **주요 라이브러리**:
  - `python-snappy` (또는 `cramjam`): Apple의 특수한 Snappy 압축/해제 처리를 위해 사용.
  - `protobuf`: `.iwa` 파일 내의 데이터를 파싱 및 직렬화하기 위해 사용.
  - `numbers-parser`: 객체 식별(Identity Mapping) 구조 참고 및 기존 Protobuf 스키마(예: `TSDArchives.proto`, `TSPArchives.proto`) 재사용.
  - `zipfile`: `.numbers` 패키지(ZIP 포맷)의 압축 및 해제.

## 3. 핵심 아키텍처 (5단계 파이프라인)

### 1단계: 압축 해제 (Unpack & Unsnappy)
1. `.numbers` 파일을 ZIP 파일로 취급하여 압축 해제합니다.
2. `Index/` 디렉토리 내의 `.iwa` 파일들을 찾습니다.
3. 각 `.iwa` 파일에 적용된 Snappy 프레이밍을 해제하여 순수 Protobuf 바이너리 페이로드로 변환합니다.

### 2단계: Protobuf 역직렬화 (Deserialize)
1. 추출된 바이너리를 `TSP.ArchiveInfo` 스키마로 래핑을 풉니다.
2. `TSD.GeometryArchive` 등 객체의 위치 및 크기 속성이 포함된 아카이브 메시지로 역직렬화합니다.

### 3단계: 객체 매핑 및 탐색 (Identity Mapping)
1. 변경 대상 객체(예: 이미지나 텍스트 박스)를 식별합니다.
   - `DocumentArchive` -> `SheetArchive` -> `DrawableArchive` -> `GeometryArchive` 계층을 따라 탐색합니다.
2. 각 아카이브는 `TSP.Reference` ID로 연결되어 있으므로, 이 Reference 그래프를 구성하여 대상 객체의 Geometry ID를 찾아냅니다.

### 4단계: 값 수정 및 재직렬화 (Modify & Serialize)
1. 대상 객체의 `TSD.GeometryArchive`에서 `origin` ($x, y$) 및 `size` ($w, h$) 필드를 원하는 값으로 수정합니다.
2. 수정된 Protobuf 객체에서 다시 바이너리 스트림으로 직렬화합니다.

### 5단계: 재압축 (Snappy & Repack)
1. 직렬화된 바이너리에 Apple 방식의 Snappy 알고리즘을 적용하여 `.iwa` 파일로 덮어씁니다.
2. 해제했던 모든 폴더와 파일 구조를 다시 ZIP 파일로 압축하고 확장자를 `.numbers`로 저장하여 최종 파일을 생성합니다.

## 4. 고려 사항 및 리스크 대응
- **Apple-specific Snappy 포맷**: 단순 Snappy가 아닌 IWA 청크 헤더 구조를 갖추고 있으므로, 청크 헤더 파싱/생성로직 구현이 필수적입니다.
- **Protobuf 스키마 의존성**: 역공학된 스키마(apple-iwork-protos)를 이용해야 하므로, 향후 Numbers 버전 업그레이드 시 스키마 변경에 대한 유지보수 대응이 필요합니다.
